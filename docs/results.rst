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

Results
=======

Products of the real processing chain, with per-band quality statistics and their
reading. Two validated end-to-end runs back this page; both consume the **Sentinel-2
MSI Synthetic Raw Data Generator**'s products as input.

L0 → L1B — real chain, persisted product
----------------------------------------

The generator's open-container L0 + calibration-database ADFs pushed through
``l0_decode → radiometric → enhancement → toa`` (``eopf == 2.8.1``, ``nominal`` mode,
``emit_reflectance``): a persisted **L1B TOA-reflectance** EOPF product.

.. figure:: _static/results/l1b_rgb.png
   :alt: L1B TOA reflectance quicklook (RGB = B04/B03/B02)
   :width: 60%

   L1B TOA reflectance, RGB = B04/B03/B02, per-channel 2–98 % percentile stretch.
   The demo scene is a flat field, so the stretch deliberately reveals the residual
   *texture*: per-column striping is the impressed PRNU pattern, the speckle is
   shot/read noise.

Per-band statistics (the pipeline's ``stats`` phase, the non-referential ALG-QA metrics
of ``msi_processor/common/metrics.py`` — SDD <5.4.1>; produced by the manual
``product-stats`` CI job, 2026-07-02):

.. list-table::
   :header-rows: 1

   * - Band
     - mean (reflectance)
     - std
     - variance
     - SNR (dB)
   * - B02
     - 0.1753
     - 0.0053
     - 0.000029
     - 30.3
   * - B03
     - 0.1888
     - 0.0066
     - 0.000044
     - 29.1
   * - B04
     - 0.1911
     - 0.0070
     - 0.000049
     - 28.7
   * - B08
     - 0.2648
     - 0.0094
     - 0.000089
     - 29.0
   * - B11
     - 0.0434
     - 0.0017
     - 0.000003
     - 28.3
   * - B12
     - 0.0535
     - 0.0019
     - 0.000004
     - 28.8

Reading the numbers
-------------------

* **Reflectance means** sit at the levels impressed by the generator's flat-field
  scene (≈ 0.19 VNIR / 0.27 NIR / 0.05 SWIR) — the absolute radiometric scale
  survives the full chain (DN → radiance → reflectance) unchanged.
* **SNR** is scene-limited, not instrument-limited: on a flat field the standard
  deviation *is* the residual instrument texture (uncorrected PRNU + noise), so the
  per-band SNR ranks the bands by their noise-model α/β and PRNU amplitude.
* **Variance** complements SNR as the raw second moment used by the QA stage
  (``ALG-QA-*``); both are computed product-side with no reference.

Validation status
-----------------

* The chain producing these numbers is CI-verified: 8 of 8 processing units
  implemented and green (see the :doc:`SUITR <compliance/suitr-unit-integration-test-report>`
  and the live :doc:`CI test report <suitr>`).
* A second, sharper end-to-end result — the real-L1A **bit-identity** run through
  ``l0_decode`` (L1A′ ≡ L1A, 13/13 bands) — is documented in the generator's
  validation pages and its qualification is summarised in the
  :doc:`QR report <compliance/qr-qualification-review-report>`.
* **AR-gated figures:** the *referential* accuracy metrics (L1B radiometric RMSE
  vs a calibrated reference — REQ-P-01 ``RAD_ACC``; geometric ``GEO_CE90`` /
  ``BAND_COREG`` — REQ-P-02; ``BOA_ACC`` — REQ-P-03) are validated on operator data
  at AR and are deliberately **not** quoted here (see the
  :doc:`V&V report <compliance/vv-report>`). the ``stats`` phase computes them
  once a reference product is available.

Reproduce
---------

Run the manual **pipeline-nominal** CI job (integration-tests stage): the repository's
single driver pulls the inputs from the shared ``ipf/data-store`` registry, runs
``l0-decode → radiometric → enhancement → toa → stats`` and artifacts the statistics
table. Locally (eopf environment): ``python scripts/run_pipeline.py <store>``;
``--mode calibration`` derives and cross-validates the NUC instead.
