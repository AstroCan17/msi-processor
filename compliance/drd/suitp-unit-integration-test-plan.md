# Software Unit & Integration Test Plan (SUITP)

| Field | Value |
|---|---|
| **Document** | SUITP — Software [Unit / Integration] Test Plan |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex K; ECSS-Q-ST-80C Rev.2 §6.2.8.2/§6.2.8.7, §6.3.5.22–25 |
| **Container** | Design Justification File (DJF) — `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | CDR (Critical Design Review) |
| **Status** | Draft for CDR |

> This SUITP is the **CDR extension** of the V&V Plan (RD-8): the V&V Plan (PDR issue) defined the V&V
> strategy and the three-tier scheme and recorded that the **detailed unit/integration test
> specifications and procedures** are produced at CDR as its *Part K* (RD-8 §1, RD-8 RD-9 placeholder).
> This document is that Part K, authored as a standalone Annex K deliverable. It refines the three-tier
> scheme into concrete **test designs**, **test cases** and **test procedures**, maps each to the SRS
> requirements (`REQ-*`, RD-4) and the SDD components (`C-*`, `IF-*`, RD-9), and fixes the test
> environment, entry/exit criteria and coverage targets. It does **not** restate the V&V strategy,
> validation campaigns or the numerical-budget (Tier C) validation — those remain in the V&V Plan
> (RD-8) and are reported in the SVR (RD-12). Per the SDP (RD-1) §5.1, **implementation starts only
> after CDR**; this plan is the contract that the Tier A/B test suite is built against, stage by stage.
> The footprint is tailored to **Category C, single-developer**, with the DRD `<8>`/`<9>`/`<10>` detail
> simplified per Annex K `<8.1>`b NOTE (unit test plan may be simplified) while remaining traceable.

**DRD clause coverage (Annex K, Table K-1).** Where this SUITP satisfies each Annex K clause:

| DRD clause | Topic | This document |
|---|---|---|
| K `<1>`/`<2>`/`<3>` | Intro / AD-RD / terms | `<1>`, `<2>`, `<3>` |
| K `<4>` | Software overview (software under test) | `<4>` |
| K `<5.1>`..`<5.7>` | Organisation, schedule, resources, responsibilities, tools, personnel, risks | `<5.1>`..`<5.7>` |
| K `<6>` | Control procedures (problem reporting / waivers / config control) | `<6>` |
| K `<7.1>`..`<7.6>` | Strategy, tasks/items, features, features-not-tested, pass/fail, manual/auto code | `<7.1>`..`<7.6>` |
| K `<8.1>`/`<8.2>` | Test design — general + per-design organisation | `<8.1>`, `<8.2>` |
| K `<9.1>`/`<9.2>` | Test case specification — general + per-case organisation | `<9.1>`, `<9.2>` |
| K `<10.1>`/`<10.2>` | Test procedures — general + per-procedure organisation | `<10.1>`, `<10.2>` |
| K `<11>` | Additional information (TP↔TC matrices, scripts, detailed procedures) | `<11>` |

---

## <1> Introduction

**Purpose.** This SUITP describes the **unit test plan** and the **software integration test plan** for
`msi-processor` (Annex K K.1.2): how each design component is verified in isolation (unit testing of the
pure algorithmic Cores and the `common` services) and how the components are verified together as the
`L0c`→`L2A` processing chain (integration testing of the PU pipeline through the EOPF CPM runtime). It is
a constituent of the Design Justification File.

**Objective.** To define, at the granularity required to author the test suite after CDR: the test
**designs** (`<8>`), the test **cases** with inputs/expected-outputs/pass-fail criteria (`<9>`), the test
**procedures** (`<10>`), and the supporting organisation, schedule, resources, tools, control procedures
and entry/exit criteria. Every test design and case traces upward to one or more SRS requirements
(`REQ-*`, RD-4) and to the SDD component(s) it exercises (`C-*` / `IF-*`, RD-9), and downward to the
pytest module that will implement it.

**Content.** Clause `<2>` lists applicable/reference documents; `<3>` adds test-specific terms; `<4>`
summarises the software under test. Clause `<5>` gives the test organisation, schedule, resources,
responsibilities, tools, personnel and risks; `<6>` the control procedures; `<7>` the testing strategy,
items, features, pass/fail and entry/exit criteria, and the manual/auto-code statement. Clause `<8>`
specifies the **test designs**, `<9>` the **test cases**, `<10>` the **test procedures**, and `<11>` the
traceability matrices and the location of scripts and detailed procedures.

**Reason for preparation.** `msi-processor` is an **integration and ECSS-productisation** effort: the
algorithms exist as prior work (RD-14) and are productised on the EOPF CPM (`eopf == 2.8.1`). The design
deliberately splits each stage into a **pure, CPM-free Core** and a **thin `EOProcessingUnit` Wrapper**
(SDD `<5.4.1>`, REQ-D-03), which is precisely what makes deterministic, off-platform **unit** testing of
the numerics possible on a public CI shell runner that has no container runtime, Dask gateway or S3
(RD-1 §4.3). This SUITP turns that design property into a concrete, gated test plan, and reconciles it
with the **private-data policy** (public code, private raw `L0` + calibration; SRS <5.1>/<5.8>) via the
three-tier scheme inherited from the V&V Plan (RD-8 §4).

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software (Annex K SUITP; Annex I/J V&V; Annex M SVR) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software (§6.2.8.2/§6.2.8.7 unit testing; §6.3.5.22–25 test specs) | ECSS-Q-ST-80C Rev.2 |
| AD-3 | EOPF CPM — Product Structure & Format Definition (PSFD) / data model | EOPF CPM docs (`eopf == 2.8.1`) |

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
| RD-8 | `msi-processor` V&V Plan (SVerP/SValP merged; this SUITP is its Part K) | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Software Design Document (SDD, detailed/CDR) — `C-*`, `IF-*` | `compliance/drd/sdd-software-design.md` |
| RD-10 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-11 | `msi-processor` Traceability matrix (REQ↔design↔test) | `compliance/traceability/traceability-matrix.md` |
| RD-12 | `msi-processor` Software Verification Report (SVR, Annex M) — test results record | `compliance/drd/vv-report.md` (QR) |
| RD-13 | `msi-processor` Risk Register | `compliance/drd/risk-register.md` |
| RD-14 | Prior work — multispectral pushbroom preprocessing pipeline (`level_0`, `level_1`, `band_coreg`, `georeferencing_v1`, `pansharp`, `metrics_ips`) | see SRF (RD-10) |
| RD-15 | EOPF CPM API documentation (`EOProduct`, `EOProcessingUnit`, `EOZarrStore`, triggering) | EOPF CPM (`eopf == 2.8.1`) |
| RD-16 | `msi-processor` Software Review Plan (SRevP) | `compliance/drd/srevp-software-review-plan.md` |
| RD-17 | `msi-processor` Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |

---

## <3> Terms, definitions and abbreviated terms

The SDP §3, SSS `<3>`, SRS `<3>`, SDD `<3>` and V&V Plan `<3>` glossaries apply in full. Only terms
specific to this SUITP and not defined there are added (Annex K `<3>`a).

| Term / abbr. | Definition |
|---|---|
| Unit test (UT) | A test of a single design component in isolation — here a pure **Core** function (`<pkg>.<stage>.core`) or a `common` service, against synthetic fixtures (Annex K UT scope) |
| Integration test (IT) | A test of two or more components working together — here PU↔PU chaining and PU↔`common`-service interaction through the CPM runtime (Annex K IT scope) |
| Tier A / B / C | The V&V-Plan three-tier scheme (RD-8 §4): A = deterministic synthetic unit/plumbing tests in public CI (blocking); B = local real-RAW integration (non-blocking/skipped in public CI); C = reference/validation metrics (local; SVR — **out of SUITP scope**, validation) |
| Test design (TD) | An Annex K `<8>` grouping of related test cases for one component/concern; id `TD-UT-*` (unit) / `TD-IT-*` (integration) |
| Test case (TC) | An Annex K `<9>` atomic test (inputs → expected output → pass/fail); id `TC-<area>-NN` |
| Test procedure (TP) | An Annex K `<10>` executable sequence running one or more cases; id `TP-*` |
| Fixture | A synthetic, in-memory input (seeded NumPy/xarray array or minimal `EOProduct`) with a known/closed-form expected response |
| Closed-form expected output | An analytically derived expected result (e.g. `L = (DN − offset)·gain`) used as the UT oracle |
| Constructed expected output | An expected result built by forward-construction (e.g. apply a known homography, then assert it is recovered) where no closed form exists |
| Marker | A `pytest` marker selecting a tier: `@pytest.mark.unit` (Tier A core), `@pytest.mark.ci_integration` (Tier A plumbing, blocking), `@pytest.mark.integration` (Tier B real-RAW, local) |
| `MSI_PROCESSOR_DATA` | Environment variable pointing at the private data root; absence triggers `pytest.skip` of all Tier B (`integration`) cases (RD-8 §4) |
| Coverage gate | The blocking CI threshold: line coverage ≥ 70 % on new code (REQ-Q-02; SPAP RD-17 §5.5) |
| Oracle | The mechanism that decides pass/fail (closed-form value, constructed invariant, round-trip identity, exception type, or `assert_allclose` bound) |

---

## <4> Software overview (software under test)

`msi-processor` is a **batch, non-interactive, single-process (optionally Dask-distributed) Python
library + CLI** that transforms downlinked RAW `L0c` data into calibrated, orthorectified,
atmospherically corrected products up to `L2A`, built on the EOPF CPM (`EOProcessingUnit` / `EOProduct` /
`EOZarrStore`, Zarr persistence). Functionality, configuration, operational environment and external
interfaces are specified in the SRS (RD-4), SDD (RD-9) and ICD (RD-5) and are **not** re-derived here
(Annex K `<4>`a NOTE — reference to technical documentation).

**Items under test (the SDD components, RD-9 `<5.3>`).** The unit of test is the design component:

- **Pure Cores** (`msi_processor.computing.<stage>.core`) — `C-PU-L0`, `C-PU-RAD`, `C-PU-ENH`,
  `C-PU-TOA`, `C-PU-COR`, `C-PU-GEO`, `C-PU-PAN` *(opt)*, `C-PU-ATM` *(new)*, `C-PU-QA`. CPM-free; the
  primary unit-test targets (numerics).
- **PU Wrappers** (`…<stage>.unit`, the `EOProcessingUnit` subclasses) — the `run()` adapters; tested in
  integration with the `common` services.
- **`common` services** — `C-COM-PRODUCT`, `C-COM-IO`, `C-COM-ADF`, `C-COM-PROFILE`, `C-COM-PROV`,
  `C-COM-QAFLAG`, `C-COM-CHUNK`, `C-COM-CONFIG`, `C-COM-ORC`, `C-COM-CLI`, and the `errors` exception
  hierarchy (SDD `<5.4.1>`).
- **`sensors` adaptation layer** — `C-SENSORS` (profile schema + per-sensor data; data only).

**Operational environment of the test.** The operational runtime is the EOPF SDE container
(`eopf == 2.8.1`, Python 3.11); the public CI runner is a **GitLab shell executor** with no container
runtime, no Dask gateway and no S3 (RD-1 §4.3). This constraint is the reason unit and CI-integration
tests run only on the **local-FS / POSIX** path with the Dask **synchronous** scheduler, while real-RAW
and distributed tests run locally (Tier B). External interfaces (E1–E6, IRD `<4.1>`) are exercised only
through their CPM/POSIX representations available in the test environment; full-ground-segment items are
recorded for system-level validation in the V&V Plan (RD-8 `<13>`), not here.

---

## <5> Software unit testing and software integration testing

### <5.1> Organization

Unit and integration testing are organised as part of the project's **continuous, automated
verification** mechanism (V&V Plan RD-8 §5.2; SRevP RD-16 §8): the test suite is a configuration item in
the same repository as the code, and the unit + CI-integration tiers (Tier A) execute on **every merge
request** to `main` as **blocking** CI jobs; the real-RAW integration tier (Tier B) is executed locally
before milestones/releases and after any algorithm or `eopf` change. There is no separate test
organisation.

- **Roles.** A single role-holder (the project owner) acts as test designer, implementer and executor;
  **CI + SonarQube** act as the independent adjudicator (pass/fail is decided by the gate, not by
  opinion) — the independence model of SPAP RD-17 §5.1, applied unchanged (Category C, single-developer).
- **Reporting channels.** Test outcomes are reported by the CI pipeline status and its artefacts
  (`TEST-pytests.xml` JUnit, `coverage.xml` Cobertura) on each MR; failures are raised as GitLab issues
  and consolidated into the SVR (RD-12) at QR.
- **Levels of authority for resolving problems.** A failing **blocking** gate blocks merge; it is cleared
  only by a fix MR that re-passes the full gate set, or by a recorded waiver (SPAP RD-17 §6.5). A failing
  **non-blocking** (Tier B `allow_failure`) job is justified in the MR thread.
- **Relationships to other activities.** Project management, configuration management and product
  assurance relationships are as defined in the SDP (RD-1) and SPAP (RD-17); the test suite is governed
  by the same Git/MR configuration control as the code.

### <5.2> Master schedule

Per Annex K `<5.2>`a/b, the schedule references the SDP master schedule (RD-1 §4.2, §5.2.3), managed as
GitLab `ipf` milestones (calendar dates are not duplicated). Test milestones and item-delivery events:

| Milestone | Unit/integration testing activity | Period of use of test facilities |
|---|---|---|
| CDR (now) | Baseline this SUITP; no code yet (implementation starts post-CDR) | — |
| Post-CDR (implementation, SDP WP-5) | Each stage delivered **with** its Tier A unit test design + cases; CI runs the full Tier A suite per MR (continuous) | CI shell runner, continuous |
| Pre-QR | Tier B real-RAW integration designs executed locally on private data; Dask-path integration executed locally | Workstation / EOPF SDE, per run |
| QR | Full Tier A re-run; Tier B results consolidated; coverage-gate evidence captured in the SVR (RD-12) | CI + workstation |
| AR | Confirm delivered-version test evidence (acceptance integration TD-IT-INSTALL) is complete | SDE + local |

Time required per testing task is not separately budgeted at Category C; Tier A is seconds-to-minutes per
MR, Tier B is minutes-to-hours per real scene and is scheduled around data availability.

### <5.3> Resource summary

| Resource | Provision |
|---|---|
| Staff | One person (project owner) holding design/implementation/test/PA roles (RD-1 §4.7) |
| Hardware | Development workstation (x86-64 Linux, multi-core CPU, **no GPU**, REQ-R-01); EOPF SDE VM hosting the GitLab shell-executor CI runner; local POSIX storage / optional S3 endpoint for Tier B |
| Software tools | `pytest` + `pytest-cov` (+ `coverage`), `numpy`/`xarray`/`zarr`, `dask` (synchronous scheduler in tests), the EOPF CPM runtime (`eopf == 2.8.1`); static gates `mypy`/`flake8`/`black`/`isort`/`bandit`/`xenon`; SonarQube; `pre-commit` (see `<5.5>`) |
| Test data | **Synthetic fixtures** (committed, Tier A) generated by the fixture factories of `<5.5>`; **private** real `L0c` + ADFs + a real profile (local only, Tier B — never committed); a public **synthetic profile** + non-sensitive default tolerances (committed) |

### <5.4> Responsibilities

Per Annex K `<5.4>`a/b the project owner is the single group responsible for **managing, designing,
preparing and executing** the unit and integration tests, and for maintaining the fixtures, the `conftest`
infrastructure and this plan. **Designing/preparing:** author each `TD-UT-*`/`TD-IT-*` and its `TC-*`
alongside the component (test-with-code). **Executing:** Tier A is executed by CI automatically on every
MR; Tier B is executed manually/locally by the owner before milestones. **Adjudicating:** CI + SonarQube
decide pass/fail of the blocking tiers; the owner records Tier B verdicts. PA review of test results
occurs at the milestone reviews (SPAP RD-17 §6.8).

### <5.5> Tools, techniques and methods

**Hardware platform.** x86-64 multi-core Linux (workstation + SDE VM); CPU-only; POSIX FS (CI) and
POSIX/S3 (local). No special test equipment, bus analyser or HW-in-the-loop (ground software).

**Software tools.** `pytest` as the test runner with markers (`unit`, `ci_integration`, `integration`);
`pytest-cov`/`coverage` for the coverage gate (Cobertura + term); the EOPF CPM runtime for PU/`EOProduct`
execution (Tier A on POSIX, Tier B with real I/O); `dask` configured with the **synchronous**
(`scheduler="synchronous"`) scheduler inside tests so the chunked code path is exercised deterministically
without a cluster/gateway; `numpy.random.default_rng(<seed>)` for all randomised fixtures. Static-analysis
gates (`mypy`, `flake8`, `black`, `isort`, `bandit`, `xenon`) and SonarQube run alongside but are
specified in the V&V Plan (RD-8 §5.7) / SPAP (RD-17) and only referenced here.

**Techniques (Annex K `<5.5>`a NOTE).**
- **Deterministic synthetic-fixture unit testing** with seeded RNG and **closed-form** oracles where the
  algorithm is analytic (RAD/TOA/QA), **constructed** oracles otherwise (COR/GEO/PAN: apply a known
  transform, assert recovery; L0: inject known loss, assert truncation+flag).
- **Property / round-trip testing** — Zarr write→read identity (`C-COM-PRODUCT`); QA-flag OR-monotonicity
  (`C-COM-QAFLAG`); determinism re-run (REQ-F-DEP-02).
- **Failure-path / exception testing** — force each typed `MsiProcessorError` subclass (SDD `<5.4.1>`) and
  assert it is raised and converted to fail-stop (REQ-F-DEP-01) with no product published.
- **Boundary/robustness testing** — saturation/no-data/fill, empty/degenerate bands, insufficient
  keypoints, missing-ADF, invalid-profile.
- **Parametrised testing** across the synthetic profile (and a second synthetic profile) for sensor-
  agnosticism (REQ-D-07).
- **Chunked-equivalence testing** — assert `map_over_blocks` (with halo) equals the whole-array result
  (`C-COM-CHUNK`), proving the tiling does not change numerics (Tier A, synchronous Dask).

**Shared fixture factories** (`tests/conftest.py` and `tests/factories/`):
`make_bandstack(...)`, `make_l0c_synthetic(...)`, `make_eoproduct(level, ...)`, `make_synthetic_profile()`,
`make_synthetic_adf(kind)`, `inject_line_loss(...)`, `inject_bad_pixels(...)`, `shift_band(homography)`.
These are the "simulator" role of the test environment (no real-time/HW to simulate).

### <5.6> Personnel and personnel training requirements

One person (project owner), competent in Python, `pytest`, EOPF CPM, NumPy/xarray/Zarr/Dask and
remote-sensing data processing (RD-1 §4.7; SPAP RD-17 §5.3). **No additional test personnel and no
specific training need** is levied (Category C, single-developer tailoring).

### <5.7> Risks and contingencies

Risks to the unit/integration test campaign are held in the Risk Register (RD-13); the dominant ones
(Annex K `<5.7>`a/b):

| Risk | Effect | Contingency plan |
|---|---|---|
| Private real `L0c`/ADF data unavailable | Tier B (TD-IT-RAW-CHAIN, -DASK, -ADAPT-real, -INSTALL real run) cannot execute | Tier A fully covers functional Cores + the chain on **synthetic** data; Tier B cases `pytest.skip` when `MSI_PROCESSOR_DATA` absent; integration evidence on real data deferred to the SVR (RD-12) and recorded as an open item |
| Shell-runner limits (no container/Dask cluster/S3) | True distributed + S3 integration not runnable in public CI | Exercise the chunked path with the **synchronous** Dask scheduler in CI (proves correctness of the tiling); run multi-worker + S3 locally (Tier B, `allow_failure`); promote to blocking when a K8s runner replaces the shell executor |
| Non-determinism in a stochastic kernel (SIFT/RANSAC) | Flaky unit tests (COR/GEO/PAN) | Pin `seed` in `CoregParams`; assert within a **documented synthetic tolerance** (not bit-identity) for stochastic kernels (REQ-F-DEP-02); fixed synthetic imagery |
| `eopf == 2.8.1` API drift on bump | CPM-facing integration (Wrappers, `C-COM-*`) breaks | Pin enforced; the documented eopf-bump procedure (REQ-M-03) re-runs the full Tier A+B suite before re-baseline |
| `[impl]` bodies (L0 codec, collinearity geoloc, RT engine, classifier) finalised post-CDR | Their detailed cases cannot be fully specified at CDR | Specify these cases at **interface + algorithm level** now (synthetic-fixture contract + exception behaviour); complete the body-level cases during WP-5 against the fixed interface |

---

## <6> Control procedures for software unit testing / integration testing

Per Annex K `<6>`a, the applicable management procedures (referenced from SRevP RD-16 / SPAP RD-17, not
redefined):

- **Problem reporting and resolution.** A failing test or gate is evidenced by a red CI pipeline and
  raised as a **GitLab issue** (`Bug`/`Action` template), classified by severity (SPAP RD-17 §6.5), fixed
  via a linked MR that must re-pass the **full** Tier A suite + gates, and closed with the merge
  reference — end-to-end traceability from failure to verified fix.
- **Deviation and waiver policy.** A blocking gate (including a failed Tier A test or the coverage gate)
  may be bypassed only by a waiver recorded on the issue with rationale and expiry/closure condition
  (SPAP RD-17 §6.5). A Tier B (`allow_failure`) failure is justified in the MR.
- **Control procedures.** The test suite, fixtures, `conftest`, CI configuration and this plan are
  configuration items under Git, changed only through reviewed MRs (ECSS-M-ST-40C; SPAP RD-17 §6.5). Test
  results are forwarded to the PA function via the milestone review record and the SVR (RD-12).

---

## <7> Software unit testing and integration testing approach

### <7.1> Unit/integration testing strategy

The integration strategy is **incremental, bottom-up, design-driven** and tied to the pure-core/thin-
wrapper architecture (SDD `<5.4.1>`, REQ-D-03):

1. **Unit level (Tier A, `@pytest.mark.unit`, CI-blocking).** Each pure **Core** is tested in isolation
   against synthetic fixtures with closed-form/constructed oracles, with **no CPM runtime, no I/O, no
   private data**. This is the primary verification of the numerics (the Category-C criticality concern,
   product-data integrity) and the bulk of the suite.
2. **Service-unit level (Tier A, `unit`/`ci_integration`).** Each `common` service (`C-COM-*`) and the
   `sensors` profile layer are tested in isolation (round-trip, validation, exception) on the POSIX path.
3. **Component-integration level (Tier A, `@pytest.mark.ci_integration`, CI-blocking).** Each PU
   **Wrapper** is integrated with its Core and the `common` services and run through the CPM `run()`
   contract on a **synthetic** `EOProduct` + synthetic ADFs on the POSIX path (IF-CHAIN-01, IF-SVC-*,
   IF-PROD-*). Then sub-chains and the **full synthetic `L0c`→`L2A` chain** are integrated and run end to
   end via `C-COM-ORC` (IF-TRIG-01). This proves chaining, breakpoints, Zarr persistence and fail-stop
   **without** private data — so it stays blocking in public CI.
4. **System-integration level (Tier B, `@pytest.mark.integration`, local / `allow_failure` / skipped).**
   The full chain and sub-chains are integrated on **real** `L0c` + private ADFs + the real profile through
   the EOPF CPM runtime with real `EOZarrStore` I/O, including the chunked/Dask and S3 paths. These need
   private data and/or services absent from the public runner, so they `pytest.skip` when
   `MSI_PROCESSOR_DATA` is unset and are `allow_failure` in public CI.

Tier C numerical-budget validation (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`,
`MEM_BUDGET`) is **validation, not unit/integration testing**, and is out of SUITP scope — it remains in
the V&V Plan (RD-8 §4/§9) and is reported in the SVR (RD-12). The integration tests here verify the chain
**runs correctly and produces well-formed products**, not that the numbers meet the private budgets.

### <7.2> Tasks and items under test

The SUITP tasks refine the V&V-Plan validation tasks (RD-8 §9, VT-1..VT-10) into unit/integration test
designs. Items under test are the SDD components of `<4>`. Criteria are in `<7.5>` (general) and per case
in `<9>`.

| Task (this SUITP) | Items under test (C-*) | Maps to V&V task | Tier | Test design(s) |
|---|---|---|---|---|
| UT functional cores | `C-PU-L0/RAD/ENH/TOA/COR/GEO/PAN/ATM/QA` `.core` | VT-1 | A | TD-UT-L0..QA |
| UT common services | `C-COM-PRODUCT/IO/ADF/PROFILE/PROV/QAFLAG/CHUNK/CONFIG`, `errors` | VT-1, VT-9 | A | TD-UT-COMMON, TD-UT-PROFILE |
| IT component (wrapper) | `C-PU-*.unit` + `C-COM-*` | VT-1, VT-7 | A | TD-IT-WRAP |
| IT chain (synthetic) | `C-COM-ORC` + full PU DAG | VT-2, VT-7 | A | TD-IT-CI-CHAIN |
| IT chain (real-RAW) | full chain on real data via CPM runtime | VT-2 | B | TD-IT-RAW-CHAIN |
| IT chunked/Dask | `C-COM-CHUNK` + spatial PUs | VT-2 (memory) | A (synchronous) + B (distributed) | TD-IT-DASK |
| IT adaptation | `C-SENSORS` + `C-COM-PROFILE` (2nd profile, ADF swap) | VT-10 | A + B | TD-IT-ADAPT |
| IT install/acceptance | wheel + clean env | VT-8 | B | TD-IT-INSTALL |

### <7.3> Features to be tested

All functional features of the SRS (RD-4 `<5.2>`) realised by the components of `<4>`, referenced to their
applicable documentation (Annex K `<7.3>`a):

- **L0 decode / loss / legality / assembly** (REQ-F-L0-01..04; DPM-M-L0; ALG-L0-DEC/LOSS; SDD `<5.4.2>`).
- **Radiometric: dark/DSNU, NUC/PRNU, BPR, saturation/no-data, optional NUC derivation** (REQ-F-RAD-01..05;
  DPM-M-RAD; ALG-RAD-*; SDD `<5.4.3>`).
- **Enhancement (mandatory): MTF compensation (MTFC) by PSF deconvolution always runs; profile-configurable
  denoise sub-step** (REQ-F-ENH-01..03; SDD `<5.4.4>`).
- **TOA: DN→radiance, optional reflectance, `L1B` emission** (REQ-F-TOA-01..03; SDD `<5.4.5>`).
- **Co-registration: feature-based alignment, acceptance, fail-stop** (REQ-F-COR-01..03; SDD `<5.4.6>`).
- **Georeference: geolocation/GSD/GCP/DEM-ortho/resample, `L1C` emission** (REQ-F-GEO-01..04; SDD `<5.4.7>`).
- **Pan-sharpen (opt): MS↔PAN fusion** (REQ-F-PAN-01/02; SDD `<5.4.8>`).
- **Atmospheric: AOT/WV ingest/retrieve, TOA→BOA, scene-class + masks, `L2A` emission** (REQ-F-ATM-01..04;
  SDD `<5.4.9>`).
- **QA metrics + per-pixel flag propagation** (REQ-F-QA-01/02; SDD `<5.4.10>`).
- **Product generation + provenance (Zarr round-trip)** (REQ-F-PRD-01/02; SDD `<5.4.11>` C-COM-PRODUCT/PROV).
- **Orchestration: PU declaration, breakpoints, sub-chain/full-chain, fail-stop, determinism, chunked**
  (REQ-F-ORC-01/02, REQ-F-DEP-01/02; SDD C-COM-ORC/CHUNK).
- **Interfaces / operability: CLI + Python API + triggering payload, URI I/O, logs/report/status, modes**
  (REQ-I-02/05/06, REQ-O-01..04; SDD C-COM-CLI/ORC/IO).
- **Portability: local-FS path on CI, SDE↔local relocation** (REQ-PORT-01..03).
- **Adaptation: profile validation, second profile, ADF swap** (REQ-AD-01/02/04/05, REQ-D-07, REQ-M-02,
  REQ-DAT-03; SDD C-SENSORS/C-COM-PROFILE).
- **Data/security plumbing: read-only inputs, no private data committed, ADF validity reject** (REQ-F-L0-05,
  REQ-S-04/05, REQ-DAT-01..03).

### <7.4> Features not to be tested (by unit/integration testing)

Per Annex K `<7.4>`a, the following are **not** covered by this SUITP and are verified elsewhere, with
rationale:

- **Numerical accuracy/performance budgets** (REQ-P-01..05, REQ-Q-03, REQ-F-COR-02, REQ-F-GEO-03,
  REQ-F-PAN-02) — Tier C **validation** against private reference products; in the V&V Plan (RD-8 §9–§10)
  and SVR (RD-12), not unit/integration testing.
- **Static quality requirements** (REQ-D-02/04, REQ-Q-01/04, REQ-S-01/02, security/complexity/style/typing)
  — verified by **inspection/static-analysis gates** (linters, `mypy`, `bandit`, `xenon`, SonarQube,
  secret/threshold scan), V&V Plan `<7.3>`, not by pytest cases.
- **Not-applicable closures** (REQ-D-08 in-flight modification, REQ-R-05 real-time, REQ-REL-03 availability)
  — verified by **review of design** (V&V Plan `<14>`).
- **Full-ground-segment behaviour** (real orchestration triggering at scale, product dissemination/STAC
  cataloguing, multi-node Dask-gateway scaling, mission-volume throughput) — **system-level validation**
  with host support (V&V Plan `<13>`); SUITP exercises only their local/CPM representation.
- **`[impl]` body internals beyond their fixed interface** (NDA L0 bit-codec body, rigorous collinearity
  geoloc body, down-selected RT engine + classifier, exact filter/matcher tunings) — their **interface and
  exception behaviour** are tested at CDR; body-level cases are added during WP-5 against the frozen
  interface.

### <7.5> Test pass-fail criteria

**General per-test pass/fail (Annex K `<7.5>`a).** A test case **passes** iff its oracle is satisfied:
(a) **closed-form** cases — output equals the analytic value within the declared `numpy.testing.assert_allclose`
`rtol`/`atol` (public, non-sensitive bounds on synthetic data); (b) **constructed** cases — the injected
invariant is recovered within the declared synthetic tolerance (e.g. recovered homography ≈ injected;
truncated lines == injected loss; flags set exactly on injected defects); (c) **round-trip** cases —
read-back equals written (bit-identical for integer/structure, `assert_allclose` for float); (d)
**determinism** cases — two runs on identical inputs are bit-identical (deterministic kernels) or within
tolerance (stochastic kernels with fixed seed) (REQ-F-DEP-02); (e) **exception/fail-stop** cases — the
**expected typed `MsiProcessorError` subclass** is raised, the correct `QAFlag` is set, the run exits
non-zero and **no product is published** (REQ-F-DEP-01); (f) **structure** cases — the emitted `EOProduct`
DataTree conforms to the ICD (RD-5 `<5.3.3>`) groups/dtypes/dims/attrs. A test **fails** on any
unsatisfied oracle, an unexpected exception, or a non-zero static-error.

**Campaign-level entry criteria.**
- *Unit campaign (Tier A) entry:* the component's SDD detailed design (RD-9 `<5.4>`) is baselined; the
  Core public signature is implemented (stub or full); fixtures for the case exist; the test environment of
  `<9.2.6>` is provisioned. (Tests are authored **with** the component — TDD where practical, RD-1 §5.3.)
- *Integration campaign (Tier A chain) entry:* all constituent PUs' unit tests pass; the synthetic profile
  and synthetic ADFs are available; `C-COM-ORC` is implemented.
- *Integration campaign (Tier B) entry:* the Tier A chain passes; `MSI_PROCESSOR_DATA` resolves to a real
  `L0c` + ADF + real profile set; the EOPF SDE/local runtime (`eopf == 2.8.1`) is available.

**Campaign-level exit criteria.**
- *Tier A exit (blocking, required at every MR and at QR):* **100 % of `unit` + `ci_integration` cases
  pass**; the **coverage gate is met** (`<7.5>` coverage targets); 0 collection/import errors; all static
  gates green or waived.
- *Tier B exit (required at QR for the delivered configuration):* the full real-RAW chain and the required
  sub-chains **run to completion and produce ICD-conformant products** (TD-IT-RAW-CHAIN, -DASK, -ADAPT,
  -INSTALL pass), or any non-execution is recorded as a data-availability open item deferred to the SVR.

**Coverage targets (REQ-Q-02; SPAP RD-17 §5.5).**
- **Blocking gate:** line coverage **≥ 70 % on new code** (the SonarQube/`coverage` gate; CI fails below).
- **Project targets (tracked, non-gating):** pure **Core** modules (`*.core`) — the criticality-relevant
  numerics — target **≥ 90 % line and ≥ 85 % branch** coverage, with every typed-exception path and every
  QA-flag branch exercised; `common` services target **≥ 80 % line**. The `[impl]`-marked bodies are
  exempt until WP-5 completion, then folded into the same targets.

### <7.6> Manually and automatically generated code

There is **no auto-generated code** in `msi-processor` (RD-1 §5.3; V&V Plan `<5.1>`). All code is manually
written; the unit/integration test activities of this plan apply uniformly to it. This statement closes
the Annex K `<7.6>` / ECSS-Q-ST-80 §6.2.8.2 vs §6.2.8.7 distinction for the whole SUITP.

---

## <8> Software unit test / integration test design

### <8.1> General

Per Annex K `<8.1>`a/b this clause defines the unit and integration **test designs**; for each, `<8.2>`
gives the identifier, the features/items, the approach refinement and the associated test cases. Per the
`<8.1>`b NOTE the unit-test detail is **simplified** (Category C): related cases are grouped per component
into one design, and the full `<8.2>` aspect set is given once as a template (`<8.2>` below) then
instantiated compactly in the **design catalogue** (`<8.3>`).

### <8.2> Organization of each identified test design (template)

Each test design is described by the Annex K `<8.2.1>`–`<8.2.4>` aspects:

- **`<8.2.1>` Test design identifier** — unique id (`TD-UT-*` unit / `TD-IT-*` integration) + a one-line
  description.
- **`<8.2.2>` Features to be tested** — the test items (component(s) and the specific functions/`run()`)
  and the features, with references to the SRS (`REQ-*`), SDD (`C-*`/`IF-*`), DPM (`DPM-M-*`) and ATBD
  (`ALG-*`) (traceability).
- **`<8.2.3>` Approach refinements** — (a) the **test class** (unit / component-integration / chain-
  integration) and approach; (b) the rationale for case selection/grouping; (c) the **result-analysis
  method** (the oracle — closed-form / constructed / round-trip / determinism / exception / structure;
  `assert_allclose`); (d) the **facility configuration** (hw + sw, tier, marker, scheduler, data root).
- **`<8.2.4>` Test case identifier** — the `TC-*` cases associated with the design (catalogue in `<9>`).

### <8.3> Test design catalogue

#### Unit test designs (Tier A, `@pytest.mark.unit` unless noted)

| TD id | Description | Items / functions | Trace (REQ / C / DPM·ALG) | Approach & oracle (`<8.2.3>`) | Facility (`<8.2.3>`d) | Cases |
|---|---|---|---|---|---|---|
| **TD-UT-L0** | L0 decode, loss, legality, initial QA | `l0_decode.core`: `decode`*[impl]*, `detect_and_truncate_loss`, `check_legality`, `initial_qa` | REQ-F-L0-01..04; C-PU-L0; DPM-M-L0 / ALG-L0-DEC,LOSS | Unit; constructed (inject known loss → assert truncation+`LOST_PACKET`; malformed → `InputValidationError`); `decode` tested at interface level on a stubbed codec | CI shell runner; POSIX; no I/O | TC-L0-01..05 |
| **TD-UT-RAD** | Dark/NUC/BPR/saturation + optional NUC derivation | `radiometric.core`: `estimate_nuc`, `apply_nuc`, `detect_bad_pixels`, `replace_bad_pixels`, `flag_saturation`, `remove_dark_fft` | REQ-F-RAD-01..05; C-PU-RAD; DPM-M-RAD / ALG-RAD-* | Unit; **closed-form** (`X=dn·g+o−d`); constructed (inject bad/saturated → `DEFECTIVE`/`SATURATED`, neighbour interp); clip to range | CI; POSIX | TC-RAD-01..07 |
| **TD-UT-ENH** | MTF compensation (mandatory) + configurable denoise | `enhancement.core`: `mtf_compensate` (PSF deconvolution), `denoise` (+kernels) | REQ-F-ENH-01..03; C-PU-ENH; ALG-ENH-* | Unit; **mandatory MTFC always runs** — constructed (flat/known-PSF in→restored within tol; radiometry preserved; output clipped); denoise sub-step **profile-configurable** (method selectable per profile); bad denoise method → `InputValidationError` at profile validation | CI; POSIX | TC-ENH-01..05 |
| **TD-UT-TOA** | DN→radiance, optional reflectance, geometry | `toa.core`: `dn_to_radiance`, `radiance_to_reflectance`, `earth_sun_distance`, `solar_geometry`*[impl]* | REQ-F-TOA-01..02; C-PU-TOA; ALG-TOA-RAD,REF | Unit; **closed-form** (`L=(DN−o)·g`; `ρ=πLd²/(E cosθ)`, clip[0,1]); assert heritage `radiance−=min` is **not** applied | CI; POSIX | TC-TOA-01..04 |
| **TD-UT-COR** | Inter-band co-registration, acceptance, fail-stop | `coregistration.core`: `estimate_homography`, `warp_to_reference`, `coregister` | REQ-F-COR-01,03; C-PU-COR; ALG-COR-* | Unit; **constructed** (apply known homography to a band, assert recovery within px tol); insufficient keypoints → `CoregistrationError`+`COREG_FAIL`; fixed `seed` (REQ-F-DEP-02) | CI; POSIX; seeded RNG | TC-COR-01..04 |
| **TD-UT-GEO** | GSD, orbit, geolocate, GCP refine, resample | `georeference.core`: `compute_gsd`, `orbit_state`*[impl]*, `geolocate`*[impl]*, `refine_with_gcp`, `resample_to_grid` | REQ-F-GEO-01,02,04; C-PU-GEO; ALG-GEO-* | Unit; closed-form (`GSD=alt·pitch/focal`); constructed on a synthetic grid+flat DEM (assert known pixel→ground mapping); resample identity on aligned grid; rigorous body interface-level *[impl]* | CI; POSIX | TC-GEO-01..05 |
| **TD-UT-PAN** *(opt)* | MS↔PAN align + fuse | `pansharpen.core`: `align_ms_to_pan`, `fuse` | REQ-F-PAN-01; C-PU-PAN; ALG-PAN-ALIGN,FUSE | Unit; constructed (`simple_mean=½(MS+PAN)` closed-form; align reuses COR machinery); clip; spectral metric reported not gated | CI; POSIX | TC-PAN-01..03 |
| **TD-UT-ATM** | AOT/WV, TOA→BOA, scene class | `atmospheric.core`: `get_atmospheric_parameters`*[impl]*, `toa_to_boa`*[impl]*, `classify_scene`*[impl]* | REQ-F-ATM-01..03; C-PU-ATM; ALG-ATM-* | Unit; **interface-level** at CDR (new dev): ingest path with a synthetic LUT → BOA in [0,1]; mask shapes/dtypes; body cases in WP-5 | CI; POSIX | TC-ATM-01..04 |
| **TD-UT-QA** | Metrics + flag merge | `qa.core`: `compute_metrics`, `align_extent`, `merge_flags`; `C-COM-QAFLAG` | REQ-F-QA-01,02; C-PU-QA, C-COM-QAFLAG; ALG-QA-* | Unit; **closed-form** (SNR/RMSE/PSNR/MSE/variance on known arrays; PSNR=∞ when MSE=0); flag merge OR-monotone; extent-crop | CI; POSIX | TC-QA-01..05 |
| **TD-UT-COMMON** | Product/IO/ADF/PROV/CHUNK/CONFIG + errors | `C-COM-PRODUCT/IO/ADF/PROV/CHUNK/CONFIG`, `errors` | REQ-F-PRD-01/02, REQ-I-06, REQ-PORT-03, REQ-F-ORC-02, REQ-S-04/05, REQ-DAT-01; IF-SVC-*; DPM-M-PRD | Unit/service; Zarr round-trip on POSIX (write→read identity); URI resolve local/POSIX; ADF validity reject → `AdfResolutionError`; provenance has ids/no coefficients; chunk-equivalence (synchronous Dask) | CI; POSIX; `scheduler="synchronous"` | TC-COM-01..08 |
| **TD-UT-PROFILE** | Profile schema + sensors layer | `C-COM-PROFILE`, `C-SENSORS` | REQ-AD-01/02, REQ-DAT-03, REQ-D-07; ICD `<5.3.6>` | Unit; valid synthetic profile loads to typed `Profile`; invalid/incomplete → `ProfileValidationError`; second synthetic profile validates (sensor-agnostic) | CI; POSIX | TC-PROF-01..04 |

#### Integration test designs

| TD id | Description | Items / interfaces | Trace (REQ / C / IF) | Approach & oracle | Facility (tier · marker · scheduler · data) | Cases |
|---|---|---|---|---|---|---|
| **TD-IT-WRAP** | Each PU `run()` integrated with Core + services on synthetic data | `C-PU-*.unit` + `C-COM-*`; IF-CHAIN-01, IF-SVC-*, IF-PROD-* | REQ-F-ORC-01, REQ-I-05, REQ-F-PRD-01, REQ-O-03; per-stage REQ-F-* | Component-integration; run `run(inputs,adfs,mode,**params)` on a synthetic upstream `EOProduct` + synthetic ADFs; assert next-level product structure + QA + provenance; assert typed error→fail-stop on a forced fault | A · `ci_integration` · synchronous · synthetic, POSIX (**blocking**) | TC-WRAP-01..09 |
| **TD-IT-CI-CHAIN** | Full synthetic `L0c`→`L2A` + sub-chains via orchestrator | `C-COM-ORC` + full DAG; IF-TRIG-01, IF-PROD-01..05, DPM-BKP-* | REQ-F-ORC-01, REQ-F-DEP-01/02, REQ-REL-02, REQ-F-PRD-01/02, REQ-PORT-03, REQ-I-02, REQ-O-01..04 | Chain-integration; drive a synthetic triggering payload through `run_chain`/CLI; full chain, each sub-chain at breakpoints, resume-from-breakpoint; determinism re-run; forced mid-chain fault → status≠0 + no publish | A · `ci_integration` · synchronous · synthetic, POSIX (**blocking**) | TC-CHN-01..08 |
| **TD-IT-RAW-CHAIN** | Full chain on **real** `L0c` + private ADFs via CPM runtime | full chain + real `EOZarrStore` I/O | REQ-F-ORC-01, REQ-R-01/02, REQ-I-03/04/06, REQ-PORT-01/02, REQ-REL-02, REQ-M-02 | System-integration; real triggering payload → real products; assert run completes, products ICD-conformant, provenance correct; product **values** are Tier-C validation (not here) | B · `integration` · default · **real, local** (`allow_failure`/skip) | TC-RAW-01..05 |
| **TD-IT-DASK** | Chunked larger-than-memory + distributed equivalence | `C-COM-CHUNK` + spatial PUs (ENH/COR/GEO/PAN/ATM) | REQ-F-ORC-02, REQ-R-04, REQ-P-05 | (a) Tier A: `map_over_blocks(use_dask=True, synchronous)` == whole-array result (chunk-equivalence, with halo); (b) Tier B: real multi-worker run, peak per-worker memory bounded by chunk | A (equivalence) + B (distributed) · `ci_integration`/`integration` | TC-DASK-01..03 |
| **TD-IT-ADAPT** | Second profile + ADF swap (sensor-agnosticism) | `C-SENSORS`, `C-COM-PROFILE`, full chain | REQ-D-07, REQ-AD-01/02/04, REQ-M-02 | Integration; run the chain under a **second synthetic profile** (Tier A) and, locally, swap an ADF without code change → product updates (Tier B); assert no core change required | A (2nd synth profile) + B (real ADF swap) | TC-ADP-01..03 |
| **TD-IT-INSTALL** | Clean install + acceptance run | wheel + clean env (SDE + local) | REQ-AD-05, REQ-R-03, REQ-DEL-01 | Integration/acceptance; `pip install` the tagged wheel in a clean env; run the synthetic acceptance chain (and, locally, a real acceptance scene); assert install succeeds and acceptance suite passes | B · `integration` · SDE + local | TC-INS-01..02 |

---

## <9> Software unit and integration test case specification

### <9.1> General

Per Annex K `<9.1>`a/b this clause identifies the unit/integration **test cases**. Each case is specified
by the Annex K `<9.2.1>`–`<9.2.9>` aspects. Per the Category-C simplification, the full aspect set is given
once as the template (`<9.2>`), one **worked example per test class** is given in full (`<9.3>`), and the
remaining cases are specified compactly in the **case catalogue** (`<9.4>`); the per-case environment,
constraints, dependencies and script are constant within a tier and stated in `<9.2.6>`–`<9.2.9>` rather
than repeated.

### <9.2> Organization of each identified test case (template)

- **`<9.2.1>` Test case identifier** — unique id (`TC-<area>-NN`) + a short statement of purpose.
- **`<9.2.2>` Test items** — the component(s)/function(s) under test, with SRS/SDD references and
  traceability (`<9.2.2>`b).
- **`<9.2.3>` Inputs specification** — the synthetic fixture(s) and parameters (seed, profile, ADFs).
- **`<9.2.4>` Outputs specification** — the expected output (closed-form value / constructed invariant /
  structure / exception).
- **`<9.2.5>` Test pass-fail criteria** — the oracle and tolerance (per `<7.5>`).
- **`<9.2.6>` Environmental needs** — *Tier A:* CI shell runner or local, Python 3.11, `eopf == 2.8.1`,
  POSIX FS, Dask `scheduler="synchronous"`, **no** S3/gateway/private data; seeded RNG. *Tier B:* local
  workstation / EOPF SDE, real runtime, `MSI_PROCESSOR_DATA` set, POSIX/S3 store. Support-software config =
  the fixture factories of `<5.5>` (the "simulation configuration").
- **`<9.2.7>` Special procedural constraints** (ECSS-Q-ST-80 §6.3.5.25) — *Tier A:* must run without
  network/private data and complete within the CI time budget; deterministic (seed fixed). *Tier B:* runs
  only when private data is present (auto-skip otherwise); never writes into the read-only `L0` input
  (REQ-F-L0-05); private numbers never logged/committed (REQ-S-05).
- **`<9.2.8>` Interfaces dependencies** — cases to run before this one: unit cases have **none**;
  component-integration (`TC-WRAP-*`) depend on the corresponding unit cases passing; chain cases
  (`TC-CHN-*`, `TC-RAW-*`) depend on all constituent `TC-WRAP-*`; `TC-INS-*` depend on a green pipeline.
- **`<9.2.9>` Test script** — the pytest module implementing the case
  (`tests/unit/test_<stage>.py::test_<case>` or `tests/integration/test_<area>.py::test_<case>`); scripts
  collected per `<11>`.

### <9.3> Worked examples (one per test class)

**TC-RAD-01 — DN→corrected radiometric value (closed-form unit).**
- `<9.2.1>` Verify `apply_nuc` computes `X = dn·gain + offset − dark` in float32 (ALG-RAD-DARK).
- `<9.2.2>` Item: `radiometric.core.apply_nuc` (C-PU-RAD); trace REQ-F-RAD-01/02; DPM-M-RAD.
- `<9.2.3>` Inputs: `dn` = fixed `uint16` array (e.g. `make_bandstack(seed=0)`); per-detector `gain`,
  `offset`, `dark` = fixed float32 vectors.
- `<9.2.4>` Output: array equal to the elementwise `dn*gain+offset-dark` reference computed independently.
- `<9.2.5>` Pass: `assert_allclose(out, ref, rtol=1e-6, atol=0)` and `out.dtype==float32`.
- `<9.2.6>`–`<9.2.9>`: Tier A defaults; no dependencies; `tests/unit/test_radiometric.py::test_apply_nuc`.

**TC-WRAP-04 — TOA wrapper emits a structurally valid `L1B` (component integration).**
- `<9.2.1>` Verify `ToaUnit.run()` produces an `L1B` `EOProduct` with radiance + QA + provenance.
- `<9.2.2>` Items: `toa.unit.ToaUnit` + `C-COM-PRODUCT/PROV/QAFLAG` (IF-CHAIN-01, IF-SVC-*); trace
  REQ-F-TOA-03, REQ-F-PRD-01/02, REQ-O-03.
- `<9.2.3>` Inputs: synthetic `rad` `EOProduct` + synthetic `radiometric` ADF + synthetic profile.
- `<9.2.4>` Output: `{"l1b": EOProduct}` with `/measurements/radiance/<band>`, `/quality/mask/<band>`
  (`uint16`), root provenance attrs (ids/versions, **no** coefficients).
- `<9.2.5>` Pass: groups/dtypes/dims match ICD `<5.3.3>`; provenance keys present; no private numeric in
  attrs; round-trip via `EOZarrStore` on POSIX is identical.
- `<9.2.6>` Tier A (`ci_integration`, synchronous, POSIX); `<9.2.8>` depends on TC-TOA-01..04.

**TC-CHN-05 — Fail-stop on mid-chain fault (chain integration).**
- `<9.2.1>` Verify a forced PU failure yields exit≠0 and **no** product published (REQ-F-DEP-01).
- `<9.2.2>` Items: `C-COM-ORC` + DAG; trace REQ-F-DEP-01, REQ-F-COR-03, REQ-O-03.
- `<9.2.3>` Inputs: synthetic payload whose COR stage gets a band with too few features (forces
  `CoregistrationError`).
- `<9.2.4>` Output: `RunResult.status != 0`; report records the typed failure + `COREG_FAIL`; output URI
  empty.
- `<9.2.5>` Pass: status≠0 **and** no Zarr product at the output URI **and** the report names the stage +
  exception.
- `<9.2.6>` Tier A (`ci_integration`); `<9.2.8>` depends on TC-WRAP-* of the upstream stages.

**TC-RAW-01 — Real `L0c`→`L2A` completes with ICD-conformant products (system integration).**
- `<9.2.1>` Verify the full chain runs on a real scene and emits well-formed `L1B/L1C/L2A`.
- `<9.2.2>` Items: full chain + real `EOZarrStore` I/O; trace REQ-F-ORC-01, REQ-R-01/02, REQ-I-03/04.
- `<9.2.3>` Inputs: real `L0c` + private ADFs + real profile via `MSI_PROCESSOR_DATA`.
- `<9.2.4>` Output: three Zarr `EOProduct`s, ICD-conformant, with provenance.
- `<9.2.5>` Pass: run exits 0; products open and validate against ICD `<5.3.3>`; **values are not asserted
  here** (Tier C / SVR). `<9.2.7>` auto-skip if data absent; never write to `L0`.

### <9.4> Test-case catalogue

The complete enumerated cases per design (`<8.3>`), each with its purpose, oracle class and trace; full
`<9.2.3>`/`<9.2.4>` fixtures are specified in the test module docstrings at implementation (the `<9.2>`
template governs). Oracle key: **CF** closed-form · **CN** constructed · **RT** round-trip · **DT**
determinism · **EX** exception/fail-stop · **ST** structure.

| TC id | Purpose | Oracle | Trace (REQ · C) |
|---|---|---|---|
| TC-L0-01 | Decode synthetic `L0c` → per-band DN arrays (interface) | ST | REQ-F-L0-01 · C-PU-L0 |
| TC-L0-02 | Assemble `L1A` `EOProduct` structure | ST | REQ-F-L0-04 · C-PU-L0 |
| TC-L0-03 | Injected line/packet loss → truncation + `LOST_PACKET` | CN | REQ-F-L0-02 · C-PU-L0 |
| TC-L0-04 | Malformed/mismatched input → `InputValidationError` | EX | REQ-F-L0-03 · C-PU-L0 |
| TC-L0-05 | `initial_qa` sets `NO_DATA` on fill | CN | REQ-F-L0-02 · C-PU-L0 |
| TC-RAD-01 | `apply_nuc` `X=dn·g+o−d` | CF | REQ-F-RAD-01/02 · C-PU-RAD |
| TC-RAD-02 | `estimate_nuc` per-detector gain/offset | CF | REQ-F-RAD-02 · C-PU-RAD |
| TC-RAD-03 | Bad-pixel detect (gain bounds + BPM) | CN | REQ-F-RAD-03 · C-PU-RAD |
| TC-RAD-04 | Bad-pixel replace (neighbour interp) + `DEFECTIVE` | CN | REQ-F-RAD-03 · C-PU-RAD |
| TC-RAD-05 | Saturation/no-data clip + `SATURATED`/`NO_DATA` | CN | REQ-F-RAD-04 · C-PU-RAD |
| TC-RAD-06 | `remove_dark_fft` optional path | CF | REQ-F-RAD-01 · C-PU-RAD |
| TC-RAD-07 | NUC derivation (calibration mode) | CF | REQ-F-RAD-05 · C-PU-RAD |
| TC-ENH-01 | Denoise sub-step preserves flat signal within tol | CN | REQ-F-ENH-01 · C-PU-ENH |
| TC-ENH-02 | MTFC (PSF deconvolution) restores known-PSF blur within tol; radiometry preserved | CN | REQ-F-ENH-02 · C-PU-ENH |
| TC-ENH-03 | Denoise sub-step profile-configurable (method selectable per profile) | ST | REQ-F-ENH-03 · C-PU-ENH |
| TC-ENH-04 | Disallowed denoise method → `InputValidationError` | EX | REQ-F-ENH-03 · C-PU-ENH/PROFILE |
| TC-ENH-05 | Enhancement stage always runs (MTFC mandatory) even with denoise disabled | ST | REQ-F-ENH-03 · C-PU-ENH |
| TC-TOA-01 | `dn_to_radiance` `L=(DN−o)·g` | CF | REQ-F-TOA-01 · C-PU-TOA |
| TC-TOA-02 | heritage `radiance−=min` **not** applied | CF | REQ-F-TOA-01 · C-PU-TOA |
| TC-TOA-03 | `radiance_to_reflectance` `ρ=πLd²/(E cosθ)`, clip[0,1] | CF | REQ-F-TOA-02 · C-PU-TOA |
| TC-TOA-04 | `earth_sun_distance(doy)` | CF | REQ-F-TOA-02 · C-PU-TOA |
| TC-COR-01 | Recover injected homography within px tol | CN | REQ-F-COR-01 · C-PU-COR |
| TC-COR-02 | `warp_to_reference` shape/extent | ST | REQ-F-COR-01 · C-PU-COR |
| TC-COR-03 | Insufficient keypoints → `CoregistrationError` + `COREG_FAIL` | EX | REQ-F-COR-03 · C-PU-COR |
| TC-COR-04 | Determinism with fixed seed | DT | REQ-F-DEP-02 · C-PU-COR |
| TC-GEO-01 | `compute_gsd=alt·pitch/focal` | CF | REQ-F-GEO-01 · C-PU-GEO |
| TC-GEO-02 | Geolocate synthetic grid + flat DEM → known mapping | CN | REQ-F-GEO-01 · C-PU-GEO |
| TC-GEO-03 | `resample_to_grid` identity on aligned grid | CN | REQ-F-GEO-02 · C-PU-GEO |
| TC-GEO-04 | `L1C` CRS + geolocation layers emitted | ST | REQ-F-GEO-04 · C-PU-GEO |
| TC-GEO-05 | Missing DEM coverage → `GeolocationError` | EX | REQ-F-GEO-02 · C-PU-GEO |
| TC-PAN-01 | `simple_mean` fuse = ½(MS+PAN) | CF | REQ-F-PAN-01 · C-PU-PAN |
| TC-PAN-02 | Align MS→PAN reuses COR machinery | CN | REQ-F-PAN-01 · C-PU-PAN |
| TC-PAN-03 | Alignment failure → flag + skip fusion (no fail-stop) | EX | REQ-F-PAN-01 · C-PU-PAN |
| TC-ATM-01 | Ingest AOT/WV from synthetic aux | ST | REQ-F-ATM-01 · C-PU-ATM |
| TC-ATM-02 | `toa_to_boa` via synthetic LUT → BOA∈[0,1] | CN | REQ-F-ATM-02 · C-PU-ATM |
| TC-ATM-03 | `classify_scene` → mask shapes/dtypes + `CLOUD`/`CLOUD_SHADOW` | ST | REQ-F-ATM-03 · C-PU-ATM |
| TC-ATM-04 | Missing atmos/DEM → `AtmosphericError` | EX | REQ-F-ATM-01 · C-PU-ATM |
| TC-QA-01 | SNR=20log10(mean/std) | CF | REQ-F-QA-01 · C-PU-QA |
| TC-QA-02 | RMSE/MSE vs reference | CF | REQ-F-QA-01 · C-PU-QA |
| TC-QA-03 | PSNR=∞ when MSE=0 | CF | REQ-F-QA-01 · C-PU-QA |
| TC-QA-04 | `merge_flags` OR-monotone | CF | REQ-F-QA-02 · C-PU-QA/C-COM-QAFLAG |
| TC-QA-05 | `align_extent` crops to common extent | CN | REQ-F-QA-01 · C-PU-QA |
| TC-COM-01 | Build `EOProduct` DataTree per ICD | ST | REQ-F-PRD-01 · C-COM-PRODUCT |
| TC-COM-02 | Zarr write→read round-trip on POSIX | RT | REQ-F-PRD-01, REQ-PORT-03 · C-COM-PRODUCT |
| TC-COM-03 | `resolve_uri` local/POSIX; unresolvable → `InputValidationError` | EX | REQ-I-06 · C-COM-IO |
| TC-COM-04 | ADF validity mismatch → `AdfResolutionError` | EX | REQ-S-04 · C-COM-ADF |
| TC-COM-05 | Provenance has ids/versions, **no** coefficients | ST | REQ-F-PRD-02, REQ-S-05 · C-COM-PROV |
| TC-COM-06 | `set_flag`/`merge` bit operations | CF | REQ-F-QA-02 · C-COM-QAFLAG |
| TC-COM-07 | Chunk-equivalence (synchronous Dask) = whole-array | CN | REQ-F-ORC-02, REQ-R-04 · C-COM-CHUNK |
| TC-COM-08 | `resolve_config` payload→`RunContext` | ST | REQ-AD-04, REQ-O-01 · C-COM-CONFIG |
| TC-PROF-01 | Valid synthetic profile → typed `Profile` | ST | REQ-AD-01 · C-COM-PROFILE |
| TC-PROF-02 | Invalid/incomplete profile → `ProfileValidationError` | EX | REQ-DAT-03 · C-COM-PROFILE |
| TC-PROF-03 | Second synthetic profile validates | ST | REQ-D-07 · C-SENSORS/PROFILE |
| TC-PROF-04 | No instrument constants in code (profile-sourced) | ST | REQ-D-04 · C-SENSORS |
| TC-WRAP-01..09 | Each PU `run()` → correct next-level product + QA + provenance; forced fault → typed error/fail-stop | ST/EX | REQ-F-ORC-01, per-stage REQ-F-* · C-PU-*.unit |
| TC-CHN-01 | Full synthetic `L0c`→`L2A` runs, all products emitted | ST | REQ-F-ORC-01 · C-COM-ORC |
| TC-CHN-02 | Each sub-chain at breakpoints (`DPM-BKP-*`) | ST | REQ-F-ORC-01, REQ-REL-02 · C-COM-ORC |
| TC-CHN-03 | Resume from a written breakpoint product | ST | REQ-REL-02 · C-COM-ORC |
| TC-CHN-04 | Determinism: two full runs bit-identical/within-tol | DT | REQ-F-DEP-02 · C-COM-ORC |
| TC-CHN-05 | Mid-chain fault → status≠0, no publish | EX | REQ-F-DEP-01 · C-COM-ORC |
| TC-CHN-06 | CLI + Python API + triggering payload invocation | ST | REQ-I-02/05, REQ-O-01 · C-COM-CLI/ORC |
| TC-CHN-07 | Logs + report + status + diagnostics emitted | ST | REQ-O-02/03 · C-COM-ORC |
| TC-CHN-08 | Mode/state transitions (configured→processing→completed/aborted) | ST | REQ-O-04 · C-COM-ORC |
| TC-DASK-01 | `map_over_blocks(use_dask, synchronous)` == whole-array | CN | REQ-F-ORC-02 · C-COM-CHUNK |
| TC-DASK-02 | Halo handling for spatial PUs preserves edges | CN | REQ-F-ORC-02 · C-COM-CHUNK |
| TC-DASK-03 | (Tier B) multi-worker run, peak per-worker memory bounded | ST | REQ-R-04, REQ-P-05 · C-COM-CHUNK |
| TC-ADP-01 | Chain runs under second synthetic profile, no core change | ST | REQ-D-07, REQ-AD-01 · C-SENSORS |
| TC-ADP-02 | Per-run profile selection via payload | ST | REQ-AD-02 · C-COM-CONFIG |
| TC-ADP-03 | (Tier B) ADF swap without code change → product updates | ST | REQ-M-02 · C-COM-ADF |
| TC-RAW-01..05 | (Tier B) real chain + sub-chains complete; ICD-conformant; real POSIX/S3 I/O; relocation SDE↔local | ST | REQ-F-ORC-01, REQ-R-01/02, REQ-I-03/04/06, REQ-PORT-01/02 · full chain |
| TC-INS-01 | (Tier B) clean `pip install` of tagged wheel succeeds | ST | REQ-AD-05, REQ-R-03 · wheel |
| TC-INS-02 | (Tier B) acceptance chain passes in clean env | ST | REQ-AD-05, REQ-DEL-01 · full chain |

---

## <10> Software unit and integration test procedures

### <10.1> General

Per Annex K `<10.1>`a/b this clause identifies the test **procedures** — the executable sequences that run
the cases of `<9>`. Because the suite is `pytest`-driven, procedures are **marker selections** executed by
the CI pipeline (Tier A) or by a local shell runner (Tier B); each procedure executes one or more cases
(Annex K NOTE 3). For each procedure, `<10.2>` gives the identifier, purpose (with the cases it
implements) and the procedure steps.

### <10.2> Organization of each identified test procedure

#### <10.2.1>/<10.2.2> Procedure catalogue (identifier · purpose · cases implemented)

| TP id | Purpose | Tier · trigger | Cases implemented (`<10.2.2>`b) |
|---|---|---|---|
| **TP-A-UNIT** | Run all pure-core + service **unit** tests, blocking | A · CI job `unit-tests` (`pytest -m unit`) | all TC-{L0,RAD,ENH,TOA,COR,GEO,PAN,ATM,QA,COM,PROF}-* |
| **TP-A-INTEG** | Run **CI-integration** (wrapper + synthetic chain + chunk-equivalence), blocking | A · CI job `unit-tests` (`pytest -m ci_integration`) | TC-WRAP-*, TC-CHN-*, TC-DASK-01/02, TC-ADP-01/02 |
| **TP-A-COV** | Enforce the coverage gate | A · CI (`pytest --cov ... --cov-fail-under=70`) | (aggregate of TP-A-UNIT + TP-A-INTEG) |
| **TP-B-RAW** | Run **real-RAW** integration locally | B · local shell `run_integration.sh` (`pytest -m integration`) | TC-RAW-*, TC-ADP-03, TC-DASK-03 |
| **TP-B-INSTALL** | Clean-install acceptance | B · local/SDE `run_acceptance.sh` | TC-INS-01/02 |

The TP↔TC and TC↔TP traceability matrices are in `<11>`.

#### <10.2.3> Procedure steps

The eight Annex K `<10.2.3>` steps, instantiated per tier (constant across the cases each procedure runs):

**TP-A-UNIT / TP-A-INTEG / TP-A-COV (Tier A, CI, blocking).**
1. **Log.** `pytest` writes JUnit `TEST-pytests.xml` + console; `coverage` writes `coverage.xml`
   (Cobertura); both are CI artefacts (the standing per-MR record).
2. **Set up.** CI checks out the MR; installs the pinned env (`eopf == 2.8.1`, Python 3.11) on the shell
   runner; sets `dask` `scheduler="synchronous"`; seeds RNG via `conftest`; **no** S3/gateway/private data
   provisioned.
3. **Start.** Invoke `pytest -m unit` (TP-A-UNIT) / `pytest -m ci_integration` (TP-A-INTEG), with
   `--cov=msi_processor --cov-report=xml` (TP-A-COV).
4. **Proceed.** Collect and execute the selected cases on the POSIX path; fixtures are generated in-memory
   by the factories of `<5.5>`.
5. **Test result acquisition.** Each case's oracle (`<7.5>`) decides pass/fail; coverage % is measured;
   results aggregate to the JUnit + Cobertura artefacts and the SonarQube ingest.
6. **Shut down.** On collection/import error or runner interruption, the job fails fast and the pipeline
   reports red; temporary POSIX stores are discarded.
7. **Restart.** Restart point = re-run the job (Tier A is stateless and idempotent — deterministic seeds);
   no partial state to recover.
8. **Wrap up.** Pipeline turns the gate green only if **all** selected cases pass **and** coverage ≥ 70 %;
   merge is enabled; artefacts retained for the SVR (RD-12).

**TP-B-RAW / TP-B-INSTALL (Tier B, local, non-blocking/skipped in public CI).**
1. **Log.** The shell runner tees `pytest` output + the processing report (`ICD-IF-DIAG`) to a local,
   git-ignored log; only pass/fail verdicts (no private numbers) are transcribed to the SVR.
2. **Set up.** On the workstation / EOPF SDE: pinned env; export `MSI_PROCESSOR_DATA=<private root>`;
   ensure real `L0c` + ADFs + real profile + (optional) S3 endpoint are reachable.
3. **Start.** `pytest -m integration` (TP-B-RAW) / `run_acceptance.sh` (TP-B-INSTALL). If
   `MSI_PROCESSOR_DATA` is unset, the session fixture `pytest.skip`s the marker (clean skip, not failure).
4. **Proceed.** Execute the full chain / sub-chains through the CPM runtime with real `EOZarrStore` I/O
   (and the distributed Dask path for TC-DASK-03), treating `L0` as read-only.
5. **Test result acquisition.** Assert run completion (exit 0) and **product structure** conformance to the
   ICD; product **values** are deferred to Tier-C validation (SVR) — not asserted here.
6. **Shut down.** On interruption, stop after the current PU; written breakpoint products remain for resume.
7. **Restart.** Restart point = the last written level breakpoint (`DPM-BKP-*`); resume the sub-chain from
   there (REQ-REL-02) rather than from `L0`.
8. **Wrap up.** Record verdicts in the SVR; raise any non-execution as a data-availability open item; clean
   up scratch stores (never the read-only inputs).

---

## <11> Software test plan additional information

Per Annex K `<11>`a. (These matrices are summarised here and maintained authoritatively in RD-11.)

**1. Test procedures → test cases traceability.**

| TP | Test cases executed |
|---|---|
| TP-A-UNIT | TC-L0-*, TC-RAD-*, TC-ENH-*, TC-TOA-*, TC-COR-*, TC-GEO-*, TC-PAN-*, TC-ATM-*, TC-QA-*, TC-COM-*, TC-PROF-* |
| TP-A-INTEG | TC-WRAP-01..09, TC-CHN-01..08, TC-DASK-01/02, TC-ADP-01/02 |
| TP-A-COV | (coverage over TP-A-UNIT + TP-A-INTEG) |
| TP-B-RAW | TC-RAW-01..05, TC-ADP-03, TC-DASK-03 |
| TP-B-INSTALL | TC-INS-01/02 |

**2. Test cases → test procedures traceability.** Unit cases (TC-{L0,RAD,ENH,TOA,COR,GEO,PAN,ATM,QA,COM,
PROF}-*) → **TP-A-UNIT** (+ TP-A-COV). Component/chain cases (TC-WRAP-*, TC-CHN-*, TC-DASK-01/02,
TC-ADP-01/02) → **TP-A-INTEG** (+ TP-A-COV). Real-RAW cases (TC-RAW-*, TC-ADP-03, TC-DASK-03) →
**TP-B-RAW**. Install cases (TC-INS-*) → **TP-B-INSTALL**. The complete forward/backward
REQ↔component↔test-case closure is kept current in RD-11.

**3. Test scripts.** Implemented as `pytest` modules under `tests/`:
`tests/unit/test_<stage>.py` (Cores), `tests/unit/test_common_*.py` / `test_profile.py` (services),
`tests/integration/test_wrappers.py`, `tests/integration/test_chain.py`, `tests/integration/test_dask.py`,
`tests/integration/test_adapt.py`, `tests/integration/test_raw_chain.py`, `tests/integration/test_install.py`;
shared infrastructure in `tests/conftest.py` and `tests/factories/`. Markers are declared in
`pyproject.toml` (`[tool.pytest.ini_options].markers = ["unit", "ci_integration", "integration"]`).
Shell runners: `scripts/run_integration.sh`, `scripts/run_acceptance.sh`. CI wiring: `.gitlab-ci.yml`
(`unit-tests` job blocking; Tier B jobs `allow_failure: true` until a K8s runner is available).

**4. Detailed test procedures.** The step-level detail is the procedure-step instantiation of `<10.2.3>`
plus the per-module test docstrings (the `<9.2.3>`/`<9.2.4>` fixtures and oracles), authored with each
component during WP-5; `[impl]`-marked bodies (L0 codec, collinearity geolocation, RT engine, scene
classifier) have their interface-level cases defined now (`<9.4>`) and their body-level cases completed
against the frozen interface during implementation.

---

*End of SUITP. Authored per ECSS-E-ST-40C Rev.1 Annex K, tailored for Category C, single-developer. This
document is the CDR Part K of the V&V Plan (RD-8): it refines the three-tier scheme (Tier A unit/CI-
integration, blocking; Tier B real-RAW integration, local/skipped) into test designs (`<8>`), cases
(`<9>`) and procedures (`<10>`), each traced to the SRS (`REQ-*`, RD-4) and SDD (`C-*`/`IF-*`, RD-9).
Tier-C numerical-budget validation remains in the V&V Plan and is reported in the SVR (RD-12). The
maintained REQ↔design↔test traceability matrix is RD-11. Implementation (SDP WP-5) and the test code it
delivers start only after CDR.*
