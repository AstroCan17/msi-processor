# Requirements Traceability Matrix (RTM)

| Field | Value |
|---|---|
| **Document** | RTM — Requirements Traceability Matrix (end-to-end, bidirectional) |
| **DRD ref** | ECSS-E-ST-40C Rev.1 §5.8 (traceability); Annex D <7> (SRS trace), Annex F <6> (design trace), Annex I/J <14>/<9> (verification trace) |
| **Container** | Design Justification File (DJF) — `compliance/traceability/`; referenced as RD-9 by the SRS, RD-11 by the SDD, RD-10 by the V&V Plan |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | CDR (Critical Design Review) |
| **Status** | Draft for CDR |

> This RTM is the consolidated, authoritative traceability artefact that every constituent document
> defers to (SRS <7>, SDD <6>, ICD <7>, V&V <14>, SSS <5.1>). It realises the **end-to-end** chain
> **SYS-\*** (SSS / RD-2) → **REQ-IF-\*** (IRD / RD-3) / **REQ-\*** (SRS / RD-4) → design components
> **C-\*** (SDD / RD-5) + processing modules **DPM-M-\*** (DPM / RD-6) + algorithms **ALG-\*** (ATBD /
> RD-7), bound to external interfaces **ICD-IF-\*** (ICD), and closed to **verification** (V&V Plan
> method T/A/I/R · tier A/B/C, validation task VT-1..VT-10). It provides both the **forward**
> (requirement → design → test) and **backward** (test/design → requirement; component/algorithm →
> requirement; upper-level → requirement) coverage, and an explicit **orphan / gap** analysis. This is
> the CDR traceability gate artefact; implementation (SDP WP-5) starts only after CDR.

---

## <1> Purpose, scope and method

**Purpose.** Demonstrate, at CDR, that (a) every software requirement decomposes from at least one
upper-level (system or interface) requirement; (b) every requirement is allocated to at least one
design component and, for processing requirements, to a DPM module and ATBD algorithm; (c) every
requirement is bound to at least one verification method and validation task; and, conversely, (d)
every upper-level requirement, design component, processing module and algorithm traces down to at
least one requirement — i.e. there are no orphans and no unverified or unimplemented requirements.

**Scope of identifiers covered.**

| Namespace | Tier | Source (authoritative) | Count |
|---|---|---|---|
| `SYS-*` | System requirement | SSS <5> (RD-2) | 66 |
| `REQ-IF-*` | Interface requirement | IRD <5> (RD-3) | 31 |
| `REQ-*` | Software requirement | SRS <5> (RD-4) | 95 |
| `C-*` | Design component | SDD <5.3>/<5.4> (RD-5) | 20 (+1 container `C-COMPUTING`) |
| `DPM-M-*` | Processing module | DPM <8> (RD-6) | 11 |
| `ALG-*` | Algorithm | ATBD <5> (RD-7) | 33 |
| `ICD-IF-*` | External interface | ICD <5.3> | 8 families (28 items) |
| `VT-1..VT-10` | Validation task | V&V <9> (RD-8) | 10 |

**Method (tailored, Category C / single-developer).** The matrix is maintained as the inverse of the
inline `Trace:` fields of the SRS/ICD/ATBD and the allocation/trace tables of the SDD (<5.3>, <6.1>),
DPM (<8>) and V&V Plan (<14>). It is the single source of truth; the per-document trace summaries are
its views. Where an upper-level correspondence is not stated verbatim in a source document it is
marked **(derived)** and its derivation basis is given. The forward/backward closure is intended to be
machine-checkable post-CDR (a CI lint that fails on any unresolved `REQ-*`).

**Legend.**
- **Method** — T (Test) · A (Analysis) · I (Inspection) · R (Review of design).
- **Tier** — A (CI-blocking, public, synthetic) · B (local/SDE integration, non-blocking in public CI) ·
  C (local numerical budget validation → SVR) · "—" (static / review evidence, no dynamic tier).
- **(opt)** — optional, profile-toggleable stage; not required for a valid baseline `L2A`.
- **[impl]** — code internal legitimately finalised in implementation (post-CDR), specified here at
  interface + algorithm level.
- **(new)** — no reuse heritage; designed in this project (atmospheric chain).

---

## <2> Applicable and reference documents

| Id | Document | Path |
|---|---|---|
| RD-1 | SDP — Software Development Plan | `compliance/software-development-plan.md` |
| RD-2 | SSS — Software System Specification (`SYS-*`) | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | IRD — Interface Requirements Document (`REQ-IF-*`) | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | SRS — Software Requirements Specification (`REQ-*`) | `compliance/drd/srs-software-requirements.md` |
| RD-5 | SDD — Software Design Document (`C-*`) | `compliance/drd/sdd-software-design.md` |
| RD-6 | DPM — Data Processing Model (`DPM-*`) | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | ATBD — Algorithm Theoretical Basis Document (`ALG-*`) | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | V&V Plan (SVerP/SValP/SUITP merged; `VT-*`) | `compliance/drd/vv-plan.md` |
| RD-9 | ICD — Interface Control Document (`ICD-IF-*`) | `compliance/drd/icd-interface-control.md` |
| AD-1 | ECSS-E-ST-40C Rev.1 (30 April 2025) — §5.8, Annex D/F/I/J | — |
| AD-2 | ECSS-Q-ST-80C Rev.2 — §6.2.6 verification | — |

---

## <3> Master end-to-end forward matrix — `REQ-*` → up / down / verify

The `REQ-*` (SRS) is the trace spine: each row gives the upstream parents (`SYS-*` and/or
`REQ-IF-*`), the implementing design component(s) `C-*`, the processing module / algorithm
(`DPM-M-*` / `ALG-*`), the bound external interface(s) `ICD-IF-*`, and the verification
(method · tier) and validation task. Upstream from the SRS `Trace:` fields (RD-4 <5>); design from
SDD <5.3>/<6.1> (RD-5); module/algorithm from DPM <8> and ATBD <5>; verification from V&V <14> and
<9>. Secondary `C-COM-*` services used by every PU wrapper (PRODUCT, ADF, PROFILE, PROV, QAFLAG,
CHUNK) are listed once in <5.3> and abbreviated here to the stage-distinctive ones.

### <3.1> Functional requirements (`REQ-F-*`)

| REQ-* | Summary | Upstream `SYS-*` | Upstream `REQ-IF-*` | Design `C-*` | `DPM-M-*` / `ALG-*` | `ICD-IF-*` | Verify (method·tier) | VT |
|---|---|---|---|---|---|---|---|---|
| REQ-F-L0-01 | Decode `L0c`→per-band/detector samples | SYS-CAP-01 | REQ-IF-IN-L0-01, REQ-IF-SW-04 | C-PU-L0, C-COM-PRODUCT | DPM-M-L0 / ALG-L0-DEC | ICD-IF-L0 | T,I·A | VT-1,2 |
| REQ-F-L0-02 | Lost-packet/line-loss detect+flag | SYS-CAP-01, SYS-OBS-02 | — | C-PU-L0, C-COM-QAFLAG | DPM-M-L0 / ALG-L0-LOSS | ICD-IF-L0 | T·A | VT-1 |
| REQ-F-L0-03 | Legality checks; resolve profile/ADF | SYS-CAP-01 | REQ-IF-IN-L0-02, REQ-IF-SEC-01 | C-PU-L0, C-COM-PROFILE, C-COM-ADF | DPM-M-L0 | ICD-IF-L0, ICD-IF-PROF | T·A | VT-1 |
| REQ-F-L0-04 | Assemble self-describing `L1A` EOProduct | SYS-CAP-01 | REQ-IF-IN-L0-01, REQ-IF-OUT-02 | C-PU-L0, C-COM-PRODUCT | DPM-M-L0 | ICD-IF-OUT | T,I·A | VT-1 |
| REQ-F-L0-05 | `L0` read-only | — | REQ-IF-IN-L0-03, REQ-IF-SEC-03 | C-PU-L0, C-COM-IO | DPM-M-L0 | ICD-IF-L0 | A,I·— | VT-9 |
| REQ-F-RAD-01 | Dark/DSNU subtraction | SYS-CAP-02 | REQ-IF-IN-ADF-01, REQ-IF-IN-ADF-02 | C-PU-RAD, C-COM-ADF | DPM-M-RAD / ALG-RAD-DARK | ICD-IF-ADF | T,A·A+C | VT-1,3 |
| REQ-F-RAD-02 | NUC/PRNU flat-field | SYS-CAP-02 | REQ-IF-IN-ADF-01 | C-PU-RAD, C-COM-ADF | DPM-M-RAD / ALG-RAD-NUC | ICD-IF-ADF | T,A·A+C | VT-1,3 |
| REQ-F-RAD-03 | Bad-pixel detect + replace + flag | SYS-CAP-02, SYS-OBS-02 | — | C-PU-RAD, C-COM-QAFLAG | DPM-M-RAD / ALG-RAD-BPR | — | T·A | VT-1 |
| REQ-F-RAD-04 | Saturation/no-data clip + flag | SYS-CAP-02, SYS-OBS-02 | — | C-PU-RAD, C-COM-QAFLAG | DPM-M-RAD / ALG-RAD-SAT | — | T·A | VT-1 |
| REQ-F-RAD-05 (opt) | Derive NUC gain/offset ADF | SYS-CAP-02, SYS-MNT-02 | REQ-IF-IN-ADF-01 | C-PU-RAD (calib mode) | DPM-M-RAD (DPM-ADF-NUC) / ALG-RAD-NUC | ICD-IF-ADF | T,A·B | VT-1 |
| REQ-F-TOA-01 | DN→TOA radiance | SYS-CAP-02, SYS-CAP-03 | REQ-IF-IN-ADF-01 | C-PU-TOA, C-COM-ADF | DPM-M-TOA / ALG-TOA-RAD | ICD-IF-ADF | T,A·A+C | VT-1,3 |
| REQ-F-TOA-02 (opt) | TOA radiance→reflectance | SYS-CAP-03 | — | C-PU-TOA | DPM-M-TOA / ALG-TOA-REF | — | T,A·A+C | VT-1,3 |
| REQ-F-TOA-03 | Emit `L1B` EOProduct + QA + prov | SYS-CAP-08 | REQ-IF-OUT-02 | C-PU-TOA, C-COM-PRODUCT, C-COM-PROV | DPM-M-TOA | ICD-IF-OUT | T,I·A | VT-1 |
| REQ-F-ENH-01 (opt) | Configurable per-band denoise | SYS-CAP-02, SYS-ADP-01 | — | C-PU-ENH | DPM-M-ENH / ALG-ENH-BWLP/WAVE/PCA/MA/GAUSS/FFTDARK | — | T,A·A+C | VT-1 |
| REQ-F-ENH-02 (opt) | Deconvolution/sharpening | SYS-CAP-02, SYS-ADP-01 | — | C-PU-ENH | DPM-M-ENH / ALG-ENH-DECONV | — | T,A·A+C | VT-1 |
| REQ-F-ENH-03 | Toggleable; default-off; QA impact | SYS-ADP-01, SYS-QUA-04 | — | C-PU-ENH, C-PU-QA | DPM-M-ENH / DPM-M-QA | — | T,R·A | VT-1 |
| REQ-F-COR-01 | Inter-band co-registration to ref band | SYS-CAP-04 | REQ-IF-CAP-01 | C-PU-COR | DPM-M-COR / ALG-COR-FEAT/HOM/WARP | — | T,A·A | VT-1,4 |
| REQ-F-COR-02 | Residual ≤ `BAND_COREG` | SYS-CAP-05 | — | C-PU-COR, C-PU-QA | DPM-M-COR | — | A,T·C | VT-4 |
| REQ-F-COR-03 | Fail-stop on insufficient matches | SYS-CAP-05, SYS-RAM-02 | — | C-PU-COR, C-COM-ORC, C-COM-QAFLAG | DPM-M-COR | ICD-IF-DIAG | T·A | VT-1 |
| REQ-F-GEO-01 | Viewing-model geolocation | SYS-CAP-04 | REQ-IF-IN-ADF-01, REQ-IF-IN-L0-01 | C-PU-GEO, C-COM-ADF | DPM-M-GEO / ALG-GEO-ORBIT/GSD | ICD-IF-ADF | T,A·A+B | VT-1,4 |
| REQ-F-GEO-02 | DEM ortho + GCP + resample to CRS | SYS-CAP-04, SYS-ADP-02 | — | C-PU-GEO, C-COM-ADF | DPM-M-GEO / ALG-GEO-GCP/ORTHO/RESAMP | ICD-IF-ADF | T,A·A+B | VT-1,4 |
| REQ-F-GEO-03 | Geolocation ≤ `GEO_CE90` | SYS-CAP-05 | — | C-PU-GEO, C-PU-QA | DPM-M-GEO | — | A,T·C | VT-4 |
| REQ-F-GEO-04 | Emit `L1C` EOProduct + CRS/geoloc | SYS-CAP-08 | REQ-IF-OUT-02 | C-PU-GEO, C-COM-PRODUCT | DPM-M-GEO | ICD-IF-OUT | T,I·A | VT-1 |
| REQ-F-PAN-01 (opt) | MS↔PAN fusion to high-res MS | SYS-CAP-04, SYS-ADP-01 | — | C-PU-PAN | DPM-M-PAN / ALG-PAN-ALIGN/FUSE | — | T,A·A+B | VT-1 |
| REQ-F-PAN-02 (opt) | Preserve spectral fidelity; QA | SYS-QUA-04 | — | C-PU-PAN, C-PU-QA | DPM-M-PAN | — | A,T·C | VT-1 |
| REQ-F-ATM-01 (new) | Retrieve/ingest AOT + water vapour | SYS-CAP-06 | REQ-IF-IN-ADF-01 | C-PU-ATM, C-COM-ADF | DPM-M-ATM / ALG-ATM-PAR | ICD-IF-ADF | T,A·A+C | VT-1,5 |
| REQ-F-ATM-02 (new) | TOA→BOA surface reflectance | SYS-CAP-06 | — | C-PU-ATM | DPM-M-ATM / ALG-ATM-RT | — | T,A·A+C | VT-1,5 |
| REQ-F-ATM-03 (new) | Scene classification + cloud/shadow mask | SYS-CAP-07, SYS-OBS-02 | — | C-PU-ATM, C-COM-QAFLAG | DPM-M-ATM / ALG-ATM-SCM | — | T·A | VT-1 |
| REQ-F-ATM-04 (new) | Emit `L2A` EOProduct | SYS-CAP-08 | REQ-IF-OUT-02 | C-PU-ATM, C-COM-PRODUCT | DPM-M-ATM | ICD-IF-OUT | T,I·A | VT-1 |
| REQ-F-QA-01 | Per-band/stage metrics (SNR/RMSE/PSNR/MSE/var) | SYS-OBS-02, SYS-OBS-03, SYS-QUA-04 | — | C-PU-QA | DPM-M-QA / ALG-QA-SNR/RMSE/PSNR/MSE/VAR | ICD-IF-OUT | T·A+C | VT-1,3,4,5 |
| REQ-F-QA-02 | Per-pixel QA flag propagation | SYS-OBS-02, SYS-CAP-08 | — | C-PU-QA, C-COM-QAFLAG | DPM-M-QA | ICD-IF-OUT | T·A | VT-1 |
| REQ-F-PRD-01 | Write cloud-native Zarr EOProduct | SYS-CAP-08 | REQ-IF-OUT-01, REQ-IF-OUT-02 | C-COM-PRODUCT | DPM-M-PRD | ICD-IF-OUT, ICD-IF-SW | T,I·A+B | VT-2 |
| REQ-F-PRD-02 | Provenance (input/ADF/profile/version ids) | SYS-OBS-01 | REQ-IF-CAP-03, REQ-IF-OUT-04 | C-COM-PROV, C-COM-PRODUCT | DPM-M-PRD | ICD-IF-OUT | I,T·A | VT-1 |
| REQ-F-ORC-01 | PU declares I/O; run level/sub/full-chain | SYS-CAP-10 | REQ-IF-CAP-01, REQ-IF-SW-01 | C-COM-ORC, C-COMPUTING | DPM-M-PRD / DPM-BKP-* | ICD-IF-TRIG, ICD-IF-SW | T,R·A | VT-2 |
| REQ-F-ORC-02 | Chunked, bounded memory, optional Dask | SYS-CAP-11 | REQ-IF-CAP-02 | C-COM-CHUNK, C-COM-ORC | DPM-PRM-GEN-02 | ICD-IF-SW | T,A·B | VT-2,6 |
| REQ-F-DEP-01 | Fail-stop; no partial product published | SYS-OPS-02, SYS-RAM-02, SYS-SAF-01 | — | C-COM-ORC | DPM-M-PRD | ICD-IF-DIAG | T·A | VT-2,7 |
| REQ-F-DEP-02 | Deterministic / reproducible | SYS-RAM-01 | REQ-IF-CAP-04 | all Cores (seeds), C-COM-ORC | ATBD <6> / <4.3> | — | T,A·A+B | VT-1,2 |

### <3.2> Performance requirements (`REQ-P-*`)

| REQ-* | Summary | Upstream `SYS-*` | Design `C-*` | `DPM` | Verify | VT |
|---|---|---|---|---|---|---|
| REQ-P-01 | `L1B` radiometric accuracy `RAD_ACC` | SYS-CAP-03, SYS-QUA-04 | C-PU-RAD, C-PU-TOA, C-PU-QA | DPM <7.4> | A,T·C | VT-3 |
| REQ-P-02 | `GEO_CE90` + `BAND_COREG` | SYS-CAP-05 | C-PU-COR, C-PU-GEO, C-PU-QA | DPM <7.4> | A,T·C | VT-4 |
| REQ-P-03 | `L2A` surface reflectance `BOA_ACC` | SYS-QUA-04 | C-PU-ATM, C-PU-QA | DPM <7.4> | A,T·C | VT-5 |
| REQ-P-04 | End-to-end throughput `THRU_SCENE` | SYS-RES-04 | C-COM-CHUNK, C-COM-ORC | DPM <7.4> | A,T·C | VT-6 |
| REQ-P-05 | Peak per-worker memory `MEM_BUDGET` | SYS-RES-03 | C-COM-CHUNK | DPM-PRM-GEN-02 | A,T·C | VT-6 |

### <3.3> Interface, operational and resource requirements (`REQ-I-*`, `REQ-O-*`, `REQ-R-*`)

| REQ-* | Summary | Upstream `SYS-*` | Upstream `REQ-IF-*` | Design `C-*` | `ICD-IF-*` | Verify | VT |
|---|---|---|---|---|---|---|---|
| REQ-I-01 | Comply with all `REQ-IF-*` + ICD/PSFD | — | REQ-IF-* (all) | C-COM-PRODUCT, C-COM-ORC | ICD-IF-* (all) | R,I·— | VT-9 |
| REQ-I-02 | CPM Python API + non-interactive CLI | SYS-IF-01 | REQ-IF-HMI-01, REQ-IF-SW-01 | C-COM-CLI | ICD-IF-HMI, ICD-IF-SW | T,I·A+B | VT-7 |
| REQ-I-03 | Consume `L0c`/ADF per ICD; read-only | SYS-IF-02 | REQ-IF-IN-L0-01, REQ-IF-IN-ADF-01, REQ-IF-IN-L0-03, REQ-IF-IN-ADF-04 | C-PU-L0, C-COM-ADF, C-COM-IO | ICD-IF-L0, ICD-IF-ADF | T·A+B | VT-1,2 |
| REQ-I-04 | Produce Zarr stores on S3/POSIX, chunked | SYS-IF-03 | REQ-IF-OUT-01, REQ-IF-OUT-03 | C-COM-PRODUCT, C-COM-IO | ICD-IF-OUT | T,I·A+B | VT-2 |
| REQ-I-05 | Invocable via CPM triggering payload | SYS-OPS-01 | REQ-IF-COM-01 | C-COM-ORC | ICD-IF-TRIG | T,I·A+B | VT-7 |
| REQ-I-06 | URI-referenced, location-transparent I/O | SYS-IF-04 | REQ-IF-COM-02, REQ-IF-COM-03 | C-COM-IO | ICD-IF-TRIG | T·A+B | VT-2,7 |
| REQ-I-07 | EOPF data-model naming conventions | SYS-DES-06 | REQ-IF-OUT-02 | C-COM-PRODUCT | ICD-IF-OUT | I·— | VT-9 |
| REQ-O-01 | Operable as batch job (CLI/API), per level | SYS-OPS-01 | REQ-IF-COM-01, REQ-IF-CAP-01 | C-COM-CLI, C-COM-CONFIG | ICD-IF-HMI, ICD-IF-TRIG | T·A+B | VT-7 |
| REQ-O-02 | Structured logs + processing report | SYS-OPS-02, SYS-OBS-01 | — | C-COM-ORC | ICD-IF-DIAG | T·A+B | VT-7 |
| REQ-O-03 | Completion status + machine-readable diag | — | REQ-IF-CAP-05 | C-COM-ORC | ICD-IF-DIAG | T·A+B | VT-7 |
| REQ-O-04 | Modes configured/idle→processing→error | SYS-CAP-10 | — | C-COM-ORC | ICD-IF-DIAG | R,T·A | VT-7 |
| REQ-R-01 | x86-64 Linux multi-core CPU, no GPU | SYS-RES-01 | — | architecture-wide | ICD-IF-SW-05 | T·B | VT-6,8 |
| REQ-R-02 | S3-compatible/POSIX; no special HW | SYS-RES-02 | REQ-IF-HW-01 | C-COM-IO | ICD-IF-SW-05 | T·B | VT-8 |
| REQ-R-03 | Python 3.11 + `eopf==2.8.1` + stack | SYS-RES-05, SYS-DES-03 | REQ-IF-SW-03 | architecture-wide | ICD-IF-SW-03 | I,T·A+B | VT-8 |
| REQ-R-04 | Memory scales with chunk; CPU with tiles | SYS-RES-03 | — | C-COM-CHUNK | — | A,T·C | VT-6 |
| REQ-R-05 | No hard real-time constraint (N/A closure) | SYS-RES-04 | — | — | — | R·— | — |

### <3.4> Design, security, portability, quality, RAMS, delivery, data, HF, adaptation

| REQ-* | Summary | Upstream `SYS-*` | Upstream `REQ-IF-*` | Design `C-*` | `ICD-IF-*` | Verify | VT |
|---|---|---|---|---|---|---|---|
| REQ-D-01 | PU/EOProduct config-driven pipeline | SYS-DES-01 | REQ-IF-SW-01 | architecture, C-COMPUTING | ICD-IF-SW | R·— | VT-9 |
| REQ-D-02 | Coding standards + ECSS tailoring | SYS-DES-02, SYS-QUA-01 | — | toolchain | — | I·— | VT-9 |
| REQ-D-03 | Pure framework-independent core | — | REQ-IF-SW-04 | all Cores (core/unit split) | — | T·A | VT-1 |
| REQ-D-04 | No hard-coded constants; bounded complexity | SYS-CAP-09, SYS-QUA-05 | — | all Cores, C-SENSORS | — | I,A·— | VT-9 |
| REQ-D-05 | Numerical accuracy/determinism management | SYS-RAM-01, SYS-QUA-04 | — | all Cores | — | A,T·A | VT-1 |
| REQ-D-06 | Reuse only SRF components + licences | SYS-DES-03 | REQ-IF-SW-02 | reused comps (SRF) | ICD-IF-SW | I·— | VT-9 |
| REQ-D-07 | New sensor = new profile, no core change | SYS-DES-07, SYS-CAP-09 | REQ-IF-AD-01 | C-SENSORS, C-COM-PROFILE | ICD-IF-PROF | T,R·A+B | VT-10 |
| REQ-D-08 | No in-flight modification (N/A closure) | — (SSS <5.12>) | — | — | — | R·— | — |
| REQ-D-09 | Zarr + EOPF/CF + STAC fields | SYS-DES-04 | REQ-IF-OUT-02 | C-COM-PRODUCT | ICD-IF-OUT | I,T·A | VT-9 |
| REQ-S-01 | Code public; `L0`/ADF private, by URI | SYS-SEC-01 | REQ-IF-SEC-02, REQ-IF-IN-ADF-03 | C-COM-ADF, C-COM-IO | ICD-IF-ADF | I,A·— | VT-9 |
| REQ-S-02 | Credentials via env/CI only | SYS-SEC-02 | — | C-COM-IO, C-COM-CONFIG | — | I,T·A | VT-9 |
| REQ-S-03 | Least privilege (read in, write out) | SYS-SEC-03 | REQ-IF-SEC-03 | C-COM-IO | ICD-IF-ADF, ICD-IF-OUT | A,I·— | VT-9 |
| REQ-S-04 | Verify id/version of `L0`/ADF/profile | — | REQ-IF-SEC-01 | C-COM-ADF, C-COM-PROFILE | ICD-IF-ADF | T·A | VT-1 |
| REQ-S-05 | Output carries provenance ids only | — | REQ-IF-SEC-02, REQ-IF-CAP-03 | C-COM-PROV | ICD-IF-OUT | I,A·— | VT-9 |
| REQ-PORT-01 | SDE↔local relocatable (config only) | SYS-QUA-03 | — | Core/Wrapper split, C-COM-IO | — | T,I·B | VT-8 |
| REQ-PORT-02 | Location-transparent I/O | — | REQ-IF-COM-02 | C-COM-IO | ICD-IF-TRIG | T·B | VT-2 |
| REQ-PORT-03 | Local-FS path on CI shell runner | — (SYS-VV-02) | REQ-IF-COM-03 | C-COM-IO, C-COM-CHUNK | ICD-IF-TRIG-03 | T·A | VT-1 |
| REQ-Q-01 | ECSS-Q-80 Cat C + quality gates | SYS-QUA-01 | — | toolchain | — | I·— | VT-9 |
| REQ-Q-02 | Test coverage meets gate | SYS-QUA-02 | — | `tests/` | — | T·A | VT-9 |
| REQ-Q-03 | Numerical objectives validated locally | SYS-QUA-04 | — | C-PU-QA | DPM <7.4> | A,T·C | VT-3,4,5 |
| REQ-Q-04 | Maintainability: reuse + bounded complexity | SYS-QUA-05 | — | C-SENSORS, all Cores | — | I,A·— | VT-9 |
| REQ-REL-01 | Deterministic/reproducible (via DEP-02) | SYS-RAM-01 | — | all Cores | — | T,A·A+B | VT-1,2 |
| REQ-REL-02 | Resumable at level granularity | SYS-RAM-02 | — | C-COM-ORC | DPM-BKP-* | T·A+B | VT-2 |
| REQ-REL-03 | No availability target (N/A closure) | SYS-RAM-03 | — | — | — | R·— | — |
| REQ-M-01 | GitLab issue→branch→MR + SemVer | SYS-MNT-01 | — | repo workflow | — | R·— | VT-9 |
| REQ-M-02 | Cal/aux update = swap data, no code change | SYS-MNT-02 | REQ-IF-IN-ADF-03 | C-COM-ADF | ICD-IF-ADF | T,R·B | VT-2 |
| REQ-M-03 | Procedure for `eopf` bump + re-V&V | SYS-MNT-03 | REQ-IF-SW-03 | process | — | R·— | VT-9 |
| REQ-M-04 | Per-stage modular structure | SYS-QUA-05 | REQ-IF-SW-04 | core/unit/profile split | — | I·— | VT-9 |
| REQ-SAF-01 | No safety-critical fn; data-integrity triad | SYS-SAF-01 | — | C-COM-QAFLAG, C-COM-PROV, C-COM-ORC | — | R·— | VT-9 |
| REQ-DEL-01 | Versioned wheels + docs from tagged CI | SYS-DEL-01 | — | CI delivery | — | T,I·A | VT-9 |
| REQ-DEL-02 | No private data in artefacts; tag integrity | SYS-DEL-02 | REQ-IF-SEC-02 | CI delivery | — | I·— | VT-9 |
| REQ-DEL-03 | Zarr product spec in delivered config | SYS-DES-04 | — | C-COM-PRODUCT | ICD-IF-OUT | I·— | VT-9 |
| REQ-DAT-01 | Output data model per ICD/PSFD | SYS-DES-04, SYS-DES-06 | REQ-IF-OUT-02 | C-COM-PRODUCT | ICD-IF-OUT | I,T·A | VT-9 |
| REQ-DAT-02 | Private ADF store external; id/version/schema | SYS-ADP-02 | REQ-IF-IN-ADF-01, REQ-IF-IN-ADF-02 | C-COM-ADF | ICD-IF-ADF | I,R·— | VT-9 |
| REQ-DAT-03 | Profile schema versioned + load-validated | SYS-ADP-03 | REQ-IF-AD-04 | C-COM-PROFILE, C-SENSORS | ICD-IF-PROF | T·A | VT-1,10 |
| REQ-HF-01 | CLI/config/logs only; no GUI | SYS-IF-05 | REQ-IF-HMI-01 | C-COM-CLI | ICD-IF-HMI | I·— | VT-9 |
| REQ-HF-02 | Report human + machine readable | SYS-OPS-02 | — | C-COM-ORC | ICD-IF-DIAG | T,I·A | VT-7 |
| REQ-AD-01 | Sensor-agnostic via profile | SYS-ADP-01, SYS-CAP-09 | REQ-IF-AD-01 | C-SENSORS, C-COM-PROFILE | ICD-IF-PROF | R,T·A | VT-10 |
| REQ-AD-02 | Profile id/version; per-run selection | SYS-ADP-01 | REQ-IF-AD-02 | C-SENSORS, C-COM-CONFIG | ICD-IF-PROF | I,T·A | VT-10 |
| REQ-AD-03 | DEM/atmos by reference, not embedded | SYS-ADP-02 | REQ-IF-AD-03 | C-COM-CONFIG, C-COM-ADF | ICD-IF-PROF | T,I·A+B | VT-2 |
| REQ-AD-04 | Ops/site settings externalised | SYS-ADP-02 | REQ-IF-AD-03 | C-COM-CONFIG | ICD-IF-PROF, ICD-IF-TRIG | I,T·A+B | VT-7 |
| REQ-AD-05 | Clean `pip install` + acceptance run | SYS-VV-06 | — | packaging | — | T,I·B | VT-8 |

---

## <4> Interface trace — `REQ-IF-*` → `ICD-IF-*` → `REQ-*`

The interface spine. Forward (IRD interface requirement → ICD interface) and the implementing
software requirements from ICD <7.2>. The `SYS-*` column is **(derived)**: the IRD (RD-3 <5>) states
each interface requirement as Statement + Rationale and does **not** carry a per-requirement `SYS-*`
trace field (verified against the source); the system correspondence below is derived from the IRD
<4> product-perspective decomposition and the `SYS-*` co-cited by the implementing `REQ-*`. The
authoritative ICD↔REQ trace is ICD <7.1>/<7.2>.

| `REQ-IF-*` | Summary | `ICD-IF-*` (ICD <7.1>) | Implementing `REQ-*` (ICD <7.2>) | `SYS-*` (derived) |
|---|---|---|---|---|
| REQ-IF-CAP-01 | Staged interfaces + breakpoints | ICD-IF-TRIG-01/04, ICD-IF-SW-01 | REQ-F-ORC-01, REQ-O-01, REQ-I-01 | SYS-CAP-10 |
| REQ-IF-CAP-02 | Chunked / lazy access | (ICD-IF-OUT-03, ICD-IF-SW) | REQ-F-ORC-02, REQ-I-01 | SYS-CAP-11, SYS-RES-03 |
| REQ-IF-CAP-03 | Metadata / provenance propagation | ICD-IF-OUT-03 | REQ-F-PRD-02, REQ-S-05, REQ-I-01 | SYS-OBS-01 |
| REQ-IF-CAP-04 | Reproducible interface behaviour | (ICD-IF-OUT, ICD-IF-SW) | REQ-F-DEP-02, REQ-I-01 | SYS-RAM-01 |
| REQ-IF-CAP-05 | Completion status + diagnostics | ICD-IF-DIAG-01 | REQ-O-03, REQ-F-DEP-01, REQ-I-01 | SYS-OPS-02, SYS-OBS-02 |
| REQ-IF-IN-L0-01 | L0 input product interface | ICD-IF-L0-01 | REQ-F-L0-01/04, REQ-I-03 | SYS-IF-02, SYS-CAP-01 |
| REQ-IF-IN-L0-02 | L0 identification/selection metadata | ICD-IF-L0-02 | REQ-F-L0-03, REQ-I-03 | SYS-IF-02, SYS-ADP-01 |
| REQ-IF-IN-L0-03 | L0 immutability | ICD-IF-L0-03 | REQ-F-L0-05, REQ-I-03 | SYS-SEC-03, SYS-IF-02 |
| REQ-IF-IN-ADF-01 | Calibration ADF input interface | ICD-IF-ADF-01 | REQ-F-RAD-01/02, REQ-F-TOA-01, REQ-F-ATM-01, REQ-DAT-02, REQ-I-03 | SYS-IF-02, SYS-CAP-02 |
| REQ-IF-IN-ADF-02 | ADF id/versioning/validity | ICD-IF-ADF-02 | REQ-F-RAD-01, REQ-DAT-02 | SYS-OBS-01, SYS-MNT-02 |
| REQ-IF-IN-ADF-03 | Runtime-resolved, private ADF refs | ICD-IF-ADF-03 | REQ-S-01, REQ-M-02 | SYS-SEC-01, SYS-MNT-02 |
| REQ-IF-IN-ADF-04 | ADF immutability | ICD-IF-ADF-04 | REQ-I-03, REQ-S-03 | SYS-SEC-03 |
| REQ-IF-OUT-01 | Output as cloud-native Zarr | ICD-IF-OUT-01 | REQ-F-PRD-01, REQ-I-04 | SYS-IF-03, SYS-DES-04 |
| REQ-IF-OUT-02 | Self-describing EOProduct | ICD-IF-OUT-02 | REQ-F-PRD-01, REQ-DAT-01, REQ-D-09, REQ-I-07 | SYS-DES-06, SYS-CAP-08 |
| REQ-IF-OUT-03 | Storage backends + chunked access | ICD-IF-OUT-03, ICD-IF-SW-02 | REQ-I-04, REQ-R-02 | SYS-RES-02, SYS-IF-03 |
| REQ-IF-OUT-04 | Output id/versioning | (ICD-IF-OUT-02) | REQ-F-PRD-02 | SYS-OBS-01, SYS-DEL-02 |
| REQ-IF-SW-01 | Stages as `EOProcessingUnit`s | ICD-IF-SW-01 | REQ-D-01, REQ-F-ORC-01 | SYS-DES-01 |
| REQ-IF-SW-02 | `EOProduct`/`EOZarrStore` persistence | ICD-IF-SW-02 | REQ-D-06, REQ-I-04 | SYS-DES-03 |
| REQ-IF-SW-03 | Framework version binding `eopf==2.8.1` | ICD-IF-SW-03 | REQ-R-03, REQ-M-03 | SYS-RES-05, SYS-MNT-03 |
| REQ-IF-SW-04 | Testable algorithmic core | ICD-IF-SW-04 | REQ-D-03, REQ-M-04, REQ-F-L0-01 | SYS-DES-07, SYS-QUA-05 |
| REQ-IF-COM-01 | Triggering payload interface | ICD-IF-TRIG-01 | REQ-I-05, REQ-O-01 | SYS-OPS-01 |
| REQ-IF-COM-02 | URI-referenced, location-transparent I/O | ICD-IF-TRIG-02 | REQ-I-06, REQ-PORT-02 | SYS-IF-04 |
| REQ-IF-COM-03 | Local-FS fallback (constrained env) | ICD-IF-TRIG-03 | REQ-I-06, REQ-PORT-03 | SYS-VV-02, SYS-QUA-03 |
| REQ-IF-HW-01 | No direct hardware interface | ICD-IF-SW-05 | REQ-R-02 | SYS-RES-01 |
| REQ-IF-HMI-01 | Non-interactive invocation | ICD-IF-HMI-01 | REQ-I-02, REQ-HF-01 | SYS-IF-05 |
| REQ-IF-SEC-01 | Input identity and integrity | ICD-IF-L0-03, ICD-IF-ADF-02 | REQ-S-04, REQ-F-L0-03 | SYS-SEC-01, SYS-CAP-01 |
| REQ-IF-SEC-02 | Confidentiality of private inputs | ICD-IF-ADF-03, ICD-IF-OUT-03 | REQ-S-01/05, REQ-DEL-02 | SYS-SEC-01 |
| REQ-IF-SEC-03 | Least-privilege access | ICD-IF-ADF-04 | REQ-S-03, REQ-F-L0-05 | SYS-SEC-03 |
| REQ-IF-AD-01 | Sensor-agnostic chain via profile | ICD-IF-PROF-01 | REQ-AD-01, REQ-D-07 | SYS-ADP-01, SYS-CAP-09 |
| REQ-IF-AD-02 | Profile id/versioning/selection | ICD-IF-PROF-02 | REQ-AD-02 | SYS-ADP-01 |
| REQ-IF-AD-03 | Externalised ops/site settings | ICD-IF-PROF-01 | REQ-AD-03/04 | SYS-ADP-02 |
| REQ-IF-AD-04 | Profile validation at load | ICD-IF-PROF-01 | REQ-DAT-03 | SYS-ADP-03 |

**Closure.** All 31 `REQ-IF-*` map to ≥1 `ICD-IF-*` interface and to ≥1 implementing `REQ-*`
(no orphan interface requirement). All 8 `ICD-IF-*` families trace back to `REQ-IF-*` and forward to
`REQ-*` (ICD <7.2>; no orphan interface).

---

## <5> Backward coverage

### <5.1> System requirements `SYS-*` → `REQ-*` (every `SYS-*` covered)

From SRS <7.2> (forward coverage). Each of the 66 `SYS-*` is covered by ≥1 software requirement.

| `SYS-*` group | Covered by `REQ-*` |
|---|---|
| SYS-CAP-01 | REQ-F-L0-01..04 |
| SYS-CAP-02 | REQ-F-RAD-01..05, REQ-F-ENH-01/02, REQ-F-TOA-01 |
| SYS-CAP-03 | REQ-F-TOA-01/02, REQ-P-01 |
| SYS-CAP-04 | REQ-F-COR-01, REQ-F-GEO-01/02, REQ-F-PAN-01 |
| SYS-CAP-05 | REQ-F-COR-02, REQ-F-GEO-03, REQ-P-02 |
| SYS-CAP-06 | REQ-F-ATM-01/02 |
| SYS-CAP-07 | REQ-F-ATM-03 |
| SYS-CAP-08 | REQ-F-TOA-03, REQ-F-GEO-04, REQ-F-ATM-04, REQ-F-PRD-01 |
| SYS-CAP-09 | REQ-D-04, REQ-D-07, REQ-AD-01 |
| SYS-CAP-10 | REQ-F-ORC-01, REQ-O-04 |
| SYS-CAP-11 | REQ-F-ORC-02, REQ-R-04 |
| SYS-IF-01..05 | REQ-I-02..07, REQ-HF-01 |
| SYS-ADP-01..03 | REQ-AD-01..04, REQ-DAT-03 |
| SYS-RES-01..05 | REQ-R-01..05, REQ-P-04/05 |
| SYS-SEC-01..03 | REQ-S-01..03 |
| SYS-SAF-01 | REQ-SAF-01, REQ-F-DEP-01 |
| SYS-RAM-01..03 | REQ-REL-01..03, REQ-F-DEP-01/02 |
| SYS-QUA-01..05 | REQ-Q-01..04, REQ-D-02/04, REQ-P-01..03 |
| SYS-DES-01..08 | REQ-D-01..09, REQ-S-01, REQ-I-07 |
| SYS-OPS-01/02 | REQ-O-01..03, REQ-F-DEP-01, REQ-HF-02 |
| SYS-MNT-01..03 | REQ-M-01..04, REQ-F-RAD-05 |
| SYS-OBS-01..03 | REQ-F-PRD-02, REQ-F-QA-01/02 |
| SYS-DEVSEC-01..03 | REQ-S-02, REQ-Q-01, REQ-PORT-03 |
| SYS-DEL-01/02 | REQ-DEL-01..03 |
| SYS-VV-01..09 | REQ-Q-02/03, REQ-AD-05, REQ-PORT-03, SRS <6> / V&V (RD-8) |

### <5.2> Design components `C-*` → `REQ-*` (every component implements ≥1 requirement)

From SDD <5.3> allocation table (inverse). No orphan component.

| `C-*` | Package | Dev type | Allocated `REQ-*` | `DPM-M-*` / `ALG-*` |
|---|---|---|---|---|
| C-COMPUTING | `…computing` | new | REQ-D-01, REQ-F-ORC-01 | — |
| C-PU-L0 | `…computing.l0_decode` | reuse-adapt (`level_0`) | REQ-F-L0-01..05 | DPM-M-L0 / ALG-L0-* |
| C-PU-RAD | `…computing.radiometric` | reuse-adapt (`level_1.NUC`) | REQ-F-RAD-01..05 | DPM-M-RAD / ALG-RAD-* |
| C-PU-ENH | `…computing.enhancement` (opt) | reuse-adapt (`Denoiser`,`sharpening`) | REQ-F-ENH-01..03 | DPM-M-ENH / ALG-ENH-* |
| C-PU-TOA | `…computing.toa` | reuse-adapt (`level_1.TOA`) | REQ-F-TOA-01..03 | DPM-M-TOA / ALG-TOA-* |
| C-PU-COR | `…computing.coregistration` | reuse-adapt (`band_coreg`) | REQ-F-COR-01..03 | DPM-M-COR / ALG-COR-* |
| C-PU-GEO | `…computing.georeference` | reuse-adapt (`georeferencing_v1`) | REQ-F-GEO-01..04 | DPM-M-GEO / ALG-GEO-* |
| C-PU-PAN | `…computing.pansharpen` (opt) | reuse-adapt (`pansharp`) | REQ-F-PAN-01/02 | DPM-M-PAN / ALG-PAN-* |
| C-PU-ATM | `…computing.atmospheric` | **new** | REQ-F-ATM-01..04 | DPM-M-ATM / ALG-ATM-* |
| C-PU-QA | `…computing.qa` | reuse-adapt (`metrics_ips`) | REQ-F-QA-01/02 | DPM-M-QA / ALG-QA-* |
| C-SENSORS | `…sensors` | new | REQ-AD-01..04, REQ-DAT-03 | DPM <7.4> |
| C-COM-PRODUCT | `…common.product` | new (over CPM) | REQ-F-PRD-01, REQ-DAT-01, REQ-D-09 | DPM-M-PRD |
| C-COM-IO | `…common.io` | new (over CPM) | REQ-I-06, REQ-PORT-02/03 | — |
| C-COM-ADF | `…common.adf` | new | REQ-F-RAD-01, REQ-DAT-02, REQ-S-04 | DPM <7.2> / DPM-ADF-* |
| C-COM-PROFILE | `…common.profile` | new | REQ-AD-01/02, REQ-DAT-03 | ICD <5.3.6> |
| C-COM-PROV | `…common.provenance` | new | REQ-F-PRD-02, REQ-S-05 | DPM-M-PRD |
| C-COM-QAFLAG | `…common.qaflags` | new | REQ-F-QA-02 | ICD <5.3.3>E |
| C-COM-CHUNK | `…common.chunking` | new (over Dask) | REQ-F-ORC-02, REQ-R-04, REQ-P-05 | DPM-PRM-GEN-02 |
| C-COM-CONFIG | `…common.config` | new | REQ-AD-04, REQ-O-01 | ICD <5.3.5> |
| C-COM-ORC | `…common.orchestration` | new (over CPM) | REQ-F-ORC-01, REQ-F-DEP-01, REQ-I-05 | DPM-M-PRD |
| C-COM-CLI | `…common.cli` | new | REQ-I-02, REQ-O-01, REQ-HF-01 | ICD <5.3.7> |

> Design measures for the residual data-integrity hazard (Cat C, REQ-SAF-01) — pure-core isolation,
> no hard-coded constants, bounded complexity, typed fault containment, determinism, fail-stop+QA+
> provenance — are allocated across all Cores + C-COM-ORC/QAFLAG/PROV (SDD <6.3>).

### <5.3> Processing modules / algorithms `DPM-M-*` / `ALG-*` → `REQ-*` / `C-*`

From DPM <8> module table and ATBD <5> `Trace:` fields. Every module/algorithm traces to a
requirement and a component.

| `DPM-M-*` | `ALG-*` | `REQ-F-*` | `C-*` | Heritage (RD-10) |
|---|---|---|---|---|
| DPM-M-L0 | ALG-L0-DEC, ALG-L0-LOSS | REQ-F-L0-01..05 | C-PU-L0 | `level_0.py` decode/lost_package |
| DPM-M-RAD | ALG-RAD-DARK, -NUC, -BPR, -SAT | REQ-F-RAD-01..05 | C-PU-RAD | `level_1.py` NUC/dark/noise |
| DPM-M-ENH | ALG-ENH-BWLP/WAVE/PCA/MA/GAUSS/FFTDARK/DECONV | REQ-F-ENH-01..03 | C-PU-ENH | `level_1.Denoiser`,`sharpening` [impl tuning] |
| DPM-M-TOA | ALG-TOA-RAD, ALG-TOA-REF | REQ-F-TOA-01..03 | C-PU-TOA | `level_1.TOA` |
| DPM-M-COR | ALG-COR-FEAT, -HOM, -WARP | REQ-F-COR-01..03 | C-PU-COR | `band_coreg.py` |
| DPM-M-GEO | ALG-GEO-ORBIT/GSD/GCP/ORTHO/RESAMP | REQ-F-GEO-01..04 | C-PU-GEO | `georeferencing_v1.py` |
| DPM-M-PAN | ALG-PAN-ALIGN, ALG-PAN-FUSE | REQ-F-PAN-01/02 | C-PU-PAN | `pansharp.py` [impl tuning] |
| DPM-M-ATM | ALG-ATM-PAR, ALG-ATM-RT, ALG-ATM-SCM | REQ-F-ATM-01..04 | C-PU-ATM | **none — new (ATBD RD-7) [impl]** |
| DPM-M-QA | ALG-QA-SNR/RMSE/PSNR/MSE/VAR | REQ-F-QA-01/02 | C-PU-QA | `metrics_ips.py` |
| DPM-M-PRD | — (EOPF CPM) | REQ-F-PRD-01/02, REQ-F-ORC-01/02 | C-COM-PRODUCT, C-COM-PROV, C-COM-ORC | — |

**ADF / breakpoint / parameter families** (DPM internal IDs, consumed by the modules above):
`DPM-ADF-DARK/FLAT/NUC/BPM/RAD/SPEC/GEOM/DEM/GCP/ATM` → ICD-IF-ADF (REQ-IF-IN-ADF-*, REQ-DAT-02);
`DPM-BKP-L1A/RAD/ENH/L1B/COR/L1C/L2A` → REQ-F-ORC-01, REQ-REL-02 (breakpoints); `DPM-PRM-*` →
REQ-AD-01/04 (profile parameters), `DPM-PRM-GEN-02` → REQ-F-ORC-02/REQ-P-05 (chunking).

### <5.4> Validation tasks `VT-*` → requirement groups (V&V <9>)

| `VT-*` | Item under test | Requirement groups | Tier |
|---|---|---|---|
| VT-1 | Pure algorithmic cores | all `REQ-F-*` (+ REQ-D-03/05, REQ-PORT-03, REQ-S-04, REQ-DAT-03) | A |
| VT-2 | PU chain + sub-chains at breakpoints | REQ-F-ORC-01/02, REQ-F-PRD-01, REQ-F-DEP-01, REQ-REL-02, REQ-I-03/04, REQ-M-02, REQ-PORT-02, REQ-AD-03 | B |
| VT-3 | Radiometric accuracy `L1B` | REQ-P-01, REQ-F-RAD-*, REQ-F-TOA-*, REQ-Q-03 | C |
| VT-4 | Geometric accuracy `L1C` | REQ-P-02, REQ-F-GEO-*, REQ-F-COR-*, REQ-Q-03 | C |
| VT-5 | Surface-reflectance accuracy `L2A` | REQ-P-03, REQ-F-ATM-*, REQ-Q-03 | C |
| VT-6 | Performance | REQ-P-04/05, REQ-R-01/04, REQ-F-ORC-02 | C |
| VT-7 | Operational procedures | REQ-O-01..04, REQ-I-02/05, REQ-HF-02 | A/B |
| VT-8 | Installation & acceptance | REQ-AD-05, REQ-R-02/03, REQ-PORT-01 | B |
| VT-9 | Quality-requirements validation | REQ-Q-01/02/04, REQ-D-02/06/09, REQ-S-*, REQ-DEL-*, REQ-DAT-01/02, REQ-I-01/07, REQ-HF-01, REQ-M-*, REQ-SAF-01 | A |
| VT-10 | Adaptation / second profile | REQ-D-07, REQ-AD-01/02, REQ-DAT-03 | A/B |

---

## <6> Orphan and gap analysis

### <6.1> Forward closure (requirement → design → verification)

- **Design allocation.** All 95 `REQ-*` are allocated to ≥1 `C-*` (SDD <5.3>/<6.1>); design-/process-
  level requirements (REQ-D/Q/M/REL/SAF/DEL-*) map to the architecture, toolchain or workflow as
  recorded in <3.4>. **No unimplemented requirement.**
- **Verification binding.** All 95 `REQ-*` carry ≥1 method (T/A/I/R) and a tier or a documented
  static-evidence "—" (V&V <14>). Every `REQ-F-*` is in VT-1; budgeted requirements add a Tier-C VT.
  **No unverified requirement.**

### <6.2> Backward closure (upper-level / design / algorithm → requirement)

- **`SYS-*`:** all 66 covered by ≥1 `REQ-*` (<5.1>). No orphan system requirement.
- **`REQ-IF-*`:** all 31 covered by ≥1 `REQ-*` and ≥1 `ICD-IF-*` (<4>). No orphan interface requirement.
- **`C-*`:** all 20 components (+ container) allocate ≥1 `REQ-*` (<5.2>). No orphan component.
- **`DPM-M-*` / `ALG-*`:** all 11 modules and 33 algorithms trace to `REQ-F-*` and a `C-*` (<5.3>).
  No orphan module/algorithm.
- **`ICD-IF-*`:** all 8 families trace to `REQ-IF-*` and `REQ-*` (ICD <7.2>). No orphan interface.

### <6.3> Gaps, watch-items and recorded exclusions

| Ref | Item | Classification | Disposition |
|---|---|---|---|
| G-1 | `C-PU-ATM` / `DPM-M-ATM` / `ALG-ATM-PAR/RT/SCM` are **new** — no reuse heritage; RT engine + scene classifier `[impl]` (ATBD <5.8> "new/to-be-defined") | Design-complete, algorithm down-selection deferred to implementation | Track to SDP WP-5; interfaces frozen at CDR; re-validate via VT-1/VT-5. Risk in Risk Register. |
| G-2 | Tier-C numerical budgets `RAD_ACC`/`GEO_CE90`/`BAND_COREG`/`BOA_ACC`/`THRU_SCENE`/`MEM_BUDGET` (REQ-P-01..05, REQ-Q-03, REQ-F-COR-02/GEO-03/PAN-02) | Verification deferred (private real data) | Pass/fail verdicts to SVR; deferral recorded per V&V <8.8>; private numbers withheld (data policy). |
| G-3 | N/A closures **REQ-D-08, REQ-R-05, REQ-REL-03** | Verified by review, no test | Recorded; not a coverage gap (V&V <14>). |
| G-4 | Static-evidence requirements with tier "—" (REQ-F-L0-05, REQ-S-01/03/05, REQ-D-04, REQ-I-01/07, REQ-Q-01/04, REQ-DEL-02/03, REQ-DAT-02, REQ-HF-01, REQ-M-01/03/04, REQ-SAF-01) | Verified by I/A/R (no dynamic tier) | Evidenced by CI/grep/review artefacts; valid closure. |
| G-5 | Optional stages `(opt)` REQ-F-ENH-*, REQ-F-PAN-*, REQ-F-TOA-02, REQ-F-RAD-05 | Profile-toggleable; default-off where not validated | Verified when enabled; not required for baseline `L2A`. |
| G-6 | `[impl]` code internals: L0 bit-codec body (NDA), geolocation collinearity kernel, atmospheric RT/classifier, filter/matcher tunings | Specified at interface+algorithm level; bodies post-CDR | Expected per SDP; not a CDR gap. |
| G-7 | `QAFlag` bit 7 reserved `[TBC@CDR]` (SDD <5.4.1>) | Open design detail | Confirm/close at CDR; spare bit, no functional impact. |
| G-8 | System-level validation items (real E4 trigger, E5 dissemination at scale, Dask-gateway scaling, mission-volume throughput) | Beyond validation environment (V&V <13>) | Need host ground-segment support; do not affect the Cat-C item-level V&V conclusion. |

**Conclusion.** The traceability is **closed in both directions** with no orphan or unimplemented/
unverified requirement at this baseline. The only open technical item is the new atmospheric chain
(G-1) and the numerical-budget verifications pending private data (G-2); both are managed, recorded
deferrals, not traceability gaps. The matrix satisfies the CDR traceability gate (ECSS-E-ST-40C §5.8;
Annex D <7>, Annex F <6>, Annex I/J).

---

## <7> Maintenance

This RTM is a configuration item under Git, changed only through reviewed MRs (ECSS-M-ST-40C; SPAP).
It is regenerated/checked when any source `Trace:` field or trace table changes (SRS, IRD, ICD, SDD,
DPM, ATBD, V&V). A post-CDR CI lint shall fail the pipeline if any `REQ-*` lacks an upstream parent, a
design component, or a verification binding, making the forward/backward closure machine-checkable.
At QR/AR the verification-result columns (Tier-A pass evidence, Tier-B/C verdicts) are consolidated
from the SVR (RD-8) into this matrix.

*End of RTM. Authored per ECSS-E-ST-40C Rev.1 §5.8 / Annex D <7> / Annex F <6> / Annex I-J, tailored
Category C, single-developer. Upstream IDs reused verbatim from RD-2..RD-9; no new requirement,
design or algorithm IDs are introduced here (this is a consolidation artefact).*
