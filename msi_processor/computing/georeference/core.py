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

"""Pure geo-referencing / orthorectification core (C-PU-GEO; ALG-GEO-*).

CPM-free, I/O-free functions implementing the geo-referencing algorithms of
ATBD <5.7>, ported faithfully from the heritage ``georeferencing_v1.py``
(``getSatelliteInfo.get_satellite_info`` GSD, ``geoReferencing.band_registration``
reference matching, ``reprojection.projection`` GDAL geotransform/CRS; RD-10).
The GPL ``pyorbital``/``skyfield`` TLE fetch and the Earth-Engine Sentinel-2
reference download of the heritage are **dropped** (SRF; non-redistributable): the
orbit/ephemeris state comes from ``L0c`` telemetry / a viewing-model ADF and the
geolocated reference comes from a GCP ADF, never from a network fetch.

**Library policy.** The cartographic-grid resampling (``ALG-GEO-RESAMP``) is
*defined by* the GDAL/PROJ affine-geotransform + reprojection machinery in the
baselined design (ATBD <5.7>, SDD <5.4.7>); it is realised here with
``rasterio``/``affine`` (the maintained GDAL Python binding; ``rasterio`` is
already an ``eopf`` transitive dependency). The ground-control refinement
(``ALG-GEO-GCP``) reuses the OpenCV feature/homography machinery of
:mod:`~msi_processor.computing.coregistration.core` against a geolocated
reference, exactly as the SDD prescribes ("reuse coregistration.core").

**Implementation status.** Two bodies are private/deferred and left as clean,
well-typed ``[impl]`` stubs (they require the proprietary sensor model and are
the CDR target, ATBD <5.7> open point 2):

* :func:`orbit_state` -- orbit/ephemeris propagation engine (the dropped GPL TLE
  path); and
* :func:`orthorectify` -- the rigorous per-pixel collinearity / DEM
  line-of-sight intersection (SDD ``geolocate``; ``ALG-GEO-ORTHO``).

The PDR-operational path realised here is the heritage reference-image homography
(:func:`gcp_refine`) plus the profile cartographic-grid assignment/resampling
(:func:`build_geotransform`, :func:`assign_grid`, :func:`resample_to_grid`); a
proprietary sensor model is **not** fabricated.

Geometry convention. Image arrays are 2-D; up to the GCP refinement they are in
instrument geometry ``(line, detector)``; from the cartographic grid they are
``(y, x)`` (DPM <8.6>). A GDAL geotransform ``[ulx, xres, 0, uly, 0, -yres]``
places the grid; pixel ``(col, row)`` upper-left maps to ``(ulx + col*xres,
uly - row*yres)`` and the cell *centre* to ``(ulx + (col+0.5)*xres, uly -
(row+0.5)*yres)`` (ATBD <5.7> ``ALG-GEO-RESAMP``).

*Trace:* REQ-F-GEO-01..04; DPM-M-GEO; ALG-GEO-ORBIT/GSD/GCP/ORTHO/RESAMP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

import numpy as np
import numpy.typing as npt
from affine import Affine
from rasterio.crs import CRS
from rasterio.warp import Resampling, reproject

from msi_processor.computing.coregistration.core import (
    CoregParams,
    estimate_homography,
    warp_to_reference,
)
from msi_processor.exceptions.errors import CoregistrationError, GeolocationError

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
]

HomographyArray = npt.NDArray[np.float64]
QAArray = npt.NDArray[np.uint16]

#: Supported cartographic resampling kernels (ATBD <5.7> ``ALG-GEO-RESAMP``).
ResamplingMethod = Literal["nearest", "bilinear", "cubic"]

# Map the profile resampling literal to the rasterio enum (CPM-free table).
_RESAMPLING: dict[str, Any] = {
    "nearest": Resampling.nearest,
    "bilinear": Resampling.bilinear,
    "cubic": Resampling.cubic,
}

_STAGE = "georeference"


@dataclass(frozen=True)
class PlatformState:
    """Platform / orbit state at acquisition (ALG-GEO-ORBIT; SDD <5.4.7>).

    Parameters
    ----------
    lat, lon:
        Sub-satellite point latitude/longitude in degrees at acquisition.
    altitude_m:
        Platform altitude above the ellipsoid in metres (drives ``ALG-GEO-GSD``).
    ground_velocity_ms:
        Ground-track velocity in m/s (line-timing kinematics, ATBD <5.7>).
    """

    lat: float
    lon: float
    altitude_m: float
    ground_velocity_ms: float


@dataclass(frozen=True)
class Geotransform:
    """North-up GDAL affine geotransform + CRS (ALG-GEO-RESAMP; SDD <5.4.7>).

    Stores the GDAL 6-tuple ``[ulx, xres, 0, uly, 0, -yres]`` decomposed for a
    north-up grid (zero rotation). ``xres``/``yres`` are stored as positive pixel
    sizes; the south-ward row step ``-yres`` is applied by :meth:`to_affine`.

    Parameters
    ----------
    ulx, uly:
        Map coordinates of the upper-left corner of the upper-left pixel.
    xres, yres:
        Pixel size in map units (positive); the grid is north-up so the
        row direction decreases ``Y`` by ``yres`` per row.
    crs_wkt:
        Target CRS as a WKT string (PROJ/``osr`` encoding).
    """

    ulx: float
    xres: float
    uly: float
    yres: float
    crs_wkt: str

    def to_affine(self) -> Affine:
        """Return the equivalent :class:`affine.Affine` (north-up GDAL order)."""
        return Affine(self.xres, 0.0, self.ulx, 0.0, -self.yres, self.uly)

    @property
    def gdal_tuple(self) -> tuple[float, float, float, float, float, float]:
        """Return the GDAL 6-tuple ``(ulx, xres, 0, uly, 0, -yres)``."""
        return (self.ulx, self.xres, 0.0, self.uly, 0.0, -self.yres)


@dataclass(frozen=True)
class GridSpec:
    """A placed cartographic grid: its geotransform and cell-centre axes.

    The 1-D ``x``/``y`` axes are the cell-centre coordinates the wrapper writes
    to ``/conditions/geolocation/{x,y}`` (the CRS is :attr:`Geotransform.crs_wkt`,
    written to ``/conditions/geolocation/spatial_ref``); REQ-F-GEO-04.

    Parameters
    ----------
    geo:
        The :class:`Geotransform` placing the grid.
    x, y:
        Cell-centre coordinate axes, ``float64`` of length ``width`` / ``height``.
    """

    geo: Geotransform
    x: npt.NDArray[np.float64]
    y: npt.NDArray[np.float64]

    @property
    def shape(self) -> tuple[int, int]:
        """Return the grid ``(height, width)`` = ``(len(y), len(x))``."""
        return (int(self.y.shape[0]), int(self.x.shape[0]))


@dataclass(frozen=True)
class GeoreferenceParams:
    """Tunable geo-referencing parameters (SDD <5.4.7>; DPM-PRM-GEO-01..03).

    Parameters
    ----------
    resolution:
        Output cartographic grid resolution (GSD) in map units
        (``DPM-PRM-GEO-01``; heritage ``~6.5 m``).
    crs_wkt:
        Target CRS as WKT (``DPM-PRM-GEO-01``); empty string inherits the CRS of
        the geolocated GCP reference (heritage behaviour).
    resampling:
        Cartographic resampling kernel (``ALG-GEO-RESAMP``; default bilinear).
    use_gcp:
        Enable the ground-control refinement against the geolocated reference
        (``DPM-PRM-GEO-03``). When ``False`` the rigorous viewing-model/DEM
        geolocation (:func:`orthorectify`) is required, which is ``[impl]``.
    min_gcp:
        Minimum number of inlier ground-control tie points required to accept a
        refinement (the ``GEO_CE90`` acceptance gate, ``DPM-PRM-GEO-03``,
        private budget); below it the refinement is rejected fail-stop.
    coreg:
        Feature-matching parameters for the GCP homography
        (reuses :class:`~msi_processor.computing.coregistration.core.CoregParams`;
        its ``reference_band`` is unused on the two-image GCP path).
    """

    resolution: float
    crs_wkt: str = ""
    resampling: ResamplingMethod = "bilinear"
    use_gcp: bool = True
    min_gcp: int = 8
    coreg: CoregParams = field(default_factory=lambda: CoregParams(reference_band=""))


@dataclass(frozen=True)
class GcpRefinement:
    """Outcome of a ground-control refinement (ALG-GEO-GCP; ICD-IF-DIAG).

    Parameters
    ----------
    n_gcp:
        Number of inlier ground-control tie points supporting the correction.
    rms_residual_px:
        Root-mean-square inlier reprojection residual in pixels.
    homography:
        The ``3x3`` image -> reference planimetric correction (``float64``).
    """

    n_gcp: int
    rms_residual_px: float
    homography: HomographyArray


def compute_gsd(altitude_m: float, pixel_pitch_m: float, focal_length_m: float) -> float:
    r"""ALG-GEO-GSD -- ground sampling distance from the pinhole relation.

    .. math:: \mathrm{GSD} = \dfrac{H\,p}{f},

    with platform altitude :math:`H` (``altitude_m``), detector pitch :math:`p`
    (``pixel_pitch_m``) and focal length :math:`f` (``focal_length_m``); heritage
    ``getSatelliteInfo.get_satellite_info``. The interior geometry :math:`p, f`
    is private viewing-model content supplied by the wrapper from the
    ``viewing_model`` ADF, never embedded (REQ-AD-01).

    Raises
    ------
    GeolocationError
        If ``focal_length_m`` is not strictly positive.
    """
    if focal_length_m <= 0.0:
        raise GeolocationError(
            f"focal_length_m must be positive for GSD (got {focal_length_m})",
            stage=_STAGE,
        )
    return float(altitude_m) * float(pixel_pitch_m) / float(focal_length_m)


def orbit_state(viewing_model: Any, acq_time: datetime) -> PlatformState:
    """ALG-GEO-ORBIT -- propagate the orbit/ephemeris to the acquisition epoch.

    Returns the sub-satellite point, altitude and ground-track velocity at
    ``acq_time`` from the platform ephemeris referenced by ``viewing_model``.

    [impl] -- **deferred.** The heritage propagation used the GPL
    ``pyorbital``/``skyfield`` TLE path, which is dropped (SRF; non-redistributable);
    the operational engine consumes ``L0c`` telemetry / a private ephemeris ADF
    and is the CDR target. This stub raises so callers do not silently rely on a
    fabricated orbit; the wrapper sources the altitude/sub-point from telemetry
    kwargs and feeds :func:`compute_gsd` directly this increment.

    Raises
    ------
    GeolocationError
        Always, until the ephemeris-propagation engine is wired in.
    """
    raise GeolocationError(
        "orbit_state (ALG-GEO-ORBIT ephemeris propagation) is not implemented; "
        "supply the platform state from L0c telemetry / a viewing-model ADF "
        "(the GPL TLE path is dropped; rigorous engine is the CDR target)",
        stage=_STAGE,
    )


def gcp_refine(
    image: npt.NDArray[Any],
    reference: npt.NDArray[Any],
    params: GeoreferenceParams,
) -> tuple[npt.NDArray[Any], GcpRefinement]:
    r"""ALG-GEO-GCP -- refine geolocation against a geolocated reference.

    Reuses the co-registration feature/homography machinery
    (:func:`~msi_processor.computing.coregistration.core.estimate_homography`):
    CLAHE -> SIFT -> FLANN -> RANSAC fits the planimetric homography
    :math:`H` mapping the ``image`` to the geolocated ``reference`` (heritage
    ``geoReferencing.band_registration`` matching a band against a Sentinel-2
    reference), then warps the image onto the reference pixel grid. The number of
    inlier tie points is gated against :attr:`GeoreferenceParams.min_gcp`.

    Parameters
    ----------
    image:
        2-D band to be refined (instrument geometry).
    reference:
        2-D geolocated reference image (its CRS/geotransform come from the GCP
        ADF and are applied to the output by the wrapper).
    params:
        Geo-referencing parameters; :attr:`GeoreferenceParams.coreg` supplies the
        matching tuning and :attr:`GeoreferenceParams.min_gcp` the gate.

    Returns
    -------
    tuple
        ``(refined_image, GcpRefinement)`` -- ``refined_image`` is ``image``
        resampled onto the reference grid (reference ``(rows, cols)`` extent), and
        the :class:`GcpRefinement` carries the inlier count, residual and ``H``.

    Raises
    ------
    GeolocationError
        If the feature matching cannot fit a homography (wraps the underlying
        :class:`~msi_processor.exceptions.errors.CoregistrationError`) or if the
        inlier count is below :attr:`GeoreferenceParams.min_gcp` (fail-stop,
        REQ-F-GEO-03).
    """
    try:
        homography, residual = estimate_homography(image, reference, params.coreg)
    except CoregistrationError as exc:
        raise GeolocationError(
            f"Ground-control matching failed: {exc}",
            stage=_STAGE,
            report_fields=dict(exc.report_fields),
        ) from exc

    if residual.n_inliers < params.min_gcp:
        raise GeolocationError(
            f"Too few ground-control points ({residual.n_inliers} < {params.min_gcp}); "
            "geolocation refinement rejected",
            stage=_STAGE,
            report_fields={"n_gcp": residual.n_inliers, "min_gcp": params.min_gcp},
        )

    ref_shape = (int(reference.shape[0]), int(reference.shape[1]))
    refined = warp_to_reference(image, homography, ref_shape)
    refinement = GcpRefinement(
        n_gcp=residual.n_inliers,
        rms_residual_px=residual.rms_residual_px,
        homography=homography,
    )
    return refined, refinement


def build_geotransform(ulx: float, uly: float, resolution: float, crs_wkt: str) -> Geotransform:
    r"""ALG-GEO-RESAMP -- build a north-up cartographic geotransform.

    Assembles the GDAL affine ``[ulx, xres, 0, uly, 0, -yres]`` with square pixels
    ``xres = yres = resolution`` (heritage ``reprojection.projection`` built
    ``[ulx, 6.5, 0, uly, 0, -6.5]`` and inherited the reference CRS).

    Parameters
    ----------
    ulx, uly:
        Upper-left corner map coordinates of the target grid.
    resolution:
        Target pixel size (GSD) in map units; must be strictly positive.
    crs_wkt:
        Target CRS as WKT.

    Raises
    ------
    GeolocationError
        If ``resolution`` is not strictly positive.
    """
    if resolution <= 0.0:
        raise GeolocationError(
            f"Target grid resolution must be positive (got {resolution})",
            stage=_STAGE,
        )
    return Geotransform(
        ulx=float(ulx),
        xres=float(resolution),
        uly=float(uly),
        yres=float(resolution),
        crs_wkt=crs_wkt,
    )


def assign_grid(shape: tuple[int, int], geo: Geotransform) -> GridSpec:
    r"""ALG-GEO-RESAMP -- derive the cell-centre axes of a placed grid.

    For a grid of ``shape = (height, width)`` placed by ``geo`` the cell-centre
    coordinates are

    .. math::
        x_c = \mathrm{ulx} + (c + 0.5)\,\mathrm{xres},\qquad
        y_r = \mathrm{uly} - (r + 0.5)\,\mathrm{yres},

    the ``/conditions/geolocation/{x,y}`` layers of the ``L1C`` product
    (REQ-F-GEO-04).

    Parameters
    ----------
    shape:
        Target grid ``(height, width)``.
    geo:
        The :class:`Geotransform` placing the grid.

    Returns
    -------
    GridSpec
        The geotransform and the ``float64`` cell-centre ``x``/``y`` axes.
    """
    height, width = int(shape[0]), int(shape[1])
    x = geo.ulx + (np.arange(width, dtype=np.float64) + 0.5) * geo.xres
    y = geo.uly - (np.arange(height, dtype=np.float64) + 0.5) * geo.yres
    return GridSpec(geo=geo, x=x, y=y)


def resample_to_grid(
    image: npt.NDArray[Any],
    src_geo: Geotransform,
    dst_geo: Geotransform,
    dst_shape: tuple[int, int],
    resampling: ResamplingMethod = "bilinear",
) -> npt.NDArray[Any]:
    r"""ALG-GEO-RESAMP -- resample a band onto the profile cartographic grid.

    Warps ``image`` from its source geotransform/CRS to the destination
    cartographic grid via ``rasterio.warp.reproject`` (the maintained GDAL/PROJ
    binding), the operational realisation of ATBD <5.7> ``ALG-GEO-RESAMP``.

    Parameters
    ----------
    image:
        2-D source band; its dtype is preserved on output.
    src_geo:
        Source geotransform + CRS (e.g. the GCP-reference grid).
    dst_geo:
        Target cartographic geotransform + CRS (profile grid).
    dst_shape:
        Output ``(height, width)``. Required because ``reproject`` writes into a
        pre-allocated destination (deviation from the SDD sketch, which elides the
        explicit extent); the wrapper derives it from the source extent and the
        target resolution.
    resampling:
        Resampling kernel (``"nearest" | "bilinear" | "cubic"``).

    Returns
    -------
    numpy.ndarray
        The resampled band, dtype-preserving, of shape ``dst_shape``.
    """
    src = np.asarray(image)
    destination = np.zeros((int(dst_shape[0]), int(dst_shape[1])), dtype=src.dtype)
    reproject(
        source=src,
        destination=destination,
        src_transform=src_geo.to_affine(),
        src_crs=CRS.from_wkt(src_geo.crs_wkt),
        dst_transform=dst_geo.to_affine(),
        dst_crs=CRS.from_wkt(dst_geo.crs_wkt),
        resampling=_RESAMPLING[resampling],
    )
    return np.asarray(destination, dtype=src.dtype)


def orthorectify(
    image: npt.NDArray[Any],
    state: PlatformState,
    viewing_model: Any,
    dem: npt.NDArray[Any],
) -> npt.NDArray[Any]:
    r"""ALG-GEO-ORTHO -- rigorous collinearity / DEM orthorectification.

    The rigorous target model intersects each detector line-of-sight with the
    ellipsoid + DEM via the collinearity relation (ATBD <5.7>): for ground point
    :math:`\mathbf X`, platform position :math:`\mathbf X_0`, attitude
    :math:`R(\omega,\varphi,\kappa)` and interior geometry,

    .. math::
        \begin{bmatrix}x\\y\\-f\end{bmatrix} =
        \lambda\,R^{\!\top}\big(\mathbf X-\mathbf X_0\big),\qquad Z=\mathrm{DEM}(X,Y),

    solved per pixel so terrain-induced displacement is removed (SDD ``geolocate``).

    [impl] -- **deferred.** The rigorous sensor model and the DEM line-of-sight
    intersection require the proprietary viewing-model coefficients and are the
    CDR target (ATBD <5.7> open point 2). A proprietary model is **not**
    fabricated here; the PDR-operational geolocation is the reference-image
    homography of :func:`gcp_refine` followed by :func:`resample_to_grid`. This
    stub raises so the no-GCP path fails loudly rather than emitting an
    un-orthorectified product as if it were rigorous.

    Raises
    ------
    GeolocationError
        Always, until the rigorous collinearity/DEM model is wired in.
    """
    raise GeolocationError(
        "orthorectify (ALG-GEO-ORTHO rigorous collinearity / DEM) is not "
        "implemented; it requires the private viewing model and is the CDR target. "
        "Use the GCP reference-image path (use_gcp=True) for operational L1C.",
        stage=_STAGE,
    )
