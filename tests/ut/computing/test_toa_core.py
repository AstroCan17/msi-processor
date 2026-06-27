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

"""Unit tests for the TOA core (ALG-TOA-RAD/REF).

Every pure function is exercised with tiny synthetic arrays and hand-computed
expected values.
"""

import math
from datetime import datetime

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.toa.core import (
    TOAParams,
    dn_to_radiance,
    earth_sun_distance,
    flag_radiance,
    radiance_to_reflectance,
    solar_geometry,
)


@pytest.mark.unit
def test_dn_to_radiance_scalar_gain_offset():
    r"""L = (DN - offset)*gain with per-band scalar coefficients."""
    dn = np.array([[10.0, 20.0], [30.0, 40.0]], dtype=np.float32)
    radiance = dn_to_radiance(dn, gain=2.0, offset=5.0)
    # (dn - 5) * 2
    expected = np.array([[10.0, 30.0], [50.0, 70.0]], dtype=np.float32)
    assert_array_equal(radiance, expected)
    assert radiance.dtype == np.float32


@pytest.mark.unit
def test_dn_to_radiance_per_detector_broadcast():
    r"""Per-detector gain/offset vectors broadcast across lines."""
    dn = np.array([[10.0, 20.0, 30.0], [40.0, 50.0, 60.0]], dtype=np.float32)
    gain = np.array([1.0, 2.0, 0.5], dtype=np.float32)
    offset = np.array([0.0, 5.0, 10.0], dtype=np.float32)
    radiance = dn_to_radiance(dn, gain, offset)
    expected = np.array([[10.0, 30.0, 10.0], [40.0, 90.0, 25.0]], dtype=np.float32)
    assert_array_equal(radiance, expected)


@pytest.mark.unit
def test_dn_to_radiance_drops_heritage_min_rebasing():
    r"""The heritage ``radiance -= radiance.min()`` is NOT applied (ATBD <5.3>)."""
    dn = np.array([[10.0, 20.0, 30.0]], dtype=np.float32)
    radiance = dn_to_radiance(dn, gain=1.0, offset=0.0)
    # would be [0, 10, 20] if the heritage min-subtraction were kept
    assert_array_equal(radiance, [[10.0, 20.0, 30.0]])


@pytest.mark.unit
def test_radiance_to_reflectance_canonical_formula():
    r"""rho = pi*L*d^2 / (E*cos theta); theta=60deg, d=1, E=1000."""
    radiance = np.array([50.0, 100.0], dtype=np.float32)
    reflectance = radiance_to_reflectance(
        radiance, esun=1000.0, sun_zenith_rad=math.radians(60.0), earth_sun_dist_au=1.0
    )
    # cos 60 = 0.5 -> rho = pi*L / (1000*0.5) = pi*L/500
    expected = np.pi * np.array([50.0, 100.0]) / 500.0
    assert_allclose(reflectance, expected, rtol=1e-6)
    assert reflectance.dtype == np.float32


@pytest.mark.unit
def test_radiance_to_reflectance_earth_sun_distance_squared():
    r"""The d^2 factor scales reflectance quadratically."""
    radiance = np.array([100.0], dtype=np.float32)
    reflectance = radiance_to_reflectance(radiance, esun=1000.0, sun_zenith_rad=0.0, earth_sun_dist_au=2.0)
    # pi*100*4 / (1000*1) = 0.4*pi -> clipped to 1.0
    assert_allclose(reflectance, [1.0])


@pytest.mark.unit
def test_radiance_to_reflectance_clips_to_unit_range():
    r"""Out-of-range reflectance is clipped to [0, 1] (REQ-D-05)."""
    radiance = np.array([0.0, 500.0, 5000.0], dtype=np.float32)
    reflectance = radiance_to_reflectance(radiance, esun=1000.0, sun_zenith_rad=0.0, earth_sun_dist_au=1.0)
    # pi*L/1000 -> [0, 1.57->1, 15.7->1]; 0 stays 0
    assert_array_equal(reflectance, [0.0, 1.0, 1.0])


@pytest.mark.unit
def test_flag_radiance_floors_negative_no_flag():
    r"""Negative (non-physical) radiance is floored at 0 without a QA flag."""
    radiance = np.array([[-5.0, 0.0, 10.0]], dtype=np.float32)
    floored, qa = flag_radiance(radiance, TOAParams())
    assert_array_equal(floored, [[0.0, 0.0, 10.0]])
    assert_array_equal(qa, [[0, 0, 0]])
    assert floored.dtype == np.float32
    assert qa.dtype == np.uint16


@pytest.mark.unit
def test_flag_radiance_flags_non_finite_as_no_data():
    r"""Non-finite radiance is flagged NO_DATA and zeroed."""
    radiance = np.array([[np.inf, np.nan, 3.0]], dtype=np.float32)
    floored, qa = flag_radiance(radiance, TOAParams())
    assert_array_equal(floored, [[0.0, 0.0, 3.0]])
    assert_array_equal(qa, [[int(QAFlag.NO_DATA), int(QAFlag.NO_DATA), 0]])


@pytest.mark.unit
def test_flag_radiance_flags_fill_value():
    r"""An explicit fill_value sample is flagged NO_DATA."""
    radiance = np.array([[7.0, 8.0]], dtype=np.float32)
    _, qa = flag_radiance(radiance, TOAParams(fill_value=7.0))
    assert_array_equal(qa, [[int(QAFlag.NO_DATA), 0]])


@pytest.mark.unit
def test_earth_sun_distance_perihelion_and_aphelion():
    r"""Closed form: minimum near DOY 4 (perihelion), maximum half a year later."""
    assert_allclose(earth_sun_distance(4), 0.98328, atol=1e-5)
    assert_allclose(earth_sun_distance(186), 1.01672, atol=1e-4)
    # perihelion is the minimum of the cycle
    assert earth_sun_distance(4) < earth_sun_distance(100) < earth_sun_distance(186)


@pytest.mark.unit
def test_solar_geometry_equator_local_noon():
    r"""Equator at J2000 UTC noon: zenith ~= |declination| ~= 23deg, sun due south."""
    zenith, azimuth = solar_geometry(datetime(2000, 1, 1, 12, 0, 0), lon=0.0, lat=0.0)
    # solar declination ~= -23.0deg on 1 Jan -> equatorial noon zenith ~= 23deg
    assert_allclose(math.degrees(zenith), 23.05, atol=0.5)
    # sun in the southern sky -> azimuth ~= 180deg (clockwise from north)
    assert_allclose(math.degrees(azimuth), 180.0, atol=5.0)


@pytest.mark.unit
def test_solar_geometry_returns_radians_in_range():
    r"""Zenith stays within [0, pi] and azimuth within [0, 2*pi)."""
    zenith, azimuth = solar_geometry(datetime(2020, 6, 21, 9, 30, 0), lon=2.35, lat=48.85)
    assert 0.0 <= zenith <= math.pi
    assert 0.0 <= azimuth < 2.0 * math.pi
