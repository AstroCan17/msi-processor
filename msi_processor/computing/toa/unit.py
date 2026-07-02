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

"""Thin ``EOProcessingUnit`` wrapper for TOA radiance/reflectance (C-PU-TOA).

Adapts the pure :mod:`~msi_processor.computing.toa.core` to the EOPF CPM
runtime following the wrapper template of SDD <5.4.1>/<5.4.5>: read parameters,
extract input bands, load/validate ADFs, call the core per band, propagate QA,
and build the output ``L1B`` ``EOProduct``. No algorithm lives here.

Mandatory inputs/ADFs are declared by the CPM computing-model JSON
(``models/msi_toa_1.0.0.json``), not by overriding the list methods.

Input convention (this increment). The upstream stage is the mandatory
``enhancement`` unit; since it is not yet implemented, this unit accepts the
corrected/enhanced bands product under input key ``enh`` carrying corrected DN
under ``measurements/detector/<band>`` and QA under ``quality/mask/<band>``
(IF-PROD-02) -- exactly the shape the ``radiometric`` unit emits, which will
feed ``enhancement`` once it lands.

ADF data convention (this increment). The unit reads ADF content from the
``AuxiliaryDataFile.data_ptr`` mapping (the CPM ``data_ptr`` is documented as
holding the opened data):

* ``radiometric`` -> ``{"gain": {band: float|ndarray1d}, "offset": {band: ...}}``
  (mandatory; absolute radiometric coefficients, ICD <5.3.2>A)
* ``spectral``    -> ``{"esun": {band: float}}`` (required only when
  ``emit_reflectance`` is set)

Illumination geometry (solar zenith, Earth-Sun distance) is taken from the run
kwargs sourced from ``L0c`` telemetry / ADF per the ICD (the GPL ``pyorbital``
TLE fetch is dropped, SRF SRF-RU-HER-TOA); the proper solar ephemeris
:func:`~msi_processor.computing.toa.core.solar_geometry` is available for the
caller and will be wired to telemetry plumbing once it lands.

*Trace:* REQ-F-TOA-01..03; DPM-M-TOA; ALG-TOA-RAD/REF; ICD IF-PROD-03.
"""

from __future__ import annotations

import math
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

from msi_processor.computing.toa.core import (
    TOAParams,
    dn_to_radiance,
    earth_sun_distance,
    flag_radiance,
    radiance_to_reflectance,
)
from msi_processor.exceptions.errors import AdfResolutionError, InputValidationError

_DETECTOR_GROUP = "measurements/detector"
_RADIANCE_GROUP = "measurements/radiance"
_REFLECTANCE_GROUP = "measurements/reflectance"
_MASK_GROUP = "quality/mask"
_DIMS = ("line", "detector")


def _coerce_mapping(adf: AuxiliaryDataFile) -> dict[str, Any]:
    """Return the ADF content mapping from ``data_ptr`` (raise if unusable)."""
    ptr = adf.data_ptr
    if isinstance(ptr, Mapping):
        return dict(ptr)
    raise AdfResolutionError(f"ADF '{adf.name}' has no usable data_ptr mapping", stage="toa")


def _require_adf(adfs: Mapping[str, AuxiliaryDataFile], name: str) -> AuxiliaryDataFile:
    """Fetch a mandatory ADF or raise :class:`AdfResolutionError`."""
    adf = adfs.get(name)
    if adf is None:
        raise AdfResolutionError(f"Missing mandatory ADF '{name}' for TOA run", stage="toa")
    return adf


def _read_detector_bands(product: EOProduct) -> dict[str, npt.NDArray[Any]]:
    """Extract ``measurements/detector/<band>`` arrays from the enh product."""
    try:
        group = cast(EOGroup, product[_DETECTOR_GROUP])
    except KeyError as exc:
        raise InputValidationError(
            f"Input enhancement product has no '{_DETECTOR_GROUP}' group",
            stage="toa",
        ) from exc
    bands: dict[str, npt.NDArray[Any]] = {}
    for name, item in group.items():
        bands[name] = np.asarray(cast(EOVariable, item).data)
    if not bands:
        raise InputValidationError(
            f"Input enhancement product has no bands under '{_DETECTOR_GROUP}'",
            stage="toa",
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


class ToaUnit(EOProcessingUnit):
    """TOA radiance/reflectance processing unit (C-PU-TOA; SDD <5.4.5>).

    Methods
    -------
    run:
        Convert corrected DN to TOA radiance (mandatory) and optional TOA
        reflectance, and emit the ``L1B`` product.
    """

    PROCESSOR_NAME = "msi_toa"
    PROCESSOR_VERSION = "1.0.0"
    PROCESSOR_LEVEL = "L1B"
    PROCESSOR_MODEL = True

    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """Run the TOA conversion.

        Parameters
        ----------
        inputs:
            ``{"enh": EOProduct}`` with bands under ``measurements/detector``
            and optional QA under ``quality/mask``.
        adfs:
            ``radiometric`` (mandatory; gain/offset); ``spectral`` (required
            only when ``emit_reflectance`` is set; per-band ESUN).
        mode:
            ``"nominal"`` (the only supported mode).
        **kwargs:
            :class:`TOAParams` fields (``emit_reflectance``, ``fill_value``);
            illumination geometry for reflectance (``sun_zenith_rad`` or
            ``sun_zenith_deg``; ``earth_sun_distance_au`` or ``day_of_year``);
            optional ``name`` for the output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"l1b": EOProduct}`` with ``measurements/radiance/<band>``
            (+ ``measurements/reflectance/<band>`` when requested) and
            ``quality/mask/<band>``.
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "nominal"
        if run_mode != "nominal":
            raise InputValidationError(
                f"Unknown TOA mode '{run_mode}'; expected 'nominal'",
                stage="toa",
            )

        params = self._build_params(kwargs)
        adf_map: Mapping[str, AuxiliaryDataFile] = adfs or {}

        if "enh" not in inputs:
            raise InputValidationError("Missing mandatory input 'enh' for TOA run", stage="toa")
        enh = cast(EOProduct, inputs["enh"])
        bands = _read_detector_bands(enh)
        upstream_qa = _read_qa_masks(enh)
        logger.info(f"TOA conversion: {len(bands)} band(s), emit_reflectance={params.emit_reflectance}")

        rad_data = _coerce_mapping(_require_adf(adf_map, "radiometric"))
        gain_map = dict(rad_data.get("gain", {}))
        offset_map = dict(rad_data.get("offset", {}))
        if not gain_map or not offset_map:
            raise AdfResolutionError(
                "radiometric ADF must provide 'gain' and 'offset' per band",
                stage="toa",
            )

        esun_map: Mapping[str, Any] = {}
        sun_zenith_rad = 0.0
        earth_sun_dist_au = 1.0
        if params.emit_reflectance:
            esun_map = self._resolve_esun(adf_map)
            sun_zenith_rad, earth_sun_dist_au = self._resolve_geometry(kwargs)

        radiance_bands: dict[str, npt.NDArray[np.float32]] = {}
        reflectance_bands: dict[str, npt.NDArray[np.float32]] = {}
        qa_bands: dict[str, npt.NDArray[np.uint16]] = {}
        for band, dn in bands.items():
            radiance, qa = self._process_band(band, dn, gain_map, offset_map, params)
            if band in upstream_qa:
                qa = qa | upstream_qa[band].astype(np.uint16)
            radiance_bands[band] = radiance
            qa_bands[band] = qa
            if params.emit_reflectance:
                if band not in esun_map:
                    raise AdfResolutionError(
                        f"spectral ADF has no ESUN for band '{band}'",
                        stage="toa",
                    )
                reflectance_bands[band] = radiance_to_reflectance(
                    radiance, float(esun_map[band]), sun_zenith_rad, earth_sun_dist_au
                )

        output_name = str(kwargs.get("name", f"{enh.name}_L1B"))
        l1b = self._build_l1b_product(output_name, radiance_bands, reflectance_bands, qa_bands, params)
        outputs: dict[str, DataType] = {"l1b": l1b}
        return outputs

    @staticmethod
    def _build_params(kwargs: Mapping[str, Any]) -> TOAParams:
        """Build :class:`TOAParams` from the run kwargs (with defaults)."""
        return TOAParams(
            emit_reflectance=bool(kwargs.get("emit_reflectance", False)),
            fill_value=kwargs.get("fill_value"),
        )

    @staticmethod
    def _resolve_esun(adfs: Mapping[str, AuxiliaryDataFile]) -> dict[str, Any]:
        """Resolve per-band ESUN from the spectral ADF (reflectance path)."""
        spectral_adf = adfs.get("spectral")
        if spectral_adf is None:
            raise AdfResolutionError(
                "Reflectance requested but mandatory 'spectral' ADF (ESUN) is missing",
                stage="toa",
            )
        esun_map = dict(_coerce_mapping(spectral_adf).get("esun", {}))
        if not esun_map:
            raise AdfResolutionError("spectral ADF must provide 'esun' per band", stage="toa")
        return esun_map

    @staticmethod
    def _resolve_geometry(kwargs: Mapping[str, Any]) -> tuple[float, float]:
        """Resolve (sun_zenith_rad, earth_sun_distance_au) from telemetry kwargs."""
        if kwargs.get("earth_sun_distance_au") is not None:
            distance = float(kwargs["earth_sun_distance_au"])
        elif kwargs.get("day_of_year") is not None:
            distance = earth_sun_distance(int(kwargs["day_of_year"]))
        else:
            raise InputValidationError(
                "Reflectance requires 'earth_sun_distance_au' or 'day_of_year'",
                stage="toa",
            )

        if kwargs.get("sun_zenith_rad") is not None:
            zenith = float(kwargs["sun_zenith_rad"])
        elif kwargs.get("sun_zenith_deg") is not None:
            zenith = math.radians(float(kwargs["sun_zenith_deg"]))
        else:
            raise InputValidationError(
                "Reflectance requires 'sun_zenith_rad' or 'sun_zenith_deg'",
                stage="toa",
            )
        return zenith, distance

    @staticmethod
    def _process_band(
        band: str,
        dn: npt.NDArray[Any],
        gain_map: Mapping[str, Any],
        offset_map: Mapping[str, Any],
        params: TOAParams,
    ) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.uint16]]:
        """Apply the DN->radiance pipeline (+ flagging) to a single band."""
        if band not in gain_map or band not in offset_map:
            raise AdfResolutionError(
                f"radiometric ADF has no gain/offset for band '{band}'",
                stage="toa",
            )
        radiance = dn_to_radiance(dn, gain_map[band], offset_map[band])
        return flag_radiance(radiance, params)

    def _build_l1b_product(
        self,
        name: str,
        radiance_bands: Mapping[str, npt.NDArray[np.float32]],
        reflectance_bands: Mapping[str, npt.NDArray[np.float32]],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        params: TOAParams,
    ) -> EOProduct:
        """Assemble the L1B radiance(/reflectance) + QA output product."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": "nominal",
            },
            "processing_parameters": {
                "emit_reflectance": params.emit_reflectance,
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product["measurements"] = EOGroup()
        product["quality"] = EOGroup()
        for band, radiance in radiance_bands.items():
            product[f"{_RADIANCE_GROUP}/{band}"] = EOVariable(data=radiance, dims=_DIMS)
            product[f"{_MASK_GROUP}/{band}"] = EOVariable(data=qa_bands[band], dims=_DIMS)
        for band, reflectance in reflectance_bands.items():
            product[f"{_REFLECTANCE_GROUP}/{band}"] = EOVariable(data=reflectance, dims=_DIMS)
        return product
