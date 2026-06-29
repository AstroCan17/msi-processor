# Configuration Item Data List (CIDL)

| Field | Value |
|---|---|
| **Document** | CIDL — Configuration Item Data List |
| **DRD ref** | ECSS-M-ST-40C Rev.1 (configuration item data list); ECSS-E-ST-40C Rev.1 (software configuration management); ECSS-Q-ST-80C Rev.2 §6.2.7 |
| **Container** | Management File (MGT) / QR data package — `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | QR (Qualification Review) |
| **Status** | Issued at QR |

> This CIDL enumerates **every configuration item** that constitutes the Software Configuration Item
> (SCI) `msi-processor` at the **Qualification Review (QR) configuration baseline** — `main` commit
> **`d140599`** (latest `main` pipeline **30730 = success**). It is a constituent of the QR data
> package (alongside the SVR, SUITR, SRelD/SRN, SUM, SCF and the CI verification evidence) and is the
> single authoritative inventory the SRelD/SRN (RD-17) and the SCF (RD-18) defer to for *what is in
> the baseline*. Per ECSS-M-ST-40C the list gives, for each item, an **identifier**, a **type**, a
> **title/role**, and a **version reference** (the QR baseline commit, plus an embedded SemVer where a
> file carries one). The SCI is held as a **single Git repository under reviewed-merge-request
> configuration control** (RD-8 V&V Plan <6>, RD-13 SPAP §6.5), so the QR baseline commit `d140599`
> is the common revision authority for all items; per-file independent revision numbers are not
> maintained. This document does not restate design content — it points to the SDD (RD-9), DPM (RD-6),
> ATBD and the RTM (RD-11) for the engineering substance — it records the **configuration inventory**
> and the **open items / deviations** carried into AR. The footprint is tailored to a **Category C,
> single-developer** ground-segment processor whose **code is public but whose raw `L0` data and
> instrument calibration are private** (RD-4 SRS <5.1>/<5.8>).

**DRD clause coverage.** Where this CIDL satisfies each ECSS-M-ST-40C CIDL clause:

| DRD clause (CIDL) | Topic | This document |
|---|---|---|
| CIDL <1> | Introduction (purpose & objective) | <1> |
| CIDL <2> | Applicable and reference documents | <2> |
| List a.1 | Cover sheets and scope | <1>, <3> |
| List a.2 | Customer-controlled documentation (customer specifications and ICDs, support specifications) | <6> |
| List a.3 | Engineering / design documentation (verification plans, lower-level specs/ICDs, test specifications and procedures, user manual) | <6>, <8> |
| List a.4 | Applicable changes not yet incorporated, and deviations | <9> |
| List a.5 | CI number breakdown (indentured breakdown, quantity per next-higher assembly, issue status) | <3>, <4>–<8>, <10> |
| List a.6 | Each entry related to the model(s) and defined by number, title, issue and release date | <3.3>, <4>–<8> |

---

## <1> Introduction

**Purpose.** This CIDL identifies and lists, at the QR configuration baseline, all configuration
items of the `msi-processor` SCI: the **source package** (`msi_processor`), the **test suite**
(`tests/`), the **ECSS document set** (`compliance/`), the **build/CI and configuration-control
items**, and the **documentation tree** (`docs/`). It establishes the inventory against which the SCI
is placed under formal configuration control and from which the SRelD/SRN (RD-17) and SCF (RD-18) are
written.

**Objective.** Per ECSS-M-ST-40C and ECSS-Q-ST-80C Rev.2 §6.2.7, to give each configuration item a
unique identifier, a type, a title/role and a version reference; to record the **indentured
breakdown** of the SCI and the **quantity** of items at each level; to capture **changes not yet
incorporated and deviations** (clause <9>); and to fix the **issue status** of the baseline against
the recorded CI verification evidence (clause <10>). This enables the QR exit criterion that *"the SCI
is a formal version under configuration control"* (SReVP RD-12 QR exit criterion (c)).

**Scope and baseline.** The baseline is `main` commit **`d140599`** — the QR configuration baseline —
whose pipeline (**30730**) is green on the nine blocking CI gates (clause <10>). Developer-local
tooling that is **not** part of the SCI is explicitly excluded in <3.1>.

**Reason for preparation.** SRR, PDR and CDR are complete and baselined to `main`; this package is the
**QR** data package and AR is next. The CIDL is authored in this package (no prior CIDL exists) and is
the configuration spine of the QR review.

---

## <2> Applicable and reference documents

### <2.1> Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space project management — Configuration and information management (CIDL content) | ECSS-M-ST-40C Rev.1 |
| AD-2 | ECSS Space engineering — Software (software configuration management, Annex R criticality) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-3 | ECSS Space product assurance — Software (§6.2.7 configuration management; §7 product quality) | ECSS-Q-ST-80C Rev.2 |
| AD-4 | EOPF CPM — Product Structure & Format Definition / data model | EOPF CPM docs (`eopf == 2.8.1`) |

### <2.2> Reference documents (RD)

| Id | Document | Reference (path at `d140599`) |
|---|---|---|
| RD-1 | Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | Interface Control Document (ICD) | `compliance/drd/icd-interface-control.md` |
| RD-6 | Detailed Processing Model (DPM) — `DPM-M-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | V&V Plan (SVerP + SValP + SUITP strategy) | `compliance/drd/vv-plan.md` |
| RD-9 | Software Design Document (SDD) — `C-*` | `compliance/drd/sdd-software-design.md` |
| RD-10 | Software Unit & Integration Test Plan (SUITP, Annex K) | `compliance/drd/suitp-unit-integration-test-plan.md` |
| RD-11 | Requirements Traceability Matrix (RTM) | `compliance/traceability/traceability-matrix.md` |
| RD-12 | Software Review Plan (SReVP) | `compliance/drd/srevp-software-review-plan.md` |
| RD-13 | Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |
| RD-14 | Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-15 | Design Justification File (DJF) | `compliance/drd/djf-design-justification.md` |
| RD-16 | Risk Register | `compliance/drd/risk-register.md` |
| RD-17 | Software Release Note / SRelD (SRN) | `compliance/drd/srn-software-release-note.md` (online rendering: `docs/srn.md`) |
| RD-18 | Software Configuration File (SCF) | `compliance/drd/scf-software-configuration-file.md` (online rendering: `docs/scf.md`) |
| RD-19 | QR Review Report (qualification record) | `compliance/qr-qualification-review-report.md` |

---

## <3> Configuration item identification, structure and versioning

### <3.1> The Software Configuration Item (SCI) and its QR baseline

The SCI is the single Git repository `gitlab.eopf.copernicus.eu/ipf/msi-processor`. The **QR
configuration baseline** is `main` commit **`d140599`** (pipeline **30730 = success**). Every
configuration item in clauses <4>–<8> is referenced to this commit; this is the model-defining
revision of the CI in the sense of ECSS-M-ST-40C List a.6 (the SCI has a single operational model —
the `msi-processor` ground processor — so all entries relate to that one model).

**Items excluded from the SCI (developer-local tooling, not configuration-controlled deliverables).**
The following are present in the working tree but are **not** configuration items of the SCI and are
not baselined: `.claude/` (local Claude Code settings), `.remember/` (local hook logs). They carry no
ECSS role and are recorded here only to make the exclusion explicit.

### <3.2> CI numbering scheme and indentured breakdown (top level)

Configuration-item identifiers use a category prefix. The top-level indentured breakdown of the SCI
(List a.5a) and the quantity of items per category (List a.5b) are:

| CI category | ID prefix | Clause | Path root | Quantity (files) |
|---|---|---|---|---|
| Source code (package + units) | `CI-SW-*`, `CI-PU-*` | <4> | `msi_processor/` | 42 (34 `.py` + 8 model `.json`) |
| Test suite | `CI-TS-*` | <5> | `tests/` | 27 `.py` (+ 1 exploratory `.ipynb`) |
| ECSS document set | `CI-DC-*` | <6> | `compliance/` | 22 `.md` |
| Build / CI / config-control | `CI-CF-*` | <7> | repo root, `.gitlab/` | 17 |
| Documentation tree | `CI-UD-*` | <8> | `docs/` | 47 |

### <3.3> Versioning and issue-status convention

- **Revision authority.** Git is the revision authority. The version reference for every item is the
  QR baseline commit `d140599`; the SCI is changed only through reviewed merge requests under
  ECSS-M-ST-40C / ECSS-E-ST-40C configuration control (RD-8 <6>, RD-13 §6.5). Per-file independent
  issue numbers are not maintained — the file's *issue* is the baseline commit and its `main`
  pipeline status.
- **Distribution version.** The Python distribution version is **dynamic** (flit backend +
  `git describe`); **no Git tag exists yet**. The proposed QR release candidate is **`v0.1.0-rc1`**,
  referenced to commit `d140599`. Tag creation is the release action taken at the AR / release
  decision; the SRelD/SRN (RD-17) states the RC and the baseline commit. This CIDL does **not** assume
  a tag is created.
- **Embedded SemVer.** The eight computing-model JSON files carry an embedded schema SemVer (`1.0.0`)
  in their filename; that SemVer is listed alongside the baseline commit in clause <4.2>.
- **Release date.** The QR baseline commit date is **2026-06-29** (List a.6 "release date").

---

## <4> Source-code configuration items (`msi_processor`)

All items below are **source code**, version reference **`d140599`** (proposed distribution
`v0.1.0-rc1`). The package implements the design components `C-*` (RD-9), processing modules
`DPM-M-*` (RD-6) and algorithms `ALG-*` (RD-7), all traced in the RTM (RD-11). The architecture is
the **pure framework-independent core + thin `EOProcessingUnit` wrapper + computing-model JSON**
pattern (RD-9, RD-4 REQ-D-03).

### <4.1> Package, common, exceptions and sensors

| CI ID | Path | Type | Role |
|---|---|---|---|
| CI-SW-01 | `msi_processor/__init__.py` | Source (package root) | Package init; flit dynamic version + description anchor |
| CI-SW-02 | `msi_processor/common/__init__.py` | Source | `common` subpackage init |
| CI-SW-03 | `msi_processor/common/types.py` | Source | Shared data types / type contracts (mypy-checked) |
| CI-SW-04 | `msi_processor/common/metrics.py` | Source | QA-metrics module (SNR/RMSE/PSNR/MSE/variance; ex-`metrics_ips`, RD-14) — REQ-F-QA-01 |
| CI-SW-05 | `msi_processor/exceptions/__init__.py` | Source | `exceptions` subpackage init |
| CI-SW-06 | `msi_processor/exceptions/errors.py` | Source | Fail-stop error hierarchy (REQ-F-DEP-01) |
| CI-SW-07 | `msi_processor/exceptions/warnings.py` | Source | QA / non-fatal warning hierarchy |
| CI-SW-08 | `msi_processor/sensors/__init__.py` | Source | `sensors` subpackage init |
| CI-SW-09 | `msi_processor/sensors/profile.py` | Source | Sensor-profile model (sensor-agnostic externalisation; REQ-D-07, REQ-AD-01) |
| CI-SW-10 | `msi_processor/computing/__init__.py` | Source | `computing` subpackage init |

### <4.2> Computing units (8 processing units)

Each computing unit is an indentured assembly of **four** files (List a.5b, quantity = 4 per unit):
`__init__.py`, `core.py` (pure core), `unit.py` (`EOProcessingUnit` wrapper), and one
`models/<name>.json` (CPM computing-model). All at `d140599`; each model JSON carries embedded schema
SemVer **`1.0.0`**.

| CI ID | Unit (package) | Output level | Files (`__init__.py`, `core.py`, `unit.py`) | Computing-model JSON (SemVer) |
|---|---|---|---|---|
| CI-PU-L0 | `computing/l0_decode` | L1A | `l0_decode/{__init__,core,unit}.py` | `models/msi_l0_decode_1.0.0.json` (1.0.0) |
| CI-PU-RAD | `computing/radiometric` | L1A | `radiometric/{__init__,core,unit}.py` | `models/msi_radiometric_1.0.0.json` (1.0.0) |
| CI-PU-ENH | `computing/enhancement` | L1B (MTF-compensation mandatory) | `enhancement/{__init__,core,unit}.py` | `models/msi_enhancement_1.0.0.json` (1.0.0) |
| CI-PU-TOA | `computing/toa` | L1B | `toa/{__init__,core,unit}.py` | `models/msi_toa_1.0.0.json` (1.0.0) |
| CI-PU-COR | `computing/coregistration` | L1B→L1C | `coregistration/{__init__,core,unit}.py` | `models/msi_coregistration_1.0.0.json` (1.0.0) |
| CI-PU-GEO | `computing/georeference` | L1C | `georeference/{__init__,core,unit}.py` | `models/msi_georeference_1.0.0.json` (1.0.0) |
| CI-PU-ATM | `computing/atmospheric` | L2A (new design) | `atmospheric/{__init__,core,unit}.py` | `models/msi_atmospheric_1.0.0.json` (1.0.0) |
| CI-PU-PAN | `computing/pansharpen` | optional post-L2A derivative | `pansharpen/{__init__,core,unit}.py` | `models/msi_pansharpen_1.0.0.json` (1.0.0) |

**Quantity check.** 10 items in <4.1> + 8 units × 4 files in <4.2> = **42** source files (34 `.py`
+ 8 `.json`). All 8 units are implemented and CI-green on `main`. Fail-stop deferrals within the
cores are recorded in clause <9.2>.

---

## <5> Test-suite configuration items (`tests/`)

Type **test source**, version reference **`d140599`**. The suite holds **246 unit** test cases (244
passed, 2 xfailed) + **2 integration** test cases (2 passed) = **248** total, collected from 238 test
functions on `cpm_env` (eopf 2.8.1 / Python 3.11). Per-unit counts below are the unit's total across
its `*_core.py` and `*_unit.py` modules.

### <5.1> Package markers

| CI ID | Path | Type | Role |
|---|---|---|---|
| CI-TS-00 | `tests/__init__.py`, `tests/ut/__init__.py`, `tests/ut/common/__init__.py`, `tests/ut/computing/__init__.py`, `tests/ut/sensors/__init__.py`, `tests/it/__init__.py`, `tests/it/computing/__init__.py` | Test source | 7 package-marker files |

### <5.2> Unit tests (`tests/ut`, `pytest -m unit`)

| CI ID | Path | Unit under test | Test cases |
|---|---|---|---|
| CI-TS-01 | `tests/ut/common/test_types.py` + `tests/ut/common/test_metrics.py` | `common` (types + metrics) | 15 |
| CI-TS-02 | `tests/ut/sensors/test_profile.py` | `sensors.profile` | 7 |
| CI-TS-03 | `tests/ut/computing/test_l0_decode_core.py` + `test_l0_decode_unit.py` | `l0_decode` | 22 |
| CI-TS-04 | `tests/ut/computing/test_radiometric_core.py` + `test_radiometric_unit.py` | `radiometric` | 21 |
| CI-TS-05 | `tests/ut/computing/test_enhancement_core.py` + `test_enhancement_unit.py` | `enhancement` | 35 |
| CI-TS-06 | `tests/ut/computing/test_toa_core.py` + `test_toa_unit.py` | `toa` | 24 |
| CI-TS-07 | `tests/ut/computing/test_coregistration_core.py` + `test_coregistration_unit.py` | `coregistration` | 23 |
| CI-TS-08 | `tests/ut/computing/test_georeference_core.py` + `test_georeference_unit.py` | `georeference` (2 xfail verify `orthorectify` fail-stop) | 27 |
| CI-TS-09 | `tests/ut/computing/test_atmospheric_core.py` + `test_atmospheric_unit.py` | `atmospheric` | 35 |
| CI-TS-10 | `tests/ut/computing/test_pansharpen_core.py` + `test_pansharpen_unit.py` | `pansharpen` | 29 |

### <5.3> Integration tests (`tests/it`, `pytest -m integration`) and exploratory notebook

| CI ID | Path | Type | Role / cases |
|---|---|---|---|
| CI-TS-11 | `tests/it/computing/test_full_chain.py` | Integration test | Wires all 8 units on one synthetic feature-rich scene: full L0c→L2A chain + chain-with-pansharpen = **2** cases (2 passed) |
| CI-TS-12 | `tests/dask-test.ipynb` | Exploratory notebook (non-CI) | Local Dask exploration; not pytest-collected, not gating |

**Quantity check.** 7 markers + 18 test modules (16 computing + 2 common + 1 sensors → counted as
listed) = **27** test `.py` files, plus 1 exploratory `.ipynb`. The integration suite surfaced and
fixed a real defect (AtmosphericUnit dropping the L1C geolocation grid from L2A; fixed via conditions
passthrough) — recorded in RD-8 / RD-11.

---

## <6> ECSS document-set configuration items (`compliance/`)

Type **ECSS document** (Markdown, no Apache header per house style), version reference **`d140599`**,
all baselined as indicated. These satisfy CIDL List a.2 (customer-controlled specifications and ICDs:
SSS, IRD, ICD — the Requirements Baseline) and List a.3 (engineering/design documentation: verification
plans, lower-level specs, test specifications and procedures). The QR-package documents (CIDL, SCF,
SRN, QR Review Report — CI-DC-17..20) are working-tree additions authored **at QR** against baseline
`d140599`, consistent with the CIDL self-reference convention of <3.1>.

| CI ID | Path | Document | Baselined at |
|---|---|---|---|
| CI-DC-01 | `compliance/software-development-plan.md` | SDP (RD-1) | SRR |
| CI-DC-02 | `compliance/drd/sss-software-system-specification.md` | SSS (RD-2) — customer-controlled spec | SRR/PDR |
| CI-DC-03 | `compliance/drd/ird-interface-requirements.md` | IRD (RD-3) — customer-controlled spec | SRR/PDR |
| CI-DC-04 | `compliance/drd/srs-software-requirements.md` | SRS (RD-4) | PDR |
| CI-DC-05 | `compliance/drd/icd-interface-control.md` | ICD (RD-5) — customer-controlled ICD | PDR/CDR |
| CI-DC-06 | `compliance/drd/dpm-data-processing-model.md` | DPM (RD-6) — `DPM-M-*` (11 modules) | CDR |
| CI-DC-07 | `compliance/drd/atbd-algorithm-theoretical-basis.md` | ATBD (RD-7) — `ALG-*` (33 algorithms) | CDR |
| CI-DC-08 | `compliance/drd/vv-plan.md` | V&V Plan (RD-8) | PDR |
| CI-DC-09 | `compliance/drd/sdd-software-design.md` | SDD (RD-9) — `C-*` (21 components) | CDR |
| CI-DC-10 | `compliance/drd/suitp-unit-integration-test-plan.md` | SUITP (RD-10) — test specs & procedures | CDR |
| CI-DC-11 | `compliance/traceability/traceability-matrix.md` | RTM (RD-11) — bidirectional, no orphans | CDR |
| CI-DC-12 | `compliance/drd/srevp-software-review-plan.md` | SReVP (RD-12) | SRR/PDR |
| CI-DC-13 | `compliance/drd/spa-plan.md` | SPAP (RD-13) | SRR/PDR |
| CI-DC-14 | `compliance/drd/srf-software-reuse-file.md` | SRF (RD-14) | CDR |
| CI-DC-15 | `compliance/drd/djf-design-justification.md` | DJF (RD-15) | CDR |
| CI-DC-16 | `compliance/drd/risk-register.md` | Risk Register (RD-16) | SRR (living) |
| CI-DC-17 | `compliance/drd/cidl-configuration-item-data-list.md` | CIDL (this document) | QR |
| CI-DC-18 | `compliance/drd/scf-software-configuration-file.md` | SCF (RD-18) — authoritative ECSS document | QR |
| CI-DC-19 | `compliance/drd/srn-software-release-note.md` | SRN/SRelD (RD-17) — authoritative ECSS document | QR |
| CI-DC-20 | `compliance/qr-qualification-review-report.md` | QR Review Report (RD-19) — qualification record | QR |
| CI-DC-21 | `compliance/drd/vv-report.md` | SVR — Software Verification Report (V&V results record) — QR deliverable | QR |
| CI-DC-22 | `compliance/drd/suitr-unit-integration-test-report.md` | SUITR — Software Unit & Integration Test Report — QR deliverable | QR |

**Quantity check.** 19 files under `compliance/drd/` (incl. CIDL, SCF, SRN, SVR, SUITR) + 1 QR Review
Report and 1 SDP at `compliance/` root + 1 RTM under `compliance/traceability/` = **22** documents. The SCF/SRN
also have online renderings under `docs/` (CI-UD-05/06), and the CIDL under `docs/cidl.md` (CI-UD-04).

---

## <7> Build, CI and configuration-control items

Type **build/CI/config**, version reference **`d140599`**.

| CI ID | Path | Type | Role |
|---|---|---|---|
| CI-CF-01 | `pyproject.toml` | Build config | flit build backend; deps (`eopf == 2.8.1`, `opencv-python-headless >= 4.8`, `rasterio >= 1.3`); pytest/black/isort config; **dynamic version → `v0.1.0-rc1`** |
| CI-CF-02 | `.gitlab-ci.yml` | CI pipeline | 9 blocking + 5 allow_failure jobs (clause <10>) |
| CI-CF-03 | `.flake8` | Lint config | flake8 rules (REQ-D-02) |
| CI-CF-04 | `.mypy.ini` | Typing config | mypy contract (ignores for `rasterio`/`affine` stubs) |
| CI-CF-05 | `bandit.yml` | SAST config | bandit security scan config |
| CI-CF-06 | `.coveragerc` | Coverage config | coverage (Cobertura) settings, gate |
| CI-CF-07 | `.pre-commit-config.yaml` | Local hooks | shift-left format/lint hooks |
| CI-CF-08 | `.hadolint.yml` | Dockerfile-lint config | hadolint rules |
| CI-CF-09 | `Dockerfile` | Container build | image recipe (kaniko `deliver-image`, non-gating on shell runner) |
| CI-CF-10 | `.gitignore` | Repo config | ignore rules |
| CI-CF-11 | `LICENSE` | Licence | Apache-2.0 |
| CI-CF-12 | `README.md` | Project readme | top-level overview |
| CI-CF-13 | `.gitlab/issue_templates/Action.md`, `Bug.md`, `Documentation.md`, `Risk.md` | Process templates | 4 GitLab issue templates |
| CI-CF-14 | `.gitlab/merge_request_templates/default.md` | Process template | default MR template |

**Quantity check.** 12 root/CI files + 4 issue templates + 1 MR template = **17** items.

---

## <8> Documentation configuration items (`docs/`)

Type **documentation** (Sphinx site, version reference **`d140599`**). Includes the QR-package
**online** documents (SCF, SRN, SUM start) authored in this tree, plus the published DPM/SDD/SUM
renderings and Sphinx assets. CIDL List a.3(i) "user manual" = the SUM tree (`docs/sum/`).

### <8.1> Sphinx root and top-level pages

| CI ID | Path | Type | Role |
|---|---|---|---|
| CI-UD-01 | `docs/conf.py` | Sphinx config | autodoc wiring; build config |
| CI-UD-02 | `docs/index.rst` | Doc root | site table of contents |
| CI-UD-03 | `docs/contributing.md`, `docs/license.md` | Doc pages | contributing + licence pages |

### <8.2> QR-package online documents

| CI ID | Path | Type | Role |
|---|---|---|---|
| CI-UD-04 | `docs/cidl.md` | Online doc | CIDL online rendering (mirrors CI-DC-17) |
| CI-UD-05 | `docs/scf.md` | Online doc | SCF (RD-18) — Software Configuration File |
| CI-UD-06 | `docs/srn.md` | Online doc | SRN/SRelD (RD-17) — Software Release Note |
| CI-UD-07 | `docs/sim.md` | Online doc | SIM — Software Installation Manual |
| CI-UD-08 | `docs/srf.md` | Online doc | SRF online rendering |
| CI-UD-09 | `docs/icd.md` | Online doc | ICD online rendering |
| CI-UD-10 | `docs/suitr.rst` | Online doc | SUITR — Software Unit & Integration Test Report (QR) |

### <8.3> DPM, SDD and SUM rendered trees

| CI ID | Path root | Type | Files |
|---|---|---|---|
| CI-UD-11 | `docs/dpm/` | DPM rendering | `breakpoints.md`, `context.md`, `conventions.md`, `index.rst`, `introduction.md`, `module-a.md`, `module-b.md`, `parameters-data-list.md` (8) |
| CI-UD-12 | `docs/sdd/` | SDD rendering | `design.md`, `djf.md`, `index.rst`, `introduction.md`, `overview.md`, `traceability.md` (6) |
| CI-UD-13 | `docs/sum/` | SUM (user manual, start) | `analytical-index.md`, `conventions.md`, `external-view.md`, `index.rst`, `introduction.md`, `operations-basics.md`, `operations-environment.md`, `operations-manual.md`, `purpose.md`, `reference-manual.md`, `tutorials.md`, `notebooks/index.rst`, `notebooks/my_processor_notebook.ipynb` (13) |

### <8.4> Sphinx static assets and templates

| CI ID | Path root | Type | Files |
|---|---|---|---|
| CI-UD-14 | `docs/_static/` | Static assets | `copernicus-logo2.png`, `esa-102x64.jpg`, `esa.jpg`, `logo_cs_group_bleu_petit-86x42.png`, `mermaid-9.4.3.min.js` (5) |
| CI-UD-15 | `docs/_templates/` | HTML templates | `help-feedback.html`, `navbar-footer.html`, `navbar-logo.html`, `test_report_template.txt` (4) |

**Quantity check.** 4 (root/pages) + 7 (online docs) + 8 (dpm) + 6 (sdd) + 13 (sum) + 5 (static)
+ 4 (templates) = **47** documentation items.

---

## <9> Changes not yet incorporated and deviations (List a.4)

This clause records, against the QR baseline `d140599`, the applicable changes not yet incorporated
into the baseline and the deviations carried into AR. All items are traced in the RTM (RD-11) and
detailed in the V&V Plan (RD-8) / SVR.

### <9.1> QR open items (changes not yet incorporated)

| Open item | Description | Disposition |
|---|---|---|
| OI-1 | **Numeric performance-budget validation withheld at QR** — the Tier-C numeric closure of REQ-P-01..05 (`RAD_ACC`, `GEO_CE90` + `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`, `MEM_BUDGET`) requires the operator's **private real RAW + calibration data** (data policy SSS <5.1>), never present in public CI. Verified by analysis/design + algorithm V&V at QR. | Carried to **AR** (validated on operator data at acceptance). The single most important QR limitation. |
| OI-2 | **No Git tag yet** — distribution version is dynamic (flit + git tag); the proposed RC is **`v0.1.0-rc1`** at `d140599`. | Tag creation is the release action at AR/release decision; SRN (RD-17) states the RC + baseline commit. |
| OI-3 | **V&V / qualification results** are consolidated at QR in the **QR Review Report** (CI-DC-20, RD-19), together with the SCF (CI-DC-18) and SRN (CI-DC-19); authored in this QR package. | Issued with the QR data package. |

### <9.2> Implementation deferral register (recorded waivers — all fail-stop)

All six `[impl]` deferrals are fail-stop, with recorded waivers traced **RTM G-1 / G-6** (RD-11); the
operational baseline never executes them.

| # | Unit | Deferred function (algorithm) | Operational substitute |
|---|---|---|---|
| 1 | `l0_decode` | `decode_source_packets` (ALG-L0-DEC) — sensor-private on-wire source-packet decode/decompression | Public path consumes the documented open-container sample layout |
| 2 | `georeference` | `orbit_state` (ALG-GEO-ORBIT) — ephemeris/orbit propagation (CDR-target; GPL TLE path dropped) | — |
| 3 | `georeference` | `orthorectify` (ALG-GEO-ORTHO) — rigorous collinearity / DEM line-of-sight (needs sensor-private viewing model; CDR-target) | Operational L1C uses GCP reference-image refinement; 2 xfail tests verify the fail-stop (CI-TS-08) |
| 4 | `atmospheric` | `retrieve_atmospheric_parameters` (ALG-ATM-PAR) — image-based AOT/water-vapour retrieval | — |
| 5 | `atmospheric` | `resolve_rt_lut` (ALG-ATM-RT) — radiative-transfer engine LUT build | — |
| 6 | `atmospheric` | `classify_scene_ml` (ALG-ATM-SCM) — ML scene-classifier refinement | — |

Additionally, `pansharpen` component-substitution fusion methods (`brovey`/`gs`/`ihs`/`atrous`) are
deferred; only `simple_mean` is operational.

### <9.3> Documented deviations (CI gating and dependency security)

| Deviation | Description | Justification |
|---|---|---|
| DEV-1 | **5 allow_failure CI jobs** (non-gating): `docs-cov` (informational), `complexity` (xenon advisory), `sonarqube` (external service), `integration-tests` (now passing; Dask-gateway/S3 absent on shell runner), `deliver-image` (kaniko has no container runtime on shell runner). | Single Studio VM, **SHELL** executor (`image:` ignored); promote to blocking on a K8s runner. |
| DEV-2 | **`deps-sec` documented ignore-list**: PYSEC-2026-248 / PYSEC-2026-249, CVE-2026-48817 / CVE-2026-48818 (eopf-transitive `starlette 1.0.1`). | Unfixable while `eopf == 2.8.1` is pinned; revisit on eopf bump (REQ-M-03). |

---

## <10> CI verification evidence and issue status (List a.5 / a.6)

The **issue status** of the QR baseline `d140599` is set by `main` pipeline **30730 = success**. The
nine **blocking** CI gates are all green (`.gitlab-ci.yml`, CI-CF-02):

| Gate | Tool | Verifies |
|---|---|---|
| `validate-variables` | CI | pipeline variable preconditions |
| `linter` | flake8 | style/lint (REQ-D-02) |
| `docker-linter` | hadolint | Dockerfile lint |
| `formater` | black + isort | format conformance |
| `typing` | mypy | type contracts |
| `unit-tests` | pytest `-m unit` + coverage | 246 unit cases (244 passed, 2 xfailed); Cobertura coverage gate |
| `security` | bandit | SAST |
| `deps-sec` | pip-audit (isolated venv) | dependency CVEs (with DEV-2 ignore-list) |
| `build-package` | flit | wheel build |
| `sphinx-build` | Sphinx | docs build |

**Test-result evidence (authoritative).** 246 unit + 2 integration = **248** test cases from 238 test
functions on `cpm_env` (eopf 2.8.1 / Python 3.11); 244 unit passed, 2 unit xfailed (verify the
`orthorectify` fail-stop, CI-TS-08), 2 integration passed (CI-TS-11). Non-gating jobs are recorded in
DEV-1.

**Baseline confirmation.** The SCI at `d140599` is a formal version under configuration control (Git +
this CIDL + the SCF RD-18 + the SRelD/SRN RD-17), satisfying SReVP (RD-12) QR exit criterion (c). The
numeric performance-budget closure (OI-1) is the documented open item carried to AR.

---

*End of CIDL. Authored per ECSS-M-ST-40C Rev.1 (configuration item data list) and ECSS-E-ST-40C Rev.1
software configuration management, tailored for Category C, single-developer. QR configuration
baseline = `main` commit `d140599` (pipeline 30730 = success); proposed release candidate
`v0.1.0-rc1`. The maintained traceability artefact is the RTM (RD-11); the release record is the
SRelD/SRN (RD-17) and the SCF (RD-18).*
