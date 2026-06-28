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

"""Thin ``EOProcessingUnit`` wrapper for inter-band co-registration (C-PU-COR).

Adapts the pure :mod:`~msi_processor.computing.coregistration.core` to the EOPF
CPM runtime following the wrapper template of SDD <5.4.1>/<5.4.6>: read
parameters, extract the input bands, orchestrate the pure-core functions per
band, propagate QA, and build the output ``cor`` ``EOProduct``. No algorithm
lives here.

Input convention. The upstream stage is the ``toa`` unit; its ``l1b`` product
carries the at-sensor radiance under ``measurements/radiance/<band>`` (the
feature source and primary measurement), optional TOA reflectance under
``measurements/reflectance/<band>``, and QA under ``quality/mask/<band>``
(IF-PROD-03). Each non-reference band is aligned to the profile-defined
reference band; the homography estimated from the radiance band is applied to
every co-located representation of that band (radiance and, when present,
reflectance) so the stack stays consistent. The reference band passes through.

This stage takes **no ADFs** (SDD <5.4.6>): the co-registration parameters
(reference band, CLAHE/SIFT/FLANN/RANSAC tuning, acceptance budget) are profile
data passed as run parameters, not private calibration content.

**Fail-stop (REQ-F-COR-03).** On insufficient matches or a residual outside the
acceptance budget, the pure core raises
:class:`~msi_processor.exceptions.errors.CoregistrationError` carrying the
:attr:`~msi_processor.common.types.QAFlag.COREG_FAIL` flag; it propagates to the
chain runner so no misregistered product is emitted.

Mandatory inputs are declared by the CPM computing-model JSON
(``models/msi_coregistration_1.0.0.json``), not by overriding the list methods.

*Trace:* REQ-F-COR-01..03; DPM-M-COR; ALG-COR-*; ICD IF-PROD-03.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, cast

import numpy as np
import numpy.typing as npt
from eopf.computing.abstract import (
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
    estimate_homography,
    warp_qa,
    warp_to_reference,
)
from msi_processor.exceptions.errors import CoregistrationError, InputValidationError

_RADIANCE_GROUP = "measurements/radiance"
_REFLECTANCE_GROUP = "measurements/reflectance"
_MASK_GROUP = "quality/mask"
_DIMS = ("line", "detector")


def _read_band_group(product: EOProduct, group_path: str) -> dict[str, npt.NDArray[Any]]:
    """Extract ``<group_path>/<band>`` arrays (empty if the group is absent)."""
    try:
        group = cast(EOGroup, product[group_path])
    except KeyError:
        return {}
    bands: dict[str, npt.NDArray[Any]] = {}
    for name, item in group.items():
        bands[name] = np.asarray(cast(EOVariable, item).data)
    return bands


class CoregistrationUnit(EOProcessingUnit):
    """Inter-band co-registration processing unit (C-PU-COR; SDD <5.4.6>).

    Methods
    -------
    run:
        Align every band to the profile-defined reference band and emit the
        co-registered ``cor`` product with residual-driven QA.
    """

    PROCESSOR_NAME = "msi_coregistration"
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
        """Run the inter-band co-registration.

        Parameters
        ----------
        inputs:
            ``{"l1b": EOProduct}`` with radiance under ``measurements/radiance``,
            optional reflectance under ``measurements/reflectance`` and QA under
            ``quality/mask``.
        adfs:
            None (this stage takes no ADFs).
        mode:
            ``"default"`` (the only supported mode).
        **kwargs:
            :class:`CoregParams` fields — ``reference_band`` (mandatory),
            ``clahe_clip``, ``clahe_grid``, ``match_fraction``, ``min_keypoints``,
            ``min_keypoints_pan``, ``pan_bands``, ``ransac_tau``, ``max_residual``,
            ``seed`` — plus an optional ``name`` for the output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"cor": EOProduct}`` with the co-registered
            ``measurements/radiance/<band>`` (+ ``measurements/reflectance/<band>``
            when present) and the propagated ``quality/mask/<band>``.

        Raises
        ------
        CoregistrationError
            On insufficient matches or a residual outside acceptance (fail-stop,
            REQ-F-COR-03).
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "default"
        if run_mode != "default":
            raise InputValidationError(
                f"Unknown coregistration mode '{run_mode}'; expected 'default'",
                stage="coregistration",
            )

        params = self._build_params(kwargs)

        if "l1b" not in inputs:
            raise InputValidationError("Missing mandatory input 'l1b' for coregistration run", stage="coregistration")
        l1b = cast(EOProduct, inputs["l1b"])
        radiance = _read_band_group(l1b, _RADIANCE_GROUP)
        if not radiance:
            raise InputValidationError(
                f"Input L1B product has no bands under '{_RADIANCE_GROUP}'",
                stage="coregistration",
            )
        reflectance = _read_band_group(l1b, _REFLECTANCE_GROUP)
        upstream_qa = _read_band_group(l1b, _MASK_GROUP)

        if params.reference_band not in radiance:
            raise InputValidationError(
                f"Reference band '{params.reference_band}' is not among the radiance bands",
                stage="coregistration",
            )
        logger.info(
            f"Co-registration: {len(radiance)} band(s) to reference "
            f"'{params.reference_band}', tau={params.ransac_tau}px"
        )

        reference = radiance[params.reference_band]
        ref_shape = (int(reference.shape[0]), int(reference.shape[1]))

        out_radiance: dict[str, npt.NDArray[Any]] = {}
        out_reflectance: dict[str, npt.NDArray[Any]] = {}
        out_qa: dict[str, npt.NDArray[np.uint16]] = {}

        for band, data in radiance.items():
            base_qa = upstream_qa.get(band, np.zeros(data.shape, dtype=np.uint16)).astype(np.uint16)
            if band == params.reference_band:
                out_radiance[band] = data
                if band in reflectance:
                    out_reflectance[band] = reflectance[band]
                out_qa[band] = base_qa
                continue

            homography, residual = estimate_homography(
                data, reference, params, min_keypoints=params.min_keypoints_for(band)
            )
            if not residual.accepted:
                # Fail-stop: flag the band and refuse to emit a misregistered product.
                raise CoregistrationError(
                    f"Co-registration residual for band '{band}' "
                    f"({residual.rms_residual_px:.3f} px) exceeds acceptance",
                    stage="coregistration",
                    qa_flag=int(QAFlag.COREG_FAIL),
                    report_fields={"band": band, "rms_residual_px": residual.rms_residual_px},
                )

            out_radiance[band] = warp_to_reference(data, homography, ref_shape)
            if band in reflectance:
                out_reflectance[band] = warp_to_reference(reflectance[band], homography, ref_shape)
            out_qa[band] = self._warp_band_qa(base_qa, data.shape, homography, ref_shape)

        output_name = str(kwargs.get("name", f"{l1b.name}_COR"))
        cor = self._build_cor_product(output_name, out_radiance, out_reflectance, out_qa, params)
        outputs: dict[str, DataType] = {"cor": cor}
        return outputs

    @staticmethod
    def _build_params(kwargs: Mapping[str, Any]) -> CoregParams:
        """Build :class:`CoregParams` from the run kwargs (with defaults)."""
        if not kwargs.get("reference_band"):
            raise InputValidationError(
                "coregistration requires a 'reference_band' parameter",
                stage="coregistration",
            )
        grid = kwargs.get("clahe_grid", (8, 8))
        max_residual = kwargs.get("max_residual")
        return CoregParams(
            reference_band=str(kwargs["reference_band"]),
            clahe_clip=float(kwargs.get("clahe_clip", 2.0)),
            clahe_grid=(int(grid[0]), int(grid[1])),
            match_fraction=float(kwargs.get("match_fraction", 0.10)),
            min_keypoints=int(kwargs.get("min_keypoints", 20)),
            min_keypoints_pan=int(kwargs.get("min_keypoints_pan", 40)),
            pan_bands=tuple(str(b) for b in kwargs.get("pan_bands", ())),
            ransac_tau=float(kwargs.get("ransac_tau", 5.0)),
            max_residual=None if max_residual is None else float(max_residual),
            seed=int(kwargs.get("seed", 0)),
        )

    @staticmethod
    def _warp_band_qa(
        base_qa: npt.NDArray[np.uint16],
        src_shape: tuple[int, ...],
        homography: npt.NDArray[Any],
        ref_shape: tuple[int, int],
    ) -> npt.NDArray[np.uint16]:
        """Warp a band's QA mask and flag NO_DATA where the source does not cover."""
        warped_qa = warp_qa(base_qa, homography, ref_shape)
        coverage = warp_qa(np.ones(src_shape, dtype=np.uint16), homography, ref_shape)
        no_data = np.where(coverage == 0, np.uint16(QAFlag.NO_DATA), np.uint16(0))
        return (warped_qa | no_data).astype(np.uint16)

    def _build_cor_product(
        self,
        name: str,
        radiance_bands: Mapping[str, npt.NDArray[Any]],
        reflectance_bands: Mapping[str, npt.NDArray[Any]],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        params: CoregParams,
    ) -> EOProduct:
        """Assemble the co-registered radiance(/reflectance) + QA output product."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": "default",
            },
            "processing_parameters": {
                "reference_band": params.reference_band,
                "ransac_tau": params.ransac_tau,
                "match_fraction": params.match_fraction,
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product["measurements"] = EOGroup()
        product["quality"] = EOGroup()
        for band, data in radiance_bands.items():
            product[f"{_RADIANCE_GROUP}/{band}"] = EOVariable(data=data, dims=_DIMS)
            product[f"{_MASK_GROUP}/{band}"] = EOVariable(data=qa_bands[band], dims=_DIMS)
        for band, data in reflectance_bands.items():
            product[f"{_REFLECTANCE_GROUP}/{band}"] = EOVariable(data=data, dims=_DIMS)
        return product
