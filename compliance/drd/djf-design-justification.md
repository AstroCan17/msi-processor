# Design Justification File (DJF) — Design Justification

| Field | Value |
|---|---|
| **Document** | DJF — Design Justification (design rationale, trade-offs, make-or-buy and feasibility record) |
| **DRD ref** | ECSS-E-ST-40C Rev.1 §4.2.4 / §4.2.5 (DJF concept); ECSS-M-ST-10-01C (review/justification concept); design-level summary of Annex F <6> |
| **Container** | Design Justification File (DJF) — `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | **CDR** |
| **Status** | Draft for CDR |

> **What this document is.** Per ECSS-E-ST-40C Rev.1 §4.2.4/§4.2.5 the **Design Justification File (DJF)**
> records "the result of all significant trade-offs, feasibility analyses, make-or-buy decisions and
> supporting technical assessments" and "the rationale for important design choices, and analysis and test
> data that show that the design meets all requirements." The DJF is a **file** (a container), not a single
> DRD; its constituents — SRevP (Annex P), SVerP/SValP/SUITP (Annexes I/J/K), SVR (Annex M), SRF (Annex N)
> and the V&V evidence — are separate documents (RD-2..RD-7). **This document is the head of the DJF**: it
> consolidates the *design justification* proper (the key design decisions, their alternatives, trade-offs,
> make-or-buy and feasibility rationale) and points to the constituents that carry the verification/test
> data. It is the companion to, and does not duplicate, the **SDD** (RD-1), which states *what* the design
> is; this DJF states *why*. Every decision traces to its driving `REQ-*` (SRS, RD-8), risk (`R-*`, Risk
> Register RD-5) and design element (`C-*`, SDD RD-1). Tailored Category C / single-developer: the footprint
> is the decision record, not a multi-volume trade study.

---

## <1> Introduction

**Purpose.** This document gives the engineering justification for the baselined design of `msi-processor`,
a generic high-resolution **pushbroom multispectral imager (MSI)** ground-segment processor transforming
downlinked RAW **Level-0 (`L0c`)** into calibrated, orthorectified, atmospherically corrected products up
to **Level-2 (`L2A`)**, built on the EOPF CPM (`eopf == 2.8.1`). It captures the significant design
decisions, the alternatives considered, and the trade-offs, make-or-buy and feasibility analyses that led
to the architecture and detailed design recorded in the SDD (RD-1).

**Objective.** To make the design **auditable**: a reviewer (CDR) can see, for each load-bearing choice,
the driving requirement/risk, the options weighed, why the chosen option was selected, and the cost
accepted — and can confirm that the design as a whole is shown to meet the requirements (clause <8>) and
that Category C levies no special criticality measures beyond those provided (clause <9>).

**Content.** Clause <2> lists applicable/reference documents; <3> adds decision-specific terms; <4> states
the justification approach and the decision-record format. Clause <5> is the core: the **key design
decisions and trade-offs** (`DEC-*`). Clause <6> is the **make-or-buy / reuse** decision summary; <7> the
**feasibility analyses and supporting technical assessments**; <8> the demonstration that the **design
meets the requirements**; <9> the **critical-software-component measures** justification (closing SDD
<6.3>); <10> the **design decisions deferred to implementation** (`[impl]` open points) and their
resolution criteria; <11> the **DJF constituents** and references.

**Reason for preparation.** `msi-processor` is an **integration and ECSS-productisation** effort: the
processing algorithms exist as prior work (RD-9) and the runtime is the EOPF CPM. The design therefore
turns on a small number of high-leverage integration decisions (platform, version pin, sensor-agnosticism,
core/wrapper split, reuse-vs-new). The DJF exists to record those decisions and their rationale at CDR,
before implementation (SDP WP-5) is authorised, so that the design freeze is defensible.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software product assurance | ECSS-Q-ST-80C Rev.2 (30 April 2025) |
| AD-3 | ECSS Space project management — Organization and conduct of reviews | ECSS-M-ST-10-01C |
| AD-4 | EOPF CPM — common data model / processing-unit framework | EOPF CPM docs (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Design Document (SDD, detailed/CDR) — `C-*` | `compliance/drd/sdd-software-design.md` |
| RD-2 | `msi-processor` Software Review Plan (SRevP) — DJF constituent | `compliance/drd/srevp-software-review-plan.md` |
| RD-3 | `msi-processor` V&V plan (SVerP + SValP + SUITP merged) — DJF constituent | `compliance/drd/vv-plan.md` |
| RD-4 | `msi-processor` Software Verification Report (SVR) — DJF constituent (QR) | `compliance/drd/vv-report.md` |
| RD-5 | `msi-processor` Risk Register — `R-*` | `compliance/drd/risk-register.md` |
| RD-6 | `msi-processor` Software Reuse File (SRF) — DJF constituent | `compliance/drd/srf-software-reuse-file.md` |
| RD-7 | `msi-processor` Traceability matrix (forward/backward, design→test) | `compliance/traceability/traceability-matrix.md` |
| RD-8 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-9 | Prior work — multispectral pushbroom preprocessing pipeline (`level_0`, `level_1`, `band_coreg`, `georeferencing_v1`, `pansharp`, `metrics_ips`) | via RD-6 |
| RD-10 | `msi-processor` Detailed Processing Model (DPM) — `DPM-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-11 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-12 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-13 | `msi-processor` SSS / IRD / ICD — `SYS-*`, `REQ-IF-*`, `ICD-IF-*` | `compliance/drd/{sss-…,ird-…,icd-…}.md` |

---

## <3> Terms, definitions and abbreviated terms

The SDP <3>, SRS <3>, SDD <3> and Risk Register glossaries apply in full. Only decision-record-specific
terms are added here.

| Term / abbr. | Definition |
|---|---|
| DDF / DJF | Design Definition File (the *what* — SDD + code) / Design Justification File (the *why* — this record + V&V evidence), ECSS-E-ST-40C §4.2 |
| `DEC-nn` | A recorded design decision in clause <5>, with options, trade-off, decision and rationale |
| Make-or-buy | The reuse vs new-development decision for a component (ECSS-E-ST-40C §4.2.4; "buy" = reuse/COTS/heritage) |
| Trade-off | Comparison of design options against the driving requirements/risks, yielding the selected option |
| `[impl]` | A design decision whose *body* is legitimately finalised during implementation (post-CDR); its interface and selection criteria are fixed at CDR (see <10>) |
| Driver | The `REQ-*` and/or `R-*` that motivates and constrains a decision |

---

## <4> Design justification approach

### <4.1> What the DJF records and where

Per ECSS-E-ST-40C §4.2.4/§4.2.5 the DJF accumulates two kinds of content across the life cycle:

1. **Decision rationale** (trade-offs, feasibility, make-or-buy, supporting assessments) — produced in the
   requirements/architecture (PDR) and design/implementation (CDR) processes. **This document** is its
   consolidation (clauses <5>–<7>, <9>, <10>).
2. **Analysis and test data showing the design meets the requirements** — produced by verification and
   validation. These live in the **DJF constituents** (RD-2..RD-4, RD-6): the SRevP (review approach), the
   merged V&V plan (verification/validation/unit-integration test design), the SVR (verification results,
   QR) and the SRF (reuse analysis). Clause <8> binds the design to those constituents; clause <11> maps
   the file.

At CDR the "design-meets-requirements" evidence is the **requirements→design→test traceability** (SDD <6>,
RD-7) plus the **test design** (SUITP in RD-3); the executed **test results** (SVR, RD-4) are added to the
DJF at QR/AR. This document is therefore complete for CDR and is updated as evidence accrues.

### <4.2> Decision-record format

Each decision in <5> is recorded as:

- **`DEC-nn` — title.**
- **Context / drivers** — the problem and the driving `REQ-*` / risk `R-*`.
- **Options** — a trade table `Option | Pros | Cons`, with the selected option marked **(chosen)**.
- **Decision & rationale** — the selected option and why it wins against the drivers.
- **Consequences / cost accepted** — the disadvantage knowingly taken on, and any mitigation.
- **Trace** — design element(s) `C-*` (SDD), and the requirements/risks satisfied or bounded.

### <4.3> Traceability of decisions

Every `DEC-*` references upstream `REQ-*` (RD-8) and, where the decision treats a risk, the risk `R-*`
(RD-5); and downstream the design element `C-*` and the SDD clause that realises it (RD-1, principally SDD
<4.7> trade-offs, <5.3> development types and <6.3> critical-component measures). The decision-to-risk
cross-reference is summarised in <5.15>. No decision is recorded without at least one driver; no Category C
"special measure" is claimed beyond those in <9>.

---

## <5> Key design decisions and trade-offs

The decisions below are ordered from the most architecture-defining (platform, version, sensor-agnosticism,
core/wrapper) to the supporting choices. They expand and justify the trade-offs summarised in SDD <4.7>7.

### <5.1> DEC-01 — Build on the EOPF CPM vs a standalone framework *(make-or-buy)*

**Context / drivers.** The processor must produce EO-standard, interoperable, cloud-native products and
integrate into the EO ground segment. Drivers: REQ-D-01 (CPM PU architecture), REQ-D-06 (reuse only
sanctioned components; product I/O only through CPM abstractions), REQ-D-09 (open Zarr/CF/STAC output),
REQ-I-05/06 (triggering, URI I/O), REQ-F-PRD-01 (`EOProduct`/Zarr). Risk: R-05 (CPM API stability), R-10
(product-format conformance).

| Option | Pros | Cons |
|---|---|---|
| **EOPF CPM (`EOProcessingUnit`/`EOProduct`/`EOZarrStore`) (chosen)** | EO-native product model, Zarr/store abstraction and triggering for free; interoperable by construction; aligns with the EOPF SDE/CI; no framework to maintain | Couples the runtime to an external, evolving framework (R-05) and to a pinned version (DEC-02) |
| Standalone bespoke framework | Full control of the runtime/format; no external coupling | Re-implements product model, I/O, store mapping, triggering, provenance — large new development against REQ-D-06/-09; loses interoperability and EOPF alignment; higher long-term maintenance |
| Generic workflow engine (e.g. Airflow/Snakemake) + custom product model | Mature orchestration | Still needs a bespoke EO product/format layer; not EO-native; off-pattern for the EOPF ground segment |

**Decision & rationale.** Adopt the EOPF CPM. It directly satisfies REQ-D-01/-06/-09 and REQ-F-PRD-01, gives
interoperability and the store/triggering machinery as reuse, and is the sanctioned platform of the host
ground segment. A bespoke framework would be a large new development squarely against the project's
"reuse over reinvention" objective (SDP <4.1>3) and Category C footprint.

**Consequences / cost accepted.** External coupling to the CPM and its version (R-05, treated by DEC-02 and
DEC-04). Mitigation: the coupling is confined to the thin Wrappers and the `C-COM-*` services; the Cores
are CPM-free (DEC-04), so a framework change re-touches only the adapters.

**Trace.** Whole architecture; C-COMPUTING, C-COM-PRODUCT, C-COM-IO, C-COM-ORC. REQ-D-01/-06/-09,
REQ-F-PRD-01, REQ-I-05/06; R-05, R-10.

### <5.2> DEC-02 — Pin `eopf == 2.8.1` vs track 3.x / the `latest` template

**Context / drivers.** The CPM must be at a fixed, reproducible version. Drivers: REQ-R-03 (run on Python
3.11 + `eopf == 2.8.1`), REQ-REL-01/F-DEP-02 (reproducibility), REQ-M-03 (governed version-bump procedure).
Risk: R-01 (pin vs SDE build-image `latest` drift), R-05 (API stability).

| Option | Pros | Cons |
|---|---|---|
| **Pin `eopf == 2.8.1` (chosen)** | Deterministic, reproducible builds; one fixed API surface to design and test against; matches the SDE `cpm-build-environment` at design time; bump is a controlled, V&V-gated change (REQ-M-03) | Can desynchronise from an SDE image tagged `latest` (R-01); deliberately forgoes newer 3.x features until a planned bump |
| Track CPM 3.x / newest template | Latest features and fixes; closer to upstream direction | Moving target during a documentation-first design; API churn (R-05) would repeatedly invalidate the SDD before code exists; not reproducible |
| Float to image `latest` (no pin) | Always matches the build image | Non-reproducible builds; silent breakage; incompatible with REQ-REL-01/REQ-R-03 |

**Decision & rationale.** Pin to **2.8.1**. A documentation-first life cycle (SDP <5.1>) baselines the SDD,
ICD and computing-model JSON against a *fixed* CPM API; a moving target (3.x/`latest`) would churn the
design and defeat reproducibility (REQ-REL-01, REQ-R-03). The pin is the single most volatile dependency,
so it is isolated (DEC-04) and its change is governed (REQ-M-03).

**Consequences / cost accepted.** Possible drift from an SDE image tagged `latest` (R-01) and deferral of
3.x features. Mitigation (R-01): pin to image digest where the SDE allows; CI smoke test against the pinned
env; monitor SDE release notes; any forced bump handled as an MR + re-baseline per REQ-M-03.

**Trace.** Platform-wide; C-COM-PRODUCT/IO/ORC, all Wrappers. REQ-R-03, REQ-REL-01, REQ-F-DEP-02,
REQ-M-03; R-01, R-05.

### <5.3> DEC-03 — Generic sensor-profile architecture vs an S2-specific (single-sensor) build

**Context / drivers.** The processor is required to be sensor-agnostic, specialised by configuration, with
the owner's sensor as the first profile. Drivers: REQ-AD-01 (sensor-agnostic, profile-parametrised),
REQ-AD-02 (identified/versioned profile, per-run selectable), REQ-D-04 (no hard-coded instrument constants
in the core), REQ-D-07 (a new sensor = a new profile, no core change), REQ-S-01/05 (public code / private
calibration never embedded). Risk: R-04 (calibration availability), R-08 (single-developer reuse leverage).

| Option | Pros | Cons |
|---|---|---|
| **Generic chain + externalised per-sensor profile + ADFs (chosen)** | One code base across sensors (REQ-D-07); no instrument constants in code (REQ-D-04, REQ-S-05); calibration stays private, swappable by ADF (REQ-M-02); maximises reuse leverage for a single developer (R-08) | Up-front cost of a versioned profile schema + validation (C-COM-PROFILE, C-SENSORS); a layer of indirection |
| S2-specific build (hard-coded sensor) | Simplest first delivery; no schema layer | Violates REQ-AD-01/-04 and REQ-D-04/-07; bakes private calibration into code (against REQ-S-05); a second sensor is a fork |
| Per-sensor code forks (branch per sensor) | Sensor code can diverge freely | N copies to maintain; divergence and drift; antithetical to single-developer maintainability (R-08) and to REQ-D-07 |

**Decision & rationale.** Adopt the generic profile architecture. It is a hard requirement set
(REQ-AD-01..04, REQ-D-04/-07) and the only option that keeps **private calibration out of public code**
(REQ-S-01/05) by holding it in profile-referenced ADFs. For a single developer it also maximises reuse:
each new sensor is data, not code (R-08). The owner's sensor is simply the first instantiated profile
(REQ-AD-02), proving the mechanism.

**Consequences / cost accepted.** A schema + validation layer (C-COM-PROFILE) and ADF-binding discipline
(C-COM-ADF, C-SENSORS). Accepted as a one-time investment that pays back at the second profile; validated
at CDR/QR by a second (synthetic) profile run (REQ-D-07 verification, SRS <7>).

**Trace.** C-SENSORS, C-COM-PROFILE, C-COM-ADF, C-COM-CONFIG. REQ-AD-01..04, REQ-D-04/-07, REQ-S-01/05,
REQ-M-02; R-04, R-08.

### <5.4> DEC-04 — Pure-core + thin-PU (wrapper) pattern vs algorithm-in-PU

**Context / drivers.** Algorithm code must be testable, portable and isolated from the framework. Drivers:
REQ-D-03 (pure, unit-testable core + thin PU wrapper), REQ-D-04 (minimise critical components; bounded
complexity), REQ-M-04 (per-stage modularity), REQ-PORT-03 (run on a local/CI shell path without the full
runtime). Risk: R-05 (CPM API stability — isolate the blast radius).

| Option | Pros | Cons |
|---|---|---|
| **Pure Core (no CPM) + thin `EOProcessingUnit` Wrapper (chosen)** | Cores unit-testable and numerically verifiable without the CPM runtime (REQ-D-03, REQ-PORT-03); CPM coupling confined to the thin adapter, so an API/version change re-touches only wrappers (R-05, REQ-M-04); bounded complexity in CPM-facing code (REQ-D-04) | A small adapter per stage and a stable Core↔Wrapper contract (IF-CORE-01) to maintain |
| Algorithm directly inside the `EOProcessingUnit` | No adapter layer; fewer files | Numerics entangled with the CPM — cannot unit-test off-platform; every CPM change reaches the algorithm (R-05); larger critical surface (against REQ-D-04) |

**Decision & rationale.** Adopt pure-core + thin-wrapper. It is the design pattern mandated by REQ-D-03 and
the SDP design method (<5.3>), and it is the structural mitigation for the two biggest integration risks:
CPM coupling (R-05) is fenced into the wrapper, and the numerics become independently verifiable
(REQ-D-03), which is essential given private-data-only verification (R-03, DEC-13). It also minimises the
critical-component surface (REQ-D-04, clause <9>).

**Consequences / cost accepted.** One adapter per stage and the `BandStack`/IF-CORE-01 contract. Accepted;
the wrapper is templated (SDD <5.4.1>) so the per-stage cost is small.

**Trace.** Every C-PU-* (`core`+`unit`); IF-CORE-01. REQ-D-03/-04, REQ-M-04, REQ-PORT-03; R-05, R-03.

### <5.5> DEC-05 — Reuse the prior-work algorithms vs rewrite from scratch *(make-or-buy)*

**Context / drivers.** The L0→L1 algorithm mathematics already exists as prior work (RD-9). Drivers: SDP
<4.1>3 (reuse over reinvention), REQ-D-06 (reused-software constraints), the Category C / single-developer
footprint. Risk: R-08 (bus factor / leverage). Governed by the SRF (RD-6, Annex N).

| Option | Pros | Cons |
|---|---|---|
| **Reuse-adapt heritage Cores (RD-9) behind IF-CORE-01 (chosen)** | Largest schedule/effort saving; algorithms already exercised; matches "integration not research" framing; SRF-governed (RD-6) | Heritage code must be refactored to the pure-Core contract and brought to ECSS/CI quality (typing, complexity, tests) |
| Rewrite all stages from scratch | Clean-room code to the new conventions | Discards proven algorithm work; large effort for a single developer (R-08); no correctness benefit at Category C |
| Adopt a third-party L0→L1 toolkit wholesale | Off-the-shelf | No sensor-agnostic, profile-driven, NDA-respecting fit; would still need heavy adaptation; weaker control of the numerics |

**Decision & rationale.** Reuse-adapt the heritage Cores. The project is explicitly an integration/
productisation of existing algorithms (SDP <1>); reuse is the dominant lever for a single developer (R-08)
and is consistent with REQ-D-06. The adaptation cost (pure-Core refactor + ECSS quality) is exactly the
productisation work the project exists to do. Each reused stage is declared in the SRF with its development
type (`reuse-adapt`, SDD <5.3>).

**Consequences / cost accepted.** Heritage code is refactored to IF-CORE-01 and raised to the CI quality
gates (SDP <5.4>). Accepted; tracked per stage in the SRF (RD-6).

**Trace.** C-PU-L0/RAD/ENH/TOA/COR/GEO/PAN/QA (`reuse-adapt`, RD-9). REQ-D-06, SDP <4.1>3; R-08; SRF RD-6.

### <5.6> DEC-06 — Atmospheric L2 as new development vs reuse *(make-or-buy)* + RT-engine basis

**Context / drivers.** Unlike L0→L1, L2 atmospheric correction has **no prior heritage**. Drivers:
REQ-F-ATM-01..04 (AOT/WV retrieval, TOA→BOA, scene classification + masks), REQ-P (BOA accuracy budget).
Risk: **R-06 (new L2 development — top technical/schedule risk)**. Basis: DPM-M-ATM (RD-10), ALG-ATM-*
(RD-11).

| Option | Pros | Cons |
|---|---|---|
| **New development on an established RT model / LUT (e.g. 6S / libRadtran), interface-first (chosen)** | Builds on a proven radiative-transfer basis rather than a novel algorithm (R-06); designed against DPM/ATBD so the rest of the chain is unaffected; explicit L2 acceptance criteria and schedule margin | Genuinely new code and verification; the only non-reused Core; RT engine + scene classifier still to be down-selected ([impl]) |
| Reuse a heritage L2 module | Would save effort | None exists in RD-9 — not available |
| Wholesale third-party L2 processor (e.g. Sen2Cor-class) | Mature for one sensor | Sensor-specific, not profile-driven/sensor-agnostic; heavy to retrofit; weak fit to the generic chain (DEC-03) |
| Skip/defer L2 (stop at L1C) | Removes the top risk | Fails the L0→L2 scope (SSS/SRS); not acceptable |

**Decision & rationale.** Develop L2 as **new** code, but on an **established RT/LUT basis** rather than a
novel algorithm, and **interface-first** against DPM-M-ATM/ALG-ATM-* so the L0→L1C chain is decoupled from
L2 maturity. This is the explicit mitigation of R-06: reduce algorithmic novelty, isolate the blast radius,
schedule L2 last with margin, and pin L2 acceptance criteria in the SValP (RD-3).

**Consequences / cost accepted.** New Core + verification, and an open down-select of the RT engine and
scene classifier (deferred decision, <10> DEC-D1). Accepted and risk-tracked (R-06); the C-PU-ATM
interface is fixed at CDR so the chain proceeds regardless of the engine choice.

**Trace.** C-PU-ATM (`new`); DPM-M-ATM, ALG-ATM-*. REQ-F-ATM-01..04, REQ-P (BOA); **R-06**.

### <5.7> DEC-07 — One PU per stage with optional stages toggleable vs fused mega-stages

**Context / drivers.** The chain must support level breakpoints, re-runnable sub-chains and independent
verification, with some stages optional. Drivers: REQ-F-ORC-01 (run a level / sub-chain / full chain),
REQ-REL-02 (re-run at breakpoint granularity), REQ-M-04 (modularity), REQ-F-ENH-03 (enhancement default-off
where unvalidated), `DPM-BKP-*` (level breakpoints).

| Option | Pros | Cons |
|---|---|---|
| **One PU per processing stage, optional stages toggleable (chosen)** | Level breakpoints `L1A/B/C/L2A`; independent per-stage verification and re-run; optional stages (enhancement, pansharpen) default-off (REQ-F-ENH-03); clean requirement allocation | More inter-PU `EOProduct` hand-offs |
| Fused mega-stages (e.g. one L0→L1C unit) | Fewer hand-offs; less I/O | No intermediate breakpoints; can't verify or re-run a single correction; poor allocation/traceability; optional stages can't be cleanly toggled |

**Decision & rationale.** One PU per stage. Granularity is what makes the chain verifiable, re-runnable
(REQ-REL-02, REQ-F-ORC-01) and cleanly traceable (one stage → one DPM module → its `REQ-F-*`), and it is
the only clean way to keep unvalidated optional stages default-off (REQ-F-ENH-03).

**Consequences / cost accepted.** More inter-PU hand-offs; mitigated by lazy Zarr I/O (DEC-09) so hand-offs
are cheap. Accepted.

**Trace.** C-COMPUTING (nine stages), C-COM-ORC. REQ-F-ORC-01, REQ-REL-02, REQ-M-04, REQ-F-ENH-03;
`DPM-BKP-*`.

### <5.8> DEC-08 — Chunked, optionally Dask-distributed execution vs whole-product in memory

**Context / drivers.** Memory must be bounded independently of product size, with optional horizontal
scaling, but must also run on a plain CI/local host. Drivers: REQ-F-ORC-02 (block processing + optional
Dask), REQ-P-04/05 (throughput / bounded memory), REQ-R-04 (scale out), REQ-PORT-03 (sequential single
process for CI/local). Risk: R-02 (shell runner has no Dask gateway).

| Option | Pros | Cons |
|---|---|---|
| **Block/tile (+halo) Cores, sequential or Dask, identical Cores (chosen)** | Peak memory set by block size, not product size (REQ-P-05); horizontal scaling when Dask present (REQ-R-04); same Cores run sequentially on the shell runner/local (REQ-PORT-03, R-02) | Tiling + halo handling in spatially-coupled stages (georeference, coregistration, enhancement) |
| Whole-product in memory | Simplest Cores; no tiling | Memory scales with product size — fails REQ-P-05/REQ-R-04 on large scenes; no scale-out |
| Dask-only (mandatory) | Uniform distributed model | Cannot run on the CI shell runner (no Dask gateway, R-02); breaks REQ-PORT-03 |

**Decision & rationale.** Block-based Cores with a **dual sequential/Dask** strategy sharing identical
Cores. Only the block mapping (C-COM-CHUNK) differs between modes, so memory is bounded (REQ-P-05) and the
same code runs on the constrained CI shell runner sequentially (REQ-PORT-03, R-02) and scales out on Dask
where available (REQ-R-04).

**Consequences / cost accepted.** Tiling/halo logic in the spatial PUs (the design's hot-spots,
georeference/atmospheric per SDD <4.6>). Accepted; these are the priority chunking/Dask validation targets.

**Trace.** C-COM-CHUNK, spatial C-PU-*. REQ-F-ORC-02, REQ-P-04/05, REQ-R-04, REQ-PORT-03; R-02.

### <5.9> DEC-09 — `EOProduct`/Zarr-exclusive open I/O vs custom or legacy formats

**Context / drivers.** Outputs must be cloud-native, open and CPM-native; I/O only through CPM abstractions.
Drivers: REQ-D-09 (Zarr + CF/STAC/GeoZarr metadata), REQ-D-06 (I/O only via CPM), REQ-F-PRD-01
(`EOProduct`/Zarr), REQ-I-06/PORT-02 (URI/store transparency). Risk: R-10 (format conformance), R-01/R-05
(coupling to pinned CPM).

| Option | Pros | Cons |
|---|---|---|
| **`EOProduct` + Zarr (CF/STAC/GeoZarr) via `EOZarrStore` only (chosen)** | Cloud-native, chunk-aligned with DEC-08, open and vendor-independent (REQ-D-09); CPM-native (REQ-D-06); URI/store transparency local/POSIX/S3 (REQ-PORT-02) | Bound to the pinned CPM I/O API (R-01/R-05) |
| GeoTIFF / NetCDF outputs | Familiar, widely supported tooling | Not chunk/cloud-native at scale; off the EOPF product model (REQ-D-06/-09); extra conversion layer |
| Custom binary format | Full control | Not open/interoperable; reinvents the product model; against REQ-D-06/-09 |

**Decision & rationale.** Zarr `EOProduct` exclusively, through `EOZarrStore`. It satisfies REQ-D-06/-09 and
REQ-F-PRD-01 directly, is the natural persistence for the block model (DEC-08), and is open and readable
independently of this software (long-lifetime, SDD <4.5>).

**Consequences / cost accepted.** I/O bound to the pinned CPM (R-01/R-05; mitigated by DEC-02/-04). Output
conformance checked in CI against the `EOProduct` schema (R-10 mitigation).

**Trace.** C-COM-PRODUCT, C-COM-IO. REQ-D-06/-09, REQ-F-PRD-01, REQ-I-06, REQ-PORT-02; R-10, R-01, R-05.

### <5.10> DEC-10 — Fail-stop recovery vs in-run retry / redundancy

**Context / drivers.** Define the recovery policy for a ground, reprocessable, Category C processor.
Drivers: REQ-F-DEP-01 (fail-stop, no partial/misleading product), REQ-REL-02 (re-runnable at breakpoints),
REQ-SAF-01 (residual hazard = product-data integrity). CPM `triggering__error_policy: FAIL_FAST`.

| Option | Pros | Cons |
|---|---|---|
| **Fail-stop: typed error at PU boundary → non-zero exit, no partial product; re-run at breakpoint (chosen)** | No partial/misleading product is ever published (REQ-F-DEP-01, REQ-SAF-01); simple, deterministic, auditable; matches a reprocessable ground context | A transient failure aborts the run (re-run required) — acceptable for batch ground processing |
| In-run retry / fallback | Could ride through transient faults | Hides faults; risks publishing degraded data as nominal; complexity unjustified at Category C |
| Redundancy / N-version | Fault tolerance | Not warranted at Category C (clause <9>); large cost; no safety/mission driver |

**Decision & rationale.** Fail-stop. For a reprocessable ground processor whose residual hazard is
*product-data integrity* (REQ-SAF-01), the correct failure mode is to **stop and publish nothing**, not to
mask the fault. The PU boundary is the fault-containment region (typed `MsiProcessorError` → flagged,
reported failure); re-run granularity comes from the breakpoints (DEC-07).

**Consequences / cost accepted.** A failed run must be re-run; acceptable for batch processing. Observational
deviations (QA metric out of tolerance) are **warnings**, not exceptions, so they do not abort the run.

**Trace.** C-COM-ORC (fail-stop), all Cores (typed errors). REQ-F-DEP-01, REQ-REL-02, REQ-SAF-01.

### <5.11> DEC-11 — Pure-Python 3.11 on CPU vs native extensions / GPU acceleration

**Context / drivers.** Choose the implementation substrate against portability, long lifetime and the CI
constraint. Drivers: REQ-R-01 (x86-64 Linux multi-core CPU, no GPU required), REQ-R-03 (Python 3.11 +
pinned stack), REQ-PORT-01/02 (relocatable SDE↔local), REQ-D-09/long-lifetime (SDD <4.5>).

| Option | Pros | Cons |
|---|---|---|
| **Pure Python 3.11 + portable array libs (numpy/xarray), CPU only (chosen)** | No native build/toolchain; relocatable SDE↔local (REQ-PORT-01/02); long-lifetime, low platform assumption (SDD <4.5>); horizontal scaling via Dask (DEC-08) covers throughput | Per-element Python is slower than native/GPU for some kernels |
| Native (C/Cython) extensions | Faster hot kernels | Build/portability burden; harder to relocate and maintain (single developer); off REQ-R-01 |
| GPU acceleration | Fast for some stages | Requires GPU hardware/runtime — against REQ-R-01 (no GPU required); not available on the CI host; portability/lifetime cost |

**Decision & rationale.** Pure Python 3.11 on CPU. REQ-R-01 explicitly does not require a GPU; portability
and long lifetime (REQ-PORT, SDD <4.5>) outweigh raw single-node speed, and throughput is met by
**horizontal** scaling (Dask, DEC-08) rather than native/GPU acceleration. The vectorised numpy/xarray
kernels are adequate within the block model.

**Consequences / cost accepted.** Some kernels slower than a native/GPU build; accepted and addressed by
chunking/parallelism. A future hot-spot can be optimised behind IF-CORE-01 without disturbing the chain.

**Trace.** Architecture-wide; Cores, C-COM-CHUNK. REQ-R-01/-03, REQ-PORT-01/02; SDD <4.5>.

### <5.12> DEC-12 — Determinism via profile-fixed seeds vs free RNG

**Context / drivers.** Output must be reproducible for a fixed input/ADF/profile/processor, but some kernels
are stochastic (RANSAC in coregistration/geolocation). Drivers: REQ-F-DEP-02 / REQ-REL-01 (reproducibility),
REQ-D-05 (numerics/tolerances). Basis: ATBD <6>.

| Option | Pros | Cons |
|---|---|---|
| **Profile-fixed seeds for all stochastic kernels (chosen)** | Bit-reproducible runs for a fixed quadruple (REQ-F-DEP-02, REQ-REL-01); verifiable against checksummed references (R-03); seed is profile data, not code | Seed must be carried in the profile and echoed in provenance |
| Free / time-based RNG | Marginally simpler | Non-reproducible outputs — breaks REQ-F-DEP-02/REQ-REL-01 and golden-test verification under private-data-only (R-03) |

**Decision & rationale.** Fix seeds in the profile. Reproducibility is required (REQ-F-DEP-02) and is the
foundation of the verification strategy under private-data-only constraints (DEC-13, R-03): golden tests
need bit-stable outputs. The seed lives in the profile (data) and is recorded in provenance.

**Consequences / cost accepted.** Seeds carried in profile + provenance. Accepted; negligible cost.

**Trace.** C-PU-COR, C-PU-GEO (RANSAC), C-COM-PROV. REQ-F-DEP-02, REQ-REL-01, REQ-D-05; ATBD <6>; R-03.

### <5.13> DEC-13 — Verification independence by tooling + synthetic fixtures vs (private-data, single-developer)

**Context / drivers.** Code is public but raw L0 and calibration are private; there is a single developer
and no second verifier and no public reference product for L0→L1. Drivers: REQ-S-01 (public code / private
data), REQ-D-03 (unit-testable cores), REQ-Q-01 (quality gates). Risks: **R-03 (private-data-only / no
public reference — top assurance risk)**, R-02 (shell-runner limits), R-07 (data/secret leakage), R-08
(bus factor / independence). Mechanism defined in the SRevP (RD-2) and V&V plan (RD-3).

| Option | Pros | Cons |
|---|---|---|
| **Automated CI gates + explicit checklists + deterministic synthetic fixtures in public CI; real-data numerical verification local, summarised in the SVR (chosen)** | Independence by tooling not staff (R-08); no private data ever in public CI/repo (REQ-S-01, R-07); golden tests run publicly on non-sensitive fixtures; real-data evidence captured locally (SVR, RD-4) | Real-data correctness is verified locally, not in public CI — only summaries are public |
| Put real data in (private) CI | Full data-path verification in CI | Risks irreversible disclosure (R-07); no private CI/runner available; against REQ-S-01 |
| Second independent verifier | Human independence | Not available (single developer, R-08); not warranted at Category C |

**Decision & rationale.** Achieve independence through **automation + checklists + synthetic golden
fixtures**, with real-data numerical verification performed locally and only its summary results published
in the SVR. This is the only model that satisfies REQ-S-01 (no private data in public CI, R-07), works for a
single developer (R-08), and still yields auditable, reproducible verification (enabled by DEC-04 and
DEC-12). Affected jobs that need a container/Dask/S3 runtime are non-blocking (`allow_failure`) on the shell
runner (R-02) with equivalent local evidence in the SVR.

**Consequences / cost accepted.** Real-data correctness is locally verified, not publicly re-runnable; the
SVR carries the checksummed evidence; where a comparable open product exists it is cross-checked
(e.g. SNAP/ESA L1). Accepted and risk-tracked (R-02, R-03).

**Trace.** Verification architecture; Cores (testable, DEC-04), C-COM-PROFILE/ADF (private by URI). REQ-S-01,
REQ-D-03, REQ-Q-01; R-02, R-03, R-07, R-08; SRevP RD-2, V&V plan RD-3.

### <5.14> DEC-14 — Per-pixel QA bit-flag registry + provenance as the integrity mechanism

**Context / drivers.** A Category C processor whose residual hazard is product-data integrity must carry
localised quality and full provenance, not just pass/fail. Drivers: REQ-F-QA-01/02 (metrics + per-pixel
flags), REQ-F-PRD-02 (provenance), REQ-SAF-01 (integrity). Basis: ICD <5.3.3>E (flag bits).

| Option | Pros | Cons |
|---|---|---|
| **Single per-pixel `QAFlag` bit registry (monotone OR-accumulated) + provenance metadata (chosen)** | Localised, per-pixel defect tracking (loss, saturation, bad-pixel, coreg-fail, cloud/shadow); single source of truth (ICD <5.3.3>E); pairs with fail-stop as the integrity triad (DEC-10); reproducible | Bit budget must be managed (one reserved bit `[TBC@CDR]`) |
| Per-stage ad-hoc masks | Simple per stage | Inconsistent semantics; hard to propagate/trace; no single registry |
| Scene-level quality only | Cheap | Loses per-pixel locality; insufficient for integrity evidence |

**Decision & rationale.** A single, OR-accumulated per-pixel `QAFlag` registry plus provenance. It gives the
localised integrity evidence the hazard class demands (REQ-SAF-01), is consistent across stages (one
registry, ICD <5.3.3>E), and forms the **fail-stop + QA flags + provenance** integrity triad of clause <9>.

**Consequences / cost accepted.** A managed bit budget (currently 7 defined, 1 reserved). Accepted.

**Trace.** C-COM-QAFLAG, C-PU-QA, C-COM-PROV. REQ-F-QA-01/02, REQ-F-PRD-02, REQ-SAF-01; ICD <5.3.3>E.

### <5.15> Decision → driver/risk cross-reference

| Decision | Primary `REQ-*` drivers | Risks treated | Design `C-*` |
|---|---|---|---|
| DEC-01 EOPF CPM | D-01, D-06, D-09, F-PRD-01, I-05/06 | R-05, R-10 | C-COMPUTING, C-COM-PRODUCT/IO/ORC |
| DEC-02 `eopf==2.8.1` pin | R-03(req), REL-01, F-DEP-02, M-03 | R-01, R-05 | platform-wide |
| DEC-03 sensor-profile | AD-01..04, D-04/-07, S-01/05, M-02 | R-04, R-08 | C-SENSORS, C-COM-PROFILE/ADF/CONFIG |
| DEC-04 core+wrapper | D-03/-04, M-04, PORT-03 | R-05, R-03 | all C-PU-* |
| DEC-05 reuse algorithms | D-06, SDP <4.1>3 | R-08 | C-PU-L0/RAD/ENH/TOA/COR/GEO/PAN/QA |
| DEC-06 L2 new dev + RT basis | F-ATM-01..04, P(BOA) | **R-06** | C-PU-ATM |
| DEC-07 PU-per-stage | F-ORC-01, REL-02, M-04, F-ENH-03 | — | C-COMPUTING, C-COM-ORC |
| DEC-08 chunk + Dask | F-ORC-02, P-04/05, R-04, PORT-03 | R-02 | C-COM-CHUNK, spatial C-PU-* |
| DEC-09 Zarr/EOProduct I/O | D-06/-09, F-PRD-01, I-06, PORT-02 | R-10, R-01, R-05 | C-COM-PRODUCT/IO |
| DEC-10 fail-stop | F-DEP-01, REL-02, SAF-01 | — | C-COM-ORC, Cores |
| DEC-11 pure-Python/CPU | R-01/-03, PORT-01/02 | — | architecture-wide |
| DEC-12 fixed seeds | F-DEP-02, REL-01, D-05 | R-03 | C-PU-COR/GEO, C-COM-PROV |
| DEC-13 tooling independence | S-01, D-03, Q-01 | R-02, R-03, R-07, R-08 | verification arch. |
| DEC-14 QA flags + provenance | F-QA-01/02, F-PRD-02, SAF-01 | — | C-COM-QAFLAG, C-PU-QA, C-COM-PROV |

---

## <6> Make-or-buy (reuse) decisions

ECSS-E-ST-40C §4.2.4 requires make-or-buy decisions to be recorded in the DJF; the authoritative reuse
analysis (licences, versions, reuse risks) is the **SRF (RD-6, Annex N)**. The per-component make-or-buy
outcome, consistent with SDD <5.3> (development type):

| Component | Make-or-buy | Basis / source |
|---|---|---|
| EOPF CPM runtime (`EOProcessingUnit`/`EOProduct`/`EOZarrStore`) | **buy (reuse)** — DEC-01 | EOPF CPM `eopf==2.8.1` (AD-4) |
| Scientific stack (numpy, xarray, zarr, Dask, scikit-image, OpenCV, GDAL/rasterio, pywt, scikit-learn) | **buy (reuse)** | open-source, SRF (RD-6) |
| C-PU-L0/RAD/ENH/TOA/COR/GEO/PAN/QA Cores | **buy then adapt (reuse-adapt)** — DEC-05 | prior work RD-9, via SRF |
| C-PU-ATM (atmospheric L2) Core | **make (new development)** — DEC-06 | DPM-M-ATM/ALG-ATM-*; established RT/LUT basis |
| C-SENSORS / C-COM-* services (profile, product, io, adf, prov, qaflags, chunking, config, orchestration, cli) | **make (new, over CPM/Dask)** — DEC-03/-04/-08/-09 | this project |

**Net.** The project is reuse-dominated (platform + L0→L1 algorithms + scientific stack are reused); the
**new development is confined to the integration/services layer and the L2 atmospheric Core** — which is
exactly the productisation scope and the locus of the top technical risk (R-06). Licence compatibility and
reuse risks are assessed in the SRF (RD-6).

---

## <7> Feasibility analyses and supporting technical assessments

The supporting assessments (ECSS-E-ST-40C §4.2.4) that show the chosen design is feasible within its
constraints:

- **Memory / throughput feasibility (DEC-08).** Peak per-worker memory is governed by the configured
  block/tile size (C-COM-CHUNK), not product size, and wall-time scales with tiles × workers (SDD <4.6>;
  REQ-P-04/05, REQ-R-04). `georeference` and `atmospheric` are the memory/compute hot-spots and the priority
  chunking/Dask validation targets. Absolute numeric budgets (`MEM_BUDGET`, `THRU_SCENE`) are per-profile
  private parameters verified locally (SRS <5.1>, `DPM-PRM-GEN-02`) and are not reproduced here.
- **CI / runner feasibility (DEC-08, DEC-13; R-02).** The same Cores run **sequentially** on the EOPF SDE
  shell runner (no container/Dask/S3); jobs needing those runtimes are non-blocking (`allow_failure`) with
  equivalent local evidence in the SVR (RD-4). Feasible today; a Kubernetes/Dask-gateway runner is a tracked
  improvement, not a precondition.
- **Atmospheric L2 feasibility (DEC-06; R-06).** Feasibility rests on building on an established
  radiative-transfer model / LUT (6S / libRadtran class) rather than a novel algorithm, scheduling L2 last
  with margin, and fixing the C-PU-ATM interface at CDR so chain integration does not wait on the engine
  down-select (<10> DEC-D1). Explicit L2 acceptance criteria are set in the SValP (RD-3).
- **Verification feasibility under private data (DEC-12, DEC-13; R-03).** Deterministic synthetic fixtures
  make golden-test verification feasible in public CI without private data; bit-reproducibility (fixed seeds)
  makes checksummed references possible; real-data numerical verification is performed locally and summarised
  in the SVR. Where a comparable open product exists, cross-checking against an open reference processor
  (e.g. SNAP/ESA L1) is used.
- **Portability / long-lifetime feasibility (DEC-09, DEC-11).** Pure Python + open Zarr + URI/store
  abstraction keep the only platform assumption a POSIX x86-64 Linux host and keep products readable
  independently of this software (SDD <4.5>; REQ-PORT-01/02, REQ-D-09).
- **Technical budgets / margins.** Per the SRevP (RD-2 <6>) and SDP (RD-12 <5.3.8> philosophy), technical
  budgets (radiometric/geometric/BOA accuracy, throughput, memory) are per-profile and verified locally; the
  margin status is reported at each milestone. The design imposes no budget that the block model cannot meet
  by sizing (C-COM-CHUNK) and parallelism.

---

## <8> Demonstration that the design meets the requirements

The DJF must show that the design meets all requirements (ECSS-E-ST-40C §4.2.5). At CDR this is established
by **complete traceability** plus the **verification/validation design**; executed results are added to the
DJF at QR/AR (SVR, RD-4):

1. **Requirement → design coverage.** Every `REQ-*` is allocated to at least one design component, and every
   component traces to at least one `REQ-*` (no orphans, no unimplemented requirements). The forward and
   backward traces are in **SDD <6.1>/<6.2>** and the authoritative matrix **RD-7**; each component also
   links to its DPM module (`DPM-M-*`) and ATBD algorithm (`ALG-*`).
2. **Design decision → requirement coverage.** Every decision in <5> cites its driving `REQ-*`/`R-*`
   (<5.15>), so the *rationale* layer is itself traceable to the requirements it serves.
3. **Verification/validation design.** The merged V&V plan (RD-3: SVerP+SValP+SUITP) defines the unit,
   integration and validation test design, including the per-stage tolerances (REQ-D-05; DPM/ATBD) and the
   methods (Test/Inspection/Analysis/Review) recorded in the SRS verification matrix (RD-8 <7>).
4. **Review approach.** The SRevP (RD-2) defines how each milestone (incl. CDR) checks design maturity and
   baselines it, and how the continuous MR/CI gates supply verification independence.
5. **Reuse adequacy.** The SRF (RD-6) shows the reused components are fit, licence-compatible and
   reuse-risk-assessed.

Together these show, at the CDR design-freeze, that the design **can** meet the requirements; the SVR (RD-4)
records that it **does**, at QR.

---

## <9> Critical-software-component measures — justification (Annex F <6>c)

This clause carries the detailed justification that SDD <6.3> defers to the DJF, per ECSS-Q-ST-80 §6.2.2.4
(minimising critical components) and ECSS-E-ST-40C Annex F <6>c.

**Criticality context.** `msi-processor` is **Category C**: a software failure produces only degraded or
incorrect data products, recoverable by reprocessing — no safety, mission-loss or space-segment consequence
(SDP <5.6>; severity ≤ Major). The residual hazard class is **product-data integrity** (REQ-SAF-01).

**Measures provided (design, not extra mechanism).** The integrity of the product is protected by design
features that exist for functional reasons and double as the criticality measures:

- **No hard-coded instrument constants in the core** (DEC-03; REQ-D-04) — a calibration error is a *data*
  fix (ADF/profile swap), not a code change, shrinking the critical code surface.
- **Pure-core isolation behind a tested interface** (DEC-04; REQ-D-03) — numerical kernels are
  unit-verifiable in isolation and off-platform, with per-stage tolerances in the DPM/ATBD (REQ-D-05).
- **Bounded cyclomatic complexity** (`xenon` thresholds) per `core`/`unit`; the thin-wrapper template keeps
  CPM-facing code trivial (REQ-D-04, REQ-Q-04).
- **Typed fault containment** — the `MsiProcessorError` hierarchy makes every failure a typed, flagged,
  reported event at the PU boundary; no silent cross-DAG propagation (DEC-10).
- **Determinism / reproducibility** for a fixed input/ADF/profile/processor quadruple, incl. profile-fixed
  RANSAC seeds (DEC-12; REQ-F-DEP-02, REQ-D-05).
- **Integrity triad: fail-stop + per-pixel QA flags + provenance** (DEC-10, DEC-14; REQ-F-DEP-01,
  REQ-F-QA-02, REQ-F-PRD-02) — no partial or misleading product is ever published as complete.

**Special measures deliberately NOT levied.** No software-criticality-driven *special* measures —
**redundancy, watchdog, N-version programming, defensive hardware fault tolerance** — are applied. The
justification: such measures address safety/availability hazards (Category A/B) that do not exist here; the
hazard is *data integrity*, which is fully addressed by detect-and-stop (fail-stop) plus localised QA and
provenance, and any incorrect product is recoverable by reprocessing. Adding redundancy/N-version would add
cost and complexity (against REQ-D-04 minimisation) with no risk reduction at Category C. This records and
closes Annex F <6>c.

---

## <10> Design decisions deferred to implementation (`[impl]`)

A small set of element-level choices are legitimately finalised during implementation (post-CDR); their
**interfaces and selection criteria are fixed at CDR**, so the design freeze holds. Each is recorded as a
deferred decision with its resolution criterion and owning component.

| Id | Deferred decision | Fixed at CDR | Resolution criterion (when/how decided) | Component | Driver / risk |
|---|---|---|---|---|---|
| DEC-D1 | Atmospheric **RT engine** (6S vs libRadtran vs LUT) and **scene classifier** | C-PU-ATM interface, DPM-M-ATM/ALG-ATM-* | Down-select in implementation against BOA accuracy budget + L2 acceptance criteria (SValP); prototype-driven | C-PU-ATM | REQ-F-ATM-*, R-06 |
| DEC-D2 | **L0 bit-codec body** (packet/CRC/corruption handling beyond the zero-line rule) | `decode`/`detect_and_truncate_loss` signatures, QA semantics | Implemented against the NDA-bound sensor spec; private, profile-bound | C-PU-L0 | REQ-F-L0-*, ATBD <5.1> |
| DEC-D3 | **Geolocation kernel** (rigorous collinearity model internals; GCP/DEM resampling tunings) | IF-CORE-01, DPM-M-GEO/ALG-GEO-* | Implemented + tuned against GCP residual budget (CE90) | C-PU-GEO | REQ-F-GEO-*, R-09 |
| DEC-D4 | **Coregistration matcher/filter tunings** (SIFT/FLANN/RANSAC thresholds) | IF-CORE-01, acceptance check (match count/residual) | Tuned against the band-coregistration accuracy budget; profile-fixed seeds | C-PU-COR | REQ-F-COR-*, R-03 |
| DEC-D5 | **Optional-stage validation status** (enhancement, pansharpen default-off until validated) | Stages present, toggleable, default-off | Enabled per profile only after the stage is validated (SValP) | C-PU-ENH, C-PU-PAN | REQ-F-ENH-03 |
| DEC-D6 | **CPM computing-model JSON exact keys** (`[TBC@CDR]` against 2.8.1) | The model contract (inputs/adfs/outputs/params/modes) | Confirmed against the pinned `eopf==2.8.1` schema at CDR finalisation | all C-PU-* | REQ-I-07, DEC-02 |

These are recorded so the CDR can confirm that nothing *architectural* is deferred — only bodies and
tunings whose contracts are already fixed.

---

## <11> DJF constituents and references

The DJF is a file; this document is its design-justification head. Its constituents and their roles:

| DJF constituent | DRD (E-40 annex) | Role in the DJF | Reference | Status |
|---|---|---|---|---|
| **DJF — Design Justification** (this document) | §4.2.4/§4.2.5 concept | Decision rationale, trade-offs, make-or-buy, feasibility, criticality-measure justification | this file | Draft for CDR |
| SRevP — Software Review Plan | Annex P | Review approach (incl. CDR) and continuous MR/CI review; independence model | RD-2 | Baselined (SRR) |
| V&V plan (SVerP+SValP+SUITP) | Annexes I/J/K | Verification/validation/unit-integration **test design** showing the design can meet requirements | RD-3 | Baselined (PDR); SUITP at CDR |
| SVR — Software Verification Report | Annex M | Executed verification **results** (added to the DJF at QR) | RD-4 | At QR |
| SRF — Software Reuse File | Annex N | Reuse analysis, licences, reuse risks (supports the make-or-buy of <6>) | RD-6 | At CDR |
| Traceability matrix | E-40 §5.8 | Requirement→design→test closure (supports <8>) | RD-7 | At CDR |

This document does **not** restate requirements (SRS, RD-8), the design (SDD, RD-1), the algorithm
mathematics (DPM RD-10 / ATBD RD-11) or the concrete interfaces (ICD, RD-13); it justifies the design those
documents define, and binds each decision to its `REQ-*`, `R-*` and `C-*`.

---

*End of DJF — Design Justification (CDR issue). Authored per ECSS-E-ST-40C Rev.1 §4.2.4/§4.2.5 (DJF
concept) and Annex F <6>c, tailored for Category C / single-developer. Design decisions `DEC-*` trace to
the SRS (`REQ-*`, RD-8), Risk Register (`R-*`, RD-5) and SDD (`C-*`, RD-1). Implementation (SDP WP-5) and
the `[impl]`/`DEC-D*` deferred decisions are resolved only after CDR.*
