# Software Review Plan (SRevP)

| | |
|---|---|
| **Document** | Software Review Plan (SRevP) |
| **DRD** | ECSS-E-ST-40C Rev.1, Annex P |
| **Container** | Design Justification File (DJF) |
| **Project** | `msi-processor` — generic high-resolution MSI data processor |
| **Configuration item** | `gitlab.eopf.copernicus.eu/ipf/msi-processor` |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | SRR |
| **Status** | Draft for SRR |

> This SRevP follows the ECSS-E-ST-40C Rev.1 Annex P DRD section structure. Annex P is written
> for the plan of a *single* review; for a Category C, single-developer project this DRD is
> tailored into **one project-level review plan** that covers the complete set of formal
> milestone reviews (SRR, PDR, CDR, QR, AR) and the continuous merge-request (MR) reviews and CI
> quality gates that act as the day-to-day technical-review mechanism. It is consistent with the
> SDP (`compliance/software-development-plan.md`, §5.2.3 and §5.5.2) and reuses its applicable
> documents, terms and tailored DRL.

## <1> Introduction

This Software Review Plan (SRevP) describes the **purpose, objectives, content and conduct of
the reviews** of the `msi-processor` software, in accordance with ECSS-E-ST-40C Rev.1 Annex P
and ECSS-M-ST-10-01C, tailored for software criticality Category C.

The processor is a **generic high-resolution pushbroom MSI ground-segment data processor**
(downlinked Level-0 → Level-2: radiometric, geometric and atmospheric correction), built on the
ESA EOPF Core Python Modules (each stage an `EOProcessingUnit`, products as `EOProduct`, outputs
as Zarr; `eopf == 2.8.1`). It is an **integration and ECSS-productisation** effort over existing
algorithm heritage, not new-algorithm research.

**Purpose.** The SRevP establishes a single, repeatable review approach so that, at every life-cycle
transition, the maturity and correctness of the work products are objectively assessed, dispositioned
and baselined before the next phase is authorised — and so that this assessment is auditable from the
GitLab history.

**Objective.** To define, for each review: its scope, objectives and level of formalism; the data
package subject to review; the entry and success criteria; the review process and schedule; the
participants and their level of independence; and the mechanism for raising, dispositioning and
closing Review Item Discrepancies (RIDs).

**Content.** This document covers the standards basis (<2>, <3>), the reviews and the product stage at
each (<4>, <5>), per-review objectives and level of formalism (<6>), expected results (<7>), the review
process including the continuous MR/CI technical-review mechanism (<8>), the schedule (<9>), the
documentation subject to review (<10>), participants and independence (<11>), logistics (<12>) and the
RID form (<13>).

**Reason prompting preparation.** The SRevP is a constituent of the Design Justification File and is a
mandatory SRR deliverable in the tailored DRL (SDP §5.5.2). It is prepared at project start to fix the
review approach **before** any document is baselined or any code is written (implementation begins only
after CDR).

## <2> Applicable and reference documents

**Applicable documents** (consistent with SDP §2)

| Ref | Document |
|---|---|
| AD-1 | ECSS-E-ST-40C Rev.1 (30 April 2025) — Space engineering — Software |
| AD-2 | ECSS-Q-ST-80C Rev.2 (30 April 2025) — Space product assurance — Software product assurance |
| AD-3 | ECSS-M-ST-10C Rev.1 — Space project management — Project planning and implementation |
| AD-4 | ECSS-M-ST-10-01C — Space project management — Organization and conduct of reviews |
| AD-5 | ECSS-M-ST-40C — Configuration and information management |

**Reference documents**

| Ref | Document |
|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) — `compliance/software-development-plan.md` |
| RD-2 | ECSS-E-ST-40C Rev.1 Annex Q — Document organization and contents at each review |
| RD-3 | ECSS-E-ST-40C Rev.1 Annex R — Tailoring based on software criticality |
| RD-4 | EOPF Software Development Environment (SDE) — User Manual & Guidelines |

## <3> Terms, definitions and abbreviated terms

Terms and definitions follow AD-1, AD-2, AD-4 and the SDP §3 glossary. Additional abbreviations used
in this document and not defined there:

| Abbreviation | Definition |
|---|---|
| CI | Continuous Integration (GitLab CI pipeline / quality gates) |
| DMA | Decision-Making Authority (authorises transition to the next phase) |
| KOM | Kick-Off Meeting (of a review) |
| MR | Merge Request (GitLab unit of change and continuous review) |
| RID | Review Item Discrepancy (a comment/finding raised against a review item) |
| RG | Review Group (the participants performing the review) |

ECSS review acronyms used: **SRR** (System Requirements Review), **PDR** (Preliminary Design Review),
**CDR** (Critical Design Review), **QR** (Qualification Review), **AR** (Acceptance Review). Anticipated
sub-reviews of E-ST-40C (SWRR, DDR, TRR, TRB, SW-DRB) are tailored into their parent milestone (see <6>).

## <4> Review title and project

### <4.1> Exact name

This SRevP governs the following reviews of the `msi-processor` configuration item:

| ID | Exact name | Type |
|---|---|---|
| SRR | Software System Requirements Review | Formal milestone review (GitLab group `ipf` milestone) |
| PDR | Software Preliminary Design Review | Formal milestone review (incl. anticipated SWRR objectives) |
| CDR | Software Critical Design Review | Formal milestone review (incl. anticipated DDR objectives) |
| QR | Software Qualification Review | Formal milestone review (incl. anticipated TRR/TRB objectives) |
| AR | Software Acceptance Review | Formal milestone review (incl. anticipated SW-DRB objectives) |
| MR-R | Continuous merge-request review | Per-change technical review (every MR to `main`) |

### <4.2> System or product subject to review

The product under review is the `msi-processor` software configuration item (the `main` branch of
`gitlab.eopf.copernicus.eu/ipf/msi-processor`) and its associated ECSS documentation set. The expected
development stage at each review is:

| Review | Product / development stage expected at the review |
|---|---|
| SRR | System & management baseline established; no code. System specification (SSS), interface requirements (IRD) and management plans (SDP, SRevP, SPAP, Risk Register) drafted. |
| PDR | Software requirements (SRS), V&V plans, interfaces (ICD start), data-processing model (DPM), algorithm basis (ATBD) and **preliminary** software architecture (SDD) established; still no production code. |
| CDR | **Detailed** design baselined (SDD + DJF), unit/integration test plan, reuse file (SRF), final ICD and traceability matrix complete. Implementation is authorised only at CDR exit. |
| QR | Software implemented, integrated and qualified against the technical specification; verification (SVR) and unit/integration test results (SUITR) available; release candidate produced. |
| AR | Software validated against the Requirements Baseline; acceptance data package, final SUM and release (SRelD/SRN) ready for hand-over/operation. |
| MR-R | Any single change (documentation or, post-CDR, code) proposed via an MR against `main`. |

## <5> Reference documents

The project documentation applicable to the reviews is the tailored DRL of SDP §5.5.2. The full
**documentation subject to review** (per review) is detailed in <10> of this SRevP; the **content
expected per review** follows AD-1 Annex Q (RD-2). Each review data package shall be assembled from the
deliveries due at that milestone in the SDP DRL (SDP §5.2.3).

## <6> Review objectives

Each review verifies the maturity of the corresponding life-cycle outputs, baselines them, and decides
whether the project may proceed. Objectives below are tailored from AD-1 Annex P (NOTES 1–11) for a
Category C, single-developer project; anticipated sub-reviews are folded into their parent.

**Level of formalism (per review).** All reviews are conducted as **documented, checklist-based,
asynchronous reviews on the GitLab platform** — there is no physical review board. Formalism is graded:

| Review | Scope | Level of formalism |
|---|---|---|
| SRR | System/requirements & management baseline | Documented milestone review; checklist; RG = owner + (optional) EOPF SDE reviewer; DMA sign-off recorded in the milestone summary issue. |
| PDR | Requirements + V&V plans + preliminary design | Documented milestone review; checklist; same RG; technical-budget/margins check. |
| CDR | Detailed design + test/reuse; authorises coding | **Highest-rigour** milestone review (design-freeze gate); checklist; mandatory traceability and SRF check. |
| QR | Qualification vs technical specification | Documented milestone review; CI verification evidence (tests, coverage, static gates) is primary input. |
| AR | Acceptance vs Requirements Baseline | Documented milestone review; acceptance data package check; release authorisation. |
| MR-R | Single change | Lightweight continuous review: MR checklist + green CI quality gates; self-review against checklist, automation provides independence. |

**SRR objectives**

- Confirm that all requirements captured in the Requirements Baseline (SSS, IRD) are understood and
  agreed; **release the Requirements Baseline**.
- Check the suitability of the draft SDP and its planning elements (SRevP, SPAP, Risk Register).
- Verify the consistency of the software planning with the upper-level ground-segment plan.
- Ensure software product-assurance activities are defined (SPAP).
- Evaluate readiness to proceed to PDR.

**PDR objectives** (includes anticipated Software Requirements Review, SWRR)

- Agree that all Requirements-Baseline requirements are captured in the technical specification (SRS);
  **release the SRS** and the ICD (start).
- Verify and **release** the software development, verification and validation approaches and their
  plans (SVerP/SValP — the merged V&V plan), and the PA approach.
- **Release** the preliminary software architecture (SDD), the DPM and the ATBD.
- Verify technical budgets and margins estimates; check the integration strategy.
- Evaluate the potential reuse of software (SRF preliminary) and known unsolved issues with major impact.
- Verify quality-assurance reports; evaluate readiness to proceed to CDR.

**CDR objectives** (includes anticipated Detailed Design Review, DDR)

- **Baseline the detailed design** (SDD + DJF), including verification reports and technical-budget report.
- Check the adequacy of the software-unit and integration plans and of the unit/integration test
  procedures (SUITP).
- Review and baseline the validation approach (SValP) and **release the SRF**.
- Verify the feasibility of integration and testing; evaluate reuse and known unsolved issues.
- Verify quality-assurance reports; evaluate readiness to **begin implementation** (the design-freeze gate).

**QR objectives** (includes anticipated Test Readiness Review / Test Review Board, TRR/TRB)

- Verify that the software meets all of its specified requirements and that verification and validation
  processes (per the V&V plan) have completed successfully.
- Verify that all Requirements-Baseline and interface requirements have been validated and verified,
  including technical budgets and **code coverage** (EOPF coverage gate).
- Verify that the Software Configuration Item under review is a formal version under configuration
  control (Git tag / SCF / CIDL); **release the software release document** (SRelD/SRN).
- Confirm the test/RB-validation configuration; check the status of all SPRs/NCRs; baseline the
  validation specification against the RB; evaluate readiness to proceed to AR.

**AR objectives** (includes anticipated Software Delivery Review Board, SW-DRB)

- Assess the acceptance-test results (including as-run procedures) and verify the complete set of
  acceptance cases ran on the same software version.
- Verify the Software Configuration Item is a formal version under configuration control; verify all RB
  software requirements were validated and verified throughout the life cycle.
- Check the software acceptance data package; verify the SRelD, installation procedure/report and the
  maintenance approach; verify the **final SUM**.
- Evaluate known unsolved issues and confirm correct closure of major SPRs/NCRs; **accept the software
  product**; verify quality-assurance reports.

**MR-R (continuous review) objectives**

- Verify that the change is correct, traceable to a requirement/issue, and consistent with the current
  baseline and the EOPF CPM design pattern.
- Confirm all CI quality gates pass (lint/format, typing, complexity, security, tests/coverage) before
  merge — the gates are the automated technical-review mechanism that supplies verification independence.

## <7> Expected results

For every review the SRevP defines entry criteria, success criteria, a conclusion and a review report.

**1. Review entry criteria**

- (a) The review data package (the documents/deliveries of <10> for that review) is complete and pushed
  to its review branch / linked from the milestone.
- (b) The review group, the process and the schedule are agreed; for MR-R, the MR is open with CI run
  and the MR checklist attached.

**2. Review success criteria**

- (a) The review objectives (<6>) for that review are met.
- (b) Actions agreed to be closed before this review have been closed.
- (c) RIDs agreed to be closed before this review have been closed.
- (d) RIDs raised at this review are dispositioned and any resulting actions are assigned (as GitLab issues).
- (e) For MR-R: all required CI quality gates are green (or every non-blocking job is justified in the MR).

**3. Review conclusion** — recorded in the milestone summary issue (or the MR decision), one of:

- **Successful** — success criteria met; authorisation to proceed to the next phase is granted (milestone
  closed / MR merged).
- **Successful with rework** — success criteria partially met; pending corrections are tracked as open
  SPRs/actions with agreed closure dates; authorisation to proceed is granted (milestone closed with
  follow-up issues / MR merged with linked follow-up issues).
- **Not successful** — success criteria not met; documents at the review are **not** baselined and software
  is not released for follow-on use in its current state; authorisation to proceed is **not** granted
  (milestone stays open / MR `Changes requested`).

**4. Review report** — for milestone reviews, a **milestone summary issue** containing: the review minutes
(the MR/issue discussion threads), the RID status metric (opened/closed/dispositioned), the dispositioned
RIDs, the actions raised, the conclusion, and links to the baselined artefacts (Git tag / MR merge
commits). For MR-R, the merged MR thread and its CI run constitute the report.

## <8> Review process

The project operates a **two-tier review process** on the GitLab platform; there are no physical meetings.

**Tier 1 — Continuous technical review (MR-R + CI quality gates).** Every change to `main` is proposed as
a Merge Request and is the unit of technical review. Each MR uses the repository MR template
(`.gitlab/merge_request_templates/default.md`) and must pass the CI quality gates defined in the SDP
(§5.4): `flake8`/`black`/`isort` (style), `mypy` (typing), `xenon` (complexity), `bandit`/`trivy`
(security), SonarQube (quality gate), and `pytest` + coverage (test). The green pipeline is the automated,
independent technical-review evidence; the MR checklist is the human technical review. Findings are raised
as MR comments (lightweight RIDs); blocking findings hold the merge. Jobs that cannot run on the shell
runner (container runtime / Dask gateway / S3) are non-blocking (`allow_failure`) and their status is
noted in the MR rather than gating it.

**Tier 2 — Formal milestone review (SRR/PDR/CDR/QR/AR).** Each milestone aggregates the MRs of its phase
and reviews the assembled data package against <6>/<7>. The complete review process, mapped to GitLab
mechanics, is:

1. **Review planning** — milestone created on group `ipf`; data-package list confirmed from <10>.
2. **Participants invitation and confirmation** — RG members (and any optional external EOPF SDE reviewer)
   assigned to the milestone summary issue.
3. **Kick-off (KOM)** — opening note in the milestone summary issue (scope, objectives, checklist).
4. **Data-package readiness check** — verify all deliveries of <10> are present and CI-clean.
5. **Data-package presentation** *(optional)* — summary in the milestone issue; no live session required.
6. **Data-package distribution** — review branch(es) / rendered docs linked from the issue.
7. **Review study and RID generation** — RG studies each delivery; RIDs raised as GitLab issues (template
   `Action.md`) or as MR comments, categorised per <13>.
8. **RID proposed disposition** — each RID dispositioned (Accepted / Partially accepted / Rejected) with
   rationale.
9. **Review meeting(s)** — asynchronous: RG/supplier exchange in the issue thread; the DMA records the
   decision (the DMA sign-off replaces the decision-making-authority meeting).
10. **Action closure** — agreed actions tracked as GitLab issues against the milestone.
11. **Review closure** — conclusion (<7>.3) recorded; baselined artefacts tagged; milestone closed.

**Independence.** As a single-developer project, reviewer independence is achieved by **automated tooling
plus explicit checklists** (CI quality gates, traceability checks) and, where available, an optional
external EOPF SDE reviewer for milestone reviews — consistent with the Category C tailoring (SDP §4.7,
§5.6).

## <9> Review schedule

Reviews are milestone-driven; **calendar dates are managed in the GitLab group `ipf` milestones**, not
duplicated here. The activity flow for each milestone review is: data-package readiness → KOM note →
distribution → RG study + RID generation → RID disposition → asynchronous review exchange → action/RID
closure → DMA conclusion → baseline (tag) → milestone closure. MR-R reviews run continuously and have no
fixed schedule (one per change); a milestone review is opened only when its phase MRs are merged and the
data package is complete. The milestone order is fixed: **SRR → PDR → CDR → QR → AR**; implementation
(WP-5) starts only after CDR closure.

## <10> Documentation subject to review

The deliveries subject to review at each milestone, per the tailored DRL (SDP §5.5.2 / §5.2.3):

| Review | Documents / deliveries subject to review |
|---|---|
| SRR | SDP, **SRevP** (this document), SPAP, Risk Register, SSS, IRD |
| PDR | SRS, V&V plan (SVerP+SValP), ICD (start), DPM, ATBD, preliminary SDD |
| CDR | SDD (+DJF), SUITP (in V&V plan), SRF, ICD (final), Traceability matrix; **source code design-freeze authorisation** |
| QR | SVR, SUITR, SRelD/SRN, SUM (start), CIDL, SCF; CI verification evidence (test/coverage/static-analysis reports) |
| AR | SUM (final), SRelD, SMP note (maintenance = GitLab issues + SemVer), acceptance data package |
| MR-R | The diff of the single change + its CI run + linked requirement/issue |

For each review the data package also includes: the reference and applicable documents (<2>, <5>), the RID
log (open/closed from the previous review), and the dependency note for any delivery that depends on
another (e.g. ICD depends on IRD; SDD depends on SRS). Content expected per review is per AD-1 Annex Q.

## <11> Participants

Participants and responsibilities follow AD-4 (ECSS-M-ST-10-01C) §5.3, tailored to a single-developer
project:

| Role | Held by | Responsibilities | Independence |
|---|---|---|---|
| Decision-Making Authority (DMA) | Project owner (acting as customer-side authority for ground-segment software) | Authorises (or withholds) transition to the next phase; records the review conclusion in the milestone summary issue. | Decision recorded and auditable in Git/GitLab. |
| Review Group chairperson | Project owner | Plans the review, confirms readiness, drives RID disposition and closure. | — |
| Review Group secretary | Project owner (assisted by GitLab automation) | Maintains the RID log (GitLab issues), minutes (issue/MR threads) and the RID status metric. | Automation-assisted. |
| Review Group member(s) | Project owner; **optional** external EOPF SDE reviewer for milestone reviews | Study the data package, raise and disposition RIDs against the checklist. | External reviewer (when available) provides human independence; otherwise CI gates + checklists. |
| Supplier project team | Project owner (software/PA/verification roles) | Provides the data package, answers RIDs, implements agreed actions. | — |

**Level of independence.** Verification and review independence are provided primarily by **automated
tooling** (the CI quality gates run on every MR, independent of the author) and by **explicit review
checklists**, supplemented by an optional external EOPF SDE reviewer at milestone reviews. This is the
accepted independence model for a Category C single-developer project (SDP §4.7, §5.6).

## <12> Logistics

- **Exact review address** — the GitLab project `gitlab.eopf.copernicus.eu/ipf/msi-processor` and the
  group `ipf` milestone for the review; all review activity is conducted in the corresponding milestone
  summary issue and the MR threads.
- **Access / security** — EOPF SDE GitLab authentication; source code is public, but **raw input data and
  instrument calibration are private and are never part of any review data package or public CI**;
  numerical verification on real data is performed locally and only its summary results are presented.
- **Tooling** — GitLab issues/MRs, rendered docs (Sphinx → GitLab Pages), CI pipeline status; no LCD
  projector, room or travel — reviews are fully asynchronous and remote.
- **Point of contact** — the project owner (see repository `README` / `docs/contributing.md`).

## <13> Annex — RID form

RIDs are recorded as **GitLab issues** (template `.gitlab/issue_templates/Action.md`) or as MR review
comments, using the fields below (conformant in content with AD-4, ECSS-M-ST-10-01C). One RID per finding.

| Field | Content |
|---|---|
| RID ID | `RID-<REVIEW>-<nnn>` (e.g. `RID-PDR-007`) — the GitLab issue/comment reference |
| Review | SRR / PDR / CDR / QR / AR / MR-R |
| Originator | Reviewer (GitLab handle) |
| Date | Raised date (auto from GitLab) |
| Item under review | Document/code item and exact location (`file.md:line`, MR id, or artefact) |
| Category | Critical / Major / Minor / Editorial |
| Type | Question / Recommendation / Defect |
| Description | The discrepancy, clearly stated |
| Proposed change | Suggested correction |
| Disposition | Accepted / Partially accepted / Rejected |
| Disposition rationale | Justification for the disposition |
| Action | Linked GitLab issue/MR implementing the agreed change (if any) |
| Status | Open / Closed |

**RID lifecycle:** raised → dispositioned (with rationale) → action assigned (if accepted) → action
implemented via MR → verified → closed. The RID status metric (opened / dispositioned / closed) is
reported in the milestone summary issue and is a success criterion for review closure (<7>.2).

---

*End of SRevP. Authored per ECSS-E-ST-40C Rev.1 Annex P, tailored for Category C.*
