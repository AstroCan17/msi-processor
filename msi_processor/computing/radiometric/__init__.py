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

"""Radiometric correction stage (C-PU-RAD; DPM-M-RAD; ALG-RAD-*).

Dark/offset (DSNU) subtraction, NUC/flat-field (PRNU) equalisation,
bad-pixel detection & replacement, and saturation/no-data flagging. The
stage is a pure :mod:`~msi_processor.computing.radiometric.core` plus a thin
:class:`~msi_processor.computing.radiometric.unit.RadiometricUnit` wrapper.
"""

from msi_processor.computing.radiometric.core import (
    RadiometricParams,
    apply_nuc,
    detect_bad_pixels,
    estimate_nuc,
    flag_saturation,
    remove_dark_fft,
    replace_bad_pixels,
)
from msi_processor.computing.radiometric.unit import RadiometricUnit

__all__ = [
    "RadiometricParams",
    "estimate_nuc",
    "apply_nuc",
    "detect_bad_pixels",
    "replace_bad_pixels",
    "flag_saturation",
    "remove_dark_fft",
    "RadiometricUnit",
]
