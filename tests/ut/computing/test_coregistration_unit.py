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

"""Unit tests for the co-registration EOProcessingUnit wrapper (C-PU-COR).

These also prove the computing-model JSON loads under eopf 2.8.1 (the model is
loaded at class-definition time), that the stage declares its mandatory input and
no ADFs, and that the in-memory L1B EOProduct round-trips through the wrapper.
"""

import numpy as np
import pytest
from eopf.product import EOGroup, EOProduct, EOVariable
from numpy.testing import assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.coregistration.unit import CoregistrationUnit
from msi_processor.exceptions.errors import CoregistrationError, InputValidationError

_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 8
_TY = 5


def _textured_scene(seed: int, size: int = _BASE, n_blobs: int = 150) -> np.ndarray:
    """A deterministic, feature-rich field of Gaussian blobs (SIFT-friendly)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    field = np.full((size, size), 200.0)
    for _ in range(n_blobs):
        cy = rng.uniform(0, size)
        cx = rng.uniform(0, size)
        sigma = rng.uniform(1.5, 4.0)
        amp = rng.uniform(200.0, 1500.0)
        field += amp * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma * sigma)))
    return field.astype(np.float32)


def _shifted_pair(seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(reference, band)`` cropped from one scene with offset ``(_TX, _TY)``."""
    base = _textured_scene(seed)
    r0, r1 = _ORIGIN, _ORIGIN + _WIN
    by0, by1 = _ORIGIN + _TY, _ORIGIN + _TY + _WIN
    bx0, bx1 = _ORIGIN + _TX, _ORIGIN + _TX + _WIN
    reference = base[r0:r1, r0:r1].copy()
    band = base[by0:by1, bx0:bx1].copy()
    return reference, band


def _l1b(
    radiance: dict[str, np.ndarray],
    masks: dict[str, np.ndarray] | None = None,
    reflectance: dict[str, np.ndarray] | None = None,
) -> EOProduct:
    """Build a minimal L1B product: radiance bands (+ optional reflectance / QA)."""
    product = EOProduct("L1B.TEST")
    product["measurements"] = EOGroup()
    for name, data in radiance.items():
        product[f"measurements/radiance/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    if reflectance:
        for name, data in reflectance.items():
            product[f"measurements/reflectance/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    if masks:
        product["quality"] = EOGroup()
        for name, data in masks.items():
            product[f"quality/mask/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    return product


@pytest.mark.unit
def test_computing_model_is_loaded():
    """The CPM computing-model JSON declares the mandatory input and no ADFs."""
    model = CoregistrationUnit.processing_model()
    assert model is not None
    assert set(CoregistrationUnit.get_available_modes()) == {"default"}
    assert CoregistrationUnit.get_mandatory_input_list("default") == ["l1b"]
    assert CoregistrationUnit.get_mandatory_adf_list("default") == []


@pytest.mark.unit
def test_coregisters_shifted_band():
    """A shifted band is aligned to the reference; the stack shares the ref grid."""
    reference, band = _shifted_pair()
    outputs = CoregistrationUnit().run(
        {"l1b": _l1b({"ref": reference, "b3": band})},
        reference_band="ref",
        seed=0,
    )
    assert set(outputs) == {"cor"}
    cor = outputs["cor"]
    warped = np.asarray(cor["measurements/radiance/b3"].data)
    assert warped.shape == reference.shape

    interior = (slice(_TY + 3, _WIN - 3), slice(_TX + 3, _WIN - 3))
    err_before = np.abs(band[interior].astype(float) - reference[interior].astype(float)).mean()
    err_after = np.abs(warped[interior].astype(float) - reference[interior].astype(float)).mean()
    assert err_after < 0.05 * err_before


@pytest.mark.unit
def test_reference_band_passes_through_unchanged():
    """The reference band is emitted untouched."""
    reference, band = _shifted_pair()
    outputs = CoregistrationUnit().run(
        {"l1b": _l1b({"ref": reference, "b3": band})},
        reference_band="ref",
    )
    assert_array_equal(np.asarray(outputs["cor"]["measurements/radiance/ref"].data), reference)


@pytest.mark.unit
def test_out_of_source_border_flagged_no_data():
    """Pixels with no source coverage after warping are flagged NO_DATA."""
    reference, band = _shifted_pair()
    outputs = CoregistrationUnit().run(
        {"l1b": _l1b({"ref": reference, "b3": band})},
        reference_band="ref",
    )
    qa = np.asarray(outputs["cor"]["quality/mask/b3"].data)
    # The (_TX, _TY) border has no source after the translation warp -> NO_DATA.
    assert qa[0, 0] & int(QAFlag.NO_DATA)
    # The covered interior carries no co-registration no-data flag.
    assert qa[_WIN // 2, _WIN // 2] == 0
    # The reference band is fully covered.
    assert_array_equal(np.asarray(outputs["cor"]["quality/mask/ref"].data), np.zeros((_WIN, _WIN), np.uint16))


@pytest.mark.unit
def test_upstream_qa_propagated_and_warped():
    """Upstream QA on a band is warped with it and OR-accumulated."""
    reference, band = _shifted_pair()
    mask = np.zeros((_WIN, _WIN), dtype=np.uint16)
    mask[_WIN // 2, _WIN // 2] = np.uint16(QAFlag.DEFECTIVE)
    outputs = CoregistrationUnit().run(
        {"l1b": _l1b({"ref": reference, "b3": band}, masks={"b3": mask})},
        reference_band="ref",
    )
    qa = np.asarray(outputs["cor"]["quality/mask/b3"].data)
    # The DEFECTIVE flag survives the warp (translated by the homography).
    assert int(qa[_WIN // 2 + _TY, _WIN // 2 + _TX]) & int(QAFlag.DEFECTIVE)


@pytest.mark.unit
def test_reflectance_warped_with_same_homography():
    """When TOA reflectance is present it is co-registered with the radiance band."""
    reference, band = _shifted_pair()
    refl = band / 4096.0
    outputs = CoregistrationUnit().run(
        {"l1b": _l1b({"ref": reference, "b3": band}, reflectance={"b3": refl})},
        reference_band="ref",
    )
    cor = outputs["cor"]
    warped_refl = np.asarray(cor["measurements/radiance/b3"].data) / 4096.0
    emitted_refl = np.asarray(cor["measurements/reflectance/b3"].data)
    assert emitted_refl.shape == reference.shape
    # Reflectance and radiance of the same band share the homography -> identical
    # geometry after warping.
    assert_array_equal(emitted_refl, warped_refl)


@pytest.mark.unit
def test_fail_stop_on_unmatchable_band():
    """A featureless band fails the keypoint gate -> CoregistrationError (fail-stop)."""
    reference, _ = _shifted_pair()
    flat = np.full((_WIN, _WIN), 700.0, dtype=np.float32)
    with pytest.raises(CoregistrationError):
        CoregistrationUnit().run(
            {"l1b": _l1b({"ref": reference, "b3": flat})},
            reference_band="ref",
        )


@pytest.mark.unit
def test_missing_input_raises():
    """A missing 'l1b' input raises InputValidationError."""
    with pytest.raises(InputValidationError):
        CoregistrationUnit().run({}, reference_band="ref")


@pytest.mark.unit
def test_missing_reference_band_param_raises():
    """The mandatory reference_band parameter must be supplied."""
    reference, band = _shifted_pair()
    with pytest.raises(InputValidationError):
        CoregistrationUnit().run({"l1b": _l1b({"ref": reference, "b3": band})})


@pytest.mark.unit
def test_reference_band_not_in_product_raises():
    """A reference_band absent from the radiance bands is rejected."""
    reference, band = _shifted_pair()
    with pytest.raises(InputValidationError):
        CoregistrationUnit().run(
            {"l1b": _l1b({"ref": reference, "b3": band})},
            reference_band="missing",
        )


@pytest.mark.unit
def test_unknown_mode_raises():
    """An unsupported mode is rejected before processing."""
    reference, band = _shifted_pair()
    with pytest.raises(InputValidationError):
        CoregistrationUnit().run(
            {"l1b": _l1b({"ref": reference, "b3": band})},
            reference_band="ref",
            mode="bogus",
        )
