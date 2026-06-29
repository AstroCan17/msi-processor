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

"""Unit tests for the Level-0 decode EOProcessingUnit wrapper (C-PU-L0).

These prove the computing-model JSON loads under eopf 2.8.1 (l0c input, no
ADFs, L1A level), that an open-container L0c round-trips to an L1A product with
detector DN + passed-through telemetry + seeded QA, that trailing line loss is
truncated (and telemetry follows), and that the undecoded on-wire form
fail-stops on the sensor-private decode body.
"""

import numpy as np
import pytest
from eopf.product import EOGroup, EOProduct, EOVariable

from msi_processor.computing.l0_decode.unit import L0DecodeUnit
from msi_processor.exceptions.errors import InputValidationError, L0DecodeError

_DIMS = ("line", "detector")


def _frame(n_lines: int = 8, n_det: int = 6, lost_tail: int = 0, seed: int = 0) -> np.ndarray:
    """A DN frame in [1, 4095] with an optional all-zero trailing block."""
    rng = np.random.default_rng(seed)
    arr = rng.integers(1, 4096, size=(n_lines, n_det)).astype(np.uint16)
    if lost_tail:
        start = n_lines - lost_tail
        arr[start:] = 0
    return arr


def _l0c(n_lines: int = 8, lost_tail: int = 0, with_conditions: bool = True) -> EOProduct:
    """Build a synthetic open-container L0c (decoded detector frames + telemetry)."""
    product = EOProduct("L0C.TEST")
    product["measurements"] = EOGroup()
    product["measurements/detector/B02"] = EOVariable(data=_frame(n_lines, lost_tail=lost_tail, seed=1), dims=_DIMS)
    product["measurements/detector/B03"] = EOVariable(data=_frame(n_lines, lost_tail=lost_tail, seed=2), dims=_DIMS)
    if with_conditions:
        product["conditions"] = EOGroup()
        product["conditions/time/line_time"] = EOVariable(data=np.arange(n_lines, dtype=np.float64), dims=("line",))
        product["conditions/orbit/position"] = EOVariable(
            data=np.zeros((n_lines, 3), dtype=np.float64), dims=("line", "xyz")
        )
        product["conditions/attitude/quaternion"] = EOVariable(
            data=np.zeros((n_lines, 4), dtype=np.float64), dims=("line", "quat")
        )
    return product


@pytest.mark.unit
def test_model_declares_input_and_no_adfs():
    """The computing-model JSON loads and declares l0c input with no ADFs."""
    unit = L0DecodeUnit("l0")
    assert unit.get_mandatory_input_list("default") == ["l0c"]
    assert unit.get_mandatory_adf_list("default") == []
    assert unit.PROCESSOR_LEVEL == "L1A"
    assert unit.PROCESSOR_NAME == "msi_l0_decode"


@pytest.mark.unit
def test_run_emits_l1a_product():
    """An open-container L0c decodes to an L1A product with detector DN + QA."""
    unit = L0DecodeUnit("l0")
    outputs = unit.run({"l0c": _l0c()})
    assert set(outputs) == {"l1a"}
    product = outputs["l1a"]
    assert product.name == "L0C.TEST_L1A"
    detector = product["measurements/detector"]
    assert set(detector) == {"B02", "B03"}
    for band in ("B02", "B03"):
        arr = np.asarray(product[f"measurements/detector/{band}"].data)
        assert arr.shape == (8, 6)
        assert arr.dtype == np.uint16
        qa = np.asarray(product[f"quality/l0_flags/{band}"].data)
        assert qa.shape == (8, 6)


@pytest.mark.unit
def test_run_truncates_line_loss_and_records_it():
    """Trailing lost lines are truncated and counted in provenance."""
    unit = L0DecodeUnit("l0")
    product = unit.run({"l0c": _l0c(n_lines=8, lost_tail=3)})["l1a"]
    assert np.asarray(product["measurements/detector/B02"].data).shape == (5, 6)
    lost = product.attrs["other_metadata"]["quality"]["lines_lost"]
    assert lost["B02"] == 3 and lost["B03"] == 3


@pytest.mark.unit
def test_run_passes_through_and_truncates_telemetry():
    """Acquisition telemetry is carried and per-line arrays follow the truncation."""
    unit = L0DecodeUnit("l0")
    product = unit.run({"l0c": _l0c(n_lines=8, lost_tail=3)})["l1a"]
    assert np.asarray(product["conditions/time/line_time"].data).shape == (5,)
    assert np.asarray(product["conditions/orbit/position"].data).shape == (5, 3)
    assert np.asarray(product["conditions/attitude/quaternion"].data).shape == (5, 4)


@pytest.mark.unit
def test_run_keeps_full_telemetry_without_loss():
    """Without loss the telemetry is passed through at full length."""
    unit = L0DecodeUnit("l0")
    product = unit.run({"l0c": _l0c(n_lines=8)})["l1a"]
    assert np.asarray(product["conditions/time/line_time"].data).shape == (8,)


@pytest.mark.unit
def test_undecoded_l0c_fail_stops_on_private_decode():
    """An L0c without decoded detector frames routes to the private [impl] decode."""
    raw = EOProduct("L0C.RAW")
    raw["source_packets"] = EOGroup()
    unit = L0DecodeUnit("l0")
    with pytest.raises(L0DecodeError, match="sensor-private"):
        unit.run({"l0c": raw})


@pytest.mark.unit
def test_missing_input_fails():
    """A run without the l0c input is rejected."""
    unit = L0DecodeUnit("l0")
    with pytest.raises(InputValidationError, match="Missing mandatory input 'l0c'"):
        unit.run({})


@pytest.mark.unit
def test_unknown_mode_fails():
    """An unsupported processing mode is rejected."""
    unit = L0DecodeUnit("l0")
    with pytest.raises(InputValidationError, match="Unknown l0_decode mode"):
        unit.run({"l0c": _l0c()}, mode="weird")


@pytest.mark.unit
def test_out_of_range_dn_fails_legality():
    """A decoded frame with an out-of-range DN fails Level-0 legality."""
    product = _l0c()
    bad = _frame(seed=3)
    bad[0, 0] = 9000  # > 4095 for 12-bit
    product["measurements/detector/B02"] = EOVariable(data=bad, dims=_DIMS)
    unit = L0DecodeUnit("l0")
    with pytest.raises(InputValidationError, match=r"outside \[0, 4095\]"):
        unit.run({"l0c": product})
