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

"""Unit tests for the enhancement core (ALG-ENH-*).

Every pure function is exercised with small, deterministic synthetic arrays:
MTF compensation recovers a sharper estimate of a blurred edge while preserving
radiometry (the band mean), and each denoise method reduces noise on a noisy
flat field while preserving the flat signal. Randomised inputs are seeded.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.enhancement.core import (
    EnhancementParams,
    butterworth_lowpass,
    denoise,
    fft_dark_subtract,
    flag_enhanced,
    gaussian_smooth,
    moving_average,
    mtf_compensate,
    pca_denoise,
    wavelet_visushrink,
)

# A normalised (sum == 1) Laplacian-sharpening kernel: unit DC gain, so the band
# mean is conserved while edges are boosted -- a stand-in for a PSF-derived MTFC
# deconvolution kernel.
_SHARPEN = np.array([[0.0, -1.0, 0.0], [-1.0, 5.0, -1.0], [0.0, -1.0, 0.0]], dtype=np.float32)


def _gaussian_psf(sigma: float = 1.0, radius: int = 2) -> np.ndarray:
    """Small normalised Gaussian point-spread function (sum == 1)."""
    axis = np.arange(-radius, radius + 1, dtype=np.float64)
    line = np.exp(-(axis**2) / (2.0 * sigma * sigma))
    kernel = np.outer(line, line)
    return (kernel / kernel.sum()).astype(np.float32)


def _gradient_energy(image: np.ndarray) -> float:
    """Sum of squared finite differences -- a proxy for high-frequency content."""
    gx = np.diff(image, axis=1)
    gy = np.diff(image, axis=0)
    return float(np.sum(gx * gx) + np.sum(gy * gy))


# --------------------------------------------------------------------------- #
# MTF compensation (mandatory; ALG-ENH-DECONV)                                #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_mtf_compensate_identity_kernel_is_identity():
    r"""A 1x1 unit kernel leaves the band unchanged."""
    image = np.array([[10.0, 20.0], [30.0, 40.0]], dtype=np.float32)
    restored = mtf_compensate(image, np.array([[1.0]], dtype=np.float32))
    assert_array_equal(restored, image)
    assert restored.dtype == np.float32


@pytest.mark.unit
def test_mtf_compensate_recovers_sharper_estimate():
    r"""MTFC on a blurred edge restores high-frequency content (ATBD <5.5>)."""
    sharp = np.zeros((32, 32), dtype=np.float32)
    sharp[:, 16:] = 1000.0
    blurred = mtf_compensate(sharp, _gaussian_psf(sigma=1.0))  # forward blur (kernel sums to 1)
    restored = mtf_compensate(blurred, _SHARPEN)
    # the restored band is sharper than the blurred input ...
    assert _gradient_energy(restored) > _gradient_energy(blurred)
    # ... and a closer estimate of the true sharp scene.
    assert np.linalg.norm(restored - sharp) < np.linalg.norm(blurred - sharp)


@pytest.mark.unit
def test_mtf_compensate_preserves_radiometry():
    r"""A unit-DC-gain kernel conserves the band mean (radiometry-preserving)."""
    rng = np.random.default_rng(1)
    image = rng.uniform(100.0, 900.0, size=(24, 20)).astype(np.float32)
    restored = mtf_compensate(image, _SHARPEN)
    assert_allclose(restored.mean(), image.mean(), rtol=1e-5)


# --------------------------------------------------------------------------- #
# Denoise dispatch + "none" (configurable sub-step; ALG-ENH-*)                #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_denoise_none_is_identity():
    r"""The disabled denoise sub-step returns the band unchanged as float32."""
    image = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    out = denoise(image, "none", {})
    assert_array_equal(out, image)
    assert out.dtype == np.float32


@pytest.mark.unit
def test_denoise_unknown_method_raises():
    r"""An unsupported denoise method raises ``ValueError`` in the pure core."""
    with pytest.raises(ValueError):
        denoise(np.zeros((4, 4), dtype=np.float32), "bogus", {})  # type: ignore[arg-type]


@pytest.mark.unit
def test_denoise_fft_dark_requires_dark():
    r"""``fft_dark`` without a dark reference raises ``ValueError``."""
    with pytest.raises(ValueError):
        denoise(np.zeros((4, 4), dtype=np.float32), "fft_dark", {})


@pytest.mark.unit
@pytest.mark.parametrize(
    "method, params",
    [
        ("butterworth", {}),
        ("wavelet", {}),
        ("pca", {"n_components": 1}),
        ("moving_average", {"n": 3}),
        ("gaussian", {"sigma": 2.0}),
    ],
)
def test_denoise_preserves_flat_signal(method, params):
    r"""Every denoiser leaves a constant (flat) band unchanged (radiometry)."""
    flat = np.full((32, 24), 200.0, dtype=np.float32)
    out = denoise(flat, method, params)
    assert_allclose(out, flat, atol=1e-3)


@pytest.mark.unit
@pytest.mark.parametrize(
    "method, params",
    [
        ("butterworth", {}),
        ("wavelet", {}),
        ("pca", {"n_components": 1}),
        ("moving_average", {"n": 3}),
        ("gaussian", {"sigma": 2.0}),
    ],
)
def test_denoise_reduces_noise(method, params):
    r"""Every denoiser reduces the noise of a noisy flat field."""
    rng = np.random.default_rng(42)
    base = np.full((48, 40), 300.0, dtype=np.float32)
    noisy = base + rng.normal(0.0, 15.0, size=base.shape).astype(np.float32)
    out = denoise(noisy, method, params)
    assert np.std(out - base) < np.std(noisy - base)


@pytest.mark.unit
def test_fft_dark_subtract_removes_dark_pattern():
    r"""FFT dark subtraction recovers the flat signal under a fixed dark pattern."""
    rng = np.random.default_rng(7)
    base = np.full((16, 16), 500.0, dtype=np.float32)
    dark = rng.normal(0.0, 20.0, size=base.shape).astype(np.float32)
    out = fft_dark_subtract(base + dark, dark)
    assert_allclose(out, base, atol=1e-2)


@pytest.mark.unit
def test_fft_dark_subtract_floors_negative():
    r"""Negative results (over-subtraction) are floored at 0."""
    image = np.array([[10.0, 10.0], [10.0, 10.0]], dtype=np.float32)
    dark = np.array([[20.0, 20.0], [20.0, 20.0]], dtype=np.float32)
    out = fft_dark_subtract(image, dark)
    assert np.all(out >= 0.0)


# --------------------------------------------------------------------------- #
# Individual denoise kernels -- properties                                     #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_butterworth_lowpass_preserves_dc_mean():
    r"""The low-pass keeps the DC term -> band mean is conserved."""
    rng = np.random.default_rng(3)
    image = rng.uniform(0.0, 1000.0, size=(32, 32)).astype(np.float32)
    out = butterworth_lowpass(image, cutoff_ratio=0.2, order=10.0)
    assert_allclose(out.mean(), image.mean(), rtol=1e-4)
    assert out.dtype == np.float32


@pytest.mark.unit
def test_wavelet_visushrink_preserves_flat_and_is_float32():
    r"""A flat band has zero detail energy -> preserved up to float round-off."""
    flat = np.full((32, 32), 123.0, dtype=np.float32)
    out = wavelet_visushrink(flat, wavelet="db3")
    assert_allclose(out, flat, atol=1e-3)
    assert out.dtype == np.float32


@pytest.mark.unit
def test_wavelet_visushrink_too_small_is_identity():
    r"""A band smaller than the filter is returned unchanged (no transform)."""
    tiny = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    out = wavelet_visushrink(tiny, wavelet="db3")
    assert_array_equal(out, tiny)


@pytest.mark.unit
def test_wavelet_visushrink_unsupported_wavelet_raises():
    r"""An unknown wavelet family raises ``ValueError``."""
    with pytest.raises(ValueError):
        wavelet_visushrink(np.zeros((8, 8), dtype=np.float32), wavelet="db99")


@pytest.mark.unit
def test_pca_denoise_clamps_components_and_preserves_flat():
    r"""``n_components`` is clamped and a flat band is reconstructed exactly."""
    flat = np.full((10, 6), 50.0, dtype=np.float32)
    out = pca_denoise(flat, n_components=999)  # clamped to min(shape)
    assert_allclose(out, flat, atol=1e-4)
    assert out.shape == flat.shape


@pytest.mark.unit
def test_moving_average_preserves_flat_at_borders():
    r"""The border-normalised sliding mean preserves a flat band everywhere."""
    flat = np.full((9, 4), 7.0, dtype=np.float32)
    out = moving_average(flat, n=3)
    assert_allclose(out, flat, atol=1e-5)


@pytest.mark.unit
def test_moving_average_smooths_alternating_rows():
    r"""A 3-row centred mean of an alternating signal tends to the row average."""
    image = np.tile(np.array([[0.0], [100.0]], dtype=np.float32), (4, 3))  # 8x3 stripes
    out = moving_average(image, n=1)
    # interior rows average three rows (e.g. 0,100,0 -> 33.33; 100,0,100 -> 66.67)
    assert out[1, 0] == pytest.approx(100.0 / 3.0, abs=1e-3)
    assert out[2, 0] == pytest.approx(200.0 / 3.0, abs=1e-3)


@pytest.mark.unit
def test_gaussian_smooth_zero_sigma_is_identity():
    r"""A degenerate sigma (flat band default) returns the band unchanged."""
    flat = np.full((8, 8), 42.0, dtype=np.float32)
    out = gaussian_smooth(flat)  # sigma defaults to std == 0 -> identity
    assert_array_equal(out, flat)


# --------------------------------------------------------------------------- #
# Clipping / no-data flagging (flag_enhanced)                                  #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_flag_enhanced_clips_range_and_flags_saturation():
    r"""Values >= the ceiling are flagged SATURATED and clipped; negatives floored."""
    params = EnhancementParams(bit_depth=12)  # max_dn == 4095
    image = np.array([[-5.0, 100.0, 4095.0, 5000.0]], dtype=np.float32)
    clipped, qa = flag_enhanced(image, params)
    assert_array_equal(clipped, [[0.0, 100.0, 4095.0, 4095.0]])
    assert_array_equal(qa, [[0, 0, int(QAFlag.SATURATED), int(QAFlag.SATURATED)]])
    assert clipped.dtype == np.float32
    assert qa.dtype == np.uint16


@pytest.mark.unit
def test_flag_enhanced_flags_non_finite_as_no_data():
    r"""Non-finite samples are flagged NO_DATA and zeroed."""
    params = EnhancementParams(bit_depth=12)
    image = np.array([[np.inf, np.nan, 3.0]], dtype=np.float32)
    clipped, qa = flag_enhanced(image, params)
    assert_array_equal(clipped, [[0.0, 0.0, 3.0]])
    assert_array_equal(qa, [[int(QAFlag.NO_DATA), int(QAFlag.NO_DATA), 0]])


@pytest.mark.unit
def test_flag_enhanced_flags_fill_value():
    r"""An explicit fill_value sample is flagged NO_DATA."""
    params = EnhancementParams(bit_depth=12, fill_value=7.0)
    _, qa = flag_enhanced(np.array([[7.0, 8.0]], dtype=np.float32), params)
    assert_array_equal(qa, [[int(QAFlag.NO_DATA), 0]])


@pytest.mark.unit
def test_enhancement_params_max_dn():
    r"""``max_dn`` is ``2**bit_depth - 1``."""
    assert EnhancementParams(bit_depth=12).max_dn == 4095
    assert EnhancementParams(bit_depth=8).max_dn == 255
