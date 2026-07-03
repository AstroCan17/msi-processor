# Copyright 2026 Can Deniz Kaya
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
"""ALG-L0-DEC — the consumer-side ground decode of the canonical (downlink) Level-0.

The real-chain L1A-side operation (the Sentinel-2 L0→L1A relation is decode/packaging:
L0 stores compressed instrument source packets, L1A decompresses): walk the CCSDS space
packets of a band's ``isp`` stream, reassemble the segment groups (seq-flags grammar +
14-bit counter continuity enforced), join them back into the CCSDS-122 stream and decode
it **bit-exactly** to the detector DN frame.

This implements the documented open interface of the producer's canonical L0
(``measurements/d{DD}/b{bb}/isp`` — ICD-IF-ISP / ICD-IF-C122 in the s2-msi-raw-generator
ICD). Truly sensor-private on-wire formats still fail-stop in
:func:`~msi_processor.computing.l0_decode.core.decode_source_packets`.

numpy-only (plus :mod:`zarr` for the path-based helper); no eopf dependency.
"""

from __future__ import annotations

import re
from typing import Any, Iterator

import numpy as np

from msi_processor.computing.l0_decode import ccsds122

__all__ = [
    "decode_stream",
    "decode_canonical_frames",
    "decode_canonical_l0",
    "iter_packets",
    "reassemble_segments",
    "parse_primary_header",
]

PRIMARY_HEADER_LEN = 6  # CCSDS Space Packet primary header (octets)
CUC_TIME_LEN = 6  # secondary header: 4-octet coarse + 2-octet fine (CUC)
SEQ_STANDALONE = 0b11  # unsegmented (standalone) packet
SEQ_FIRST = 0b01  # first packet of a segmented group
SEQ_CONT = 0b00  # continuation packet
SEQ_LAST = 0b10  # last packet of a segmented group
SEQ_COUNT_MOD = 1 << 14  # 14-bit sequence counter

#: Canonical L0 band-group path pattern: measurements/d{DD}/b{bb} (b8a for B8A).
_CANONICAL_RE = re.compile(r"^d(\d{2})/(b[0-9a-z]{2,3})$")


def parse_primary_header(b: bytes) -> dict[str, int]:
    """CCSDS Space Packet primary header → field dict (decode direction)."""
    w0 = (b[0] << 8) | b[1]
    w1 = (b[2] << 8) | b[3]
    w2 = (b[4] << 8) | b[5]
    return {
        "version": w0 >> 13,
        "packet_type": (w0 >> 12) & 1,
        "sec_hdr_flag": (w0 >> 11) & 1,
        "apid": w0 & 0x7FF,
        "seq_flags": (w1 >> 14) & 0x3,
        "seq_count": w1 & 0x3FFF,
        "data_len": w2,
    }


def _parse_cuc_time(b: bytes) -> float:
    """6-octet CUC → seconds (4-octet coarse + 2-octet fine / 65536)."""
    coarse = (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]
    fine = (b[4] << 8) | b[5]
    return coarse + fine / 65536.0


def iter_packets(buf: bytes | np.ndarray) -> Iterator[tuple[dict[str, int], float | None, bytes]]:
    """Iterate CCSDS packets in a concatenated stream → ``(header, cuc_seconds, body)``.

    The primary header's *Packet Data Length* field walks the stream; a stream is
    well-formed iff packets tile it exactly. ``body`` excludes the CUC secondary header.
    """
    data = bytes(bytearray(np.asarray(buf, dtype=np.uint8))) if not isinstance(buf, (bytes, memoryview)) else bytes(buf)
    pos = 0
    while pos < len(data):
        if pos + PRIMARY_HEADER_LEN > len(data):
            raise ValueError(f"truncated primary header at offset {pos}")
        hdr_end = pos + PRIMARY_HEADER_LEN
        hdr = parse_primary_header(data[pos:hdr_end])
        dlen = hdr["data_len"] + 1
        end = pos + PRIMARY_HEADER_LEN + dlen
        if end > len(data):
            raise ValueError(f"packet at offset {pos} overruns the stream")
        field = data[hdr_end:end]
        has_cuc = hdr["sec_hdr_flag"] and dlen >= CUC_TIME_LEN
        cuc = _parse_cuc_time(field[:CUC_TIME_LEN]) if has_cuc else None
        body = field[CUC_TIME_LEN:] if has_cuc else field
        yield hdr, cuc, body
        pos = end


def reassemble_segments(buf: bytes | np.ndarray) -> list[bytes]:
    """Packets → per-segment byte streams (strict grammar + continuity).

    Enforces the seq-flags grammar (FIRST → CONT* → LAST, or STANDALONE) and the 14-bit
    sequence-counter continuity; raises ``ValueError`` on gaps or malformed sequences.
    """
    segments: list[bytes] = []
    current: list[bytes] | None = None
    prev_seq: int | None = None
    for hdr, _cuc, body in iter_packets(buf):
        if prev_seq is not None and hdr["seq_count"] != (prev_seq + 1) % SEQ_COUNT_MOD:
            raise ValueError(f"sequence gap: {prev_seq} → {hdr['seq_count']}")
        prev_seq = hdr["seq_count"]
        flags = hdr["seq_flags"]
        if flags == SEQ_STANDALONE:
            if current is not None:
                raise ValueError("STANDALONE inside an open segmented group")
            segments.append(body)
        elif flags == SEQ_FIRST:
            if current is not None:
                raise ValueError("FIRST inside an open segmented group")
            current = [body]
        elif flags == SEQ_CONT:
            if current is None:
                raise ValueError("CONTINUATION without FIRST")
            current.append(body)
        elif flags == SEQ_LAST:
            if current is None:
                raise ValueError("LAST without FIRST")
            current.append(body)
            segments.append(b"".join(current))
            current = None
    if current is not None:
        raise ValueError("stream ended inside a segmented group")
    return segments


def decode_stream(stream: bytes | np.ndarray) -> np.ndarray:
    """One band's canonical ``isp`` stream → the exact uint16 DN frame (bit-exact)."""
    payload = b"".join(reassemble_segments(stream))
    return ccsds122.decompress_frame(payload)


def decode_canonical_frames(band_groups: dict[str, Any]) -> dict[str, np.ndarray]:
    """Decode a mapping of canonical band groups → ``{BAND: DN}``.

    ``band_groups`` maps ``d{DD}/b{bb}`` paths to objects exposing an ``isp`` member
    (zarr groups or nested mappings of arrays). Band keys are upper-cased to the
    processor convention (``b8a`` → ``B8A``).
    """
    frames: dict[str, np.ndarray] = {}
    for path, grp in band_groups.items():
        m = _CANONICAL_RE.match(path)
        if not m:
            continue
        band = m.group(2).upper()  # b04 -> B04, b8a -> B8A
        frames[band] = decode_stream(np.asarray(grp["isp"]))
    if not frames:
        raise ValueError("no canonical d{DD}/b{bb}/isp band groups found")
    return frames


def decode_canonical_l0(path: str, detector: int, band: str) -> np.ndarray:
    """Path-based helper: canonical L0 zarr → one band's bit-exact DN frame."""
    import zarr

    key = "b" + band[1:].lower()  # B03 -> b03, B8A -> b8a (producer convention)
    g = zarr.open_group(str(path), mode="r")
    mg = g[f"measurements/d{detector:02d}/{key}"]
    return decode_stream(np.asarray(mg["isp"]))
