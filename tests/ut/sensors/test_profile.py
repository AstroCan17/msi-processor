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

"""Unit tests for the sensor profile loader (SDD <5.4.12>)."""

import json
from pathlib import Path

import pytest

from msi_processor.exceptions.errors import ProfileValidationError
from msi_processor.sensors.profile import SensorProfile, load_profile

_VALID_PROFILE = {
    "profile_id": "demo-msi",
    "profile_version": "1.0.0",
    "sensor_id": "demo-sat",
    "bands": [{"name": "b2", "center_wavelength_nm": 490.0}, {"name": "b3"}],
    "bit_depth": 12,
    "gsd": 10.0,
    "adf_bindings": {"dark": "s3://adf/dark.zarr", "nuc": "s3://adf/nuc.zarr"},
}


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.mark.unit
def test_load_valid_profile(tmp_path):
    """A well-formed profile loads into a typed SensorProfile."""
    profile = load_profile(_write(tmp_path, _VALID_PROFILE))
    assert isinstance(profile, SensorProfile)
    assert profile.profile_id == "demo-msi"
    assert profile.bit_depth == 12
    assert profile.gsd == 10.0
    assert profile.band_names == ["b2", "b3"]
    assert profile.adf_bindings["dark"] == "s3://adf/dark.zarr"


@pytest.mark.unit
def test_bit_depth_defaults_to_twelve(tmp_path):
    """bit_depth defaults to 12 when omitted (DPM-PRM-GEN-01)."""
    payload = {k: v for k, v in _VALID_PROFILE.items() if k != "bit_depth"}
    profile = load_profile(_write(tmp_path, payload))
    assert profile.bit_depth == 12


@pytest.mark.unit
def test_invalid_bit_depth_raises(tmp_path):
    """A non-positive bit_depth is rejected."""
    payload = {**_VALID_PROFILE, "bit_depth": 0}
    with pytest.raises(ProfileValidationError):
        load_profile(_write(tmp_path, payload))


@pytest.mark.unit
def test_empty_bands_raises(tmp_path):
    """At least one band is required."""
    payload = {**_VALID_PROFILE, "bands": []}
    with pytest.raises(ProfileValidationError):
        load_profile(_write(tmp_path, payload))


@pytest.mark.unit
def test_negative_gsd_raises(tmp_path):
    """A non-positive GSD is rejected."""
    payload = {**_VALID_PROFILE, "gsd": -1.0}
    with pytest.raises(ProfileValidationError):
        load_profile(_write(tmp_path, payload))


@pytest.mark.unit
def test_missing_file_raises(tmp_path):
    """A missing profile file raises ProfileValidationError."""
    with pytest.raises(ProfileValidationError):
        load_profile(tmp_path / "does-not-exist.json")


@pytest.mark.unit
def test_malformed_json_raises(tmp_path):
    """A syntactically invalid JSON file raises ProfileValidationError."""
    path = tmp_path / "broken.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ProfileValidationError):
        load_profile(path)
