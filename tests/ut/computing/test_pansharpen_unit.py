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

"""Unit tests for the pan-sharpening EOProcessingUnit wrapper (C-PU-PAN).

These also prove the computing-model JSON loads under eopf 2.8.1 (loaded at
class-definition time), that the stage declares its mandatory ``l2a`` input with
no ADFs, and that an in-memory L2A BOA product round-trips through the wrapper to
the optional ``DPM-PR-L2A-PAN`` derivative with fused bands and per-band
spectral-fidelity QA. The default-off gate and the ``[impl]`` fusion methods are
verified to fail-stop.
"""

import numpy as np
import pytest
from eopf.product import EOGroup, EOProduct, EOVariable

from msi_processor.computing.pansharpen.unit import PansharpenUnit
from msi_processor.exceptions.errors import InputValidationError, PansharpenError

# Known crop geometry of the synthetic feature-rich scene (PAN / MS offset).
_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 8
_TY = 5


def _textured_scene(seed: int, size: int = _BASE, n_blobs: int = 150) -> np.ndarray:
    """A deterministic, feature-rich reflectance field (SIFT-friendly, in [0, 1])."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    field = np.full((size, size), 0.1)
    for _ in range(n_blobs):
        cy = rng.uniform(0, size)
        cx = rng.uniform(0, size)
        sigma = rng.uniform(1.5, 4.0)
        amp = rng.uniform(0.1, 0.6)
        field += amp * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma * sigma)))
    return np.clip(field, 0.0, 1.0).astype(np.float32)


def _pan_and_ms_band(seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(pan, ms_band)`` cropped with the known ``(_TX, _TY)`` offset."""
    base = _textured_scene(seed)
    r0, r1 = _ORIGIN, _ORIGIN + _WIN
    my0, my1 = _ORIGIN + _TY, _ORIGIN + _TY + _WIN
    mx0, mx1 = _ORIGIN + _TX, _ORIGIN + _TX + _WIN
    pan = base[r0:r1, r0:r1].copy()
    ms = base[my0:my1, mx0:mx1].copy()
    return pan, ms


def _l2a(pan_band: str = "PAN") -> EOProduct:
    """Build a minimal L2A product: BOA reflectance MS bands + a PAN band."""
    pan, ms_b1 = _pan_and_ms_band(seed=1)
    _, ms_b2 = _pan_and_ms_band(seed=2)
    bands = {"B02": ms_b1, "B03": ms_b2, pan_band: pan}
    product = EOProduct("L2A.TEST")
    product["measurements"] = EOGroup()
    for name, data in bands.items():
        product[f"measurements/reflectance/{name}"] = EOVariable(data=data, dims=("y", "x"))
    return product


@pytest.mark.unit
def test_model_declares_input_and_no_adfs():
    """The computing-model JSON loads and declares l2a input with no ADFs."""
    unit = PansharpenUnit("pan")
    assert unit.get_mandatory_input_list("nominal") == ["l2a"]
    assert unit.get_mandatory_adf_list("nominal") == []
    assert unit.PROCESSOR_LEVEL == "L2A"
    assert unit.PROCESSOR_NAME == "msi_pansharpen"


@pytest.mark.unit
def test_run_emits_pan_derivative():
    """The unit fuses the MS bands with PAN and emits a sharpened derivative."""
    unit = PansharpenUnit("pan")
    outputs = unit.run({"l2a": _l2a()}, pan_band="PAN")
    assert set(outputs) == {"pan"}
    product = outputs["pan"]
    assert product.name == "L2A.TEST_L2A_PAN"
    # The PAN band is consumed, not re-emitted; only the MS bands are sharpened.
    fused = product["measurements/reflectance"]
    assert set(fused) == {"B02", "B03"}
    for band in ("B02", "B03"):
        arr = np.asarray(product[f"measurements/reflectance/{band}"].data)
        assert arr.shape == (_WIN, _WIN)
        assert arr.dtype == np.float32
        assert np.all((arr >= 0.0) & (arr <= 1.0))


@pytest.mark.unit
def test_run_records_spectral_fidelity_qa():
    """Per-band spectral fidelity is written to QA and provenance (REQ-F-PAN-02)."""
    unit = PansharpenUnit("pan")
    product = unit.run({"l2a": _l2a()}, pan_band="PAN")["pan"]
    for band in ("B02", "B03"):
        fidelity = np.asarray(product[f"quality/spectral_fidelity/{band}"].data)
        assert fidelity.shape == (1,)
        assert -1.0 <= float(fidelity[0]) <= 1.0
    meta = product.attrs["other_metadata"]["quality"]["spectral_fidelity"]
    assert set(meta) == {"B02", "B03"}


@pytest.mark.unit
def test_fidelity_budget_flags_low_bands():
    """A high budget flags bands below it without failing the stage."""
    unit = PansharpenUnit("pan")
    product = unit.run({"l2a": _l2a()}, pan_band="PAN", fidelity_budget=1.5)["pan"]
    flagged = product.attrs["other_metadata"]["quality"]["bands_below_fidelity_budget"]
    assert set(flagged) == {"B02", "B03"}  # nothing can exceed a 1.5 budget


@pytest.mark.unit
def test_disabled_stage_fails_stop():
    """enabled=false fail-stops rather than emitting a product (CR-4 default-off)."""
    unit = PansharpenUnit("pan")
    with pytest.raises(PansharpenError, match="enabled=false"):
        unit.run({"l2a": _l2a()}, pan_band="PAN", enabled=False)


@pytest.mark.unit
def test_missing_pan_band_param_fails():
    """A run without a pan_band parameter is a fail-stop."""
    unit = PansharpenUnit("pan")
    with pytest.raises(PansharpenError, match="requires a 'pan_band'"):
        unit.run({"l2a": _l2a()})


@pytest.mark.unit
def test_pan_band_absent_from_product_fails():
    """Naming a PAN band that is not in the L2A reflectance fail-stops."""
    unit = PansharpenUnit("pan")
    with pytest.raises(PansharpenError, match="absent from the L2A reflectance"):
        unit.run({"l2a": _l2a()}, pan_band="B11")


@pytest.mark.unit
def test_no_ms_bands_after_removing_pan_fails():
    """A product whose only band is the PAN band has nothing to sharpen."""
    product = EOProduct("L2A.ONLYPAN")
    product["measurements"] = EOGroup()
    pan, _ = _pan_and_ms_band(seed=1)
    product["measurements/reflectance/PAN"] = EOVariable(data=pan, dims=("y", "x"))
    unit = PansharpenUnit("pan")
    with pytest.raises(PansharpenError, match="No MS bands"):
        unit.run({"l2a": product}, pan_band="PAN")


@pytest.mark.unit
def test_missing_input_fails():
    """A run without the l2a input is rejected."""
    unit = PansharpenUnit("pan")
    with pytest.raises(InputValidationError, match="Missing mandatory input 'l2a'"):
        unit.run({}, pan_band="PAN")


@pytest.mark.unit
def test_unknown_mode_fails():
    """An unsupported processing mode is rejected."""
    unit = PansharpenUnit("pan")
    with pytest.raises(InputValidationError, match="Unknown pansharpen mode"):
        unit.run({"l2a": _l2a()}, mode="weird", pan_band="PAN")


@pytest.mark.unit
def test_unknown_method_fails():
    """An unrecognised fusion method name is rejected at the wrapper."""
    unit = PansharpenUnit("pan")
    with pytest.raises(InputValidationError, match="Unknown fusion method"):
        unit.run({"l2a": _l2a()}, pan_band="PAN", method="nonsense")


@pytest.mark.unit
def test_component_substitution_method_is_impl():
    """A valid-but-deferred method ([impl]) fail-stops from the core."""
    unit = PansharpenUnit("pan")
    with pytest.raises(PansharpenError, match="not implemented"):
        unit.run({"l2a": _l2a()}, pan_band="PAN", method="gs")


@pytest.mark.unit
def test_missing_reflectance_group_fails():
    """An L2A product without a reflectance group is rejected."""
    product = EOProduct("L2A.EMPTY")
    product["measurements"] = EOGroup()
    unit = PansharpenUnit("pan")
    with pytest.raises(InputValidationError, match="no 'measurements/reflectance' group"):
        unit.run({"l2a": product}, pan_band="PAN")
