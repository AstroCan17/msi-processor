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

"""Unit tests for the radiometric EOProcessingUnit wrapper (C-PU-RAD).

These also prove the computing-model JSON loads under eopf 2.8.1 (the model
is loaded at class-definition time) and that mandatory inputs/ADFs are
declared via that model.
"""

from typing import Any

import numpy as np
import pytest
from eopf.computing.abstract import AuxiliaryDataFile
from eopf.product import EOGroup, EOProduct, EOVariable
from numpy.testing import assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.radiometric.unit import RadiometricUnit
from msi_processor.exceptions.errors import AdfResolutionError, InputValidationError


def _l1a(bands: dict[str, np.ndarray]) -> EOProduct:
    """Build a minimal L1A product with bands under measurements/detector."""
    product = EOProduct("L1A.TEST")
    product["measurements"] = EOGroup()
    for name, data in bands.items():
        product[f"measurements/detector/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    return product


def _adf(name: str, data: Any) -> AuxiliaryDataFile:
    """Build an ADF carrying its content in data_ptr (this-increment convention)."""
    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


@pytest.mark.unit
def test_computing_model_is_loaded():
    """The CPM computing-model JSON declares the mandatory input/ADFs."""
    model = RadiometricUnit.processing_model()
    assert model is not None
    assert set(RadiometricUnit.get_available_modes()) == {"nominal", "calibration"}
    assert RadiometricUnit.get_mandatory_input_list("nominal") == ["l1a"]
    assert RadiometricUnit.get_mandatory_adf_list("nominal") == ["dark", "nuc"]
    assert RadiometricUnit.get_mandatory_adf_list("calibration") == ["dark", "flatfield"]


@pytest.mark.unit
def test_default_mode_identity_correction():
    """Unit gain, zero offset/dark -> output DN equals input DN, QA all zero."""
    dn = np.array([[10, 20], [30, 40]], dtype=np.uint16)
    l1a = _l1a({"b2": dn})
    adfs = {
        "dark": _adf("dark", {"dark_offset": {"b2": 0.0}}),
        "nuc": _adf("nuc", {"gain": {"b2": np.array([1.0, 1.0])}, "offset": {"b2": np.array([0.0, 0.0])}}),
    }
    outputs = RadiometricUnit().run({"l1a": l1a}, adfs=adfs)
    assert set(outputs) == {"rad"}
    rad = outputs["rad"]
    assert_array_equal(np.asarray(rad["measurements/detector/b2"].data), dn)
    assert_array_equal(np.asarray(rad["quality/mask/b2"].data), np.zeros((2, 2), dtype=np.uint16))


@pytest.mark.unit
def test_default_mode_flags_and_replaces_bad_pixel():
    """An out-of-bound gain marks the detector DEFECTIVE and interpolates it."""
    dn = np.array([[10, 20, 30]], dtype=np.uint16)
    l1a = _l1a({"b2": dn})
    adfs = {
        "dark": _adf("dark", {"dark_offset": {"b2": 0.0}}),
        "nuc": _adf(
            "nuc",
            {"gain": {"b2": np.array([1.0, 100.0, 1.0])}, "offset": {"b2": np.array([0.0, 0.0, 0.0])}},
        ),
    }
    outputs = RadiometricUnit().run({"l1a": l1a}, adfs=adfs, g_max=10.0)
    rad = outputs["rad"]
    # detector 1 (gain 100 >= g_max) replaced by mean(neighbours) = (10+30)/2 = 20
    assert_array_equal(np.asarray(rad["measurements/detector/b2"].data), [[10, 20, 30]])
    assert_array_equal(
        np.asarray(rad["quality/mask/b2"].data),
        [[0, int(QAFlag.DEFECTIVE), 0]],
    )


@pytest.mark.unit
def test_calibration_mode_derives_nuc_and_emits_product():
    """Calibration mode derives gain/offset from dark+flat and emits a nuc product."""
    dn = np.array([[2.0, 4.0], [2.0, 4.0]], dtype=np.float32)
    l1a = _l1a({"b2": dn})
    dark_frame = np.zeros((2, 2), dtype=np.float32)
    flat_frame = np.array([[2.0, 4.0], [2.0, 4.0]], dtype=np.float32)
    adfs = {
        "dark": _adf("dark", {"frame": {"b2": dark_frame}, "dark_offset": {"b2": 0.0}}),
        "flatfield": _adf("flatfield", {"b2": flat_frame}),
    }
    outputs = RadiometricUnit().run({"l1a": l1a}, adfs=adfs, mode="calibration")
    assert set(outputs) == {"rad", "nuc"}
    # mu_F = 3 -> gain = 3 / [2, 4] = [1.5, 0.75]; offset = 3 - gain*Fbar = [0, 0]
    nuc = outputs["nuc"]
    assert_array_equal(np.asarray(nuc["gain/b2"].data), [1.5, 0.75])
    assert_array_equal(np.asarray(nuc["offset/b2"].data), [0.0, 0.0])
    # corrected = dn*gain = [[3,3],[3,3]]
    rad = outputs["rad"]
    assert_array_equal(np.asarray(rad["measurements/detector/b2"].data), [[3, 3], [3, 3]])


@pytest.mark.unit
def test_missing_input_raises():
    """A missing 'l1a' input raises InputValidationError."""
    with pytest.raises(InputValidationError):
        RadiometricUnit().run({}, adfs={"dark": _adf("dark", {})})


@pytest.mark.unit
def test_missing_dark_adf_raises():
    """The mandatory dark ADF must be present."""
    l1a = _l1a({"b2": np.array([[1, 2]], dtype=np.uint16)})
    nuc = _adf("nuc", {"gain": {"b2": np.array([1.0, 1.0])}, "offset": {"b2": np.array([0.0, 0.0])}})
    with pytest.raises(AdfResolutionError):
        RadiometricUnit().run({"l1a": l1a}, adfs={"nuc": nuc})


@pytest.mark.unit
def test_missing_nuc_adf_in_default_mode_raises():
    """Default mode requires the nuc ADF (gain/offset)."""
    l1a = _l1a({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(AdfResolutionError):
        RadiometricUnit().run({"l1a": l1a}, adfs={"dark": _adf("dark", {"dark_offset": {"b2": 0.0}})})


@pytest.mark.unit
def test_unknown_mode_raises():
    """An unsupported mode is rejected before processing."""
    l1a = _l1a({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(InputValidationError):
        RadiometricUnit().run({"l1a": l1a}, adfs={}, mode="bogus")
