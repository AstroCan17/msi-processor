# Software Verification Report (SVR)

| Field | Value |
|---|---|
| **Document** | SVR — Software Verification Report (the V&V results record) |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex M (SVR); reports the results of the V&V Plan — Annex I SVerP + Annex J SValP (RD-8) and the SUITP (Annex K, RD-10); ECSS-Q-ST-80C Rev.2 §6.2.6 |
| **Container** | Design Justification File (DJF) — `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | QR (Qualification Review) |
| **Status** | Issued at QR |

> This SVR is the **Annex M verification report** for `msi-processor`: it reports the **results** of
> executing the V&V Plan (RD-8, Annex I SVerP + Annex J SValP) and the SUITP (RD-10, Annex K) against
> the **QR configuration baseline** (`main` commit `d140599`, the latest successful `main` pipeline
> `30730`). It does **not** restate the V&V strategy, the three-tier scheme or the test specifications
> — those remain in RD-8 and RD-10 — but consolidates, per ECSS-E-ST-40C §5.8 and ECSS-Q-ST-80C
> §6.2.6: the static-analysis / quality-gate verdicts (`<5>`); the unit and integration test results
> (`<6>`); the **requirements verification matrix** covering all **100** SRS requirements (RD-4 `<5>`)
> with their method (T/A/I/R) and result (`<7>`); the **deferred Tier-C numeric budgets** carried to
> AR (`<8>`); the **`[impl]` fail-stop waiver register** (`<9>`); the traceability closure (`<10>`);
> the deviation/NCR status (`<11>`); and the qualification conclusion (`<12>`). The single most
> important QR limitation is stated plainly: the **five REQ-P-\* numeric accuracy/performance budgets**
> (and four budget-coupled accuracy requirements) cannot be closed at QR because they require the
> operator's **private real RAW + calibration data** (data policy SSS `<5.1>`), which is never in the
> public CI; their numeric pass/fail verdict is a documented **QR open item carried to AR**. The
> footprint is tailored to a **Category C, single-developer** ground-segment processor and mirrors the
> heading style of the V&V Plan (RD-8) and SUITP (RD-10).

**DRD clause coverage (Annex M).** Where this SVR satisfies each Annex M / ECSS-Q-ST-80 §6.2.6 clause:

| DRD clause | Topic | This document |
|---|---|---|
| SVR (M) `<1>`/`<2>`/`<3>` | Intro / AD-RD / terms | `<1>`, `<2>`, `<3>` |
| SVR (M) `<4>` | Verification scope, configuration verified, approach recap | `<4>` |
| SVR (M) `<5.1>` | Software-process and static-quality verification results | `<5>` |
| SVR (M) `<5.2>` | Unit and integration test verification results (Tier A/B) | `<6>` |
| SVR (M) `<5.3>` | Requirement-level verification results (verification matrix) | `<7>` |
| SVR (M) `<5.4>` | Quality-requirements verification results | `<5.6>` (within `<5>`) |
| SVR (M) `<6>` | Deferred verifications (Tier-C budgets) and `[impl]` waivers | `<8>`, `<9>` |
| SVR (M) `<7>` | Traceability of verification results to requirements | `<10>` |
| SVR (M) `<8>` | Deviations / nonconformances / open items | `<11>` |
| SVR (M) `<9>` | Conclusion and recommendation | `<12>` |
| ECSS-Q-ST-80 §6.2.6 | Verification of the software (process + product + quality) | `<5>`, `<6>`, `<7>`, `<12>` |

---

## <1> Introduction

**Purpose.** This SVR records, at QR, the outcome of the verification and validation activities
defined in the V&V Plan (RD-8) and detailed in the SUITP (RD-10), executed against the `msi-processor`
QR configuration baseline. It demonstrates, per the SReVP QR exit criteria (RD-13 `<6>`/`<7>`), that the
software meets its specified requirements (SRS, RD-4) and that V&V per the V&V Plan has been completed,
except for the explicitly deferred Tier-C numeric budgets recorded as open items.

**Objective.** To present, for the QR Software Configuration Item (SCI): (a) the verification approach
recap and the configuration actually verified (`<4>`); (b) the results of the static-analysis and
quality-requirements gates (`<5>`); (c) the unit and integration test results, including coverage
(`<6>`); (d) the **requirements verification matrix** binding every SRS `REQ-*` to its method and a
verdict — **Verified**, **Verified (fail-stop)** or **Deferred** (`<7>`); (e) the status of the
deferred Tier-C numeric budgets (`<8>`) and of the `[impl]` fail-stop waivers (`<9>`); (f) the
traceability closure (`<10>`); (g) the deviation / nonconformance status (`<11>`); and (h) the
qualification conclusion (`<12>`).

**Content.** Clause `<2>` lists applicable/reference documents; `<3>` adds SVR-specific terms; `<4>`
recaps the verified configuration and the three-tier scheme; `<5>` reports the CI gate and
quality-requirements verdicts; `<6>` the test results; `<7>` the requirement-level verification
matrix; `<8>` the deferred budgets; `<9>` the `[impl]` waiver register; `<10>` the traceability
closure; `<11>` deviations/open items; `<12>` the conclusion.

**Configuration verified (the QR baseline).**

| Item | Value |
|---|---|
| Repository | `gitlab.eopf.copernicus.eu/ipf/msi-processor` |
| Baseline commit (`main`) | `d140599` (QR configuration baseline) |
| Reference pipeline | `main` pipeline `30730` — **success** |
| Release candidate | `v0.1.0-rc1` referenced to commit `d140599` (dynamic version: flit + git tag; **no git tag created yet** — tagging is the release action at the AR / release decision; see SRN, RD-18) |
| Runtime | `eopf == 2.8.1`, Python 3.11 (EOPF SDE / CPM) |
| Processing units verified | 8 of 8 implemented and CI-green (`l0_decode`, `radiometric`, `enhancement`, `toa`, `coregistration`, `georeference`, `atmospheric`, `pansharpen`) |
| Runner | single EOPF SDE Studio VM, **SHELL executor** (`image:` directives ignored; no container runtime / Dask-gateway / S3) |

**Reason for preparation.** The SVR is the child of the V&V Plan (RD-8 `<14>` "Forwarding to the SVR")
and the SUITP (RD-10 `<5.2>`): both record that the accumulated Tier-A/B/C evidence and the
quality-gate verdicts are consolidated into the SVR at QR and assessed at AR against the Requirements
Baseline. This document is that consolidation. It is a constituent of the QR data package (SVR +
SUITR + SRelD/SRN + SUM(start) + CIDL + SCF + CI verification evidence).

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software (Annex I SVerP, Annex J SValP, Annex K SUITP, **Annex M SVR**) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software (§6.2.6 verification; §6.3.5 testing/validation; §7 product quality) | ECSS-Q-ST-80C Rev.2 |
| AD-3 | ECSS System engineering — General requirements (verification process) | ECSS-E-ST-10C Rev.1 |
| AD-4 | EOPF CPM — Product Structure & Format Definition (PSFD) / data model | EOPF CPM docs (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Control Document (ICD) — `ICD-IF-*` | `compliance/drd/icd-interface-control.md` |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — `DPM-M-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V Plan (SVerP/SValP merged) — **this SVR reports its results** | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Software Design Document (SDD) — `C-*` | `compliance/drd/sdd-software-design.md` |
| RD-10 | `msi-processor` SUITP (Annex K — unit/integration test specs & procedures) | `compliance/drd/suitp-unit-integration-test-plan.md` |
| RD-11 | `msi-processor` Requirements Traceability Matrix (RTM) | `compliance/traceability/traceability-matrix.md` |
| RD-12 | `msi-processor` Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |
| RD-13 | `msi-processor` Software Review Plan (SReVP) | `compliance/drd/srevp-software-review-plan.md` |
| RD-14 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-15 | `msi-processor` Risk Register | `compliance/drd/risk-register.md` |
| RD-16 | `msi-processor` Configuration Item Data List (CIDL) | `docs/cidl.md` |
| RD-17 | `msi-processor` Software Configuration File (SCF) | `docs/scf.md` |
| RD-18 | `msi-processor` Software Release Note / Document (SRN / SRelD) | `docs/srn.md` |
| RD-19 | `msi-processor` Software User Manual (SUM, start) | `docs/sum/` |
| RD-20 | CI pipeline definition + tool configuration (verification evidence) | `.gitlab-ci.yml`, `pyproject.toml`, `.flake8`, `bandit.yml`, `.coveragerc` |

---

## <3> Terms, definitions and abbreviated terms

The SDP §3, SSS `<3>`, SRS `<3>`, SDD `<3>`, V&V Plan `<3>` and SUITP `<3>` glossaries apply in full.
Only terms specific to this SVR are added.

| Term / abbr. | Definition |
|---|---|
| SVR | Software Verification Report (ECSS-E-ST-40C Annex M) — the consolidated V&V results record |
| SCI | Software Configuration Item — the QR baseline (`d140599`) under configuration control |
| Tier A / B / C | The V&V-Plan three-tier scheme (RD-8 `<4>`): A = deterministic synthetic unit/plumbing tests in public CI (blocking); B = local real-RAW integration (non-blocking / skipped in public CI); C = reference/validation-data numeric budgets (local; reported here as verdicts only) |
| T / A / I / R | Verification methods: Test / Analysis / Inspection / Review of design |
| **Verified (V)** | The requirement's method(s) were executed and the verdict is pass at the QR baseline |
| **Verified — fail-stop (V-fs)** | The operational baseline path is verified; the deferred `[impl]` algorithm body is held behind a **tested fail-stop** safety net (recorded waiver, RTM G-1/G-6) that the operational baseline never executes |
| **Deferred (D)** | The Tier-C **numeric budget** verdict is withheld at QR (operator-private real RAW + calibration data absent from public CI, data policy SSS `<5.1>`) and carried to AR as a documented open item; the analysis/design and algorithm-V&V component of the requirement is complete |
| `[impl]` | Code internal legitimately finalised in implementation, specified at interface + algorithm level; six such bodies are fail-stop (`<9>`) |
| Budget parameter | A per-profile numeric tolerance held privately (`RAD_ACC`, `GEO_CE90`, `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`, `MEM_BUDGET`; RD-4 `<5.3>`) |
| xfail | A `pytest` expected-failure case; here used to *assert* the `[impl]` fail-stop is in force |
| SPR / NCR | Software Problem Report / Nonconformance Report (SPAP RD-12 §6.5; SReVP RD-13 §6) |

---

## <4> Verification scope, configuration verified and approach recap

### <4.1> Scope

This SVR covers the verification of the single software item `msi_processor` at the QR baseline
(`d140599`). The verification universe is the **100** software requirements of the SRS (RD-4 `<5>`),
plus the software-process verification of the life-cycle outputs and the software-quality-requirements
verification of ECSS-Q-ST-80C §6.2.6. The upstream `SYS-*` (66, RD-2), `REQ-IF-*` (31, RD-3),
design `C-*` (20 + 1 container, RD-9), `DPM-M-*` (11, RD-6) and `ALG-*` (33, RD-7) namespaces are
covered indirectly through the RTM closure (`<10>`, RD-11).

### <4.2> Approach recap — the three-tier scheme (RD-8 <4>)

Verification follows the V&V-Plan three-tier scheme, reconciling the public-code / private-data policy
(SSS `<5.1>`/`<5.8>`) and the shell-executor CI runner with what can be proven publicly,
automatically and deterministically:

| Tier | Verifies | Where executed at QR | Result reported in |
|---|---|---|---|
| **A — deterministic synthetic unit + plumbing tests** (blocking) + **static gates** | Functional correctness of the pure algorithmic cores and the EOProduct/Zarr-POSIX plumbing; code quality | Public CI (shell runner), pipeline `30730` | `<5>`, `<6>` |
| **B — local real-RAW integration** (non-blocking / skipped in public CI) | End-to-end PU chaining, real I/O, chunked execution, product structure on real data | Locally / EOPF SDE; synthetic-data equivalent runs in CI (blocking) | `<6>`, `<8>` |
| **C — reference / validation-data numeric budgets** (local only) | Numerical product-quality and performance **budgets** against the Requirements Baseline | **Not executed at QR** — private real RAW + calibration data absent | `<8>` (deferred) |

The verification method per requirement (T/A/I/R) and its primary tier are defined in RD-8 `<14>` and
consolidated in RD-11; this report records the **result** against that map. Because verification is
continuous and automated (RD-8 `<5.1>`), the standing verification record is the Git/CI history; this
SVR snapshots it at the QR baseline.

### <4.3> Independence

Per the Category-C, single-developer tailoring (RD-8 `<5.1>`, RD-12 §5.1), personnel independence is
replaced by **automated, version-controlled gates** that pass/fail independently of the developer's
opinion (CI), a third-party adjudicator (SonarQube) and explicit review checklists (RD-13 §11). The
QR verdicts below are the gate outcomes, not subjective assessments.

---

## <5> Static-analysis and quality-requirements verification results

### <5.1> Blocking CI gate results (pipeline 30730, baseline d140599)

All blocking jobs are **green** on the QR baseline. The gate set is the `validate-variables`
pipeline-variable guard plus **nine** verification gates:

| Gate (CI job) | Tool | Method | Verifies (REQ) | Result |
|---|---|---|---|---|
| `validate-variables` | CI variable guard | I | pipeline preconditions | **PASS** |
| `linter` | `flake8` | I | style/PEP-8 (REQ-D-02) | **PASS** — 0 findings |
| `docker-linter` | `hadolint` | I | Dockerfile lint | **PASS** — 0 findings |
| `formater` | `black` + `isort` | I | format conformance (REQ-D-02) | **PASS** — 0 diffs |
| `typing` | `mypy` | I | static type contracts | **PASS** — 0 errors |
| `unit-tests` | `pytest -m unit` + `coverage` (Cobertura) | T | functional cores + coverage gate (REQ-Q-02, REQ-D-03, all `REQ-F-*` Tier-A) | **PASS** — see `<6>` |
| `security` | `bandit` | I/T | SAST — Python security defects (REQ-S-02) | **PASS** — 0 findings |
| `deps-sec` | `pip-audit` (isolated venv) | I | dependency CVEs (REQ-D-06) | **PASS** — with documented ignore-list (`<5.3>`) |
| `build-package` | `flit` wheel build | T/I | deliverable wheel builds (REQ-DEL-01) | **PASS** |
| `sphinx-build` | Sphinx (autodoc) | I | documentation builds (REQ-DEL-01) | **PASS** |

### <5.2> Allow-failure (informational / advisory) job results

Five jobs are `allow_failure: true` — **not gating** at the QR baseline, with justification:

| Gate (CI job) | Tool | Status at QR | Justification (non-gating) |
|---|---|---|---|
| `docs-cov` | `docstr-coverage` | informational | docstring density is advisory (RD-8 `<5.7>`) |
| `complexity` | `xenon` | advisory | cyclomatic-complexity bound is advisory at Cat C (REQ-D-04/Q-04) |
| `sonarqube` | SonarQube | external | external service; quality verdict adjudicated when reachable |
| `integration-tests` | `pytest -m integration` | **now passing** | Dask-gateway / S3 absent on the shell runner → non-blocking until a Kubernetes runner (RD-15) |
| `deliver-image` | kaniko | n/a | no container runtime on the shell runner; image delivery deferred to a K8s runner |

### <5.3> Dependency-security ignore-list (justified, deps-sec)

The `deps-sec` (`pip-audit`) gate is green with a **documented ignore-list**: **PYSEC-2026-248**,
**PYSEC-2026-249**, **CVE-2026-48817**, **CVE-2026-48818**. All four are in the **eopf-transitive
`starlette 1.0.1`** dependency and are **unfixable while `eopf == 2.8.1` is pinned** (REQ-R-03,
REQ-IF-SW-03). They are not reachable from `msi-processor`'s own attack surface (no network server is
exposed by the processor). Disposition: **revisit on the next `eopf` bump** under the documented
eopf-bump re-V&V procedure (REQ-M-03); tracked in the Risk Register (RD-15).

### <5.4> Quality-requirements verification (ECSS-Q-ST-80 §6.2.6.1)

The product-quality model (SPAP RD-12 §5.5) is met at the QR baseline: test pass + line coverage gate
(≥ 70 % new code) by `unit-tests`; 0 lint/format/typing/SAST findings; 0 unignored HIGH/CRITICAL
dependency CVEs; documentation builds. The dedicated **no-private-data scan** (REQ-S-01/05) confirms
no private threshold or calibration coefficient is committed. These verdicts close the
quality-requirements verification (REQ-Q-01/02/04, REQ-D-02, REQ-S-02, `<7>` rows).

---

## <6> Unit and integration test verification results (Tier A / Tier B)

### <6.1> Test execution summary (pytest, cpm_env, eopf 2.8.1 / Python 3.11)

The authoritative pytest-collected outcome at the QR baseline:

| Class | Cases | Passed | xfailed | Failed | Result |
|---|---|---|---|---|---|
| Unit (`@pytest.mark.unit`, Tier A) | **246** | **244** | **2** | 0 | **PASS** |
| Integration (`it/computing`, Tier B-equivalent on synthetic data) | **2** | **2** | 0 | 0 | **PASS** |
| **Total** | **248** | **246** | **2** | **0** | **PASS** |

The 248 test cases are collected (with parametrisation) from **238 test functions**. The **2 xfailed**
cases are in `tests/ut/computing/test_georeference_core.py` and are **intentional**: they assert that
the `orthorectify` `[impl]` rigorous-collinearity path is **fail-stop** (they verify the safety net,
not a defect — see `<9>` item 3). There are **0 unexpected failures and 0 collection/import errors**;
the Tier-A exit criterion (100 % of `unit` cases pass + coverage gate met, RD-10 `<7.5>`) is satisfied.

### <6.2> Per-area unit-test distribution (test functions)

| Area (unit / module) | Level | Unit tests |
|---|---|---|
| `l0_decode` | L1A | 22 |
| `radiometric` | L1A | 21 |
| `enhancement` (MTFC mandatory) | L1B | 35 |
| `toa` | L1B | 24 |
| `coregistration` | L1B→L1C | 23 |
| `georeference` | L1C | 27 |
| `atmospheric` (new design) | L2A | 35 |
| `pansharpen` (optional post-L2A) | derivative | 29 |
| `common` (types + metrics) | — | 15 |
| `sensors` (profile) | — | 7 |
| **Total (test functions)** | | **238** |

(Parametrisation expands these 238 functions to the **246** collected unit cases of `<6.1>`.) Each
pure core is exercised against synthetic, seeded fixtures with closed-form / constructed oracles, with
**no CPM runtime, no I/O and no private data** (RD-10 `<7.1>`), so the suite is reproducible on the
public shell runner.

### <6.3> Integration test results (Tier B on synthetic data — blocking-equivalent)

`tests/it/computing/test_full_chain.py` provides **2 integration cases** (both **passed**): the full
**`L0c`→`L2A`** chain and the **chain-with-pansharpen** derivative, wiring **all 8 processing units**
on one synthetic, feature-rich scene through the EOPF CPM runtime on the POSIX path. The real-RAW
distributed/S3 Tier-B variants (`@pytest.mark.integration`) auto-skip on the shell runner (no
Dask-gateway / S3) and are non-blocking (`<5.2>`).

**Verification finding (closed).** The integration tests **surfaced and fixed a real defect**: the
`AtmosphericUnit` was dropping the `L1C` geolocation grid from the `L2A` product. It was raised,
fixed (by `conditions` passthrough) and re-verified — the chain now preserves geolocation end to end.
This SPR is **closed** at the QR baseline (`<11>`), and is the concrete demonstration of the V&V
campaign's effectiveness required by ECSS-Q-ST-80 §6.3.5.

---

## <7> Requirements verification matrix (all 100 SRS requirements)

This matrix consolidates the result of executing RD-8 `<14>` against the QR baseline. Method codes are
T/A/I/R; **Result** is **V** (Verified), **V-fs** (Verified — operational path; `[impl]` body
fail-stop, `<9>`) or **D** (Deferred — Tier-C numeric budget, `<8>`). Counts are the authoritative SRS
(RD-4 `<5>`) and RTM (RD-11) figures.

### <7.1> Summary by category

| Category | Count | Method(s) | Primary tier | V | V-fs | D | Category result |
|---|---|---|---|---|---|---|---|
| REQ-F (functional) | 37 | T, A, I, R | A (+B/+C where budgeted) | 28 | 6 | 3 | Verified; 3 budget-coupled deferred |
| REQ-P (performance) | 5 | A, T | C | 0 | 0 | 5 | **Deferred to AR** (numeric budgets) |
| REQ-I (interface) | 7 | T, I, R | A/B/— | 7 | 0 | 0 | Verified |
| REQ-O (operational) | 4 | T, R | A/B | 4 | 0 | 0 | Verified |
| REQ-R (resources) | 5 | T, A, I, R | A/B/C/— | 5 | 0 | 0 | Verified (REQ-R-05 N/A closure) |
| REQ-D (design) | 9 | R, I, A, T | A/— | 9 | 0 | 0 | Verified (REQ-D-08 N/A closure) |
| REQ-S (security) | 5 | I, A, T | A/— | 5 | 0 | 0 | Verified |
| REQ-PORT (portability) | 3 | T, I | A/B | 3 | 0 | 0 | Verified |
| REQ-Q (quality) | 4 | I, A, T | A/C/— | 3 | 0 | 1 | Verified; REQ-Q-03 numeric deferred |
| REQ-REL (reliability) | 3 | T, A, R | A/B/— | 3 | 0 | 0 | Verified (REQ-REL-03 N/A closure) |
| REQ-M (maintainability) | 4 | R, I, T | B/— | 4 | 0 | 0 | Verified |
| REQ-SAF (safety) | 1 | R | — | 1 | 0 | 0 | Verified (hazard review) |
| REQ-DEL (delivery) | 3 | T, I | A/— | 3 | 0 | 0 | Verified |
| REQ-DAT (data) | 3 | I, R, T | A/— | 3 | 0 | 0 | Verified |
| REQ-HF (human factors) | 2 | I, T | A/— | 2 | 0 | 0 | Verified |
| REQ-AD (adaptation) | 5 | R, T, I | A/B | 5 | 0 | 0 | Verified |
| **Total** | **100** | | | **85** | **6** | **9** | **91 verified, 9 deferred** |

**Tally.** Of the 100 SRS requirements: **85 Verified**, **6 Verified (fail-stop)** = **91 verified at
QR**; **9 Deferred** to AR (Tier-C numeric-budget verdict): the **5 REQ-P-01..05** performance budgets
plus the **4 budget-coupled** accuracy requirements **REQ-F-COR-02**, **REQ-F-GEO-03**,
**REQ-F-PAN-02** and **REQ-Q-03** (RTM G-2). No requirement is unverified for lack of evidence other
than the documented private-data deferral.

### <7.2> Functional detail (REQ-F, 37)

| REQ-F group | IDs | Method | Tier | Result | Note |
|---|---|---|---|---|---|
| L0 decode | REQ-F-L0-01 | T, I | A (+B) | **V-fs** | operational open-container path verified; on-wire codec `[impl]` fail-stop (`<9>` #1) |
| L0 loss/legality/assembly | REQ-F-L0-02/03/04 | T, A, I | A | V | line/packet-loss + flags; legality reject; `L1A` EOProduct |
| L0 read-only | REQ-F-L0-05 | A, I | — | V | static: no write path to `L0` |
| Radiometric | REQ-F-RAD-01..04 | T, A | A (+C) | V | dark/NUC/BPR/saturation closed-form + flags |
| NUC derivation (opt) | REQ-F-RAD-05 | T, A | B | V | local calib-mode |
| TOA radiance/reflectance/emit | REQ-F-TOA-01..03 | T, A, I | A (+C) | V | DN→radiance/reflectance closed-form; `L1B` EOProduct |
| Enhancement (MTFC mandatory) | REQ-F-ENH-01..03 | T, A, R | A (+C) | V | MTFC always runs; denoise profile-configurable (35 unit tests) |
| Co-registration (functional) | REQ-F-COR-01/03 | T, A | A | V | known-homography recovery; fail-stop on insufficient matches |
| Co-registration residual budget | REQ-F-COR-02 | A, T | C | **D** | `BAND_COREG` numeric budget — deferred (`<8>`) |
| Geolocation | REQ-F-GEO-01 | T, A | A (+B) | **V-fs** | GSD/geolocate verified; orbit-state `[impl]` fail-stop (`<9>` #2) |
| Ortho + GCP + resample | REQ-F-GEO-02 | T, A | A (+B) | **V-fs** | GCP refinement operational; rigorous ortho `[impl]` fail-stop (`<9>` #3; 2 xfail) |
| Geolocation accuracy budget | REQ-F-GEO-03 | A, T | C | **D** | `GEO_CE90` numeric budget — deferred (`<8>`) |
| `L1C` emission | REQ-F-GEO-04 | T, I | A | V | CRS + geolocation layers |
| Pan-sharpen fuse (opt) | REQ-F-PAN-01 | T, A | A (+B) | V | `simple_mean` operational; brovey/gs/ihs/atrous fusion deferred fail-stop (`<9>`) |
| Pan-sharpen fidelity budget (opt) | REQ-F-PAN-02 | A, T | C | **D** | spectral-fidelity numeric budget — deferred (`<8>`) |
| Atmospheric AOT/WV (new) | REQ-F-ATM-01 | T, A | A (+C) | **V-fs** | ADF-ingest path verified; image-based retrieval `[impl]` fail-stop (`<9>` #4) |
| TOA→BOA (new) | REQ-F-ATM-02 | T, A | A (+C) | **V-fs** | LUT-applied path verified; RT-engine LUT build `[impl]` fail-stop (`<9>` #5) |
| Scene class + mask (new) | REQ-F-ATM-03 | T | A | **V-fs** | deterministic classifier verified; ML refinement `[impl]` fail-stop (`<9>` #6) |
| `L2A` emission (new) | REQ-F-ATM-04 | T, I | A | V | `L2A` EOProduct (geolocation passthrough fix verified, `<6.3>`) |
| QA metrics + flags | REQ-F-QA-01/02 | T | A (+C) | V | SNR/RMSE/PSNR/MSE/variance closed-form; flag OR-monotone |
| Product + provenance | REQ-F-PRD-01/02 | T, I | A (+B) | V | Zarr round-trip; provenance ids |
| Orchestration | REQ-F-ORC-01/02 | T, A, R | A (+B) | V | PU DAG + breakpoints; chunk-equivalence (synchronous Dask) |
| Dependability | REQ-F-DEP-01/02 | T, A | A (+B) | V | fail-stop (no partial publish); determinism |

### <7.3> Non-functional detail (selected results)

| REQ | Method | Tier | Result | Verification evidence (artefact) |
|---|---|---|---|---|
| REQ-P-01..05 | A, T | C | **D** | analysis/design + algorithm-V&V done; numeric budgets (`RAD_ACC`/`GEO_CE90`/`BAND_COREG`/`BOA_ACC`/`THRU_SCENE`/`MEM_BUDGET`) deferred to AR (`<8>`) |
| REQ-I-01/03/04/06 | T, I, R | A/B/— | V | ICD/PSFD compliance; Zarr POSIX (CI) / S3 (local); URI I/O |
| REQ-I-02/05/07 | T, I | A/— | V | CLI + Python API + triggering payload; EOPF naming |
| REQ-O-01..04 | T, R | A/B | V | batch/sub-chain; logs+report+status; mode transitions |
| REQ-R-01/02/03 | T, I | A/B | V | CPU-only x86-64 Linux; POSIX/S3; `eopf==2.8.1` clean install |
| REQ-R-04 | A, T | A/C | V | sizing analysis + Tier-A chunk-equivalence (absolute `MEM_BUDGET` rides REQ-P-05) |
| REQ-R-05 | R | — | V | **N/A closure** — no hard real-time constraint (RTM G-3) |
| REQ-D-01..07/09 | R, I, A, T | A/— | V | architecture review; pure-core unit-testable; numerical-tolerance analysis; data-model inspection |
| REQ-D-08 | R | — | V | **N/A closure** — no in-flight modification (RTM G-3) |
| REQ-S-01..05 | I, A, T | A/— | V | no private data/threshold committed (scan); least-privilege; id/version verify; provenance-only output |
| REQ-PORT-01..03 | T, I | A/B | V | SDE↔local relocation; URI transparency; local-FS path on CI shell runner |
| REQ-Q-01/02/04 | I, A, T | A/— | V | quality gates green; coverage gate met; bounded complexity + reuse |
| REQ-Q-03 | A, T | C | **D** | numerical objectives — deferred to AR (`<8>`) |
| REQ-REL-01/02 | T, A | A/B | V | determinism/reproducibility; resume-from-level |
| REQ-REL-03 | R | — | V | **N/A closure** — no availability target (RTM G-3) |
| REQ-M-01..04 | R, I, T | B/— | V | issue→branch→MR + SemVer; ADF swap; eopf-bump procedure; modular structure |
| REQ-SAF-01 | R | — | V | hazard review — data-integrity triad (QA flags + provenance + fail-stop) |
| REQ-DEL-01..03 | T, I | A/— | V | tagged-CI wheel + docs (build verified; tag is the AR release action); no private data in artefacts; Zarr spec present |
| REQ-DAT-01..03 | I, R, T | A/— | V | product model vs ICD/PSFD; external ADF store; profile load-validation |
| REQ-HF-01/02 | I, T | A/— | V | no GUI dependency; human+machine-readable report |
| REQ-AD-01..05 | R, T, I | A/B | V | sensor-agnostic profile; per-run selection; externalised DEM/atmos; clean `pip install` + acceptance |

---

## <8> Deferred Tier-C numeric-budget verification status (carried to AR)

**This is the single most important QR limitation, stated plainly.** The Tier-C numeric accuracy and
performance budgets **cannot be closed at QR**: their validation requires the operator's **private
real RAW (`L0`) + instrument calibration / reference data**, which by the data policy (SSS `<5.1>`,
SRS `<5.1>`/`<5.8>`; REQ-S-01) is **never present in the public CI** and was not available at the QR
baseline. The affected requirements are **verified by analysis/design and by the algorithm V&V**
(method A), but their **numeric pass/fail verdict (method T, Tier C)** is **withheld** and recorded as
a **QR open item carried to the Acceptance Review (AR)**, where it is validated on operator data.

| Deferred requirement | Budget parameter | Metric / comparison (RD-8 `<4.1>`) | QR status | Closure |
|---|---|---|---|---|
| REQ-P-01 | `RAD_ACC` | `L1B` radiometric RMSE / relative error vs reference | A-verified; T-verdict withheld | AR (private data) |
| REQ-P-02 | `GEO_CE90`, `BAND_COREG` | GCP-residual CE90; inter-band tie-point RMSE | A-verified; T-verdict withheld | AR |
| REQ-P-03 | `BOA_ACC` | `L2A` surface-reflectance RMSE / relative error vs reference | A-verified; T-verdict withheld | AR |
| REQ-P-04 | `THRU_SCENE` | wall-time per reference scene | A-verified; T-verdict withheld | AR |
| REQ-P-05 | `MEM_BUDGET` | peak per-worker RSS bounded by chunk/tile size | A-verified (chunk-equivalence, Tier-A); absolute figure withheld | AR |
| REQ-F-COR-02 | `BAND_COREG` | inter-band co-registration residual | functional (REQ-F-COR-01) verified; budget withheld | AR |
| REQ-F-GEO-03 | `GEO_CE90` | geolocation circular error 90th percentile | functional (REQ-F-GEO-01/02) verified; budget withheld | AR |
| REQ-F-PAN-02 (opt) | spectral fidelity | spectral-fidelity metric vs budget | functional (REQ-F-PAN-01) verified; budget withheld | AR |
| REQ-Q-03 | (all of the above) | numerical objectives validated locally | A-verified; T-verdict withheld | AR |

Consistent with RD-8 `<8.8>` (validation-campaign contingency) and RTM G-2: the deferral is a
**managed, recorded open item, not a verification gap**. No private threshold or numeric target is
disclosed in this report (REQ-S-01/05). The deferral is the only item preventing full closure of the
Requirements-Baseline numeric budgets at QR; all other QR exit criteria are met.

---

## <9> `[impl]` fail-stop waiver register

Six algorithm bodies are legitimately finalised in implementation (`[impl]`) and are **all
fail-stop**: the operational baseline never executes them, and each is held behind a typed
`MsiProcessorError` fail-stop so that no degraded product is ever produced. All six are **recorded
waivers traced to RTM G-1 / G-6** and do not affect the Category-C V&V conclusion for the operational
baseline.

| # | Unit | Function ( `[impl]` ) | Algorithm | Operational baseline substitute | Fail-stop evidence |
|---|---|---|---|---|---|
| 1 | `l0_decode` | `decode_source_packets` | ALG-L0-DEC | public path consumes the documented open-container sample layout | typed reject; covered by L0 unit tests |
| 2 | `georeference` | `orbit_state` | ALG-GEO-ORBIT | GCP reference-image refinement (no ephemeris) | fail-stop on the orbit-propagation path |
| 3 | `georeference` | `orthorectify` | ALG-GEO-ORTHO | GCP reference-image refinement | **2 xfail tests** in `test_georeference_core.py` assert the fail-stop (`<6.1>`) |
| 4 | `atmospheric` | `retrieve_atmospheric_parameters` | ALG-ATM-PAR | AOT / water-vapour ingested from ADF | fail-stop on image-based retrieval |
| 5 | `atmospheric` | `resolve_rt_lut` | ALG-ATM-RT | radiative-transfer LUT supplied as ADF | fail-stop on RT-engine LUT build |
| 6 | `atmospheric` | `classify_scene_ml` | ALG-ATM-SCM | deterministic scene classifier | fail-stop on ML refinement |

**Also deferred (pan-sharpen).** The component-substitution fusion methods (`brovey`, `gs`, `ihs`,
`atrous`) are deferred; only `simple_mean` is operational (REQ-F-PAN-01, optional). Selection of a
deferred method is rejected at profile validation (fail-stop), so no untested fusion path runs in the
baseline.

**Disposition.** All waivers are expected per the SDP (RD-1 §5.1) and recorded in the RTM (G-1/G-6) and
Risk Register (RD-15). Each `[impl]` body's **interface and exception behaviour is verified now**; the
body-level numerics are completed post-QR against the frozen interface and re-validated via VT-1/VT-5.
The waivers are non-gating because the **operational `L0c`→`L2A` baseline never executes them** and the
fail-stop guarantees data-integrity (REQ-SAF-01, REQ-F-DEP-01).

---

## <10> Traceability closure

The bidirectional traceability is **closed with no orphans** at the QR baseline, per the RTM (RD-11
`<6>`):

- **Forward (requirement → design → verification).** All **100** `REQ-*` are allocated to ≥ 1 design
  component `C-*` (RD-9) and carry ≥ 1 verification method with a result in `<7>`. **No unimplemented
  and no unverified requirement** (the 9 deferred carry a recorded Tier-C deferral, not a missing
  binding).
- **Backward (upper-level / design / algorithm → requirement).** All **66** `SYS-*` (RD-2), **31**
  `REQ-IF-*` (RD-3), **20 + 1** `C-*` (RD-9), **11** `DPM-M-*` (RD-6) and **33** `ALG-*` (RD-7) trace
  down to ≥ 1 requirement. **No orphan** system/interface requirement, component, module or algorithm.
- **Recorded exclusions (not gaps).** N/A closures **REQ-D-08, REQ-R-05, REQ-REL-03** (verified by
  review, RTM G-3); static-evidence "—" requirements verified by I/A/R (RTM G-4); optional `(opt)`
  stages verified when enabled (RTM G-5); `[impl]` bodies at interface level (RTM G-6, `<9>`).

The QR verification results in `<7>`–`<9>` are forwarded into the RTM verification columns (RD-11
`<7>`), keeping the matrix the single source of truth.

---

## <11> Deviations, nonconformances and open items

| Ref | Item | Type | Status at QR |
|---|---|---|---|
| SPR-IT-01 | `AtmosphericUnit` dropped the `L1C` geolocation grid from `L2A` (surfaced by integration tests, `<6.3>`) | SPR (defect) | **Closed** — fixed by `conditions` passthrough; re-verified |
| OI-1 | Tier-C numeric budgets (REQ-P-01..05, REQ-F-COR-02, REQ-F-GEO-03, REQ-F-PAN-02, REQ-Q-03) | Open item (deferral) | **Open** — carried to AR (private data); RTM G-2, `<8>` |
| OI-2 | `[impl]` fail-stop bodies (6) + pan-sharpen fusion methods | Waiver | **Recorded** — non-gating; RTM G-1/G-6, `<9>` |
| OI-3 | `deps-sec` ignore-list (PYSEC-2026-248/249, CVE-2026-48817/48818) | Waiver | **Recorded** — eopf-transitive, unfixable while `eopf==2.8.1` pinned; revisit on bump (`<5.3>`) |
| OI-4 | `integration-tests` / `deliver-image` non-blocking (shell runner) | Constraint | **Open** — promote to blocking on a K8s runner (RD-15) |
| OI-5 | No git tag created for `v0.1.0-rc1` | Config action | **Open** — tagging is the AR / release-decision action; SRN states the RC + baseline commit (RD-18, RD-16/RD-17) |

No open **NCR** of severity blocking QR exists. SPR/NCR status is tracked to closure at QR/AR per RD-13
`<6>` and RD-12 §6.5.

---

## <12> Conclusion

Against the QR configuration baseline (`main` commit `d140599`, pipeline `30730` success), the
verification and validation defined in the V&V Plan (RD-8) and SUITP (RD-10) has been executed and
its results recorded above. The findings are:

1. **Static analysis and quality gates** — all blocking CI gates are **green**: `flake8`, `black` +
   `isort`, `mypy`, `bandit`, `pip-audit` (with the justified eopf-transitive ignore-list), `hadolint`,
   `unit-tests` + coverage, wheel build and Sphinx docs (`<5>`).
2. **Test verification** — **248** test cases (**246** unit: 244 passed + 2 intentional xfail
   verifying the orthorectify fail-stop; **2** integration: passed) from **238** test functions, with
   **0** unexpected failures and the coverage gate met; the integration suite wired all **8**
   processing units and surfaced+fixed one real defect, now closed (`<6>`).
3. **Requirements** — of the **100** SRS requirements, **91 are verified at QR** (85 Verified + 6
   Verified with a tested `[impl]` fail-stop safety net), and **9 carry a deferred Tier-C numeric-budget
   verdict** — the **5 REQ-P-01..05 performance budgets** plus the budget-coupled **REQ-F-COR-02,
   REQ-F-GEO-03, REQ-F-PAN-02, REQ-Q-03** — withheld at QR because they depend on operator-private real
   RAW + calibration data (SSS `<5.1>`) and **carried to AR** (`<7>`, `<8>`).
4. **Waivers and traceability** — the six `[impl]` fail-stop bodies (and the deferred pan-sharpen
   fusion methods) are recorded, non-gating waivers (`<9>`); traceability is **closed in both
   directions with no orphans** (`<10>`).

**Qualification statement.** The `msi-processor` software at the QR baseline is **verified against its
technical specification (SRS, RD-4) and qualified**, with the **single, explicitly bounded exception**
of the Tier-C numeric accuracy/performance budgets (REQ-P-01..05 and the four budget-coupled
requirements), whose numeric closure is a **documented open item carried to the Acceptance Review** and
to be validated on operator-private data. All Requirements-Baseline and interface requirements other
than these deferred budgets are verified, the code-coverage gate is met, and the SCI is under
configuration control (CIDL RD-16 / SCF RD-17) with the release candidate `v0.1.0-rc1` referenced to
`d140599` and stated in the SRN (RD-18). On this basis the software is assessed **ready to proceed to
the anticipated TRR/TRB and AR**, with OI-1 as the principal item to close at AR.

---

*End of Software Verification Report. Authored per ECSS-E-ST-40C Rev.1 Annex M and ECSS-Q-ST-80C
Rev.2 §6.2.6, tailored for Category C, single-developer. It reports the results of the V&V Plan (RD-8)
and SUITP (RD-10); the maintained traceability matrix is RD-11; deferred Tier-C numeric budgets are
carried to AR. No private threshold, calibration coefficient or numeric budget target is disclosed
(REQ-S-01/05).*
