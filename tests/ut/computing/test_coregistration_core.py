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

"""Unit tests for the co-registration core (ALG-COR-FEAT/HOM/WARP).

Deterministic, synthetic scenes: a textured base field is cropped twice with a
known integer offset to build a reference band and a shifted band whose exact
inter-band transform is known, so each pure function can be checked against
ground truth with fixed seeds (REQ-F-DEP-02).
"""

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.coregistration.core import (
    CoregParams,
    coregister,
    detect_and_match,
    estimate_homography,
    warp_qa,
    warp_to_reference,
)
from msi_processor.exceptions.errors import CoregistrationError

# Known crop geometry of the synthetic scene (reference / shifted-band offset).
_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 8
_TY = 5


def _textured_scene(seed: int, size: int = _BASE, n_blobs: int = 150) -> np.ndarray:
    """A deterministic, feature-rich field of Gaussian blobs (SIFT-friendly)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    field = np.full((size, size), 200.0)
    for _ in range(n_blobs):
        cy = rng.uniform(0, size)
        cx = rng.uniform(0, size)
        sigma = rng.uniform(1.5, 4.0)
        amp = rng.uniform(200.0, 1500.0)
        field += amp * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma * sigma)))
    return field.astype(np.float32)


def _shifted_pair(seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(reference, band)`` cropped from one scene with offset ``(_TX, _TY)``.

    A reference point ``(x, y)`` matches band point ``(x - _TX, y - _TY)``, so the
    band -> reference homography is a pure translation by ``(_TX, _TY)``.
    """
    base = _textured_scene(seed)
    r0, r1 = _ORIGIN, _ORIGIN + _WIN
    by0, by1 = _ORIGIN + _TY, _ORIGIN + _TY + _WIN
    bx0, bx1 = _ORIGIN + _TX, _ORIGIN + _TX + _WIN
    reference = base[r0:r1, r0:r1].copy()
    band = base[by0:by1, bx0:bx1].copy()
    return reference, band


def _params(**overrides: object) -> CoregParams:
    base = {"reference_band": "ref", "seed": 0}
    base.update(overrides)
    return CoregParams(**base)  # type: ignore[arg-type]


@pytest.mark.unit
def test_detect_and_match_finds_correspondences():
    """ALG-COR-FEAT yields enough band<->reference tie points on a textured scene."""
    reference, band = _shifted_pair()
    src_pts, dst_pts = detect_and_match(band, reference, _params())
    assert src_pts.shape[0] == dst_pts.shape[0]
    assert src_pts.shape[0] >= 8
    assert src_pts.shape[1:] == (1, 2)
    assert src_pts.dtype == np.float32
    # The matched offset (band -> reference) is the known translation on average.
    mean_shift = (dst_pts.reshape(-1, 2) - src_pts.reshape(-1, 2)).mean(axis=0)
    assert mean_shift[0] == pytest.approx(_TX, abs=1.0)
    assert mean_shift[1] == pytest.approx(_TY, abs=1.0)


@pytest.mark.unit
def test_estimate_homography_recovers_known_shift():
    """ALG-COR-HOM recovers the known translation homography within tolerance."""
    reference, band = _shifted_pair()
    homography, residual = estimate_homography(band, reference, _params())
    assert homography.shape == (3, 3)
    # Translation terms recover (_TX, _TY); the linear part is ~identity.
    assert homography[0, 2] == pytest.approx(_TX, abs=1.0)
    assert homography[1, 2] == pytest.approx(_TY, abs=1.0)
    assert homography[0, 0] == pytest.approx(1.0, abs=0.05)
    assert homography[1, 1] == pytest.approx(1.0, abs=0.05)
    assert homography[0, 1] == pytest.approx(0.0, abs=0.05)
    assert homography[1, 0] == pytest.approx(0.0, abs=0.05)
    assert residual.n_inliers >= 4
    assert residual.rms_residual_px < 1.0
    assert residual.accepted  # max_residual is None -> any sufficient solution accepted


@pytest.mark.unit
def test_warp_to_reference_realigns_band():
    """ALG-COR-WARP re-aligns the band; residual misregistration collapses."""
    reference, band = _shifted_pair()
    homography, _ = estimate_homography(band, reference, _params())
    warped = warp_to_reference(band, homography, (_WIN, _WIN))
    assert warped.shape == reference.shape

    interior = (slice(_TY + 3, _WIN - 3), slice(_TX + 3, _WIN - 3))
    err_before = np.abs(band[interior].astype(float) - reference[interior].astype(float)).mean()
    err_after = np.abs(warped[interior].astype(float) - reference[interior].astype(float)).mean()
    # Co-registration removes the bulk inter-band shift (>20x residual reduction).
    assert err_after < 0.05 * err_before
    # Output radiometry is the original band resampled (radiance units, not the
    # 0-255 CLAHE matching surrogate).
    assert warped[interior].max() > 255.0


@pytest.mark.unit
def test_warp_to_reference_preserves_dtype():
    """The warp keeps the input radiometric dtype (radiometry-preserving)."""
    reference, band = _shifted_pair()
    homography, _ = estimate_homography(band, reference, _params())
    warped = warp_to_reference(band.astype(np.float32), homography, (_WIN, _WIN))
    assert warped.dtype == np.float32


@pytest.mark.unit
def test_warp_qa_nearest_neighbour_preserves_flag_values():
    """QA masks warp with nearest-neighbour, so exact bit patterns are preserved."""
    flag = np.uint16(QAFlag.NO_DATA | QAFlag.SATURATED)  # == 5
    qa = np.zeros((_WIN, _WIN), dtype=np.uint16)
    qa[40:60, 40:60] = flag
    translate = np.array([[1.0, 0.0, 4.0], [0.0, 1.0, 3.0], [0.0, 0.0, 1.0]], dtype=np.float64)
    warped = warp_qa(qa, translate, (_WIN, _WIN))
    assert warped.dtype == np.uint16
    # No interpolation artefacts: only the original flag value or 0 appear.
    assert set(np.unique(warped).tolist()) <= {0, int(flag)}
    # The flagged block translated by the homography (nearest-neighbour exact).
    assert warped[43, 44] == int(flag)


@pytest.mark.unit
def test_warp_qa_identity_is_passthrough():
    """An identity homography leaves the QA mask unchanged."""
    qa = np.zeros((16, 16), dtype=np.uint16)
    qa[2, 3] = np.uint16(QAFlag.DEFECTIVE)
    identity = np.eye(3, dtype=np.float64)
    assert_array_equal(warp_qa(qa, identity, (16, 16)), qa)


@pytest.mark.unit
def test_keypoint_gate_rejects_no_overlap_case():
    """A featureless reference fails the keypoint gate (REQ-F-COR-03 fail-stop)."""
    _, band = _shifted_pair()
    flat = np.full((_WIN, _WIN), 500.0, dtype=np.float32)
    with pytest.raises(CoregistrationError):
        detect_and_match(band, flat, _params())
    with pytest.raises(CoregistrationError):
        estimate_homography(band, flat, _params())


@pytest.mark.unit
def test_acceptance_gate_rejects_excessive_residual():
    """A residual above max_residual is reported not-accepted and fails coregister."""
    reference, band = _shifted_pair()
    _, residual = estimate_homography(band, reference, _params())
    assert residual.rms_residual_px > 0.0
    # A budget below the measured residual must reject this solution.
    tight = _params(max_residual=residual.rms_residual_px * 0.5)
    _, rejected = estimate_homography(band, reference, tight)
    assert not rejected.accepted
    with pytest.raises(CoregistrationError):
        coregister({"ref": reference, "b3": band}, tight)


@pytest.mark.unit
def test_coregister_aligns_multiband_stack():
    """coregister returns every band on the reference grid with accepted residuals."""
    reference, band = _shifted_pair()
    base = _textured_scene(42)
    cy0, cy1 = _ORIGIN - 4, _ORIGIN - 4 + _WIN
    cx0, cx1 = _ORIGIN + 3, _ORIGIN + 3 + _WIN
    band2 = base[cy0:cy1, cx0:cx1].copy()
    registered, residuals = coregister({"ref": reference, "b3": band, "b4": band2}, _params())
    assert set(registered) == {"ref", "b3", "b4"}
    for arr in registered.values():
        assert arr.shape == (_WIN, _WIN)
    # The reference passes through untouched.
    assert_array_equal(registered["ref"], reference)
    assert {r.band for r in residuals} == {"b3", "b4"}
    assert all(r.accepted for r in residuals)


@pytest.mark.unit
def test_coregister_missing_reference_raises():
    """An absent reference band is a fail-stop condition."""
    reference, band = _shifted_pair()
    with pytest.raises(CoregistrationError):
        coregister({"b3": band, "b4": reference}, _params(reference_band="ref"))


@pytest.mark.unit
def test_estimate_homography_is_deterministic():
    """A fixed seed makes RANSAC reproducible (bit-identical H)."""
    reference, band = _shifted_pair()
    homography_a, _ = estimate_homography(band, reference, _params(seed=7))
    homography_b, _ = estimate_homography(band, reference, _params(seed=7))
    assert_array_equal(homography_a, homography_b)


@pytest.mark.unit
def test_pan_band_uses_higher_keypoint_gate():
    """pan_bands raises the keypoint gate to min_keypoints_pan for that band."""
    params = _params()
    assert params.min_keypoints_for("b2") == params.min_keypoints
    pan = _params(pan_bands=("pan",), min_keypoints_pan=40)
    assert pan.min_keypoints_for("pan") == 40
    assert pan.min_keypoints_for("b2") == pan.min_keypoints
