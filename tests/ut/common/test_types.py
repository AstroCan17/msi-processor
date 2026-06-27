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

"""Unit tests for the shared core data structures (SDD <5.4.1>)."""

import numpy as np
import pytest

from msi_processor.common.types import BandImage, BandStack, QAFlag


@pytest.mark.unit
def test_qaflag_bit_positions():
    """QA bits match the registry of SDD <5.4.1> / ICD <5.3.3>E."""
    assert int(QAFlag.NO_DATA) == 1
    assert int(QAFlag.LOST_PACKET) == 2
    assert int(QAFlag.SATURATED) == 4
    assert int(QAFlag.DEFECTIVE) == 8
    assert int(QAFlag.COREG_FAIL) == 16
    assert int(QAFlag.CLOUD) == 32
    assert int(QAFlag.CLOUD_SHADOW) == 64


@pytest.mark.unit
def test_qaflag_or_accumulation_is_monotone():
    """OR-accumulation preserves previously set bits (REQ-F-QA-02)."""
    mask = QAFlag(0)
    mask |= QAFlag.SATURATED
    mask |= QAFlag.DEFECTIVE
    assert QAFlag.SATURATED in mask
    assert QAFlag.DEFECTIVE in mask
    assert QAFlag.CLOUD not in mask
    assert int(mask) == int(QAFlag.SATURATED) | int(QAFlag.DEFECTIVE)


@pytest.mark.unit
def test_band_image_defaults_to_focal_plane():
    """A BandImage defaults to focal-plane geometry."""
    data = np.zeros((2, 3), dtype=np.float32)
    qa = np.zeros((2, 3), dtype=np.uint16)
    image = BandImage(data=data, qa=qa, name="b2")
    assert image.geom == "focal_plane"
    assert image.name == "b2"
    assert image.data.shape == (2, 3)


@pytest.mark.unit
def test_band_image_is_frozen():
    """BandImage is immutable (frozen dataclass)."""
    image = BandImage(
        data=np.zeros((1, 1), dtype=np.float32),
        qa=np.zeros((1, 1), dtype=np.uint16),
        name="b2",
    )
    with pytest.raises(AttributeError):
        image.name = "b3"  # type: ignore[misc]


@pytest.mark.unit
def test_band_stack_band_names_preserve_order():
    """BandStack.band_names returns ids in insertion order."""
    bands = {
        name: BandImage(
            data=np.zeros((1, 1), dtype=np.float32),
            qa=np.zeros((1, 1), dtype=np.uint16),
            name=name,
        )
        for name in ("b4", "b2", "b3")
    }
    stack = BandStack(bands=bands)
    assert stack.band_names == ["b4", "b2", "b3"]
    assert stack.meta == {}
