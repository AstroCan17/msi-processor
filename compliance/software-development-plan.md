# Software Development Plan (SDP)

| | |
|---|---|
| **Document** | Software Development Plan (SDP) |
| **DRD** | ECSS-E-ST-40C Rev.1, Annex O |
| **Container** | Management File (MGT) |
| **Project** | `msi-processor` — generic high-resolution MSI data processor |
| **Configuration item** | `gitlab.eopf.copernicus.eu/ipf/msi-processor` |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | SRR |
| **Status** | Draft for SRR |

> This SDP is the top-level management artefact of the ECSS software life cycle for the
> `msi-processor` project. It follows the ECSS-E-ST-40C Rev.1 Annex O DRD section structure
> and records the management and development approach, the life-cycle model, the review
> milestones, and — through the tailoring in §5.5 / §5.6 — the documentation tree the project
> commits to. The footprint is tailored to a Category C, small-team ground-segment processor.

## <1> Introduction

The `msi-processor` is an **operational ground-segment data processor** that transforms
**downlinked raw (Level-0) multispectral imager (MSI) data** into calibrated and
geophysically usable products **up to Level 2**. It is designed as a **generic high-resolution
pushbroom MSI processor**: the processing chain (decoding → radiometric correction →
geometric correction → atmospheric correction) is sensor-agnostic and driven by a per-sensor
configuration/profile, the first instantiated profile being the project owner's own sensor.

The processor is built on the **ESA Earth Observation Processing Framework (EOPF)**: each
processing stage is an EOPF Core Python Modules (CPM) `EOProcessingUnit`, products are
handled as EOPF `EOProduct` objects, and outputs are written as cloud-native **Zarr**. The
processing algorithms are not developed from scratch — their mathematical basis already
exists in prior work (see SRF) — so this project is fundamentally an **integration and
ECSS-compliant productisation** effort rather than new-algorithm research.

The purpose of this SDP is to describe the established management and development approach
for the software items of `msi-processor`, in accordance with ECSS-E-ST-40C Rev.1. It is
prepared at project start to establish the SRR baseline and is maintained throughout the life
cycle.

## <2> Applicable and reference documents

**Applicable documents**

| Ref | Document |
|---|---|
| AD-1 | ECSS-E-ST-40C Rev.1 (30 April 2025) — Space engineering — Software |
| AD-2 | ECSS-Q-ST-80C Rev.2 (30 April 2025) — Space product assurance — Software product assurance |
| AD-3 | ECSS-M-ST-10C Rev.1 — Space project management — Project planning and implementation |
| AD-4 | ECSS-M-ST-40C — Configuration and information management |

**Reference documents**

| Ref | Document |
|---|---|
| RD-1 | EOPF Software Development Environment (SDE) — User Manual & Guidelines |
| RD-2 | EOPF Core Python Modules (CPM) documentation (`eopf == 2.8.1`) |
| RD-3 | Prior work — multispectral pushbroom preprocessing pipeline (algorithm heritage; see SRF) |
| RD-4 | ECSS-E-ST-40C Rev.1 Annex R — Tailoring based on software criticality |
| RD-5 | ECSS-E-ST-40C Rev.1 Annex Q — Document organization and contents at each review |

## <3> Terms, definitions and abbreviated terms

Terms and definitions follow AD-1, AD-2 and the EOPF SDE glossary. Abbreviations used in
this document and not defined in the applicable/reference documentation:

| Abbreviation | Definition |
|---|---|
| ADF | Auxiliary Data File |
| ATBD | Algorithm Theoretical Basis Document |
| CPM | (EOPF) Core Python Modules |
| DPM | Data Processing Model |
| DRD / DRL | Document Requirements Definition / Document Requirements List |
| EOPF | Earth Observation Processing Framework |
| MSI | Multispectral Imager |
| NUC | Non-Uniformity Correction |
| PU | (EOPF CPM) Processing Unit |
| SDE | (EOPF) Software Development Environment |
| TOA | Top Of Atmosphere |

(ECSS review acronyms SRR/PDR/CDR/QR/AR and DRD acronyms SDP/SRS/SDD/ICD/… per AD-1.)

## <4> Software project management approach

### <4.1> Management objectives and priorities

Management objectives, in priority order:

1. **Standards conformance** — develop the processor under the ECSS-E-ST-40C Rev.1 life
   cycle (documentation-first, milestone-driven) so that progress, rationale and traceability
   are auditable from the Git history.
2. **Correctness & verifiability** — every processing stage is traceable to a requirement
   and verified against deterministic unit tests and, where data permits, reference products.
3. **Reuse over reinvention** — integrate the existing algorithm heritage and the EOPF CPM
   framework rather than redeveloping (see SRF).
4. **Reproducibility & portability** — pinned environment (`eopf == 2.8.1`), Zarr outputs,
   CI-enforced quality gates.

### <4.2> Master schedule

The project schedule is milestone-driven and tracked as **GitLab group milestones** on
`ipf` (SRR, PDR, CDR, QR, AR). The master schedule references those milestones; document
baselines per milestone are defined in §5.2.3. (Calendar dates are managed in the GitLab
milestones, not duplicated here.)

### <4.3> Assumptions, dependencies and constraints

- **Assumptions:** the algorithm mathematical basis is available from prior work; the owner's
  raw data and the corresponding instrument calibration (gain/offset, dark, flat-field) are
  available for local verification.
- **Dependencies:** EOPF SDE GitLab platform and CI runner; EOPF CPM (`eopf == 2.8.1`) build
  image; availability of the sensor calibration auxiliary data.
- **Constraints:**
  - `eopf` is pinned to **2.8.1** to match the SDE `cpm-build-environment` image; it is not
    upgraded (a version change would desynchronise the build environment and break CI).
  - **Code is public; raw input data and calibration are private** — they are never committed
    and never used in public CI. Numerical verification on real data is performed locally.
  - The CI runner is a **shell executor** (no container runtime, no Dask gateway, no S3 in
    CI); jobs requiring those tools are non-blocking (`allow_failure`) until a Kubernetes
    runner is available.

### <4.4> Work breakdown structure

Top-level work packages (WP), in execution order:

| WP | Title | Milestone |
|---|---|---|
| WP-1 | Project setup (repository, CI, runner, milestones) | (pre-SRR, done) |
| WP-2 | SRR documentation (SDP, SRevP, SPAP, Risk Register, SSS, IRD) | SRR |
| WP-3 | PDR documentation (SRS, SVerP, SValP, ICD, DPM, ATBD, preliminary SDD) | PDR |
| WP-4 | CDR documentation (detailed SDD+DJF, SUITP, SRF, traceability matrix) | CDR |
| WP-5 | Implementation — processing units L0→L2 (per design) | post-CDR |
| WP-6 | Verification & validation (SVR, SUITR), release (SRelD/SRN), SUM | QR / AR |

Detailed activities are managed as GitLab issues assigned to the corresponding milestone.

### <4.5> Risk management

The software engineering function contributes to project risk management per ECSS-M-ST-80.
Risks are recorded and maintained in the **Risk Register** (`compliance/drd/risk-register.md`),
reviewed at each milestone.

### <4.6> Monitoring and controlling mechanisms

Work is monitored through: GitLab milestones and issues (progress), merge requests (change
control and review), and the CI pipeline status (quality gates). Each documentation/work item
is a merge request linked to its milestone, giving an auditable progress trail.

### <4.7> Staffing plan

Single-developer project (project owner acting as supplier-side software, PA and verification
roles). Independence of verification is achieved by automated tooling and explicit review
checklists rather than separate staff; this is consistent with the Category C tailoring (§5.6).

### <4.8> Software procurement process

No software is procured. All third-party software is open-source reuse (EOPF CPM and its
dependencies, scientific Python stack); the reuse declaration and licences are recorded in the
**SRF**. Therefore the procured-software list is empty.

### <4.9> Supplier management

Not applicable beyond §4.8 — there are no subcontracted software suppliers.

## <5> Software development approach

### <5.1> Strategy to the software development

The overall strategy is **documentation-first systems engineering followed by incremental
implementation**: the requirements, interfaces, data processing model, algorithm basis and
design are baselined through SRR → PDR → CDR **before** code is written; implementation
(WP-5) starts only after CDR. Each processing stage is then implemented incrementally as a
CPM `EOProcessingUnit` (pure, unit-testable core + thin PU wrapper), integrated and verified
against its requirement before the next stage. Git history therefore mirrors the engineering
order.

### <5.2> Software project development life cycle

#### <5.2.1> Software development life cycle identification

The life-cycle paradigm is **incremental**, synchronised by the formal ECSS reviews. Software
versioning follows **semantic versioning** with Git tags; the configuration item is the `main`
branch of the Git repository (see SCF). The SDP covers the implementation of all relevant
software processes: system-related, requirements & architecture, design & implementation,
validation, verification, delivery & acceptance, operation, maintenance, and management.

#### <5.2.2> Relationship with the system development cycle

The processor is a ground-segment software product. Its life cycle is phased to the standard
EO ground-segment process model; the milestones below are the synchronisation points.

#### <5.2.3> Reviews and milestones identification and associated documentation

Reviews are implemented as **GitLab group milestones** (group `ipf`). Each review baselines
the documents listed (see §5.5 for the full tailored DRL and Annex Q for content-per-review):

| Review | Scope / purpose | Baselined documents |
|---|---|---|
| **SRR** | System & management baseline | SDP, SRevP, SPAP, Risk Register, SSS, IRD |
| **PDR** | Software requirements + V&V plans + preliminary design | SRS, SVerP, SValP, ICD (start), DPM, ATBD, preliminary SDD |
| **CDR** | Detailed design + test/reuse | SDD (+DJF), SUITP, SRF, ICD (final), Traceability matrix |
| **QR** | Qualification | SVR, SUITR, SRelD/SRN, SUM (start), CIDL/SCF |
| **AR** | Acceptance | SUM (final), SRelD, SMP |

Level of formalism: reviews are conducted as documented, checklist-based merge-request reviews
(proportionate to a single-developer Category C project; see SRevP). Implementation begins
after CDR.

### <5.3> Software engineering standards and techniques

- **Methodologies/standards:** ECSS-E-ST-40C Rev.1 (engineering) and ECSS-Q-ST-80C Rev.2 (PA),
  tailored for Category C (§5.6). Coding follows PEP 8 enforced by `black`/`ruff`/`flake8`.
- **Requirements analysis method:** textual, uniquely-identified requirements (`REQ-*`) with
  forward/backward traceability (see SRS and Traceability matrix).
- **Design method:** EOPF CPM processing-unit architecture — pure-function core + thin
  `EOProcessingUnit` wrapper, with mandatory inputs/ADFs/outputs/parameters declared in CPM
  computing-model JSON; sensor-specific behaviour externalised to a sensor-profile layer.
- **Auto-code generation:** none.
- **Delivery format:** Python package + container image + Zarr product specification (see SRelD).

### <5.4> Software development and software testing environment

- **Language:** Python 3.11. **Dependency/build:** `uv` / `flit`; environment pinned via
  `pyproject.toml` (`eopf == 2.8.1`).
- **Build image:** `registry.eopf.copernicus.eu/sde/cpm-build-environment:latest` (provides CPM).
- **CI/CD:** GitLab CI on the EOPF SDE; self-hosted shell runner on the Studio VM.
- **Quality/static analysis tools:** `flake8`, `black`, `isort` (style); `mypy` (typing);
  `bandit` + `trivy` (security); `xenon` (complexity); `SonarQube` (quality gate);
  `pytest` + coverage (test).
- **Documentation:** Sphinx → GitLab Pages.
- **Note:** tools requiring a container runtime / Dask gateway / S3 are not available on the
  shell runner and are configured non-blocking until a Kubernetes runner lands.

### <5.5> Software documentation plan

#### <5.5.1> General

All project documentation follows the ECSS-E-ST-40C Rev.1 DRDs (engineering) and
ECSS-Q-ST-80C Rev.2 (PA), tailored for Category C. Formal DRD deliverables are authored in
`compliance/` (authoritative) and the EOPF SDE-rendered subset is published from `docs/`
(Sphinx/Pages). The two are kept consistent.

#### <5.5.2> Software documentation identification — tailored DRL

For each document: file location, document name, the review at which it is delivered, and the
tailoring decision (**PRODUCE** / **REUSE** / **TAILORED-OUT**). Tailoring is per Annex R for
Category C.

**ECSS-E-ST-40C (engineering)**

| DRD | Annex | Decision | Delivered | File |
|---|---|---|---|---|
| SSS — Software System Specification | B | PRODUCE (light) | SRR | `compliance/drd/sss-software-system-specification.md` |
| IRD — Interface Requirements Document | C | PRODUCE | SRR | `compliance/drd/ird-interface-requirements.md` |
| SRS — Software Requirements Specification | D | PRODUCE | PDR | `compliance/drd/srs-software-requirements.md` |
| ICD — Interface Control Document | E | PRODUCE | PDR/CDR | `compliance/drd/icd-interface-control.md` + `docs/icd.md` |
| SDD — Software Design Document | F | PRODUCE | CDR | `compliance/drd/sdd-software-design.md` + `docs/sdd/` |
| DPM — Data Processing Model | (EOPF) | PRODUCE | PDR | `docs/dpm/` |
| ATBD — Algorithm Theoretical Basis | (EO) | PRODUCE | PDR | `docs/atbd/` |
| SRelD — Software Release Document | G | PRODUCE (light) | QR/AR | `docs/srn.md` + GitLab Releases |
| SUM — Software User Manual | H | PRODUCE | QR/AR | `docs/sum/` |
| SVerP — Software Verification Plan | I | PRODUCE (merged) | PDR | `compliance/drd/vv-plan.md` |
| SValP — Software Validation Plan | J | PRODUCE (merged) | PDR | `compliance/drd/vv-plan.md` |
| SUITP — Unit/Integration Test Plan | K | PRODUCE (merged) | CDR | `compliance/drd/vv-plan.md` |
| SVS — Software Validation Specification | L | REUSE | — | test suite + V&V plan |
| SVR — Software Verification Report | M | PRODUCE | QR | `compliance/drd/vv-report.md` |
| SRF — Software Reuse File | N | PRODUCE | CDR | `compliance/drd/srf-software-reuse-file.md` + `docs/srf.md` |
| SDP — Software Development Plan | O | PRODUCE | SRR | *this document* |
| SRevP — Software Review Plan | P | PRODUCE (light) | SRR | `compliance/drd/srevp-software-review-plan.md` |
| SMP — Software Maintenance Plan | T | TAILORED-OUT (light) | AR | maintenance = GitLab issues + SemVer; noted in SRS |

**ECSS-Q-ST-80C (product assurance) and cross-discipline**

| Artefact | Decision | Delivered | File |
|---|---|---|---|
| SPAP — SW Product Assurance Plan | PRODUCE (light) | SRR | `compliance/drd/spa-plan.md` |
| Risk Register (M-ST-80) | PRODUCE | SRR | `compliance/drd/risk-register.md` |
| Traceability matrix (E-40 §5.8) | PRODUCE | CDR | `compliance/traceability/traceability-matrix.md` |
| CIDL — Configuration Item Data List | PRODUCE (light) | QR | `docs/cidl.md` |
| SCF — Software Configuration File | PRODUCE (light) | QR | `docs/scf.md` |

#### <5.5.3> Deliverable items

Deliverable items: the documentation set above; the software package (`msi_processor`); the
container image; and the Zarr product specification. Internal vs deliverable status, sender/
receiver, perimeter, maturity and known limitations of each delivery are recorded in the SRelD.

#### <5.5.4> Software documentation standards

Documents are authored in Markdown (CommonMark/MyST), rendered with Sphinx. Each formal DRD
document states its DRD reference and follows the corresponding Annex section structure. Any
tailoring of a DRD's content is recorded in that document's header.

### <5.6> This Standard's tailoring traceability

The applicable tailoring of ECSS-E-ST-40C clause 5 is derived from **Annex R for software
criticality Category C**. Rationale for the classification: a failure of `msi-processor`
produces degraded or incorrect data products only — it has no safety, mission-loss or
space-segment consequence and is recoverable by reprocessing — which corresponds to a *major*
severity, i.e. Category C.

The **document-level** tailoring (DRL) is given in §5.5.2. The detailed **clause-by-clause**
coverage matrix of ECSS-E-ST-40C clause 5 (each requirement: applied / tailored / N/A with
rationale) is maintained in `compliance/gap-analysis.md` and referenced here. TAILORED-OUT
items with rationale: SMP (light — GitLab issues + SemVer); SPAMR (no formal PA milestone
reports — subsumed by SVR and the milestone reviews).

---

*End of SDP. Authored per ECSS-E-ST-40C Rev.1 Annex O.*
