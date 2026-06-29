# Qualification Review (QR) Report

| Field | Value |
|---|---|
| **Document** | Qualification Review (QR) Report — milestone review record (incl. anticipated TRR/TRB) |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex P/Q (review plan & content) + ECSS-M-ST-10-01C (organization and conduct of reviews); QR objectives & success criteria per SReVP (RD-2) <6>/<7>; ECSS-Q-ST-80C Rev.2 |
| **Container** | Management File (MGT) — `compliance/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | QR |
| **Status** | Issued at QR |

> This is the **milestone review record of the Software Qualification Review (QR)** of the
> `msi-processor` software configuration item. It records the QR objectives, the QR **data package**
> reviewed, the consolidated **verification & validation evidence**, the **SPR/NCR** and **RID** status,
> the assessment of the **QR success (exit) criteria** defined in the Software Review Plan (SReVP, RD-2)
> <6>/<7>, the **action items** carried to the Acceptance Review (AR), and the **review conclusion**. It
> is the QR counterpart of the SRR/PDR/CDR milestone records and is produced per SReVP <7>.4 ("review
> report" = milestone review record). The QR folds in the **anticipated Test Readiness Review / Test
> Review Board (TRR/TRB)** objectives (SReVP <4.1>/<6>). The configuration under review is the `main`
> baseline at commit **d140599** (latest `main` pipeline **30730** = success). The footprint is tailored
> to a **Category C, single-developer** ground-segment processor whose **code is public but whose raw
> `L0` data and instrument calibration are private** (RD-4 SRS <5.1>/<5.8>) — the policy that scopes what
> QR can prove publicly versus what is deferred to AR on operator data.

**DRD clause coverage.** Where this QR Report satisfies each review-report / Annex P–Q content item:

| Review-report content (SReVP RD-2 <6>/<7>; Annex P/Q) | This document |
|---|---|
| Review identification, objectives, level of formalism (SReVP <6> QR; anticipated TRR/TRB) | <1>, <4> |
| Applicable / reference documents | <2> |
| Terms, definitions, abbreviations | <3> |
| Data package subject to review (SReVP <10>, QR row) | <5> |
| Review minutes / consolidated verification evidence (SReVP <7>.4) | <6> |
| SPR/NCR status (SReVP <6> QR; <7>.2b/c) | <7> |
| RID status metric + dispositioned RIDs (SReVP <13>; <7>.4) | <8> |
| Review success (exit) criteria assessment + conclusion (SReVP <7>.2/<7>.3) | <9>, <11> |
| Actions raised / carried forward (SReVP <7>.4; <9>) | <10> |

---

## <1> Introduction

**Purpose.** This QR Report assesses whether `msi-processor` has been **implemented, integrated and
qualified against its technical specification** (the SRS, RD-4) such that the project may be authorised
to proceed to the Acceptance Review (AR). It records the objective evidence supporting that decision and
the actions that remain open.

**Software under review.** `msi-processor` is a generic, sensor-agnostic high-resolution **pushbroom MSI
ground processor** that transforms downlinked private RAW (`L0`) into calibrated, orthorectified and
atmospherically corrected products up to **`L2A`**, built on the ESA EOPF CPM (`EOProcessingUnit` /
`EOProduct` / `EOZarrStore`, Zarr persistence; `eopf == 2.8.1`, Python 3.11). It is an **integration and
ECSS-productisation** effort over existing algorithm heritage (RD-1 §1; SRF RD-19), not new-algorithm
research.

**Life-cycle position.** SRR, PDR and CDR are closed and baselined to `main`; implementation was
authorised at CDR exit (RD-1 §5.1). This QR is the qualification gate: the eight processing units are
implemented and CI-green on `main`, and the QR data package (<5>) consolidates the verification and
validation evidence produced by executing the V&V Plan (RD-8) and the SUITP (RD-10).

**Content.** Clause <2> lists the applicable/reference documents; <3> adds QR-specific terms; <4> records
the QR objectives (quoting SReVP <6>) and the anticipated TRR/TRB; <5> inventories the QR data package by
compliance path; <6> consolidates the verification & validation summary; <7> records SPR/NCR status; <8>
records RID disposition; <9> assesses the four SReVP QR exit criteria; <10> lists the action items carried
to AR; <11> states the conclusion.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software (Annex P/Q reviews; Annex I/J V&V; Annex K SUITP; Annex M SVR) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software (§6.2.6.1 quality verification; §6.3.5 testing/validation) | ECSS-Q-ST-80C Rev.2 |
| AD-3 | ECSS Space project management — Organization and conduct of reviews | ECSS-M-ST-10-01C |
| AD-4 | ECSS Configuration and information management | ECSS-M-ST-40C |
| AD-5 | EOPF CPM — Product Structure & Format Definition (PSFD) / data model | EOPF CPM docs (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software Review Plan (SReVP) — QR objectives, success criteria, RID form | `compliance/drd/srevp-software-review-plan.md` |
| RD-3 | `msi-processor` Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Control Document (ICD) | `compliance/drd/icd-interface-control.md` |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — `DPM-M-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V Plan (SVerP + SValP; three-tier scheme) | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Software Design Document (SDD) — `C-*`, `IF-*` | `compliance/drd/sdd-software-design.md` |
| RD-10 | `msi-processor` SUITP (Annex K — unit/integration test specs & procedures) | `compliance/drd/suitp-unit-integration-test-plan.md` |
| RD-11 | `msi-processor` Traceability matrix (RTM) — REQ↔design↔test, bidirectional | `compliance/traceability/traceability-matrix.md` |
| RD-12 | `msi-processor` Software Verification Report (SVR, Annex M) — **QR deliverable** | `compliance/drd/vv-report.md` |
| RD-13 | `msi-processor` Software Unit & Integration Test Report (SUITR) — **QR deliverable** | `compliance/drd/suitr-unit-integration-test-report.md` |
| RD-14 | `msi-processor` Software Release Note / Document (SRN/SRelD) — **QR deliverable** | `compliance/drd/srn-software-release-note.md` |
| RD-15 | `msi-processor` Configuration Item Data List (CIDL) — **QR deliverable** | `compliance/drd/cidl-configuration-item-data-list.md` |
| RD-16 | `msi-processor` Software Configuration File (SCF) — **QR deliverable** | `compliance/drd/scf-software-configuration-file.md` |
| RD-17 | `msi-processor` Software User Manual (SUM, start) — **QR deliverable** | `docs/sum/` |
| RD-18 | `msi-processor` Risk Register | `compliance/drd/risk-register.md` |
| RD-19 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-20 | `msi-processor` Design Justification File (DJF) | `compliance/drd/djf-design-justification.md` |
| RD-21 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-22 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-23 | CI pipeline definition + verification evidence | `.gitlab-ci.yml`; `main` pipeline **30730** (commit **d140599**) |

---

## <3> Terms, definitions and abbreviated terms

The SDP §3, SRS <3>, SDD <3>, V&V Plan (RD-8) <3>, SUITP (RD-10) <3> and SReVP (RD-2) <3> glossaries apply
in full. Only terms specific to this QR record and not defined there are added.

| Term / abbr. | Definition |
|---|---|
| QR | Software Qualification Review — qualification of the software against the technical specification (SRS, RD-4) |
| TRR / TRB | Test Readiness Review / Test Review Board — E-ST-40C sub-reviews **anticipated within the QR** (SReVP <4.1>/<6>) |
| AR | Software Acceptance Review — validation against the Requirements Baseline; the next milestone |
| RB / TS | Requirements Baseline (SSS RD-21 + IRD RD-22) / Technical Specification (SRS RD-4) |
| SPR / NCR | Software Problem Report / Non-Conformance Report (SPAP RD-3 §6.5; SReVP <13>) |
| RID | Review Item Discrepancy — a finding raised against a review item (SReVP <13>) |
| SCI | Software Configuration Item — the `main` baseline of the repository |
| Tier A / B / C | The V&V-Plan three-tier scheme (RD-8 <4>): A = deterministic synthetic unit/plumbing tests in public CI (blocking); B = local real-RAW integration (non-blocking/skipped in public CI); C = reference/validation-data **numeric budget** metrics (local; reported in the SVR) |
| `[impl]` item | A documented, fail-stop **deferred algorithm body** that the operational baseline never executes; recorded as a waiver and traced in the RTM (RD-11) |
| Budget parameter | A per-profile numeric tolerance (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`, `MEM_BUDGET`) held privately (RD-4 SRS <5.1>) |
| Blocking gate | A CI job whose failure fails the pipeline (verification gate); contrast `allow_failure` (non-gating) |

---

## <4> QR objectives

The QR objectives are those defined for the QR in the SReVP (RD-2 <6>), reproduced here verbatim. The QR
is conducted as a **documented, checklist-based, asynchronous milestone review on the GitLab platform**
(SReVP <6>/<8>), with the CI verification evidence as the primary input, and **folds in the anticipated
Test Readiness Review / Test Review Board (TRR/TRB)** objectives.

**QR objectives (SReVP <6>, "QR objectives — includes anticipated TRR/TRB"):**

- Verify that the software **meets all of its specified requirements** and that verification and
  validation processes (per the V&V plan) **have completed successfully**.
- Verify that **all Requirements-Baseline and interface requirements have been validated and verified**,
  including **technical budgets** and **code coverage** (EOPF coverage gate).
- Verify that the **Software Configuration Item** under review is a **formal version under configuration
  control** (Git tag / SCF / CIDL); **release the software release document** (SRelD/SRN).
- **Confirm the test/RB-validation configuration**; **check the status of all SPRs/NCRs**; **baseline the
  validation specification against the RB**; **evaluate readiness to proceed to AR**.

**Anticipated TRR/TRB (folded into QR).** Per SReVP <4.1>/<6>, the QR also discharges the TRR/TRB intent:
confirm that the test configuration is frozen and identified (baseline commit **d140599**, pipeline
**30730**); confirm test readiness and that the executed test campaign (Tier A in CI, Tier B/C locally) is
complete and reviewed; and disposition the test results and any anomalies before authorising transition.
The assessment against these objectives is in <6> (evidence), <7> (SPR/NCR), <8> (RIDs) and <9> (exit
criteria).

---

## <5> QR data package inventory

Per SReVP <10> (QR row), the QR data package comprises the five DRD deliverables **SVR, SUITR, SRelD/SRN,
CIDL, SCF**, plus the **SUM (start)** and the **CI verification evidence**. Each is referenced below by its
compliance path; deliverables authored within this QR package or still being completed are flagged with
the corresponding action item of <10>.

| # | Deliverable | DRD / Annex | Path (compliance / repo) | Status at QR |
|---|---|---|---|---|
| 1 | **SVR** — Software Verification Report (V&V results record) | E-ST-40C Annex M; from RD-8 / RD-10 execution | `compliance/drd/vv-report.md` (RD-12) | Issued at QR — consolidates Tier A/B/C verdicts; Tier-C numeric budgets carried (AI-QR-01) |
| 2 | **SUITR** — Software Unit & Integration Test Report | E-ST-40C Annex K results; companion to SUITP (RD-10) | `compliance/drd/suitr-unit-integration-test-report.md` (RD-13) | Issued at QR with action — completion published per AI-QR-03 |
| 3 | **SRelD / SRN** — Software Release Note/Document | E-ST-40C (release); SReVP <6> QR | `compliance/drd/srn-software-release-note.md` (RD-14) | Authored in this package — states RC **v0.1.0-rc1** referenced to baseline commit **d140599**; formal Git tag is the release action (AI-QR-04) |
| 4 | **CIDL** — Configuration Item Data List | E-ST-40C / M-ST-40C config control | `compliance/drd/cidl-configuration-item-data-list.md` (RD-15) | Authored in this package — lists the SCI constituents under Git config control |
| 5 | **SCF** — Software Configuration File | E-ST-40C / M-ST-40C config control | `compliance/drd/scf-software-configuration-file.md` (RD-16) | Authored in this package — records the as-built configuration at d140599 |
| 6 | **SUM (start)** — Software User Manual | E-ST-40C Annex S (start at QR, final at AR) | `docs/sum/` (RD-17) | Start — tree exists (introduction, operations, reference, tutorials, notebooks); finalised at AR (AI-QR-03) |
| 7 | **CI verification evidence** | E-ST-40C Annex I <7.3>; SPAP RD-3 §7 | `.gitlab-ci.yml`; `main` pipeline **30730** @ **d140599** (RD-23) | Green — 9 blocking verification gates pass; artefacts (JUnit, Cobertura coverage, lint/SAST/SCA logs) |

Supporting baselined inputs reviewed alongside the data package: the SRS (RD-4), SDD (RD-9), DPM (RD-6),
ATBD (RD-7), V&V Plan (RD-8), SUITP (RD-10) and the **traceability matrix / RTM** (RD-11), plus the RID
log from the prior milestone (SReVP <10>). No private raw data or calibration is part of any review data
package or public CI (SReVP <12>; RD-4 SRS <5.1>/<5.8>).

---

## <6> Verification & validation summary

This clause consolidates the verification evidence produced by executing the V&V Plan (RD-8) and the
SUITP (RD-10) on the QR baseline (commit **d140599**, `main` pipeline **30730** = success). Detail is in
the SVR (RD-12) and SUITR (RD-13); the authoritative trace is the RTM (RD-11).

### <6.1> Implementation completeness — 8 of 8 processing units

All eight processing units are implemented on `main` and CI-green, each as a **pure framework-independent
core** + a thin `EOProcessingUnit` wrapper + a per-unit computing-model JSON (RD-9; RD-4 REQ-D-03):

| Unit | Product level | Notes |
|---|---|---|
| `l0_decode` | `L1A` | open-container sample layout on the public path |
| `radiometric` | `L1A` | dark/NUC/BPR/saturation |
| `enhancement` | `L1B` | **MTF-compensation mandatory** (always runs); configurable denoise |
| `toa` | `L1B` | DN→radiance, optional reflectance |
| `coregistration` | `L1B → L1C` | feature-based inter-band alignment, fail-stop |
| `georeference` | `L1C` | GCP reference-image refinement on the operational path |
| `atmospheric` | `L2A` | new design; TOA→BOA, scene class + masks |
| `pansharpen` | optional post-`L2A` derivative | `simple_mean` operational |

The design realised is **21 design components (`C-*`)**, **11 DPM modules (`DPM-M-*`)** and **33 algorithms
(`ALG-*`)** (RD-9, RD-6, RD-7).

### <6.2> Test campaign — 248 test cases

The test suite was pytest-collected on the CPM environment (`eopf == 2.8.1`, Python 3.11). **238 test
functions** (some parametrised) are collected as **248 test cases**: **246 unit** (244 passed, **2
xfailed**) + **2 integration** (2 passed).

| Module (test functions) | Count |
|---|---|
| `l0_decode` | 22 |
| `radiometric` | 21 |
| `enhancement` | 35 |
| `toa` | 24 |
| `coregistration` | 23 |
| `georeference` | 27 |
| `atmospheric` | 35 |
| `pansharpen` | 29 |
| `common` (types + metrics) | 15 |
| `sensors` (profile) | 7 |
| **Total test functions** | **238** |

- **Unit (Tier A):** 246 cases — **244 passed, 2 xfailed**. The **2 xfailed** are in
  `tests/ut/computing/test_georeference_core.py` and **intentionally verify the `orthorectify` `[impl]`
  fail-stop** (they are expected failures, not defects).
- **Integration (Tier A CI-chain):** 2 cases in `tests/it/computing/test_full_chain.py` — the full
  `L0c → L2A` chain and the chain-with-pansharpen, wiring **all 8 units** on one synthetic feature-rich
  scene, both passing. This integration campaign **surfaced and fixed a real defect**: `AtmosphericUnit`
  was dropping the `L1C` geolocation grid from `L2A`; fixed by conditions passthrough (now part of the
  baseline at d140599). This is positive evidence that integration testing is materially exercising the
  chain, not merely smoke-testing it.

### <6.3> CI verification gates — 9 blocking gates green

On `main` pipeline **30730** the **nine blocking verification/quality gates** are all green (preceded by
the `validate-variables` precondition guard, which checks the mandatory pipeline variables):

| Gate (CI job) | Method | Verifies |
|---|---|---|
| `linter` (flake8) | I | style/lint (PEP 8) |
| `docker-linter` (hadolint) | I | Dockerfile lint |
| `formater` (black + isort) | I | format conformance |
| `typing` (mypy) | I | static type contracts |
| `unit-tests` (pytest `-m unit` + coverage Cobertura) | T | functional correctness + **code-coverage gate** (≥ 70 % new code, REQ-Q-02) |
| `security` (bandit) | I/T | SAST (Python security defects) |
| `deps-sec` (pip-audit, isolated venv) | I | dependency CVEs |
| `build-package` | T/I | wheel build |
| `sphinx-build` | I/T | docs build (autodoc wired in `docs/conf.py`) |

**5 `allow_failure` jobs** are justified and **not gating** (SReVP <8>; RD-8 <5.7>): `docs-cov`
(docstr-coverage, informational), `complexity` (xenon, advisory), `sonarqube` (external service),
`integration-tests` (now passing, but Dask-gateway/S3 absent on the shell runner → non-blocking until a
K8s runner; AI-QR-02), and `deliver-image` (kaniko has no container runtime on the shell runner). The
`deps-sec` gate carries a **documented ignore-list** — PYSEC-2026-248/249 and CVE-2026-48817/48818
(eopf-transitive `starlette 1.0.1`, unfixable while `eopf == 2.8.1` is pinned; revisit on an eopf bump,
AI-QR-04).

### <6.4> Requirements verification — 100 requirements, 91 verified at QR, 9 deferred to AR

The SRS (RD-4 <5>) defines **100 requirements** across sixteen categories (REQ-F functional, REQ-P
performance, REQ-I interface, REQ-O operational, REQ-R resource, REQ-D design, REQ-S security, REQ-PORT
portability, REQ-Q quality, REQ-REL reliability, REQ-M maintainability, REQ-SAF safety, REQ-DEL delivery,
REQ-DAT data, REQ-HF human-factors, REQ-AD adaptation). All carry a verification method (T/A/I/R) and are
traced in the RTM (RD-11) with **bidirectional closure and no orphans**.

- **91 of 100 requirements are verified at QR** (85 Verified + 6 Verified with a tested `[impl]`
  fail-stop; Tier A in CI + Tier B locally + I/A/R static and review evidence), per the V&V Plan
  requirement→method→tier map (RD-8 <14>) and the RTM (RD-11); **9 are deferred to AR** (Tier-C
  numeric-budget verdict).
- **The 9 deferred requirements are the 5 performance/accuracy budgets REQ-P-01..05** — `RAD_ACC`
  radiometric accuracy, `GEO_CE90` + `BAND_COREG` geolocation/co-registration, `BOA_ACC` surface
  reflectance, `THRU_SCENE` throughput, `MEM_BUDGET` peak memory — **plus the 4 budget-coupled
  requirements REQ-F-COR-02, REQ-F-GEO-03, REQ-F-PAN-02 and REQ-Q-03** (RTM G-2). All nine are verified
  **by analysis/design and the algorithm V&V** at QR. Their **Tier-C numeric budget validation is
  WITHHELD at QR**: it requires the operator's **private real RAW + calibration data** (data policy, SSS
  RD-21 <5.1>), which is never present in public CI. The numeric budget closure is a **documented QR open
  item carried to AR**, where it is validated on operator data (AI-QR-01). **This is the single most
  important stated limitation of this QR.**

---

## <7> SPR/NCR status

Per the QR objective "check the status of all SPRs/NCRs" (SReVP <6>; success criterion <7>.2):

- **No SPR/NCR is open** against the QR baseline. The blocking CI gates are green, the unit and
  integration campaigns pass (the 2 xfailed are expected fail-stop verifications, not defects), and the
  one defect surfaced during integration (the `L2A` geolocation-grid drop, <6.2>) was **fixed and closed**
  in the baseline (d140599).
- **The six `[impl]` deferral items are recorded waivers, not defects.** Each is **fail-stop** by design,
  is traced in the RTM (RD-11) as a recorded waiver (G-1/G-6), and **the operational baseline never
  executes them** (the public/operational path uses the documented alternatives):

  | # | `[impl]` item | Algorithm | Disposition / operational alternative |
  |---|---|---|---|
  | 1 | `l0_decode.decode_source_packets` | ALG-L0-DEC | sensor-private on-wire source-packet decode/decompression; public path consumes the documented open-container sample layout |
  | 2 | `georeference.orbit_state` | ALG-GEO-ORBIT | ephemeris/orbit propagation; CDR-target (GPL TLE path dropped) |
  | 3 | `georeference.orthorectify` | ALG-GEO-ORTHO | rigorous collinearity / DEM line-of-sight (needs sensor-private viewing model), CDR-target; operational `L1C` uses GCP reference-image refinement; **2 xfail tests verify the fail-stop** |
  | 4 | `atmospheric.retrieve_atmospheric_parameters` | ALG-ATM-PAR | image-based AOT/water-vapour retrieval |
  | 5 | `atmospheric.resolve_rt_lut` | ALG-ATM-RT | radiative-transfer engine LUT build |
  | 6 | `atmospheric.classify_scene_ml` | ALG-ATM-SCM | ML scene-classifier refinement |

  Additionally, the pansharpen **component-substitution fusion methods** (brovey/gs/ihs/atrous) are
  deferred; only `simple_mean` is operational. These deferrals are by design, recorded, and do not
  constitute open problem reports.

---

## <8> RID disposition

The QR review group conducted an **internal adversarial review** of the QR data package (<5>) against the
SReVP QR checklist (RD-2 <6>/<7>), with independence supplied by the automated CI gates and the explicit
review checklists (SReVP <11>). RIDs were recorded as GitLab issues / MR comments per the SReVP RID form
(RD-2 <13>, `RID-QR-<nnn>`).

- **All RIDs raised at the QR board were dispositioned** (Accepted / Partially accepted / Rejected) with
  rationale per SReVP <13>.
- RIDs accepted with rework required **before AR** were **converted into the action items of <10>** and
  assigned as GitLab issues against the QR/AR milestone; editorial and document-gap RIDs were dispositioned
  to the same action set (SUITR/SUM completion, formal tagging).
- The **RID status metric** (opened / dispositioned / closed) is recorded in the QR milestone summary
  issue and satisfies success criteria SReVP <7>.2(c)/(d). No RID remains undispositioned; therefore no
  RID blocks the QR conclusion.

---

## <9> Exit-criteria assessment

Assessment of the four QR success (exit) criteria of the SReVP (RD-2 <6> QR / <7>.2), with a per-criterion
verdict.

| # | QR exit criterion (SReVP) | Evidence | Verdict |
|---|---|---|---|
| **(a)** | Software meets all specified requirements; V&V per the V&V plan completed successfully | 8/8 units implemented and CI-green; 248 test cases (244 passed + 2 expected xfail + 2 integration passed); Tier A V&V complete (<6.1>–<6.3>); 91/100 requirements verified at QR, 9 deferred to AR (the 5 REQ-P budgets + REQ-F-COR-02, REQ-F-GEO-03, REQ-F-PAN-02, REQ-Q-03) verified by analysis with numeric closure deferred | **Pass with action** (AI-QR-01) |
| **(b)** | All RB + interface requirements verified, incl. technical budgets and code-coverage gate | RTM (RD-11) bidirectional, no orphans; interface requirements (REQ-I, IRD RD-22) verified; **code-coverage gate green** (unit-tests job, ≥ 70 % new code, REQ-Q-02); **technical budgets (REQ-P-01..05) numeric closure withheld at QR** (private operator data), verified by analysis/algorithm-V&V | **Pass with action** (AI-QR-01) |
| **(c)** | SCI is a formal version under configuration control (Git tag / SCF / CIDL); SRelD/SRN released | SCI baseline under Git config control at **d140599**; **SCF (RD-16), CIDL (RD-15) and SRN/SRelD (RD-14) authored in this package**; **no Git tag exists yet** — the **v0.1.0-rc1** RC is stated by the SRN referenced to d140599, and the formal tag is the release action at the release decision (AR) | **Pass with action** (AI-QR-04) |
| **(d)** | Confirm test/RB-validation configuration; check SPR/NCR status; baseline validation spec vs RB; evaluate readiness for AR | Test/validation configuration frozen and identified (d140599 / pipeline 30730); **no SPR/NCR open** (<7>); the validation specification (V&V Plan RD-8 + SUITP RD-10) is baselined against the RB (SSS RD-21 + IRD RD-22); readiness to proceed to AR confirmed with the carried actions | **Pass** |

**Overall exit-criteria verdict: PASS WITH ACTIONS.** The qualification objectives are met for the
software item itself; the only material reservations are the **Tier-C numeric budget validation** (private
operator data, deferred to AR) and the **formal release tagging** — both carried as explicit AR actions,
neither affecting the Category-C qualification conclusion for the software item.

---

## <10> Action items carried to AR

| Id | Action | Origin | Owner | Target |
|---|---|---|---|---|
| **AI-QR-01** | Execute **Tier-C numeric budget validation** of REQ-P-01..05 (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`, `MEM_BUDGET`) on the operator's **private RAW + calibration data**; record pass/fail verdicts (private numbers withheld) in the SVR (RD-12) | <6.4>, criteria (a)/(b) | Project owner | AR |
| **AI-QR-02** | **Promote `integration-tests` to a blocking gate** on a Kubernetes / Dask-gateway runner (currently `allow_failure` because the shell runner has no container runtime / Dask gateway / S3) | <6.3>; RD-18 risk | Project owner | AR / runner availability |
| **AI-QR-03** | **Publish SUITR completion** (RD-13) and **complete the SUM** (RD-17, start → final at AR) | <5>, RID disposition | Project owner | AR |
| **AI-QR-04** | Close the open documentation/release gaps: finalise and issue the QR deliverables and **apply the formal Git tag** (`v0.1.0-rc1` → release) at the release decision; carry the `deps-sec` ignore-list (PYSEC-2026-248/249, CVE-2026-48817/48818) for **revisit on the next `eopf` bump** | criterion (c); <6.3> | Project owner | AR / release decision |

The six `[impl]` deferral items (<7>) are recorded waivers traced in the RTM (RD-11 G-1/G-6), not action
items; the CDR-target bodies (`orbit_state`, `orthorectify`) remain monitored against their algorithm
plans but are not on the operational qualification path.

---

## <11> Conclusion

The Software Qualification Review of `msi-processor` is concluded **SUCCESSFUL WITH REWORK — QR PASSED WITH
ACTIONS** (SReVP <7>.3). The software is implemented (8/8 processing units), integrated and CI-green on the
`main` baseline at **commit d140599** (pipeline **30730** = success); the test campaign of **248 cases**
(244 passed + 2 expected fail-stop xfails + 2 integration passed) and the **nine blocking CI verification
gates** demonstrate qualification against the technical specification; **91 of 100 requirements are
verified at QR** and **9 are deferred to AR** — the **five REQ-P performance/accuracy budgets** plus the
four budget-coupled **REQ-F-COR-02, REQ-F-GEO-03, REQ-F-PAN-02 and REQ-Q-03** — verified by analysis with
their **Tier-C numeric closure carried to AR** on operator data. There are **no open SPRs/NCRs** (the six `[impl]` items
are recorded fail-stop waivers, never executed operationally), and all QR-board **RIDs are dispositioned**.
All four SReVP QR exit criteria are met (criteria (a), (b), (c) with the carried actions of <10>;
criterion (d) met), and the anticipated **TRR/TRB** objectives are discharged.

**Authorisation:** the project is authorised to **proceed to the Acceptance Review (AR)**, subject to the
four action items of <10> — principally the Tier-C numeric budget validation on operator data and the
formal release tagging of the release candidate **v0.1.0-rc1**.

---

*End of QR Report. Authored per ECSS-E-ST-40C Rev.1 Annex P/Q and ECSS-M-ST-10-01C, tailored for Category
C, single-developer. QR objectives and success criteria are those of the SReVP (RD-2) <6>/<7>; verification
results are in the SVR (RD-12) and SUITR (RD-13); the maintained traceability matrix is the RTM (RD-11).*
