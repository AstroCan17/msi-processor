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

"""End-to-end integration test of the full L0c → L2A (+ pansharpen) chain.

Wires all eight processing units in sequence on a single deterministic,
feature-rich synthetic scene (Gaussian-blob texture survives the SIFT-based
co-registration and GCP geolocation), with minimal in-memory ADFs. This is the
first integration coverage of the chain hand-off contract (SDD <5.3>,
DPM <8>): each stage's output product satisfies the next stage's input
expectations, and an open-container L0c round-trips to an L2A BOA product with a
scene classification and a cartographic geolocation grid.

No private codec, no network, no real RAW — the public open-container path only.
"""

from typing import Any

import numpy as np
import pytest
from eopf.computing.abstract import AuxiliaryDataFile
from eopf.product import EOGroup, EOProduct, EOVariable
from pyproj import CRS

from msi_processor.computing.atmospheric.unit import AtmosphericUnit
from msi_processor.computing.coregistration.unit import CoregistrationUnit
from msi_processor.computing.enhancement.unit import EnhancementUnit
from msi_processor.computing.georeference.unit import GeoreferenceUnit
from msi_processor.computing.l0_decode.unit import L0DecodeUnit
from msi_processor.computing.pansharpen.unit import PansharpenUnit
from msi_processor.computing.radiometric.unit import RadiometricUnit
from msi_processor.computing.toa.unit import ToaUnit

_BASE = 160
_WIN = 128
_ORIGIN = 16
_TX = 6
_TY = 4
_DET = ("line", "detector")
_UTM35N_WKT = CRS.from_epsg(32635).to_wkt()
_GDAL = [600000.0, 10.0, 0.0, 4500000.0, 0.0, -10.0]


def _textured_scene(seed: int, size: int = _BASE, n_blobs: int = 150) -> np.ndarray:
    """A deterministic, feature-rich field of Gaussian blobs (SIFT-friendly)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    field = np.full((size, size), 100.0)
    for _ in range(n_blobs):
        cy = rng.uniform(0, size)
        cx = rng.uniform(0, size)
        sigma = rng.uniform(1.5, 4.0)
        amp = rng.uniform(200.0, 1500.0)
        field += amp * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * sigma * sigma)))
    return field


def _to_dn(field: np.ndarray) -> np.ndarray:
    """Scale a texture field into a 12-bit DN frame [0, 4000]."""
    lo, hi = float(field.min()), float(field.max())
    scaled = (field - lo) / (hi - lo) * 4000.0
    return scaled.astype(np.uint16)


def _scene_bands(bands: tuple[str, ...]) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Return ``({band: DN frame}, gcp_reference)`` from one base scene.

    The reference band is the origin crop; every other band is the same scene
    cropped with the known ``(_TX, _TY)`` offset so co-registration recovers it.
    The GCP reference is the float reference crop (structure matches the
    co-registered reference band).
    """
    base = _textured_scene(seed=1)
    o, w = _ORIGIN, _WIN
    oe = o + w
    ref_crop = base[o:oe, o:oe]
    frames: dict[str, np.ndarray] = {}
    for i, band in enumerate(bands):
        if i == 0:
            frames[band] = _to_dn(ref_crop)
        else:
            sy, sx = o + _TY, o + _TX
            ey, ex = sy + w, sx + w
            frames[band] = _to_dn(base[sy:ey, sx:ex])
    return frames, ref_crop.astype(np.float32)


def _adf(name: str, data: Any) -> AuxiliaryDataFile:
    """Build an ADF carrying its content in ``data_ptr`` (this-increment convention)."""
    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


def _l0c(frames: dict[str, np.ndarray]) -> EOProduct:
    """An open-container L0c with decoded detector frames + minimal telemetry."""
    n_lines = next(iter(frames.values())).shape[0]
    product = EOProduct("L0C.IT")
    product["measurements"] = EOGroup()
    for band, dn in frames.items():
        product[f"measurements/detector/{band}"] = EOVariable(data=dn, dims=_DET)
    product["conditions"] = EOGroup()
    product["conditions/time/line_time"] = EOVariable(data=np.arange(n_lines, dtype=np.float64), dims=("line",))
    product["conditions/orbit/position"] = EOVariable(
        data=np.zeros((n_lines, 3), dtype=np.float64), dims=("line", "xyz")
    )
    return product


def _run_to_l2a(bands: tuple[str, ...]) -> EOProduct:
    """Run the L0c → L2A core chain over the given bands; return the L2A product."""
    frames, gcp_ref = _scene_bands(bands)
    n_det = _WIN

    # 1. l0_decode
    l1a = L0DecodeUnit("l0").run({"l0c": _l0c(frames)})["l1a"]

    # 2. radiometric (identity NUC + zero dark)
    rad = RadiometricUnit("rad").run(
        {"l1a": l1a},
        adfs={
            "dark": _adf("dark", {"dark_offset": {b: 0.0 for b in bands}}),
            "nuc": _adf(
                "nuc",
                {
                    "gain": {b: np.ones(n_det, dtype=np.float32) for b in bands},
                    "offset": {b: np.zeros(n_det, dtype=np.float32) for b in bands},
                },
            ),
        },
    )["rad"]

    # 3. enhancement (identity PSF, no denoise)
    enh = EnhancementUnit("enh").run(
        {"rad": rad},
        adfs={"psf": _adf("psf", {"kernel": {b: np.array([[1.0]], dtype=np.float32) for b in bands}})},
        denoise_method="none",
    )["enh"]

    # 4. toa (DN -> radiance -> reflectance)
    l1b = ToaUnit("toa").run(
        {"enh": enh},
        adfs={
            "radiometric": _adf(
                "radiometric",
                {"gain": {b: 1.0e-4 for b in bands}, "offset": {b: 0.0 for b in bands}},
            ),
            "spectral": _adf("spectral", {"esun": {b: 2.0 for b in bands}}),
        },
        emit_reflectance=True,
        sun_zenith_deg=30.0,
        earth_sun_distance_au=1.0,
    )["l1b"]

    # 5. coregistration (reference band = first band)
    cor = CoregistrationUnit("cor").run({"l1b": l1b}, reference_band=bands[0], seed=0)["cor"]

    # 6. georeference (GCP path against the geolocated reference scene)
    l1c = GeoreferenceUnit("geo").run(
        {"cor": cor},
        adfs={
            "viewing_model": _adf("viewing_model", {"pixel_pitch_m": 5.5e-6, "focal_length_m": 845e-6}),
            "dem": _adf(
                "dem",
                {"elevation": np.zeros((10, 10), dtype=np.float32), "geotransform": _GDAL, "crs_wkt": _UTM35N_WKT},
            ),
            "gcp": _adf("gcp", {"image": gcp_ref, "geotransform": _GDAL, "crs_wkt": _UTM35N_WKT}),
        },
        resolution=10.0,
        gcp_reference_band=bands[0],
        seed=0,
    )["l1c"]

    # 7. atmospheric (6S BOA inversion in ingest mode); DEM sized to the L1C grid
    ref0 = np.asarray(l1c[f"measurements/reflectance/{bands[0]}"].data)
    rt_lut = {
        "path_reflectance": {b: 0.04 for b in bands},
        "transmittance": {b: 0.85 for b in bands},
        "spherical_albedo": {b: 0.08 for b in bands},
    }
    l2a = AtmosphericUnit("atm").run(
        {"l1c": l1c},
        adfs={
            "atmospheric": _adf("atmospheric", {"aot": 0.15, "water_vapour": 2.5, "ozone": 300.0, "rt_lut": rt_lut}),
            "dem": _adf("dem", {"elevation": np.zeros(ref0.shape, dtype=np.float32)}),
        },
        param_mode="ingest",
        sun_zenith=30.0,
        view_zenith=0.0,
        relative_azimuth=0.0,
    )["l2a"]
    return l2a


@pytest.mark.integration
def test_l0c_to_l2a_full_chain():
    """The seven core units chain L0c → L2A and emit a BOA product with QA."""
    bands = ("B02", "B03")
    l2a = _run_to_l2a(bands)

    reflectance = l2a["measurements/reflectance"]
    assert set(reflectance) == set(bands)
    for band in bands:
        boa = np.asarray(l2a[f"measurements/reflectance/{band}"].data)
        assert boa.dtype == np.float32
        assert np.all((boa >= 0.0) & (boa <= 1.0))
    # L2A carries a scene classification and the upstream geolocation grid.
    scl = np.asarray(l2a["quality/scene_classification"].data)
    assert scl.dtype == np.uint8
    # The cartographic geolocation grid propagates end-to-end (georef -> L2A).
    assert np.asarray(l2a["conditions/geolocation/x"].data).ndim == 1
    assert np.asarray(l2a["conditions/geolocation/y"].data).ndim == 1
    spatial_ref = l2a["conditions/geolocation/spatial_ref"]
    assert "crs_wkt" in spatial_ref.attrs


@pytest.mark.integration
def test_full_chain_with_pansharpen():
    """The optional pansharpen derivative runs on the L2A BOA + PAN band."""
    bands = ("B02", "B03", "PAN")
    l2a = _run_to_l2a(bands)

    pan = PansharpenUnit("pan").run({"l2a": l2a}, pan_band="PAN")["pan"]
    fused = pan["measurements/reflectance"]
    # PAN is consumed; only the MS bands are emitted, sharpened.
    assert set(fused) == {"B02", "B03"}
    for band in ("B02", "B03"):
        arr = np.asarray(pan[f"measurements/reflectance/{band}"].data)
        assert arr.dtype == np.float32
        assert np.all((arr >= 0.0) & (arr <= 1.0))
        fidelity = np.asarray(pan[f"quality/spectral_fidelity/{band}"].data)
        assert fidelity.shape == (1,)
