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
     - ``fetch-store → cal-decode → radiometric-cal → cal-validate → report``
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

The calibration campaign arrives **exactly like any downlink**: the producer packages the
dark (``S02MSIDCA``, operation mode ``DASC``) and Lambertian sun-diffuser (``S02MSISCA``,
``ABSR``) acquisitions as canonical L0 products (CCSDS-122 compressed ISPs, PSFD names,
operation-mode metadata). ``cal-decode`` ground-decodes both through ``L0DecodeUnit``
(the REQ-F-L0-06 path in operational use), ``radiometric-cal`` derives the NUC in the
``radiometric`` unit's **calibration mode** on the diffuser datatake, and ``cal-validate``
cross-checks it against the producer-derived cal-DB — both sides derive from the same
(bit-exactly carried) frames, so agreement to float32 precision is expected. The
producer-acquires → downlink → consumer-derives loop closes over the data-store.

CI
--

The manual **pipeline-nominal** and **pipeline-calibration** jobs (integration-tests
stage) run the two modes end-to-end against the shared data-store and artifact the
``report/`` evidence; see the :doc:`results page <results>` for the current numbers.
