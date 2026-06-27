# Software Verification & Validation Plan (V&V Plan — SVerP + SValP)

| Field | Value |
|---|---|
| **Document** | V&V Plan — Software Verification Plan (SVerP) merged with Software Validation Plan (SValP) |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex I (SVerP) + Annex J (SValP); ECSS-Q-ST-80C Rev.2 §6.2.6.1 |
| **Container** | Design Justification File (DJF) — `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | PDR (Preliminary Design Review) |
| **Status** | Draft for PDR |

> This document merges the **Software Verification Plan** (ECSS-E-ST-40C Rev.1 Annex I) and the
> **Software Validation Plan** (Annex J) into one V&V plan, per the tailored DRL of the SDP (RD-1,
> §5.5.2), which assigns SVerP, SValP and SUITP to the single file `compliance/drd/vv-plan.md`. It
> follows the Annex I and Annex J DRD section structures (clause-by-clause coverage in the table
> below) and mirrors the heading style of the SDP and SRS. The **SUITP** (Annex K — detailed
> unit/integration test *specifications and procedures*) is **produced at CDR** and will be
> appended to this file as Part K; this PDR issue defines the V&V **strategy, methods, organisation
> and the requirement→method map**, not the individual test-case procedures. The footprint is
> tailored to a Category C, single-developer ground-segment processor whose **code is public but
> whose raw `L0` data and instrument calibration are private** (RD-4 SRS <5.1>, <5.8>).

**DRD clause coverage.** Where this merged document satisfies each Annex I / Annex J clause:

| DRD clause | Topic | This document |
|---|---|---|
| SVerP (I) <1>/<2>/<3> | Intro / AD-RD / terms | <1>, <2>, <3> |
| SVerP (I) <4.1>..<4.7> | Verification process overview (general, org, schedule, resources, responsibilities, risks/independence, tools) | <5.1>..<5.7> |
| SVerP (I) <5> | Control procedures for verification | <6> |
| SVerP (I) <6.1>..<6.3> | Verification activities (general, process verification, quality-requirements verification) | <7.1>..<7.3> |
| SValP (J) <1>/<2>/<3> | Intro / AD-RD / terms | <1>, <2>, <3> (shared) |
| SValP (J) <4.1>..<4.8> | Validation process planning | <8.1>..<8.8> |
| SValP (J) <5> | Validation tasks identification | <9> |
| SValP (J) <6> | Validation approach | <10> |
| SValP (J) <7> | Validation testing facilities | <11> |
| SValP (J) <8> | Control procedures for validation | <12> |
| SValP (J) <9> | Complement of validation at system level | <13> |
| — (cross-cutting) | Requirement → method → tier → means map | <14> |

---

## <1> Introduction

**Purpose.** This V&V Plan describes the approach, organisation and methods used to **verify** the
`msi-processor` software (Annex I — "is the software built right?": each item conforms to its
specification, RD-4 SRS) and to **validate** it (Annex J — "is it the right software?": it meets the
Requirements Baseline RD-2/RD-3 and the operational objectives on data it was not fitted to). Both
plans are constituents of the Design Justification File.

**Objective.** Based on the verification and validation tasks implied by the SRS (RD-4), this
document addresses, per Annex I.1.2 and Annex J.1.2: the life-cycle activities and software products
subject to V&V; the required tasks, resources, responsibilities and schedule; the procedures for
forwarding V&V results; and the level of independence. It binds **every** SRS requirement (`REQ-*`)
to a verification method (**T** Test / **A** Analysis / **I** Inspection / **R** Review of design)
and to a place in the project's **three-tier V&V scheme** (clause <4>).

**Content.** Clause <4> defines the V&V strategy and the three-tier scheme that is the spine of the
whole plan. Clauses <5>–<7> are the **verification plan** (Annex I): process overview, control
procedures, and verification activities including software-quality-requirements verification.
Clauses <8>–<13> are the **validation plan** (Annex J): planning, tasks, approach, facilities,
control and the system-level complement. Clause <14> is the consolidated requirement→method→tier
map.

**Reason for preparation.** The project is an **integration and ECSS-productisation** effort
(RD-1 §1): the processing algorithms exist as prior work (RD-15; SRF RD-14) and are re-derived,
productised on the EOPF CPM and verified, rather than researched anew. This plan is produced at PDR
to baseline the V&V approach **before** detailed design (SDD) and before implementation begins
(implementation starts only after CDR, RD-1 §5.1). It is the parent of the Software Verification
Report (SVR, RD-8) delivered at QR.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software (Annex I SVerP, Annex J SValP, Annex K SUITP, Annex M SVR) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software (§6.2.6.1 quality verification; §6.3.5 testing/validation; §7 product quality) | ECSS-Q-ST-80C Rev.2 |
| AD-3 | ECSS System engineering — General requirements (verification process) | ECSS-E-ST-10C Rev.1 |
| AD-4 | EOPF CPM — Product Structure & Format Definition (PSFD) / data model | EOPF CPM docs (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Control Document (ICD) | `compliance/drd/icd-interface-control.md` (PDR/CDR) |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) | `docs/dpm/` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) | `docs/atbd/` |
| RD-8 | `msi-processor` Software Verification Report (SVR, Annex M) | `compliance/drd/vv-report.md` (QR) |
| RD-9 | `msi-processor` SUITP (Annex K — unit/integration test specifications & procedures) | **this file, Part K** (appended at CDR) |
| RD-10 | `msi-processor` Traceability matrix | `compliance/traceability/traceability-matrix.md` (CDR) |
| RD-11 | `msi-processor` Software Review Plan (SRevP) | `compliance/drd/srevp-software-review-plan.md` |
| RD-12 | `msi-processor` Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |
| RD-13 | `msi-processor` Risk Register | `compliance/drd/risk-register.md` |
| RD-14 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` (CDR) |
| RD-15 | Prior work — multispectral pushbroom preprocessing pipeline (incl. `metrics_ips`: SNR/RMSE/PSNR/MSE/variance) | see SRF (RD-14) |
| RD-16 | EOPF CPM API documentation (`EOProduct`, `EOProcessingUnit`, `EOZarrStore`, triggering) | EOPF CPM (`eopf == 2.8.1`) |

---

## <3> Terms, definitions and abbreviated terms

The SDP §3, SSS <3> and SRS <3> glossaries apply in full. Only terms specific to V&V and not defined
there are listed.

| Term / abbr. | Definition |
|---|---|
| V&V | Verification and validation |
| Verification | Confirmation that an output of a life-cycle activity meets its specification (RD-4) |
| Validation | Confirmation that the software meets the Requirements Baseline (RD-2/RD-3) and its operational objectives |
| RB / TS | Requirements Baseline (SSS + IRD) / Technical Specification (SRS) — the two validation references (Annex J <4.1>b) |
| T / A / I / R | Verification methods: Test / Analysis / Inspection / Review of design |
| Tier A | Deterministic **synthetic unit** tests run in public CI, **blocking**, no I/O (see <4>) |
| Tier B | **Local real-RAW integration** tests on private `L0`+ADFs; non-blocking / skipped in public CI |
| Tier C | **Reference / validation-data metric** evaluation against accuracy budgets (local only) |
| Budget parameter | A per-profile numeric tolerance (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`, `MEM_BUDGET`) held privately (RD-4 SRS <5.1>) |
| Fixture | A synthetic, in-memory test input (NumPy/xarray array or minimal `EOProduct`) with a known expected response |
| QA metric | A quantitative quality figure (SNR, RMSE, PSNR, MSE, variance) per RD-4 REQ-F-QA-01 |
| SUITP | Software Unit & Integration Test Plan (Annex K) — detailed test specs/procedures, produced at CDR |
| SVR | Software Verification Report (Annex M) — the V&V results record, delivered at QR |

---

## <4> V&V strategy and the three-tier scheme

The data policy (public code / private raw data + calibration, RD-4 SRS <5.1>/<5.8>) and the public
CI runner (a **shell executor** with no container runtime, Dask gateway or S3, RD-1 §4.3) shape the
entire V&V approach. They are reconciled by a **three-tier scheme** that separates what can be
proven publicly, automatically and deterministically from what requires private data, real runtime
services, or reference products. Every requirement (clause <14>) is placed in exactly one primary
tier (some carry a secondary numerical-validation component in Tier C).

| Tier | Name | Where it runs | Inputs | Gating | Verifies |
|---|---|---|---|---|---|
| **A** | Deterministic synthetic unit tests | Public CI (shell runner) **and** local | **Synthetic, in-memory** fixtures; seeded RNG; **no** network/private-data/container/Dask/S3 | **Blocking** (pipeline fails on failure; coverage gate) | Functional correctness of the pure algorithmic cores and the EOProduct/Zarr-POSIX plumbing |
| **B** | Local real-RAW integration | Local workstation / EOPF SDE (later: K8s CI runner) | **Real** `L0c` + private ADFs + real profile, via the EOPF CPM runtime, `EOZarrStore`, optional Dask/S3 | **Non-blocking** in public CI (`allow_failure`) or **skipped** when private data absent | End-to-end PU chaining, real I/O, chunked/distributed execution, real product structure |
| **C** | Reference / validation-data metrics | Local only | Real products vs **reference products / cal-val targets**; QA metrics (SNR/RMSE/PSNR/MSE/variance) | Not in CI; results recorded in the SVR (RD-8) | Numerical product-quality and performance **budgets** (validation against the RB) |

**Tier A — deterministic synthetic unit tests (verification, blocking).** Each processing stage is
designed as a **pure, framework-independent algorithmic core** callable without the CPM runtime
(RD-4 REQ-D-03); Tier A tests these cores directly with `pytest -m unit` against synthetic NumPy/
xarray fixtures. Randomised cases are seeded (`numpy.random.default_rng(0)`) so runs are
reproducible (RD-4 REQ-F-DEP-02). Expected responses are **closed-form** where the algorithm is
analytic (e.g. `radiance = (DN − offset)·gain` for REQ-F-TOA-01; `corrected = sample·gain + offset −
dark` for REQ-F-RAD-01/02) and **constructed** otherwise (synthetic-shifted bands with a known
homography for REQ-F-COR-01; injected defective/saturated pixels for REQ-F-RAD-03/04; injected
line/packet loss for REQ-F-L0-02). Tier A uses **no private data and no real services**; the
EOProduct/Zarr round-trip (REQ-F-PRD-01) is exercised on the **POSIX** path that runs on the shell
runner (RD-4 REQ-PORT-03, REQ-I-04). Tier A is the CI-enforced verification gate.

**Tier B — local real-RAW integration (non-blocking / skipped).** Tier B drives full chains or
sub-chains (`L0c→L1A→…→L2A`, runnable at breakpoints, REQ-F-ORC-01) on **real** downlinked `L0c`
plus private calibration ADFs and the real sensor profile, through the EOPF CPM runtime and
`EOZarrStore`, including chunked/`Dask`-distributed and S3 paths (REQ-F-ORC-02, REQ-I-03/04/05/06,
REQ-R-01/02, REQ-PORT-01/02). Because these need private data and/or services unavailable on the
public shell runner, Tier B tests are marked `@pytest.mark.integration`, configured
`allow_failure: true` in public CI, and **auto-skip when the private data root is absent** (a
session fixture checks an `MSI_PROCESSOR_DATA` reference and `pytest.skip`s the marker otherwise).
This satisfies SYS-VV-02 (RD-2) without ever exposing private data to public CI (REQ-S-01). Tier B
becomes blocking once a Kubernetes runner replaces the shell executor (tracked as a risk, RD-13).

**Tier C — reference / validation-data metrics (local).** Tier C is the **numerical validation**
layer: real products are compared against reference products and/or cal-val targets to evaluate the
per-profile accuracy and performance **budgets** (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`,
`THRU_SCENE`, `MEM_BUDGET`; RD-4 REQ-P-01..05, REQ-Q-03, REQ-F-COR-02, REQ-F-GEO-03, REQ-F-PAN-02).
The quality figures are computed by a productised QA-metrics module derived from the prior-work
`metrics_ips.calculateMetrics.run_validation` (SNR, RMSE, PSNR, MSE, variance; RD-15) — refactored
into a **pure, `EOProduct`-aware** function with the interactive Tk file-dialog/`print` heritage
removed (RD-4 REQ-F-QA-01). Tier C runs locally only; its pass/fail verdicts and metric summaries
(not the private numbers themselves) are recorded in the SVR (RD-8).

### <4.1> Tolerances approach (parameterised; numbers not disclosed)

To honour the private-data policy (RD-4 REQ-S-01/REQ-S-05; SRS <5.1> note), **no instrument-derived
numeric value or budget threshold is written into source code, tests committed to the public
repository, or this document.** Tolerances are handled in two classes:

- **Algorithmic / determinism tolerances (Tier A).** Synthetic-fixture assertions use
  `numpy.testing.assert_allclose` with **fixed, public** `rtol`/`atol` (these are not sensitive —
  they bound float round-off on synthetic data) or assert **bit-identical** re-runs for
  deterministic kernels (REQ-F-DEP-02, REQ-D-05). Numerical processing uses explicit float precision
  and range clipping (REQ-D-05) so these bounds are stable across platforms.
- **Accuracy/performance-budget tolerances (Tier C).** The pass thresholds are **per-profile budget
  parameters** held in the private auxiliary/calibration store as named keys (e.g. `tol.rad_acc`,
  `tol.geo_ce90`, `tol.band_coreg`, `tol.boa_acc`, `tol.thru_scene`, `tol.mem_budget`). The Tier C
  harness **reads the value at runtime** from the active profile / private `thresholds.toml` and
  compares; this plan specifies only the **metric and comparison method** — e.g. `GEO_CE90` from GCP
  residual circular error at the 90th percentile, `BAND_COREG` from inter-band tie-point RMSE,
  radiometric/`BOA` accuracy via RMSE/relative error vs reference, `THRU_SCENE` as wall-time per
  reference scene, `MEM_BUDGET` as peak per-worker RSS — never the numeric target. A public,
  **synthetic profile** ships non-sensitive default tolerances so Tier A and the second-profile
  externalisation test (REQ-D-07, REQ-AD-01) can run in CI.

This separation is itself a verification item: a CI scan asserts that no private threshold or
calibration coefficient leaks into committed artefacts (REQ-S-01/05; <7.3>, SPAP RD-12 §6.4).

---

# Part I — Software Verification Plan (Annex I)

## <5> Software verification process overview

### <5.1> General (approach, effort, independence)

The verification approach is **continuous and automated**: verification is performed on **every**
merge request to `main` by the CI pipeline (RD-1 §5.4) and re-run on every change, so the Git/CI
history is the standing verification record. The dominant method is **T (Test)** — Tier A in public
CI, Tier B locally — backed by **I (Inspection)** for the static quality gates, **A (Analysis)** for
numerical-accuracy/sizing arguments and Tier C, and **R (Review of design)** for architectural and
not-applicable-closure items. The split of method per requirement is in clause <14>.

**Verification effort (Annex I <4.1> NOTE 2).** The effort is sized to a **Category C** product
whose worst-case failure is a degraded or mislabelled *data product*, recoverable by reprocessing —
no death/injury, mission loss or space-segment damage (RD-1 §5.6; SPAP RD-12 §6.3). The technology
risk is low (mature open-source reuse + existing algorithm heritage). Effort therefore concentrates
on (a) deterministic functional correctness of the algorithmic cores (Tier A, with a coverage gate),
and (b) numerical product correctness on real data (Tier C). The independent-software-verification
provisions of ECSS-Q-ST-80 §6.2.6.13 are **tailored out** (not applicable at Category C,
single-developer).

**Manually vs automatically generated code (Annex I <6.1>b).** There is **no auto-generated code**
(RD-1 §5.3); all code is manually written and the verification activities below apply uniformly to
it. This statement closes the manual/automatic-code distinction for the whole plan.

**Independence.** Personnel independence is not achievable in a single-developer project; it is
replaced by **automated, version-controlled gates** that fail independently of the developer's
opinion, a third-party adjudicator (SonarQube), and explicit review checklists — the model defined
in SPAP RD-12 §5.1 and SRevP RD-11 §11, applied here unchanged.

### <5.2> Organization

Verification is organised as a **two-tier review/CI process** (SRevP RD-11 §8): (1) continuous
merge-request review + CI quality gates on every change (the automated verification mechanism); and
(2) milestone consolidation at PDR/CDR/QR where the accumulated verification evidence is assessed and
baselined. Documentation review, tracing and proof activities are conducted asynchronously on the
GitLab platform (issues + MR threads); there is no physical board. Tracing is maintained in the
traceability matrix (RD-10) and summarised in SRS <7>.

### <5.3> Master schedule

The master schedule is referenced from the SDP (RD-1 §4.2, §5.2.3) and managed as GitLab group
`ipf` milestones (calendar dates are not duplicated here). Verification activities by milestone:

| Milestone | Verification activity |
|---|---|
| PDR (now) | Baseline this plan; verify SRS/ICD/DPM/ATBD/preliminary-SDD by review & inspection |
| CDR | Append the SUITP (RD-9); verify detailed design vs SRS; baseline the traceability matrix |
| post-CDR (impl.) | Tier A authored with each stage; CI gates run per MR (continuous) |
| QR | Run full Tier A; run Tier B/C locally; consolidate results in the SVR (RD-8); coverage gate evidence |
| AR | Confirm delivered-version verification evidence (SCF/SRN) is complete |

### <5.4> Resource summary

| Resource | Provision |
|---|---|
| Staff | One person (project owner) holding software, PA and verification roles (RD-1 §4.7) |
| Hardware | Development workstation (x86-64 Linux, multi-core CPU, no GPU); EOPF SDE Studio VM hosting the GitLab **shell-executor** CI runner; local storage/S3 endpoint for Tier B |
| Software tools | `pytest`+coverage, `mypy`, `flake8`/`black`/`isort`, `bandit`, `trivy`, `xenon`, `hadolint`, `docstr-coverage`, SonarQube, `pre-commit`; EOPF CPM runtime (`eopf == 2.8.1`); productised QA-metrics module (ex-`metrics_ips`) — see <5.7> |
| Test data | **Synthetic fixtures** (committed, Tier A); **private** real `L0c`+ADFs+reference products (local, Tier B/C — never committed) |

### <5.5> Responsibilities

The project owner is responsible for authoring and maintaining the Tier A test suite, the Tier B/C
local harness, this plan and the SVR; for ensuring each MR passes the blocking gates (or carries a
recorded waiver, SPAP RD-12 §6.5); and for recording verification verdicts. Automation
(CI + SonarQube) executes and adjudicates the gates, supplying verification independence.

### <5.6> Identification of risks and level of independence

Risks to the verification campaign are held in the Risk Register (RD-13); the V&V-relevant ones:

| Risk | Effect on verification | Mitigation |
|---|---|---|
| Private calibration/reference data unavailable | Tier B/C cannot run | Tier A fully covers functional cores on synthetic data; Tier B/C auto-skip; budgets deferred to SVR when data lands |
| Shell-runner limits (no container/Dask/S3) | Tier B non-blocking in CI | Tier B marked `allow_failure`/skip; promote to blocking on K8s runner |
| `eopf == 2.8.1` pin desync | Real-runtime tests break | Pin enforced; documented eopf-bump procedure re-runs full V&V before re-baseline (REQ-M-03) |
| Non-determinism in a kernel (e.g. feature matching) | Flaky Tier A | Seed RNG; assert within documented tolerance, not bit-identity, for stochastic kernels (REQ-F-DEP-02) |

**Level of independence:** automated gates + SonarQube adjudication + checklists, optionally an
external EOPF SDE reviewer at milestones (SRevP RD-11 §11). Tailored for Category C single-developer.

### <5.7> Tools, techniques and methods

| Tool | Role in verification | Method | Gating |
|---|---|---|---|
| `pytest` + `coverage` (cobertura/junit) | Tier A unit tests; Tier B integration (local) | T | **Blocking** (Tier A + coverage gate) |
| `mypy` | Static type-contract verification | I | **Blocking** |
| `flake8`, `black`, `isort` | Style/format conformance (PEP 8, REQ-D-02) | I | **Blocking** |
| `bandit` | SAST — Python security defects | I/T | **Blocking** |
| `hadolint` | Dockerfile lint | I | **Blocking** |
| `trivy` | SCA — dependency CVEs (HIGH/CRITICAL) | I | Non-blocking → blocking on K8s |
| `xenon` | Cyclomatic-complexity bound (REQ-D-04/Q-04) | A | Non-blocking → blocking |
| `docstr-coverage` | Docstring coverage (≥30 %) | I | Non-blocking |
| SonarQube | Quality-gate adjudication (reliability/security/debt/coverage) | I | Non-blocking → blocking |
| `pre-commit` | Local shift-left of format/lint hooks | I | Local |
| EOPF CPM runtime + `EOZarrStore` | Real product I/O and PU chaining (Tier B) | T | Local |
| QA-metrics module (ex-`metrics_ips`, RD-15) | SNR/RMSE/PSNR/MSE/variance for Tier C | A/T | Local |

**Techniques:** deterministic synthetic-fixture unit testing with seeded RNG; closed-form expected
responses; property/round-trip testing (Zarr write→read); failure-path testing (forced stage
failure, REQ-F-DEP-01); chunked larger-than-memory execution analysis; numerical comparison against
reference products; static analysis and design review. Tool versions and licences are recorded in
the SRF (RD-14).

## <6> Control procedures for verification process

Applicable management procedures (referenced, not redefined — SRevP RD-11, SPAP RD-12):

- **Problem reporting and resolution.** Verification findings (failing gate, failed test, defect)
  are raised as **GitLab issues** (`Bug`/`Action` templates) or auto-evidenced by a red pipeline,
  classified by severity (SPAP RD-12 §6.5), fixed via a linked MR that must re-pass the full gate
  set, and closed with the merge reference — end-to-end traceability from report to verified fix.
- **Deviation and waiver policy.** A blocking gate may be bypassed **only** by a waiver recorded on
  the issue with rationale and an expiry/closure condition (SPAP RD-12 §6.5); a non-blocking job
  that fails is justified in the MR.
- **Control procedures.** All verification artefacts (tests, configs, CI pipeline, this plan) are
  configuration items under Git, changed only through reviewed MRs (ECSS-M-ST-40C; SPAP RD-12 §6.5).
  Verification results are forwarded to the customer/PA function via the milestone review record and
  the SVR (RD-8) — this is the "procedure for forwarding verification reports" of Annex I.1.2.

## <7> Verification activities

### <7.1> General

The plan addresses the verification activities of the single software item `msi_processor` (Annex I
<6.1>a). As stated in <5.1>, all code is manually generated (Annex I <6.1>b closed). Activities are
of three kinds: **(a) software process verification** (<7.2>) — verifying the outputs of each
life-cycle activity; **(b) software product (functional/non-functional) verification** — the
requirement-level testing/analysis mapped in clause <14>, executed across Tiers A/B/C; and **(c)
software quality-requirements verification** (<7.3>) per ECSS-Q-ST-80 §6.2.6.1.

### <7.2> Software process verification

For each life-cycle activity, the verification performed, its inputs, outputs and methodology
(Annex I <6.2>a):

| Life-cycle activity | Verification performed (how) | Inputs | Outputs | Methodology / tools |
|---|---|---|---|---|
| Requirements & architecture | Each `REQ-*` is uniquely identified, has ≥1 upstream parent and a method (no orphans); preliminary SDD traces to SRS | Draft SRS (RD-4), preliminary SDD | Verification finding log; traceability summary (SRS <7>) | Review + traceability analysis (RD-10) |
| Detailed design | SDD detailed design reviewed against SRS; PU pattern (pure core + thin wrapper) confirmed | SDD, SRS | CDR review record | Design review (R); checklist (RD-11) |
| Coding | Style/format/typing/security/complexity gates on every MR | Source + CI configs | `linter.txt`, `mypy`/`bandit` logs, `xenon` report | I/A — flake8/black/isort/mypy/bandit/xenon |
| Unit & integration testing | Tier A blocking with coverage gate; Tier B locally | Test suite, fixtures, (private data) | `coverage.xml`, `TEST-pytests.xml` | T — pytest+coverage; SUITP procedures (RD-9, CDR) |
| Validation | Tier C numerical validation vs reference; operational runs | Real products, reference, profiles | SVR (RD-8) | A/T — QA-metrics module |
| Delivery & acceptance | Tagged CI build → wheel + versioned docs; no private data in artefacts | Tagged commit | Wheel, docs, checksums (SRN) | T/I |

### <7.3> Software quality requirements verification (ECSS-Q-ST-80 §6.2.6.1)

**<7.3.1> Activities.** Verify that the software meets the product-quality model (SPAP RD-12 §5.5):
test pass + line coverage ≥ 70 % (new code) by `unit-tests`; 0 lint/format/typing/SAST findings by
`linter`/`formater`/`typing`/`security`; bounded complexity by `xenon`; 0 HIGH/CRITICAL dependency
CVEs by `deps-sec`; documentation density by `docs-cov`; and the SonarQube quality verdict
(reliability A, security A, technical-debt ratio ≤ 5 %, 0 vulnerabilities). A dedicated check also
verifies **no private data, threshold or calibration coefficient is committed** (REQ-S-01/05).

**<7.3.2> Inputs.** The source tree, test suite and synthetic fixtures, CI configuration
(`.gitlab-ci.yml`, `pyproject.toml`, `.flake8`, `.mypy.ini`, `bandit.yml`, `.coveragerc`), and the
SonarQube project configuration.

**<7.3.3> Outputs.** The CI pipeline status and its artefacts (`linter.txt`, `coverage.xml`,
`TEST-pytests.xml`, `vulnerability.json`, trivy output, SonarQube dashboard) — the standing quality
record per MR — consolidated per milestone and into the SVR (RD-8).

**<7.3.4> Methodology, tools and facilities.** The toolchain of <5.7>, executed on the GitLab
shell-executor CI runner (with the noted non-blocking jobs pending a Kubernetes runner), adjudicated
by SonarQube. This realises the gate→PA-objective mapping of SPAP RD-12 §7.

---

# Part J — Software Validation Plan (Annex J)

## <8> Software validation process planning

### <8.1> General

Validation confirms that `msi-processor` meets the **Requirements Baseline (RB = SSS RD-2 + IRD
RD-3)** and its operational objectives, on **mission-representative real data and scenarios**
processed locally (SYS-VV-04). Per Annex J <4.1>b the project runs **two validation campaigns** that
share one environment: validation **against the RB** (operational adequacy of the products) and
validation **against the TS (SRS, RD-4)** (each `REQ-*` satisfied). Because both use the same local
SDE-equivalent environment, they do **not** require different environments (Annex J <7>c). Validation
of the **quality requirements** is included (Annex J <4.1>d) and is the Tier-C/quality-gate evidence
of <7.3>/<10>. As in <5.1>, there is **no auto-generated code**, so the manual/automatic-code
distinction (Annex J <4.1>c) is closed for all validation tasks.

**Required effort and independence.** Sized to Category C: validation effort concentrates on the
numerical product-quality budgets for the **first sensor profile** (the owner's sensor) and on
exercising the operational CLI/Python-API procedures. Independence is by automated gates + checklists
(as <5.1>), optionally an external EOPF SDE reviewer at QR/AR.

### <8.2> Organization

Validation activities are organised around the **milestone reviews** (SRevP RD-11): the
TS-validation campaign is consolidated at **QR** (qualification vs SRS), the RB-validation campaign
at **AR** (acceptance vs SSS/IRD), both fed continuously by Tier A (CI) and by the locally-run Tier
B/C harness. Relationships to the other activities (project management, development, configuration
management, product assurance) are as defined in the SDP and SPAP; the validation function is not a
separate organisation but the project owner in the verification/PA role. Level of implemented
independence: automated tooling + checklists (single-developer Category C).

### <8.3> Schedule

A reference to the master schedule is in the SDP (RD-1 §4.2); calendar dates live in the GitLab `ipf`
milestones. Test milestones and item-delivery events: Tier A continuous (per MR) from
implementation start (post-CDR); Tier B/C executed locally **before each milestone and each release**
and **after any algorithm change or `eopf` bump** (REQ-M-03); TS-validation completed by QR;
RB-validation/acceptance by AR. Period of use of the test facilities = the workstation/SDE for the
duration of Tiers B/C runs (no scheduled shared facility).

### <8.4> Resource summary

As <5.4>, plus the **validation-specific data and support software**: real `L0c` + private ADFs +
**reference products / cal-val targets** (the validation "testing data", private — local only); the
sensor profile(s) including a public **synthetic profile** for environment-independent checks; and
the QA-metrics module (ex-`metrics_ips`, RD-15) as the validation support software. No hardware
simulator is required (ground software; no real-time, no HW-in-the-loop).

### <8.5> Responsibilities

The project owner manages, designs, prepares, executes and checks the validation tests (Annex J
<4.5>) — there is no separate test team. Witnessing/checking independence is provided by the
recorded, automated evidence (CI artefacts, SVR) rather than a separate witness. PA review of
validation results occurs at QR/AR (SPAP RD-12 §6.8).

### <8.6> Tools, techniques and methods (validation facility characterisation)

Validation tools/techniques are those of <5.7> (Tiers B/C: EOPF CPM runtime, `EOZarrStore`,
QA-metrics module, `pytest`). The **validation facility** is characterised per Annex J <4.6>b:

| Facility aspect | Characterisation for `msi-processor` |
|---|---|
| 1. Representativeness (processor / real-time) | **Fully representative**: the EOPF SDE container (`eopf == 2.8.1`, Python 3.11) is the operational runtime; the same code runs on the workstation. **No real-time** representativeness needed (no hard timing, REQ-R-05) |
| 2. Software/hardware-in-the-loop | Not applicable — ground software, no HW-in-the-loop, no on-board element |
| 3. Open/closed-loop | **Open-loop**: deterministic batch processing of fixed inputs to products; functional and performance tests are open-loop |
| 4. Debugging / observability | Full — structured logs + processing report (REQ-O-02), per-pixel QA flags, provenance (REQ-F-PRD-02), pytest introspection |
| 5. Real-time constraints on test execution | None — no code-instrumentation interdiction; no real-time/safety measurement constraints |

### <8.7> Personnel requirements

One person (project owner), competent in Python, EOPF CPM, remote-sensing data processing and the
ECSS-E-40/Q-80 framework (RD-1 §4.7; SPAP RD-12 §5.3). No additional validation personnel and no
special training needs; no independent validation team is levied (Category C tailoring).

### <8.8> Risks

Validation-campaign risks (and contingency) are held in the Risk Register (RD-13); the dominant ones
are those of <5.6> — **private reference/cal-val data unavailability** (contingency: complete TS
functional validation on synthetic data via Tier A and defer budget validation to the SVR when data
is available, recording the open item) and the **shell-runner limitation** (contingency: run Tier
B/C locally; promote to CI on the K8s runner). Contingency plans are the auto-skip mechanism (<4>)
and the documented deferral of budget validation to the SVR.

## <9> Software validation tasks identification

The validation tasks, the items under test and their criteria (Annex J <5>):

| Task | Item(s) under test | Criteria | Tier | Inputs | Outputs | Resources |
|---|---|---|---|---|---|---|
| VT-1 Functional core validation | Pure algorithmic cores (all `REQ-F-*`) | Closed-form / constructed expected response within Tier-A tolerance | A | Synthetic fixtures | pytest report, coverage | CI runner |
| VT-2 Chain integration | PU chain + sub-chains at breakpoints (REQ-F-ORC-01/02) | Chain runs L0c→L2A; products well-formed; chunked within memory | B | Real `L0c`+ADFs+profile | Products, logs | Local/SDE, EOPF runtime |
| VT-3 Radiometric accuracy | L1B products (REQ-P-01, REQ-F-RAD/TOA) | RMSE/relative error vs reference within `RAD_ACC` | C | L1B vs reference | SVR metrics | QA-metrics module |
| VT-4 Geometric accuracy | L1C products (REQ-P-02, REQ-F-GEO/COR) | `GEO_CE90` (GCP residual CE90) and `BAND_COREG` (tie-point RMSE) within budget | C | L1C vs ground ref | SVR metrics | QA-metrics + geometry harness |
| VT-5 Surface-reflectance accuracy | L2A products (REQ-P-03, REQ-F-ATM) | BOA RMSE/relative error within `BOA_ACC` | C | L2A vs reference | SVR metrics | QA-metrics module |
| VT-6 Performance | End-to-end run (REQ-P-04/05) | `THRU_SCENE` (wall-time/scene), `MEM_BUDGET` (peak per-worker RSS) | C | Reference config run | Benchmark | Local/SDE |
| VT-7 Operational procedures | CLI / Python API / triggering payload (REQ-O-*, REQ-I-02/05) | Batch + sub-chain runs; logs/report/status/diagnostics correct | A/B | Synthetic + real | Run logs | CLI |
| VT-8 Installation & acceptance | Clean `pip install` (SDE + local) + acceptance set (REQ-AD-05) | Install succeeds; acceptance suite passes | B | Wheel, env | Install/test report | SDE + local |
| VT-9 Quality-requirements validation | Quality model (SPAP §5.5) | Gates green; SonarQube verdict pass | A | Source + CI | CI artefacts | CI + SonarQube |
| VT-10 Adaptation / second-profile | Sensor-agnosticism (REQ-D-07, REQ-AD-01/02) | Second (synthetic) profile runs without core change | A/B | Synthetic profile | Run result | CI/local |

**Resumption (Annex J <5>c).** If validation is interrupted, the tasks to **repeat on resume** are:
Tier A (re-run is cheap and authoritative) and any Tier B/C task whose inputs, profile, algorithm or
`eopf` version changed since the last successful run (REQ-M-03). Detailed per-task data and procedures
are deferred to the SUITP/SVS (Annex J <5>e; RD-9 at CDR).

## <10> Software validation approach

**Overall approach (Annex J <6>a).** Validation overall = Tier A functional adequacy (vs TS) +
Tier B operational/integration adequacy + Tier C numerical adequacy (vs RB budgets) + the
quality-gate evidence, consolidated in the SVR (RD-8). The kinds of tests to execute are those of
clause <9> (VT-1..VT-10). Each `REQ-*` carries a validation method inline in the SRS and is
consolidated in clause <14> and RD-10.

**Requirements validated by inspection/analysis/review of design (Annex J <6>b).** Requirements not
validated by test are validated as follows (full list in <14>): architecture/design and
not-applicable closures by **R** (REQ-D-01/08, REQ-R-05, REQ-REL-03, REQ-SAF-01, REQ-M-01/03,
REQ-O-04); toolchain/standards/data-standard/licence/naming and delivery-content by **I**
(REQ-D-02/06/09, REQ-Q-01/04, REQ-DEL-01..03, REQ-DAT-01/02, REQ-HF-01, REQ-I-01/07, REQ-AD-02/04);
access-mode/sizing/numerical/security-policy by **A** (REQ-F-L0-05, REQ-S-01/03/05, REQ-R-04,
REQ-D-04/05). These are evidenced by review records, static-analysis/grep scans, and CI/inspection
artefacts rather than dynamic tests.

**Regression testing strategy (Annex J <6>c).** Regression is **gate-enforced and total at Tier A**:
the **full** Tier A suite + all blocking quality gates re-run on **every** MR (RD-1 §5.4; SPAP RD-12
§6.8), so any regression in a pure core or plumbing is caught before merge. Tier B/C are re-run
**before each milestone/release and after any algorithm change or `eopf` bump** (REQ-M-03); a
fixed-input determinism comparison (REQ-F-DEP-02) detects numerical regressions in the real-data
path. Reused-component upgrades are gated through the same suite plus the `trivy` SCA gate (SPAP
RD-12 §6.7).

## <11> Software validation testing facilities

**Test environment (Annex J <7>a).** Two environments, both representative and used for **both** the
RB- and TS-validation campaigns (so Annex J <7>c — "different environments" — does **not** apply):

- **EOPF SDE container** (`registry.eopf.copernicus.eu/sde/cpm-build-environment`, `eopf == 2.8.1`,
  Python 3.11) — the operational runtime; the reference for Tier B/C and for performance budgets.
- **Local workstation** — identical software stack (relocatable without code change, REQ-PORT-01)
  for numerical verification on private data.
- **Public CI shell runner** — runs Tier A only (no container/Dask/S3); the local-FS path is
  validated here (REQ-PORT-03).

**Configuration (Annex J <7>b).** Software: the toolchain of <5.7> + the QA-metrics module +
synthetic and real profiles. Hardware: x86-64 multi-core CPU host, no GPU (REQ-R-01); S3-compatible
object store or POSIX filesystem (REQ-R-02). Test equipment / communications networks / bus
analysers: **not applicable** (no hardware interfaces, no on-board element). Testing data: synthetic
fixtures (public) and private real `L0c`/ADFs/reference products (local). Support software
(simulators): **none required** — there is no real-time or HW element to simulate; the "simulator"
role is filled by the synthetic-fixture generators.

## <12> Control procedures for software validation process

As <6> (shared with verification): **problem reporting and resolution** via GitLab issues +
gated-MR fixes; **deviation and waiver policy** via recorded issue waivers; **configuration control
and management** via Git/MR-only changes under ECSS-M-ST-40C (SPAP RD-12 §6.5). Validation results
are forwarded via the milestone review record and the SVR (RD-8); SPRs/NCRs are tracked to closure
at QR/AR (SRevP RD-11 §6).

## <13> Complement of validation at system level

Requirements that **cannot be validated in the validation environment** and need the full real
ground segment (Annex J <9>) — to be confirmed with the hosting EOPF ground segment, with the
project owner providing integration support (SYS-VV-08):

| Aspect needing system-level validation | Why not in the validation environment |
|---|---|
| Real orchestration trigger (E4) end-to-end | The CPM triggering payload is exercised locally (REQ-I-05); full operational triggering/scheduling belongs to the host orchestration |
| Product store / archive / dissemination (E5) at scale | Local validation uses a POSIX/S3 target; real dissemination, cataloguing (STAC) and large-scale object storage are ground-segment functions |
| Dask-gateway horizontal scaling | The shell runner has no gateway; multi-node scaling (REQ-F-ORC-02) is validated locally on a single node, full scaling at system level |
| Operational throughput at mission volume (REQ-P-04) | Single-scene `THRU_SCENE` is validated locally; sustained operational throughput is a ground-segment property |

These items are listed for the SVS w.r.t. TS/RB (Annex J <9>) and require customer/host support; they
do **not** affect the Category-C V&V conclusion for the software item itself.

---

## <14> Requirement → method → tier → means map

The authoritative, tool-maintained trace (including downward links to test cases) is RD-10 at CDR;
the SRS <6> validation matrix gives the detailed means. The table below adds the **tier** and the
**verification means/artefact** to every SRS `REQ-*` group. Method codes T/A/I/R; Tier A/B/C per
<4>; "—" = no dynamic tier (static/review evidence). Where a requirement has both a functional
Tier-A check and a numerical Tier-C budget, both tiers are listed.

| Requirement(s) | Method | Tier | Verification means / artefact |
|---|---|---|---|
| REQ-F-L0-01, -04 | T, I | A | Decode synthetic `L0c`; assert `L1A` arrays + EOProduct structure; (real sample, Tier B) |
| REQ-F-L0-02 | T | A | Inject line/packet loss fixture → truncation + QA flag |
| REQ-F-L0-03 | T | A | Malformed/mismatched input → reject/flag; profile/ADF resolution test |
| REQ-F-L0-05 | A, I | — | Static analysis: no write path to `L0` (read-only) |
| REQ-F-RAD-01, -02 | T, A | A + C | Closed-form on synthetic fixture; vs DPM/reference on real data |
| REQ-F-RAD-03, -04 | T | A | Bad-pixel/saturation fixtures → replacement + QA flags |
| REQ-F-RAD-05 (opt) | T, A | B | Derive gain/offset from real dark+flat; compare to reference (local) |
| REQ-F-TOA-01, -02 | T, A | A + C | DN→radiance/reflectance closed-form on fixtures; vs reference (local) |
| REQ-F-TOA-03 | T, I | A | `L1B` EOProduct emitted with QA + provenance |
| REQ-F-ENH-01, -02 | T, A | A + C | Filter/kernel unit tests (MTFC/PSF deconvolution + denoise); radiometric-impact analysis on real data |
| REQ-F-ENH-03 | T, R | A | Confirm enhancement stage always runs (MTFC mandatory, always applied); verify denoise toggle behaves per sensor profile |
| REQ-F-COR-01, -03 | T, A | A | Co-register synthetic-shifted bands (known homography); failure-path test |
| REQ-F-COR-02 | A, T | C | Inter-band tie-point RMSE vs `BAND_COREG` (local) |
| REQ-F-GEO-01, -02 | T, A | A + B | Geolocation/ortho on synthetic grid; on real scene with DEM/GCP (local) |
| REQ-F-GEO-03 | A, T | C | GCP residual `GEO_CE90` vs budget (local) |
| REQ-F-GEO-04 | T, I | A | `L1C` EOProduct with CRS + geolocation layers |
| REQ-F-PAN-01 (opt) | T, A | A + B | Pan-sharpen MS+PAN fixtures; on real data (local) |
| REQ-F-PAN-02 (opt) | A, T | C | Spectral-fidelity metric vs budget (local) |
| REQ-F-ATM-01, -02 | T, A | A + C | AOT/WV ingest+retrieve; TOA→BOA vs DPM/reference (local) |
| REQ-F-ATM-03, -04 | T | A | Scene-class + cloud/shadow mask; `L2A` EOProduct |
| REQ-F-QA-01 | T | A + C | SNR/RMSE/PSNR/MSE/variance on fixtures (Tier A); vs reference (Tier C) — ex-`metrics_ips` module |
| REQ-F-QA-02 | T | A | Flag propagation across stages to output |
| REQ-F-PRD-01 | T, I | A (POSIX) + B (S3) | Zarr round-trip via `EOZarrStore` on POSIX (CI); S3 (Tier B) |
| REQ-F-PRD-02 | I, T | A | Inspect provenance fields (input/ADF/profile/version ids) |
| REQ-F-ORC-01 | T, R | A | Sub-chain/full-chain at breakpoints; review CPM computing-model JSON |
| REQ-F-ORC-02 | T, A | B | Chunked larger-than-memory + Dask run; memory-footprint analysis (local) |
| REQ-F-DEP-01 | T | A | Forced stage failure → non-zero exit, no published product |
| REQ-F-DEP-02 | T, A | A + B | Re-run identical inputs → bit-identical / within-tolerance compare |
| REQ-P-01..03 | A, T | C | Accuracy budgets (`RAD_ACC`/`GEO_CE90`/`BAND_COREG`/`BOA_ACC`) vs reference (local) |
| REQ-P-04, -05 | A, T | C | `THRU_SCENE` + `MEM_BUDGET` benchmark on reference config (local) |
| REQ-I-01 | R, I | — | Review compliance to IRD/ICD/PSFD |
| REQ-I-02, -05 | T, I | A + B | Invoke via CLI/API and triggering payload |
| REQ-I-03, -04, -06 | T | A (POSIX/local URI) + B (S3/remote) | Read-only input test; Zarr write POSIX(CI)/S3; URI local+remote |
| REQ-I-07 | I | — | Inspect naming vs EOPF data model |
| REQ-O-01, -02, -03 | T | A + B | Batch/sub-chain run; logs+report+status+diagnostics asserted |
| REQ-O-04 | R, T | A | Review state/mode model; exercise error/aborted transition |
| REQ-R-01, -02 | T | B | Run on CPU-only x86-64 Linux against POSIX/S3 |
| REQ-R-03 | I, T | A + B | Inspect `eopf == 2.8.1` pin + stack; clean-install run |
| REQ-R-04 | A, T | C | Sizing analysis + chunked benchmark |
| REQ-R-05 | R | — | Review: no real-time/validity-deadline constraint (N/A closure) |
| REQ-D-01, -08 | R | — | Architecture / not-applicable review |
| REQ-D-02, -06, -09 | I | — | Toolchain gate logs; SRF/licence inspection; data-standard inspection |
| REQ-D-03 | T | A | Unit-test pure core without CPM runtime |
| REQ-D-04 | I, A | — | `xenon` thresholds; grep/review for no hard-coded constants |
| REQ-D-05 | A, T | A | Numerical-tolerance analysis + determinism test |
| REQ-D-07 | T, R | A + B | Run a second (synthetic) profile; review externalisation |
| REQ-S-01, -05 | I, A | — | Repo/CI scan: no private data/threshold/coefficient committed; output carries only provenance ids |
| REQ-S-02 | I, T | A | Secret-leak scan; env-var injection test |
| REQ-S-03 | A, I | — | Access-mode inspection (read inputs, write output store only) |
| REQ-S-04 | T | A | Mismatched ADF/profile validity → reject/flag |
| REQ-PORT-01, -02 | T, I | B | SDE↔local relocation; local+remote URI run |
| REQ-PORT-03 | T | A | Trigger + verify on CI shell runner (local-FS path) |
| REQ-Q-01 | I | — | Quality-gate CI logs |
| REQ-Q-02 | T | A | Coverage CI job vs gate (≥ 70 % new code) |
| REQ-Q-03 | A, T | C | Accuracy budgets (local) → SVR |
| REQ-Q-04 | I, A | — | `xenon` + reuse review |
| REQ-REL-01 | T, A | A + B | Determinism/reproducibility (see REQ-F-DEP-02) |
| REQ-REL-02 | T | A + B | Resume-from-level; no partial-as-complete |
| REQ-REL-03 | R | — | Review: no availability target (N/A closure) |
| REQ-M-01, -03 | R | — | Review workflow + eopf-bump/V&V procedure |
| REQ-M-02 | T, R | B | Swap ADF without code change → product updates (local) |
| REQ-M-04 | I | — | Module-structure inspection |
| REQ-SAF-01 | R | — | Hazard review (QA flags + provenance + fail-stop) |
| REQ-DEL-01 | T, I | A | Tagged CI build → wheel + versioned docs |
| REQ-DEL-02 | I | — | Artefact scan: no private data; tag/registry integrity |
| REQ-DEL-03 | I | — | Zarr product spec present in delivery |
| REQ-DAT-01 | I, T | A | Product structure vs ICD/PSFD |
| REQ-DAT-02 | I, R | — | ADF store external + id/version/validity/schema review |
| REQ-DAT-03 | T | A | Invalid/incomplete profile → rejected with diagnostic |
| REQ-HF-01 | I | — | Confirm no GUI dependency |
| REQ-HF-02 | T, I | A | Report human+machine readable; no private-data dependency |
| REQ-AD-01 | R, T | A | Externalisation review + second-profile run |
| REQ-AD-02 | I, T | A | Profile id/version; per-run selection via payload |
| REQ-AD-03, -04 | T, I | A + B | DEM/atmos by reference; change a setting without code change |
| REQ-AD-05 | T, I | B | Clean `pip install` (SDE + local) + acceptance run |

**Coverage statement.** Every `REQ-*` of the SRS (RD-4) carries at least one verification method and
is placed in the scheme; functional requirements are primarily Tier A (CI-blocking) with a Tier-C
numerical-validation component where an accuracy/performance budget applies; integration and
real-runtime requirements are Tier B (local, non-blocking in public CI); design/policy/closure
requirements are verified by I/A/R. A requirement excluded from validation against the baseline,
with rationale, is recorded in RD-10 (at this issue only the not-applicable closures REQ-D-08,
REQ-R-05, REQ-REL-03 — verified by review).

**Forwarding to the SVR.** The outcome of executing this plan — Tier A coverage/pass evidence, Tier
B integration results, Tier C budget verdicts (pass/fail only; private numbers withheld), and the
quality-gate verdicts — is consolidated in the Software Verification Report (RD-8) at QR and assessed
at AR against the Requirements Baseline.

---

*End of V&V Plan. Authored per ECSS-E-ST-40C Rev.1 Annex I (SVerP) and Annex J (SValP), tailored for
Category C, single-developer. The SUITP (Annex K — detailed unit/integration test specifications and
procedures) is produced at CDR and appended to this file as Part K (RD-9). Verification results are
reported in the SVR (RD-8); the maintained traceability matrix is RD-10.*
