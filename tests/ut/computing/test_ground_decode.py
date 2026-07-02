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
"""Ground decode of the canonical L0 (REQ-F-L0D-06, ALG-L0-DEC).

The fixture pair (``canonical_isp_stream.npy`` / ``canonical_isp_dn.npy``) was produced
by the producer's public chain (CCSDS-122 lossless compress → CCSDS space packets,
seed 42, 24×32 @ 12 bit, max_payload 512 → 3 segments / 3 packets); the consumer-side
decode must return the DN **bit-exactly**.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from msi_processor.computing.l0_decode import ground_decode
from msi_processor.computing.l0_decode.core import L0DecodeParams, decode_source_packets
from msi_processor.exceptions.errors import L0DecodeError

_DATA = Path(__file__).parent / "data"

pytestmark = pytest.mark.unit


@pytest.fixture()
def stream() -> np.ndarray:
    return np.load(_DATA / "canonical_isp_stream.npy")


@pytest.fixture()
def dn() -> np.ndarray:
    return np.load(_DATA / "canonical_isp_dn.npy")


def test_decode_stream_is_bit_exact(stream, dn):
    out = ground_decode.decode_stream(stream)
    assert out.dtype == dn.dtype and out.shape == dn.shape
    assert np.array_equal(out, dn)


def test_packets_tile_the_stream_and_carry_cuc(stream):
    pkts = list(ground_decode.iter_packets(stream))
    assert len(pkts) == 3
    covered = sum(ground_decode.PRIMARY_HEADER_LEN + h["data_len"] + 1 for h, _, _ in pkts)
    assert covered == stream.size                       # well-formed iff packets tile exactly
    assert all(cuc is not None and cuc > 0 for _, cuc, _ in pkts)
    seqs = [h["seq_count"] for h, _, _ in pkts]
    assert seqs == [(seqs[0] + i) % ground_decode.SEQ_COUNT_MOD for i in range(len(seqs))]


def test_sequence_gap_is_rejected(stream):
    corrupt = stream.copy()
    pkts = list(ground_decode.iter_packets(stream))
    second_off = ground_decode.PRIMARY_HEADER_LEN + pkts[0][0]["data_len"] + 1
    corrupt[second_off + 3] ^= 0x01                     # flip a seq_count bit of packet 2
    with pytest.raises(ValueError, match="sequence gap"):
        ground_decode.reassemble_segments(corrupt)


def test_truncated_stream_is_rejected(stream):
    with pytest.raises(ValueError, match="overruns|truncated"):
        list(ground_decode.iter_packets(stream[: stream.size - 5]))


def test_decode_source_packets_canonical_product(stream, dn):
    """The unit's [impl] fallback now ground-decodes the documented canonical form."""
    product = {"measurements": {"d01": {"b04": {"isp": stream}}}}
    frames = decode_source_packets(product, codec_spec=L0DecodeParams())
    assert set(frames) == {"B04"}
    assert np.array_equal(frames["B04"], dn)


def test_decode_source_packets_still_fail_stops_on_unknown_forms():
    with pytest.raises(L0DecodeError, match="sensor-private"):
        decode_source_packets({"measurements": {}}, codec_spec=L0DecodeParams())
