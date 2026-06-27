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

"""Exception and warning vocabulary of ``msi-processor``.

The typed :class:`~msi_processor.exceptions.errors.MsiProcessorError`
hierarchy (SDD <5.4.1>) is re-exported here for convenient import.
"""

from msi_processor.exceptions.errors import (
    AdfResolutionError,
    AtmosphericError,
    CoregistrationError,
    GeolocationError,
    InputValidationError,
    MsiProcessorError,
    MyError,
    ProductWriteError,
    ProfileValidationError,
    RadiometricError,
)
from msi_processor.exceptions.warnings import MyWarning

__all__ = [
    "MsiProcessorError",
    "InputValidationError",
    "ProfileValidationError",
    "AdfResolutionError",
    "RadiometricError",
    "CoregistrationError",
    "GeolocationError",
    "AtmosphericError",
    "ProductWriteError",
    "MyError",
    "MyWarning",
]
