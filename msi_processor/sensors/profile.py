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

"""Typed sensor profile (C-SENSORS; SDD <5.4.12>, ICD <5.3.6>).

A minimal, schema-validated :class:`SensorProfile` specialising the generic
chain for one instrument. It carries **references** to the private
calibration ADFs (by id → URI) and never embeds private calibration values
(REQ-AD-01, REQ-S-01/05). The loader :func:`load_profile` reads a profile
JSON instance and validates it.

*Trace:* REQ-AD-01..04, REQ-DAT-03; ICD-IF-PROF-*.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from msi_processor.exceptions.errors import ProfileValidationError

__all__ = ["BandSpec", "SensorProfile", "load_profile"]


class BandSpec(BaseModel):
    """One spectral band of the sensor (data only, no private values)."""

    name: str = Field(..., min_length=1)
    center_wavelength_nm: Optional[float] = None

    @field_validator("center_wavelength_nm")
    @classmethod
    def _positive_wavelength(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value <= 0.0:
            raise ValueError("center_wavelength_nm must be positive")
        return value


class SensorProfile(BaseModel):
    """Per-sensor configuration (SDD <5.4.12>).

    Parameters
    ----------
    profile_id, profile_version, sensor_id:
        Identity of the profile instance.
    bands:
        Ordered list of :class:`BandSpec` (at least one).
    bit_depth:
        Sensor radiometric depth; valid DN range ``[0, 2**bit_depth - 1]``
        (``DPM-PRM-GEN-01``, default 12).
    gsd:
        Nominal ground sampling distance in metres.
    adf_bindings:
        Mapping of ADF id → URI **reference**. Private calibration content is
        resolved from these URIs at run time and is never stored in the
        profile (REQ-S-01/05).
    """

    profile_id: str = Field(..., min_length=1)
    profile_version: str = Field(..., min_length=1)
    sensor_id: str = Field(..., min_length=1)
    bands: list[BandSpec] = Field(..., min_length=1)
    bit_depth: int = 12
    gsd: float
    adf_bindings: dict[str, str] = Field(default_factory=dict)

    @field_validator("bit_depth")
    @classmethod
    def _check_bit_depth(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("bit_depth must be a positive integer")
        return value

    @field_validator("gsd")
    @classmethod
    def _check_gsd(cls, value: float) -> float:
        if value <= 0.0:
            raise ValueError("gsd must be positive")
        return value

    @property
    def band_names(self) -> list[str]:
        """Return the band ids in declaration order."""
        return [band.name for band in self.bands]


def load_profile(path: str | Path) -> SensorProfile:
    """Load and validate a sensor profile JSON instance.

    Parameters
    ----------
    path:
        Filesystem path to the profile JSON.

    Returns
    -------
    SensorProfile
        The validated, typed profile.

    Raises
    ------
    ProfileValidationError
        If the file is missing, not valid JSON, or fails schema validation
        (REQ-DAT-03).
    """
    profile_path = Path(path)
    try:
        raw_text = profile_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProfileValidationError(
            f"Cannot read profile file '{profile_path}': {exc}",
            stage="profile",
        ) from exc
    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ProfileValidationError(
            f"Profile file '{profile_path}' is not valid JSON: {exc}",
            stage="profile",
        ) from exc
    try:
        return SensorProfile.model_validate(raw)
    except ValueError as exc:
        raise ProfileValidationError(
            f"Profile file '{profile_path}' failed validation: {exc}",
            stage="profile",
        ) from exc
