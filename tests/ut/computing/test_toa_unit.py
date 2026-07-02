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

"""Unit tests for the TOA EOProcessingUnit wrapper (C-PU-TOA).

These also prove the computing-model JSON loads under eopf 2.8.1 (the model
is loaded at class-definition time) and that mandatory inputs/ADFs are
declared via that model.
"""

from typing import Any

import numpy as np
import pytest
from eopf.computing.abstract import AuxiliaryDataFile
from eopf.product import EOGroup, EOProduct, EOVariable
from numpy.testing import assert_allclose, assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.toa.unit import ToaUnit
from msi_processor.exceptions.errors import AdfResolutionError, InputValidationError


def _enh(bands: dict[str, np.ndarray], masks: dict[str, np.ndarray] | None = None) -> EOProduct:
    """Build a minimal enhancement product: detector bands (+ optional QA)."""
    product = EOProduct("ENH.TEST")
    product["measurements"] = EOGroup()
    for name, data in bands.items():
        product[f"measurements/detector/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    if masks:
        product["quality"] = EOGroup()
        for name, data in masks.items():
            product[f"quality/mask/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    return product


def _adf(name: str, data: Any) -> AuxiliaryDataFile:
    """Build an ADF carrying its content in data_ptr (this-increment convention)."""
    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


def _radiometric(gain: dict[str, Any], offset: dict[str, Any]) -> AuxiliaryDataFile:
    """Build a radiometric ADF (per-band absolute gain/offset)."""
    return _adf("radiometric", {"gain": gain, "offset": offset})


@pytest.mark.unit
def test_computing_model_is_loaded():
    """The CPM computing-model JSON declares the mandatory input/ADFs."""
    model = ToaUnit.processing_model()
    assert model is not None
    assert set(ToaUnit.get_available_modes()) == {"nominal"}
    assert ToaUnit.get_mandatory_input_list("nominal") == ["enh"]
    assert ToaUnit.get_mandatory_adf_list("nominal") == ["radiometric"]


@pytest.mark.unit
def test_radiance_only_default_run():
    """Unit gain, zero offset -> radiance equals DN; reflectance absent; QA zero."""
    dn = np.array([[10, 20], [30, 40]], dtype=np.uint16)
    enh = _enh({"b2": dn})
    adfs = {"radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0})}
    outputs = ToaUnit().run({"enh": enh}, adfs=adfs)
    assert set(outputs) == {"l1b"}
    l1b = outputs["l1b"]
    radiance = np.asarray(l1b["measurements/radiance/b2"].data)
    assert_array_equal(radiance, dn.astype(np.float32))
    assert radiance.dtype == np.float32
    assert_array_equal(np.asarray(l1b["quality/mask/b2"].data), np.zeros((2, 2), dtype=np.uint16))
    assert "reflectance" not in [k for k, _ in l1b["measurements"].items()]


@pytest.mark.unit
def test_dn_to_radiance_affine_through_unit():
    """radiance = (DN - offset)*gain end-to-end through the wrapper."""
    dn = np.array([[100, 200]], dtype=np.uint16)
    enh = _enh({"b3": dn})
    adfs = {"radiometric": _radiometric({"b3": 2.0}, {"b3": 50.0})}
    outputs = ToaUnit().run({"enh": enh}, adfs=adfs)
    # (dn - 50) * 2
    assert_array_equal(np.asarray(outputs["l1b"]["measurements/radiance/b3"].data), [[100.0, 300.0]])


@pytest.mark.unit
def test_emit_reflectance_with_geometry_and_spectral_adf():
    """Reflectance path: rho = pi*L / E with theta=0, d=1."""
    dn = np.array([[100, 100]], dtype=np.uint16)
    enh = _enh({"b2": dn})
    adfs = {
        "radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0}),
        "spectral": _adf("spectral", {"esun": {"b2": 1000.0}}),
    }
    outputs = ToaUnit().run(
        {"enh": enh},
        adfs=adfs,
        emit_reflectance=True,
        sun_zenith_rad=0.0,
        earth_sun_distance_au=1.0,
    )
    l1b = outputs["l1b"]
    # radiance = 100 ; rho = pi*100 / 1000 = 0.31415927
    assert_allclose(np.asarray(l1b["measurements/reflectance/b2"].data), [[0.31415927, 0.31415927]], rtol=1e-6)
    assert_array_equal(np.asarray(l1b["measurements/radiance/b2"].data), [[100.0, 100.0]])


@pytest.mark.unit
def test_emit_reflectance_derives_distance_from_day_of_year():
    """earth_sun_distance is derived from day_of_year when not given explicitly."""
    dn = np.array([[100]], dtype=np.uint16)
    enh = _enh({"b2": dn})
    adfs = {
        "radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0}),
        "spectral": _adf("spectral", {"esun": {"b2": 1000.0}}),
    }
    outputs = ToaUnit().run(
        {"enh": enh},
        adfs=adfs,
        emit_reflectance=True,
        sun_zenith_deg=0.0,
        day_of_year=4,
    )
    # d(4) = 0.98328 -> rho = pi*100*d^2 / 1000
    expected = np.pi * 100.0 * (0.98328**2) / 1000.0
    assert_allclose(np.asarray(outputs["l1b"]["measurements/reflectance/b2"].data), [[expected]], rtol=1e-5)


@pytest.mark.unit
def test_upstream_qa_is_propagated():
    """Upstream quality/mask flags are OR-accumulated into the output QA."""
    dn = np.array([[10, 20]], dtype=np.uint16)
    mask = np.array([[int(QAFlag.SATURATED), 0]], dtype=np.uint16)
    enh = _enh({"b2": dn}, masks={"b2": mask})
    adfs = {"radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0})}
    outputs = ToaUnit().run({"enh": enh}, adfs=adfs)
    assert_array_equal(
        np.asarray(outputs["l1b"]["quality/mask/b2"].data),
        [[int(QAFlag.SATURATED), 0]],
    )


@pytest.mark.unit
def test_negative_radiance_is_floored():
    """Offset larger than DN yields negative radiance, floored at 0."""
    dn = np.array([[10, 100]], dtype=np.uint16)
    enh = _enh({"b2": dn})
    adfs = {"radiometric": _radiometric({"b2": 1.0}, {"b2": 50.0})}
    outputs = ToaUnit().run({"enh": enh}, adfs=adfs)
    # (10-50)*1 = -40 -> 0 ; (100-50)*1 = 50
    assert_array_equal(np.asarray(outputs["l1b"]["measurements/radiance/b2"].data), [[0.0, 50.0]])


@pytest.mark.unit
def test_missing_input_raises():
    """A missing 'enh' input raises InputValidationError."""
    with pytest.raises(InputValidationError):
        ToaUnit().run({}, adfs={"radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0})})


@pytest.mark.unit
def test_missing_radiometric_adf_raises():
    """The mandatory radiometric ADF must be present."""
    enh = _enh({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(AdfResolutionError):
        ToaUnit().run({"enh": enh}, adfs={})


@pytest.mark.unit
def test_reflectance_without_spectral_adf_raises():
    """Requesting reflectance without the spectral ADF raises AdfResolutionError."""
    enh = _enh({"b2": np.array([[1, 2]], dtype=np.uint16)})
    adfs = {"radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0})}
    with pytest.raises(AdfResolutionError):
        ToaUnit().run({"enh": enh}, adfs=adfs, emit_reflectance=True, sun_zenith_rad=0.0, earth_sun_distance_au=1.0)


@pytest.mark.unit
def test_reflectance_without_geometry_raises():
    """Requesting reflectance without solar geometry raises InputValidationError."""
    enh = _enh({"b2": np.array([[1, 2]], dtype=np.uint16)})
    adfs = {
        "radiometric": _radiometric({"b2": 1.0}, {"b2": 0.0}),
        "spectral": _adf("spectral", {"esun": {"b2": 1000.0}}),
    }
    with pytest.raises(InputValidationError):
        ToaUnit().run({"enh": enh}, adfs=adfs, emit_reflectance=True)


@pytest.mark.unit
def test_unknown_mode_raises():
    """An unsupported mode is rejected before processing."""
    enh = _enh({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(InputValidationError):
        ToaUnit().run({"enh": enh}, adfs={}, mode="bogus")
