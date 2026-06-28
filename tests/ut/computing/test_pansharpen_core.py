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

"""Unit tests for the pan-sharpening core (ALG-PAN-ALIGN/FUSE).

Alignment reuses the co-registration estimator, so the same deterministic
feature-rich synthetic scene (Gaussian blobs cropped with a known offset) drives
the MS->PAN registration tests; the fusion and spectral-fidelity tests operate on
reflectance-scaled arrays so the ``[0, 1]`` clip and correlation metric are
checked against ground truth (REQ-F-PAN-01..02, REQ-F-DEP-02).
"""

import numpy as np
import pytest

from msi_processor.computing.coregistration.core import CoregParams
from msi_processor.computing.pansharpen.core import (
    OPERATIONAL_METHODS,
    align_ms_to_pan,
    fuse,
    spectral_fidelity,
)
from msi_processor.exceptions.errors import PansharpenError

# Known crop geometry of the synthetic scene (PAN / MS-band offset).
_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 8
_TY = 5


def _textured_scene(seed: int, size: int = _BASE, n_blobs: int = 150) -> np.ndarray:
    """A deterministic, feature-rich reflectance field (SIFT-friendly, in [0, 1])."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    field = np.full((size, size), 0.1)
    for _ in range(n_blobs):
        cy = rng.uniform(0, size)
        cx = rng.uniform(0, size)
        sigma = rng.uniform(1.5, 4.0)
        amp = rng.uniform(0.1, 0.6)
        field += amp * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma * sigma)))
    return np.clip(field, 0.0, 1.0).astype(np.float32)


def _pan_and_ms(seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(pan, ms_band)`` cropped from one scene with offset ``(_TX, _TY)``.

    A PAN point ``(x, y)`` matches MS point ``(x - _TX, y - _TY)``, so the
    MS -> PAN homography is a pure translation by ``(_TX, _TY)``.
    """
    base = _textured_scene(seed)
    r0, r1 = _ORIGIN, _ORIGIN + _WIN
    my0, my1 = _ORIGIN + _TY, _ORIGIN + _TY + _WIN
    mx0, mx1 = _ORIGIN + _TX, _ORIGIN + _TX + _WIN
    pan = base[r0:r1, r0:r1].copy()
    ms_band = base[my0:my1, mx0:mx1].copy()
    return pan, ms_band


def _params(**overrides: object) -> CoregParams:
    base: dict[str, object] = {"reference_band": "pan", "seed": 0}
    base.update(overrides)
    return CoregParams(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ALG-PAN-ALIGN                                                                #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_align_resamples_ms_onto_pan_grid():
    """Every MS band is warped onto the PAN (rows, cols) extent as float32."""
    pan, ms_band = _pan_and_ms()
    aligned = align_ms_to_pan({"b1": ms_band, "b2": ms_band}, pan, _params())
    assert set(aligned) == {"b1", "b2"}
    for arr in aligned.values():
        assert arr.shape == pan.shape
        assert arr.dtype == np.float32


@pytest.mark.unit
def test_align_recovers_known_shift():
    """The aligned MS band matches the PAN scene in the interior (translation undone)."""
    pan, ms_band = _pan_and_ms()
    aligned = align_ms_to_pan({"b1": ms_band}, pan, _params())["b1"]
    # Compare a central window robust to warp edge fill; structure should track PAN.
    sl = slice(_WIN // 4, 3 * _WIN // 4)
    corr = np.corrcoef(aligned[sl, sl].ravel(), pan[sl, sl].ravel())[0, 1]
    assert corr > 0.9


@pytest.mark.unit
def test_align_empty_stack_fails():
    """An empty MS stack is a fail-stop (REQ-F-PAN-01)."""
    pan, _ = _pan_and_ms()
    with pytest.raises(PansharpenError, match="at least one MS band"):
        align_ms_to_pan({}, pan, _params())


@pytest.mark.unit
def test_align_non_2d_pan_fails():
    """A PAN array that is not 2-D is rejected."""
    pan, ms_band = _pan_and_ms()
    with pytest.raises(PansharpenError, match="2-D array"):
        align_ms_to_pan({"b1": ms_band}, pan[np.newaxis, ...], _params())


@pytest.mark.unit
def test_align_featureless_band_fails():
    """A featureless band yields too few keypoints -> PansharpenError fail-stop."""
    pan, _ = _pan_and_ms()
    flat = np.full_like(pan, 0.3)
    with pytest.raises(PansharpenError, match="alignment failed"):
        align_ms_to_pan({"b1": flat}, pan, _params())


# --------------------------------------------------------------------------- #
# ALG-PAN-FUSE                                                                 #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_fuse_simple_mean_is_average():
    """simple_mean fuses each band as the per-pixel mean of MS and PAN."""
    pan = np.array([[0.2, 0.4], [0.6, 0.8]], dtype=np.float32)
    ms = np.array([[0.4, 0.4], [0.4, 0.4]], dtype=np.float32)
    fused = fuse({"b1": ms}, pan, "simple_mean")["b1"]
    expected = 0.5 * (ms + pan)
    np.testing.assert_allclose(fused, expected, rtol=1e-6)
    assert fused.dtype == np.float32


@pytest.mark.unit
def test_fuse_identity_when_ms_equals_pan():
    """Averaging two equal arrays returns the same array."""
    pan = np.array([[0.1, 0.9], [0.5, 0.3]], dtype=np.float32)
    fused = fuse({"b1": pan.copy()}, pan, "simple_mean")["b1"]
    np.testing.assert_allclose(fused, pan, rtol=1e-6)


@pytest.mark.unit
def test_fuse_clips_to_reflectance_range():
    """Fused values are clipped to the BOA reflectance range [0, 1]."""
    pan = np.array([[1.0, 0.0]], dtype=np.float32)
    ms = np.array([[1.6, -0.4]], dtype=np.float32)  # out-of-range inputs
    fused = fuse({"b1": ms}, pan, "simple_mean")["b1"]
    assert np.all((fused >= 0.0) & (fused <= 1.0))
    # 0.5*(1.6+1.0)=1.3 -> 1.0 ; 0.5*(-0.4+0.0)=-0.2 -> 0.0
    np.testing.assert_allclose(fused, np.array([[1.0, 0.0]], dtype=np.float32), rtol=1e-6)


@pytest.mark.unit
def test_fuse_unknown_method_fails():
    """An unrecognised method name is rejected."""
    pan = np.zeros((2, 2), dtype=np.float32)
    with pytest.raises(PansharpenError, match="Unknown fusion method"):
        fuse({"b1": pan}, pan, "nonsense")  # type: ignore[arg-type]


@pytest.mark.unit
def test_fuse_component_substitution_is_impl():
    """The component-substitution methods are deferred [impl] fail-stops."""
    pan = np.zeros((2, 2), dtype=np.float32)
    with pytest.raises(PansharpenError, match="not implemented"):
        fuse({"b1": pan}, pan, "brovey")


@pytest.mark.unit
def test_fuse_empty_stack_fails():
    """Fusing with no aligned bands is a fail-stop."""
    pan = np.zeros((2, 2), dtype=np.float32)
    with pytest.raises(PansharpenError, match="at least one aligned MS band"):
        fuse({}, pan, "simple_mean")


@pytest.mark.unit
def test_fuse_shape_mismatch_fails():
    """An aligned band whose shape differs from PAN is rejected."""
    pan = np.zeros((2, 2), dtype=np.float32)
    bad = np.zeros((3, 3), dtype=np.float32)
    with pytest.raises(PansharpenError, match="does not match PAN"):
        fuse({"b1": bad}, pan, "simple_mean")


@pytest.mark.unit
def test_operational_methods_are_simple_mean_only():
    """Only simple_mean is operational this increment; the rest are [impl]."""
    assert OPERATIONAL_METHODS == ("simple_mean",)


# --------------------------------------------------------------------------- #
# Spectral fidelity (REQ-F-PAN-02)                                            #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_fidelity_high_for_constant_pan():
    """With a constant PAN, the fused band is linear in MS -> correlation ~ 1."""
    rng = np.random.default_rng(0)
    ms = rng.uniform(0.0, 1.0, size=(8, 8)).astype(np.float32)
    pan = np.full((8, 8), 0.5, dtype=np.float32)
    fused = fuse({"b1": ms}, pan, "simple_mean")
    fidelity = spectral_fidelity({"b1": ms}, fused)
    assert fidelity["b1"] > 0.99


@pytest.mark.unit
def test_fidelity_zero_for_constant_band():
    """A constant (zero-variance) band has undefined correlation -> reported 0.0."""
    flat = np.full((4, 4), 0.3, dtype=np.float32)
    fidelity = spectral_fidelity({"b1": flat}, {"b1": flat})
    assert fidelity["b1"] == 0.0


@pytest.mark.unit
def test_fidelity_missing_reference_is_zero():
    """A fused band with no matching MS reference reports 0.0 fidelity."""
    out = np.array([[0.1, 0.2]], dtype=np.float32)
    fidelity = spectral_fidelity({}, {"b1": out})
    assert fidelity["b1"] == 0.0
