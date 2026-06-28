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

"""Geo-referencing / orthorectification stage (C-PU-GEO; DPM-M-GEO; ALG-GEO-*).

Viewing-model geolocation + GSD, ground-control refinement against a geolocated
reference, DEM orthorectification, and resampling onto the profile cartographic
grid/CRS, emitting the ``L1C`` product. The stage is a pure
:mod:`~msi_processor.computing.georeference.core` plus a thin
:class:`~msi_processor.computing.georeference.unit.GeoreferenceUnit` wrapper. The
rigorous viewing-model/DEM collinearity bodies are private/deferred ``[impl]``
(ATBD <5.7> open point 2); the PDR-operational path is the reference-image
homography (``ALG-GEO-GCP``) plus cartographic resampling (``ALG-GEO-RESAMP``).
"""

from msi_processor.computing.georeference.core import (
    GcpRefinement,
    GeoreferenceParams,
    Geotransform,
    GridSpec,
    PlatformState,
    ResamplingMethod,
    assign_grid,
    build_geotransform,
    compute_gsd,
    gcp_refine,
    orbit_state,
    orthorectify,
    resample_to_grid,
)
from msi_processor.computing.georeference.unit import GeoreferenceUnit

__all__ = [
    "ResamplingMethod",
    "PlatformState",
    "Geotransform",
    "GridSpec",
    "GeoreferenceParams",
    "GcpRefinement",
    "compute_gsd",
    "orbit_state",
    "gcp_refine",
    "build_geotransform",
    "assign_grid",
    "resample_to_grid",
    "orthorectify",
    "GeoreferenceUnit",
]
