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

"""Thin ``EOProcessingUnit`` wrapper for radiometric correction (C-PU-RAD).

Adapts the pure :mod:`~msi_processor.computing.radiometric.core` to the EOPF
CPM runtime following the wrapper template of SDD <5.4.1>: read parameters,
extract input bands, load/validate ADFs, call the core per band, attach QA
flags, and build the output ``EOProduct``. No algorithm lives here.

Mandatory inputs/ADFs are declared by the CPM computing-model JSON
(``models/msi_radiometric_1.0.0.json``), not by overriding the list methods.

ADF data convention (this increment). The unit reads ADF content from the
``AuxiliaryDataFile.data_ptr`` mapping (the CPM ``data_ptr`` is documented as
holding the opened data):

* ``dark``      -> ``{"dark_offset": {band: float}, "frame": {band: ndarray2d}}``
  (both keys optional; ``dark_offset`` defaults to 0.0, ``frame`` is only
  needed for FFT dark removal or calibration-mode NUC derivation)
* ``nuc``       -> ``{"gain": {band: ndarray1d}, "offset": {band: ndarray1d}}``
  (nominal mode)
* ``flatfield`` -> ``{band: ndarray2d}`` (calibration mode)
* ``badpixel``  -> ``{band: ndarray1d[bool]}`` (optional)

*Trace:* REQ-F-RAD-01..05; DPM-M-RAD; ALG-RAD-*; ICD <5.3.4>A.
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
from msi_processor.computing.radiometric.core import (
    RadiometricParams,
    apply_nuc,
    detect_bad_pixels,
    estimate_nuc,
    flag_saturation,
    remove_dark_fft,
    replace_bad_pixels,
)
from msi_processor.exceptions.errors import (
    AdfResolutionError,
    InputValidationError,
    RadiometricError,
)

_DETECTOR_GROUP = "measurements/detector"
_MASK_GROUP = "quality/mask"
_DIMS = ("line", "detector")
_VALID_MODES = ("nominal", "calibration")


def _coerce_mapping(adf: AuxiliaryDataFile) -> dict[str, Any]:
    """Return the ADF content mapping from ``data_ptr`` (raise if unusable)."""
    ptr = adf.data_ptr
    if isinstance(ptr, Mapping):
        return dict(ptr)
    raise AdfResolutionError(
        f"ADF '{adf.name}' has no usable data_ptr mapping",
        stage="radiometric",
    )


def _require_adf(adfs: Mapping[str, AuxiliaryDataFile], name: str, mode: str) -> AuxiliaryDataFile:
    """Fetch a mandatory ADF or raise :class:`AdfResolutionError`."""
    adf = adfs.get(name)
    if adf is None:
        raise AdfResolutionError(
            f"Missing mandatory ADF '{name}' for radiometric mode '{mode}'",
            stage="radiometric",
        )
    return adf


def _read_detector_bands(product: EOProduct) -> dict[str, npt.NDArray[Any]]:
    """Extract ``measurements/detector/<band>`` arrays from an L1A product."""
    try:
        group = cast(EOGroup, product[_DETECTOR_GROUP])
    except KeyError as exc:
        raise InputValidationError(
            f"Input L1A product has no '{_DETECTOR_GROUP}' group",
            stage="radiometric",
        ) from exc
    bands: dict[str, npt.NDArray[Any]] = {}
    for name, item in group.items():
        bands[name] = np.asarray(cast(EOVariable, item).data)
    if not bands:
        raise InputValidationError(
            f"Input L1A product has no bands under '{_DETECTOR_GROUP}'",
            stage="radiometric",
        )
    return bands


class RadiometricUnit(EOProcessingUnit):
    """Radiometric correction processing unit (C-PU-RAD; SDD <5.4.3>).

    Methods
    -------
    run:
        Execute dark/NUC/BPR/saturation correction over the input bands.
    """

    PROCESSOR_NAME = "msi_radiometric"
    PROCESSOR_VERSION = "1.0.0"
    PROCESSOR_LEVEL = "L1A"
    PROCESSOR_MODEL = True

    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """Run the radiometric correction.

        Parameters
        ----------
        inputs:
            ``{"l1a": EOProduct}`` with bands under ``measurements/detector``.
        adfs:
            ``dark`` (mandatory); ``nuc`` (nominal mode) or ``flatfield``
            (calibration mode); ``badpixel`` (optional).
        mode:
            ``"nominal"`` (read NUC from ADF) or ``"calibration"`` (derive
            NUC from dark+flat and emit a ``nuc`` product, REQ-F-RAD-05).
        **kwargs:
            :class:`RadiometricParams` fields plus optional ``name`` for the
            output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"rad": EOProduct}`` (corrected DN + QA); additionally
            ``{"nuc": EOProduct}`` in calibration mode.
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "nominal"
        if run_mode not in _VALID_MODES:
            raise InputValidationError(
                f"Unknown radiometric mode '{run_mode}'; expected one of {_VALID_MODES}",
                stage="radiometric",
            )

        params = self._build_params(kwargs)
        adf_map: Mapping[str, AuxiliaryDataFile] = adfs or {}

        if "l1a" not in inputs:
            raise InputValidationError(
                "Missing mandatory input 'l1a' for radiometric run",
                stage="radiometric",
            )
        l1a = cast(EOProduct, inputs["l1a"])
        bands = _read_detector_bands(l1a)
        logger.info(f"Radiometric correction: {len(bands)} band(s), mode={run_mode}")

        dark_data = _coerce_mapping(_require_adf(adf_map, "dark", run_mode))
        dark_offsets: Mapping[str, Any] = dark_data.get("dark_offset", {})
        dark_frames: Mapping[str, Any] = dark_data.get("frame", {})

        badpixel_adf = adf_map.get("badpixel")
        bpm_map: Mapping[str, Any] = _coerce_mapping(badpixel_adf) if badpixel_adf is not None else {}

        gain_map, offset_map = self._resolve_nuc(adf_map, run_mode, bands, dark_frames)

        corrected_bands: dict[str, npt.NDArray[np.float32]] = {}
        qa_bands: dict[str, npt.NDArray[np.uint16]] = {}
        for band, raw in bands.items():
            corrected_bands[band], qa_bands[band] = self._process_band(
                band, raw, gain_map, offset_map, dark_offsets, dark_frames, bpm_map, params
            )

        output_name = str(kwargs.get("name", f"{l1a.name}_RAD"))
        rad_product = self._build_rad_product(output_name, corrected_bands, qa_bands, params, run_mode)
        outputs: dict[str, DataType] = {"rad": rad_product}
        if run_mode == "calibration":
            outputs["nuc"] = self._build_nuc_product(f"{output_name}_NUC", gain_map, offset_map)
        return outputs

    @staticmethod
    def _build_params(kwargs: Mapping[str, Any]) -> RadiometricParams:
        """Build :class:`RadiometricParams` from the run kwargs (with defaults)."""
        return RadiometricParams(
            bit_depth=int(kwargs.get("bit_depth", 12)),
            g_min=kwargs.get("g_min"),
            g_max=kwargs.get("g_max"),
            saturation=kwargs.get("saturation"),
            fill_value=kwargs.get("fill_value"),
            remove_dark_fft=bool(kwargs.get("remove_dark_fft", False)),
        )

    def _resolve_nuc(
        self,
        adfs: Mapping[str, AuxiliaryDataFile],
        mode: str,
        bands: Mapping[str, npt.NDArray[Any]],
        dark_frames: Mapping[str, Any],
    ) -> tuple[dict[str, npt.NDArray[Any]], dict[str, npt.NDArray[Any]]]:
        """Resolve per-band gain/offset: read (nominal) or derive (calibration)."""
        if mode == "nominal":
            nuc_data = _coerce_mapping(_require_adf(adfs, "nuc", mode))
            gain_map = dict(nuc_data.get("gain", {}))
            offset_map = dict(nuc_data.get("offset", {}))
            if not gain_map or not offset_map:
                raise AdfResolutionError(
                    "NUC ADF must provide 'gain' and 'offset' per band",
                    stage="radiometric",
                )
            return gain_map, offset_map

        flat_data = _coerce_mapping(_require_adf(adfs, "flatfield", mode))
        gain_map = {}
        offset_map = {}
        for band in bands:
            if band not in dark_frames or band not in flat_data:
                raise AdfResolutionError(
                    f"Calibration mode requires dark and flat frames for band '{band}'",
                    stage="radiometric",
                )
            gain, offset = estimate_nuc(dark_frames[band], flat_data[band])
            gain_map[band] = gain
            offset_map[band] = offset
        return gain_map, offset_map

    @staticmethod
    def _process_band(
        band: str,
        raw: npt.NDArray[Any],
        gain_map: Mapping[str, npt.NDArray[Any]],
        offset_map: Mapping[str, npt.NDArray[Any]],
        dark_offsets: Mapping[str, Any],
        dark_frames: Mapping[str, Any],
        bpm_map: Mapping[str, Any],
        params: RadiometricParams,
    ) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.uint16]]:
        """Apply the full radiometric pipeline to a single band."""
        if band not in gain_map or band not in offset_map:
            raise RadiometricError(
                f"No NUC gain/offset available for band '{band}'",
                stage="radiometric",
            )
        dn = np.asarray(raw, dtype=np.float32)
        if params.remove_dark_fft and band in dark_frames:
            dn = remove_dark_fft(dn, np.asarray(dark_frames[band], dtype=np.float32))

        gain = np.asarray(gain_map[band], dtype=np.float32)
        offset = np.asarray(offset_map[band], dtype=np.float32)
        dark_offset = float(dark_offsets.get(band, 0.0))

        corrected = apply_nuc(dn, gain, offset, dark_offset)
        bpm = np.asarray(bpm_map[band], dtype=bool) if band in bpm_map else None
        bad = detect_bad_pixels(gain, params, bpm)
        corrected = replace_bad_pixels(corrected, bad)
        clipped, qa = flag_saturation(corrected, params)
        if bad.any():
            qa[:, bad] |= np.uint16(QAFlag.DEFECTIVE)
        return clipped.astype(np.uint16), qa

    def _build_rad_product(
        self,
        name: str,
        corrected_bands: Mapping[str, npt.NDArray[np.float32]],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        params: RadiometricParams,
        mode: str,
    ) -> EOProduct:
        """Assemble the corrected-DN + QA output product (no coefficients)."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": mode,
            },
            "processing_parameters": {
                "bit_depth": params.bit_depth,
                "remove_dark_fft": params.remove_dark_fft,
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product["measurements"] = EOGroup()
        product["quality"] = EOGroup()
        for band, data in corrected_bands.items():
            product[f"{_DETECTOR_GROUP}/{band}"] = EOVariable(data=data, dims=_DIMS)
            product[f"{_MASK_GROUP}/{band}"] = EOVariable(data=qa_bands[band], dims=_DIMS)
        return product

    @staticmethod
    def _build_nuc_product(
        name: str,
        gain_map: Mapping[str, npt.NDArray[Any]],
        offset_map: Mapping[str, npt.NDArray[Any]],
    ) -> EOProduct:
        """Assemble the derived NUC calibration product (calibration mode)."""
        product = EOProduct(name)
        product["gain"] = EOGroup()
        product["offset"] = EOGroup()
        for band, gain in gain_map.items():
            product[f"gain/{band}"] = EOVariable(data=np.asarray(gain, dtype=np.float32), dims=("detector",))
        for band, offset in offset_map.items():
            product[f"offset/{band}"] = EOVariable(data=np.asarray(offset, dtype=np.float32), dims=("detector",))
        return product
