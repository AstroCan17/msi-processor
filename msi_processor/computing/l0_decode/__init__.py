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

"""Level-0 decode stage (C-PU-L0; DPM-M-L0; ALG-L0-DEC, ALG-L0-LOSS).

Turns the downlinked Level-0 (L0c) product into L1A: detector DN in focal-plane
geometry, passed-through acquisition telemetry (timing, orbit, attitude), and
seeded QA, with deterministic trailing line-loss truncation. The stage is a
pure :mod:`~msi_processor.computing.l0_decode.core` plus a thin
:class:`~msi_processor.computing.l0_decode.unit.L0DecodeUnit` wrapper. The
sensor-private source-packet decode body is held outside this public
distribution; the public path operates on the documented open-container sample
layout.
"""

from msi_processor.computing.l0_decode.core import (
    L0DecodeParams,
    check_legality,
    decode_source_packets,
    detect_line_loss,
    initial_qa,
    truncate_loss,
)
from msi_processor.computing.l0_decode.unit import L0DecodeUnit

__all__ = [
    "L0DecodeParams",
    "detect_line_loss",
    "truncate_loss",
    "check_legality",
    "initial_qa",
    "decode_source_packets",
    "L0DecodeUnit",
]
