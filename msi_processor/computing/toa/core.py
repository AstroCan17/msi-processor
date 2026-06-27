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

"""Pure TOA radiance/reflectance core (C-PU-TOA; ALG-TOA-RAD/REF).

CPM-free, I/O-free numpy/math functions implementing the TOA algorithms of
ATBD <5.3>, ported faithfully from the heritage ``level_1.py`` ``TOA`` class
(``dn_to_radiance`` / ``toa_rad_to_ref`` / ``get_ESUN`` / ``get_sun_el_esdist``;
RD-10). All arrays are processed in ``float32`` (REQ-F-DEP-02, REQ-D-05).

Two heritage simplifications are corrected here (ATBD <5.3> open points):

* the per-image ``radiance -= radiance.min()`` rebasing is **dropped** (not
  radiometrically rigorous); and
* solar geometry is no longer derived from the satellite sub-point through a
  GPL ``pyorbital`` TLE fetch. :func:`solar_geometry` is a dependency-free
  NOAA solar-position computation and :func:`earth_sun_distance` a closed form,
  so the GPL dependency is removed (SRF SRF-RU-HER-TOA); at run time the unit
  takes illumination geometry from ``L0c`` telemetry / ADF per the ICD.

Private calibration constants (per-band ESUN, radiometric gain/offset) are
**never** embedded; they are supplied to these functions by the wrapper from
the ``radiometric`` / ``spectral`` ADFs (REQ-AD-01).

Geometry convention: arrays are 2-D ``(line, detector)`` in focal-plane
geometry; per-detector ``gain``/``offset`` are 1-D ``(detector,)`` vectors
broadcast across lines (ATBD <4.2>, SDD <5.4.5>).

*Trace:* REQ-F-TOA-01..03; DPM-M-TOA; ALG-TOA-RAD/REF.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

import numpy as np
import numpy.typing as npt

from msi_processor.common.types import QAFlag

__all__ = [
    "TOAParams",
    "dn_to_radiance",
    "radiance_to_reflectance",
    "flag_radiance",
    "earth_sun_distance",
    "solar_geometry",
]

FloatArray = npt.NDArray[np.float32]
QAArray = npt.NDArray[np.uint16]


@dataclass(frozen=True)
class TOAParams:
    """Tunable TOA parameters (SDD <5.4.5>; DPM-PRM-TOA-03).

    Parameters
    ----------
    emit_reflectance:
        When ``True`` the optional radiance->TOA-reflectance stage is run in
        addition to the mandatory DN->radiance stage (REQ-F-TOA-02,
        ``DPM-PRM-TOA-03``).
    fill_value:
        No-data sentinel radiance; flagged :attr:`QAFlag.NO_DATA` when present.
    """

    emit_reflectance: bool = False
    fill_value: Optional[float] = None


def dn_to_radiance(
    dn: npt.NDArray[Any],
    gain: Union[npt.NDArray[Any], float],
    offset: Union[npt.NDArray[Any], float],
) -> FloatArray:
    r"""ALG-TOA-RAD — convert corrected DN to at-sensor (TOA) radiance.

    Linear inversion of the radiometric model (heritage ``TOA.dn_to_radiance``):

    .. math::

        L^{(b)}_{l,d} = \big(\mathrm{DN}^{(b)}_{l,d} - o^{\mathrm{rad},(b)}\big)
        \, g^{\mathrm{rad},(b)} .

    ``gain``/``offset`` are the absolute radiometric coefficients from the
    ``radiometric`` ADF; they may be per-band scalars or 1-D ``(detector,)``
    vectors broadcast across lines.

    Notes
    -----
    The heritage per-image ``radiance -= radiance.min()`` rebasing is **not**
    applied (ATBD <5.3>, open point); negative/no-data handling is deferred to
    :func:`flag_radiance`. Returns ``float32``.
    """
    dn_f = np.asarray(dn, dtype=np.float32)
    gain_f = np.asarray(gain, dtype=np.float32)
    offset_f = np.asarray(offset, dtype=np.float32)
    radiance = (dn_f - offset_f) * gain_f
    return radiance.astype(np.float32)


def radiance_to_reflectance(
    radiance: npt.NDArray[Any],
    esun: float,
    sun_zenith_rad: float,
    earth_sun_dist_au: float,
) -> FloatArray:
    r"""ALG-TOA-REF — convert TOA radiance to TOA reflectance.

    The canonical solar normalisation (heritage ``TOA.toa_rad_to_ref``):

    .. math::

        \rho^{(b)}_{\mathrm{TOA}} =
        \dfrac{\pi\,L^{(b)}\,d_{\mathrm{ES}}^{\,2}}{E^{(b)}_{\mathrm{SUN}}
        \,\cos\theta_s} ,

    with ``esun`` the band-integrated exo-atmospheric solar irradiance
    :math:`E_{\mathrm{SUN}}` (``spectral`` ADF / profile), ``earth_sun_dist_au``
    the Earth-Sun distance :math:`d_{\mathrm{ES}}` in AU at acquisition, and
    ``sun_zenith_rad`` the **solar** zenith angle :math:`\theta_s` in radians.
    The result is clipped to ``[0, 1]`` (REQ-D-05). Returns ``float32``.
    """
    radiance_f = np.asarray(radiance, dtype=np.float32)
    cos_theta = math.cos(sun_zenith_rad)
    numerator = np.pi * radiance_f * np.float32(earth_sun_dist_au) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        reflectance = numerator / (np.float32(esun) * np.float32(cos_theta))
    clipped = np.clip(np.nan_to_num(reflectance, nan=0.0, posinf=1.0, neginf=0.0), 0.0, 1.0)
    return clipped.astype(np.float32)


def flag_radiance(radiance: npt.NDArray[Any], params: TOAParams) -> tuple[FloatArray, QAArray]:
    r"""Floor non-physical radiance and flag no-data (SDD <5.4.5> error handling).

    Non-finite samples (e.g. from a non-finite gain) and any equal to
    ``params.fill_value`` are flagged :attr:`QAFlag.NO_DATA`; the data is then
    floored at 0 (radiance is non-negative by definition, ICD <5.3.3>B; the
    upper bound is physical, not the DN ceiling, so no top clip is applied).
    Mirrors the radiometric ``flag_saturation`` contract.

    Returns
    -------
    tuple of ndarray
        ``(floored[float32], qa[uint16])`` of the same shape as ``radiance``.
    """
    data = np.asarray(radiance, dtype=np.float32)
    qa = np.zeros(data.shape, dtype=np.uint16)
    finite = np.isfinite(data)
    qa[~finite] |= np.uint16(QAFlag.NO_DATA)
    if params.fill_value is not None:
        qa[finite & (data == np.float32(params.fill_value))] |= np.uint16(QAFlag.NO_DATA)
    floored = np.clip(np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0), 0.0, None)
    return floored.astype(np.float32), qa


def earth_sun_distance(doy: int) -> float:
    r"""Earth-Sun distance in AU from the day-of-year (ATBD <5.3>).

    .. math::

        d_{\mathrm{ES}} \approx 1 - 0.01672\,
        \cos\!\big(0.9856^\circ\,(\mathrm{DOY}-4)\big),

    a closed-form approximation (perihelion near DOY 4). A solar ephemeris may
    be substituted via :func:`solar_geometry`'s caller when sub-second accuracy
    is required.
    """
    angle_deg = 0.9856 * (doy - 4)
    return 1.0 - 0.01672 * math.cos(math.radians(angle_deg))


def solar_geometry(acq_time: datetime, lon: float, lat: float) -> tuple[float, float]:
    """Solar zenith/azimuth from acquisition time and sub-point (NOAA algorithm).

    A dependency-free implementation of the NOAA solar-position algorithm,
    replacing the heritage satellite-sub-point conflation that relied on the
    GPL ``pyorbital`` TLE fetch (ATBD <5.3> open point; SRF SRF-RU-HER-TOA).

    Parameters
    ----------
    acq_time:
        Acquisition time in **UTC** (naive datetimes are treated as UTC).
    lon, lat:
        Sub-point longitude/latitude in degrees (east/north positive).

    Returns
    -------
    tuple of float
        ``(sun_zenith_rad, sun_azimuth_rad)`` with azimuth measured clockwise
        from geographic north.
    """
    hour = acq_time.hour + acq_time.minute / 60.0 + acq_time.second / 3600.0
    year, month, day = acq_time.year, acq_time.month, acq_time.day
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5 + hour / 24.0
    t = (jd - 2451545.0) / 36525.0

    mean_long = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360.0
    mean_anom = 357.52911 + t * (35999.05029 - 0.0001537 * t)
    mean_anom_rad = math.radians(mean_anom)
    eccentricity = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    centre = (
        math.sin(mean_anom_rad) * (1.914602 - t * (0.004817 + 0.000014 * t))
        + math.sin(2 * mean_anom_rad) * (0.019993 - 0.000101 * t)
        + math.sin(3 * mean_anom_rad) * 0.000289
    )
    true_long = mean_long + centre
    omega = 125.04 - 1934.136 * t
    app_long = math.radians(true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega)))
    obliquity = 23.0 + (26.0 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0) / 60.0
    obliquity_corr = math.radians(obliquity + 0.00256 * math.cos(math.radians(omega)))
    declination = math.asin(math.sin(obliquity_corr) * math.sin(app_long))

    var_y = math.tan(obliquity_corr / 2.0) ** 2
    mean_long_rad = math.radians(mean_long)
    eot = 4.0 * math.degrees(
        var_y * math.sin(2 * mean_long_rad)
        - 2 * eccentricity * math.sin(mean_anom_rad)
        + 4 * eccentricity * var_y * math.sin(mean_anom_rad) * math.cos(2 * mean_long_rad)
        - 0.5 * var_y * var_y * math.sin(4 * mean_long_rad)
        - 1.25 * eccentricity * eccentricity * math.sin(2 * mean_anom_rad)
    )

    minutes_utc = acq_time.hour * 60.0 + acq_time.minute + acq_time.second / 60.0
    true_solar_time = (minutes_utc + eot + 4.0 * lon) % 1440.0
    hour_angle = true_solar_time / 4.0 - 180.0
    hour_angle_rad = math.radians(hour_angle)

    lat_rad = math.radians(lat)
    cos_zenith = math.sin(lat_rad) * math.sin(declination) + math.cos(lat_rad) * math.cos(declination) * math.cos(
        hour_angle_rad
    )
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith = math.acos(cos_zenith)

    sin_zenith = math.sin(zenith)
    if sin_zenith < 1e-9:
        return zenith, 0.0
    cos_azimuth = (math.sin(lat_rad) * math.cos(zenith) - math.sin(declination)) / (math.cos(lat_rad) * sin_zenith)
    cos_azimuth = max(-1.0, min(1.0, cos_azimuth))
    azimuth_deg = math.degrees(math.acos(cos_azimuth))
    azimuth_deg = (azimuth_deg + 180.0) % 360.0 if hour_angle > 0.0 else (540.0 - azimuth_deg) % 360.0
    return zenith, math.radians(azimuth_deg)
