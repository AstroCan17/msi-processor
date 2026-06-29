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

"""Unit tests for the Level-0 decode core (ALG-L0-DEC, ALG-L0-LOSS).

The public scaffolding (line-loss detection/truncation, legality, initial QA)
is checked against deterministic synthetic frames; the sensor-private decode
body is verified to fail-stop (it is not part of this public distribution).
"""

import numpy as np
import pytest

from msi_processor.common.types import QAFlag
from msi_processor.computing.l0_decode.core import (
    L0DecodeParams,
    check_legality,
    decode_source_packets,
    detect_line_loss,
    initial_qa,
    truncate_loss,
)
from msi_processor.exceptions.errors import InputValidationError, L0DecodeError


def _frame(n_lines: int = 8, n_det: int = 6, lost_tail: int = 0, seed: int = 0) -> np.ndarray:
    """A DN frame in [1, 4095] with an optional all-zero trailing block."""
    rng = np.random.default_rng(seed)
    arr = rng.integers(1, 4096, size=(n_lines, n_det)).astype(np.uint16)
    if lost_tail:
        start = n_lines - lost_tail
        arr[start:] = 0
    return arr


# --------------------------------------------------------------------------- #
# ALG-L0-LOSS                                                                  #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_detect_line_loss_none_when_no_zero_tail():
    """A fully-populated frame has no trailing loss."""
    mask = detect_line_loss(_frame())
    assert not mask.any()


@pytest.mark.unit
def test_detect_line_loss_marks_trailing_zeros():
    """The all-zero tail following data is flagged lost."""
    mask = detect_line_loss(_frame(n_lines=8, lost_tail=3))
    assert mask.tolist() == [False] * 5 + [True] * 3


@pytest.mark.unit
def test_detect_line_loss_all_zero_frame_is_not_loss():
    """A wholly-zero frame is a no-data signal, not a truncation event."""
    mask = detect_line_loss(np.zeros((4, 5), dtype=np.uint16))
    assert not mask.any()


@pytest.mark.unit
def test_detect_line_loss_rejects_non_2d():
    """A non-2-D band is rejected."""
    with pytest.raises(InputValidationError, match="2-D"):
        detect_line_loss(np.zeros((4,), dtype=np.uint16))


@pytest.mark.unit
def test_truncate_loss_drops_tail_and_counts():
    """Truncation removes the lost lines and reports their count."""
    frame = _frame(n_lines=8, lost_tail=3)
    kept, n_lost = truncate_loss(frame, detect_line_loss(frame))
    assert n_lost == 3
    assert kept.shape == (5, 6)


@pytest.mark.unit
def test_truncate_loss_noop_without_loss():
    """A clean frame is returned unchanged with zero loss."""
    frame = _frame()
    kept, n_lost = truncate_loss(frame, detect_line_loss(frame))
    assert n_lost == 0
    assert kept.shape == frame.shape


# --------------------------------------------------------------------------- #
# Legality (REQ-F-L0-03)                                                       #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_check_legality_passes_for_valid_frames():
    """A valid frame set passes legality."""
    check_legality({"B02": _frame()}, L0DecodeParams())


@pytest.mark.unit
def test_check_legality_rejects_empty_frame_set():
    """An L0c with no decoded bands is rejected."""
    with pytest.raises(InputValidationError, match="no decoded bands"):
        check_legality({}, L0DecodeParams())


@pytest.mark.unit
def test_check_legality_rejects_out_of_range_dn():
    """A DN above the bit-depth range is rejected."""
    frame = _frame()
    frame[0, 0] = 9000  # > 4095 for 12-bit
    with pytest.raises(InputValidationError, match=r"outside \[0, 4095\]"):
        check_legality({"B02": frame}, L0DecodeParams(bit_depth=12))


@pytest.mark.unit
def test_check_legality_rejects_excess_line_loss():
    """Line loss beyond max_lost_fraction is rejected."""
    frame = _frame(n_lines=10, lost_tail=6)
    with pytest.raises(InputValidationError, match="exceeds"):
        check_legality({"B02": frame}, L0DecodeParams(max_lost_fraction=0.4))


# --------------------------------------------------------------------------- #
# Initial QA                                                                   #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_initial_qa_flags_fill_value():
    """Fill-value pixels are flagged NO_DATA."""
    frame = _frame()
    frame[2, 3] = 0
    qa = initial_qa(frame, L0DecodeParams(fill_value=0))
    assert qa[2, 3] & int(QAFlag.NO_DATA)
    assert qa[0, 0] == 0


@pytest.mark.unit
def test_initial_qa_flags_interior_zero_line():
    """A wholly-zero interior line is flagged NO_DATA across its width."""
    frame = _frame(n_lines=6)
    frame[3, :] = 0
    qa = initial_qa(frame, L0DecodeParams())
    assert np.all(qa[3, :] & int(QAFlag.NO_DATA))
    assert not qa[0, :].any()


# --------------------------------------------------------------------------- #
# Private decode body                                                          #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_decode_source_packets_is_private_impl():
    """The on-wire decode body fail-stops (sensor-private [impl], absent here)."""
    with pytest.raises(L0DecodeError, match="sensor-private"):
        decode_source_packets(object(), object())
