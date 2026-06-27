# Software Product Assurance Plan (SPAP)

| | |
|---|---|
| **Document** | Software Product Assurance Plan (SPAP) |
| **DRD** | ECSS-Q-ST-80C Rev.2 (30 April 2025), Annex B |
| **Container** | Product Assurance File (PAF) |
| **Project** | `msi-processor` — generic high-resolution MSI data processor |
| **Configuration item** | `gitlab.eopf.copernicus.eu/ipf/msi-processor` |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 Annex D / ECSS-E-ST-40C Rev.1 Annex R) |
| **Baselined at** | SRR |
| **Status** | Draft for SRR |

> This SPAP is the software product assurance constituent of the Product Assurance File for the
> `msi-processor` project. It follows the ECSS-Q-ST-80C Rev.2 Annex B DRD section structure
> (clauses `<1>`–`<8>`), tailored for **Category C** and proportionate to a **single-developer**
> ground-segment project. Its central tenet: in the absence of an independent PA organisation,
> product assurance is **operationalised as automated, version-controlled CI quality and security
> gates** plus documented checklists, so that PA objectives are *evidenced* by pipeline artefacts
> rather than asserted. It is consistent with, and cross-references, the SDP
> (`compliance/software-development-plan.md`).

## <1> Introduction

The `msi-processor` is an operational ground-segment data processor that transforms downlinked
raw (Level-0) multispectral imager (MSI) data into calibrated, geophysically usable products up
to Level 2. It is a **generic high-resolution pushbroom MSI processor**: the chain (decoding →
radiometric correction → geometric correction → atmospheric correction) is sensor-agnostic and
driven by a per-sensor profile. It is built on the ESA EOPF (each stage an EOPF CPM
`EOProcessingUnit`, products as `EOProduct`, outputs as cloud-native Zarr, `eopf == 2.8.1`).

**Purpose and objective.** The purpose of this SPAP is to provide information on the
organisational aspects and the technical approach to the execution of the software product
assurance programme for `msi-processor`, in conformance with ECSS-Q-ST-80C Rev.2. The objective
is to give assurance — to the project owner and to any downstream user of the products — that
the processor is developed under a controlled, standards-conformant process and that the
delivered software meets its specified quality requirements.

**Content.** This plan describes the PA organisation and independence model (`<5.1>`–`<5.2>`),
the PA resources, reporting, quality models, risk and supplier contributions, and the methods
and tools (`<5.3>`–`<5.10>`); the software process assurance measures including dependability,
security, configuration/non-conformance control, metrics, reuse and per-activity PA planning
(`<6>`); the software product quality assurance approach mapping each CI gate to a PA objective
(`<7>`); and the compliance matrix to the applicable ECSS-Q-ST-80 clauses (`<8>`).

**Reason prompting preparation.** This document is prepared at project start to establish the
**SRR baseline** of the software product assurance programme, and is maintained throughout the
life cycle.

## <2> Applicable and reference documents

**Applicable documents**

| Ref | Document |
|---|---|
| AD-1 | ECSS-Q-ST-80C Rev.2 (30 April 2025) — Space product assurance — Software product assurance |
| AD-2 | ECSS-E-ST-40C Rev.1 (30 April 2025) — Space engineering — Software |
| AD-3 | ECSS-Q-ST-10C Rev.1 — Space product assurance — Product assurance management |
| AD-4 | ECSS-M-ST-40C — Configuration and information management |
| AD-5 | ECSS-M-ST-80C — Risk management |

**Reference documents**

| Ref | Document |
|---|---|
| RD-1 | SDP — Software Development Plan (`compliance/software-development-plan.md`) |
| RD-2 | SRevP — Software Review Plan (`compliance/drd/srevp-software-review-plan.md`) |
| RD-3 | Risk Register (`compliance/drd/risk-register.md`) |
| RD-4 | V&V Plan — SVerP/SValP/SUITP (`compliance/drd/vv-plan.md`) |
| RD-5 | SRF — Software Reuse File (`compliance/drd/srf-software-reuse-file.md`, `docs/srf.md`) |
| RD-6 | EOPF SDE — User Manual & CI/SonarQube quality-gate guidelines |
| RD-7 | EOPF Core Python Modules (CPM) documentation (`eopf == 2.8.1`) |

## <3> Terms, definitions and abbreviated terms

Terms and definitions follow AD-1, AD-2 and the SDP §3. Abbreviations specific to or emphasised
in this SPAP and not already defined in the SDP:

| Abbreviation | Definition |
|---|---|
| NCR | Non-Conformance Report |
| NRB | Non-conformance Review Board (here: the documented single-developer disposition record) |
| PA | Product Assurance |
| PAF | Product Assurance File |
| SAST | Static Application Security Testing |
| SCA | Software Composition Analysis (dependency vulnerability scanning) |
| SPA | Software Product Assurance |
| SPAMR | Software Product Assurance Milestone Report (tailored out — see `<5.4>`) |
| SQ | SonarQube |

(ECSS review acronyms SRR/PDR/CDR/QR/AR and DRD acronyms per the SDP §3.)

## <4> System Overview

A full description of the system and software products is given in the SDP §1 and in the
SSS/IRD; it is not duplicated here. In summary, the configuration item is the Python package
`msi_processor` (the `main` branch of the Git repository), composed of L0→L2 processing units
implemented as EOPF CPM `EOProcessingUnit`s with a pure, unit-testable core plus a thin PU
wrapper, parameterised by a per-sensor profile. Outputs are Zarr `EOProduct`s. The software is
distributed as a Python wheel and a container image; the runtime is the EOPF SDE
(`registry.eopf.copernicus.eu/sde/cpm-build-environment:latest`, Python 3.11).

**Data and exportability policy (PA-relevant).** Source code is public (Apache-2.0). Raw input
data and instrument calibration (gain/offset, dark, flat-field) are **private** — never
committed and never used in public CI. Numerical verification on real data is performed locally.
This split shapes the PA approach: CI assures *process and code* quality; *numerical* product
quality is assured locally and recorded in the SVR.

## <5> Software product assurance programme implementation

### <5.1> Organization

**Organizational structure.** `msi-processor` is a **single-developer** project. The project
owner holds, concurrently, the supplier-side software engineering, software product assurance,
and verification roles. There is no separate PA department and no customer/supplier hierarchy
beyond the project owner and the hosting EOPF SDE programme.

**Interfaces.** The only external organisational interface is the **EOPF SDE platform team**
(provider of the build image, CI runner, SonarQube instance and Pages hosting), consumed as a
service. There are no internal sub-organisations. ECSS milestone governance is the `ipf` GitLab
group (SRR→PDR→CDR→QR→AR group milestones).

**Relationship to system-level PA and safety.** `msi-processor` is ground-segment software with
no flight, safety or mission-loss function (see `<6.3>`); there is no system-level safety case to
interface with. System-level PA reduces to the milestone reviews and the Risk Register (RD-3).

**Independence of the SPA function.** Personnel independence is not achievable in a
single-developer project. Independence of the *verification and PA judgement* is therefore
obtained by **structural and automated means**:

1. **Automated, non-overridable gates** — the CI pipeline (`.gitlab-ci.yml`) executes the
   quality and security checks of `<5.8>`/`<7>` on every merge request; blocking gates fail the
   pipeline independently of the developer's opinion. The developer cannot merge a
   gate-failing change without an explicit, recorded waiver.
2. **Static, version-controlled tool configurations** — gate thresholds live in
   `pyproject.toml`, `.flake8`, `.mypy.ini`, `bandit.yml`, `.coveragerc`, `.hadolint.yml` and
   `.pre-commit-config.yaml`; changing a threshold is itself a reviewable diff with audit trail.
3. **A third-party adjudicator** — SonarQube applies the EOPF quality gate (`<5.5>`) as an
   external pass/fail authority on coverage, reliability, security and maintainability.
4. **Documented checklists** — merge-request and milestone-review checklists (RD-2) force an
   explicit, recorded self-review against PA criteria before baselining.

**Delegation to a lower-level supplier.** None. No software is procured or subcontracted; all
third-party software is open-source *reuse* assured per `<5.7>`/`<6.7>` and the SRF (RD-5).

### <5.2> Responsibilities

The SPA function (the project owner acting in the PA role) is responsible for:

- defining and maintaining this SPAP and the PA-relevant configurations of the CI gates;
- ensuring every change to `main` passes the blocking CI gates, or carries a recorded waiver;
- triaging, classifying and dispositioning non-conformances (`<6.5>`);
- maintaining standards conformance (`<6.9>`) and the compliance matrix (`<8>`);
- assuring reused open-source software via the SRF and the SCA gate (`<6.7>`);
- reporting PA status at each milestone review (`<5.4>`).

### <5.3> Resources

**Human resources and skills.** One person (the project owner), competent in Python, EOPF CPM,
remote-sensing data processing and the ECSS-E-40/Q-80 framework. No additional PA staff are
allocated; the staffing model and its rationale are in the SDP §4.7.

**Hardware.** Development workstation; the EOPF SDE Studio VM hosting the GitLab **shell-executor**
CI runner. Container-runtime / Dask-gateway / S3-dependent jobs are not runnable on the shell
runner and are configured non-blocking until a Kubernetes runner is available (see `<5.8>`).

**Software tools.** The CI toolchain of `<5.8>` (flake8, black, isort, mypy, bandit, trivy,
xenon, hadolint, docstr-coverage, pytest+coverage, SonarQube, pre-commit), the GitLab platform
(issues, merge requests, milestones, package & container registries, Pages), and the EOPF CPM
build image. All tools are open-source or platform-provided; licences are recorded in the SRF.

### <5.4> Reporting

PA reporting is **artefact-based and continuous** rather than periodic written reports:

- **Per change:** the CI pipeline status and its artefacts (`linter.txt`, `coverage.xml`,
  `TEST-pytests.xml`, `vulnerability.json`, trivy output, SonarQube dashboard) are the standing
  PA record for each merge request.
- **Per milestone:** PA status (gate results, open non-conformances by severity, waivers,
  standards-conformance and compliance-matrix status) is summarised in the milestone review per
  RD-2 and recorded against the GitLab milestone.

A standalone **Software Product Assurance Milestone Report (SPAMR, Annex C)** is **tailored out**
for this Category C single-developer project; its content is subsumed by the milestone review
record and the SVR (RD-4). This tailoring is recorded in the SDP §5.6 and in `<8>`.

### <5.5> Quality models

The applicable product-quality model is the **EOPF SonarQube quality gate** (RD-6), expressed as
quantitative thresholds and used to derive the product quality requirements assured in `<7>`:

| Quality characteristic | Metric | Target |
|---|---|---|
| Reliability | SonarQube reliability rating | A |
| Security | SonarQube security rating | A |
| Maintainability | Technical-debt ratio | ≤ 5 % |
| Testability | Unit-test line coverage (new code) | ≥ 70 % |
| Security (vulnerabilities) | Open vulnerabilities | 0 |
| Analysability | Comment / documentation density | ≥ 20 % |

Complexity is additionally bounded by `xenon` (`<5.8>`). These thresholds are the contract
between the CI gates (`<7>`) and the PA objectives; deviations are non-conformances (`<6.5>`).

### <5.6> Risk management

The SPA function contributes to project risk management (AD-5) by surfacing process and product
risks (e.g. uncovered code paths, unfixed dependency CVEs, complexity hotspots, calibration-data
unavailability) from the CI gate outputs into the **Risk Register** (RD-3), which is reviewed at
each milestone. PA-originated risks are raised as GitLab issues with the `Risk` template and
linked to their mitigation merge requests.

### <5.7> Supplier selection and control

There are **no commercial software suppliers and no subcontracting** (SDP §4.8–4.9). The only
"suppliers" are the **open-source projects reused** by `msi-processor` and the EOPF SDE platform.
The SPA contribution to their selection and control is:

- **Selection** — driven by the EOPF CPM ecosystem and recorded, with licence and provenance, in
  the SRF (RD-5); only permissively licensed (Apache-2.0/MIT/BSD/PSF) components are admitted.
- **Control** — versions are pinned (`pyproject.toml`, `eopf == 2.8.1`); dependency
  vulnerabilities are monitored by the **trivy** SCA gate (`deps-sec`, `<6.7>`); licence and
  exportability constraints are tracked in the SRF.

### <5.8> Methods and tools

PA is implemented through an automated toolchain applied at two stages — **local pre-commit** and
**CI pipeline** — over the development cycle. All tools are mature, widely adopted open-source
products at stable releases (versions and licences in the SRF, RD-5); their configurations are
version-controlled.

**Local gate.** `pre-commit` (`.pre-commit-config.yaml`) runs fast formatting/lint hooks before
each commit, shifting defect detection left of CI.

**CI gate inventory** (`.gitlab-ci.yml`). Blocking = pipeline fails on violation; Non-blocking =
`allow_failure: true` (reported, not gating — pending the SDE Kubernetes runner, or advisory by
nature):

| Job | Tool | Config | Invocation (essentials) | Gating |
|---|---|---|---|---|
| `linter` | flake8 | `.flake8` | `flake8 msi_processor tests` | **Blocking** |
| `formater` | black, isort | `pyproject.toml` | `black --check --diff .`; `isort --check --diff` | **Blocking** |
| `typing` | mypy | `.mypy.ini` | `mypy msi_processor` | **Blocking** |
| `unit-tests` | pytest, coverage | `pyproject.toml`, `.coveragerc` | `pytest --cov -m unit` → cobertura + junit | **Blocking** |
| `security` | bandit | `bandit.yml` | `bandit -c bandit.yml -r msi_processor` (+ JSON) | **Blocking** |
| `docker-linter` | hadolint | `.hadolint.yml` | `hadolint Dockerfile` (codequality report) | **Blocking** |
| `deps-sec` | trivy | — | `trivy fs --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed` | Non-blocking |
| `complexity` | xenon | — | `xenon --max-average B --max-modules C --max-absolute D` | Non-blocking |
| `docs-cov` | docstr-coverage | — | `docstr-coverage -F 30` | Non-blocking |
| `sonarqube` | SonarQube scanner | server gate | `sonar-scanner -Dsonar.qualitygate.wait=true` (ingests flake8/bandit/coverage/junit) | Non-blocking |

**Maturity note.** `trivy`, `complexity` and `sonarqube` are intended to be **blocking** once the
SDE Kubernetes runner replaces the shell executor; until then they run advisory so that no
infrastructure limitation silently weakens a PA objective. This planned hardening is tracked as a
risk in RD-3.

### <5.9> Process assessment and improvement

**Scope and objectives.** Assessment is limited to verifying that the documented life cycle (SDP)
and the CI gates of this SPAP are actually applied, and to incrementally tightening gates as the
codebase and infrastructure mature. Formal external process assessment (e.g. ISO/IEC 15504) is
**tailored out** as disproportionate for Category C single-developer scope.

**Methods and tools.** Assessment evidence is the Git/CI history (every change is a reviewed
merge request with an attached pipeline) and the milestone-review checklists (RD-2). Improvement
actions are raised as GitLab issues (`Action` template) and closed via merge requests — e.g.
promoting a non-blocking gate to blocking, raising the coverage target, or adding a check.

### <5.10> Operations and maintenance (optional)

Operations and maintenance PA is **light**. Maintenance is performed through the same gated
issue→branch→merge-request→review flow as development; releases follow semantic versioning with
Git tags and GitLab Releases. A standalone Software Maintenance Plan is tailored out (SDP §5.5.2);
maintenance quality is assured by re-running the full CI gate set on every change, including after
delivery.

## <6> Software process assurance

### <6.1> Software development cycle

The software development life cycle is defined in the **SDP** (RD-1, §5.2): an incremental
paradigm synchronised by the ECSS reviews SRR→PDR→CDR→QR→AR (GitLab group milestones), with
implementation starting only after CDR. The SPAP does not redefine it. The milestone immediately
**before the start of software validation** is **CDR**: design, test plans (RD-4) and the reuse
file are baselined at CDR, after which coding and then validation proceed.

### <6.2> Projects plans

All project plans and their relationships are defined in the SDP §5.5 (tailored DRL). The plans
relevant to PA are: this SPAP, the SDP (RD-1), the SRevP (RD-2), the V&V Plan (RD-4), the Risk
Register (RD-3) and the SRF (RD-5). Each plan is baselined at the review indicated in the SDP DRL
and updated through merge requests thereafter; timely preparation/update is enforced by tying each
plan to its GitLab milestone.

### <6.3> Software dependability and safety

`msi-processor` is classified **Category C** (ECSS-Q-ST-80C Rev.2 Annex D). Rationale: a failure
produces degraded or incorrect *data products only* — there is no safety, mission-loss or
space-segment consequence, and any defect is recoverable by reprocessing. Consequently:

- **No safety-critical functions** exist; no safety case, FMECA or fault-tree analysis is
  required, and the corresponding ECSS-Q-ST-80 dependability/safety requirements are tailored out
  for Category C (recorded in `<8>`).
- The dependability measures retained are *correctness* measures, proportionate to Category C:
  deterministic unit tests with coverage gating, static typing (mypy), bounded complexity
  (xenon), and **numerical-accuracy** control of the processing algorithms (verified locally on
  real data and recorded in the SVR — see `<6.9>` item 15 and `<7>`).

### <6.4> Software security

The software handles no classified or security-sensitive information; there is no
security-sensitive function. The security assurance approach is nonetheless concrete:

- **No secrets in the repository.** Credentials and platform tokens (e.g. `SQ_LOGIN`,
  `CI_REGISTRY_PASSWORD`, Dask/JupyterHub tokens) are CI variables only; `validate-variables`
  fails the pipeline if a required variable is unset. Raw data and calibration are never
  committed.
- **SAST** — `bandit` (`security` job, blocking) statically scans `msi_processor` for common
  Python security defects; findings are also fed to SonarQube.
- **SCA** — `trivy fs` (`deps-sec` job) scans dependencies for HIGH/CRITICAL CVEs.
- **Container hardening** — `hadolint` (`docker-linter`, blocking) lints the `Dockerfile`.

This clause constitutes the **security assurance section** required by the DRD: the related
security activities are the gates above and the no-secrets/data-privacy policy of `<4>`. No
separate security file is produced (none is warranted at this criticality).

### <6.5> Software documentation and configuration management

**Contribution to documentation and CM.** PA assures that every configuration item — code,
formal DRD documents, CI configuration — is under Git version control with change introduced only
through reviewed merge requests, per ECSS-M-ST-40C (AD-4). Configuration identification, status
accounting and the baseline-per-milestone scheme are defined in the SCF/CIDL and the SDP §5.2.3.

**Non-conformance control system.** Non-conformances are managed as **GitLab issues** on the
project, which constitute the NCR channel. The procedure applies **from the SRR baseline onward**
(i.e. from the first baselined CI pipeline and document set); pre-baseline defects are ordinary
development work. The workflow is:

1. **Report** — an issue is opened using the appropriate template (`Bug`, `Action`,
   `Documentation`, `Risk`), or auto-evidenced by a failing CI gate.
2. **Classify** — a severity label is applied:

   | Label | Meaning |
   |---|---|
   | `severity:critical` | Wrong/lost product data, security exposure, or pipeline-blocking failure |
   | `severity:major` | Incorrect result or broken feature with no workaround |
   | `severity:minor` | Degraded behaviour with a workaround |
   | `severity:trivial` | Cosmetic / documentation defect |

3. **Disposition** — the project owner records the disposition (fix / waiver / N/A) on the issue;
   this is the single-developer equivalent of an NRB decision. A waiver of a blocking gate is only
   valid when recorded on the issue with rationale and an expiry/closure condition.
4. **Verify & close** — the fix is delivered by a linked merge request that must pass the full
   gate set; the issue is closed with the merge reference, giving end-to-end traceability from
   report to verified fix.

**Protection, integrity key and labelling of delivered software.** The delivered wheel and
container image are integrity-identified by **SHA-256 checksum** (wheel) and **image digest**
(container); the **labelling/marking** of a release is the **semantic-version Git tag + GitLab
Release** (and the package-registry version), which is the authoritative delivered-media label.
These identifiers are recorded in the SRelD/SRN.

### <6.6> Process metrics

Process metrics are derived from the quality model (`<5.5>`) and collected automatically by the
CI pipeline as build artefacts: test pass/fail and coverage trend (`coverage.xml`,
`TEST-pytests.xml`), static-analysis and security findings (`linter.txt`, `vulnerability.json`,
trivy output), complexity and docstring-coverage, and the SonarQube history. They are stored as
pipeline artefacts and in the SonarQube project, analysed at each milestone, and used to manage
the process (e.g. promoting gates to blocking, prioritising refactoring of complexity hotspots).

### <6.7> Reuse of software

`msi-processor` reuses (a) the **EOPF CPM** framework and the scientific-Python stack as runtime
dependencies, and (b) the **algorithm mathematical heritage** from prior work (SDP §1, RD-5). The
PA approach for reuse:

- Every reused component is declared in the **SRF** (RD-5) with version, developer, licence,
  exportability constraints and execution environment.
- **Delta qualification** of reused *code* is achieved by integration into the gated pipeline:
  reused libraries are exercised through `msi_processor`'s own unit/integration tests, type
  checks, and the `trivy` SCA gate; only permissive licences are admitted (`<5.7>`).
- Reuse of the *algorithm heritage* is qualified by re-deriving each algorithm against its ATBD
  and verifying numerical results locally on real data (recorded in the SVR), since the heritage
  is mathematical, not a black-box binary.

### <6.8> Product assurance planning for individual processes and activities

Taking into account the project scope and life cycle, PA measures per activity are:

| Activity | PA measures |
|---|---|
| Software requirements analysis | Uniquely-identified `REQ-*` requirements with forward/backward traceability (SRS + traceability matrix); reviewed at PDR. |
| Architectural & detailed design | EOPF CPM PU pattern (pure core + thin wrapper) reviewed against SRS at CDR; design recorded in SDD/DJF. |
| Coding | `flake8` + `black` + `isort` + `mypy` + `bandit` blocking gates; `xenon` complexity bound; PEP 8. |
| Testing & validation (incl. regression) | `pytest -m unit` blocking with ≥ 70 % coverage gate; full gate set re-run on every change provides regression assurance; integration tests when runner available; numerical validation locally → SVR. |
| Verification | Per the V&V Plan (RD-4); gate artefacts are verification evidence; milestone checklists (RD-2). |
| Delivery & acceptance | Wheel/image built and (on tag) published; integrity checksums and SemVer labelling (`<6.5>`); acceptance at QR/AR. |
| Operations & maintenance | Light (`<5.10>`): same gated flow post-delivery. |

### <6.9> Procedures and standards

The procedures and standards applicable to development are defined or referenced in the SDP and
enforced by PA as follows. PA measures ensuring adherence are primarily the **blocking CI gates**
and the **review checklists** (RD-2):

| # | Aspect | Standard / procedure | PA adherence measure |
|---|---|---|---|
| 1 | Project management | SDP (RD-1), GitLab milestones | Milestone review checklist |
| 2 | Risk management | AD-5, Risk Register (RD-3) | Reviewed each milestone |
| 3 | Config. & documentation mgmt | AD-4, SCF/CIDL | All CIs in Git; MR-only changes |
| 4 | Verification & validation | V&V Plan (RD-4) | Gate artefacts; SVR |
| 5 | Requirements engineering | ECSS-E-ST-40 DRDs | Traceability matrix |
| 6 | Design | EOPF CPM PU pattern | CDR design review |
| 7 | Coding | PEP 8 | `flake8`/`black`/`isort` (blocking) |
| 8 | Metrication | EOPF SQ quality gate (`<5.5>`) | SonarQube + coverage gates |
| 9 | Non-conformance control | `<6.5>` | GitLab issues + severity labels |
| 10 | Audits | Self-audit via Git/CI history | `<5.9>` |
| 11 | Alerts | GitLab security advisories; trivy CVEs | `deps-sec` job |
| 12 | Procurement | N/A (no procurement) | SDP §4.8 |
| 13 | Reuse of existing software | SRF (RD-5) | `<6.7>` |
| 14 | Use of methods and tools | `<5.8>` | Version-controlled tool configs |
| 15 | Numerical accuracy | ATBD / SVR | Local verification on real data |
| 16 | Delivery, installation, acceptance | SRelD/SRN | Checksums + SemVer (`<6.5>`) |
| 17 | Operations / maintenance | `<5.10>` | Gated MR flow |
| 18 | Device programming and marking | N/A (no programmable devices) | — |

## <7> Software product quality assurance

The approach to ensuring software-product quality is the **mapping of each CI gate to a PA
objective**, with target values from the quality model (`<5.5>`) and automated collection. This is
the core of the single-developer independence model (`<5.1>`): the gates are the assurance
activities.

**Gate → PA objective mapping**

| PA objective | Product metric & target | CI gate (job/tool) | Collection means | Feedback |
|---|---|---|---|---|
| Code is style-conformant & lint-clean | 0 flake8 violations | `linter` / flake8 (blocking) | `linter.txt` artefact → SonarQube | Pipeline fails; fix via MR |
| Code is consistently formatted | 0 black/isort diffs | `formater` (blocking) | check-mode diff | Pipeline fails |
| Type contracts hold | 0 mypy errors | `typing` / mypy (blocking) | job log | Pipeline fails |
| Behaviour is correct & covered | tests pass; coverage ≥ 70 % | `unit-tests` / pytest+cov (blocking) | cobertura + junit artefacts | Pipeline fails; coverage trend |
| No SAST security defects | 0 bandit findings | `security` / bandit (blocking) | `vulnerability.json` → SonarQube | Pipeline fails |
| No vulnerable dependencies | 0 HIGH/CRITICAL CVEs | `deps-sec` / trivy (advisory→blocking) | trivy report | Risk/issue raised |
| Container image well-formed | 0 hadolint errors | `docker-linter` / hadolint (blocking) | codequality report | Pipeline fails |
| Complexity bounded | xenon ≤ B avg / C module / D abs | `complexity` / xenon (advisory→blocking) | job log | Refactor issue |
| Code is documented | docstring coverage ≥ 30 % (→ SQ ≥ 20 %) | `docs-cov` / docstr-coverage | badge artefact | Issue raised |
| Overall product quality | SQ gate: reliability A, security A, debt ≤ 5 %, vulnerabilities 0 | `sonarqube` (`qualitygate.wait=true`) | SonarQube dashboard | Gate verdict |
| Numerical/product correctness | matches reference products (local) | local verification (not CI) | SVR (RD-4) | Documented at QR |

**Metrication programme.** Metrics are collected on **every** push and merge request (continuous
metrication); trends accumulate in SonarQube and in pipeline artefacts and are reviewed at each
milestone (`<6.6>`).

**Analyses and feedback.** Gate failures feed back immediately to the developer (the pipeline
blocks the merge); trend analyses (coverage, complexity, debt) feed back at milestones and drive
the improvement actions of `<5.9>`.

**Documentation quality requirements.** Code is documented to the docstring-coverage and
comment-density targets above; formal DRD documents follow their Annex structure and are reviewed
per RD-2.

**Assurance activities.** The blocking gates, the SonarQube quality verdict, the review
checklists and the local numerical verification together constitute the assurance that the
product meets its quality requirements.

## <8> Compliance matrix to software product assurance requirements

Compliance to the applicable ECSS-Q-ST-80C Rev.2 clauses (per the SPAP traceability of DRD
Table B-1), tailored for Category C. Legend: **C** = compliant, **NC** = non-compliant,
**NA** = not applicable / tailored out.

| ECSS-Q-ST-80 clause | Topic | Compliance | SPAP reference | Remarks |
|---|---|---|---|---|
| 5.1.2 / 5.1.3 / 5.1.4 | PA organisation, responsibility, authority | C | `<5.1>`, `<5.2>` | Single-developer; independence via tooling |
| 5.2.1 | PA planning and control | C | `<5.4>`, `<5.8>` | Artefact-based, continuous |
| 5.2.1.4 | Operations & maintenance measures | C | `<5.10>` | Light |
| 5.2.1.5 | Compliance matrix maintained | C | `<8>` | This table |
| 5.2.6 | Non-conformances | C | `<6.5>` | GitLab issues + severity labels |
| 5.2.7 | Quality requirements and quality models | C | `<5.5>`, `<7>` | EOPF SQ quality gate |
| 5.3 | Risk management contribution | C | `<5.6>` | Risk Register (RD-3) |
| 5.4.3 / 5.4.4 | Supplier selection & control | NA | `<5.7>` | No suppliers; open-source reuse only |
| 5.6.1 | Methods and tools | C | `<5.8>` | Version-controlled tool configs |
| 5.7 | Process assessment & improvement | C | `<5.9>` | Self-audit via Git/CI; ext. assessment tailored out |
| 6.1 | Software development cycle | C | `<6.1>` | Defined in SDP (RD-1) |
| 6.2.x | Documentation of processes / metrics / CM / verification | C | `<6.2>`,`<6.5>`,`<6.6>`,`<7>` | — |
| 6.2.2 / 6.3.x | Dependability and safety; critical software | NA | `<6.3>` | Category C; no safety function |
| 6.2.7 | Reuse of existing software | C | `<6.7>` | SRF (RD-5) + delta qualification |
| 6.2.9 / 6.2.10 | Software security / sensitive software | C / NA | `<6.4>` | Security gates present; no sensitive data |
| 6.3.3–6.3.5 | PA for design / coding / testing & validation | C | `<6.8>` | Per-activity gates |
| 7.1 | Product quality objectives & metrication | C | `<5.5>`, `<7>` | Gate→objective mapping |
| 7.1.7 | Numerical accuracy | C | `<6.9>` #15, `<7>` | Verified locally → SVR |
| 7.2.2.3 | Design/related documentation quality | C | `<6.8>`, `<7>` | — |
| 7.5.x | Programmable device programming/marking/calibration | NA | `<6.9>` #18 | No programmable devices |
| Annex C | SPAMR | NA | `<5.4>` | Tailored out; subsumed by milestone review + SVR |

---

*End of SPAP. Authored per ECSS-Q-ST-80C Rev.2 Annex B; tailored for Category C, single-developer.
May be combined with the project Product Assurance Plan (ECSS-Q-ST-10) per DRD B.2.2.*
