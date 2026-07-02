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

"""Thin ``EOProcessingUnit`` wrapper for Level-0 decode (C-PU-L0).

Adapts the pure :mod:`~msi_processor.computing.l0_decode.core` to the EOPF CPM
runtime (SDD <5.4.2>): read parameters, obtain decoded detector frames, detect
and truncate line loss, seed QA, pass acquisition telemetry through, and build
the L1A ``EOProduct``. No algorithm lives here.

Decode seam (SDD <5.4.2>). The on-wire source-packet reassembly / decompression
(ALG-L0-DEC) is sensor-private and held outside this public distribution. The
unit therefore takes one of two L0c forms:

* an *open container* that already exposes decoded samples under
  ``measurements/detector/<band>`` (the documented sample layout the simulator
  and the operational decoder both emit) — the public path exercised here;
* an undecoded on-wire form — which routes to
  :func:`~msi_processor.computing.l0_decode.core.decode_source_packets`, the
  private ``[impl]`` backend, and fail-stops with :class:`L0DecodeError` when
  that backend is absent.

*Trace:* REQ-F-L0-01..05; DPM-M-L0; ALG-L0-DEC, ALG-L0-LOSS; ICD <5.3.1>A.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, cast

import numpy as np
import numpy.typing as npt
from eopf.computing.abstract import EOProcessingUnit, MappingAuxiliary, MappingDataType
from eopf.logging import EOLogging
from eopf.product import EOGroup, EOProduct, EOVariable

from msi_processor.computing.l0_decode.core import (
    L0DecodeParams,
    check_legality,
    decode_source_packets,
    detect_line_loss,
    initial_qa,
    truncate_loss,
)
from msi_processor.exceptions.errors import InputValidationError

_DETECTOR_GROUP = "measurements/detector"
_CONDITIONS_GROUP = "conditions"
_FLAGS_GROUP = "quality/l0_flags"
_DIMS = ("line", "detector")
_VALID_MODES = ("nominal",)
_STAGE = "l0_decode"


def _read_detector_frames(l0c: EOProduct, params: L0DecodeParams) -> dict[str, npt.NDArray[Any]]:
    """Return decoded ``measurements/detector`` frames, or invoke the [impl] decode.

    An L0c that already carries decoded frames is the public open-container path;
    one that does not routes to the sensor-private decode (which fail-stops).
    """
    try:
        group = cast(EOGroup, l0c[_DETECTOR_GROUP])
    except KeyError:
        # No decoded samples present -> the undecoded on-wire form needs the
        # private [impl] backend; this fail-stops with L0DecodeError.
        return decode_source_packets(l0c, codec_spec=params)
    return {name: np.asarray(cast(EOVariable, item).data) for name, item in group.items()}


def _walk_variables(group: EOGroup, prefix: str) -> list[tuple[str, EOVariable]]:
    """Collect ``(path, EOVariable)`` leaves under an ``EOGroup`` recursively."""
    leaves: list[tuple[str, EOVariable]] = []
    for name, item in group.items():
        path = f"{prefix}/{name}"
        if isinstance(item, EOGroup):
            leaves.extend(_walk_variables(item, path))
        else:
            leaves.append((path, cast(EOVariable, item)))
    return leaves


class L0DecodeUnit(EOProcessingUnit):
    """Level-0 decode processing unit (C-PU-L0; SDD <5.4.2>).

    Methods
    -------
    run:
        Decode (open-container) L0c into an L1A product: detector DN in
        focal-plane geometry, passed-through acquisition telemetry, and seeded
        QA, with trailing line loss truncated (ALG-L0-LOSS).
    """

    PROCESSOR_NAME = "msi_l0_decode"
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
        """Decode an L0c product into L1A.

        Parameters
        ----------
        inputs:
            ``{"l0c": EOProduct}`` — the Level-0 product (open-container form
            carries ``measurements/detector/<band>`` + ``conditions/*``).
        adfs:
            None — no auxiliary data is consumed at Level-0 (REQ-F-L0-01).
        mode:
            ``"nominal"``.
        **kwargs:
            :class:`L0DecodeParams` fields plus optional ``name`` for the output.

        Returns
        -------
        Mapping[str, DataType]
            ``{"l1a": EOProduct}`` — detector DN, conditions, and ``l0_flags``.
        """
        logger = EOLogging().get_logger()
        run_mode = mode or "nominal"
        if run_mode not in _VALID_MODES:
            raise InputValidationError(
                f"Unknown l0_decode mode '{run_mode}'; expected one of {_VALID_MODES}",
                stage=_STAGE,
            )
        if "l0c" not in inputs:
            raise InputValidationError("Missing mandatory input 'l0c' for l0_decode run", stage=_STAGE)

        params = self._build_params(kwargs)
        l0c = cast(EOProduct, inputs["l0c"])
        frames = _read_detector_frames(l0c, params)
        check_legality(frames, params)
        logger.info(f"L0 decode: {len(frames)} band(s), mode={run_mode}")

        detector_bands: dict[str, npt.NDArray[np.uint16]] = {}
        qa_bands: dict[str, npt.NDArray[np.uint16]] = {}
        n_lost: dict[str, int] = {}
        for band, raw in frames.items():
            kept, lost = truncate_loss(raw, detect_line_loss(raw))
            detector_bands[band] = np.asarray(kept).astype(np.uint16)
            qa_bands[band] = initial_qa(kept, params)
            n_lost[band] = lost

        primary = next(iter(frames))
        orig_lines = int(np.asarray(frames[primary]).shape[0])
        kept_lines = int(detector_bands[primary].shape[0])

        output_name = str(kwargs.get("name", f"{l0c.name}_L1A"))
        product = self._build_l1a_product(output_name, detector_bands, qa_bands, params, run_mode, n_lost)
        self._passthrough_conditions(l0c, product, orig_lines, kept_lines)
        return cast(MappingDataType, {"l1a": product})

    @staticmethod
    def _build_params(kwargs: Mapping[str, Any]) -> L0DecodeParams:
        """Build :class:`L0DecodeParams` from the run kwargs (with defaults)."""
        return L0DecodeParams(
            bit_depth=int(kwargs.get("bit_depth", 12)),
            line_factor=dict(kwargs.get("line_factor", {})),
            fill_value=kwargs.get("fill_value"),
            max_lost_fraction=kwargs.get("max_lost_fraction"),
        )

    def _build_l1a_product(
        self,
        name: str,
        detector_bands: Mapping[str, npt.NDArray[np.uint16]],
        qa_bands: Mapping[str, npt.NDArray[np.uint16]],
        params: L0DecodeParams,
        mode: str,
        n_lost: Mapping[str, int],
    ) -> EOProduct:
        """Assemble the L1A product (detector DN + seeded QA, no telemetry yet)."""
        provenance = {
            "processor": {
                "name": self.PROCESSOR_NAME,
                "version": self.PROCESSOR_VERSION,
                "mode": mode,
            },
            "processing_parameters": {
                "bit_depth": params.bit_depth,
                "line_factor": dict(params.line_factor),
            },
            "quality": {"lines_lost": dict(n_lost)},
        }
        product = EOProduct(name, attrs={"other_metadata": provenance})
        product["measurements"] = EOGroup()
        product["quality"] = EOGroup()
        for band, data in detector_bands.items():
            product[f"{_DETECTOR_GROUP}/{band}"] = EOVariable(data=data, dims=_DIMS)
            product[f"{_FLAGS_GROUP}/{band}"] = EOVariable(data=qa_bands[band], dims=_DIMS)
        return product

    @staticmethod
    def _passthrough_conditions(
        l0c: EOProduct,
        product: EOProduct,
        orig_lines: int,
        kept_lines: int,
    ) -> None:
        """Copy acquisition telemetry, truncating per-line arrays to kept lines."""
        try:
            conditions = cast(EOGroup, l0c[_CONDITIONS_GROUP])
        except KeyError:
            return
        product[_CONDITIONS_GROUP] = EOGroup()
        for path, var in _walk_variables(conditions, _CONDITIONS_GROUP):
            data = np.asarray(var.data)
            if kept_lines < orig_lines and data.ndim >= 1 and data.shape[0] == orig_lines:
                data = data[:kept_lines]
            product[path] = EOVariable(data=data, dims=var.dims)
