# Risk Register

| | |
|---|---|
| **Document** | Risk Register |
| **DRD** | No dedicated DRD — risk attributes per ECSS-M-ST-80C (risk management); contributes to SDP §4.5 |
| **Container** | Management File (MGT) |
| **Project** | `msi-processor` — generic high-resolution MSI data processor |
| **Configuration item** | `gitlab.eopf.copernicus.eu/ipf/msi-processor` |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | SRR |
| **Status** | Draft for SRR |

> This Risk Register is the software engineering function's contribution to project risk
> management (SDP §4.5). It records, assesses and tracks the risks of the `msi-processor`
> project using the ECSS-M-ST-80C risk attributes (likelihood A–E, severity 1–5, risk
> index/magnitude, treatment, owner, status, trend). It is established at SRR and reviewed at
> every subsequent milestone (PDR, CDR, QR, AR). The scope is the software engineering risks
> of a Category C, single-developer ground-segment processor; it is proportionate to that
> footprint and does not duplicate the project-level (programmatic) risk management of the
> `ipf` group.

## <1> Introduction

The purpose of this register is to identify the risks that can affect the correct, on-time and
standards-conformant delivery of `msi-processor`, to assess their likelihood and severity, to
record the treatment (mitigation) and the responsible owner, and to track their evolution
across the life cycle. Risk management for this project is *operational, not bureaucratic*:
each risk that is rated High has a concrete mitigation action tracked in GitLab, and the
register is re-assessed at each review.

The risks below derive from the project's defining constraints (recorded in SDP §4.3):
the `eopf == 2.8.1` pin against an SDE build image tagged `latest`; a CI **shell executor**
with no container runtime, Dask gateway or S3; a **public code / private data** policy that
forbids raw and calibration data from CI; and a **single-developer** organisation in which
verification independence must be achieved by tooling rather than by separate staff.

## <2> Applicable and reference documents

Risk management follows **ECSS-M-ST-80C** (Space project management — Risk management) for the
attribute set and scoring approach, and **ECSS-M-ST-10C Rev.1** (AD-3) for the programmatic
context. The full applicable/reference document list is in **SDP §2**; the documents directly
relevant here are:

| Ref | Document |
|---|---|
| AD-3 | ECSS-M-ST-10C Rev.1 — Project planning and implementation |
| — | ECSS-M-ST-80C — Risk management (attribute set / scoring scheme) |
| RD-1 | EOPF SDE — User Manual & Guidelines (build image, runner) |
| RD-2 | EOPF CPM documentation (`eopf == 2.8.1`) |
| SDP | Software Development Plan — §4.3 (constraints), §4.5 (risk management), §4.7 (staffing) |

## <3> Risk management process

The process implements the ECSS-M-ST-80C cycle, tailored to a single-developer Category C
project:

1. **Identification** — risks are captured from the project constraints, the engineering plan
   and milestone reviews. Each risk is recorded as a GitLab issue with the `~Risk` label
   (issue template `Risk.md`) and mirrored in this register.
2. **Assessment** — each risk is scored for **likelihood** (A–E, §4.1) and **severity** (1–5,
   §4.2); the **risk index/magnitude** (Low / Medium / High) is read from the matrix in §4.3,
   taking existing controls into account.
3. **Decision & treatment** — a treatment strategy is selected (ECSS-M-ST-80C): *Reduce*
   (mitigate), *Accept* (tolerate a constraint), *Watch* (monitor), *Avoid* or *Transfer*.
   Risks rated **High** must have at least one linked mitigation **action** (`~Action` issue);
   actions for Medium/Low risks are recommended, not mandatory.
4. **Monitoring & control** — the register is reviewed at every milestone (SRR → PDR → CDR →
   QR → AR). Each review updates likelihood/severity, status and **trend**, and adds or closes
   risks. Change control is via merge request, consistent with SDP §4.6.

## <4> Scoring scheme

### <4.1> Likelihood (A–E)

| Score | Level | Interpretation for this project |
|:---:|---|---|
| **E** | Maximum | Near-certain to occur within the project life cycle |
| **D** | High | Likely to occur |
| **C** | Medium | May occur |
| **B** | Low | Unlikely but credible |
| **A** | Minimum | Very unlikely |

### <4.2> Severity of consequences (1–5)

The scale combines the **technical/quality**, **schedule/cost** and **confidentiality**
consequence domains. Note the Category C classification (SDP §5.6): a *software failure* of
`msi-processor` produces only degraded or incorrect data products, recoverable by reprocessing
— i.e. its technical severity does not exceed **Major (3)**. Higher scores (4–5) are reserved
for *project* consequences that are not software-failure consequences: loss of the core
capability/schedule (4) and irreversible disclosure of private data (5).

| Score | Level | Interpretation |
|:---:|---|---|
| **5** | Catastrophic | Project failure, or irreversible disclosure of private raw/calibration data |
| **4** | Critical | Core processing capability blocked; major rework; significant schedule slip |
| **3** | Major | Degraded/incorrect data products or a verification gap; recoverable by reprocessing |
| **2** | Significant | Limited, localised impact; minor rework |
| **1** | Negligible | Minimal impact |

### <4.3> Risk index / magnitude matrix

The risk index is the magnitude read from the severity × likelihood matrix (L = Low,
M = Medium, H = High):

| Severity \ Likelihood | A | B | C | D | E |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **5** | M | H | H | H | H |
| **4** | M | M | H | H | H |
| **3** | L | M | M | H | H |
| **2** | L | L | M | M | H |
| **1** | L | L | L | M | M |

**Acceptance criteria:** **High** = not acceptable; requires an active mitigation action and is
reported at the next review. **Medium** = acceptable while monitored and mitigated. **Low** =
acceptable; monitored only.

## <5> Risk register

Likelihood (L) and severity (S) columns give the **current assessed** value (with existing
controls applied); the *strategy* tag and text give the treatment. Owners are project roles
(§6) — all held by the single project owner per SDP §4.7. Trend is measured against the
previous review; at this first (SRR) baseline all entries are **New (N)**.

| ID | Risk (area) | L | S | Index | Mitigation / treatment | Owner | Status | Trend |
|---|---|:---:|:---:|:---:|---|:---:|---|:---:|
| R-01 | **`eopf==2.8.1` pin vs SDE build-image drift.** The CPM build image is tagged `latest`; an SDE upgrade can desynchronise the pinned `eopf` from the image and break builds/CI. | C | 3 | **M** | *Reduce* — pin to image digest where the SDE allows; CPM access isolated behind a thin wrapper (R-05); CI smoke test against the pinned env; monitor RD-1 release notes; any forced `eopf` bump handled as a controlled change (MR + re-baseline). | Eng | Monitored | N |
| R-02 | **Shell-runner limitations block automated verification.** The CI shell executor has no container runtime, Dask gateway or S3, so integration/distributed/object-store verification cannot run in public CI. | D | 3 | **H** | *Accept + Reduce* — affected jobs set `allow_failure: true` (non-blocking); equivalent verification performed locally with evidence recorded in the SVR (`compliance/drd/vv-report.md`); migration to a Kubernetes/Dask-gateway runner tracked as an action. | V&V | Accepted | N |
| R-03 | **Private-data-only verification, no public reference (L0→L1).** Raw L0 and calibration are private; there is no public reference product and no second verifier, so radiometric/geometric correctness cannot be independently checked in CI. | C | 4 | **H** | *Reduce* — deterministic synthetic fixtures (non-sensitive) drive golden tests in public CI; local numerical verification on real data with checksummed reference outputs logged in the SVR; cross-check against an open reference processor (e.g. SNAP/ESA L1) where a comparable product exists; independence via automated gates + documented review checklists (SRevP). | V&V | Open | N |
| R-04 | **Instrument calibration availability/quality.** Missing, late or low-quality calibration ADFs (gain/offset, dark, flat-field) prevent or corrupt radiometric correction; flat-field defects can produce subtly wrong L1. | B | 4 | **M** | *Reduce* — acquire calibration ADFs early; ADF sanity checks (range, NaN, dead-pixel maps) before use; synthetic calibration ADFs for unit/pipeline tests; record calibration provenance/version in product metadata and the SCF. | Eng | Open | N |
| R-05 | **CPM API stability.** EOPF CPM (`EOProcessingUnit`/`EOProduct`) interfaces evolve across `eopf` versions; an API change could invalidate the design. | B | 3 | **M** | *Reduce* — pin `eopf==2.8.1`; concentrate CPM usage in a thin PU wrapper/adapter (per SDD) so the core is framework-agnostic; integration tests bound to the pinned API; review the CPM changelog before any upgrade. | Eng | Mitigated | N |
| R-06 | **Atmospheric L2 is genuinely new development.** Unlike L0→L1 (algorithm heritage via SRF), L2 atmospheric correction has no prior heritage, raising correctness and schedule uncertainty. | D | 3 | **H** | *Reduce* — author the L2 ATBD at PDR (`docs/atbd/`); base L2 on an established radiative-transfer model / LUT (e.g. 6S, libRadtran) rather than a novel algorithm; prototype early and schedule L2 as the final increment; define explicit L2 acceptance criteria in the SValP with schedule margin. | Eng | Open | N |
| R-07 | **Public-code / private-data (or secret) leakage.** Accidental commit of raw data, calibration or credentials to the public repository is irreversible disclosure. | B | 5 | **H** | *Reduce* — data/calibration never committed (enforced `.gitignore`); pre-commit secret/data scanning (`gitleaks`/`detect-secrets`); CI `bandit` + `trivy`; MR checklist item "no data/secrets"; private data kept outside the repository tree. | PA | Mitigated | N |
| R-08 | **Single-developer bus factor / verification independence.** One person holds all knowledge and all roles; unavailability halts the project, and verification independence is tooling-based only. | C | 3 | **M** | *Reduce* — documentation-first (all design, decisions and rationale auditable in Git); public repo lowers the pickup barrier; automated quality gates + explicit review checklists substitute for a second verifier; SemVer + GitLab issues for continuity (SMP-light). | PM | Open | N |
| R-09 | **Geometric-correction auxiliary data.** Orthorectification depends on DEM and orbit/attitude (and GCPs); poor availability or accuracy degrades geolocation. | C | 3 | **M** | *Reduce* — use open auxiliary data (Copernicus DEM, public orbit/attitude) where possible; document aux-data sources and accuracy in the DPM/ICD; bound geolocation residuals against GCPs; expose aux-data accuracy in product quality metadata. | Eng | Open | N |
| R-10 | **EOPF Zarr product-format conformance.** Output Zarr that does not conform to EOPF `EOProduct` conventions reduces interoperability. | B | 2 | **L** | *Watch* — validate outputs against the CPM `EOProduct` schema / EOPF product conventions (RD-2); add a conformance test in CI. | Eng | Open | N |
| R-11 | **Schedule/scope risk of the documentation-first plan.** A single developer carrying SRR→AR with a five-milestone documentation tree may slip, especially around the new L2 work (R-06). | C | 2 | **M** | *Reduce* — Category C tailoring keeps the footprint small (merged V&V docs, light DRDs per SDP §5.5.2); milestone + issue tracking; documentation-first reduces late rework; L2 scheduled as the final increment. | PM | Open | N |

## <6> Risk owners

All roles are held by the single project owner (SDP §4.7); the role attribution below shows
under which discipline each risk is managed, supporting the tooling-based separation of duties.

| Owner code | Role |
|---|---|
| **Eng** | Software engineering (design, implementation, data/algorithm integration) |
| **PA** | Software product assurance (security, configuration, data policy) |
| **V&V** | Verification & validation |
| **PM** | Project management (schedule, scope, continuity) |

## <7> Summary and top exposures

- **Risk profile at SRR:** 4 High, 6 Medium, 1 Low (11 risks).
- **Top exposures (High):**
  - **R-02 — shell-runner verification gap:** the top *operational* risk; accepted as a known
    constraint and compensated by local verification + `allow_failure`, pending a Kubernetes
    runner.
  - **R-03 — private-data-only / no public reference:** the top *assurance* risk; the binding
    challenge for verification independence and auditable correctness of L0→L1.
  - **R-06 — new L2 development:** the top *technical/schedule* risk; the only stage without
    algorithm heritage.
  - **R-07 — data/secret leakage:** low likelihood but catastrophic severity (irreversible);
    kept High by severity and held down by preventive controls.
- **Watch items:** R-01 (build-image drift) and R-04 (calibration) can escalate quickly if the
  SDE image or the calibration supply changes; both are monitored at each review.

## <8> Tooling and traceability

Risks are maintained both here (authoritative, baselined per review) and as GitLab issues:

- Each risk is a GitLab issue labelled `~Risk` (template `.gitlab/issue_templates/Risk.md`),
  carrying the rating label `~Risk::Rating::{Low|Medium|High}`.
- High-rated risks (R-02, R-03, R-06, R-07) carry at least one linked mitigation `~Action`
  issue (`/relate`), per the issue template and §3.
- The GitLab template's simplified 3×3 scheme (Probability 1–3 × Severity 1–3 → Low/Medium/
  High) maps onto this register's ECSS 5×5 scheme as follows: the **Index** column (§4.3) is
  authoritative, and the GitLab `Rating` label mirrors it band-for-band (Low/Medium/High).
- Mitigation evidence (test runs, local verification, scan results) is recorded against the
  SVR (`compliance/drd/vv-report.md`) and the CI pipeline status (SDP §4.6).

## <9> Review and maintenance

The register is re-assessed at every milestone review (SRR, PDR, CDR, QR, AR). Each review:
updates L/S, Index, Status and Trend; opens risks for newly identified exposures (notably new
L2/atmospheric risks expected at PDR/CDR); and closes risks whose conditions no longer apply.
Status values: **Open** (no controls yet), **Mitigated** (controls in place, residual
acceptable), **Accepted** (tolerated constraint), **Monitored** (watched, no action due),
**Closed**. Trend values: **N** (new), **↑** (worsening), **→** (stable), **↓** (improving).

---

*End of Risk Register. Risk attributes per ECSS-M-ST-80C; contributes to SDP §4.5.*
