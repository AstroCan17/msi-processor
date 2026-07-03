#!/usr/bin/env python3
# Copyright 2026 Can Deniz Kaya
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
"""The msi-processor pipeline — the repository's single driver script.

Phase-structured, idempotent, one data-store root (``inputs/ caldb/ l0/ l1a/ l1b/ l1c/
l2a/ nuc/ quicklook/ report/``); inputs come from the shared **ipf/data-store** registry
(``fetch-store``) and products carry EOPF PSFD §3 names (naming authority: the producer's
``s2_msi_raw_generator.naming`` — a minimal composer is ported here).

**Nominal mode** (default)::

    fetch-store l0-decode radiometric enhancement toa stats report

``--full`` extends the chain after ``toa``::

    coregister georeference atmospheric pansharpen        # demo geo/atm ADFs, flagged

**Calibration mode** (``--mode calibration``)::

    fetch-store l0-decode radiometric-cal cal-validate report

The calibration mode consumes the producer's raw calibration *acquisitions*
(``inputs/calibration/{dark,flatfield}.zarr``), derives the NUC in the ``radiometric``
unit's calibration mode, persists it as a PSFD-named product and cross-checks it against
the producer-derived coefficients (``cal-validate``).

Examples::

    python scripts/run_pipeline.py store                          # nominal chain
    python scripts/run_pipeline.py store --full                   # + L1C/L2A (demo geo ADFs)
    python scripts/run_pipeline.py store --mode calibration
    python scripts/run_pipeline.py store --phases stats           # QA table of the L1B

The eopf/unit imports are lazy (chain phases only); ``fetch-store``/``stats``/``report``/
``publish-store`` run with numpy+zarr alone. Chain phases pass products in-process — run
them in one invocation (each *product* is persisted; ``stats``/``report`` re-read disk).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# PSFD naming (minimal composer; authority: s2_msi_raw_generator.naming)
# ---------------------------------------------------------------------------

TYPE_CODES = ("S02MSIL0_", "S02MSIL1A", "S02MSIL1B", "S02MSIL1C", "S02MSIL2A")
_NAME_RE = re.compile(
    r"^(?P<product_type>[A-Z0-9_]{9})_(?P<start>\d{8}T\d{6})_(?P<duration>\d{4})"
    r"_(?P<unit>[A-Z])(?P<relative_orbit>\d{3})_(?P<consolidation>[T_S])(?P<discriminator>[0-9A-F]{3})"
    r"(?:_(?P<z_suffix>[A-Za-z0-9_]+))?(?P<ext>\.zarr\.zip|\.zarr)?$"
)


def psfd_name(
    product_type: str,
    start: str,
    duration: int,
    unit: str,
    relative_orbit: int,
    *,
    z_suffix: str | None = None,
) -> str:
    """Compose a PSFD §3 product file name (fields as parsed by :func:`parse_psfd_name`)."""
    if product_type not in TYPE_CODES:
        raise ValueError(f"unknown product type {product_type!r}")
    seed = f"{product_type}{start}{duration}{unit}{relative_orbit}"
    disc = f"{zlib.crc32(seed.encode('utf-8')):03X}"[-3:]
    name = f"{product_type}_{start}_{duration:04d}_{unit}{relative_orbit:03d}_T{disc}"
    if z_suffix:
        name += f"_{z_suffix}"
    return name + ".zarr"


def parse_psfd_name(name: str) -> dict[str, Any]:
    """Parse a PSFD §3 product file name into its fields."""
    m = _NAME_RE.match(name)
    if m is None:
        raise ValueError(f"not a valid PSFD product name: {name!r}")
    return {
        "product_type": m["product_type"],
        "start": m["start"],
        "duration": int(m["duration"]),
        "unit": m["unit"],
        "relative_orbit": int(m["relative_orbit"]),
        "z_suffix": m["z_suffix"],
    }


# ---------------------------------------------------------------------------
# store layout + data-store sync (ported from the producer's driver)
# ---------------------------------------------------------------------------

DATASTORE_API = "https://gitlab.eopf.copernicus.eu/api/v4/projects/ipf%2Fdata-store/packages/generic"
DATASTORE_PACKAGES_API = "https://gitlab.eopf.copernicus.eu/api/v4/projects/ipf%2Fdata-store/packages"

PHASES = [
    "fetch-store",
    "l0-decode",
    "radiometric",
    "enhancement",
    "toa",
    "coregister",
    "georeference",
    "atmospheric",
    "pansharpen",
    "radiometric-cal",
    "cal-validate",
    "stats",
    "report",
    "publish-store",
]
NOMINAL_PHASES = ["fetch-store", "l0-decode", "radiometric", "enhancement", "toa", "stats", "report"]
FULL_EXTRA = ["coregister", "georeference", "atmospheric", "pansharpen"]
CALIBRATION_PHASES = ["fetch-store", "l0-decode", "radiometric-cal", "cal-validate", "report"]


def _store_paths(store: Path) -> dict[str, Path]:
    p = {
        name: store / name
        for name in ("inputs", "caldb", "l0", "l1a", "l1b", "l1c", "l2a", "nuc", "quicklook", "report")
    }
    for d in p.values():
        d.mkdir(parents=True, exist_ok=True)
    return p


def _jdump(obj: Any, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def _jload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _store_auth_headers() -> dict[str, str]:
    if os.environ.get("CI_JOB_TOKEN"):
        return {"JOB-TOKEN": os.environ["CI_JOB_TOKEN"]}
    tok = os.environ.get("DATASTORE_TOKEN") or os.environ.get("GITLAB_TOKEN")
    if tok:
        return {"PRIVATE-TOKEN": tok}
    raise SystemExit("[publish-store] needs CI_JOB_TOKEN (CI) or DATASTORE_TOKEN/GITLAB_TOKEN")


def _http(url: str, *, headers: dict[str, str] | None = None, method: str = "GET", data: bytes | None = None) -> bytes:
    import urllib.request

    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def _sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _zip_dir(src: Path, dest_zip: Path) -> None:
    import zipfile

    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(src.parent))


def phase_fetch_store(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Pull the shared data-store (manifest → missing packages → sha256 → unpack)."""
    import hashlib
    import io as _io
    import zipfile

    root = store["report"].parent
    manifest = json.loads(_http(f"{DATASTORE_API}/manifest/latest/manifest.json").decode())
    wanted = {n.strip() for n in args.fetch_packages.split(",") if n.strip()}
    fetched = skipped = 0
    for pkg in manifest.get("packages", []):
        if wanted and pkg["name"] not in wanted:
            continue
        for f in pkg["files"]:
            target = root / (f["path"][:-4] if f["path"].endswith(".zip") else f["path"])
            if target.is_file() or (target.is_dir() and any(target.iterdir())):
                skipped += 1
                continue
            blob = _http(f"{DATASTORE_API}/{pkg['name']}/{pkg['version']}/{f['file']}")
            got = hashlib.sha256(blob).hexdigest()
            if got != f["sha256"]:
                raise SystemExit(f"[fetch-store] sha256 mismatch for {f['file']}: {got}")
            if f["path"].endswith(".zip"):
                (root / f["path"]).parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(_io.BytesIO(blob)) as zf:
                    zf.extractall((root / f["path"]).parent)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(blob)
            fetched += 1
            print(f"[fetch-store] {pkg['name']}/{pkg['version']}: {f['file']} → {target}")
    print(f"[fetch-store] done — {fetched} fetched, {skipped} already present")


def phase_publish_store(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Publish this store's products to the shared registry + refresh the manifest."""
    if not args.publish_version:
        raise SystemExit("[publish-store] needs --publish-version (immutable package version)")
    name, version = args.publish_name, args.publish_version
    headers = _store_auth_headers()
    root = store["report"].parent
    stage = root / ".publish-stage"
    stage.mkdir(exist_ok=True)

    entries: list[tuple[Path, str]] = []
    for sub in ("l1a", "l1b", "l1c", "l2a", "nuc"):
        for z in sorted((root / sub).glob("*.zarr")):
            zp = stage / f"{z.name}.zip"
            _zip_dir(z, zp)
            entries.append((zp, f"{sub}/{z.name}.zip"))
    for sub in ("quicklook", "report"):
        d = root / sub
        if d.is_dir() and any(d.iterdir()):
            zp = stage / f"{sub}.zip"
            _zip_dir(d, zp)
            entries.append((zp, f"{sub}.zip"))
    if not entries:
        raise SystemExit(f"[publish-store] nothing to publish under {root}")

    files = []
    for zp, rel in entries:
        flat = rel.replace("/", "__")
        _http(f"{DATASTORE_API}/{name}/{version}/{flat}", headers=headers, method="PUT", data=zp.read_bytes())
        files.append({"file": flat, "path": rel, "sha256": _sha256_file(zp), "bytes": zp.stat().st_size})
        print(f"[publish-store] {name}/{version}: {flat} ({zp.stat().st_size / 1e6:.1f} MB)")

    try:
        manifest = json.loads(_http(f"{DATASTORE_API}/manifest/latest/manifest.json").decode())
    except Exception:  # noqa: BLE001 - first publish ever
        manifest = {"schema": 1, "packages": [], "external": []}
    manifest["packages"] = [p for p in manifest["packages"] if not (p["name"] == name and p["version"] == version)]
    manifest["packages"].append(
        {"name": name, "version": version, "layer": "products", "files": files, "source": args.publish_source}
    )
    pkgs = json.loads(_http(f"{DATASTORE_PACKAGES_API}?package_name=manifest", headers=headers).decode())
    for p in pkgs:
        if p.get("version") == "latest":
            _http(f"{DATASTORE_PACKAGES_API}/{p['id']}", headers=headers, method="DELETE")
    _http(
        f"{DATASTORE_API}/manifest/latest/manifest.json",
        headers=headers,
        method="PUT",
        data=json.dumps(manifest, indent=2).encode(),
    )
    print(f"[publish-store] manifest updated — {len(manifest['packages'])} packages")


# ---------------------------------------------------------------------------
# chain helpers (lazy eopf)
# ---------------------------------------------------------------------------


def _adf(name: str, data: Any) -> Any:
    from eopf.computing.abstract import AuxiliaryDataFile

    return AuxiliaryDataFile(name=name, path=f"{name}.zarr", data_ptr=data)


def _caldb_group(store: dict[str, Path], name: str) -> Any:
    import zarr

    return zarr.open_group(str(store["caldb"] / f"{name}.zarr"), mode="r")


def _persist(product: Any, out_dir: Path, name: str) -> str:
    """Persist an EOProduct to ``out_dir/<name>.zarr`` (eopf native zarr store)."""
    from eopf.common.constants import OpeningMode
    from eopf.store.zarr import EOZarrStore

    out_dir.mkdir(parents=True, exist_ok=True)
    st = EOZarrStore(str(out_dir))
    st.open(mode=OpeningMode.CREATE_OVERWRITE, delayed_writing=False)
    try:
        st[name.removesuffix(".zarr")] = product
    finally:
        st.close()
    return str(out_dir / name)


def _l0_context(store: dict[str, Path], args: argparse.Namespace) -> dict[str, Any]:
    """Fields of the input L0's PSFD name, reused for this run's product names."""
    ocs = sorted(store["l0"].glob("*_OC.zarr")) or sorted(store["l0"].glob("*.zarr"))
    if args.l0:
        ocs = [p for p in ocs if args.l0 in p.name]
    if not ocs:
        raise SystemExit(f"[l0-decode] no L0 product under {store['l0']} (run fetch-store first)")
    if len(ocs) > 1:
        print(f"[l0-decode] {len(ocs)} L0 candidates; using {ocs[0].name} (select with --l0)")
    fields = parse_psfd_name(ocs[0].name)
    fields["l0_path"] = str(ocs[0])
    return fields


def _out_name(ctx: dict[str, Any], product_type: str, z_suffix: str | None = None) -> str:
    f = ctx["l0_fields"]
    return psfd_name(product_type, f["start"], f["duration"], f["unit"], f["relative_orbit"], z_suffix=z_suffix)


def phase_l0_decode(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Open-container (or canonical, via the unit's ground decode) L0 → L1A."""
    import zarr
    from eopf.product import EOProduct, EOVariable

    from msi_processor.computing.l0_decode.unit import L0DecodeUnit

    ctx["l0_fields"] = _l0_context(store, args)
    g = zarr.open_group(ctx["l0_fields"]["l0_path"], mode="r")
    prod = EOProduct("L0C")
    if "measurements/detector" in g:
        for b in sorted(g["measurements/detector"].array_keys()):
            prod[f"measurements/detector/{b}"] = EOVariable(
                data=np.asarray(g[f"measurements/detector/{b}"]), dims=("line", "detector")
            )
    else:  # canonical compressed-ISP layout → the unit's ground decode takes it from here
        for dname, det in g["measurements"].groups():
            for bname, grp in det.groups():
                prod[f"measurements/{dname}/{bname}/isp"] = EOVariable(data=np.asarray(grp["isp"]), dims=("byte",))
    if "conditions/time/line_time" in g:
        prod["conditions/time/line_time"] = EOVariable(data=np.asarray(g["conditions/time/line_time"]), dims=("line",))
    l1a = L0DecodeUnit("l0").run({"l0c": prod}, bit_depth=args.bit_depth)["l1a"]
    ctx["l1a"] = l1a
    ctx["bands"] = sorted(name for name, _ in l1a["measurements/detector"].items())  # type: ignore[union-attr]
    path = _persist(l1a, store["l1a"], _out_name(ctx, "S02MSIL1A"))
    print(f"[l0-decode] {len(ctx['bands'])} bands → {path}")


def phase_radiometric(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Nominal radiometric correction (cal-DB ``dark`` + ``nuc``)."""
    from msi_processor.computing.radiometric.unit import RadiometricUnit

    bands = ctx["bands"]
    nz, dz = _caldb_group(store, "nuc"), _caldb_group(store, "dark")
    adfs = {
        "nuc": _adf(
            "nuc",
            {
                "gain": {b: np.asarray(nz[f"gain/{b}"]) for b in bands},
                "offset": {b: np.asarray(nz[f"offset/{b}"]) for b in bands},
            },
        ),
        "dark": _adf("dark", {"dark_offset": {b: float(np.asarray(dz[f"dark_offset/{b}"])) for b in bands}}),
    }
    ctx["rad"] = RadiometricUnit("rad").run({"l1a": ctx["l1a"]}, adfs=adfs)["rad"]
    print(f"[radiometric] nominal NUC applied ({len(bands)} bands)")


def phase_enhancement(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """MTF compensation stage; the cal-DB carries no PSF → identity kernel (flagged)."""
    from msi_processor.computing.enhancement.unit import EnhancementUnit

    bands = ctx["bands"]
    psf = _adf("psf", {"kernel": {b: np.array([[1.0]], dtype=np.float32) for b in bands}})
    ctx["enh"] = EnhancementUnit("enh").run({"rad": ctx["rad"]}, adfs={"psf": psf}, denoise_method="none")["enh"]
    ctx.setdefault("notes", []).append("enhancement ran with an identity PSF (no psf ADF in the cal-DB)")
    print("[enhancement] identity PSF (flagged), no denoise")


def phase_toa(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """DN → radiance → TOA reflectance; persists the PSFD-named L1B."""
    from msi_processor.computing.toa.unit import ToaUnit

    bands = ctx["bands"]
    rz, sz = _caldb_group(store, "radiometric"), _caldb_group(store, "spectral")
    adfs = {
        "radiometric": _adf(
            "radiometric",
            {
                "gain": {b: float(np.asarray(rz[f"gain/{b}"])) for b in bands},
                "offset": {b: float(np.asarray(rz[f"offset/{b}"])) for b in bands},
            },
        ),
        "spectral": _adf("spectral", {"esun": {b: float(np.asarray(sz[f"esun/{b}"])) for b in bands}}),
    }
    l1b = ToaUnit("toa").run(
        {"enh": ctx["enh"]},
        adfs=adfs,
        emit_reflectance=True,
        sun_zenith_deg=args.sun_zenith_deg,
        earth_sun_distance_au=1.0,
    )["l1b"]
    ctx["l1b"] = l1b
    ctx["l1b_path"] = _persist(l1b, store["l1b"], _out_name(ctx, "S02MSIL1B"))
    print(f"[toa] L1B reflectance → {ctx['l1b_path']}")


def phase_coregister(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    from msi_processor.computing.coregistration.unit import CoregistrationUnit

    ctx["cor"] = CoregistrationUnit("cor").run({"l1b": ctx["l1b"]}, reference_band=ctx["bands"][0], seed=0)["cor"]
    print(f"[coregister] reference band {ctx['bands'][0]}")


_GDAL = [600000.0, 10.0, 0.0, 4500000.0, 0.0, -10.0]


def phase_georeference(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """GCP-refined grid resampling — DEMO geo ADFs (synthetic viewing model / flat DEM)."""
    from rasterio.crs import CRS

    from msi_processor.computing.georeference.unit import GeoreferenceUnit

    wkt = CRS.from_epsg(32635).to_wkt()
    ref = np.asarray(ctx["cor"][f"measurements/radiance/{ctx['bands'][0]}"].data, dtype=np.float32)
    adfs = {
        "viewing_model": _adf("viewing_model", {"pixel_pitch_m": 5.5e-6, "focal_length_m": 845e-6}),
        "dem": _adf("dem", {"elevation": np.zeros((10, 10), dtype=np.float32), "geotransform": _GDAL, "crs_wkt": wkt}),
        "gcp": _adf("gcp", {"image": ref, "geotransform": _GDAL, "crs_wkt": wkt}),
    }
    l1c = GeoreferenceUnit("geo").run(
        {"cor": ctx["cor"]}, adfs=adfs, resolution=10.0, gcp_reference_band=ctx["bands"][0], seed=0
    )["l1c"]
    ctx["l1c"] = l1c
    ctx["l1c_path"] = _persist(l1c, store["l1c"], _out_name(ctx, "S02MSIL1C"))
    ctx.setdefault("notes", []).append("georeference ran with DEMO geo ADFs (synthetic viewing model, flat DEM)")
    print(f"[georeference] L1C (demo geo ADFs) → {ctx['l1c_path']}")


def phase_atmospheric(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """6S BOA inversion (ingest mode) — DEMO atmospheric parameters (flagged)."""
    from msi_processor.computing.atmospheric.unit import AtmosphericUnit

    bands = ctx["bands"]
    ref0 = np.asarray(ctx["l1c"][f"measurements/reflectance/{bands[0]}"].data)
    rt_lut = {
        "path_reflectance": {b: 0.04 for b in bands},
        "transmittance": {b: 0.85 for b in bands},
        "spherical_albedo": {b: 0.08 for b in bands},
    }
    adfs = {
        "atmospheric": _adf("atmospheric", {"aot": 0.15, "water_vapour": 2.5, "ozone": 300.0, "rt_lut": rt_lut}),
        "dem": _adf("dem", {"elevation": np.zeros(ref0.shape, dtype=np.float32)}),
    }
    l2a = AtmosphericUnit("atm").run(
        {"l1c": ctx["l1c"]},
        adfs=adfs,
        param_mode="ingest",
        sun_zenith=args.sun_zenith_deg,
        view_zenith=0.0,
        relative_azimuth=0.0,
    )["l2a"]
    ctx["l2a"] = l2a
    ctx["l2a_path"] = _persist(l2a, store["l2a"], _out_name(ctx, "S02MSIL2A"))
    ctx.setdefault("notes", []).append("atmospheric ran in ingest mode with DEMO parameters (aot/wv/o3/rt_lut)")
    print(f"[atmospheric] L2A (demo params) → {ctx['l2a_path']}")


def phase_pansharpen(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    from msi_processor.computing.pansharpen.unit import PansharpenUnit

    if "PAN" not in ctx["bands"]:
        print("[pansharpen] skipped (no PAN band in the input)")
        return
    pan = PansharpenUnit("pan").run({"l2a": ctx["l2a"]}, pan_band="PAN")["pan"]
    _persist(pan, store["l2a"], _out_name(ctx, "S02MSIL2A", z_suffix="PAN"))
    print("[pansharpen] PAN-fused derivative persisted")


def phase_radiometric_cal(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Calibration mode: derive the NUC from the producer's dark+flatfield acquisitions."""
    import zarr

    from msi_processor.computing.radiometric.unit import RadiometricUnit

    caldir = store["inputs"] / "calibration"
    if not (caldir / "flatfield.zarr").exists():
        raise SystemExit(f"[radiometric-cal] no calibration acquisitions under {caldir} (fetch-store first)")
    flat = zarr.open_group(str(caldir / "flatfield.zarr"), mode="r")
    dark = zarr.open_group(str(caldir / "dark.zarr"), mode="r")
    bands = [b for b in ctx["bands"] if b in flat.array_keys()]
    adfs = {
        "dark": _adf(
            "dark",
            {
                "frame": {b: np.asarray(dark[f"frame/{b}"]) for b in bands},
                "dark_offset": {b: float(np.asarray(dark[f"dark_offset/{b}"])) for b in bands},
            },
        ),
        "flatfield": _adf("flatfield", {b: np.asarray(flat[b]) for b in bands}),
    }
    outputs = RadiometricUnit("rad").run({"l1a": ctx["l1a"]}, adfs=adfs, mode="calibration")
    ctx["nuc_derived"] = outputs["nuc"]
    ctx["cal_bands"] = bands
    path = _persist(outputs["nuc"], store["nuc"], _out_name(ctx, "S02MSIL1A", z_suffix="NUC"))
    print(f"[radiometric-cal] derived NUC ({len(bands)} bands) → {path}")


def phase_cal_validate(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Consumer-derived NUC vs the producer-derived coefficients (closing the cal loop)."""
    import zarr

    prod_nuc = zarr.open_group(str(store["inputs"] / "calibration" / "nuc.zarr"), mode="r")
    res: dict[str, Any] = {}
    for b in ctx["cal_bands"]:
        g_c = np.asarray(ctx["nuc_derived"][f"gain/{b}"].data, dtype=np.float64)
        g_p = np.asarray(prod_nuc[f"gain/{b}"], dtype=np.float64)
        o_c = np.asarray(ctx["nuc_derived"][f"offset/{b}"].data, dtype=np.float64)
        o_p = np.asarray(prod_nuc[f"offset/{b}"], dtype=np.float64)
        res[b] = {
            "gain_rmse": float(np.sqrt(np.mean((g_c - g_p) ** 2))),
            "gain_max_rel": float(np.max(np.abs(g_c - g_p) / np.abs(g_p))),
            "offset_rmse": float(np.sqrt(np.mean((o_c - o_p) ** 2))),
        }
        print(f"[cal-validate] {b}: gain RMSE={res[b]['gain_rmse']:.4g} max_rel={res[b]['gain_max_rel']:.3%}")
    res["_note"] = (
        "consumer derives gain = mean(F)/colmean(F) (no dark subtraction); the producer's "
        "two-point NUC subtracts the dark acquisition — small systematic differences are expected"
    )
    _jdump(res, store["report"] / "cal_validate.json")


def phase_stats(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    """Per-band QA statistics of the L1B (ALG-QA-*, SDD <5.4.1>) → markdown + json."""
    import zarr

    from msi_processor.common.metrics import compute_metrics

    products = sorted(store["l1b"].glob("*.zarr"))
    if not products:
        raise SystemExit(f"[stats] no L1B product under {store['l1b']}")
    g = zarr.open_group(str(products[-1]), mode="r")["measurements/reflectance"]
    lines = [
        f"Product : {products[-1].name}  group=measurements/reflectance",
        "",
        "| Band | mean | std | variance | SNR (dB) |",
        "|---|---|---|---|---|",
    ]
    stats: dict[str, Any] = {}
    for b in sorted(g.array_keys()):
        a = np.asarray(g[b])
        ms = compute_metrics(a, bit_depth=args.bit_depth)
        stats[b] = {"mean": float(a.mean()), "std": float(a.std()), "variance": ms.variance, "snr_db": ms.snr}
        lines.append(f"| {b} | {a.mean():.4f} | {a.std():.4f} | {ms.variance:.6f} | {ms.snr:.1f} |")
    md = "\n".join(lines) + "\n"
    (store["report"] / "product_stats.md").write_text(md)
    _jdump(stats, store["report"] / "product_stats.json")
    print(md)


def phase_report(store: dict[str, Path], ctx: dict[str, Any], args: argparse.Namespace) -> None:
    rep = store["report"]
    lines = [f"# msi-processor pipeline report ({args.mode} mode)", ""]
    if ctx.get("l0_fields"):
        lines += [f"- L0 input: `{Path(ctx['l0_fields']['l0_path']).name}`"]
    for key in ("l1b_path", "l1c_path", "l2a_path"):
        if ctx.get(key):
            lines += [f"- {key.split('_')[0]}: `{Path(ctx[key]).name}`"]
    for note in ctx.get("notes", []):
        lines += [f"- NOTE: {note}"]
    for name in ("product_stats", "cal_validate"):
        p = rep / f"{name}.json"
        if p.exists():
            lines += ["", f"## {name}", "", "```json", p.read_text().rstrip(), "```"]
    (rep / "pipeline_report.md").write_text("\n".join(lines) + "\n")
    print(f"[report] {rep / 'pipeline_report.md'}")


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("store", help="data-store root (working copy of ipf/data-store)")
    ap.add_argument("--mode", default="nominal", choices=("nominal", "calibration"))
    ap.add_argument("--full", action="store_true", help="nominal mode: continue to L1C/L2A (demo geo ADFs)")
    ap.add_argument("--phases", default=None, help=f"comma list from {PHASES}")
    ap.add_argument("--sun-zenith-deg", type=float, default=35.0, dest="sun_zenith_deg")
    ap.add_argument("--bit-depth", type=int, default=12, dest="bit_depth")
    ap.add_argument("--l0", default=None, help="substring selecting the input L0 when several are present")
    ap.add_argument(
        "--fetch-packages",
        default="synthetic,calibration",
        dest="fetch_packages",
        help="comma list of data-store packages fetch-store pulls (empty = all)",
    )
    ap.add_argument("--publish-name", default="msi-products", dest="publish_name")
    ap.add_argument("--publish-version", default=None, dest="publish_version")
    ap.add_argument("--publish-source", default="msi-processor run_pipeline", dest="publish_source")
    args = ap.parse_args(argv)

    if args.phases:
        todo = [p.strip() for p in args.phases.split(",") if p.strip()]
    elif args.mode == "calibration":
        todo = list(CALIBRATION_PHASES)
    else:
        todo = list(NOMINAL_PHASES)
        if args.full:
            cut = todo.index("stats")
            todo = todo[:cut] + FULL_EXTRA + todo[cut:]
    unknown = [p for p in todo if p not in PHASES]
    if unknown:
        ap.error(f"unknown phases: {unknown} (choose from {PHASES})")

    store = _store_paths(Path(os.path.expanduser(args.store)))
    ctx: dict[str, Any] = {"started_utc": datetime.utcnow().isoformat()}
    fns = {
        "fetch-store": phase_fetch_store,
        "l0-decode": phase_l0_decode,
        "radiometric": phase_radiometric,
        "enhancement": phase_enhancement,
        "toa": phase_toa,
        "coregister": phase_coregister,
        "georeference": phase_georeference,
        "atmospheric": phase_atmospheric,
        "pansharpen": phase_pansharpen,
        "radiometric-cal": phase_radiometric_cal,
        "cal-validate": phase_cal_validate,
        "stats": phase_stats,
        "report": phase_report,
        "publish-store": phase_publish_store,
    }
    for p in PHASES:
        if p in todo:
            fns[p](store, ctx, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
