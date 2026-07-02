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

"""Unit tests for the geo-referencing EOProcessingUnit wrapper (C-PU-GEO).

These also prove the computing-model JSON loads under eopf 2.8.1 (the model is
loaded at class-definition time), that the stage declares its mandatory input and
ADFs (viewing_model + dem mandatory, gcp optional), and that the in-memory ``cor``
EOProduct round-trips through the wrapper onto the cartographic grid. The rigorous
viewing-model/DEM path (``use_gcp=False``) is ``[impl]`` and verified to fail-stop.
"""

from typing import Any

import numpy as np
import pytest
from eopf.computing.abstract import AuxiliaryDataFile
from eopf.product import EOGroup, EOProduct, EOVariable
from rasterio.crs import CRS

from msi_processor.common.types import QAFlag
from msi_processor.computing.georeference.unit import GeoreferenceUnit
from msi_processor.exceptions.errors import GeolocationError, InputValidationError

_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 8
_TY = 5

_UTM35N_WKT = CRS.from_epsg(32635).to_wkt()
_GDAL = [600000.0, 10.0, 0.0, 4500000.0, 0.0, -10.0]


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
    """Return ``(reference, image)`` cropped from one scene with offset ``(_TX, _TY)``."""
    base = _textured_scene(seed)
    r0, r1 = _ORIGIN, _ORIGIN + _WIN
    by0, by1 = _ORIGIN + _TY, _ORIGIN + _TY + _WIN
    bx0, bx1 = _ORIGIN + _TX, _ORIGIN + _TX + _WIN
    reference = base[r0:r1, r0:r1].copy()
    image = base[by0:by1, bx0:bx1].copy()
    return reference, image


def _cor(reflectance: dict[str, np.ndarray], masks: dict[str, np.ndarray] | None = None) -> EOProduct:
    """Build a minimal co-registered product: reflectance bands (+ optional QA)."""
    product = EOProduct("COR.TEST")
    product["measurements"] = EOGroup()
    for name, data in reflectance.items():
        product[f"measurements/reflectance/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    if masks:
        product["quality"] = EOGroup()
        for name, data in masks.items():
            product[f"quality/mask/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    return product


def _adf(name: str, data: Any) -> AuxiliaryDataFile:
    """Build an ADF carrying its content in data_ptr (this-increment convention)."""
    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


def _adfs(reference: np.ndarray) -> dict[str, AuxiliaryDataFile]:
    """The mandatory viewing_model + dem and the geolocated gcp reference."""
    return {
        "viewing_model": _adf("viewing_model", {"pixel_pitch_m": 5.5e-6, "focal_length_m": 845e-6}),
        "dem": _adf(
            "dem", {"elevation": np.zeros((10, 10), dtype=np.float32), "geotransform": _GDAL, "crs_wkt": _UTM35N_WKT}
        ),
        "gcp": _adf("gcp", {"image": reference, "geotransform": _GDAL, "crs_wkt": _UTM35N_WKT}),
    }


@pytest.mark.unit
def test_computing_model_is_loaded():
    """The CPM computing-model JSON declares the mandatory input and ADFs."""
    model = GeoreferenceUnit.processing_model()
    assert model is not None
    assert set(GeoreferenceUnit.get_available_modes()) == {"nominal"}
    assert GeoreferenceUnit.get_mandatory_input_list("nominal") == ["cor"]
    assert GeoreferenceUnit.get_mandatory_adf_list("nominal") == ["viewing_model", "dem"]
    assert GeoreferenceUnit.PROCESSOR_LEVEL == "L1C"


@pytest.mark.unit
def test_georeferences_to_cartographic_grid():
    """The co-registered band is placed on the profile cartographic grid (L1C)."""
    reference, image = _shifted_pair()
    outputs = GeoreferenceUnit().run(
        {"cor": _cor({"b3": image})},
        adfs=_adfs(reference),
        resolution=10.0,
        resampling="nearest",
        min_gcp=8,
        seed=0,
    )
    assert set(outputs) == {"l1c"}
    l1c = outputs["l1c"]
    gridded = np.asarray(l1c["measurements/reflectance/b3"].data)
    x = np.asarray(l1c["conditions/geolocation/x"].data)
    y = np.asarray(l1c["conditions/geolocation/y"].data)
    # The grid is square at 10 m matching the reference extent, with axes to match.
    assert gridded.shape == (y.shape[0], x.shape[0])
    assert gridded.shape == (_WIN, _WIN)
    # The grid corner coordinate comes from the geolocated reference geotransform.
    assert x[0] == pytest.approx(600000.0 + 5.0)
    assert y[0] == pytest.approx(4500000.0 - 5.0)


@pytest.mark.unit
def test_spatial_ref_carries_crs_and_geotransform():
    """REQ-F-GEO-04: the L1C carries CRS + geotransform encoding."""
    reference, image = _shifted_pair()
    outputs = GeoreferenceUnit().run(
        {"cor": _cor({"b3": image})},
        adfs=_adfs(reference),
        resolution=10.0,
    )
    spatial_ref = outputs["l1c"]["conditions/geolocation/spatial_ref"]
    assert CRS.from_wkt(spatial_ref.attrs["crs_wkt"]).to_epsg() == 32635
    assert spatial_ref.attrs["GeoTransform"][1] == pytest.approx(10.0)


@pytest.mark.unit
def test_provenance_records_gcp_diagnostics():
    """The L1C provenance carries the ground-control diagnostics (ICD-IF-DIAG)."""
    reference, image = _shifted_pair()
    outputs = GeoreferenceUnit().run(
        {"cor": _cor({"b3": image})},
        adfs=_adfs(reference),
        resolution=10.0,
    )
    geoloc = outputs["l1c"].attrs["other_metadata"]["geolocation"]
    assert geoloc["n_gcp"] >= 8
    assert geoloc["rms_residual_px"] < 1.0


@pytest.mark.unit
def test_no_gcp_rigorous_path_is_impl_fail_stop():
    """use_gcp=False routes to the rigorous [impl] path, which fail-stops."""
    reference, image = _shifted_pair()
    with pytest.raises(GeolocationError):
        GeoreferenceUnit().run(
            {"cor": _cor({"b3": image})},
            adfs=_adfs(reference),
            resolution=10.0,
            use_gcp=False,
        )


@pytest.mark.unit
def test_missing_dem_adf_fail_stops():
    """A missing mandatory DEM ADF is a coverage fail-stop (REQ-F-GEO-02)."""
    reference, image = _shifted_pair()
    adfs = _adfs(reference)
    del adfs["dem"]
    with pytest.raises(GeolocationError):
        GeoreferenceUnit().run({"cor": _cor({"b3": image})}, adfs=adfs, resolution=10.0)


@pytest.mark.unit
def test_missing_viewing_model_adf_fail_stops():
    """A missing mandatory viewing-model ADF is a coverage fail-stop (REQ-F-GEO-01)."""
    reference, image = _shifted_pair()
    adfs = _adfs(reference)
    del adfs["viewing_model"]
    with pytest.raises(GeolocationError):
        GeoreferenceUnit().run({"cor": _cor({"b3": image})}, adfs=adfs, resolution=10.0)


@pytest.mark.unit
def test_missing_gcp_reference_when_enabled_fail_stops():
    """use_gcp=True without the gcp ADF fail-stops (no reference to refine against)."""
    reference, image = _shifted_pair()
    adfs = _adfs(reference)
    del adfs["gcp"]
    with pytest.raises(GeolocationError):
        GeoreferenceUnit().run({"cor": _cor({"b3": image})}, adfs=adfs, resolution=10.0)


@pytest.mark.unit
def test_insufficient_gcp_gate_fail_stops():
    """Too few ground-control points fail-stop (REQ-F-GEO-03 acceptance gate)."""
    reference, image = _shifted_pair()
    with pytest.raises(GeolocationError):
        GeoreferenceUnit().run(
            {"cor": _cor({"b3": image})},
            adfs=_adfs(reference),
            resolution=10.0,
            min_gcp=100_000,
        )


@pytest.mark.unit
def test_upstream_qa_propagated_to_grid():
    """Upstream QA is geo-referenced with its band and OR-accumulated onto the grid."""
    reference, image = _shifted_pair()
    mask = np.zeros((_WIN, _WIN), dtype=np.uint16)
    mask[_WIN // 2, _WIN // 2] = np.uint16(QAFlag.DEFECTIVE)
    outputs = GeoreferenceUnit().run(
        {"cor": _cor({"b3": image}, masks={"b3": mask})},
        adfs=_adfs(reference),
        resolution=10.0,
        resampling="nearest",
    )
    qa = np.asarray(outputs["l1c"]["quality/mask/b3"].data)
    assert qa.dtype == np.uint16
    # The DEFECTIVE flag survives geo-referencing somewhere on the grid.
    assert int(QAFlag.DEFECTIVE) in set(np.unique(qa).tolist())


@pytest.mark.unit
def test_missing_input_raises():
    """A missing 'cor' input raises InputValidationError."""
    with pytest.raises(InputValidationError):
        GeoreferenceUnit().run({}, resolution=10.0)


@pytest.mark.unit
def test_missing_resolution_raises():
    """The mandatory resolution parameter must be supplied."""
    reference, image = _shifted_pair()
    with pytest.raises(InputValidationError):
        GeoreferenceUnit().run({"cor": _cor({"b3": image})}, adfs=_adfs(reference))


@pytest.mark.unit
def test_unknown_resampling_raises():
    """An unsupported resampling kernel is rejected before processing."""
    reference, image = _shifted_pair()
    with pytest.raises(InputValidationError):
        GeoreferenceUnit().run(
            {"cor": _cor({"b3": image})},
            adfs=_adfs(reference),
            resolution=10.0,
            resampling="sinc",
        )


@pytest.mark.unit
def test_unknown_mode_raises():
    """An unsupported mode is rejected before processing."""
    reference, image = _shifted_pair()
    with pytest.raises(InputValidationError):
        GeoreferenceUnit().run(
            {"cor": _cor({"b3": image})},
            adfs=_adfs(reference),
            resolution=10.0,
            mode="bogus",
        )
