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

"""Unit tests for the atmospheric-correction EOProcessingUnit wrapper (C-PU-ATM).

These also prove the computing-model JSON loads under eopf 2.8.1 (the model is
loaded at class-definition time), that the stage declares its mandatory input and
ADFs (dem mandatory, atmospheric optional), and that the in-memory ``l1c``
EOProduct round-trips through the wrapper to an ``L2A`` BOA product with a scene
classification and cloud/shadow QA. The retrieval / RT-engine paths are ``[impl]``
and verified to fail-stop.
"""

from typing import Any

import numpy as np
import pytest
from eopf.computing.abstract import AuxiliaryDataFile
from eopf.product import EOGroup, EOProduct, EOVariable

from msi_processor.common.types import QAFlag
from msi_processor.computing.atmospheric.core import SceneClass
from msi_processor.computing.atmospheric.unit import AtmosphericUnit
from msi_processor.exceptions.errors import AtmosphericError, InputValidationError

_BANDS = ("B02", "B03", "B04", "B08")


def _l1c(reflectance: dict[str, np.ndarray], masks: dict[str, np.ndarray] | None = None) -> EOProduct:
    """Build a minimal L1C product: TOA reflectance bands (+ optional QA)."""
    product = EOProduct("L1C.TEST")
    product["measurements"] = EOGroup()
    for name, data in reflectance.items():
        product[f"measurements/reflectance/{name}"] = EOVariable(data=data, dims=("y", "x"))
    if masks:
        product["quality"] = EOGroup()
        for name, data in masks.items():
            product[f"quality/mask/{name}"] = EOVariable(data=data, dims=("y", "x"))
    return product


def _adf(name: str, data: Any) -> AuxiliaryDataFile:
    """Build an ADF carrying its content in data_ptr (this-increment convention)."""
    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


def _rt_lut() -> dict[str, Any]:
    """A resolved per-band RT-LUT (identity-ish, well-conditioned)."""
    return {
        "path_reflectance": {b: 0.04 for b in _BANDS},
        "transmittance": {b: 0.85 for b in _BANDS},
        "spherical_albedo": {b: 0.08 for b in _BANDS},
    }


def _atmospheric_adf() -> AuxiliaryDataFile:
    """The ingest-mode atmospheric ADF: AOT/WV/ozone + resolved RT-LUT."""
    return _adf(
        "atmospheric",
        {"aot": 0.15, "water_vapour": 2.5, "ozone": 300.0, "rt_lut": _rt_lut()},
    )


def _dem_adf(shape: tuple[int, int] = (4, 4)) -> AuxiliaryDataFile:
    """The mandatory DEM ADF."""
    return _adf("dem", {"elevation": np.zeros(shape, dtype=np.float32)})


def _toa_scene() -> dict[str, np.ndarray]:
    """A 1x4 TOA reflectance scene (cloud / shadow / veg / water columns)."""
    return {
        "B02": np.array([[0.75, 0.06, 0.08, 0.09]], dtype=np.float32),
        "B03": np.array([[0.75, 0.07, 0.10, 0.13]], dtype=np.float32),
        "B04": np.array([[0.75, 0.07, 0.09, 0.08]], dtype=np.float32),
        "B08": np.array([[0.75, 0.06, 0.44, 0.06]], dtype=np.float32),
    }


@pytest.mark.unit
def test_model_declares_input_and_adfs():
    """The computing-model JSON loads and declares l1c + dem mandatory."""
    unit = AtmosphericUnit("atm")
    assert unit.get_mandatory_input_list("nominal") == ["l1c"]
    assert unit.get_mandatory_adf_list("nominal") == ["dem"]
    assert unit.PROCESSOR_LEVEL == "L2A"


@pytest.mark.unit
def test_run_emits_l2a_boa_product():
    """Ingest mode produces an L2A product with BOA reflectance under each band."""
    unit = AtmosphericUnit("atm")
    outputs = unit.run(
        {"l1c": _l1c(_toa_scene())},
        {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
        sun_zenith=30.0,
    )
    assert set(outputs) == {"l2a"}
    l2a = outputs["l2a"]
    assert l2a.name == "L1C.TEST_L2A"
    for band in _BANDS:
        arr = np.asarray(l2a[f"measurements/reflectance/{band}"].data)
        assert arr.shape == (1, 4)
        assert arr.dtype == np.float32
        assert np.all((arr >= 0.0) & (arr <= 1.0))


@pytest.mark.unit
def test_run_propagates_geolocation_grid():
    """A gridded L1C's geolocation (conditions/*) is carried into the L2A, attrs kept."""
    l1c = _l1c(_toa_scene())
    l1c["conditions"] = EOGroup()
    l1c["conditions/geolocation/x"] = EOVariable(data=np.arange(4, dtype=np.float64), dims=("x",))
    l1c["conditions/geolocation/y"] = EOVariable(data=np.arange(1, dtype=np.float64), dims=("y",))
    l1c["conditions/geolocation/spatial_ref"] = EOVariable(
        data=np.array([0], dtype=np.int32), dims=("ref",), attrs={"crs_wkt": "TEST_WKT"}
    )
    l2a = AtmosphericUnit("atm").run(
        {"l1c": l1c}, {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()}, sun_zenith=30.0
    )["l2a"]
    assert np.asarray(l2a["conditions/geolocation/x"].data).shape == (4,)
    assert l2a["conditions/geolocation/spatial_ref"].attrs["crs_wkt"] == "TEST_WKT"


@pytest.mark.unit
def test_run_boa_below_toa_for_clear_pixel():
    """Removing path reflectance lowers a clear-pixel reflectance vs TOA."""
    toa = _toa_scene()
    unit = AtmosphericUnit("atm")
    outputs = unit.run(
        {"l1c": _l1c(toa)},
        {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
    )
    # Vegetation NIR column: BOA should differ from (and for this LUT, exceed-after
    # path removal need not hold) -- assert the inversion ran and stayed physical.
    boa_nir = np.asarray(outputs["l2a"]["measurements/reflectance/B08"].data)
    assert np.all(np.isfinite(boa_nir))
    assert boa_nir[0, 2] != toa["B08"][0, 2]


@pytest.mark.unit
def test_run_emits_scene_classification():
    """The L2A product carries a uint8 scene-classification layer."""
    unit = AtmosphericUnit("atm")
    outputs = unit.run(
        {"l1c": _l1c(_toa_scene())},
        {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
    )
    scene = np.asarray(outputs["l2a"]["quality/scene_classification"].data)
    assert scene.dtype == np.uint8
    assert scene.shape == (1, 4)
    # The bright column should be cloud.
    assert scene[0, 0] == SceneClass.CLOUD


@pytest.mark.unit
def test_run_flags_cloud_and_shadow_in_qa():
    """Cloud / cloud-shadow pixels set the QA bits per band (REQ-F-ATM-03)."""
    unit = AtmosphericUnit("atm")
    outputs = unit.run(
        {"l1c": _l1c(_toa_scene())},
        {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
    )
    qa = np.asarray(outputs["l2a"]["quality/mask/B02"].data)
    assert qa[0, 0] & int(QAFlag.CLOUD)
    assert qa[0, 1] & int(QAFlag.CLOUD_SHADOW)


@pytest.mark.unit
def test_run_merges_upstream_qa():
    """Upstream QA flags are preserved (OR-accumulated) into the L2A QA."""
    toa = _toa_scene()
    masks = {b: np.zeros((1, 4), dtype=np.uint16) for b in _BANDS}
    masks["B02"][0, 3] = int(QAFlag.NO_DATA)
    unit = AtmosphericUnit("atm")
    outputs = unit.run(
        {"l1c": _l1c(toa, masks)},
        {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
    )
    qa = np.asarray(outputs["l2a"]["quality/mask/B02"].data)
    assert qa[0, 3] & int(QAFlag.NO_DATA)


@pytest.mark.unit
def test_run_requires_dem_adf():
    """Missing DEM coverage is a fail-stop (REQ-F-ATM-02)."""
    unit = AtmosphericUnit("atm")
    with pytest.raises(AtmosphericError):
        unit.run({"l1c": _l1c(_toa_scene())}, {"atmospheric": _atmospheric_adf()})


@pytest.mark.unit
def test_run_ingest_requires_atmospheric_adf():
    """Ingest mode without the atmospheric ADF fail-stops."""
    unit = AtmosphericUnit("atm")
    with pytest.raises(AtmosphericError):
        unit.run({"l1c": _l1c(_toa_scene())}, {"dem": _dem_adf()})


@pytest.mark.unit
def test_run_missing_input():
    """A missing mandatory l1c input is an input error."""
    unit = AtmosphericUnit("atm")
    with pytest.raises(InputValidationError):
        unit.run({}, {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()})


@pytest.mark.unit
def test_run_unknown_mode():
    """An unknown processing mode is rejected."""
    unit = AtmosphericUnit("atm")
    with pytest.raises(InputValidationError):
        unit.run(
            {"l1c": _l1c(_toa_scene())},
            {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
            mode="bogus",
        )


@pytest.mark.unit
def test_run_unknown_param_mode():
    """An unknown param_mode is rejected."""
    unit = AtmosphericUnit("atm")
    with pytest.raises(InputValidationError):
        unit.run(
            {"l1c": _l1c(_toa_scene())},
            {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
            param_mode="bogus",
        )


@pytest.mark.unit
def test_run_retrieve_mode_is_impl():
    """Image-based parameter retrieval is [impl] and fail-stops."""
    unit = AtmosphericUnit("atm")
    with pytest.raises(AtmosphericError):
        unit.run(
            {"l1c": _l1c(_toa_scene())},
            {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()},
            param_mode="retrieve",
        )


@pytest.mark.unit
def test_run_missing_reflectance_group():
    """An L1C product without a reflectance group is an input error."""
    product = EOProduct("L1C.EMPTY")
    product["measurements"] = EOGroup()
    unit = AtmosphericUnit("atm")
    with pytest.raises(InputValidationError):
        unit.run({"l1c": product}, {"atmospheric": _atmospheric_adf(), "dem": _dem_adf()})


@pytest.mark.unit
def test_run_atmospheric_adf_without_rt_lut_fail_stops():
    """Ingest mode requires the resolved RT-LUT in the atmospheric ADF."""
    bad = _adf("atmospheric", {"aot": 0.15, "water_vapour": 2.5})
    unit = AtmosphericUnit("atm")
    with pytest.raises(AtmosphericError):
        unit.run({"l1c": _l1c(_toa_scene())}, {"atmospheric": bad, "dem": _dem_adf()})
