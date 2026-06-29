# Software Release Note (SRN / SRelD)

| Field | Value |
|---|---|
| **Document** | SRN — Software Release Note (Software Release Document, SRelD) |
| **DRD ref** | ECSS-E-ST-40C Rev.1 — Software Release Document (SRelD); ECSS-M-ST-40C (configuration management); ECSS-Q-ST-80C Rev.2 (software delivery, acceptance & release) |
| **Container** | Released-software documentation set — `compliance/drd/` (source); published as `docs/srn.md` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | QR (Qualification Review) |
| **Status** | Issued at QR |

> This document is the **Software Release Note (SRN)** — the Software Release Document (SRelD) of
> ECSS-E-ST-40C Rev.1 — for the `msi-processor` software configuration item (SCI). It identifies the
> **release candidate** proposed for qualification (version **v0.1.0-rc1**, referenced to the QR
> configuration baseline commit **`d140599`**), states its **scope** (the `L0c`→`L2A` processing chain
> plus the optional pan-sharpen derivative, **8 of 8** processing units) and **contents** (the
> `msi_processor` package modules and the ECSS document set), records the **runtime dependencies** and
> the **build/install** procedure, enumerates the **known problems and limitations** carried into the
> release, summarises the **changelog** from SRR to QR, and reports the **verification status** at the
> release point. It is a delivery/configuration record, **not** a requirements (SRS, RD-4), design
> (SDD, RD-9) or verification-results (SVR, RD-12) document; those are cross-referenced rather than
> restated. The footprint is tailored to a **Category C, single-developer** ground-segment processor
> whose **code is public but whose raw `L0` data and instrument calibration are private** (RD-4 SRS
> <5.1>/<5.8>). The companion **Software Configuration File (SCF, RD-19)** and **Configuration Item
> Data List (CIDL, RD-20)** record the SCI inventory and the controlled-document list; this SRN is
> their change/known-problems counterpart for the released version.

**DRD clause coverage.** Where this SRN satisfies each SRelD DRD clause:

| SRelD clause | Topic | This document |
|---|---|---|
| SRelD <1> | Introduction | <1> |
| (house style) | Applicable / reference documents; terms | <2>, <3> |
| SRelD <2> | Software release overview (identification, version, contents, dependencies, build/install, verification status) | <4> (<4.1>..<4.6>) |
| SRelD <3.1> | Status of the software — evolution since previous version (changelog) | <5.1> |
| SRelD <3.2> | Status of the software — known problems or limitations; status of SPRs/SCRs/waivers | <5.2> |
| SRelD <4> | Advice for use of the software configuration item | <6> |
| SRelD <5> | On-going changes | <7> |

---

## <1> Introduction

**Purpose.** This SRN announces and characterises the **qualification release candidate** of
`msi-processor`, a generic high-resolution **pushbroom multispectral imager (MSI)** ground-segment
processor that transforms downlinked RAW **Level-0 (`L0c`)** data into calibrated, enhanced,
orthorectified and atmospherically corrected products up to **Level-2A (`L2A`)** on the ESA EOPF
**Common Processor Model (CPM)** runtime (`eopf == 2.8.1`, Zarr). It provides, per the SRelD DRD: the
**version** of the release and the SCI identity under configuration control; an **overview of the
contents** (code + documents); the **status of SPRs, SCRs and software waivers/deviations (SW&D)**;
the **known problems and limitations**; and **advice for use**.

**Objective.** To give the reviewer and the receiving party (the hosting EOPF ground segment) a
single, authoritative record of *what is being released at QR, in which configuration, with which
verification evidence, and subject to which limitations* — so that the QR exit criteria (SReVP,
RD-16: SCI under configuration control + released SRelD/SRN; SPR/NCR status checked; readiness to
proceed to AR) can be assessed against an explicit release statement.

**Content.** Clause <2> lists applicable and reference documents; <3> adds release-specific terms.
Clause <4> is the **software release overview**: release identification (<4.1>), scope (<4.2>),
contents (<4.3>), runtime dependencies and environment (<4.4>), build and installation (<4.5>) and
verification status at release (<4.6>). Clause <5> is the **status of the software**: the SRR→QR
changelog (<5.1>) and the known problems/limitations with SPR/NCR/waiver status (<5.2>). Clause <6>
gives advice for use; clause <7> records the on-going (planned) evolution toward AR.

**Reason for preparation.** `msi-processor` is an **integration and ECSS-productisation** effort
(RD-1 §1): mature processing algorithms (RD-14 prior work; RD-7 ATBD) are productised on the EOPF CPM
and verified, rather than researched anew. The lifecycle has passed **SRR, PDR and CDR** (all
baselined to `main`); **this package is the QR (Qualification Review)** data package, and this SRN is
its release statement. The SRN is the parent of the formal tagging/delivery action taken at the
**release decision** (AR), and the change/known-problems source for the SCF (RD-19) and CIDL (RD-20).

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software (Software Release Document; Annex F SDD; Annex I/J V&V; Annex K SUITP; Annex M SVR) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space configuration and information management | ECSS-M-ST-40C Rev.1 |
| AD-3 | ECSS Space product assurance — Software (delivery, acceptance & release; product quality) | ECSS-Q-ST-80C Rev.2 |
| AD-4 | EOPF CPM — Product Structure & Format Definition (PSFD) / data model | EOPF CPM docs (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Control Document (ICD) — `ICD-IF-*` | `compliance/drd/icd-interface-control.md` |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — `DPM-M-*`, `DPM-PRM/ADF/BKP-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V Plan (SVerP/SValP merged) | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Software Design Document (SDD, detailed/CDR) — `C-*`, `IF-*` | `compliance/drd/sdd-software-design.md` |
| RD-10 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-11 | `msi-processor` Traceability matrix (RTM; REQ↔design↔test) | `compliance/traceability/traceability-matrix.md` |
| RD-12 | `msi-processor` Software Verification Report (SVR, Annex M) — V&V results record | `compliance/drd/vv-report.md` (QR) |
| RD-13 | `msi-processor` Risk Register | `compliance/drd/risk-register.md` |
| RD-14 | Prior work — multispectral pushbroom preprocessing pipeline (`level_0`, `level_1`, `band_coreg`, `georeferencing_v1`, `pansharp`, `metrics_ips`) | see SRF (RD-10) |
| RD-15 | EOPF CPM API documentation (`EOProduct`, `EOProcessingUnit`, `EOZarrStore`, triggering) | EOPF CPM (`eopf == 2.8.1`) |
| RD-16 | `msi-processor` Software Review Plan (SReVP) | `compliance/drd/srevp-software-review-plan.md` |
| RD-17 | `msi-processor` Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |
| RD-18 | `msi-processor` SUITP (Annex K — unit/integration test specs & procedures) | `compliance/drd/suitp-unit-integration-test-plan.md` |
| RD-19 | `msi-processor` Software Configuration File (SCF) | `docs/scf.md` |
| RD-20 | `msi-processor` Configuration Item Data List (CIDL) | `docs/cidl.md` |
| RD-21 | `msi-processor` Software User Manual (SUM, start) | `docs/sum/` |
| RD-22 | `msi-processor` Software Installation Manual (SIM) | `docs/sim.md` |

---

## <3> Terms, definitions and abbreviated terms

The SDP §3, SSS <3>, SRS <3>, SDD <3> and V&V Plan <3> glossaries apply in full. Only terms specific
to this SRN and not defined there are added.

| Term / abbr. | Definition |
|---|---|
| SCI | Software Configuration Item — the released `msi-processor` software and its baselined documentation |
| SRN / SRelD | Software Release Note / Software Release Document (this document) |
| SCF | Software Configuration File (RD-19) — SCI inventory and composition |
| CIDL | Configuration Item Data List (RD-20) — the list of controlled documents for the SCI |
| RC | Release candidate — a version proposed for qualification, tagged only at the release decision |
| QR / AR | Qualification Review / Acceptance Review (the milestones this SRN spans) |
| SPR | Software Problem Report (a recorded defect/anomaly) |
| SCR | Software Change Request |
| SW&D | Software Waiver and Deviation (an approved departure from a requirement/gate) |
| NCR | Non-Conformance Report |
| `[impl]` | A design body whose finalisation is legitimately deferred to (or after) implementation; here, all `[impl]` items are **fail-stop** and not on the operational baseline (SDD RD-9; see <5.2.1>) |
| Tier A / B / C | V&V three-tier scheme (RD-8 §4): A = deterministic synthetic unit tests in public CI (blocking); B = local real-RAW integration (non-blocking/skipped in public CI); C = reference/validation-data numeric budgets (local only) |
| Budget parameter | A private per-profile numeric tolerance (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`, `MEM_BUDGET`) held in the calibration store (RD-4 SRS <5.1>) |

---

## <4> Software release overview

### <4.1> Release identification

| Item | Value |
|---|---|
| Software configuration item | `msi-processor` (`msi_processor` Python package) |
| Repository | `gitlab.eopf.copernicus.eu/ipf/msi-processor` |
| **Proposed release-candidate version** | **`v0.1.0-rc1`** (qualification release candidate) |
| **QR configuration baseline commit** | **`d140599`** (`main`) |
| Baseline pipeline | CI pipeline **30730** on `main` — **success** (see <4.6>) |
| Git tag | **none yet** — applied at the release decision (see tagging policy below) |
| Branch | `main` (the SCI is the full content of `main` at the baseline commit; SCF RD-19) |
| Licence | Apache-2.0 (`LICENSE`); `pyproject.toml` declares `Private :: Do Not Upload` (not for public package indices) |

**Version mechanism.** The package version is **resolved dynamically by the flit build backend**:
`pyproject.toml` declares `dynamic = ["version", "description"]` and builds with `flit_core`
(`build-system.requires = ["flit_core >=3.2,<4"]`). The released version string is bound to the
annotated **Git tag** created at the release decision.

**Tagging policy (release action deferred).** **No Git tag exists on the QR baseline yet.** Tagging
is the formal **release action**, performed at the **AR / release decision**, not at authoring time;
this SRN therefore records the *proposed* release-candidate identity **`v0.1.0-rc1`** referenced to
the QR configuration baseline commit **`d140599`**. At the release decision an annotated tag
`v0.1.0-rc1` is created on `d140599`, the SCF (RD-19) and CIDL (RD-20) are updated to cite the tag,
and the delivery jobs publish the tagged wheel and versioned documentation. This SRN must not be read
as evidence that a tag already exists.

### <4.2> Release scope

The release delivers the complete **`L0c`→`L2A`** ground-processing chain, plus the **optional**
post-`L2A` pan-sharpen derivative — **8 of 8** processing units implemented on `main` and CI-green.
Each unit follows the SDD pattern of a **pure, framework-independent algorithmic core** + a thin
**`EOProcessingUnit` wrapper** + a **CPM computing-model JSON** (RD-9; RD-4 REQ-D-03).

| # | Processing unit | Output level | Role |
|---|---|---|---|
| 1 | `l0_decode` | L1A | Level-0 (`L0c`) decode → L1A image arrays + `EOProduct` structure |
| 2 | `radiometric` | L1A | Dark/gain/offset correction; bad-pixel & saturation handling + QA flags |
| 3 | `enhancement` | L1B | **MTF compensation (mandatory, always applied)** + denoise (per profile) |
| 4 | `toa` | L1B | DN → TOA radiance/reflectance |
| 5 | `coregistration` | L1B→L1C | Inter-band co-registration (feature matching + homography) |
| 6 | `georeference` | L1C | Geolocation / cartographic referencing (GCP reference-image refinement path) |
| 7 | `atmospheric` | L2A | Atmospheric correction → surface (BOA) reflectance |
| 8 | `pansharpen` | post-`L2A` (optional) | MS+PAN fusion derivative (operational method: `simple_mean`) |

The chain is runnable end-to-end and at breakpoints/sub-chains (RD-4 REQ-F-ORC-01) via the CPM
computing-model and triggering payloads (RD-15). The operational baseline runs the documented,
public processing path; the deferred `[impl]` bodies are never executed by it (<5.2.1>).

### <4.3> Contents of the release

**(a) Code — the `msi_processor` package.**

| Subpackage / module | Contents |
|---|---|
| `msi_processor/computing/` | The 8 processing units (`l0_decode`, `radiometric`, `enhancement`, `toa`, `coregistration`, `georeference`, `atmospheric`, `pansharpen`), each providing `core.py` (pure core), `unit.py` (`EOProcessingUnit` wrapper), `models/` (CPM computing-model JSON) and `__init__.py` |
| `msi_processor/common/` | `types.py` (shared data types) and `metrics.py` (QA metrics — SNR/RMSE/PSNR/MSE/variance, productised from `metrics_ips`, RD-14) |
| `msi_processor/sensors/` | `profile.py` (the externalised, sensor-agnostic processing **profile** — REQ-D-07, REQ-AD-01) |
| `msi_processor/exceptions/` | `errors.py` and `warnings.py` (typed error/warning classes, fail-stop support) |
| `msi_processor/__init__.py` | Package root |

This realises the **21 design components (`C-*`)**, **11 DPM modules (`DPM-M-*`)** and **33
algorithms (`ALG-*`)** of the baselined design (RD-9 / RD-6 / RD-7), allocating the **100** SRS
requirements (RD-4).

**(b) Tests.** `tests/ut/` (unit — `computing/`, `common/`, `sensors/`) and `tests/it/computing/`
(integration — full-chain), executed per the SUITP (RD-18); results in <4.6>.

**(c) Documentation set (DRD deliverables of the SCI).** The baselined ECSS documents listed in the
CIDL (RD-20): SDP (RD-1), SSS (RD-2), IRD (RD-3), SRS (RD-4), ICD (RD-5), DPM (RD-6), ATBD (RD-7),
V&V Plan (RD-8), SDD (RD-9), SRF (RD-10), traceability matrix/RTM (RD-11), SVR (RD-12), Risk Register
(RD-13), SReVP (RD-16), SPAP (RD-17), SUITP (RD-18), and the QR delivery documents **SCF (RD-19),
CIDL (RD-20), SUM (start, RD-21), SIM (RD-22)** and **this SRN**. Sphinx autodoc is wired in
`docs/conf.py` and the documentation builds in CI (job `sphinx-build`, <4.6>).

**(d) Build / CI configuration.** `pyproject.toml`, `.gitlab-ci.yml`, `Dockerfile`, and the gate
configs (`.flake8`, `.mypy.ini`, `bandit.yml`, `.coveragerc`, `.hadolint.yml`,
`.pre-commit-config.yaml`).

### <4.4> Runtime dependencies and execution environment

**Runtime dependencies** (`pyproject.toml` `[project].dependencies`):

| Dependency | Constraint | Role |
|---|---|---|
| `eopf` | **`== 2.8.1`** (pinned) | ESA EOPF CPM runtime — `EOProduct`, `EOProcessingUnit`, `EOZarrStore`, triggering (RD-15); the pin matches the SDE `cpm-build-environment` image (REQ-R-03, REQ-M-03) |
| `opencv-python-headless` | `>= 4.8` | Feature matching / homography / warping for co-registration and pan-sharpen (ALG; SDD <5.4.6>); headless wheel (no display); ships PEP 561 stubs |
| `rasterio` | `>= 1.3` | GDAL/PROJ binding for the cartographic affine geotransform + reprojection in `georeference` (ALG-GEO-RESAMP; SDD <5.4.7>); also an `eopf` transitive dependency, declared explicitly as it is imported directly |

**Interpreter.** Python **`>= 3.11`** (`requires-python = ">=3.11"`; classified for CPython 3.11).
**Optional extras:** `cluster-plugin` (`eopf[cluster-plugin] >= 1.5.0`) and `tests`
(`eopf[tests] >= 1.5.0`).

**Operational environment.** The EOPF SDE container
(`registry.eopf.copernicus.eu/sde/cpm-build-environment`, `eopf == 2.8.1`, Python 3.11) is the
reference runtime; the same code runs unchanged on an x86-64 Linux workstation (CPU-only, no GPU;
REQ-R-01) against a POSIX filesystem or an S3-compatible object store (REQ-R-02). The public CI
runner is a **single Studio VM with a SHELL executor** (no container runtime, Dask gateway or S3;
`image:` directives are ignored), which is the reason for the non-blocking jobs of <5.2.3>.

### <4.5> Build and installation

The package builds to a **wheel via the flit backend** and installs with `pip`:

- **Build:** `python -m build` (or `flit build`) → a PEP 517 wheel (CI job `build-package`, green at
  the baseline). The version is taken from the Git tag at build time (<4.1>).
- **Install (operational):** `pip install .` inside the EOPF SDE environment (or `pip install
  msi_processor-<version>-py3-none-any.whl`), which pulls `eopf == 2.8.1`,
  `opencv-python-headless >= 4.8` and `rasterio >= 1.3`. A clean `pip install` is the acceptance
  installation check (RD-4 REQ-AD-05; V&V Plan VT-8). Detailed steps are in the SIM (RD-22).
- **Install (development):** `pip install .[tests]` for the test extra; `pre-commit install` for the
  local lint/format hooks.

The package is **not** published to a public index (`pyproject.toml` carries
`Private :: Do Not Upload`); delivery is via the EOPF Git repository and the SDE-internal
artefact/registry targets at the release decision.

### <4.6> Verification status at release

The QR baseline (`d140599`) is **CI-green**: **CI pipeline 30730** on `main` succeeded. The pipeline
ran **9 blocking verification gates, preceded by the blocking `validate-variables` precondition guard**,
all green, and **five** justified `allow_failure` (non-gating) jobs:

| Blocking gate (all green on pipeline 30730) | Verifies |
|---|---|
| `validate-variables` | CI variable/precondition validation |
| `linter` (flake8) | Style / lint conformance |
| `docker-linter` (hadolint) | Dockerfile lint |
| `formater` (black + isort) | Formatting / import order |
| `typing` (mypy) | Static type contracts |
| `unit-tests` (pytest `-m unit` + coverage, Cobertura) | Tier-A unit tests + coverage gate |
| `security` (bandit) | Python SAST |
| `deps-sec` (pip-audit, isolated venv) | Dependency CVE scan (accepted findings in <5.2.4>) |
| `build-package` | Wheel build |
| `sphinx-build` | Documentation build |

**Test results (authoritative; pytest-collected on `cpm_env`, `eopf 2.8.1` / Python 3.11):**

| Test set | Cases | Result |
|---|---|---|
| Unit (`tests/ut`) | **246** | **244 passed, 2 xfailed** |
| Integration (`tests/it/computing/test_full_chain.py`) | **2** | **2 passed** |
| **Total** | **248** | **246 passed, 2 xfailed** (from **238** test functions, some parametrised) |

Per-unit unit-test counts: `l0_decode` 22, `radiometric` 21, `enhancement` 35, `toa` 24,
`coregistration` 23, `georeference` 27, `atmospheric` 35, `pansharpen` 29, `common` (types + metrics)
15, `sensors` (profile) 7. The **2 xfailed** cases are in `tests/ut/computing/test_georeference_core.py`
and intentionally verify the `orthorectify` `[impl]` fail-stop (<5.2.1>). The **2 integration** cases
(full `L0c`→`L2A` chain and chain-with-pansharpen) wire all 8 units on one synthetic feature-rich
scene; they surfaced and fixed a real defect (the `AtmosphericUnit` was dropping the L1C geolocation
grid from `L2A`; fixed by conditions passthrough — see <5.1>).

The full V&V results record is the **SVR (RD-12)**; this SRN reports status only. The Tier-C numeric
performance-budget closure is **withheld at QR** and is a documented open item carried to AR
(<5.2.2>).

---

## <5> Status of the software

### <5.1> Evolution since previous version

This is the **first release candidate** of `msi-processor`; there is **no previous released
version**. "Evolution" is therefore the milestone changelog from project start (SRR) to this QR
baseline. All of SRR, PDR and CDR were baselined to `main`.

| Milestone | Baseline established | Summary of evolution |
|---|---|---|
| **SRR** | Requirements & system baseline | SSS (`SYS-*`, RD-2), IRD (`REQ-IF-*`, RD-3) and SRS (`REQ-*`, **100** requirements, RD-4) issued; public-code / private-data policy fixed (SRS <5.1>/<5.8>) |
| **PDR** | Preliminary design + V&V approach | Architectural SDD, ICD (RD-5), DPM (RD-6), ATBD (RD-7); V&V Plan (RD-8) with the three-tier scheme baselined before detailed design |
| **CDR** | Detailed design + test contract | Detailed SDD (**21 `C-*`** components, internal interfaces, RD-9); SUITP (Annex K, RD-18); traceability matrix/RTM (RD-11) with bidirectional closure and **no orphans**; the 6 `[impl]` bodies marked for post-CDR finalisation |
| **post-CDR (implementation)** | Code on `main` | **8/8** processing units implemented (pure core + `EOProcessingUnit` wrapper + computing-model JSON each), plus `common` (types + QA metrics), the sensor `profile`, and typed exceptions; CI gates green per merge request |
| **QR (this release)** | Qualification | Full Tier-A suite green (**246** UT: 244 passed / 2 xfail) **+ 2** integration passed = **248**; CI pipeline **30730** green on `d140599`; QR data package authored (SVR, SUITR, this SRN, SUM start, CIDL, SCF, CI evidence) |

**Notable code changes consolidated into this baseline (from the `main` history):**

- **`l0_decode` unit added** (the Level-0→L1A decode unit, `C-PU-L0`), **closing the `L0c`→`L2A`
  chain at 8/8**.
- **End-to-end integration chain** (`L0c`→`L2A`, with the pan-sharpen variant) added; it surfaced and
  fixed a real defect — the `AtmosphericUnit` was **dropping the L1C geolocation grid** from the
  `L2A` product; corrected by a conditions passthrough. This is the merge that establishes the QR
  baseline (`d140599`).

### <5.2> Known problems and limitations

This release carries the following known limitations. **None** is an unresolved operational defect on
the public processing path; each is a *scoped, recorded* limitation traced in the RTM (RD-11) and/or
documented in the V&V Plan (RD-8) and SVR (RD-12).

#### <5.2.1> Deferred algorithm bodies (`[impl]`, fail-stop)

Six algorithm bodies are deferred (their finalisation requires sensor-private models/data or is a
CDR/AR-target). **All are fail-stop** (they raise rather than emit a wrong product), **all carry
recorded waivers (SW&D) traced in the RTM at G-1/G-6**, and the **operational baseline never executes
them** — the public path uses the documented alternative in each case.

| # | Unit · body | Algorithm | Reason deferred / operational alternative |
|---|---|---|---|
| 1 | `l0_decode` · `decode_source_packets` | ALG-L0-DEC | Sensor-private on-wire source-packet decode/decompression; the public path consumes the documented open-container sample layout |
| 2 | `georeference` · `orbit_state` | ALG-GEO-ORBIT | Ephemeris/orbit propagation (CDR-target; GPL TLE path dropped) |
| 3 | `georeference` · `orthorectify` | ALG-GEO-ORTHO | Rigorous collinearity / DEM line-of-sight needs the sensor-private viewing model (CDR-target); the operational L1C path uses **GCP reference-image refinement** instead. **2 xfail tests** verify this fail-stop |
| 4 | `atmospheric` · `retrieve_atmospheric_parameters` | ALG-ATM-PAR | Image-based AOT / water-vapour retrieval |
| 5 | `atmospheric` · `resolve_rt_lut` | ALG-ATM-RT | Radiative-transfer engine LUT build |
| 6 | `atmospheric` · `classify_scene_ml` | ALG-ATM-SCM | ML scene-classifier refinement |

In addition, the **pan-sharpen component-substitution fusion methods** (`brovey`, `gs`, `ihs`,
`atrous`) are deferred; only **`simple_mean`** is operational.

#### <5.2.2> Withheld Tier-C performance-budget validation (QR open item → AR)

The **numeric** performance-budget closure for the five performance requirements **REQ-P-01..05**
(`RAD_ACC` radiometric accuracy; `GEO_CE90` + `BAND_COREG` geolocation/co-registration; `BOA_ACC`
surface reflectance; `THRU_SCENE` throughput; `MEM_BUDGET` peak memory) is **withheld at QR**. The
Tier-C numeric validation requires the **operator's private real RAW + calibration data** (data
policy SSS <5.1>), which is never present in the public CI. At QR these requirements are verified by
**analysis/design and the algorithm V&V**; the numeric budget closure is a **documented QR OPEN ITEM
carried to AR**, where it is validated on operator data at the Acceptance Review. This is the single
most important QR limitation and is stated honestly here and in the SVR (RD-12).

#### <5.2.3> Non-blocking (`allow_failure`) CI jobs

The following CI jobs are **`allow_failure` (non-gating)** on the shell-executor runner; their status
does not gate the release. The justification is the runner's lack of a container runtime, Dask
gateway and S3 (a single Studio VM, SHELL executor).

| Job | Why non-blocking |
|---|---|
| `docs-cov` (docstr-coverage) | Informational docstring-coverage metric |
| `complexity` (xenon) | Advisory cyclomatic-complexity bound |
| `sonarqube` | External service (quality-gate adjudication) |
| `integration-tests` | Now **passing**, but Dask-gateway / S3 are absent on the shell runner; **non-blocking until a Kubernetes runner** lands |
| `deliver-image` (kaniko) | kaniko needs a container runtime that the shell runner lacks |

The **integration tests pass** at the baseline (<4.6>); they are non-gating only because the runner
cannot guarantee the real-runtime services, not because of a test failure. They become blocking once
a K8s runner replaces the shell executor (tracked in the Risk Register, RD-13).

#### <5.2.4> Dependency-security accepted findings (`deps-sec` ignore-list)

The `deps-sec` (pip-audit) gate is green with a documented, justified ignore-list:
**PYSEC-2026-248 / PYSEC-2026-249** and **CVE-2026-48817 / CVE-2026-48818**. These are
**`eopf`-transitive** advisories against **starlette 1.0.1**; they are **unfixable while
`eopf == 2.8.1` is pinned** (the pin is a hard runtime constraint, REQ-R-03/REQ-M-03). They are
**revisited on the next `eopf` bump**, which re-runs the full V&V before re-baselining (REQ-M-03).

#### <5.2.5> SPR / SCR / NCR / waiver status

| Item | Status at QR |
|---|---|
| Open SPRs (unresolved problem reports) on the operational path | **None** — the one defect found by the integration tests (L2A geolocation drop) was fixed in this baseline (<5.1>) |
| Open SCRs (change requests) blocking release | None |
| Approved SW&D (waivers/deviations) | The `[impl]` fail-stop deferrals of <5.2.1> are recorded waivers traced in the RTM (RD-11) at G-1/G-6; the Tier-C budget withholding (<5.2.2>) is a recorded open item; the `deps-sec` ignores (<5.2.4>) are recorded justifications |
| NCR status | No open non-conformances against the released configuration |

SPR/NCR status is checked as part of the QR exit criteria (SReVP, RD-16); the controlled record is
the GitLab issue tracker and the SVR (RD-12).

---

## <6> Advice for use of the software configuration item

- **Run inside the EOPF SDE / `eopf == 2.8.1` environment.** The `eopf` pin is exact; do not mix with
  another `eopf` version. Use `opencv-python-headless` (display-free) and the declared `rasterio`.
- **Operational scope.** Use the documented public processing path (the open-container `L0c` sample
  layout → `L2A`). Do **not** invoke the deferred `[impl]` bodies of <5.2.1>: they are fail-stop and
  will raise. For geolocation, the operational path is **GCP reference-image refinement**, not the
  deferred rigorous orthorectification. For pan-sharpen, use **`simple_mean`** only.
- **Accuracy budgets are not numerically qualified at QR.** Treat product accuracy/throughput/memory
  figures as **provisional** until the AR Tier-C validation on operator data (<5.2.2>). Numeric
  budgets and calibration coefficients are **private** and are supplied via the sensor profile / ADFs,
  never hard-coded.
- **Data policy.** Never commit private raw `L0`, calibration coefficients or budget thresholds; the
  CI scan enforces this (REQ-S-01/05). The released code is public; the data are not.
- **Distributed / S3 execution** (Dask-gateway, object store) is exercised locally only at QR; at
  scale it is a system-level (ground-segment) concern (V&V Plan <13>).
- **This is a release candidate (`-rc1`).** It is intended for qualification assessment and AR
  validation, not yet a final operational acceptance baseline.

---

## <7> On-going changes

Planned evolution from this QR release candidate toward AR / a final release:

- **Promote the tag** `v0.1.0-rc1` on `d140599` at the release decision, and update SCF (RD-19) /
  CIDL (RD-20) to cite it (<4.1>).
- **Close the Tier-C performance budgets** (REQ-P-01..05) on operator private RAW + calibration data
  at AR; fold the numeric verdicts (pass/fail only, private numbers withheld) into the SVR (RD-12)
  (<5.2.2>).
- **Promote `integration-tests` to blocking** once an EOPF SDE **Kubernetes** runner replaces the
  shell executor (also enables `deliver-image`/kaniko, real Dask-gateway/S3 paths) (<5.2.3>;
  Risk Register RD-13).
- **Re-evaluate the `deps-sec` ignore-list** at the next `eopf` bump; an `eopf` change triggers a full
  V&V re-run before re-baseline (REQ-M-03) (<5.2.4>).
- **`[impl]` bodies** (<5.2.1>) remain deferred targets; any future activation re-opens the relevant
  ALG-* verification and the affected REQ-* in the RTM (RD-11).
- **Complete the SUM** (RD-21) from its current start state toward full operational coverage.

Planned changes are tracked as GitLab issues against the `ipf/msi-processor` project.

---

*End of Software Release Note. Authored per ECSS-E-ST-40C Rev.1 (Software Release Document / SRelD),
ECSS-M-ST-40C (configuration management) and ECSS-Q-ST-80C Rev.2 (delivery & release), tailored for
Category C, single-developer. The proposed release candidate is `v0.1.0-rc1` at QR baseline commit
`d140599` (CI pipeline 30730 green; 248 tests — 246 passed, 2 xfail). The Git tag is applied at the
release decision. The verification-results record is the SVR (RD-12); the SCI inventory is the SCF
(RD-19) and CIDL (RD-20); the maintained traceability matrix is RD-11.*
