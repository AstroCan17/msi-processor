.. Copyright 2026 ESA

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Pipeline driver
===============

Everything in this repository runs through the **single driver**
``scripts/run_pipeline.py``: a phase-structured, idempotent pipeline over one
data-store working copy. Inputs are pulled from the shared
`ipf/data-store <https://gitlab.eopf.copernicus.eu/ipf/data-store>`_ registry
(``fetch-store``, sha256-verified) and every product carries an EOPF PSFD §3 name.

Modes
-----

.. list-table::
   :header-rows: 1

   * - Mode
     - Phases
     - Products
   * - ``--mode nominal`` (default)
     - ``fetch-store → l0-decode → radiometric → enhancement → toa → stats → report``
     - PSFD-named L1A + L1B (TOA reflectance) + the per-band QA statistics table
   * - nominal + ``--full``
     - … ``toa → coregister → georeference → atmospheric → pansharpen`` …
     - \+ L1C / L2A (demo geo/atmospheric ADFs — flagged in the report)
   * - ``--mode calibration``
     - ``fetch-store → l0-decode → radiometric-cal → cal-validate → report``
     - the derived-NUC product (PSFD ``_NUC``) + the coefficient cross-check

Usage
-----

.. code-block:: bash

   python scripts/run_pipeline.py <store>                        # nominal chain
   python scripts/run_pipeline.py <store> --full                 # + L1C/L2A (demo geo ADFs)
   python scripts/run_pipeline.py <store> --mode calibration     # derive + cross-validate the NUC
   python scripts/run_pipeline.py <store> --phases stats         # QA table of the persisted L1B
   python scripts/run_pipeline.py <store> --phases publish-store --publish-version <X.Y.Z>

Phases are idempotent and individually selectable (``--phases``); each writes its
evidence under ``<store>/report/`` and the ``report`` phase assembles
``pipeline_report.md``. Chain phases need the eopf environment; ``fetch-store`` /
``stats`` / ``report`` / ``publish-store`` run with numpy+zarr alone.

Calibration mode
----------------

The calibration mode consumes the producer's raw calibration *acquisitions*
(``inputs/calibration/{dark,flatfield}.zarr`` from the data-store), derives the NUC in
the ``radiometric`` unit's **calibration mode** and cross-checks it against the
producer-derived coefficients (``cal-validate``). On the shared synthetic set the two
derivations agree to float32 precision (per-band gain RMSE ≈ 6e-08) — the
producer-acquires / consumer-derives loop closes over the data-store.

CI
--

The manual **pipeline-nominal** and **pipeline-calibration** jobs (integration-tests
stage) run the two modes end-to-end against the shared data-store and artifact the
``report/`` evidence; see the :doc:`results page <results>` for the current numbers.
