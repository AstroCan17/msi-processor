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

"""Thin ``EOProcessingUnit`` wrapper for image-quality enhancement (C-PU-ENH).

Adapts the pure :mod:`~msi_processor.computing.enhancement.core` to the EOPF
CPM runtime following the wrapper template of SDD <5.4.1>/<5.4.4>: read
parameters, extract input bands, load/validate ADFs, call the core per band,
propagate QA, and build the output ``enh`` ``EOProduct``. No algorithm lives
here.

The enhancement **stage always runs** (REQ-F-ENH-03): the mandatory MTF
compensation (:func:`~msi_processor.computing.enhancement.core.mtf_compensate`)
is applied to every band, optionally preceded by the profile-configurable
denoise sub-step. The denoise sub-step is disabled by selecting
``denoise_method="none"``; the stage still executes because MTFC is mandatory.

Mandatory inputs/ADFs are declared by the CPM computing-model JSON
(``models/msi_enhancement_1.0.0.json``), not by overriding the list methods.

Input convention. The upstream stage is the mandatory ``radiometric`` unit; its
``rad`` product carries corrected DN under ``measurements/detector/<band>`` and
QA under ``quality/mask/<band>`` (IF-PROD-02). The ``enh`` output keeps the same
shape so it can feed the downstream ``toa`` unit unchanged.

ADF data convention (this increment). The unit reads ADF content from the
``AuxiliaryDataFile.data_ptr`` mapping (the CPM ``data_ptr`` is documented as
holding the opened data):

* ``psf``  -> ``{"kernel": {band: ndarray2d}}`` (mandatory; the per-band
  PSF-derived deconvolution kernel for MTFC, ATBD <5.5>). **Deviation note:**
  the SDD <5.4.4> computing-model JSON sketch lists only the optional ``dark``
  ADF, but MTFC is mandatory and consumes a PSF/MTF kernel, so the kernel ADF is
  declared mandatory here (per the C-PU-ENH task brief). Private kernel content
  is supplied via this ADF and never embedded (REQ-AD-01).
* ``dark`` -> ``{"frame": {band: ndarray2d}}`` (optional; required only when
  ``denoise_method="fft_dark"``), matching the radiometric ``dark`` ADF shape.

*Trace:* REQ-F-ENH-01..03; DPM-M-ENH; ALG-ENH-*; ICD IF-PROD-02.
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

from msi_processor.computing.enhancement.core import (
    DenoiseMethod,
    EnhancementParams,
    denoise,
    flag_enhanced,
    mtf_compensate,
)
from msi_processor.exceptions.errors import AdfResolutionError, InputValidationError

_DETECTOR_GROUP = "measurements/detector"
_MASK_GROUP = "quality/mask"
_DIMS = ("line", "detector")
_ALLOWED_DENOISE: tuple[DenoiseMethod, ...] = (
    "none",
    "butterworth",
    "wavelet",
    "pca",
    "moving_average",
    "gaussian",
    "fft_dark",
)


def _coerce_mapping(adf: AuxiliaryDataFile) -> dict[str, Any]:
    """Return the ADF content mapping from ``data_ptr`` (raise if unusable)."""
    ptr = adf.data_ptr
    if isinstance(ptr, Mapping):
        return dict(ptr)
    raise AdfResolutionError(f"ADF '{adf.name}' has no usable data_ptr mapping", stage="enhancement")


def _require_adf(adfs: Mapping[str, AuxiliaryDataFile], name: str) -> AuxiliaryDataFile:
    """Fetch a mandatory ADF or raise :class:`AdfResolutionError`."""
    adf = adfs.get(name)
    if adf is None:
        raise AdfResolutionError(f"Missing mandatory ADF '{name}' for enhancement run", stage="enhancement")
    return adf


def _read_detector_bands(product: EOProduct) -> dict[str, npt.NDArray[Any]]:
    """Extract ``measurements/detector/<band>`` arrays from the rad product."""
    try:
        group = cast(EOGroup, product[_DETECTOR_GROUP])
    except KeyError as exc:
        raise InputValidationError(
            f"Input radiometric product has no '{_DETECTOR_GROUP}' group",
            stage="enhancement",
        ) from exc
    bands: dict[str, npt.NDArray[Any]] = {}
    for name, item in group.items():
        bands[name] = np.asarray(cast(EOVariable, item).data)
    if not bands:
        raise InputValidationError(
            f"Input radiometric product has no bands under '{_DETECTOR_GROUP}'",
            stage="enhancement",
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


class EnhancementUnit(EOProcessingUnit):
    """Image-quality-enhancement processing unit (C-PU-ENH; SDD <5.4.4>).

    Methods
    -------
    run:
        Apply the optional denoise sub-step and the mandatory MTF compensation
        to every band and emit the ``enh`` product.
    """

    PROCESSOR_NAME = "msi_enhancement"
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
        """Run the image-quality enhancement.

        Parameters
        ----------
        inputs:
            ``{"rad": EOProduct}`` with bands under ``measurements/detector``
            and optional QA under ``quality/mask``.
        adfs:
            ``psf`` (mandatory; per-band MTFC deconvolution kernel); ``dark``
            (optional; required only for ``denoise_method="fft_dark"``).
        mode:
            ``"default"`` (the only supported mode); the stage always runs.
        **kwargs:
            :class:`EnhancementParams` fields (``denoise_method``,
            ``denoise_params``, ``bit_depth``, ``fill_value``,
            ``mtfc_regularization``); optional ``name`` for the output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"enh": EOProduct}`` with the MTFC-restored (optionally denoised)
            DN under ``measurements/detector/<band>`` and the propagated QA under
            ``quality/mask/<band>``.
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "default"
        if run_mode != "default":
            raise InputValidationError(
                f"Unknown enhancement mode '{run_mode}'; expected 'default'",
                stage="enhancement",
            )

        params = self._build_params(kwargs)
        adf_map: Mapping[str, AuxiliaryDataFile] = adfs or {}

        if "rad" not in inputs:
            raise InputValidationError("Missing mandatory input 'rad' for enhancement run", stage="enhancement")
        rad = cast(EOProduct, inputs["rad"])
        bands = _read_detector_bands(rad)
        upstream_qa = _read_qa_masks(rad)
        logger.info(f"Enhancement: {len(bands)} band(s), denoise={params.denoise_method}, MTFC mandatory (always runs)")

        kernels = self._resolve_psf(adf_map)
        dark_frames = self._resolve_dark(adf_map)

        enhanced_bands: dict[str, npt.NDArray[np.uint16]] = {}
        qa_bands: dict[str, npt.NDArray[np.uint16]] = {}
        for band, dn in bands.items():
            clipped, qa = self._process_band(band, dn, kernels, dark_frames, params)
            if band in upstream_qa:
                qa = qa | upstream_qa[band].astype(np.uint16)
            enhanced_bands[band] = clipped.astype(np.uint16)
            qa_bands[band] = qa

        output_name = str(kwargs.get("name", f"{rad.name}_ENH"))
        enh = self._build_enh_product(output_name, enhanced_bands, qa_bands, params)
        outputs: dict[str, DataType] = {"enh": enh}
        return outputs

    @staticmethod
    def _build_params(kwargs: Mapping[str, Any]) -> EnhancementParams:
        """Build :class:`EnhancementParams` from the run kwargs (with defaults)."""
        method_raw = str(kwargs.get("denoise_method", "none"))
        method: Optional[DenoiseMethod] = None
        for allowed in _ALLOWED_DENOISE:
            if method_raw == allowed:
                method = allowed  # narrows to the DenoiseMethod literal (no cast needed)
                break
        if method is None:
            raise InputValidationError(
                f"Unknown denoise method '{method_raw}'; expected one of {_ALLOWED_DENOISE}",
                stage="enhancement",
            )
        return EnhancementParams(
            denoise_method=method,
            denoise_params=dict(kwargs.get("denoise_params", {})),
            bit_depth=int(kwargs.get("bit_depth", 12)),
            fill_value=kwargs.get("fill_value"),
            mtfc_regularization=float(kwargs.get("mtfc_regularization", 0.0)),
        )

    @staticmethod
    def _resolve_psf(adfs: Mapping[str, AuxiliaryDataFile]) -> dict[str, npt.NDArray[Any]]:
        """Resolve the mandatory per-band MTFC deconvolution kernels (psf ADF)."""
        psf_data = _coerce_mapping(_require_adf(adfs, "psf"))
        kernels = dict(psf_data.get("kernel", {}))
        if not kernels:
            raise AdfResolutionError("psf ADF must provide 'kernel' per band", stage="enhancement")
        return kernels

    @staticmethod
    def _resolve_dark(adfs: Mapping[str, AuxiliaryDataFile]) -> dict[str, npt.NDArray[Any]]:
        """Resolve the optional per-band dark frames (dark ADF, fft_dark only)."""
        dark_adf = adfs.get("dark")
        if dark_adf is None:
            return {}
        return dict(_coerce_mapping(dark_adf).get("frame", {}))

    @staticmethod
    def _process_band(
        band: str,
        dn: npt.NDArray[Any],
        kernels: Mapping[str, npt.NDArray[Any]],
        dark_frames: Mapping[str, npt.NDArray[Any]],
        params: EnhancementParams,
    ) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.uint16]]:
        """Apply the optional denoise then the mandatory MTFC to a single band."""
        image = np.asarray(dn, dtype=np.float32)
        if params.denoise_method != "none":
            dark: Optional[npt.NDArray[Any]] = None
            if params.denoise_method == "fft_dark":
                if band not in dark_frames:
                    raise AdfResolutionError(
                        f"fft_dark denoise requires a dark frame for band '{band}'",
                        stage="enhancement",
                    )
                dark = np.asarray(dark_frames[band], dtype=np.float32)
            image = denoise(image, params.denoise_method, params.denoise_params, dark=dark)

        if band not in kernels:
            raise AdfResolutionError(f"psf ADF has no MTFC kernel for band '{band}'", stage="enhancement")
        restored = mtf_compensate(image, np.asarray(kernels[band], dtype=np.float32))
        return flag_enhanced(restored, params)

    def _build_enh_product(
        self,
        name: str,
        enhanced_bands: Mapping[str, npt.NDArray[np.uint16]],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        params: EnhancementParams,
    ) -> EOProduct:
        """Assemble the enhanced-DN + QA output product (no coefficients)."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": "default",
            },
            "processing_parameters": {
                "denoise_method": params.denoise_method,
                "bit_depth": params.bit_depth,
                "mtfc": "psf_deconvolution",
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product["measurements"] = EOGroup()
        product["quality"] = EOGroup()
        for band, data in enhanced_bands.items():
            product[f"{_DETECTOR_GROUP}/{band}"] = EOVariable(data=data, dims=_DIMS)
            product[f"{_MASK_GROUP}/{band}"] = EOVariable(data=qa_bands[band], dims=_DIMS)
        return product
