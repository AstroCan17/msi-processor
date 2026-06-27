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

"""Pure radiometric-correction core (C-PU-RAD; ALG-RAD-NUC/DARK/BPR/SAT).

CPM-free, I/O-free numpy functions implementing the radiometric algorithms of
ATBD <5.2>, ported faithfully from the heritage ``level_1.py`` ``NUC`` class
(``compute_nuc`` / ``apply_nuc_and_bpr``; RD-9). All arrays are processed in
``float32`` with a fixed operation order for reproducibility
(REQ-F-DEP-02, REQ-D-05).

Geometry convention: arrays are 2-D ``(line, detector)`` in focal-plane
geometry; per-detector ``gain``/``offset``/``dark`` are 1-D ``(detector,)``
vectors broadcast across lines (ATBD <4.2>, SDD <5.5>).

*Trace:* REQ-F-RAD-01..05; DPM-M-RAD; ALG-RAD-*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union

import numpy as np
import numpy.typing as npt

from msi_processor.common.types import QAFlag

__all__ = [
    "RadiometricParams",
    "estimate_nuc",
    "apply_nuc",
    "detect_bad_pixels",
    "replace_bad_pixels",
    "flag_saturation",
    "remove_dark_fft",
]

FloatArray = npt.NDArray[np.float32]
BoolArray = npt.NDArray[np.bool_]
QAArray = npt.NDArray[np.uint16]


@dataclass(frozen=True)
class RadiometricParams:
    """Tunable radiometric parameters (SDD <5.4.3>; DPM-PRM-RAD-01..04).

    Parameters
    ----------
    bit_depth:
        Sensor radiometric depth; valid DN range ``[0, 2**bit_depth - 1]``
        (``DPM-PRM-GEN-01``, default 12).
    g_min, g_max:
        Bad-pixel gain bounds (``DPM-PRM-RAD-02``). ``None`` disables that
        bound.
    saturation:
        Saturation threshold DN; defaults to ``2**bit_depth - 1`` when
        ``None``.
    fill_value:
        No-data sentinel DN; flagged ``NO_DATA`` when present.
    remove_dark_fft:
        Enable the optional FFT dark-noise pre-removal (``DPM-PRM-RAD-03``).
    """

    bit_depth: int = 12
    g_min: Optional[float] = None
    g_max: Optional[float] = None
    saturation: Optional[int] = None
    fill_value: Optional[int] = None
    remove_dark_fft: bool = False

    @property
    def max_dn(self) -> int:
        """Upper bound of the valid DN range, ``2**bit_depth - 1``."""
        return 2**self.bit_depth - 1


def estimate_nuc(
    dark: npt.NDArray[Any],
    flat: npt.NDArray[Any],
    cut_dark: int = 0,
    cut_flat: int = 0,
) -> tuple[FloatArray, FloatArray]:
    r"""ALG-RAD-NUC — estimate per-detector gain/offset (heritage ``compute_nuc``).

    From a dark frame :math:`D` and a flat-field frame :math:`F` (both
    ``(line, detector)``), reduce to per-detector column means and derive the
    normalising affine that maps every detector's flat response to the array
    mean :math:`\mu_F` and its dark to :math:`\mu_D`:

    .. math::

        g_d = \frac{\mu_F - \mu_D}{\bar F_d - \bar D_d}, \qquad
        o_d = \mu_F - g_d\,\bar F_d .

    Parameters
    ----------
    dark, flat:
        Dark / flat-field reference frames, dims ``(line, detector)``.
    cut_dark, cut_flat:
        Number of leading along-track rows to discard before reduction
        (edge-cut alignment; default 0).

    Returns
    -------
    tuple of ndarray
        ``(gain[detector], offset[detector])`` as ``float32``.

    Notes
    -----
    Detectors with :math:`\bar F_d = \bar D_d` yield a non-finite gain
    (NUC singularity); these are not raised here but are caught downstream by
    :func:`detect_bad_pixels` and repaired (SDD <5.4.3>).
    """
    dark_f = np.asarray(dark, dtype=np.float32)
    flat_f = np.asarray(flat, dtype=np.float32)
    if cut_dark:
        dark_f = dark_f[cut_dark:, :]
    if cut_flat:
        flat_f = flat_f[cut_flat:, :]

    dark_mean = np.mean(dark_f, axis=0)  # per-detector column mean, shape (detector,)
    flat_mean = np.mean(flat_f, axis=0)
    mu_dark = float(np.mean(dark_mean))
    mu_flat = float(np.mean(flat_mean))

    with np.errstate(divide="ignore", invalid="ignore"):
        gain = (mu_flat - mu_dark) / (flat_mean - dark_mean)
    offset = mu_flat - gain * flat_mean
    return gain.astype(np.float32), offset.astype(np.float32)


def apply_nuc(
    dn: npt.NDArray[Any],
    gain: npt.NDArray[Any],
    offset: npt.NDArray[Any],
    dark_offset: Union[npt.NDArray[Any], float],
) -> FloatArray:
    r"""ALG-RAD-DARK — apply the per-detector affine plus dark-offset.

    .. math::

        X^{(b)}_{l,d} = \mathrm{DN}^{(b)}_{l,d}\,g^{(b)}_d + o^{(b)}_d - k^{(b)}

    (heritage ``apply_nuc_and_bpr``). ``gain``/``offset`` are 1-D
    ``(detector,)`` vectors broadcast across lines; ``dark_offset`` is the
    per-band scalar :math:`k` (or a per-detector vector). Returns ``float32``.
    """
    dn_f = np.asarray(dn, dtype=np.float32)
    gain_f = np.asarray(gain, dtype=np.float32)
    offset_f = np.asarray(offset, dtype=np.float32)
    dark_f = np.asarray(dark_offset, dtype=np.float32)
    corrected = dn_f * gain_f + offset_f - dark_f
    return corrected.astype(np.float32)


def detect_bad_pixels(
    gain: npt.NDArray[Any],
    params: RadiometricParams,
    bpm: Optional[npt.NDArray[Any]],
) -> BoolArray:
    r"""ALG-RAD-BPR (detection) — flag bad detectors.

    A detector is bad when its gain falls outside the admissible bounds, when
    its gain is non-finite (NUC singularity), or when it is listed in the
    bad-pixel-map ADF:

    .. math::

        \text{bad}(d) \iff g_d \ge g_{\max} \;\vee\; g_d \le g_{\min}
        \;\vee\; \neg\,\mathrm{finite}(g_d) \;\vee\; \mathrm{bpm}(d).

    Returns a boolean array of shape ``(detector,)``.
    """
    gain_f = np.asarray(gain, dtype=np.float32)
    bad = ~np.isfinite(gain_f)
    if params.g_max is not None:
        bad |= gain_f >= np.float32(params.g_max)
    if params.g_min is not None:
        bad |= gain_f <= np.float32(params.g_min)
    if bpm is not None:
        bad |= np.asarray(bpm, dtype=bool)
    return bad.astype(bool)


def replace_bad_pixels(corrected: npt.NDArray[Any], bad: npt.NDArray[Any]) -> FloatArray:
    r"""ALG-RAD-BPR (replacement) — across-track neighbour interpolation.

    Repairs bad detectors column-wise (heritage ``apply_nuc_and_bpr``):

    .. math::

        X_{:,d} \leftarrow
        \begin{cases}
          X_{:,d_{\text{next valid}}}, & d = 0,\\
          X_{:,d-1}, & d \text{ and } d{+}1 \text{ both bad},\\
          \tfrac12\big(X_{:,d-1}+X_{:,d+1}\big), & d \text{ bad}, d{+}1 \text{ valid},\\
          X_{:,d-1}, & d = N_d - 1.
        \end{cases}

    The pass is sequential left-to-right and operates on a copy. If every
    detector is bad (degenerate input) the array is returned unchanged.
    Returns ``float32``.
    """
    out = np.array(corrected, dtype=np.float32, copy=True)
    bad_f = np.asarray(bad, dtype=bool)
    n_detectors = bad_f.shape[0]
    if n_detectors == 0 or not bad_f.any():
        return out
    if bad_f.all():
        return out

    if bad_f[0]:
        valid_index = int(np.argwhere(~bad_f)[0][0])
        out[:, 0] = out[:, valid_index]
    for d in range(1, n_detectors - 1):
        if bad_f[d]:
            if bad_f[d + 1]:
                out[:, d] = out[:, d - 1]
            else:
                out[:, d] = (out[:, d - 1] + out[:, d + 1]) / np.float32(2.0)
    if bad_f[-1]:
        out[:, -1] = out[:, -2]
    return out


def flag_saturation(corrected: npt.NDArray[Any], params: RadiometricParams) -> tuple[FloatArray, QAArray]:
    r"""ALG-RAD-SAT — clip to the valid range and flag saturation / no-data.

    Values at or above the saturation level (``params.saturation`` or
    ``2**bit_depth - 1``) are flagged :attr:`QAFlag.SATURATED`; non-finite
    values and any equal to ``params.fill_value`` are flagged
    :attr:`QAFlag.NO_DATA`. The data is then clipped to
    ``[0, 2**bit_depth - 1]`` (REQ-F-RAD-04, REQ-D-05).

    Returns
    -------
    tuple of ndarray
        ``(clipped[float32], qa[uint16])`` of the same shape as ``corrected``.
    """
    data = np.asarray(corrected, dtype=np.float32)
    max_dn = params.max_dn
    saturation = params.saturation if params.saturation is not None else max_dn

    qa = np.zeros(data.shape, dtype=np.uint16)
    finite = np.isfinite(data)
    qa[~finite] |= np.uint16(QAFlag.NO_DATA)
    qa[finite & (data >= np.float32(saturation))] |= np.uint16(QAFlag.SATURATED)
    if params.fill_value is not None:
        qa[finite & (data == np.float32(params.fill_value))] |= np.uint16(QAFlag.NO_DATA)

    clipped = np.clip(np.nan_to_num(data, nan=0.0, posinf=float(max_dn), neginf=0.0), 0.0, float(max_dn))
    return clipped.astype(np.float32), qa


def remove_dark_fft(dn: npt.NDArray[Any], dark: npt.NDArray[Any]) -> FloatArray:
    r"""Optional FFT dark-noise removal (heritage ``dark_noise_removal``).

    .. math::

        \hat I = \Re\big\{\mathcal F^{-1}(\mathcal F(I) - \mathcal F(D))\big\}

    By linearity of the Fourier transform this equals spatial dark
    subtraction :math:`I - D`; the FFT route is retained where a
    frequency-selective dark notch is desired (ATBD <5.4>, ALG-ENH-FFTDARK).
    The dark frame is cropped to the image extent and negative results are
    floored at 0 (upper clipping is deferred to :func:`flag_saturation`).
    Returns ``float32``.
    """
    dn_f = np.asarray(dn, dtype=np.float32)
    dark_f = np.asarray(dark, dtype=np.float32)
    dark_crop = dark_f[: dn_f.shape[0], : dn_f.shape[1]]
    spectrum = np.fft.fft2(dn_f) - np.fft.fft2(dark_crop)
    result = np.real(np.fft.ifft2(spectrum))
    result = np.clip(result, 0.0, None)
    return result.astype(np.float32)
