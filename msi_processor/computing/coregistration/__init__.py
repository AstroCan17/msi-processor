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

"""Inter-band co-registration stage (C-PU-COR; DPM-M-COR; ALG-COR-FEAT/HOM/WARP).

Feature-based (CLAHE -> SIFT -> FLANN -> RANSAC homography -> warp) alignment of
the spectral bands to a profile-defined reference band, emitting the co-registered
``cor`` product. The stage is a pure
:mod:`~msi_processor.computing.coregistration.core` plus a thin
:class:`~msi_processor.computing.coregistration.unit.CoregistrationUnit` wrapper.
"""

from msi_processor.computing.coregistration.core import (
    CoregParams,
    CoregResidual,
    coregister,
    detect_and_match,
    estimate_homography,
    warp_qa,
    warp_to_reference,
)
from msi_processor.computing.coregistration.unit import CoregistrationUnit

__all__ = [
    "CoregParams",
    "CoregResidual",
    "detect_and_match",
    "estimate_homography",
    "warp_to_reference",
    "warp_qa",
    "coregister",
    "CoregistrationUnit",
]
