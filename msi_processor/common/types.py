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

"""Shared, CPM-free core data structures (SDD <5.4.1>, <5.5>).

These types are deliberately framework-independent (no ``eopf`` / no I/O) so
that the pure algorithmic cores can be unit-tested off-platform (REQ-D-03,
REQ-PORT-03). They mirror the element-level definitions of SDD <5.5>.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt

__all__ = ["QAFlag", "BandImage", "BandStack"]


class QAFlag(enum.IntFlag):
    """Per-pixel quality bit registry (SDD <5.4.1>, ICD <5.3.3>E).

    Flags are OR-accumulated only (monotone propagation, REQ-F-QA-02); the
    initial value of a QA mask is ``0``. This is the single source of truth
    mirrored by ``C-COM-QAFLAG``.
    """

    NO_DATA = 1 << 0  # fill / no-data
    LOST_PACKET = 1 << 1  # line/packet loss (REQ-F-L0-02)
    SATURATED = 1 << 2  # at/above saturation (REQ-F-RAD-04)
    DEFECTIVE = 1 << 3  # bad pixel replaced (REQ-F-RAD-03)
    COREG_FAIL = 1 << 4  # co-registration failure (REQ-F-COR-03)
    CLOUD = 1 << 5  # cloud (REQ-F-ATM-03)
    CLOUD_SHADOW = 1 << 6  # cloud shadow (REQ-F-ATM-03)
    # bit 7 reserved [TBC@CDR]


@dataclass(frozen=True)
class BandImage:
    """One band in a generic 2-D geometry (SDD <5.4.1>).

    Parameters
    ----------
    data:
        Pixel array, dtype ``float32`` (working) or ``uint16`` (DN/packed),
        dims ``(line|y, detector|x)``. Valid range ``[0, 2**bit_depth - 1]``
        for DN or ``[0.0, 1.0]`` for reflectance.
    qa:
        ``uint16`` :class:`QAFlag` bitmask, same shape as ``data``; initial
        value ``0``.
    name:
        Band id, from ``profile.bands[].name`` (e.g. ``"b2"``).
    geom:
        Geometry tag, one of ``"focal_plane" | "instrument" | "map"``.
    """

    data: npt.NDArray[Any]
    qa: npt.NDArray[np.uint16]
    name: str
    geom: str = "focal_plane"


@dataclass(frozen=True)
class BandStack:
    """The inter-stage payload of the pure cores (SDD <5.4.1>, IF-CORE-01).

    One :class:`BandImage` entry per band, plus a free-form ``meta`` mapping
    carrying acquisition/telemetry and per-stage parameters echoed for
    provenance (never private calibration values).
    """

    bands: dict[str, BandImage]
    meta: dict[str, object] = field(default_factory=dict)

    @property
    def band_names(self) -> list[str]:
        """Return the band ids in insertion order."""
        return list(self.bands.keys())
