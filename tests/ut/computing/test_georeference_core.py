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

"""Unit tests for the geo-referencing core (ALG-GEO-GSD/GCP/RESAMP/ORTHO).

Deterministic, synthetic scenes with fixed seeds (REQ-F-DEP-02): a textured base
field is cropped twice with a known integer offset so the ground-control
refinement recovers a known transform against a synthetic geolocated reference;
the cartographic-grid primitives are checked against analytically known
affine/CRS/corner coordinates. The rigorous viewing-model/DEM bodies are
``[impl]`` and verified to fail-stop (xfail).
"""

import numpy as np
import pytest
from affine import Affine
from numpy.testing import assert_allclose
from rasterio.crs import CRS

from msi_processor.computing.coregistration.core import CoregParams
from msi_processor.computing.georeference.core import (
    GeoreferenceParams,
    PlatformState,
    assign_grid,
    build_geotransform,
    compute_gsd,
    gcp_refine,
    orbit_state,
    orthorectify,
    resample_to_grid,
)
from msi_processor.exceptions.errors import GeolocationError

# Known crop geometry of the synthetic scene (reference / shifted-band offset).
_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 8
_TY = 5

# A known cartographic grid (UTM 35N) used for the affine/CRS/resampling tests.
_UTM35N_WKT = CRS.from_epsg(32635).to_wkt()
_ULX = 600000.0
_ULY = 4500000.0


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
    """Return ``(reference, image)`` cropped from one scene with offset ``(_TX, _TY)``.

    A reference point ``(x, y)`` matches image point ``(x - _TX, y - _TY)``, so the
    image -> reference homography is a pure translation by ``(_TX, _TY)``.
    """
    base = _textured_scene(seed)
    r0, r1 = _ORIGIN, _ORIGIN + _WIN
    by0, by1 = _ORIGIN + _TY, _ORIGIN + _TY + _WIN
    bx0, bx1 = _ORIGIN + _TX, _ORIGIN + _TX + _WIN
    reference = base[r0:r1, r0:r1].copy()
    image = base[by0:by1, bx0:bx1].copy()
    return reference, image


def _params(**overrides: object) -> GeoreferenceParams:
    base: dict[str, object] = {"resolution": 10.0, "min_gcp": 8, "coreg": CoregParams(reference_band="", seed=0)}
    base.update(overrides)
    return GeoreferenceParams(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ALG-GEO-GSD                                                                  #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_compute_gsd_pinhole_relation():
    """ALG-GEO-GSD: GSD = H*p/f (heritage pinhole relation)."""
    gsd = compute_gsd(altitude_m=500_000.0, pixel_pitch_m=5.5e-6, focal_length_m=845e-6)
    assert gsd == pytest.approx(500_000.0 * 5.5e-6 / 845e-6)


@pytest.mark.unit
def test_compute_gsd_rejects_nonpositive_focal_length():
    """A non-positive focal length is a fail-stop condition."""
    with pytest.raises(GeolocationError):
        compute_gsd(500_000.0, 5.5e-6, 0.0)


# --------------------------------------------------------------------------- #
# ALG-GEO-GCP                                                                  #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_gcp_refine_recovers_known_offset():
    """ALG-GEO-GCP recovers the known translation against a geolocated reference."""
    reference, image = _shifted_pair()
    refined, refinement = gcp_refine(image, reference, _params())
    # The recovered homography is the known translation (image -> reference).
    assert refinement.homography.shape == (3, 3)
    assert refinement.homography[0, 2] == pytest.approx(_TX, abs=1.0)
    assert refinement.homography[1, 2] == pytest.approx(_TY, abs=1.0)
    assert refinement.n_gcp >= 8
    assert refinement.rms_residual_px < 1.0
    # The refined image is aligned to the reference grid; residual collapses.
    assert refined.shape == reference.shape
    interior = (slice(_TY + 3, _WIN - 3), slice(_TX + 3, _WIN - 3))
    err_before = np.abs(image[interior].astype(float) - reference[interior].astype(float)).mean()
    err_after = np.abs(refined[interior].astype(float) - reference[interior].astype(float)).mean()
    assert err_after < 0.05 * err_before


@pytest.mark.unit
def test_gcp_gate_rejects_insufficient_points():
    """A min_gcp above the achievable inlier count is rejected fail-stop."""
    reference, image = _shifted_pair()
    with pytest.raises(GeolocationError):
        gcp_refine(image, reference, _params(min_gcp=100_000))


@pytest.mark.unit
def test_gcp_refine_wraps_matching_failure_as_geolocation_error():
    """A featureless reference (no SIFT keypoints) surfaces as GeolocationError."""
    _, image = _shifted_pair()
    flat = np.full((_WIN, _WIN), 500.0, dtype=np.float32)
    with pytest.raises(GeolocationError):
        gcp_refine(image, flat, _params())


@pytest.mark.unit
def test_gcp_refine_is_deterministic():
    """A fixed seed makes the GCP refinement reproducible (bit-identical H)."""
    reference, image = _shifted_pair()
    _, a = gcp_refine(image, reference, _params(coreg=CoregParams(reference_band="", seed=7)))
    _, b = gcp_refine(image, reference, _params(coreg=CoregParams(reference_band="", seed=7)))
    np.testing.assert_array_equal(a.homography, b.homography)


# --------------------------------------------------------------------------- #
# ALG-GEO-RESAMP (build_geotransform / assign_grid / resample_to_grid)         #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_build_geotransform_matches_known_affine_and_crs():
    """build_geotransform yields the GDAL north-up affine + CRS for a known grid."""
    geo = build_geotransform(_ULX, _ULY, 10.0, _UTM35N_WKT)
    assert geo.to_affine() == Affine.from_gdal(_ULX, 10.0, 0.0, _ULY, 0.0, -10.0)
    assert geo.gdal_tuple == (_ULX, 10.0, 0.0, _ULY, 0.0, -10.0)
    assert CRS.from_wkt(geo.crs_wkt).to_epsg() == 32635


@pytest.mark.unit
def test_build_geotransform_rejects_nonpositive_resolution():
    """A non-positive target resolution is a fail-stop condition."""
    with pytest.raises(GeolocationError):
        build_geotransform(_ULX, _ULY, 0.0, _UTM35N_WKT)


@pytest.mark.unit
def test_assign_grid_cell_centre_axes():
    """assign_grid returns the expected cell-centre x/y axes for a known grid."""
    geo = build_geotransform(_ULX, _ULY, 10.0, _UTM35N_WKT)
    grid = assign_grid((5, 4), geo)  # (height, width)
    assert grid.shape == (5, 4)
    # Column centres: ulx + (c + 0.5) * xres.
    assert_allclose(grid.x, [_ULX + 5.0, _ULX + 15.0, _ULX + 25.0, _ULX + 35.0])
    # Row centres: uly - (r + 0.5) * yres.
    assert_allclose(grid.y, [_ULY - 5.0, _ULY - 15.0, _ULY - 25.0, _ULY - 35.0, _ULY - 45.0])


@pytest.mark.unit
def test_resample_to_grid_places_feature_on_known_grid():
    """ALG-GEO-RESAMP resamples a band to a known grid with correct corner coords."""
    src = np.zeros((4, 4), dtype=np.float32)
    src[1, 2] = 100.0  # source cell centre (600050, 4499970)
    src_geo = build_geotransform(_ULX, _ULY, 20.0, _UTM35N_WKT)
    dst_geo = build_geotransform(_ULX, _ULY, 10.0, _UTM35N_WKT)

    out = resample_to_grid(src, src_geo, dst_geo, (8, 8), "nearest")
    assert out.shape == (8, 8)
    assert out.dtype == np.float32
    # The grid corner coordinate is preserved exactly (north-up affine).
    assert dst_geo.to_affine() * (0, 0) == (_ULX, _ULY)
    # Nearest resampling onto the 10 m grid preserves the source value and places
    # it deterministically where the source cell maps (row 2, col 4).
    assert out.max() == pytest.approx(100.0)
    assert np.unravel_index(int(np.argmax(out)), out.shape) == (2, 4)


@pytest.mark.unit
def test_resample_to_grid_preserves_dtype_uint16():
    """The resample preserves the input dtype (e.g. packed uint16 reflectance)."""
    src = np.zeros((4, 4), dtype=np.uint16)
    src[2, 2] = 4095
    src_geo = build_geotransform(_ULX, _ULY, 10.0, _UTM35N_WKT)
    dst_geo = build_geotransform(_ULX, _ULY, 10.0, _UTM35N_WKT)
    out = resample_to_grid(src, src_geo, dst_geo, (4, 4), "nearest")
    assert out.dtype == np.uint16
    # Same grid -> identity resample.
    np.testing.assert_array_equal(out, src)


# --------------------------------------------------------------------------- #
# ALG-GEO-ORBIT / ALG-GEO-ORTHO ([impl] stubs, deferred to CDR)                #
# --------------------------------------------------------------------------- #


@pytest.mark.unit
@pytest.mark.xfail(
    reason="ALG-GEO-ORTHO rigorous collinearity/DEM is [impl] (private viewing model; CDR target)",
    raises=GeolocationError,
    strict=True,
)
def test_orthorectify_rigorous_path_is_impl_stub():
    """The rigorous viewing-model/DEM orthorectification fail-stops until wired in."""
    image = np.zeros((4, 4), dtype=np.float32)
    dem = np.zeros((4, 4), dtype=np.float32)
    state = PlatformState(lat=0.0, lon=0.0, altitude_m=500_000.0, ground_velocity_ms=7000.0)
    orthorectify(image, state, viewing_model=None, dem=dem)


@pytest.mark.unit
@pytest.mark.xfail(
    reason="ALG-GEO-ORBIT ephemeris propagation is [impl] (GPL TLE path dropped; CDR target)",
    raises=GeolocationError,
    strict=True,
)
def test_orbit_state_is_impl_stub():
    """The orbit/ephemeris propagation fail-stops until the engine is wired in."""
    import datetime

    orbit_state(viewing_model=None, acq_time=datetime.datetime(2024, 1, 1))
