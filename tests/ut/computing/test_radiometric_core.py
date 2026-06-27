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

"""Unit tests for the radiometric core (ALG-RAD-NUC/DARK/BPR/SAT).

Every pure function is exercised with tiny synthetic arrays and hand-computed
expected values.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.radiometric.core import (
    RadiometricParams,
    apply_nuc,
    detect_bad_pixels,
    estimate_nuc,
    flag_saturation,
    remove_dark_fft,
    replace_bad_pixels,
)


@pytest.mark.unit
def test_estimate_nuc_affine_formula():
    r"""Column means Dbar=[1,2,3], Fbar=[3,4,5] -> g=[1,1,1], o=[1,0,-1]."""
    dark = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]], dtype=np.float32)
    flat = np.array([[3.0, 4.0, 5.0], [3.0, 4.0, 5.0]], dtype=np.float32)
    gain, offset = estimate_nuc(dark, flat)
    # mu_D = 2, mu_F = 4 ; g = (4-2)/(Fbar-Dbar) = 2/2 = 1 ; o = 4 - g*Fbar
    assert_allclose(gain, [1.0, 1.0, 1.0])
    assert_allclose(offset, [1.0, 0.0, -1.0])
    assert gain.dtype == np.float32
    assert offset.dtype == np.float32


@pytest.mark.unit
def test_estimate_nuc_honours_edge_cut():
    """Leading garbage rows are discarded by cut_dark / cut_flat."""
    dark = np.array([[999.0, 999.0, 999.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]], dtype=np.float32)
    flat = np.array([[999.0, 999.0, 999.0], [3.0, 4.0, 5.0], [3.0, 4.0, 5.0]], dtype=np.float32)
    gain, offset = estimate_nuc(dark, flat, cut_dark=1, cut_flat=1)
    assert_allclose(gain, [1.0, 1.0, 1.0])
    assert_allclose(offset, [1.0, 0.0, -1.0])


@pytest.mark.unit
def test_estimate_nuc_singularity_is_non_finite():
    """A detector with Fbar == Dbar yields a non-finite gain (NUC singularity)."""
    dark = np.array([[1.0, 2.0], [1.0, 2.0]], dtype=np.float32)
    flat = np.array([[1.0, 5.0], [1.0, 5.0]], dtype=np.float32)
    gain, _ = estimate_nuc(dark, flat)
    assert not np.isfinite(gain[0])  # Fbar[0]==Dbar[0]==1 -> division by zero
    assert np.isfinite(gain[1])


@pytest.mark.unit
def test_apply_nuc_affine_with_dark_offset():
    r"""X = dn*g + o - k, with g/o broadcast across lines and scalar k."""
    dn = np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]], dtype=np.float32)
    gain = np.array([1.0, 2.0, 1.0], dtype=np.float32)
    offset = np.array([0.0, 0.0, 5.0], dtype=np.float32)
    corrected = apply_nuc(dn, gain, offset, dark_offset=5.0)
    expected = np.array([[5.0, 35.0, 30.0], [35.0, 95.0, 60.0]], dtype=np.float32)
    assert_array_equal(corrected, expected)
    assert corrected.dtype == np.float32


@pytest.mark.unit
def test_detect_bad_pixels_thresholds_and_non_finite():
    """Out-of-bound and non-finite gains are flagged bad."""
    gain = np.array([0.5, 1.0, 5.0, np.nan], dtype=np.float32)
    params = RadiometricParams(g_min=0.6, g_max=4.0)
    bad = detect_bad_pixels(gain, params, bpm=None)
    assert_array_equal(bad, [True, False, True, True])


@pytest.mark.unit
def test_detect_bad_pixels_merges_bad_pixel_map():
    """The bad-pixel-map ADF contributes additional bad detectors."""
    gain = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    params = RadiometricParams(g_min=0.0, g_max=10.0)
    bpm = np.array([False, True, False])
    bad = detect_bad_pixels(gain, params, bpm=bpm)
    assert_array_equal(bad, [False, True, False])


@pytest.mark.unit
def test_replace_bad_pixels_all_branches():
    """Edge copy, interior average, and trailing-edge copy across two lines."""
    corrected = np.array(
        [[100.0, 200.0, 999.0, 400.0, 500.0], [110.0, 210.0, 999.0, 410.0, 510.0]],
        dtype=np.float32,
    )
    bad = np.array([True, False, True, False, True])
    result = replace_bad_pixels(corrected, bad)
    expected = np.array(
        [[200.0, 200.0, 300.0, 400.0, 400.0], [210.0, 210.0, 310.0, 410.0, 410.0]],
        dtype=np.float32,
    )
    assert_array_equal(result, expected)


@pytest.mark.unit
def test_replace_bad_pixels_cluster_uses_left_neighbour():
    """Two consecutive bad detectors: the first copies its left neighbour."""
    corrected = np.array([[10.0, 20.0, 30.0, 40.0]], dtype=np.float32)
    bad = np.array([False, True, True, False])
    result = replace_bad_pixels(corrected, bad)
    # d=1 (next also bad) -> copy left (10); d=2 -> average(left=10, right=40) = 25
    assert_array_equal(result, [[10.0, 10.0, 25.0, 40.0]])


@pytest.mark.unit
def test_replace_bad_pixels_all_bad_returns_unchanged():
    """A fully-bad array is returned unchanged (degenerate input guard)."""
    corrected = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    bad = np.array([True, True])
    result = replace_bad_pixels(corrected, bad)
    assert_array_equal(result, corrected)


@pytest.mark.unit
def test_flag_saturation_clips_and_flags():
    """Saturated, over-range and non-finite samples are clipped and flagged."""
    params = RadiometricParams(bit_depth=4)  # max_dn = 15
    corrected = np.array([[-2.0, 5.0, 15.0, 20.0, np.inf]], dtype=np.float32)
    clipped, qa = flag_saturation(corrected, params)
    assert_array_equal(clipped, [[0.0, 5.0, 15.0, 15.0, 15.0]])
    expected_qa = np.array(
        [[0, 0, int(QAFlag.SATURATED), int(QAFlag.SATURATED), int(QAFlag.NO_DATA)]],
        dtype=np.uint16,
    )
    assert_array_equal(qa, expected_qa)
    assert clipped.dtype == np.float32
    assert qa.dtype == np.uint16


@pytest.mark.unit
def test_flag_saturation_flags_fill_value():
    """An explicit fill_value sample is flagged NO_DATA."""
    params = RadiometricParams(bit_depth=12, fill_value=7)
    corrected = np.array([[7.0, 8.0]], dtype=np.float32)
    _, qa = flag_saturation(corrected, params)
    assert_array_equal(qa, [[int(QAFlag.NO_DATA), 0]])


@pytest.mark.unit
def test_remove_dark_fft_equals_spatial_subtraction():
    """By linearity of the FFT, the result equals dn - dark (floored at 0)."""
    dn = np.array([[10.0, 20.0], [30.0, 40.0]], dtype=np.float32)
    dark = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    result = remove_dark_fft(dn, dark)
    assert_allclose(result, [[9.0, 18.0], [27.0, 36.0]], atol=1e-3)
    assert result.dtype == np.float32


@pytest.mark.unit
def test_remove_dark_fft_floors_negative_at_zero():
    """Negative results are floored at zero (upper clipping is deferred)."""
    dn = np.array([[1.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    dark = np.array([[2.0, 0.0], [0.0, 0.0]], dtype=np.float32)
    result = remove_dark_fft(dn, dark)
    assert_allclose(result, [[0.0, 1.0], [1.0, 1.0]], atol=1e-3)
