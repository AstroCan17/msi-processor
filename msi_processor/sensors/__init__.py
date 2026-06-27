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

"""Sensor adaptation layer (C-SENSORS).

Externalises all sensor-specific *data* (band set, radiometric depth, GSD,
ADF bindings) so the generic processing chain stays sensor-agnostic: a new
sensor is a new profile plus private ADFs, with no core change (REQ-AD-01,
REQ-D-07). This package contains **no instrument constants in code and no
algorithm code** (REQ-D-04); private calibration values live only in the
ADFs, which the profile references by URI (REQ-S-01/05).
"""
