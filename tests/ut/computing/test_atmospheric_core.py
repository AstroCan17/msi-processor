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

"""Unit tests for the atmospheric-correction core (ALG-ATM-PAR/RT/SCM).

The exact 6S BOA inversion and the spectral-threshold scene classifier are
exercised with tiny synthetic arrays and hand-computed expected values; the
``[impl]`` retrieval / RT-engine / ML-classifier bodies are verified to fail-stop.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from msi_processor.computing.atmospheric.core import (
    AtmAux,
    AtmParams,
    RTLut,
    SceneClass,
    SceneGeometry,
    classify_scene,
    classify_scene_ml,
    get_atmospheric_parameters,
    invert_boa,
    resolve_rt_lut,
    retrieve_atmospheric_parameters,
    toa_to_boa,
)
from msi_processor.exceptions.errors import AtmosphericError, InputValidationError


# --------------------------------------------------------------------------- #
# ALG-ATM-RT -- BOA inversion                                                  #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_invert_boa_roundtrips_the_forward_model():
    """invert_boa exactly inverts the 6S forward TOA model rho_BOA -> rho_TOA."""
    rho_atm, t_total, s_alb = 0.05, 0.8, 0.1
    rho_s = np.array([[0.1, 0.2], [0.3, 0.45]], dtype=np.float64)
    # Forward 6S: rho_TOA = rho_atm + T*rho_s / (1 - S*rho_s)
    toa = rho_atm + t_total * rho_s / (1.0 - s_alb * rho_s)
    boa = invert_boa(toa, rho_atm, t_total, s_alb)
    assert_allclose(boa, rho_s.astype(np.float32), atol=1e-6)


@pytest.mark.unit
def test_invert_boa_no_atmosphere_is_identity():
    """With no path reflectance, unit transmittance and zero albedo, BOA == TOA."""
    toa = np.array([[0.0, 0.25], [0.5, 1.0]], dtype=np.float64)
    boa = invert_boa(toa, path_reflectance=0.0, transmittance=1.0, spherical_albedo=0.0)
    assert_allclose(boa, toa.astype(np.float32), atol=1e-6)


@pytest.mark.unit
def test_invert_boa_clips_to_physical_range():
    """Out-of-range inversions are clipped to [0, 1]."""
    # Very low TOA below path reflectance -> negative -> clipped to 0.
    boa = invert_boa(np.array([0.01]), path_reflectance=0.2, transmittance=0.8, spherical_albedo=0.0)
    assert_array_equal(boa, np.array([0.0], dtype=np.float32))


@pytest.mark.unit
def test_invert_boa_rejects_nonpositive_transmittance():
    """A non-positive total transmittance is a degenerate / invalid LUT term."""
    with pytest.raises(AtmosphericError):
        invert_boa(np.array([0.3]), path_reflectance=0.0, transmittance=0.0, spherical_albedo=0.0)


@pytest.mark.unit
def test_toa_to_boa_applies_per_band_terms():
    """toa_to_boa looks up per-band RT terms and inverts each band."""
    rho_s = {"B02": np.array([[0.2]]), "B08": np.array([[0.4]])}
    lut = RTLut(
        path_reflectance={"B02": 0.08, "B08": 0.02},
        transmittance={"B02": 0.7, "B08": 0.9},
        spherical_albedo={"B02": 0.12, "B08": 0.06},
    )
    toa = {
        b: 0.0 * v + lut.path_reflectance[b] + lut.transmittance[b] * v / (1.0 - lut.spherical_albedo[b] * v)
        for b, v in rho_s.items()
    }
    atm = AtmParams(aot=0.1, water_vapour=2.0)
    geom = SceneGeometry(sun_zenith=30.0)
    boa = toa_to_boa(toa, atm, geom, dem=np.zeros((1, 1)), rt_lut=lut)
    assert set(boa) == {"B02", "B08"}
    assert_allclose(boa["B02"], rho_s["B02"].astype(np.float32), atol=1e-6)
    assert_allclose(boa["B08"], rho_s["B08"].astype(np.float32), atol=1e-6)


@pytest.mark.unit
def test_toa_to_boa_missing_band_terms_fail_stop():
    """A band absent from the RT-LUT means missing atmospheric coverage."""
    lut = RTLut(path_reflectance={"B02": 0.05}, transmittance={"B02": 0.8})
    with pytest.raises(AtmosphericError):
        toa_to_boa(
            {"B08": np.array([[0.3]])},
            AtmParams(aot=0.1, water_vapour=2.0),
            SceneGeometry(sun_zenith=30.0),
            dem=np.zeros((1, 1)),
            rt_lut=lut,
        )


@pytest.mark.unit
def test_toa_to_boa_returns_float32():
    """BOA reflectance is emitted as float32."""
    lut = RTLut(path_reflectance={"B02": 0.0}, transmittance={"B02": 1.0})
    boa = toa_to_boa(
        {"B02": np.array([[0.3]], dtype=np.float64)},
        AtmParams(aot=0.1, water_vapour=2.0),
        SceneGeometry(sun_zenith=30.0),
        dem=np.zeros((1, 1)),
        rt_lut=lut,
    )
    assert boa["B02"].dtype == np.float32


# --------------------------------------------------------------------------- #
# ALG-ATM-PAR -- parameter ingest / retrieval                                 #
# --------------------------------------------------------------------------- #
@pytest.mark.unit
def test_get_atmospheric_parameters_ingest_from_aux():
    """Ingest mode passes the auxiliary AOT/WV/ozone straight through."""
    aux = AtmAux(aot=0.15, water_vapour=2.5, ozone=300.0)
    atm = get_atmospheric_parameters({}, "ingest", aux, {})
    assert atm.aot == 0.15
    assert atm.water_vapour == 2.5
    assert atm.ozone == 300.0


@pytest.mark.unit
def test_get_atmospheric_parameters_ingest_requires_aux():
    """Ingest mode without auxiliary inputs is an input error."""
    with pytest.raises(InputValidationError):
        get_atmospheric_parameters({}, "ingest", None, {})


@pytest.mark.unit
def test_get_atmospheric_parameters_unknown_mode():
    """An unknown parameter mode is rejected."""
    with pytest.raises(InputValidationError):
        get_atmospheric_parameters({}, "bogus", None, {})  # type: ignore[arg-type]


@pytest.mark.unit
def test_retrieve_atmospheric_parameters_is_impl():
    """Image-based retrieval (DDV/band-ratio) is [impl] and fail-stops."""
    with pytest.raises(AtmosphericError):
        retrieve_atmospheric_parameters({"B02": np.zeros((2, 2))}, {})


@pytest.mark.unit
def test_get_atmospheric_parameters_retrieve_delegates_to_impl():
    """Retrieve mode routes to the [impl] body."""
    with pytest.raises(AtmosphericError):
        get_atmospheric_parameters({"B02": np.zeros((2, 2))}, "retrieve", None, {})


@pytest.mark.unit
def test_resolve_rt_lut_is_impl():
    """RT-LUT resolution / RT engine is [impl] and fail-stops."""
    with pytest.raises(AtmosphericError):
        resolve_rt_lut(
            AtmParams(aot=0.1, water_vapour=2.0),
            SceneGeometry(sun_zenith=30.0),
            dem=np.zeros((2, 2)),
            raw_lut={},
        )


# --------------------------------------------------------------------------- #
# ALG-ATM-SCM -- scene classification & masks                                 #
# --------------------------------------------------------------------------- #
def _scene_stack() -> dict[str, np.ndarray]:
    """A 1x4 BOA stack with one cloud, one shadow, one vegetation, one water pixel."""
    #            cloud  shadow  veg    water
    blue = np.array([[0.7, 0.02, 0.04, 0.05]])
    green = np.array([[0.7, 0.03, 0.06, 0.09]])
    red = np.array([[0.7, 0.03, 0.05, 0.04]])
    nir = np.array([[0.7, 0.02, 0.40, 0.02]])
    return {"B02": blue, "B03": green, "B04": red, "B08": nir}


@pytest.mark.unit
def test_classify_scene_labels_each_class():
    """The threshold classifier assigns the expected scene class per pixel."""
    scene, cloud, shadow = classify_scene(_scene_stack(), {})
    assert scene.dtype == np.uint8
    assert scene[0, 0] == SceneClass.CLOUD
    assert scene[0, 1] == SceneClass.CLOUD_SHADOW
    assert scene[0, 2] == SceneClass.VEGETATION
    assert scene[0, 3] == SceneClass.WATER


@pytest.mark.unit
def test_classify_scene_masks_are_consistent_with_labels():
    """The boolean masks match the cloud / cloud-shadow scene labels."""
    scene, cloud, shadow = classify_scene(_scene_stack(), {})
    assert_array_equal(cloud, scene == SceneClass.CLOUD)
    assert_array_equal(shadow, scene == SceneClass.CLOUD_SHADOW)
    assert cloud.dtype == np.bool_ and shadow.dtype == np.bool_


@pytest.mark.unit
def test_classify_scene_band_roles_override():
    """Custom band-role names resolve the spectral indices."""
    stack = {
        "blu": np.array([[0.04]]),
        "grn": np.array([[0.06]]),
        "rd": np.array([[0.05]]),
        "n": np.array([[0.40]]),
    }
    roles = {"blue": "blu", "green": "grn", "red": "rd", "nir": "n"}
    scene, _, _ = classify_scene(stack, {"band_roles": roles})
    assert scene[0, 0] == SceneClass.VEGETATION


@pytest.mark.unit
def test_classify_scene_no_data_for_nonfinite():
    """Non-finite pixels are flagged NO_DATA and excluded from the masks."""
    stack = {b: v.copy() for b, v in _scene_stack().items()}
    stack["B08"][0, 0] = np.nan  # invalidate the cloud pixel
    scene, cloud, shadow = classify_scene(stack, {})
    assert scene[0, 0] == SceneClass.NO_DATA
    assert not cloud[0, 0]


@pytest.mark.unit
def test_classify_scene_threshold_override():
    """A raised cloud-brightness threshold reclassifies the bright pixel."""
    scene, cloud, _ = classify_scene(_scene_stack(), {"cloud_brightness": 0.9})
    assert scene[0, 0] != SceneClass.CLOUD
    assert not cloud[0, 0]


@pytest.mark.unit
def test_classify_scene_empty_stack():
    """An empty BOA stack is an input error."""
    with pytest.raises(InputValidationError):
        classify_scene({}, {})


@pytest.mark.unit
def test_classify_scene_ml_is_impl():
    """The learned scene classifier refinement is [impl] and fail-stops."""
    with pytest.raises(AtmosphericError):
        classify_scene_ml(_scene_stack(), {})
