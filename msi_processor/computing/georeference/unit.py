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

"""Thin ``EOProcessingUnit`` wrapper for geo-referencing / ortho (C-PU-GEO).

Adapts the pure :mod:`~msi_processor.computing.georeference.core` to the EOPF CPM
runtime following the wrapper template of SDD <5.4.1>/<5.4.7>: read parameters,
extract the co-registered bands, load/validate ADFs, orchestrate the pure-core
functions, propagate QA, and build the output ``L1C`` ``EOProduct`` on the
profile cartographic grid. No algorithm lives here.

Input convention. The upstream stage is the ``coregistration`` unit; its ``cor``
product carries the band-aligned measurements under ``measurements/<rep>/<band>``
(``rep`` = ``radiance`` and/or ``reflectance``) and QA under ``quality/mask/<band>``
(IF-PROD-03). Every present measurement representation is geo-referenced with the
**same** planimetric correction so the stack stays consistent; ``L1C`` is the
orthorectified TOA reflectance on the cartographic grid (DPM <8.6>).

ADF data convention (this increment). ADF content is read from the
``AuxiliaryDataFile.data_ptr`` mapping (the CPM ``data_ptr`` holds the opened
data):

* ``viewing_model`` -> ``{"pixel_pitch_m": float, "focal_length_m": float, ...}``
  (mandatory; interior geometry for ``ALG-GEO-GSD`` and the rigorous LOS model,
  ICD <5.3.2>A). The rigorous viewing-model body is ``[impl]``; presence/coverage
  is enforced here (REQ-F-GEO-01, fail-stop on absence).
* ``dem`` -> ``{"elevation": ndarray2d, "geotransform": [6], "crs_wkt": str}``
  (mandatory; consumed by the rigorous orthorectification, which is ``[impl]``;
  presence/coverage is enforced here, REQ-F-GEO-02).
* ``gcp`` -> ``{"image": ndarray2d, "geotransform": [ulx,xres,0,uly,0,-yres],
  "crs_wkt": str}`` (optional; required when ``use_gcp`` is set: the geolocated
  reference for ``ALG-GEO-GCP``).

**Implementation status (ATBD <5.7> open point 2).** The rigorous viewing-model +
DEM collinearity geolocation (:func:`~msi_processor.computing.georeference.core.orthorectify`)
is the CDR target and is left ``[impl]``. The PDR-operational path realised here
is the heritage reference-image homography (``ALG-GEO-GCP``) plus profile
cartographic-grid resampling (``ALG-GEO-RESAMP``); it therefore requires
``use_gcp=True`` and the ``gcp`` ADF. With ``use_gcp=False`` the unit invokes the
``[impl]`` rigorous path, which fail-stops with a clear
:class:`~msi_processor.exceptions.errors.GeolocationError`.

**Fail-stop (REQ-F-GEO-03).** Missing DEM/viewing-model coverage, a missing GCP
reference when refinement is enabled, or too few ground-control points raise
:class:`~msi_processor.exceptions.errors.GeolocationError`; it propagates to the
chain runner so no mis-geolocated product is emitted.

Mandatory inputs/ADFs are declared by the CPM computing-model JSON
(``models/msi_georeference_1.0.0.json``), not by overriding the list methods.

*Trace:* REQ-F-GEO-01..04; DPM-M-GEO; ALG-GEO-*; ICD IF-PROD-03, REQ-IF-OUT-02.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, cast

import numpy as np
import numpy.typing as npt
from eopf.computing.abstract import (
    AuxiliaryDataFile,
    DataType,
    EOProcessingUnit,
    MappingAuxiliary,
    MappingDataType,
)
from eopf.logging import EOLogging
from eopf.product import EOGroup, EOProduct, EOVariable

from msi_processor.common.types import QAFlag
from msi_processor.computing.coregistration.core import (
    CoregParams,
    warp_qa,
    warp_to_reference,
)
from msi_processor.computing.georeference.core import (
    GcpRefinement,
    GeoreferenceParams,
    Geotransform,
    ResamplingMethod,
    assign_grid,
    build_geotransform,
    gcp_refine,
    orthorectify,
    resample_to_grid,
)
from msi_processor.exceptions.errors import (
    AdfResolutionError,
    GeolocationError,
    InputValidationError,
)

_MEASUREMENTS = "measurements"
_MASK_GROUP = "quality/mask"
_GEOLOCATION = "conditions/geolocation"
_DIMS = ("y", "x")
_STAGE = "georeference"
_ALLOWED_RESAMPLING: tuple[ResamplingMethod, ...] = ("nearest", "bilinear", "cubic")


def _coerce_mapping(adf: AuxiliaryDataFile) -> dict[str, Any]:
    """Return the ADF content mapping from ``data_ptr`` (raise if unusable)."""
    ptr = adf.data_ptr
    if isinstance(ptr, Mapping):
        return dict(ptr)
    raise AdfResolutionError(f"ADF '{adf.name}' has no usable data_ptr mapping", stage=_STAGE)


def _require_adf(adfs: Mapping[str, AuxiliaryDataFile], name: str) -> AuxiliaryDataFile:
    """Fetch a mandatory ADF or raise :class:`GeolocationError` (coverage fail-stop)."""
    adf = adfs.get(name)
    if adf is None:
        raise GeolocationError(f"Missing mandatory ADF '{name}' for georeference run", stage=_STAGE)
    return adf


def _read_measurement_groups(product: EOProduct) -> dict[str, dict[str, npt.NDArray[Any]]]:
    """Extract ``measurements/<rep>/<band>`` arrays keyed by representation."""
    try:
        measurements = cast(EOGroup, product[_MEASUREMENTS])
    except KeyError as exc:
        raise InputValidationError(
            f"Input co-registered product has no '{_MEASUREMENTS}' group",
            stage=_STAGE,
        ) from exc
    groups: dict[str, dict[str, npt.NDArray[Any]]] = {}
    for rep_name, rep in measurements.items():
        if not isinstance(rep, EOGroup):
            continue
        bands: dict[str, npt.NDArray[Any]] = {}
        for band_name, var in rep.items():
            bands[band_name] = np.asarray(cast(EOVariable, var).data)
        if bands:
            groups[rep_name] = bands
    if not groups:
        raise InputValidationError(
            f"Input co-registered product has no bands under '{_MEASUREMENTS}'",
            stage=_STAGE,
        )
    return groups


def _read_qa_masks(product: EOProduct) -> dict[str, npt.NDArray[np.uint16]]:
    """Extract upstream ``quality/mask/<band>`` arrays (empty if absent)."""
    try:
        group = cast(EOGroup, product[_MASK_GROUP])
    except KeyError:
        return {}
    masks: dict[str, npt.NDArray[np.uint16]] = {}
    for name, item in group.items():
        masks[name] = np.asarray(cast(EOVariable, item).data, dtype=np.uint16)
    return masks


def _geotransform_from_adf(content: Mapping[str, Any], crs_override: str) -> Geotransform:
    """Build a :class:`Geotransform` from a GCP/DEM ADF (GDAL 6-tuple + CRS)."""
    gdal = content.get("geotransform")
    if gdal is None or len(gdal) < 6:
        raise GeolocationError(
            "GCP reference ADF must carry a 6-element GDAL 'geotransform'",
            stage=_STAGE,
        )
    crs_wkt = crs_override or str(content.get("crs_wkt", ""))
    if not crs_wkt:
        raise GeolocationError("GCP reference ADF must carry a 'crs_wkt'", stage=_STAGE)
    return Geotransform(
        ulx=float(gdal[0]),
        xres=float(gdal[1]),
        uly=float(gdal[3]),
        yres=-float(gdal[5]),
        crs_wkt=crs_wkt,
    )


class GeoreferenceUnit(EOProcessingUnit):
    """Geo-referencing / orthorectification processing unit (C-PU-GEO; SDD <5.4.7>).

    Methods
    -------
    run:
        Geolocate the co-registered stack (GCP refinement against the geolocated
        reference, then cartographic-grid resampling) and emit the ``L1C`` product
        with CRS + geolocation layers and QA. The rigorous viewing-model/DEM
        orthorectification is ``[impl]`` (ATBD <5.7> open point 2).
    """

    PROCESSOR_NAME = "msi_georeference"
    PROCESSOR_VERSION = "1.0.0"
    PROCESSOR_LEVEL = "L1C"
    PROCESSOR_MODEL = True

    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """Run the geo-referencing.

        Parameters
        ----------
        inputs:
            ``{"cor": EOProduct}`` with co-registered bands under
            ``measurements/<rep>/<band>`` and optional QA under
            ``quality/mask/<band>``.
        adfs:
            ``viewing_model`` (mandatory), ``dem`` (mandatory), ``gcp`` (optional;
            required when ``use_gcp`` is set).
        mode:
            ``"default"`` (the only supported mode).
        **kwargs:
            :class:`GeoreferenceParams` fields -- ``resolution`` (mandatory),
            ``crs`` (target CRS WKT; empty inherits the GCP-reference CRS),
            ``resampling``, ``use_gcp``, ``min_gcp`` -- plus GCP matching tuning
            (``match_fraction``, ``ransac_tau``, ``min_keypoints``, ``seed``), an
            optional ``gcp_reference_band``, and an optional ``name`` for the
            output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"l1c": EOProduct}`` with gridded ``measurements/<rep>/<band>``,
            ``conditions/geolocation/{x,y,spatial_ref}`` and ``quality/mask/<band>``.

        Raises
        ------
        GeolocationError
            On missing DEM/viewing-model coverage, a missing GCP reference when
            refinement is enabled, too few ground-control points, or the ``[impl]``
            rigorous path (``use_gcp=False``) -- fail-stop (REQ-F-GEO-03).
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "default"
        if run_mode != "default":
            raise InputValidationError(
                f"Unknown georeference mode '{run_mode}'; expected 'default'",
                stage=_STAGE,
            )

        params = self._build_params(kwargs)
        adf_map: Mapping[str, AuxiliaryDataFile] = adfs or {}

        if "cor" not in inputs:
            raise InputValidationError("Missing mandatory input 'cor' for georeference run", stage=_STAGE)
        cor = cast(EOProduct, inputs["cor"])
        groups = _read_measurement_groups(cor)
        upstream_qa = _read_qa_masks(cor)

        # Mandatory ADF coverage (REQ-F-GEO-01/02): viewing-model + DEM presence is
        # enforced regardless of path; their rigorous consumption is [impl].
        _require_adf(adf_map, "viewing_model")
        _require_adf(adf_map, "dem")

        primary_rep, band_names = self._primary_representation(groups)
        logger.info(
            f"Georeference: {len(groups)} representation(s) "
            f"({', '.join(sorted(groups))}), {len(band_names)} band(s), "
            f"target {params.resolution} m, use_gcp={params.use_gcp}"
        )

        if not params.use_gcp:
            # Rigorous viewing-model/DEM geolocation is the only non-GCP path and is
            # [impl]; delegate so the failure is explicit rather than a silent
            # un-orthorectified product (ATBD <5.7> open point 2).
            self._rigorous_geolocate(groups[primary_rep][band_names[0]], adf_map)

        homography, refinement, src_geo = self._refine_against_reference(
            groups, primary_rep, band_names, adf_map, params, kwargs
        )

        target_geo = build_geotransform(
            ulx=src_geo.ulx,
            uly=src_geo.uly,
            resolution=params.resolution,
            crs_wkt=params.crs_wkt or src_geo.crs_wkt,
        )
        ref_shape = self._reference_shape(groups[primary_rep][band_names[0]], homography, src_geo)
        dst_shape = self._target_shape(ref_shape, src_geo.xres, src_geo.yres, params.resolution)
        grid = assign_grid(dst_shape, target_geo)
        coverage = self._coverage_no_data(ref_shape, src_geo, target_geo, dst_shape)

        out_groups: dict[str, dict[str, npt.NDArray[Any]]] = {}
        for rep_name, bands in groups.items():
            out_bands: dict[str, npt.NDArray[Any]] = {}
            for band, data in bands.items():
                warped = warp_to_reference(data, homography, ref_shape)
                out_bands[band] = resample_to_grid(warped, src_geo, target_geo, dst_shape, params.resampling)
            out_groups[rep_name] = out_bands

        out_qa = self._georeference_qa(
            band_names, upstream_qa, homography, ref_shape, src_geo, target_geo, dst_shape, coverage
        )

        output_name = str(kwargs.get("name", f"{cor.name}_L1C"))
        l1c = self._build_l1c_product(output_name, out_groups, out_qa, grid, refinement, params)
        outputs: dict[str, DataType] = {"l1c": l1c}
        return outputs

    # ----------------------------------------------------------------------- #
    # Parameter / structure helpers                                           #
    # ----------------------------------------------------------------------- #

    @staticmethod
    def _build_params(kwargs: Mapping[str, Any]) -> GeoreferenceParams:
        """Build :class:`GeoreferenceParams` from the run kwargs (with defaults)."""
        if kwargs.get("resolution") is None:
            raise InputValidationError(
                "georeference requires a 'resolution' (target grid GSD) parameter",
                stage=_STAGE,
            )
        resampling_raw = str(kwargs.get("resampling", "bilinear"))
        resampling: Optional[ResamplingMethod] = None
        for allowed in _ALLOWED_RESAMPLING:
            if resampling_raw == allowed:
                resampling = allowed  # narrows to the ResamplingMethod literal (no cast)
                break
        if resampling is None:
            raise InputValidationError(
                f"Unknown resampling '{resampling_raw}'; expected one of {_ALLOWED_RESAMPLING}",
                stage=_STAGE,
            )
        max_residual = kwargs.get("max_residual")
        coreg = CoregParams(
            reference_band="",
            match_fraction=float(kwargs.get("match_fraction", 0.10)),
            min_keypoints=int(kwargs.get("min_keypoints", 20)),
            ransac_tau=float(kwargs.get("ransac_tau", 5.0)),
            max_residual=None if max_residual is None else float(max_residual),
            seed=int(kwargs.get("seed", 0)),
        )
        return GeoreferenceParams(
            resolution=float(kwargs["resolution"]),
            crs_wkt=str(kwargs.get("crs", "")),
            resampling=resampling,
            use_gcp=bool(kwargs.get("use_gcp", True)),
            min_gcp=int(kwargs.get("min_gcp", 8)),
            coreg=coreg,
        )

    @staticmethod
    def _primary_representation(
        groups: Mapping[str, Mapping[str, npt.NDArray[Any]]],
    ) -> tuple[str, list[str]]:
        """Pick the GCP-matching representation (reflectance preferred) + band ids."""
        rep = "reflectance" if "reflectance" in groups else sorted(groups)[0]
        return rep, sorted(groups[rep])

    def _refine_against_reference(
        self,
        groups: Mapping[str, Mapping[str, npt.NDArray[Any]]],
        primary_rep: str,
        band_names: list[str],
        adf_map: Mapping[str, AuxiliaryDataFile],
        params: GeoreferenceParams,
        kwargs: Mapping[str, Any],
    ) -> tuple[npt.NDArray[np.float64], GcpRefinement, Geotransform]:
        """Match the GCP reference band to the geolocated reference (ALG-GEO-GCP)."""
        gcp_adf = adf_map.get("gcp")
        if gcp_adf is None:
            raise GeolocationError(
                "Ground-control refinement is enabled (use_gcp=True) but the 'gcp' "
                "ADF (geolocated reference) is missing",
                stage=_STAGE,
            )
        content = _coerce_mapping(gcp_adf)
        reference = content.get("image")
        if reference is None:
            raise GeolocationError("gcp ADF must carry a geolocated reference 'image'", stage=_STAGE)
        reference_arr = np.asarray(reference)
        src_geo = _geotransform_from_adf(content, params.crs_wkt)

        ref_band = str(kwargs.get("gcp_reference_band", band_names[0]))
        if ref_band not in groups[primary_rep]:
            raise GeolocationError(
                f"gcp_reference_band '{ref_band}' is not among the '{primary_rep}' bands",
                stage=_STAGE,
            )
        _, refinement = gcp_refine(groups[primary_rep][ref_band], reference_arr, params)
        return refinement.homography, refinement, src_geo

    @staticmethod
    def _rigorous_geolocate(image: npt.NDArray[Any], adf_map: Mapping[str, AuxiliaryDataFile]) -> None:
        """Invoke the [impl] rigorous viewing-model/DEM path (fail-stop)."""
        dem_content = _coerce_mapping(_require_adf(adf_map, "dem"))
        dem = np.asarray(dem_content.get("elevation", np.zeros((1, 1), dtype=np.float32)))
        # State is unavailable without the ephemeris engine; orthorectify is [impl]
        # and raises GeolocationError before the state is used.
        from msi_processor.computing.georeference.core import PlatformState

        state = PlatformState(lat=0.0, lon=0.0, altitude_m=0.0, ground_velocity_ms=0.0)
        orthorectify(image, state, adf_map.get("viewing_model"), dem)

    @staticmethod
    def _reference_shape(
        sample: npt.NDArray[Any],
        homography: npt.NDArray[np.float64],
        src_geo: Geotransform,
    ) -> tuple[int, int]:
        """Reference (GCP-grid) shape every band is warped onto before resampling."""
        warped = warp_to_reference(sample, homography, (sample.shape[0], sample.shape[1]))
        return (int(warped.shape[0]), int(warped.shape[1]))

    @staticmethod
    def _target_shape(
        ref_shape: tuple[int, int],
        src_xres: float,
        src_yres: float,
        dst_res: float,
    ) -> tuple[int, int]:
        """Cartographic-grid shape preserving the source map extent at ``dst_res``."""
        rows = max(1, int(round(ref_shape[0] * src_yres / dst_res)))
        cols = max(1, int(round(ref_shape[1] * src_xres / dst_res)))
        return rows, cols

    @staticmethod
    def _coverage_no_data(
        ref_shape: tuple[int, int],
        src_geo: Geotransform,
        target_geo: Geotransform,
        dst_shape: tuple[int, int],
    ) -> npt.NDArray[np.uint16]:
        """NO_DATA mask where the resampled grid has no source coverage."""
        ones = np.ones(ref_shape, dtype=np.uint16)
        covered = resample_to_grid(ones, src_geo, target_geo, dst_shape, "nearest")
        return np.where(np.asarray(covered) == 0, np.uint16(QAFlag.NO_DATA), np.uint16(0)).astype(np.uint16)

    @staticmethod
    def _georeference_qa(
        band_names: list[str],
        upstream_qa: Mapping[str, npt.NDArray[np.uint16]],
        homography: npt.NDArray[np.float64],
        ref_shape: tuple[int, int],
        src_geo: Geotransform,
        target_geo: Geotransform,
        dst_shape: tuple[int, int],
        coverage: npt.NDArray[np.uint16],
    ) -> dict[str, npt.NDArray[np.uint16]]:
        """Warp + resample each band's QA to the grid and OR the NO_DATA coverage."""
        out_qa: dict[str, npt.NDArray[np.uint16]] = {}
        for band in band_names:
            base = upstream_qa.get(band)
            if base is None:
                out_qa[band] = coverage.copy()
                continue
            warped = warp_qa(base, homography, ref_shape)
            gridded = resample_to_grid(warped, src_geo, target_geo, dst_shape, "nearest")
            out_qa[band] = (np.asarray(gridded, dtype=np.uint16) | coverage).astype(np.uint16)
        return out_qa

    def _build_l1c_product(
        self,
        name: str,
        groups: Mapping[str, Mapping[str, npt.NDArray[Any]]],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        grid: Any,
        refinement: GcpRefinement,
        params: GeoreferenceParams,
    ) -> EOProduct:
        """Assemble the gridded L1C product with CRS + geolocation layers + QA."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": "default",
            },
            "processing_parameters": {
                "resolution": params.resolution,
                "crs_wkt": grid.geo.crs_wkt,
                "resampling": params.resampling,
                "use_gcp": params.use_gcp,
            },
            "geolocation": {
                "n_gcp": refinement.n_gcp,
                "rms_residual_px": refinement.rms_residual_px,
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product[_MEASUREMENTS] = EOGroup()
        product["quality"] = EOGroup()
        product["conditions"] = EOGroup()
        for rep_name, bands in groups.items():
            for band, data in bands.items():
                product[f"{_MEASUREMENTS}/{rep_name}/{band}"] = EOVariable(data=data, dims=_DIMS)
        for band, qa in qa_bands.items():
            product[f"{_MASK_GROUP}/{band}"] = EOVariable(data=qa, dims=_DIMS)
        product[f"{_GEOLOCATION}/x"] = EOVariable(data=grid.x, dims=("x",))
        product[f"{_GEOLOCATION}/y"] = EOVariable(data=grid.y, dims=("y",))
        product[f"{_GEOLOCATION}/spatial_ref"] = EOVariable(
            data=np.array(0, dtype=np.int32),
            attrs={"crs_wkt": grid.geo.crs_wkt, "GeoTransform": list(grid.geo.gdal_tuple)},
        )
        return product
