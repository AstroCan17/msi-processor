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
"""Unit tests of the pipeline driver's eopf-free parts (naming, store, stats)."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pytest

zarr = pytest.importorskip("zarr")

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_pipeline.py"
_spec = importlib.util.spec_from_file_location("msi_run_pipeline", _SCRIPT)
drv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drv)

pytestmark = pytest.mark.unit


def test_psfd_name_round_trips():
    name = drv.psfd_name("S02MSIL1B", "20240403T102415", 1, "A", 45)
    fields = drv.parse_psfd_name(name)
    assert fields["product_type"] == "S02MSIL1B"
    assert fields["start"] == "20240403T102415"
    assert (fields["duration"], fields["unit"], fields["relative_orbit"]) == (1, "A", 45)
    with_suffix = drv.psfd_name("S02MSIL1A", "20240403T102415", 1, "A", 45, z_suffix="NUC")
    assert drv.parse_psfd_name(with_suffix)["z_suffix"] == "NUC"
    assert {"S02MSIL1C", "S02MSIL2A"} <= set(drv.TYPE_CODES)
    with pytest.raises(ValueError):
        drv.psfd_name("S02MSIXXX", "20240403T102415", 1, "A", 45)


def test_store_paths_layout(tmp_path):
    store = drv._store_paths(tmp_path / "store")
    assert set(store) == {"inputs", "caldb", "l0", "l1a", "l1b", "l1c", "l2a", "nuc", "quicklook", "report"}
    assert all(p.is_dir() for p in store.values())


def test_default_phase_sets():
    assert drv.NOMINAL_PHASES[0] == "fetch-store" and drv.NOMINAL_PHASES[-1] == "report"
    assert "radiometric-cal" in drv.CALIBRATION_PHASES and "cal-validate" in drv.CALIBRATION_PHASES
    assert all(p in drv.PHASES for p in drv.NOMINAL_PHASES + drv.CALIBRATION_PHASES + drv.FULL_EXTRA)


def test_stats_phase_writes_table(tmp_path):
    store = drv._store_paths(tmp_path / "store")
    g = zarr.open_group(str(store["l1b"] / "S02MSIL1B_20240403T102415_0001_A045_T145.zarr"), mode="w")
    refl = g.create_group("measurements").create_group("reflectance")
    rng = np.random.default_rng(0)
    for b in ("B02", "B03"):
        refl[b] = rng.uniform(0.1, 0.3, size=(16, 16)).astype(np.float32)
    args = argparse.Namespace(bit_depth=12)
    drv.phase_stats(store, {}, args)
    md = (store["report"] / "product_stats.md").read_text()
    assert "| B02 |" in md and "| B03 |" in md and "SNR (dB)" in md
    stats = drv._jload(store["report"] / "product_stats.json")
    assert 0.1 < stats["B02"]["mean"] < 0.3
