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

"""Unit tests for the enhancement EOProcessingUnit wrapper (C-PU-ENH).

These also prove the computing-model JSON loads under eopf 2.8.1 (the model is
loaded at class-definition time) and that mandatory inputs/ADFs are declared via
that model. The output product keeps the radiometric product shape so it can
feed the downstream TOA unit.
"""

from typing import Any

import numpy as np
import pytest
from eopf.computing.abstract import AuxiliaryDataFile
from eopf.product import EOGroup, EOProduct, EOVariable
from numpy.testing import assert_allclose, assert_array_equal

from msi_processor.common.types import QAFlag
from msi_processor.computing.enhancement.unit import EnhancementUnit
from msi_processor.exceptions.errors import AdfResolutionError, InputValidationError

_IDENTITY = np.array([[1.0]], dtype=np.float32)
# Normalised Laplacian-sharpening kernel (sum == 1) used as a PSF-derived MTFC
# deconvolution kernel stand-in.
_SHARPEN = np.array([[0.0, -1.0, 0.0], [-1.0, 5.0, -1.0], [0.0, -1.0, 0.0]], dtype=np.float32)


def _rad(bands: dict[str, np.ndarray], masks: dict[str, np.ndarray] | None = None) -> EOProduct:
    """Build a minimal radiometric product: detector bands (+ optional QA)."""
    product = EOProduct("RAD.TEST")
    product["measurements"] = EOGroup()
    for name, data in bands.items():
        product[f"measurements/detector/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    if masks:
        product["quality"] = EOGroup()
        for name, data in masks.items():
            product[f"quality/mask/{name}"] = EOVariable(data=data, dims=("line", "detector"))
    return product


def _adf(name: str, data: Any) -> AuxiliaryDataFile:
    """Build an ADF carrying its content in data_ptr (this-increment convention)."""
    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


def _psf(kernels: dict[str, Any]) -> AuxiliaryDataFile:
    """Build a psf ADF (per-band MTFC deconvolution kernel)."""
    return _adf("psf", {"kernel": kernels})


@pytest.mark.unit
def test_computing_model_is_loaded():
    """The CPM computing-model JSON declares the mandatory input/ADFs."""
    model = EnhancementUnit.processing_model()
    assert model is not None
    assert set(EnhancementUnit.get_available_modes()) == {"default"}
    assert EnhancementUnit.get_mandatory_input_list("default") == ["rad"]
    assert EnhancementUnit.get_mandatory_adf_list("default") == ["psf"]


@pytest.mark.unit
def test_identity_kernel_no_denoise_passthrough():
    """Identity MTFC kernel + no denoise -> output DN equals input DN, QA zero."""
    dn = np.array([[10, 20], [30, 40]], dtype=np.uint16)
    outputs = EnhancementUnit().run(
        {"rad": _rad({"b2": dn})},
        adfs={"psf": _psf({"b2": _IDENTITY})},
        denoise_method="none",
    )
    assert set(outputs) == {"enh"}
    enh = outputs["enh"]
    result = np.asarray(enh["measurements/detector/b2"].data)
    assert_array_equal(result, dn)
    assert result.dtype == np.uint16
    assert_array_equal(np.asarray(enh["quality/mask/b2"].data), np.zeros((2, 2), dtype=np.uint16))


@pytest.mark.unit
def test_mtfc_always_runs_and_preserves_mean():
    """The stage always applies MTFC; a unit-DC-gain kernel conserves the mean."""
    # A smooth, mid-range, periodic field: MTFC boosts its amplitude (data
    # changes) but the sharpened result stays inside the valid DN range, so no
    # clipping confounds the radiometry (unit-DC-gain kernel -> mean conserved).
    yy, xx = np.mgrid[0:32, 0:24]
    field = 2000.0 + 200.0 * np.sin(2.0 * np.pi * xx / 24.0) + 150.0 * np.cos(2.0 * np.pi * yy / 32.0)
    dn = field.astype(np.uint16)
    outputs = EnhancementUnit().run(
        {"rad": _rad({"b2": dn})},
        adfs={"psf": _psf({"b2": _SHARPEN})},
        denoise_method="none",
    )
    result = np.asarray(outputs["enh"]["measurements/detector/b2"].data)
    # MTFC ran (sharpening changed the data), staying within the valid DN range ...
    assert not np.array_equal(result, dn)
    assert result.min() >= 0 and result.max() <= 4095
    # ... while the band mean is conserved within integer-rounding tolerance.
    assert_allclose(result.mean(), dn.mean(), atol=1.0)


@pytest.mark.unit
def test_denoise_then_mtfc_multiband():
    """A configurable denoiser runs before the mandatory MTFC across bands."""
    rng = np.random.default_rng(5)
    bands = {
        "b2": rng.integers(200, 800, size=(32, 24)).astype(np.uint16),
        "b3": rng.integers(200, 800, size=(32, 24)).astype(np.uint16),
    }
    outputs = EnhancementUnit().run(
        {"rad": _rad(bands)},
        adfs={"psf": _psf({"b2": _IDENTITY, "b3": _IDENTITY})},
        denoise_method="gaussian",
        denoise_params={"sigma": 2.0},
    )
    enh = outputs["enh"]
    for band, dn in bands.items():
        result = np.asarray(enh[f"measurements/detector/{band}"].data)
        assert result.shape == dn.shape
        assert result.dtype == np.uint16
        # denoising reduced the high-frequency content versus the raw DN
        assert np.std(result.astype(np.float64)) <= np.std(dn.astype(np.float64))


@pytest.mark.unit
def test_fft_dark_denoise_uses_dark_adf():
    """The fft_dark denoiser consumes the optional dark ADF frame per band."""
    base = np.full((16, 16), 500, dtype=np.uint16)
    dark = np.random.default_rng(9).integers(0, 40, size=(16, 16)).astype(np.float32)
    noisy = (base.astype(np.float32) + dark).astype(np.uint16)
    outputs = EnhancementUnit().run(
        {"rad": _rad({"b2": noisy})},
        adfs={
            "psf": _psf({"b2": _IDENTITY}),
            "dark": _adf("dark", {"frame": {"b2": dark}}),
        },
        denoise_method="fft_dark",
    )
    result = np.asarray(outputs["enh"]["measurements/detector/b2"].data).astype(np.float64)
    # dark subtraction recovers the flat base (within DN rounding)
    assert_allclose(result, base.astype(np.float64), atol=1.0)


@pytest.mark.unit
def test_upstream_qa_is_propagated():
    """Upstream quality/mask flags are OR-accumulated into the output QA."""
    dn = np.array([[10, 20]], dtype=np.uint16)
    mask = np.array([[int(QAFlag.DEFECTIVE), 0]], dtype=np.uint16)
    outputs = EnhancementUnit().run(
        {"rad": _rad({"b2": dn}, masks={"b2": mask})},
        adfs={"psf": _psf({"b2": _IDENTITY})},
        denoise_method="none",
    )
    assert_array_equal(
        np.asarray(outputs["enh"]["quality/mask/b2"].data),
        [[int(QAFlag.DEFECTIVE), 0]],
    )


@pytest.mark.unit
def test_saturation_flagged_on_overshoot():
    """MTFC overshoot above the DN ceiling is flagged SATURATED and clipped."""
    dn = np.array([[0, 0, 0], [0, 4095, 0], [0, 0, 0]], dtype=np.uint16)
    outputs = EnhancementUnit().run(
        {"rad": _rad({"b2": dn})},
        adfs={"psf": _psf({"b2": _SHARPEN})},
        denoise_method="none",
        bit_depth=12,
    )
    enh = outputs["enh"]
    result = np.asarray(enh["measurements/detector/b2"].data)
    qa = np.asarray(enh["quality/mask/b2"].data)
    assert result.max() <= 4095  # clipped to the ceiling
    assert qa[1, 1] & int(QAFlag.SATURATED)  # the boosted centre saturates


@pytest.mark.unit
def test_missing_input_raises():
    """A missing 'rad' input raises InputValidationError."""
    with pytest.raises(InputValidationError):
        EnhancementUnit().run({}, adfs={"psf": _psf({"b2": _IDENTITY})})


@pytest.mark.unit
def test_missing_psf_adf_raises():
    """The mandatory psf ADF must be present."""
    rad = _rad({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(AdfResolutionError):
        EnhancementUnit().run({"rad": rad}, adfs={})


@pytest.mark.unit
def test_missing_band_kernel_raises():
    """A band without an MTFC kernel raises AdfResolutionError."""
    rad = _rad({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(AdfResolutionError):
        EnhancementUnit().run({"rad": rad}, adfs={"psf": _psf({"b3": _IDENTITY})})


@pytest.mark.unit
def test_fft_dark_without_dark_frame_raises():
    """fft_dark denoise without a dark frame for the band raises AdfResolutionError."""
    rad = _rad({"b2": np.array([[1, 2], [3, 4]], dtype=np.uint16)})
    with pytest.raises(AdfResolutionError):
        EnhancementUnit().run(
            {"rad": rad},
            adfs={"psf": _psf({"b2": _IDENTITY})},
            denoise_method="fft_dark",
        )


@pytest.mark.unit
def test_unknown_denoise_method_raises():
    """An unsupported denoise method is rejected before processing."""
    rad = _rad({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(InputValidationError):
        EnhancementUnit().run(
            {"rad": rad},
            adfs={"psf": _psf({"b2": _IDENTITY})},
            denoise_method="bogus",
        )


@pytest.mark.unit
def test_unknown_mode_raises():
    """An unsupported mode is rejected before processing."""
    rad = _rad({"b2": np.array([[1, 2]], dtype=np.uint16)})
    with pytest.raises(InputValidationError):
        EnhancementUnit().run({"rad": rad}, adfs={"psf": _psf({"b2": _IDENTITY})}, mode="bogus")
