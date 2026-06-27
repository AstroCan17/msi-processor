# Copyright 2026 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pure image-quality-enhancement core (C-PU-ENH; ALG-ENH-*).

CPM-free, I/O-free ``numpy`` functions implementing the enhancement algorithms
of ATBD <5.4> (configurable denoise) and ATBD <5.5> (**mandatory** MTF
compensation / PSF deconvolution), ported faithfully from the heritage
``level_1.py`` ``Denoiser`` / ``sharpening`` classes (RD-10). All arrays are
processed in ``float32`` with a fixed operation order for reproducibility
(REQ-F-DEP-02, REQ-D-05).

Two enhancement sub-steps are provided:

* **MTF compensation (MTFC)** — :func:`mtf_compensate`, the **mandatory**
  restoration (ALG-ENH-DECONV). It convolves the band with a profile/ADF-bound
  PSF-derived deconvolution kernel (heritage ``sharpening.deconvolution_kernel``
  / ``cv2.filter2D``). Because a low-pass restoration kernel that integrates to
  one has unit DC gain, the operation is **radiometry-preserving** (total
  radiance / mean is conserved) while the high-spatial-frequency content
  attenuated by the instrument MTF is restored.
* **Denoise** — :func:`denoise`, dispatching the **profile-configurable**
  sub-step (ALG-ENH-BWLP/WAVE/PCA/MA/GAUSS/FFTDARK). The selector includes
  ``"none"`` so the sub-step can be disabled per sensor; the enhancement *stage*
  still always runs because MTFC is mandatory (REQ-F-ENH-03).

**Forced deviation from SDD <5.4.4> (libraries).** The SDD sketches the denoise
bodies as thin wrappers over ``skimage`` / ``pywt`` / ``scikit-image`` (RD-10).
``scikit-image`` and ``PyWavelets`` are **not** available in the target
runtime (only ``eopf``/``numpy``/``scipy``), so — mirroring the
dependency-minimal choice already made for the radiometric and TOA cores (which
re-implement e.g. the NOAA solar position in pure ``numpy`` rather than pull a
GPL dependency) — every kernel here is re-implemented in pure ``numpy``:

* :func:`butterworth_lowpass` — FFT-domain Butterworth low-pass built directly
  (the ``skimage.filters.butterworth`` frequency response);
* :func:`wavelet_visushrink` — a periodic, orthonormal multilevel Daubechies
  DWT with VisuShrink soft/hard thresholding (replacing ``pywt`` /
  ``skimage.restoration.denoise_wavelet``);
* :func:`pca_denoise` — low-rank reconstruction via :func:`numpy.linalg.svd`
  (mathematically identical to the heritage ``sklearn`` PCA reconstruction).

Private calibration data (the per-band PSF / MTF and its derived deconvolution
kernel) is **never** embedded; the kernel is supplied to :func:`mtf_compensate`
by the wrapper from the PSF/MTF ADF / sensor profile (REQ-AD-01, REQ-S-01/05).

Geometry convention: arrays are 2-D ``(line, detector)`` in focal-plane
geometry (ATBD <4.2>, SDD <5.4.4>).

*Trace:* REQ-F-ENH-01..03; DPM-M-ENH; ALG-ENH-*.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

import numpy as np
import numpy.typing as npt

from msi_processor.common.types import QAFlag

__all__ = [
    "DenoiseMethod",
    "EnhancementParams",
    "denoise",
    "butterworth_lowpass",
    "wavelet_visushrink",
    "pca_denoise",
    "moving_average",
    "gaussian_smooth",
    "fft_dark_subtract",
    "mtf_compensate",
    "flag_enhanced",
]

FloatArray = npt.NDArray[np.float32]
QAArray = npt.NDArray[np.uint16]

# Denoise selector. Extends the SDD <5.4.4> ``DenoiseMethod`` with ``"none"`` so
# the (configurable) denoise sub-step can be disabled per sensor profile while
# the enhancement stage still runs (MTFC is mandatory, REQ-F-ENH-03).
DenoiseMethod = Literal[
    "none",
    "butterworth",
    "wavelet",
    "pca",
    "moving_average",
    "gaussian",
    "fft_dark",
]

# Daubechies decomposition (scaling) coefficients ``dec_lo`` — public
# mathematical constants (PyWavelets convention); the orthonormal high-pass and
# the synthesis filters are derived from these in :func:`wavelet_visushrink`.
_DAUBECHIES: dict[str, tuple[float, ...]] = {
    "db1": (0.7071067811865476, 0.7071067811865476),
    "db2": (
        0.4829629131445341,
        0.8365163037378079,
        0.2241438680420134,
        -0.1294095225512604,
    ),
    "db3": (
        0.3326705529509569,
        0.8068915093133388,
        0.4598775021193313,
        -0.1350110200102546,
        -0.0854412738820267,
        0.0352262918857095,
    ),
    "db4": (
        0.2303778133088964,
        0.7148465705529154,
        0.6308807679298587,
        -0.0279837694168599,
        -0.1870348117190931,
        0.0308413818355607,
        0.0328830116668852,
        -0.0105974017850690,
    ),
}


@dataclass(frozen=True)
class EnhancementParams:
    """Tunable enhancement parameters (SDD <5.4.4>; DPM-PRM-ENH-01..05).

    Parameters
    ----------
    denoise_method:
        Selector for the **configurable** denoise sub-step (REQ-F-ENH-01).
        ``"none"`` disables denoising; the enhancement stage still runs because
        MTF compensation is mandatory (REQ-F-ENH-03).
    denoise_params:
        Per-method keyword parameters (e.g. ``{"cutoff_ratio": 0.2}`` for
        Butterworth); all per-band-overridable by the caller.
    bit_depth:
        Sensor radiometric depth; valid DN range ``[0, 2**bit_depth - 1]``
        (``DPM-PRM-GEN-01``, default 12) used by :func:`flag_enhanced`.
    fill_value:
        No-data sentinel DN; flagged :attr:`QAFlag.NO_DATA` when present.
    mtfc_regularization:
        Reserved regularisation strength for the full-deconvolution MTFC mode
        (Wiener NSR :math:`K` / Tikhonov :math:`\\gamma`); unused by the
        reference kernel-convolution path, whose regularisation is baked into
        the profile/ADF kernel (ATBD <5.5>).
    """

    denoise_method: DenoiseMethod = "none"
    denoise_params: Mapping[str, Any] = field(default_factory=dict)
    bit_depth: int = 12
    fill_value: Optional[float] = None
    mtfc_regularization: float = 0.0

    @property
    def max_dn(self) -> int:
        """Upper bound of the valid DN range, ``2**bit_depth - 1``."""
        return 2**self.bit_depth - 1


def mtf_compensate(image: npt.NDArray[Any], psf_kernel: npt.NDArray[Any]) -> FloatArray:
    r"""ALG-ENH-DECONV — MTF compensation (MTFC) via PSF deconvolution.

    The **mandatory** Level-1 restoration. The band is filtered with the
    profile/ADF-bound, PSF-derived spatial deconvolution kernel :math:`k`
    (heritage ``sharpening.deconvolution_kernel`` / ``cv2.filter2D``):

    .. math::

        \hat I = I \star k ,

    a cross-correlation with periodic (wrap-around) boundary handling. The
    kernel is the spatial-domain image of a regularised inverse of the system
    PSF (Wiener / Tikhonov / Richardson-Lucy candidate, down-selected per
    sensor; ATBD <5.5>), broader for the higher-resolution (panchromatic) band.

    Notes
    -----
    The kernel is supplied by the caller from the PSF/MTF ADF and is **never**
    embedded here (REQ-AD-01). A restoration kernel that integrates to one has
    unit DC gain, so the global radiance (mean) is conserved — the restoration
    is **radiometry-preserving**. Final clipping to the valid DN range is
    deferred to :func:`flag_enhanced` (mirroring the
    ``dn_to_radiance`` / ``flag_radiance`` split of the TOA core). Returns
    ``float32``.
    """
    restored = _correlate2d(image, psf_kernel)
    return restored.astype(np.float32)


def denoise(
    image: npt.NDArray[Any],
    method: DenoiseMethod,
    params: Mapping[str, Any],
    dark: Optional[npt.NDArray[Any]] = None,
) -> FloatArray:
    """Dispatch to the selected denoiser (heritage ``Denoiser.*``).

    Parameters
    ----------
    image:
        Input band, dims ``(line, detector)``.
    method:
        One of :data:`DenoiseMethod`. ``"none"`` returns the band unchanged
        (the configurable sub-step disabled, REQ-F-ENH-01).
    params:
        Per-method keyword parameters (see each kernel's defaults).
    dark:
        Dark reference frame, required only for ``"fft_dark"``.

    Returns
    -------
    numpy.ndarray
        The denoised band as ``float32``. Range clipping to the valid DN
        interval is centralised in :func:`flag_enhanced`.
    """
    img = np.asarray(image, dtype=np.float32)
    if method == "none":
        return img.astype(np.float32)
    if method == "butterworth":
        return butterworth_lowpass(
            img,
            cutoff_ratio=float(params.get("cutoff_ratio", 0.2)),
            order=float(params.get("order", 10.0)),
            squared=bool(params.get("squared", False)),
            npad=int(params.get("npad", 0)),
        )
    if method == "wavelet":
        return wavelet_visushrink(
            img,
            wavelet=str(params.get("wavelet", "db3")),
            levels=int(params.get("levels", 20)),
            sigma_scale=float(params.get("sigma_scale", 1.0 / 3.0)),
            mode=str(params.get("mode", "soft")),
        )
    if method == "pca":
        return pca_denoise(img, n_components=int(params.get("n_components", min(img.shape))))
    if method == "moving_average":
        return moving_average(img, n=int(params.get("n", 60)))
    if method == "gaussian":
        sigma = params.get("sigma")
        return gaussian_smooth(
            img,
            ksize=int(params.get("ksize", 5)),
            sigma=None if sigma is None else float(sigma),
        )
    if method == "fft_dark":
        if dark is None:
            raise ValueError("fft_dark denoise requires a dark reference frame")
        return fft_dark_subtract(img, dark)
    raise ValueError(f"Unknown denoise method '{method}'")


def butterworth_lowpass(
    image: npt.NDArray[Any],
    cutoff_ratio: float = 0.2,
    order: float = 10.0,
    squared: bool = False,
    npad: int = 0,
) -> FloatArray:
    r"""ALG-ENH-BWLP — frequency-domain Butterworth low-pass denoise.

    Re-implements the ``skimage.filters.butterworth`` low-pass response in pure
    ``numpy`` (heritage ``Denoiser.get_filtered_butterworth``):

    .. math::

        W(\mathbf q) = \Big(1 + (\lVert \mathbf q\rVert / f_c)^{2n}\Big)^{-s},

    with :math:`s = 1` for ``squared`` and :math:`s = 1/2` otherwise, ``f_c`` =
    ``cutoff_ratio`` and ``n`` = ``order``. Because :math:`W(\mathbf 0) = 1` the
    DC term is preserved, so the band mean is conserved (radiometry-preserving)
    while high frequencies (noise) are attenuated. ``npad`` edge-pads the band
    before the FFT to mitigate boundary ringing (Gibbs). Returns ``float32``.
    """
    img = np.asarray(image, dtype=np.float32)
    padded = np.pad(img, npad, mode="edge") if npad > 0 else img
    spectrum = np.fft.fftn(padded.astype(np.float64))
    wfilt = _butterworth_filter(padded.shape, cutoff_ratio, order, squared)
    filtered = np.real(np.fft.ifftn(spectrum * wfilt))
    if npad > 0:
        end_row = npad + img.shape[0]
        end_col = npad + img.shape[1]
        filtered = filtered[npad:end_row, npad:end_col]
    return filtered.astype(np.float32)


def wavelet_visushrink(
    image: npt.NDArray[Any],
    wavelet: str = "db3",
    levels: int = 20,
    sigma_scale: float = 1.0 / 3.0,
    mode: str = "soft",
) -> FloatArray:
    r"""ALG-ENH-WAVE — VisuShrink wavelet denoise (periodic Daubechies DWT).

    Re-implements ``skimage.restoration.denoise_wavelet`` (``method="VisuShrink"``)
    in pure ``numpy`` (heritage ``Denoiser.wavelet_denoising_cdk``): a multilevel
    orthonormal Daubechies decimated DWT with periodic boundary, MAD noise
    estimation and universal-threshold shrinkage of every detail band.

    The noise level is estimated from the finest diagonal detail band,
    :math:`\hat\sigma = \mathrm{median}(|d_{HH}^{(1)}|)/0.6745`, and the
    universal threshold is :math:`\lambda = s\,\hat\sigma\sqrt{2\ln N}` with
    ``sigma_scale`` :math:`s` and :math:`N` the pixel count. Detail
    coefficients are soft- or hard-thresholded; the coarse approximation is left
    intact. A flat band has zero detail energy, so it is preserved exactly (up
    to float round-off). Returns ``float32``.

    Notes
    -----
    The number of levels is capped at the largest depth for which both axes stay
    even and no shorter than the filter (so the periodic transform stays
    orthonormal / perfectly reconstructing).
    """
    img = np.asarray(image, dtype=np.float32)
    coeffs = _DAUBECHIES.get(wavelet)
    if coeffs is None:
        raise ValueError(f"Unsupported wavelet '{wavelet}'; expected one of {sorted(_DAUBECHIES)}")
    dec_lo = np.asarray(coeffs, dtype=np.float64)
    filt_len = dec_lo.shape[0]
    dec_hi = np.array([((-1) ** k) * dec_lo[filt_len - 1 - k] for k in range(filt_len)], dtype=np.float64)

    approx = img.astype(np.float64)
    shapes: list[tuple[int, int]] = []
    details: list[tuple[npt.NDArray[Any], npt.NDArray[Any], npt.NDArray[Any]]] = []
    for _ in range(max(0, int(levels))):
        rows, cols = approx.shape
        if rows < filt_len or cols < filt_len or rows % 2 != 0 or cols % 2 != 0:
            break
        ll, det = _wavedec2_level(approx, dec_lo, dec_hi)
        shapes.append((rows, cols))
        details.append(det)
        approx = ll

    if not details:
        return img.astype(np.float32)

    sigma = float(np.median(np.abs(details[0][2]))) / 0.6745
    n_pix = int(img.size)
    threshold = sigma_scale * sigma * math.sqrt(2.0 * math.log(n_pix)) if n_pix > 1 else 0.0

    for level in range(len(details) - 1, -1, -1):
        det = details[level]
        shrunk = (
            _threshold(det[0], threshold, mode),
            _threshold(det[1], threshold, mode),
            _threshold(det[2], threshold, mode),
        )
        approx = _waverec2_level(approx, shrunk, dec_lo, dec_hi, shapes[level])
    return approx.astype(np.float32)


def pca_denoise(image: npt.NDArray[Any], n_components: int) -> FloatArray:
    r"""ALG-ENH-PCA — low-rank PCA reconstruction denoise.

    Mathematically identical to the heritage ``sklearn`` PCA fit / inverse
    transform, re-expressed via the (economy) SVD of the column-centred band:
    with :math:`X = \bar X + U\Sigma V^{\!\top}` the rank-:math:`k`
    reconstruction :math:`\hat X = \bar X + U_k\Sigma_k V_k^{\!\top}` discards
    the low-variance (noise) subspace. Rows are samples and columns features, as
    in the heritage code. ``n_components`` is clamped to
    ``[1, min(line, detector)]``. A flat band (zero centred residual) is
    preserved exactly. Returns ``float32``.
    """
    img = np.asarray(image, dtype=np.float32)
    n_samples, n_features = img.shape
    k = max(1, min(int(n_components), min(n_samples, n_features)))
    mean = img.mean(axis=0, keepdims=True)
    centred = img - mean
    u, s, vt = np.linalg.svd(centred, full_matrices=False)
    s_k = s.copy()
    s_k[k:] = 0.0
    recon = (u * s_k) @ vt + mean
    return recon.astype(np.float32)


def moving_average(image: npt.NDArray[Any], n: int = 60) -> FloatArray:
    r"""ALG-ENH-MA — along-track :math:`(2N+1)` sliding-mean denoise.

    The canonical centred sliding mean over the line (along-track) axis adopted
    by ``msi-processor`` in place of the heritage row-block-to-scalar reduction
    (ATBD <5.4>):

    .. math::

        \hat I_{l,d} = \frac{1}{|\mathcal W_l|}\sum_{l'\in\mathcal W_l} I_{l',d},
        \qquad \mathcal W_l = [l-N,\,l+N] .

    The window is truncated (and the mean re-normalised by the available count)
    at the array borders, so a flat band is preserved exactly everywhere.
    Returns ``float32``.
    """
    img = np.asarray(image, dtype=np.float32)
    rows = img.shape[0]
    if n <= 0 or rows == 0:
        return img.astype(np.float32)
    cumsum = np.zeros((rows + 1, img.shape[1]), dtype=np.float64)
    np.cumsum(img.astype(np.float64), axis=0, out=cumsum[1:])
    index = np.arange(rows)
    lo = np.clip(index - n, 0, rows)
    hi = np.clip(index + n + 1, 0, rows)
    window_sum = cumsum[hi] - cumsum[lo]
    counts = (hi - lo).astype(np.float64)[:, None]
    return (window_sum / counts).astype(np.float32)


def gaussian_smooth(
    image: npt.NDArray[Any],
    ksize: int = 5,
    sigma: Optional[float] = None,
) -> FloatArray:
    r"""ALG-ENH-GAUSS — separable Gaussian-blur denoise.

    Convolves the band with a normalised, separable 2-D Gaussian of window
    ``ksize`` (heritage ``Denoiser.gaussian_filter_ips``, ``cv2.GaussianBlur``).
    When ``sigma`` is ``None`` it defaults to the band standard deviation (the
    heritage choice). The kernel integrates to one, so the band mean is
    conserved (radiometry-preserving); a degenerate :math:`\sigma \le 0`
    returns the band unchanged. Returns ``float32``.
    """
    img = np.asarray(image, dtype=np.float32)
    std = float(sigma) if sigma is not None else float(np.std(img))
    if std <= 0.0 or ksize <= 1:
        return img.astype(np.float32)
    radius = ksize // 2
    axis = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel_1d = np.exp(-(axis**2) / (2.0 * std * std))
    kernel_1d /= kernel_1d.sum()
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    return _correlate2d(img, kernel_2d)


def fft_dark_subtract(image: npt.NDArray[Any], dark: npt.NDArray[Any]) -> FloatArray:
    r"""ALG-ENH-FFTDARK — FFT-domain dark-pattern subtraction denoise.

    .. math::

        \hat I = \Re\big\{\mathcal F^{-1}(\mathcal F(I) - \mathcal F(D))\big\}

    (heritage ``Denoiser.dark_noise_removal``). By linearity of the Fourier
    transform this equals the spatial dark subtraction :math:`I - D`; the FFT
    route is retained where a frequency-selective dark notch is desired (cf. the
    radiometric ``remove_dark_fft``). The dark frame is cropped to the band
    extent and negative results are floored at 0. Returns ``float32``.
    """
    img = np.asarray(image, dtype=np.float32)
    drk = np.asarray(dark, dtype=np.float32)
    dark_crop = drk[: img.shape[0], : img.shape[1]]
    spectrum = np.fft.fft2(img) - np.fft.fft2(dark_crop)
    result = np.real(np.fft.ifft2(spectrum))
    return np.clip(result, 0.0, None).astype(np.float32)


def flag_enhanced(image: npt.NDArray[Any], params: EnhancementParams) -> tuple[FloatArray, QAArray]:
    r"""Clip to the valid range and flag saturation / no-data (SDD <5.4.4>).

    The enhanced band is clipped to ``[0, 2**bit_depth - 1]`` (REQ-D-05);
    samples at or above the ceiling — e.g. MTFC restoration overshoot — are
    flagged :attr:`QAFlag.SATURATED`; non-finite samples and any equal to
    ``params.fill_value`` are flagged :attr:`QAFlag.NO_DATA`. Mirrors the
    radiometric ``flag_saturation`` contract.

    Returns
    -------
    tuple of numpy.ndarray
        ``(clipped[float32], qa[uint16])`` of the same shape as ``image``.
    """
    data = np.asarray(image, dtype=np.float32)
    max_dn = params.max_dn
    qa = np.zeros(data.shape, dtype=np.uint16)
    finite = np.isfinite(data)
    qa[~finite] |= np.uint16(QAFlag.NO_DATA)
    qa[finite & (data >= np.float32(max_dn))] |= np.uint16(QAFlag.SATURATED)
    if params.fill_value is not None:
        qa[finite & (data == np.float32(params.fill_value))] |= np.uint16(QAFlag.NO_DATA)
    clipped = np.clip(np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0), 0.0, float(max_dn))
    return clipped.astype(np.float32), qa


# --------------------------------------------------------------------------- #
# Private helpers (CPM-free numpy)                                             #
# --------------------------------------------------------------------------- #


def _correlate2d(image: npt.NDArray[Any], kernel: npt.NDArray[Any]) -> FloatArray:
    """Centred 2-D cross-correlation with periodic boundary (``cv2.filter2D``).

    Periodic (wrap-around) handling makes a kernel that sums to one preserve the
    array total exactly, which is what keeps :func:`mtf_compensate` and
    :func:`gaussian_smooth` radiometry-preserving.
    """
    img = np.asarray(image, dtype=np.float32)
    k = np.asarray(kernel, dtype=np.float32)
    if k.ndim != 2:
        raise ValueError("kernel must be a 2-D array")
    kh, kw = k.shape
    ci, cj = kh // 2, kw // 2
    out = np.zeros_like(img, dtype=np.float64)
    for u in range(kh):
        for v in range(kw):
            coeff = float(k[u, v])
            if coeff == 0.0:
                continue
            out += coeff * np.roll(img.astype(np.float64), shift=(ci - u, cj - v), axis=(0, 1))
    return out.astype(np.float32)


def _butterworth_filter(
    shape: tuple[int, ...],
    cutoff_ratio: float,
    order: float,
    squared: bool,
) -> npt.NDArray[np.float64]:
    """Build the (low-pass) Butterworth frequency response (skimage convention)."""
    ranges = []
    for dim in shape:
        axis = np.arange((-(dim - 1)) // 2, (dim - 1) // 2 + 1) / (dim * cutoff_ratio)
        ranges.append(np.fft.ifftshift(axis**2))
    q2 = ranges[0][:, None] + ranges[1][None, :]
    wfilt = 1.0 / (1.0 + q2**order)
    if not squared:
        wfilt = np.sqrt(wfilt)
    return wfilt.astype(np.float64)


def _threshold(coeff: npt.NDArray[Any], value: float, mode: str) -> npt.NDArray[np.float64]:
    """Soft- or hard-threshold wavelet detail coefficients."""
    data = np.asarray(coeff, dtype=np.float64)
    if value <= 0.0:
        return data
    if mode == "hard":
        return np.where(np.abs(data) >= value, data, 0.0)
    return np.sign(data) * np.maximum(np.abs(data) - value, 0.0)


def _dwt_axis(
    array: npt.NDArray[Any],
    dec_lo: npt.NDArray[Any],
    dec_hi: npt.NDArray[Any],
    axis: int,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Single-level periodic DWT (decimating) along one axis."""
    moved = np.moveaxis(np.asarray(array, dtype=np.float64), axis, -1)
    n = moved.shape[-1]
    half = n // 2
    filt_len = dec_lo.shape[0]
    taps = (2 * np.arange(half)[:, None] + np.arange(filt_len)[None, :]) % n
    gathered = moved[..., taps]
    approx = np.moveaxis(gathered @ dec_lo, -1, axis)
    detail = np.moveaxis(gathered @ dec_hi, -1, axis)
    return approx, detail


def _idwt_axis(
    approx: npt.NDArray[Any],
    detail: npt.NDArray[Any],
    dec_lo: npt.NDArray[Any],
    dec_hi: npt.NDArray[Any],
    axis: int,
    n: int,
) -> npt.NDArray[np.float64]:
    """Inverse of :func:`_dwt_axis` (adjoint of the orthonormal analysis)."""
    approx_m = np.moveaxis(np.asarray(approx, dtype=np.float64), axis, -1)
    detail_m = np.moveaxis(np.asarray(detail, dtype=np.float64), axis, -1)
    half = approx_m.shape[-1]
    filt_len = dec_lo.shape[0]
    taps = (2 * np.arange(half)[:, None] + np.arange(filt_len)[None, :]) % n
    leading = approx_m.shape[:-1]
    rows = int(np.prod(leading)) if leading else 1
    contrib = approx_m[..., :, None] * dec_lo[None, :] + detail_m[..., :, None] * dec_hi[None, :]
    # Scatter-add the (half, filt_len) overlap-adding contributions of every row
    # into a flat buffer using 1-D linear indices (perfect-reconstruction adjoint).
    columns = taps.reshape(-1)
    linear = (np.arange(rows)[:, None] * n + columns[None, :]).reshape(-1)
    out_flat = np.zeros(rows * n, dtype=np.float64)
    np.add.at(out_flat, linear, contrib.reshape(-1))
    out = out_flat.reshape(leading + (n,))
    return np.moveaxis(out, -1, axis)


def _wavedec2_level(
    array: npt.NDArray[Any],
    dec_lo: npt.NDArray[Any],
    dec_hi: npt.NDArray[Any],
) -> tuple[npt.NDArray[np.float64], tuple[npt.NDArray[Any], npt.NDArray[Any], npt.NDArray[Any]]]:
    """One 2-D DWT level -> (approximation, (HL, LH, HH) detail bands)."""
    low_cols, high_cols = _dwt_axis(array, dec_lo, dec_hi, axis=1)
    ll, hl = _dwt_axis(low_cols, dec_lo, dec_hi, axis=0)
    lh, hh = _dwt_axis(high_cols, dec_lo, dec_hi, axis=0)
    return ll, (hl, lh, hh)


def _waverec2_level(
    approx: npt.NDArray[Any],
    details: tuple[npt.NDArray[Any], npt.NDArray[Any], npt.NDArray[Any]],
    dec_lo: npt.NDArray[Any],
    dec_hi: npt.NDArray[Any],
    shape: tuple[int, int],
) -> npt.NDArray[np.float64]:
    """Inverse of :func:`_wavedec2_level` to the given ``shape``."""
    hl, lh, hh = details
    rows, cols = shape
    low_cols = _idwt_axis(approx, hl, dec_lo, dec_hi, axis=0, n=rows)
    high_cols = _idwt_axis(lh, hh, dec_lo, dec_hi, axis=0, n=rows)
    return _idwt_axis(low_cols, high_cols, dec_lo, dec_hi, axis=1, n=cols)
