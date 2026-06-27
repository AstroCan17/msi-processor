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

"""TOA radiance/reflectance stage (C-PU-TOA; DPM-M-TOA; ALG-TOA-RAD/REF).

DN->TOA radiance (mandatory) and optional DN->TOA reflectance, emitting the
``L1B`` product. The stage is a pure
:mod:`~msi_processor.computing.toa.core` plus a thin
:class:`~msi_processor.computing.toa.unit.ToaUnit` wrapper.
"""

from msi_processor.computing.toa.core import (
    TOAParams,
    dn_to_radiance,
    earth_sun_distance,
    flag_radiance,
    radiance_to_reflectance,
    solar_geometry,
)
from msi_processor.computing.toa.unit import ToaUnit

__all__ = [
    "TOAParams",
    "dn_to_radiance",
    "radiance_to_reflectance",
    "flag_radiance",
    "earth_sun_distance",
    "solar_geometry",
    "ToaUnit",
]
