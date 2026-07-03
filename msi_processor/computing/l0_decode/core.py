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

"""Pure Level-0 decode core (C-PU-L0; ALG-L0-DEC, ALG-L0-LOSS).

CPM-free, I/O-free numpy functions implementing the *public* Level-0 → L1A
scaffolding of ATBD <5.1>: deterministic line-loss detection and truncation
(ALG-L0-LOSS), structural legality checking (REQ-F-L0-03) and initial QA
flagging. Arrays are 2-D ``(line, detector)`` in focal-plane geometry.

The sensor-private source-packet reassembly / decompression (ALG-L0-DEC) is a
profile-bound ``[impl]`` backend held outside this public distribution; the
public path here operates on already-decoded *open-container* detector frames
(the documented sample layout the simulator and the operational decoder both
produce). :func:`decode_source_packets` is the explicit fail-stop seam.

*Trace:* REQ-F-L0-01..05; DPM-M-L0; ALG-L0-DEC, ALG-L0-LOSS.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from struct import error as struct_error
from typing import Any, Optional

import numpy as np
import numpy.typing as npt

from msi_processor.common.types import QAFlag
from msi_processor.exceptions.errors import InputValidationError, L0DecodeError

__all__ = [
    "L0DecodeParams",
    "detect_line_loss",
    "truncate_loss",
    "check_legality",
    "initial_qa",
    "decode_source_packets",
]

IntArray = npt.NDArray[np.uint16]
BoolArray = npt.NDArray[np.bool_]
QAArray = npt.NDArray[np.uint16]

_STAGE = "l0_decode"


@dataclass(frozen=True)
class L0DecodeParams:
    """Tunable Level-0 decode parameters (SDD <5.4.2>; DPM-PRM-L0-01).

    Parameters
    ----------
    bit_depth:
        Sensor radiometric depth; legal DN range ``[0, 2**bit_depth - 1]``
        (``DPM-PRM-GEN-01``, default 12).
    line_factor:
        Per-band line decimation factor echoed for provenance (e.g. a PAN band
        acquired at twice the line rate); does not transform the samples here.
    fill_value:
        No-data sentinel DN; flagged ``NO_DATA`` when present.
    max_lost_fraction:
        Legality bound (REQ-F-L0-03): reject a band whose truncated line loss
        exceeds this fraction. ``None`` disables the bound.
    """

    bit_depth: int = 12
    line_factor: Mapping[str, int] = field(default_factory=dict)
    fill_value: Optional[int] = None
    max_lost_fraction: Optional[float] = None

    @property
    def max_dn(self) -> int:
        """Upper bound of the valid DN range, ``2**bit_depth - 1``."""
        return 2**self.bit_depth - 1


def detect_line_loss(band: npt.NDArray[Any]) -> BoolArray:
    """ALG-L0-LOSS — boolean mask of trailing lost lines in a band.

    Deterministic rule (ATBD <5.1>): downlink line loss zero-fills the tail of
    the frame, so the loss boundary is the first all-zero line that follows a
    non-zero line; every line from there to the end is marked lost. A frame with
    no non-zero→zero transition has no loss. Interior partially-corrupted
    (non-zero) lines are *not* caught here (ATBD <5.1> open point).

    Parameters
    ----------
    band:
        2-D ``(line, detector)`` DN frame.

    Returns
    -------
    BoolArray
        Per-line mask, ``True`` on lost lines.
    """
    arr = np.asarray(band)
    if arr.ndim != 2:
        raise InputValidationError(
            f"L0 band must be a 2-D (line, detector) array; got ndim={arr.ndim}",
            stage=_STAGE,
        )
    n_lines = arr.shape[0]
    mask = np.zeros(n_lines, dtype=bool)
    line_is_zero = ~np.any(arr != 0, axis=1)
    nonzero_lines = np.flatnonzero(~line_is_zero)
    if nonzero_lines.size == 0 or nonzero_lines.size == n_lines:
        return mask  # all-zero frame (no data signal) or no zero tail -> no truncation
    last_data = int(nonzero_lines[-1])
    first_lost = last_data + 1
    if first_lost < n_lines:
        mask[first_lost:] = True
    return mask


def truncate_loss(band: npt.NDArray[Any], loss_mask: BoolArray) -> tuple[npt.NDArray[Any], int]:
    """Drop the trailing lost lines (REQ-F-L0-02); return ``(kept, n_lost)``."""
    n_lost = int(np.count_nonzero(loss_mask))
    if n_lost == 0:
        return band, 0
    keep = band.shape[0] - n_lost
    return band[:keep], n_lost


def check_legality(frames: Mapping[str, npt.NDArray[Any]], params: L0DecodeParams) -> None:
    """REQ-F-L0-03 — validate decoded frame structure / DN range; raise on fault.

    Checks that the frame set is non-empty, every band is a 2-D integer-valued
    frame within ``[0, max_dn]``, and (if ``max_lost_fraction`` is set) that the
    trailing line loss is within budget. Raises :class:`InputValidationError`.
    """
    if not frames:
        raise InputValidationError("L0c product carries no decoded bands", stage=_STAGE)
    for band, data in frames.items():
        arr = np.asarray(data)
        if arr.ndim != 2:
            raise InputValidationError(
                f"L0 band '{band}' must be 2-D (line, detector); got ndim={arr.ndim}",
                stage=_STAGE,
            )
        if arr.size == 0:
            raise InputValidationError(f"L0 band '{band}' is empty", stage=_STAGE)
        finite = arr[np.isfinite(arr)] if np.issubdtype(arr.dtype, np.floating) else arr
        if finite.size and (int(np.min(finite)) < 0 or int(np.max(finite)) > params.max_dn):
            raise InputValidationError(
                f"L0 band '{band}' has DN outside [0, {params.max_dn}] (bit_depth={params.bit_depth})",
                stage=_STAGE,
            )
        if params.max_lost_fraction is not None:
            lost = int(np.count_nonzero(detect_line_loss(arr)))
            if lost / arr.shape[0] > params.max_lost_fraction:
                raise InputValidationError(
                    f"L0 band '{band}' line loss {lost}/{arr.shape[0]} exceeds "
                    f"max_lost_fraction={params.max_lost_fraction}",
                    stage=_STAGE,
                    report_fields={"band": band, "n_lost": lost, "n_lines": int(arr.shape[0])},
                )


def initial_qa(band: npt.NDArray[Any], params: L0DecodeParams) -> QAArray:
    """Build the initial L1A QA mask for a (truncated) band (REQ-F-QA-02 seed).

    Sets ``NO_DATA`` on fill-value pixels (if a sentinel is configured) and on
    any wholly-zero interior line. Bits accumulate monotonically downstream
    (OR-only); the initial mask is otherwise ``0``.
    """
    arr = np.asarray(band)
    qa = np.zeros(arr.shape, dtype=np.uint16)
    if params.fill_value is not None:
        qa[arr == params.fill_value] |= np.uint16(QAFlag.NO_DATA)
    interior_zero = ~np.any(arr != 0, axis=1)
    if interior_zero.any():
        qa[interior_zero, :] |= np.uint16(QAFlag.NO_DATA)
    return qa


def _canonical_band_streams(raw: Any) -> dict[str, dict[str, npt.NDArray[np.uint8]]]:
    """Collect ``d{DD}/b{bb} -> {"isp": stream}`` from a canonical L0 product (duck-typed).

    Walks ``measurements/d*/b*`` groups of the input product (EOProduct or any nested
    mapping) and returns the uint8 packet streams; empty when the product carries no
    canonical band groups (i.e. it is not the documented downlink form).
    """
    streams: dict[str, dict[str, npt.NDArray[np.uint8]]] = {}
    try:
        meas = raw["measurements"]
        items = meas.items()
    except (KeyError, TypeError, AttributeError):
        return streams
    for dname, det in items:
        if not (isinstance(dname, str) and dname.startswith("d") and hasattr(det, "items")):
            continue
        for bname, grp in det.items():
            try:
                var = grp["isp"]
            except (KeyError, TypeError):
                continue
            stream = np.asarray(getattr(var, "data", var), dtype=np.uint8)
            streams[f"{dname}/{bname}"] = {"isp": stream}
    return streams


def decode_source_packets(raw: Any, codec_spec: Any) -> dict[str, IntArray]:
    """ALG-L0-DEC — reassemble/decompress source packets to detector frames.

    The **documented open downlink form** — the producer's canonical L0
    (``measurements/d{DD}/b{bb}/isp``: CCSDS space packets carrying CCSDS-122
    lossless payloads) — is ground-decoded here bit-exactly
    (:mod:`~msi_processor.computing.l0_decode.ground_decode`, REQ-F-L0D-06): the
    real-chain L1A-side decompression now lives in the consumer.

    Any *other* on-wire packetisation remains sensor/NDA-specific and
    profile-bound: that body is a private ``[impl]`` backend not part of this
    public distribution, and fail-stops below.
    """
    from msi_processor.computing.l0_decode import ground_decode

    streams = _canonical_band_streams(raw)
    if streams:
        try:
            frames = ground_decode.decode_canonical_frames(streams)
        except (ValueError, struct_error) as exc:
            raise L0DecodeError(f"canonical L0 ground decode failed: {exc}", stage=_STAGE) from exc
        return {b: np.asarray(f, dtype=np.uint16) for b, f in frames.items()}
    raise L0DecodeError(
        "the Level-0 source-packet decode body is sensor-private and profile-bound "
        "([impl]); supply the documented canonical L0 (compressed ISPs) or "
        "already-decoded open-container detector frames",
        stage=_STAGE,
    )
