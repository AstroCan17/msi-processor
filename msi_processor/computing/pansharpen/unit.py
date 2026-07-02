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

"""Thin ``EOProcessingUnit`` wrapper for pan-sharpening (C-PU-PAN).

Adapts the pure :mod:`~msi_processor.computing.pansharpen.core` to the EOPF CPM
runtime following the wrapper template of SDD <5.4.1>/<5.4.10>: read parameters,
split the BOA-MS bands from the PAN band, orchestrate the pure-core functions
(ALG-PAN-ALIGN -> ALG-PAN-FUSE -> spectral fidelity), and build the optional
``DPM-PR-L2A-PAN`` derivative product. No algorithm lives here.

Input convention. The upstream stage is the ``atmospheric`` unit; its ``l2a``
product carries the BOA (surface) reflectance under
``measurements/reflectance/<band>`` (IF-PROD-04). One of those bands is the
high-resolution panchromatic band, named by the ``pan_band`` parameter; the
remaining bands form the MS stack that is sharpened onto the PAN grid. Building a
science-grade PAN reflectance (the BOA-PAN vs TOA-PAN choice) is an open
``[impl]``/profile point (ATBD <5.9> open point 7): this wrapper fuses whatever
reflectance the ``pan_band`` carries.

Optionality (CR-4). Pan-sharpening is a terminal, **default-off** derivative. The
chain runner skips it when ``optional_stages.pansharpen`` is false; if the unit is
nevertheless invoked with ``enabled=false`` it fail-stops rather than silently
emitting a product (defensive, REQ-F-PAN-01).

**Fail-stop (REQ-F-PAN-01/02).** A missing reflectance group, an absent
``pan_band``, fewer than one MS band, an alignment failure, or a deferred
``[impl]`` fusion method raise
:class:`~msi_processor.exceptions.errors.PansharpenError` (or
:class:`~msi_processor.exceptions.errors.InputValidationError` for malformed
inputs); it propagates to the chain runner so no derivative is emitted from
incomplete inputs. Per-band spectral fidelity is reported as QA and, when a
profile fidelity budget is supplied, checked against it (REQ-F-PAN-02).

Mandatory inputs are declared by the CPM computing-model JSON
(``models/msi_pansharpen_1.0.0.json``), not by overriding the list methods.

*Trace:* REQ-F-PAN-01..02; DPM-M-PAN, DPM-PR-L2A-PAN; ALG-PAN-ALIGN/FUSE;
ICD IF-PROD-04; SYS-CAP-04.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, cast, get_args

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

from msi_processor.computing.coregistration.core import CoregParams
from msi_processor.computing.pansharpen.core import (
    OPERATIONAL_METHODS,
    FusionMethod,
    align_ms_to_pan,
    fuse,
    spectral_fidelity,
)
from msi_processor.exceptions.errors import InputValidationError, PansharpenError

_MEASUREMENTS = "measurements"
_REFLECTANCE = "reflectance"
_FIDELITY_GROUP = "quality/spectral_fidelity"
_DIMS = ("y", "x")
_METRIC_DIMS = ("metric",)
_STAGE = "pansharpen"


def _read_reflectance(product: EOProduct) -> dict[str, npt.NDArray[np.float32]]:
    """Extract the BOA ``measurements/reflectance/<band>`` arrays."""
    try:
        reflectance = cast(EOGroup, product[f"{_MEASUREMENTS}/{_REFLECTANCE}"])
    except KeyError as exc:
        raise InputValidationError(
            f"Input L2A product has no '{_MEASUREMENTS}/{_REFLECTANCE}' group "
            "(pan-sharpening requires BOA reflectance)",
            stage=_STAGE,
        ) from exc
    bands: dict[str, npt.NDArray[np.float32]] = {}
    for band_name, var in reflectance.items():
        bands[band_name] = np.asarray(cast(EOVariable, var).data, dtype=np.float32)
    if not bands:
        raise InputValidationError(
            f"Input L2A product has no bands under '{_MEASUREMENTS}/{_REFLECTANCE}'",
            stage=_STAGE,
        )
    return bands


def _coreg_params(pan_band: str, kwargs: Mapping[str, Any]) -> CoregParams:
    """Build the alignment parameters (PAN is the reference grid)."""
    grid = kwargs.get("clahe_grid", (8, 8))
    return CoregParams(
        reference_band=pan_band,
        clahe_clip=float(kwargs.get("clahe_clip", 2.0)),
        clahe_grid=(int(grid[0]), int(grid[1])),
        match_fraction=float(kwargs.get("match_fraction", 0.10)),
        min_keypoints=int(kwargs.get("min_keypoints", 20)),
        min_keypoints_pan=int(kwargs.get("min_keypoints_pan", 40)),
        pan_bands=(pan_band,),
        ransac_tau=float(kwargs.get("ransac_tau", 5.0)),
        max_residual=kwargs.get("max_residual"),
        seed=int(kwargs.get("seed", 0)),
    )


class PansharpenUnit(EOProcessingUnit):
    """Optional pan-sharpening processing unit (C-PU-PAN; SDD <5.4.10>).

    Methods
    -------
    run:
        Align the BOA-MS bands onto the PAN grid, fuse them with the PAN band
        and emit the optional ``DPM-PR-L2A-PAN`` derivative with per-band
        spectral-fidelity QA. Only ``method="simple_mean"`` is operational; the
        component-substitution methods are ``[impl]`` (ATBD <5.9> open point 6).
    """

    PROCESSOR_NAME = "msi_pansharpen"
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
        """Run the pan-sharpening derivative.

        Parameters
        ----------
        inputs:
            ``{"l2a": EOProduct}`` with BOA reflectance under
            ``measurements/reflectance/<band>``, including the panchromatic band.
        adfs:
            None required (the PAN band is carried by the L2A product).
        mode:
            ``"nominal"`` (the only supported processing mode).
        **kwargs:
            ``enabled`` (``bool``, default ``True``; ``False`` fail-stops),
            ``method`` (fusion method, default ``"simple_mean"``), ``pan_band``
            (band id of the PAN band; required), ``fidelity_budget`` (optional
            minimum acceptable per-band fidelity), the alignment parameters
            (``ransac_tau``, ``clahe_clip``/``clahe_grid``, ``match_fraction``,
            ``min_keypoints``/``min_keypoints_pan``, ``seed``, ``max_residual``),
            and an optional ``name`` for the output product.

        Returns
        -------
        Mapping[str, DataType]
            ``{"pan": EOProduct}`` with fused ``measurements/reflectance/<band>``
            and ``quality/spectral_fidelity/<band>``.

        Raises
        ------
        PansharpenError
            On a missing ``pan_band``, no MS bands, an alignment failure, a
            deferred ``[impl]`` fusion method, or ``enabled=false`` -- fail-stop
            (REQ-F-PAN-01).
        InputValidationError
            On a missing input / reflectance group or an unknown mode/method type.
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "nominal"
        if run_mode != "nominal":
            raise InputValidationError(
                f"Unknown pansharpen mode '{run_mode}'; expected 'nominal'",
                stage=_STAGE,
            )

        enabled = bool(kwargs.get("enabled", True))
        if not enabled:
            raise PansharpenError(
                "Pan-sharpening invoked with enabled=false; the chain must skip "
                "this optional stage rather than run it (CR-4 default-off)",
                stage=_STAGE,
            )

        method = str(kwargs.get("method", "simple_mean"))
        if method not in get_args(FusionMethod):
            raise InputValidationError(
                f"Unknown fusion method '{method}'; expected one of {get_args(FusionMethod)}",
                stage=_STAGE,
            )

        if "l2a" not in inputs:
            raise InputValidationError("Missing mandatory input 'l2a' for pansharpen run", stage=_STAGE)
        l2a = cast(EOProduct, inputs["l2a"])
        reflectance = _read_reflectance(l2a)

        pan_band = kwargs.get("pan_band")
        if pan_band is None:
            raise PansharpenError(
                "Pan-sharpening requires a 'pan_band' parameter naming the " "panchromatic band in the L2A product",
                stage=_STAGE,
            )
        pan_band = str(pan_band)
        if pan_band not in reflectance:
            raise PansharpenError(
                f"PAN band '{pan_band}' is absent from the L2A reflectance " f"(available: {sorted(reflectance)})",
                stage=_STAGE,
            )
        pan = reflectance[pan_band]
        ms_stack = {band: data for band, data in reflectance.items() if band != pan_band}
        if not ms_stack:
            raise PansharpenError(
                f"No MS bands to sharpen after removing PAN band '{pan_band}'",
                stage=_STAGE,
            )

        params = _coreg_params(pan_band, kwargs)
        aligned = align_ms_to_pan(ms_stack, pan, params)
        fused = fuse(aligned, pan, cast(FusionMethod, method))
        fidelity = spectral_fidelity(aligned, fused)

        budget = kwargs.get("fidelity_budget")
        below_budget = self._check_fidelity(fidelity, budget)

        logger.info(
            f"Pansharpen: {len(ms_stack)} MS band(s) fused with PAN '{pan_band}' "
            f"via '{method}'; min fidelity={min(fidelity.values()) if fidelity else float('nan'):.3f}"
        )

        output_name = str(kwargs.get("name", f"{l2a.name}_L2A_PAN"))
        product = self._build_pan_product(output_name, fused, fidelity, method, pan_band, budget, below_budget)
        outputs: dict[str, DataType] = {"pan": product}
        return outputs

    # ----------------------------------------------------------------------- #
    # Helpers                                                                  #
    # ----------------------------------------------------------------------- #
    @staticmethod
    def _check_fidelity(
        fidelity: Mapping[str, float],
        budget: Any,
    ) -> list[str]:
        """Return bands whose fidelity falls below the profile budget (REQ-F-PAN-02).

        The budget is private/per-profile; ``None`` accepts any value. Bands below
        budget are reported in QA but do not fail the stage (the derivative is not
        science-grade, DPM <8.9>).
        """
        if budget is None:
            return []
        threshold = float(budget)
        return [band for band, value in fidelity.items() if value < threshold]

    def _build_pan_product(
        self,
        name: str,
        fused: Mapping[str, npt.NDArray[np.float32]],
        fidelity: Mapping[str, float],
        method: str,
        pan_band: str,
        budget: Any,
        below_budget: list[str],
    ) -> EOProduct:
        """Assemble the DPM-PR-L2A-PAN derivative (fused bands + fidelity QA)."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": "nominal",
            },
            "processing_parameters": {
                "method": method,
                "pan_band": pan_band,
                "fidelity_budget": None if budget is None else float(budget),
                "operational_methods": list(OPERATIONAL_METHODS),
            },
            "quality": {
                "spectral_fidelity": {band: float(v) for band, v in fidelity.items()},
                "bands_below_fidelity_budget": list(below_budget),
                "science_grade": False,
            },
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product[_MEASUREMENTS] = EOGroup()
        product["quality"] = EOGroup()
        for band, data in fused.items():
            product[f"{_MEASUREMENTS}/{_REFLECTANCE}/{band}"] = EOVariable(data=data, dims=_DIMS)
        for band, value in fidelity.items():
            product[f"{_FIDELITY_GROUP}/{band}"] = EOVariable(
                data=np.array([value], dtype=np.float32), dims=_METRIC_DIMS
            )
        return product
