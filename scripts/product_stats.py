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
"""Per-band quality statistics of a produced EOPF product (results-page generator).

Reads an L1B/L2A Zarr product written by the processing chain and prints a markdown
table of the non-referential QA metrics (ALG-QA-*, SDD <5.4.1>) per band: mean, std,
variance and SNR (dB), via :mod:`msi_processor.common.metrics`. With ``--reference``
(an aligned truth product) it adds the referential metrics (RMSE/PSNR/MSE) — the AR
scenario; without it those stay out (their acceptance is AR-gated, see the V&V report).

Usage:
    python scripts/product_stats.py <product.zarr> [--group measurements/reflectance]
        [--reference <truth.zarr>] [--bit-depth 12]

Dependencies: numpy + zarr (+ the metrics module; imported from the installed package
or, as a fallback, straight from the repository tree so no eopf install is required).
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import zarr

try:
    from msi_processor.common.metrics import compute_metrics
except Exception:  # pragma: no cover - fallback when eopf isn't installed
    import importlib.util

    _p = os.path.join(os.path.dirname(__file__), "..", "msi_processor", "common", "metrics.py")
    _spec = importlib.util.spec_from_file_location("_metrics", _p)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    compute_metrics = _m.compute_metrics


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("product")
    ap.add_argument("--group", default="measurements/reflectance")
    ap.add_argument("--reference", default=None)
    ap.add_argument("--bit-depth", type=int, default=12)
    args = ap.parse_args()

    g = zarr.open_group(args.product, mode="r")[args.group]
    ref = zarr.open_group(args.reference, mode="r")[args.group] if args.reference else None
    bands = sorted(g.array_keys()) if hasattr(g, "array_keys") else sorted(g.keys())

    header = "| Band | mean | std | variance | SNR (dB) |"
    sep = "|---|---|---|---|---|"
    if ref is not None:
        header += " RMSE | PSNR (dB) |"
        sep += "---|---|"
    print(f"Product : {os.path.basename(os.path.normpath(args.product))}  group={args.group}  "
          f"bands={len(bands)}")
    print()
    print(header)
    print(sep)
    for b in bands:
        a = np.asarray(g[b])
        r = np.asarray(ref[b]) if ref is not None else None
        ms = compute_metrics(a, reference=r, bit_depth=args.bit_depth)
        row = (f"| {b} | {float(a.mean()):.4f} | {float(a.std()):.4f} | "
               f"{ms.variance:.6f} | {ms.snr:.1f} |")
        if ref is not None:
            row += f" {ms.rmse:.6f} | {ms.psnr:.1f} |"
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
