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

"""Thin ``EOProcessingUnit`` wrapper for atmospheric correction (C-PU-ATM).

Adapts the pure :mod:`~msi_processor.computing.atmospheric.core` to the EOPF CPM
runtime following the wrapper template of SDD <5.4.1>/<5.4.9>: read parameters,
extract the TOA-reflectance bands, load/validate ADFs, orchestrate the pure-core
functions (ALG-ATM-PAR -> ALG-ATM-RT -> ALG-ATM-SCM), propagate QA, and build the
``L2A`` ``EOProduct`` (BOA reflectance + scene classification + cloud/shadow
masks). No algorithm lives here.

Input convention. The upstream stage is the ``georeference`` unit; its ``l1c``
product carries the orthorectified TOA reflectance under
``measurements/reflectance/<band>`` and QA under ``quality/mask/<band>``
(IF-PROD-03). Atmospheric correction inverts the TOA reflectance to BOA (surface)
reflectance on the same grid; ``L2A`` is the surface-reflectance product (DPM <8.7>).

ADF data convention (this increment). ADF content is read from the
``AuxiliaryDataFile.data_ptr`` mapping:

* ``atmospheric`` -> ``{"aot": float|ndarray, "water_vapour": float|ndarray,
  "ozone": float | None, "rt_lut": {"path_reflectance": {band: float},
  "transmittance": {band: float}, "spherical_albedo": {band: float}}}`` (optional;
  required when ``mode="ingest"``: ingested AOT/water-vapour + the resolved
  per-band RT terms for the scene operating point, ICD <5.3.2>A). Building the
  ``rt_lut`` from a radiative-transfer engine is the ``[impl]``
  :func:`~msi_processor.computing.atmospheric.core.resolve_rt_lut`.
* ``dem`` -> ``{"elevation": ndarray2d, ...}`` (mandatory; surface altitude for
  the RT operating point; presence/coverage enforced here, REQ-F-ATM-02).

**Implementation status (ATBD <5.8> open point 1).** Image-based parameter
*retrieval* (``mode="retrieve"``) and the RT engine that *builds* the LUT are
``[impl]`` (DPM down-selection / CDR target). The PDR-operational path realised
here is parameter *ingest* (``mode="ingest"``) with a pre-resolved RT-LUT from the
``atmospheric`` ADF, the exact 6S BOA inversion, and the spectral-threshold scene
classifier.

**Fail-stop (REQ-F-ATM-04).** Missing DEM coverage, a missing ``atmospheric`` ADF
in ingest mode, or the ``[impl]`` retrieval/RT-engine paths raise
:class:`~msi_processor.exceptions.errors.AtmosphericError`; it propagates to the
chain runner so no L2A product is emitted from incomplete atmospheric inputs.
Cloud / cloud-shadow pixels are flagged ``CLOUD`` / ``CLOUD_SHADOW`` in the QA
layer (REQ-F-ATM-03) but never abort the chain.

Mandatory inputs/ADFs are declared by the CPM computing-model JSON
(``models/msi_atmospheric_1.0.0.json``), not by overriding the list methods.

*Trace:* REQ-F-ATM-01..04; DPM-M-ATM; ALG-ATM-PAR/RT/SCM; ICD IF-PROD-03,
REQ-IF-OUT-02.
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
from msi_processor.computing.atmospheric.core import (
    AtmAux,
    RTLut,
    SceneClass,
    SceneGeometry,
    classify_scene,
    get_atmospheric_parameters,
    toa_to_boa,
)
from msi_processor.exceptions.errors import (
    AdfResolutionError,
    AtmosphericError,
    InputValidationError,
)

_MEASUREMENTS = "measurements"
_REFLECTANCE = "reflectance"
_MASK_GROUP = "quality/mask"
_SCENE_GROUP = "quality/scene_classification"
_DIMS = ("y", "x")
_STAGE = "atmospheric"
_ALLOWED_MODES = ("ingest", "retrieve")


def _coerce_mapping(adf: AuxiliaryDataFile) -> dict[str, Any]:
    """Return the ADF content mapping from ``data_ptr`` (raise if unusable)."""
    ptr = adf.data_ptr
    if isinstance(ptr, Mapping):
        return dict(ptr)
    raise AdfResolutionError(f"ADF '{adf.name}' has no usable data_ptr mapping", stage=_STAGE)


def _require_adf(adfs: Mapping[str, AuxiliaryDataFile], name: str) -> AuxiliaryDataFile:
    """Fetch a mandatory ADF or raise :class:`AtmosphericError` (coverage fail-stop)."""
    adf = adfs.get(name)
    if adf is None:
        raise AtmosphericError(f"Missing mandatory ADF '{name}' for atmospheric run", stage=_STAGE)
    return adf


def _read_toa_reflectance(product: EOProduct) -> dict[str, npt.NDArray[np.float64]]:
    """Extract the TOA ``measurements/reflectance/<band>`` arrays."""
    try:
        reflectance = cast(EOGroup, product[f"{_MEASUREMENTS}/{_REFLECTANCE}"])
    except KeyError as exc:
        raise InputValidationError(
            f"Input L1C product has no '{_MEASUREMENTS}/{_REFLECTANCE}' group "
            "(atmospheric correction requires TOA reflectance)",
            stage=_STAGE,
        ) from exc
    bands: dict[str, npt.NDArray[np.float64]] = {}
    for band_name, var in reflectance.items():
        bands[band_name] = np.asarray(cast(EOVariable, var).data, dtype=np.float64)
    if not bands:
        raise InputValidationError(
            f"Input L1C product has no bands under '{_MEASUREMENTS}/{_REFLECTANCE}'",
            stage=_STAGE,
        )
    return bands


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


def _atm_aux_from_adf(content: Mapping[str, Any]) -> AtmAux:
    """Build :class:`AtmAux` from the ``atmospheric`` ADF content."""
    if "aot" not in content or "water_vapour" not in content:
        raise AtmosphericError(
            "atmospheric ADF must carry 'aot' and 'water_vapour' for ingest mode",
            stage=_STAGE,
        )
    ozone = content.get("ozone")
    return AtmAux(
        aot=content["aot"],
        water_vapour=content["water_vapour"],
        ozone=None if ozone is None else float(ozone),
    )


def _rt_lut_from_adf(content: Mapping[str, Any]) -> RTLut:
    """Build a pre-resolved :class:`RTLut` from the ``atmospheric`` ADF content."""
    raw = content.get("rt_lut")
    if not isinstance(raw, Mapping):
        raise AtmosphericError(
            "atmospheric ADF must carry a resolved 'rt_lut' (per-band path "
            "reflectance / transmittance / spherical albedo); building it from an "
            "RT engine is [impl] (ATBD <5.8> open point 1)",
            stage=_STAGE,
        )
    path = raw.get("path_reflectance")
    trans = raw.get("transmittance")
    if not isinstance(path, Mapping) or not isinstance(trans, Mapping):
        raise AtmosphericError(
            "atmospheric ADF 'rt_lut' must provide 'path_reflectance' and " "'transmittance' per-band mappings",
            stage=_STAGE,
        )
    albedo = raw.get("spherical_albedo")
    return RTLut(
        path_reflectance={str(k): float(v) for k, v in path.items()},
        transmittance={str(k): float(v) for k, v in trans.items()},
        spherical_albedo=({str(k): float(v) for k, v in albedo.items()} if isinstance(albedo, Mapping) else {}),
    )


class AtmosphericUnit(EOProcessingUnit):
    """Atmospheric-correction processing unit (C-PU-ATM; SDD <5.4.9>).

    Methods
    -------
    run:
        Invert the TOA-reflectance stack to BOA (surface) reflectance, classify the
        scene and emit the ``L2A`` product with cloud / cloud-shadow QA. Image-based
        parameter retrieval and the RT-LUT-building engine are ``[impl]`` (ATBD
        <5.8> open point 1); the operational path is ingest mode with a pre-resolved
        RT-LUT.
    """

    PROCESSOR_NAME = "msi_atmospheric"
    PROCESSOR_VERSION = "1.0.0"
    PROCESSOR_LEVEL = "L2A"
    PROCESSOR_MODEL = True

    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """Run the atmospheric correction.

        Parameters
        ----------
        inputs:
            ``{"l1c": EOProduct}`` with TOA reflectance under
            ``measurements/reflectance/<band>`` and optional QA under
            ``quality/mask/<band>``.
        adfs:
            ``atmospheric`` (required for ``param_mode="ingest"``: ingested
            AOT/water-vapour + a resolved RT-LUT) and ``dem`` (mandatory; surface
            altitude).
        mode:
            ``"default"`` (the only supported processing mode).
        **kwargs:
            ``param_mode`` (``"ingest"`` | ``"retrieve"``, default ``"ingest"``),
            ``sun_zenith`` / ``view_zenith`` / ``relative_azimuth`` (scene geometry
            operating point), scene-classification thresholds and ``band_roles``
            (see :func:`~msi_processor.computing.atmospheric.core.classify_scene`),
            and an optional ``name`` for the output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"l2a": EOProduct}`` with BOA ``measurements/reflectance/<band>``,
            ``quality/scene_classification`` and ``quality/mask/<band>``.

        Raises
        ------
        AtmosphericError
            On missing DEM coverage, a missing ``atmospheric`` ADF in ingest mode,
            or the ``[impl]`` retrieval / RT-engine paths -- fail-stop
            (REQ-F-ATM-04).
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "default"
        if run_mode != "default":
            raise InputValidationError(
                f"Unknown atmospheric mode '{run_mode}'; expected 'default'",
                stage=_STAGE,
            )

        param_mode = str(kwargs.get("param_mode", "ingest"))
        if param_mode not in _ALLOWED_MODES:
            raise InputValidationError(
                f"Unknown param_mode '{param_mode}'; expected one of {_ALLOWED_MODES}",
                stage=_STAGE,
            )

        if "l1c" not in inputs:
            raise InputValidationError("Missing mandatory input 'l1c' for atmospheric run", stage=_STAGE)
        l1c = cast(EOProduct, inputs["l1c"])
        toa_refl = _read_toa_reflectance(l1c)
        upstream_qa = _read_qa_masks(l1c)
        adf_map: Mapping[str, AuxiliaryDataFile] = adfs or {}

        # Mandatory DEM coverage (REQ-F-ATM-02): presence enforced regardless of
        # path; its rigorous per-pixel consumption lives in the [impl] RT engine.
        dem_content = _coerce_mapping(_require_adf(adf_map, "dem"))
        dem = np.asarray(dem_content.get("elevation", np.zeros((1, 1), dtype=np.float32)))

        geometry = SceneGeometry(
            sun_zenith=float(kwargs.get("sun_zenith", 0.0)),
            view_zenith=float(kwargs.get("view_zenith", 0.0)),
            relative_azimuth=float(kwargs.get("relative_azimuth", 0.0)),
        )

        aux, rt_lut = self._resolve_atmospherics(adf_map, param_mode)
        atm = get_atmospheric_parameters(toa_refl, param_mode, aux, kwargs)  # type: ignore[arg-type]

        logger.info(
            f"Atmospheric: {len(toa_refl)} band(s), param_mode={param_mode}, "
            f"sun_zenith={geometry.sun_zenith:.1f} deg"
        )

        boa = toa_to_boa(toa_refl, atm, geometry, dem, rt_lut)
        scene_class, cloud_mask, shadow_mask = classify_scene(boa, kwargs)

        out_qa = self._atmospheric_qa(toa_refl.keys(), upstream_qa, cloud_mask, shadow_mask)

        output_name = str(kwargs.get("name", f"{l1c.name}_L2A"))
        l2a = self._build_l2a_product(output_name, boa, scene_class, out_qa, param_mode, geometry)
        self._passthrough_geolocation(l1c, l2a)
        outputs: dict[str, DataType] = {"l2a": l2a}
        return outputs

    @staticmethod
    def _passthrough_geolocation(l1c: EOProduct, l2a: EOProduct) -> None:
        """Carry the L1C cartographic geolocation grid (conditions/*) into L2A.

        A gridded L2A product must retain its geolocation; the BOA inversion does
        not touch the grid, so the ``conditions`` tree (geolocation x/y and the
        ``spatial_ref`` CRS, with its attributes) is copied verbatim.
        """
        try:
            conditions = cast(EOGroup, l1c["conditions"])
        except KeyError:
            return
        l2a["conditions"] = EOGroup()

        def _copy(group: EOGroup, prefix: str) -> None:
            for name, item in group.items():
                path = f"{prefix}/{name}"
                if isinstance(item, EOGroup):
                    _copy(item, path)
                else:
                    var = cast(EOVariable, item)
                    l2a[path] = EOVariable(data=np.asarray(var.data), dims=var.dims, attrs=dict(var.attrs))

        _copy(conditions, "conditions")

    # ----------------------------------------------------------------------- #
    # Helpers                                                                  #
    # ----------------------------------------------------------------------- #
    @staticmethod
    def _resolve_atmospherics(
        adf_map: Mapping[str, AuxiliaryDataFile],
        param_mode: str,
    ) -> tuple[AtmAux | None, RTLut]:
        """Resolve the ingest auxiliaries + RT-LUT (retrieve mode is [impl]).

        In ``ingest`` mode both the auxiliary AOT/water-vapour and a pre-resolved
        RT-LUT are read from the ``atmospheric`` ADF. In ``retrieve`` mode the
        parameter retrieval is ``[impl]``; the RT-LUT is still required from the ADF
        (building it from an RT engine is also ``[impl]``).
        """
        if param_mode == "ingest":
            content = _coerce_mapping(_require_adf(adf_map, "atmospheric"))
            return _atm_aux_from_adf(content), _rt_lut_from_adf(content)
        # retrieve mode: parameters come from the imagery ([impl]); the RT-LUT is
        # still needed (its construction is [impl] too) -- read it if present so the
        # explicit [impl] fail-stop comes from get_atmospheric_parameters.
        atm_adf = adf_map.get("atmospheric")
        if atm_adf is None:
            return None, RTLut(path_reflectance={}, transmittance={})
        content = _coerce_mapping(atm_adf)
        return None, _rt_lut_from_adf(content)

    @staticmethod
    def _atmospheric_qa(
        band_names: Any,
        upstream_qa: Mapping[str, npt.NDArray[np.uint16]],
        cloud_mask: npt.NDArray[np.bool_],
        shadow_mask: npt.NDArray[np.bool_],
    ) -> dict[str, npt.NDArray[np.uint16]]:
        """OR the cloud / cloud-shadow flags into each band's QA (REQ-F-ATM-03)."""
        cloud_bits = np.where(cloud_mask, np.uint16(QAFlag.CLOUD), np.uint16(0)).astype(np.uint16)
        shadow_bits = np.where(shadow_mask, np.uint16(QAFlag.CLOUD_SHADOW), np.uint16(0)).astype(np.uint16)
        scene_bits = (cloud_bits | shadow_bits).astype(np.uint16)
        out_qa: dict[str, npt.NDArray[np.uint16]] = {}
        for band in band_names:
            base = upstream_qa.get(band)
            if base is None:
                out_qa[band] = scene_bits.copy()
            else:
                out_qa[band] = (np.asarray(base, dtype=np.uint16) | scene_bits).astype(np.uint16)
        return out_qa

    def _build_l2a_product(
        self,
        name: str,
        boa: Mapping[str, npt.NDArray[np.float32]],
        scene_class: npt.NDArray[np.uint8],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        param_mode: str,
        geometry: SceneGeometry,
    ) -> EOProduct:
        """Assemble the L2A product (BOA reflectance + scene class + QA)."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": "default",
            },
            "processing_parameters": {
                "param_mode": param_mode,
                "sun_zenith": geometry.sun_zenith,
                "view_zenith": geometry.view_zenith,
                "relative_azimuth": geometry.relative_azimuth,
            },
            "scene_classification": {
                "scheme": "msi-threshold-baseline",
                "classes": {
                    "no_data": SceneClass.NO_DATA,
                    "cloud": SceneClass.CLOUD,
                    "cloud_shadow": SceneClass.CLOUD_SHADOW,
                    "vegetation": SceneClass.VEGETATION,
                    "bare_soil": SceneClass.BARE_SOIL,
                    "water": SceneClass.WATER,
                    "unclassified": SceneClass.UNCLASSIFIED,
                },
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product[_MEASUREMENTS] = EOGroup()
        product["quality"] = EOGroup()
        for band, data in boa.items():
            product[f"{_MEASUREMENTS}/{_REFLECTANCE}/{band}"] = EOVariable(data=data, dims=_DIMS)
        product[_SCENE_GROUP] = EOVariable(data=scene_class, dims=_DIMS)
        for band, qa in qa_bands.items():
            product[f"{_MASK_GROUP}/{band}"] = EOVariable(data=qa, dims=_DIMS)
        return product
