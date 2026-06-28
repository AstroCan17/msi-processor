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

r"""Pure atmospheric-correction core (C-PU-ATM; ALG-ATM-PAR/RT/SCM).

CPM-free, I/O-free functions implementing the atmospheric-correction algorithms
of ATBD <5.8>. **This stage has no prior-work heritage**; it is new development
specified interface-first (SDD <5.4.9>) with a candidate algorithm whose RT
engine and parameter-retrieval/classifier bodies are down-selected in the DPM and
left as private ``[impl]`` stubs.

Algorithm split (operational baseline vs ``[impl]``)
----------------------------------------------------
Two boundaries follow the same pattern as the geo-referencing core (an operational
baseline now, the rigorous body deferred to the DPM/CDR):

* ``ALG-ATM-RT`` (TOA -> BOA inversion). The **6S surface-reflectance inversion**
  itself is exact algebra once the per-band radiative-transfer terms
  :math:`\{\rho_{\mathrm{atm}}, T, S\}` are known; it is realised here
  (:func:`invert_boa`, :func:`toa_to_boa`) and fully unit-tested. The **RT engine
  that *builds/interpolates* the LUT** for the per-pixel geometry / AOT / water
  vapour / surface altitude (Py6S / 6SV / Sen2Cor-LUT / ACOLITE -- down-selected
  in the DPM) is the deferred body :func:`resolve_rt_lut` (``[impl]``). The unit
  consumes an already-resolved :class:`RTLut` for the scene operating point.

* ``ALG-ATM-PAR`` (parameter ingest/retrieval). **Ingesting** AOT / water vapour /
  ozone from auxiliary meteorology is realised here (:func:`get_atmospheric_parameters`
  with ``mode="ingest"``). **Retrieving** them from the imagery (dark-dense-vegetation
  AOT inversion, differential band-ratio water vapour) is the deferred body
  (``mode="retrieve"`` -> :func:`retrieve_atmospheric_parameters`, ``[impl]``).

* ``ALG-ATM-SCM`` (scene classification & masks). A **spectral-threshold scene
  classifier** (Sen2Cor-style candidate, ATBD <5.8>) is realised here
  (:func:`classify_scene`) producing a scene-class layer plus cloud / cloud-shadow
  masks. A sophisticated (e.g. ML) classifier is the deferred refinement
  (:func:`classify_scene_ml`, ``[impl]``).

Theory (ATBD <5.8>). Over a Lambertian surface the TOA reflectance is
:math:`\rho_{\mathrm{TOA}} = \rho_{\mathrm{atm}} + T(\theta_s)T(\theta_v)\rho_s /
(1 - S\rho_s)`; inverting for the surface (BOA) reflectance gives
:math:`\rho_{\mathrm{BOA}} = (\rho_{\mathrm{TOA}} - \rho_{\mathrm{atm}}) /
(T + S(\rho_{\mathrm{TOA}} - \rho_{\mathrm{atm}}))` with :math:`T = T(\theta_s)T(\theta_v)`.

*Trace:* REQ-F-ATM-01..04; DPM-M-ATM; ALG-ATM-PAR/RT/SCM.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Union

import numpy as np
import numpy.typing as npt

from msi_processor.exceptions.errors import AtmosphericError, InputValidationError

__all__ = [
    "ScalarOrArray",
    "AtmParams",
    "AtmAux",
    "SceneGeometry",
    "RTLut",
    "SceneClass",
    "get_atmospheric_parameters",
    "retrieve_atmospheric_parameters",
    "resolve_rt_lut",
    "invert_boa",
    "toa_to_boa",
    "classify_scene",
    "classify_scene_ml",
]

_STAGE = "atmospheric"

#: A radiative quantity that may be a per-scene scalar or a per-pixel field.
ScalarOrArray = Union[float, npt.NDArray[np.float64]]

RetrievalMode = Literal["ingest", "retrieve"]


class SceneClass:
    """Scene-classification label codes (Sen2Cor-style subset, ALG-ATM-SCM).

    Stored as a ``uint8`` layer in ``quality/scene_classification`` of the L2A
    product. ``NO_DATA`` is reserved for fill; the cloud / cloud-shadow classes are
    mirrored into the per-band QA flag layer (:class:`~msi_processor.common.types.QAFlag`).
    """

    NO_DATA = 0
    CLOUD = 1
    CLOUD_SHADOW = 2
    VEGETATION = 3
    BARE_SOIL = 4
    WATER = 5
    UNCLASSIFIED = 6


@dataclass(frozen=True)
class AtmParams:
    """Atmospheric state used by the RT inversion (ALG-ATM-PAR output).

    Attributes
    ----------
    aot:
        Aerosol optical thickness (550 nm), scalar or per-pixel field.
    water_vapour:
        Columnar water vapour (g/cm^2), scalar or per-pixel field.
    ozone:
        Columnar ozone (Dobson units), optional scalar.
    """

    aot: ScalarOrArray
    water_vapour: ScalarOrArray
    ozone: float | None = None


@dataclass(frozen=True)
class AtmAux:
    """Auxiliary atmospheric inputs ingested from meteorology ADFs (ingest mode).

    Mirrors the ``atmospheric`` ADF content for ``ALG-ATM-PAR`` ``mode="ingest"``.
    """

    aot: ScalarOrArray
    water_vapour: ScalarOrArray
    ozone: float | None = None


@dataclass(frozen=True)
class SceneGeometry:
    """Per-scene illumination/view geometry operating point (degrees).

    The LUT is resolved at this operating point; rigorous per-pixel variation is
    handled inside the ``[impl]`` :func:`resolve_rt_lut`.
    """

    sun_zenith: float
    view_zenith: float = 0.0
    relative_azimuth: float = 0.0


@dataclass(frozen=True)
class RTLut:
    r"""Per-band radiative-transfer terms for the scene operating point (ALG-ATM-RT).

    Each mapping is keyed by band id. The terms are the Vermote/6S decomposition:

    * ``path_reflectance`` -- intrinsic (path) reflectance :math:`\rho_{\mathrm{atm}}`;
    * ``transmittance`` -- total two-way transmittance :math:`T = T(\theta_s)T(\theta_v)`;
    * ``spherical_albedo`` -- atmospheric spherical albedo :math:`S`.

    Producing this table from an RT engine / pre-computed LUT for a given
    :class:`AtmParams` + :class:`SceneGeometry` + DEM altitude is the ``[impl]``
    :func:`resolve_rt_lut`.
    """

    path_reflectance: Mapping[str, float]
    transmittance: Mapping[str, float]
    spherical_albedo: Mapping[str, float] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# ALG-ATM-PAR -- atmospheric parameter ingest / retrieval                      #
# --------------------------------------------------------------------------- #
def get_atmospheric_parameters(
    toa_refl: Mapping[str, npt.NDArray[Any]],
    mode: RetrievalMode,
    aux: AtmAux | None,
    params: Mapping[str, object],
) -> AtmParams:
    """ALG-ATM-PAR -- obtain the atmospheric state (ingest or retrieve).

    Parameters
    ----------
    toa_refl:
        TOA reflectance band stack (only used by the retrieval path).
    mode:
        ``"ingest"`` reads AOT / water vapour / ozone from ``aux`` (auxiliary
        meteorology); ``"retrieve"`` inverts them from the imagery and is the
        deferred ``[impl]`` body (DDV AOT, band-ratio water vapour, ATBD <5.8>).
    aux:
        Ingested auxiliary atmospheric inputs (mandatory for ``mode="ingest"``).
    params:
        Profile parameters (e.g. default fallbacks); reserved for the retrieval
        path.

    Returns
    -------
    AtmParams
        The atmospheric state for the RT inversion.

    Raises
    ------
    InputValidationError
        On an unknown ``mode`` or a missing ``aux`` in ingest mode.
    AtmosphericError
        From the ``[impl]`` retrieval path (until down-selected in the DPM).
    """
    if mode == "ingest":
        if aux is None:
            raise InputValidationError(
                "atmospheric ingest mode requires auxiliary AOT/water-vapour inputs (aux)",
                stage=_STAGE,
            )
        return AtmParams(aot=aux.aot, water_vapour=aux.water_vapour, ozone=aux.ozone)
    if mode == "retrieve":
        return retrieve_atmospheric_parameters(toa_refl, params)
    raise InputValidationError(
        f"Unknown atmospheric parameter mode '{mode}'; expected 'ingest' or 'retrieve'",
        stage=_STAGE,
    )


def retrieve_atmospheric_parameters(
    toa_refl: Mapping[str, npt.NDArray[Any]],
    params: Mapping[str, object],
) -> AtmParams:
    """ALG-ATM-PAR retrieval body -- **[impl]** (DPM down-selection / CDR target).

    Image-based retrieval of AOT (dark-dense-vegetation inversion) and water
    vapour (differential band-ratio absorption) per ATBD <5.8>. The concrete
    method is down-selected and validated in the DPM before CDR; until then this
    fail-stops so the chain never emits an L2A product from un-retrieved
    parameters.
    """
    raise AtmosphericError(
        "Image-based atmospheric parameter retrieval (ALG-ATM-PAR) is [impl]; "
        "use ingest mode with an atmospheric ADF, or down-select the retrieval "
        "engine in the DPM (ATBD <5.8> open point 1)",
        stage=_STAGE,
    )


# --------------------------------------------------------------------------- #
# ALG-ATM-RT -- TOA -> BOA inversion                                           #
# --------------------------------------------------------------------------- #
def resolve_rt_lut(
    atm: AtmParams,
    geometry: SceneGeometry,
    dem: npt.NDArray[Any],
    raw_lut: Mapping[str, object],
) -> RTLut:
    """Interpolate the per-band RT terms for the scene operating point -- **[impl]**.

    Multi-dimensional interpolation of a pre-computed radiative-transfer LUT (or a
    direct RT-engine call) over geometry, AOT, water vapour and surface altitude,
    yielding :class:`RTLut`. The engine (Py6S / 6SV / Sen2Cor-LUT / ACOLITE) is
    down-selected in the DPM and licence-screened in the SRF; the inversion that
    consumes the result (:func:`toa_to_boa`) is operational. Fail-stops until the
    engine is selected (ATBD <5.8> open point 1).
    """
    raise AtmosphericError(
        "RT-LUT resolution / radiative-transfer engine (ALG-ATM-RT LUT) is [impl]; "
        "supply a pre-resolved RTLut for the scene operating point, or down-select "
        "the RT engine in the DPM (ATBD <5.8> open point 1)",
        stage=_STAGE,
    )


def invert_boa(
    toa: npt.NDArray[Any],
    path_reflectance: float,
    transmittance: float,
    spherical_albedo: float,
) -> npt.NDArray[np.float32]:
    r"""ALG-ATM-RT kernel -- invert one band's TOA reflectance to BOA.

    Applies the 6S surface-reflectance inversion (ATBD <5.8>):

    .. math::
        \rho_{\mathrm{BOA}} = \frac{\rho_{\mathrm{TOA}} - \rho_{\mathrm{atm}}}
        {T + S\,(\rho_{\mathrm{TOA}} - \rho_{\mathrm{atm}})}

    with ``T`` the total two-way transmittance and ``S`` the spherical albedo.
    The result is clipped to the physical ``[0, 1]`` reflectance range.

    Raises
    ------
    AtmosphericError
        If the total transmittance is non-positive (degenerate / invalid LUT term).
    """
    if not transmittance > 0.0:
        raise AtmosphericError(
            f"Non-positive total transmittance ({transmittance}) in BOA inversion",
            stage=_STAGE,
        )
    toa_f = np.asarray(toa, dtype=np.float64)
    y = toa_f - float(path_reflectance)
    denom = float(transmittance) + float(spherical_albedo) * y
    # Guard the (rare) denominator zero-crossing before dividing.
    safe_denom = np.where(np.abs(denom) < 1e-12, np.float64(1e-12), denom)
    boa = y / safe_denom
    clipped = np.clip(np.nan_to_num(boa, nan=0.0, posinf=1.0, neginf=0.0), 0.0, 1.0)
    return clipped.astype(np.float32)


def toa_to_boa(
    toa_refl: Mapping[str, npt.NDArray[Any]],
    atm: AtmParams,
    geometry: SceneGeometry,
    dem: npt.NDArray[Any],
    rt_lut: RTLut,
) -> dict[str, npt.NDArray[np.float32]]:
    """ALG-ATM-RT -- invert the TOA reflectance stack to BOA per band.

    For each band the per-band RT terms are looked up from ``rt_lut`` (resolved at
    the scene operating point) and the 6S inversion (:func:`invert_boa`) is
    applied. The ``atm`` / ``geometry`` / ``dem`` arguments document the operating
    point the LUT was resolved at; per-pixel LUT interpolation lives in the
    ``[impl]`` :func:`resolve_rt_lut`.

    Returns
    -------
    dict[str, ndarray]
        BOA reflectance per band, ``float32`` in ``[0, 1]``.

    Raises
    ------
    AtmosphericError
        If a band has no RT terms in the LUT (missing coverage).
    """
    boa: dict[str, npt.NDArray[np.float32]] = {}
    for band, data in toa_refl.items():
        if band not in rt_lut.path_reflectance or band not in rt_lut.transmittance:
            raise AtmosphericError(
                f"RT-LUT has no terms for band '{band}' (missing atmospheric coverage)",
                stage=_STAGE,
            )
        boa[band] = invert_boa(
            data,
            path_reflectance=float(rt_lut.path_reflectance[band]),
            transmittance=float(rt_lut.transmittance[band]),
            spherical_albedo=float(rt_lut.spherical_albedo.get(band, 0.0)),
        )
    return boa


# --------------------------------------------------------------------------- #
# ALG-ATM-SCM -- scene classification & cloud / cloud-shadow masks             #
# --------------------------------------------------------------------------- #
def _resolve_band(
    boa: Mapping[str, npt.NDArray[Any]],
    params: Mapping[str, object],
    role: str,
    default_names: tuple[str, ...],
) -> npt.NDArray[np.float64] | None:
    """Resolve a spectral role (e.g. ``"nir"``) to a band array, or ``None``.

    The mapping is profile-driven: ``params["band_roles"]`` maps roles to band
    ids; otherwise common band names are tried.
    """
    roles = params.get("band_roles")
    if isinstance(roles, Mapping):
        mapped = roles.get(role)
        if isinstance(mapped, str) and mapped in boa:
            return np.asarray(boa[mapped], dtype=np.float64)
    for name in default_names:
        if name in boa:
            return np.asarray(boa[name], dtype=np.float64)
    return None


def classify_scene(
    boa: Mapping[str, npt.NDArray[Any]],
    params: Mapping[str, object],
) -> tuple[npt.NDArray[np.uint8], npt.NDArray[np.bool_], npt.NDArray[np.bool_]]:
    """ALG-ATM-SCM -- spectral-threshold scene classification + masks.

    A Sen2Cor-style spectral-threshold classifier (ATBD <5.8> candidate). It
    derives, from the BOA stack, a scene-class layer (:class:`SceneClass` codes)
    plus boolean cloud and cloud-shadow masks. Spectral roles (``blue``, ``green``,
    ``red``, ``nir``) are resolved via ``params["band_roles"]`` or common band
    names; vegetation/water use NDVI/NDWI, clouds use a brightness threshold and
    shadows a low-NIR/low-brightness threshold. A more sophisticated (ML)
    classifier is the deferred :func:`classify_scene_ml` (``[impl]``).

    Thresholds (overridable via ``params``): ``cloud_brightness`` (0.5),
    ``shadow_nir`` (0.08), ``shadow_brightness`` (0.12), ``ndvi_veg`` (0.4),
    ``ndwi_water`` (0.2).

    Returns
    -------
    tuple
        ``(scene_class[uint8], cloud_mask[bool], cloud_shadow_mask[bool])``.

    Raises
    ------
    InputValidationError
        If the BOA stack is empty.
    """
    if not boa:
        raise InputValidationError("classify_scene received an empty BOA stack", stage=_STAGE)

    blue = _resolve_band(boa, params, "blue", ("B02", "blue", "B2"))
    green = _resolve_band(boa, params, "green", ("B03", "green", "B3"))
    red = _resolve_band(boa, params, "red", ("B04", "red", "B4"))
    nir = _resolve_band(boa, params, "nir", ("B08", "nir", "B8", "B8A"))

    sample = np.asarray(next(iter(boa.values())), dtype=np.float64)
    shape = sample.shape

    t_cloud = float(_as_float(params.get("cloud_brightness"), 0.5))
    t_shadow_nir = float(_as_float(params.get("shadow_nir"), 0.08))
    t_shadow_bright = float(_as_float(params.get("shadow_brightness"), 0.12))
    t_ndvi = float(_as_float(params.get("ndvi_veg"), 0.4))
    t_ndwi = float(_as_float(params.get("ndwi_water"), 0.2))

    # Brightness = mean over the visible bands available.
    visible = [b for b in (blue, green, red) if b is not None]
    brightness = np.mean(np.stack(visible, axis=0), axis=0) if visible else np.zeros(shape, dtype=np.float64)

    valid = np.ones(shape, dtype=bool)
    for arr in boa.values():
        valid &= np.isfinite(np.asarray(arr, dtype=np.float64))

    ndvi = _normalised_difference(nir, red)
    ndwi = _normalised_difference(green, nir)

    water = (ndwi > t_ndwi) if ndwi is not None else np.zeros(shape, dtype=bool)
    cloud = brightness > t_cloud
    if nir is not None:
        cloud &= nir > t_cloud  # clouds are bright in NIR too -> reject bright bare soil
    cloud &= ~water
    shadow = np.zeros(shape, dtype=bool)
    if nir is not None:
        shadow = (nir < t_shadow_nir) & (brightness < t_shadow_bright) & ~water & ~cloud
    vegetation = (ndvi > t_ndvi) if ndvi is not None else np.zeros(shape, dtype=bool)
    vegetation &= ~cloud & ~shadow & ~water

    scene = np.full(shape, SceneClass.UNCLASSIFIED, dtype=np.uint8)
    scene[vegetation] = SceneClass.VEGETATION
    scene[water] = SceneClass.WATER
    scene[shadow] = SceneClass.CLOUD_SHADOW
    scene[cloud] = SceneClass.CLOUD
    # Bare soil: unclassified-but-valid land left as bare soil when not vegetation.
    bare = ~cloud & ~shadow & ~water & ~vegetation & valid & (scene == SceneClass.UNCLASSIFIED)
    scene[bare] = SceneClass.BARE_SOIL
    scene[~valid] = SceneClass.NO_DATA

    return scene, cloud & valid, shadow & valid


def classify_scene_ml(
    boa: Mapping[str, npt.NDArray[Any]],
    params: Mapping[str, object],
) -> tuple[npt.NDArray[np.uint8], npt.NDArray[np.bool_], npt.NDArray[np.bool_]]:
    """ALG-ATM-SCM refinement -- learned scene classifier, **[impl]**.

    A trained (e.g. CNN / random-forest) scene classifier is the CDR refinement of
    the spectral-threshold baseline (:func:`classify_scene`). The model and its
    training data are down-selected in the DPM; this fail-stops until then.
    """
    raise AtmosphericError(
        "Learned scene classifier (ALG-ATM-SCM ML refinement) is [impl]; use the "
        "spectral-threshold classify_scene baseline (ATBD <5.8> open point 1)",
        stage=_STAGE,
    )


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #
def _as_float(value: object, default: float) -> float:
    """Coerce an optional profile parameter to ``float`` (with a default)."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    raise InputValidationError(f"Expected a numeric parameter, got {value!r}", stage=_STAGE)


def _normalised_difference(
    a: npt.NDArray[np.float64] | None,
    b: npt.NDArray[np.float64] | None,
) -> npt.NDArray[np.float64] | None:
    """Normalised difference ``(a - b) / (a + b)`` with a safe denominator."""
    if a is None or b is None:
        return None
    denom = a + b
    safe = np.where(np.abs(denom) < 1e-12, np.float64(1e-12), denom)
    return (a - b) / safe
