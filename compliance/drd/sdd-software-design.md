# Software Design Document (SDD) — Detailed (CDR)

| Field | Value |
|---|---|
| **Document** | SDD — Software Design Document (DETAILED / element-level) |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex F |
| **Container** | Design Definition File (DDF) — `compliance/drd/` (source), published subset in `docs/sdd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | **CDR** (detailed per-component design + internal-interface data; supersedes the PDR architectural issue) |
| **Status** | Draft for CDR |

> **Detailed issue (CDR).** This is the **detailed** issue of the SDD, the design constituent of the
> DDF (Annex F, F.1.2). It **supersedes** the PDR architectural issue: clauses <1>–<4> and <5.1>–<5.3>
> retain (and where needed refine) the baselined **architecture**; clause **<5.4>** is expanded from
> architectural granularity to the **element-level detailed design** required by Annex F <5.4.2>–<5.4.11>
> (component identifier/type/purpose/function/subordinates/dependencies/interfaces/resources/references/
> data, with data-element dtype/dimension/range/initial value); clause **<5.5>** gives the full
> internal-interface data design (Annex F <5.5>c/e), the file-level data structures previously postponed
> (<5.5>d); clause **<6>** closes the requirements→design traceability and the critical-component measures
> for the DJF. Per the SDP (RD-1) §5.2.3/§5.5.2 the full SDD is delivered at CDR; **implementation
> (SDP WP-5) starts only after CDR**. Element-level *code internals* that are legitimately fixed during
> implementation (the NDA-bound L0 bit-codec body, the rigorous collinearity geolocation kernel, the
> down-selected atmospheric RT engine and scene classifier, exact filter/matcher tunings) are specified
> here at interface + algorithm level and **explicitly marked `[impl]`** where the body is finalised
> post-CDR. Sensor-private numbers (calibration coefficients, accuracy budgets) stay in the profile/ADFs
> and are **not** reproduced (data policy, SRS <5.8>). This SDD does not re-specify requirements (SRS,
> RD-4) nor algorithm mathematics (DPM RD-6 / ATBD RD-7); it specifies *how the software is structured
> and built* to satisfy them, binding each design element to its `REQ-*`, `DPM-M-*`/`DPM-*` and `ALG-*`.

---

## <1> Introduction

**Purpose.** This SDD describes the software design of `msi-processor`, a generic high-resolution
**pushbroom multispectral imager (MSI)** ground-segment processor that transforms downlinked RAW
**Level-0 (`L0c`)** data into calibrated, orthorectified, atmospherically corrected products up to
**Level-2 (`L2A`)**. At this (CDR) issue it gives both the **architectural design** (static, dynamic and
behavioural views; patterns; standards; requirement allocation) and the **detailed design** (per-component
core signatures and data structures, the `EOProcessingUnit` wrapper contracts, the CPM computing-model
JSON, error handling and the element-level internal-interface data).

**Objective.** The SDD is the bridge from the baselined requirements (SRS, RD-4) and processing model
(DPM RD-6 / ATBD RD-7) to the implementation (SDP WP-5) and the unit/integration test design (V&V plan,
RD-8). Every design component traces upward to one or more `REQ-*` software requirements (clause <6>) and
to the DPM module(s) / ATBD algorithm(s) it realises, and is the unit of work for implementation and unit
test.

**Content.** Clause <2> lists applicable/reference documents; clause <3> adds design-specific terms.
Clause <4> gives the design overview — static architecture (<4.1>), dynamic architecture and
computational model (<4.2>), behaviour (<4.3>), interfaces context (<4.4>), long-lifetime design (<4.5>),
memory & PU budget (<4.6>), and design standards/conventions/trade-offs (<4.7>). Clause <5> gives the
software design proper — general (<5.1>), overall architecture (<5.2>), component design general (<5.3>),
**per-component detailed design (<5.4>)** and **internal-interface design (<5.5>)**. Clause <6> gives the
requirements→design traceability and the measures for critical components.

**Reason for preparation.** `msi-processor` is an **integration and ECSS productisation** effort: the
processing algorithms already exist as prior work (RD-9 / SRF RD-10) and the runtime platform is the EOPF
CPM (`eopf == 2.8.1`). This detailed SDD records, at CDR, the element-level design that turns that heritage
into a sensor-agnostic, configuration-driven, verifiable CPM product, so that implementation can begin
against a fixed, traceable design.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software product assurance | ECSS-Q-ST-80C Rev.2 |
| AD-3 | EOPF CPM — Product Structure & Format Definition (PSFD) / common data model | EOPF CPM docs (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Control Document (ICD) — `ICD-IF-*` | `compliance/drd/icd-interface-control.md` |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — `DPM-M-*`, `DPM-PR/ADF/PRM/BKP-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V plan (SVerP/SValP/SUITP merged) | `compliance/drd/vv-plan.md` |
| RD-9 | Prior work — multispectral pushbroom preprocessing pipeline (`02_scripts/`: `level_0.py`, `level_1.py`, `band_coreg.py`, `georeferencing_v1.py`, `pansharp.py`, `metrics_ips.py`) | RD-10 |
| RD-10 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-11 | `msi-processor` Traceability matrix (forward/backward, design→test) | `compliance/traceability/traceability-matrix.md` |
| RD-12 | EOPF CPM API documentation (`EOProduct`, `EOProcessingUnit`, `EOZarrStore`, triggering / computing model) | EOPF CPM (`eopf == 2.8.1`) |
| RD-13 | Cloud-native data conventions | Zarr v2/v3, CF metadata, STAC, GeoZarr |

---

## <3> Terms, definitions and abbreviated terms

The SSS <3>, IRD <3>, SRS <3>, DPM <3> and ATBD <3> glossaries apply in full. Only **design-specific**
terms not defined there are added here (per Annex F <3>).

| Term / abbr. | Definition |
|---|---|
| Processing Unit (PU) | An EOPF CPM `EOProcessingUnit`: the framework-facing executable component for one processing stage |
| Core | The pure, framework-independent algorithmic function set behind a PU (no CPM dependency); the unit of numerical test (`<pkg>.<stage>.core`) |
| Wrapper / adapter | The thin `EOProcessingUnit` subclass adapting a Core to the CPM runtime (`<pkg>.<stage>.unit`) |
| Computing model (JSON) | The per-PU CPM declarative model (`models/<name>_<version>.json`) declaring inputs, ADFs, outputs, parameters, modes; loaded via the CPM `processing_model()` |
| Triggering payload | The CPM job order (`workflow`+`io`+…) wiring PUs into a chain (ICD <5.3.5>); distinct from the per-PU computing model |
| Profile | Per-sensor configuration set (schema-validated) specialising the generic chain; data only, no algorithm code |
| ADF | Auxiliary Data File (private instrument calibration / auxiliary input), referenced by URI as a CPM `AuxiliaryDataFile` |
| `DataType` / `MappingDataType` | CPM `EOProduct`/`EOGroup` object / `Mapping[str, DataType]` exchanged at a PU boundary |
| Block / chunk / tile | A bounded (line- or grid-) block processed independently to bound memory (Zarr/Dask unit); a **halo** is the overlap added to a tile for spatially-coupled stages |
| QAFlag | The per-pixel quality bit registry (`C-COM-QAFLAG`), bits per ICD <5.3.3>E |
| `[impl]` | Marks an element-level code internal whose body is legitimately finalised during implementation (post-CDR); its interface and algorithm are fixed here |
| `[TBC@CDR]` | A field whose exact encoding is sensor-private or pinned-CPM-specific and confirmed at CDR finalisation (per ICD <3>) |
| DDF / DJF | Design Definition File / Design Justification File (ECSS-E-ST-40C) |
| Component aspect | The Annex F <5.4> description axes (identifier, type, purpose, function, subordinates, dependencies, interfaces, resources, references, data) |

---

## <4> Software design overview

This clause introduces the system context and the design before the formal design in clause <5>.

### <4.1> Software static architecture

`msi-processor` is a **batch, non-interactive, single-process (optionally Dask-distributed) Python
library + CLI**. Its static architecture is a **layered, three-package decomposition** over the EOPF
CPM, where the processing chain is a sequence of `EOProcessingUnit`s and every product is an
`EOProduct` persisted as cloud-native Zarr (REQ-D-01, REQ-F-PRD-01).

The three top-level components and their relationship:

```
                     ┌─────────────────────────────────────────────────────────────┐
                     │                     msi_processor (item)                       │
                     │                                                               │
   trigger/payload   │   msi_processor.sensors        msi_processor.common          │
   ───────────────►  │   (C-SENSORS)                  (C-COMMON)                     │
   (triggering JSON) │   profile schema + per-sensor  product/Zarr I/O, ADF access, │
                     │   profile data + ADF bindings  profile loader, provenance,   │
                     │        │  (config, data only)   QA-flag registry, chunking,   │
                     │        │                        URI/store map, orchestration  │
                     │        ▼            ▲   ▲   ▲        │                        │
                     │   ┌──────────────────────────────────────────────────────┐  │
                     │   │            msi_processor.computing (C-COMPUTING)       │  │
                     │   │   l0_decode → radiometric → enhancement → toa  ───►    │  │
                     │   │   coregistration → georeference → [pansharpen] ──►     │  │
                     │   │   atmospheric ;  qa (cross-cutting)                    │  │
                     │   │   each stage = pure Core + thin EOProcessingUnit Wrap  │  │
                     │   └──────────────────────────────────────────────────────┘  │
                     └─────────────────────────────────────────────────────────────┘
                          ▲ ADFs (private, by URI)        ▼ EOProduct (Zarr) out
```

- **`msi_processor.computing` (C-COMPUTING)** — the processing chain. One subpackage per stage; each
  contains a **pure Core** (algorithm, no CPM/IO) and a **thin Wrapper** (the `EOProcessingUnit`).
  This is where the heritage algorithms (RD-9) live, realising the DPM modules `DPM-M-*` (RD-6) and the
  ATBD algorithms `ALG-*` (RD-7).
- **`msi_processor.sensors` (C-SENSORS)** — the **adaptation layer**: the versioned profile schema
  and per-sensor profile data + ADF bindings. It contains **no instrument constants in code and no
  algorithm code** (REQ-AD-01, REQ-D-04); the first instantiated profile is the owner's sensor
  (REQ-AD-02).
- **`msi_processor.common` (C-COMMON)** — the **platform/services layer** shared by all PUs:
  `EOProduct`/`EOZarrStore` build and I/O, ADF resolution, profile load/validation, provenance
  assembly, QA-flag registry/propagation, chunking/Dask wiring, URI/store mapping, run configuration,
  chain orchestration + computing-model handling, and the CLI.

**Dependency rule (acyclic, downward only).** `computing` depends on `common` and consumes a resolved
`sensors` profile; `common` depends only on EOPF CPM and the reused stack (RD-10); a Core depends on
**neither** the CPM nor `common` (it takes plain arrays/parameters). `sensors` is data + schema and
depends on nothing. There is no upward or cyclic dependency.

**Main relationship between major components.** The chain is data-driven: each PU consumes the upstream
`EOProduct` (+ ADFs + profile-derived parameters), produces the next-level `EOProduct`, and hands it on.
The level breakpoints (`L1A`/`L1B`/`L1C`/`L2A`, `DPM-BKP-*`) are the inter-component contract (internal
interface, <5.5>). QA (`qa`) is cross-cutting: it is invoked by every measurement PU to attach metrics
and accumulate the per-pixel flag layer (REQ-F-QA-01/02).

**a. Architecture of the software item.** As above: a 3-layer package decomposition (`computing` /
`sensors` / `common`) realising a CPM PU pipeline with a pure-core + thin-wrapper pattern.

**b. System states/modes in which the software operates.** The processor implements the three
states/modes of SRS <4.1>/<8> and REQ-O-04: *configured/idle* (profile, inputs and ADFs resolved),
*processing* (one or more PUs executing), terminating in *completed* or *error/aborted* (fail-stop,
REQ-F-DEP-01). There is **no resident, cyclic or real-time mode** (SSS <4.2>). The behavioural model is
in <4.3>/<5.2>e.

**c. Separated mission and configuration data (Annex F <4.1>c).** All sensor-, mission- and
site-dependent data is **externalised from the code** into the profile and ADFs (REQ-AD-01/03/04,
REQ-D-04), classified per the Annex F NOTE categories:

| Data category (Annex F <4.1>c) | In `msi-processor` | Location / owner | Changeable without code change |
|---|---|---|---|
| Mission-analysis data, varies per mission | Orbit/attitude & viewing-model references, acquisition geometry sources | `L0c` telemetry + profile-referenced ADF (`DPM-ADF-GEOM`) | Yes (by reference) |
| Reference data specific to a family of products | Profile schema defaults, band list / spectral-response references, output CRS/grid/tiling | `sensors/<profile>` (data) | Yes (profile edit) |
| Reference data that never changes | Physical constants (π, solar-spectrum integration constants) used by Cores | code constants in `common`, no instrument specificity | n/a (universal) |
| Data depending on the specific mission (e.g. sensor calibration) | Dark/DSNU, PRNU/flat-field, bad-pixel map, radiometric gain/offset, viewing model | **private ADFs**, referenced by URI (`DPM-ADF-*`) | Yes (ADF swap, REQ-M-02) |
| Data varying with the higher-level system design | Output store target + chunking, breakpoints, optional-stage toggles, atmospheric source | run config / triggering JSON (`ICD-IF-TRIG`) | Yes (config) |

This separation is the mechanism by which the same software runs across sensors and contexts (REQ-D-07,
REQ-AD-01..04) and by which **no private calibration is ever embedded in the code** (REQ-S-01/05).

### <4.2> Software dynamic architecture (computational model)

`msi-processor` has **no hard real-time constraint** (REQ-R-05): there are no cyclic/sporadic threads,
no scheduling-by-deadline, and no RMS/DMS/EDF analysis is applicable. The computational model required by
Annex F <4.2>/<5.2>c is expressed as a **data-flow DAG of passive components** with two interchangeable
execution strategies:

- **Component types.** All components are *passive* (called, not self-scheduling). The active element is
  the **chain runner** (C-COM-ORC, realising `DPM-M-PRD` orchestration), which executes the PU DAG. PUs
  are stateless across invocations; state lives in the `EOProduct`s flowing between them.
- **Scheduling model.** Two modes selected by configuration: (1) **sequential** — the runner executes
  PUs in topological order in a single process (the CI / local-workstation path, REQ-PORT-03);
  (2) **distributed** — the per-PU Core operates on Zarr/Dask blocks and the Dask scheduler builds and
  runs the task graph across workers (REQ-F-ORC-02, REQ-R-04). The two share identical Cores; only the
  block mapping (C-COM-CHUNK) changes.
- **Means of communication.** Components communicate exclusively through **`EOProduct` objects**
  (in-memory `xarray`-backed `MappingDataType`) and, at level breakpoints, through **Zarr stores**
  read/written via `EOZarrStore` (REQ-F-PRD-01). There are no mailboxes, shared mutable globals or RPC;
  the only inter-process channel is the Dask task graph over chunked arrays.
- **Means of synchronisation.** None at application level beyond the DAG topology (a PU starts when its
  inputs are materialised). Concurrency control is delegated to the Dask scheduler; Cores are pure and
  free of shared state, so they are inherently safe to parallelise per block.
- **Distribution (Annex F <5.2>c).** Optional, via Dask only; nodes are Dask workers, the unit of
  distribution is the block/tile. No custom inter-node protocol is defined.

**Computing-model / triggering approach.** The static DAG is wired declaratively by the **CPM triggering
payload** (ICD <5.3.5>, RD-12): a `workflow[]` of `WorkFlowUnitDescription`s naming, for the requested
chain or sub-chain, the active PUs, the `io` (input product(s), ADF set, output target), the per-PU
`parameters` and the `breakpoints`. Each PU additionally carries its own **computing-model JSON**
(`models/<name>_<version>.json`, <5.4>) declaring its mandatory inputs, ADFs, outputs, parameters and
modes; the CPM validates a unit's wiring against this model. The runner (C-COM-ORC) parses the payload,
resolves URIs (C-COM-IO), validates the profile (C-COM-PROFILE), instantiates the required
`EOProcessingUnit`s and executes them honouring breakpoints. This is the single mechanism realising "run
a level, a sub-chain, or the full `L0c`→`L2A` chain" (REQ-F-ORC-01, REQ-I-05, `DPM-BKP-*`).

### <4.3> Software behaviour

A single run is a finite state machine (mirroring SRS <8>):

```mermaid
stateDiagram-v2
  [*] --> ConfiguredIdle: parse triggering JSON,\nresolve URIs, validate profile+ADF
  ConfiguredIdle --> Processing: inputs+ADFs+profile OK
  ConfiguredIdle --> ErrorAborted: invalid profile/ADF/input (REQ-DAT-03, REQ-S-04)
  Processing --> Processing: next PU (per DAG / breakpoints)
  Processing --> Completed: last PU OK -> publish EOProduct(s)
  Processing --> ErrorAborted: any PU fails (fail-stop, REQ-F-DEP-01)
  Completed --> [*]: status 0 + report
  ErrorAborted --> [*]: status !=0, no partial product published
```

Behaviour is **deterministic and reproducible** for a fixed (input, ADF, profile, processor) quadruple
(REQ-F-DEP-02, REQ-REL-01); stochastic kernels (RANSAC) use a profile-fixed seed (ATBD <6>). Error
handling and fault tolerance are detailed in <5.2>g and, per-component, in <5.4>.

### <4.4> Interfaces context

The external interfaces are specified at requirements level in the IRD (RD-3, `REQ-IF-*`) and **defined
concretely in the ICD (RD-5, `ICD-IF-*`)**; per Annex F <4.4>a this SDD **refers to the ICD** and does
not re-derive them. The context (IRD <4.1> external entities E1–E6) is:

```mermaid
flowchart LR
  E1[E1 L0 ingestion / downlink\nL0c product] -->|input, read-only| MSI
  E2[E2 Calibration facility / ADF provider\nprivate ADFs] -->|input, by URI| MSI
  E3[E3 Sensor-profile / config provider] -->|input, profile| MSI
  E4[E4 Orchestration / trigger\ntriggering JSON] -->|invoke| MSI
  MSI[msi-processor] -->|output, Zarr EOProduct| E5[E5 Product store / archive / dissemination]
  MSI -. executes within .-> E6[E6 EOPF CPM + storage backend]
```

Internal interfaces (between the design components of clause <5>) are designed in detail in <5.5>;
external interfaces are bound by REQ-I-01..07 and controlled in the ICD (RD-5, `ICD-IF-*`).

### <4.5> Long lifetime software

Design choices that minimise dependency on the operating system and hardware to support a long planned
lifetime and portability (Annex F <4.5>; REQ-PORT-01/02, REQ-D-09):

- **Pure Python 3.11, no native build, no GPU** (REQ-R-01): the only platform assumption is a POSIX
  x86-64 Linux host; the Cores use portable array libraries (numpy/xarray).
- **Open data format**: outputs are Zarr with CF/STAC/GeoZarr metadata (RD-13, REQ-D-09) — readable
  independently of this software and of any vendor runtime.
- **Location-transparent I/O**: all inputs/outputs are referenced by **URI** and resolved through the
  EOPF store abstraction (C-COM-IO), so local-FS, POSIX and S3 backends are interchangeable without code
  change (REQ-PORT-02, REQ-I-06).
- **Externalised volatile data**: instrument constants, CRS/grid, and per-stage parameters live in the
  profile/ADFs, so sensor and mission evolution does not touch the code (REQ-AD-01, <4.1>c).
- **Single pinned platform dependency** (`eopf == 2.8.1`) with a documented, V&V-gated bump procedure
  (REQ-M-03), isolating the one component most likely to force change. The CPM coupling is confined to
  the Wrappers and the `C-COM-*` services (see <5.4>); the Cores are CPM-free.
- **Pure-core isolation** keeps the algorithm bodies independent of the CPM, so a future platform change
  re-touches only the thin wrappers, not the numerics (REQ-D-03, REQ-M-04).

### <4.6> Memory and PU budget

Per Annex F <4.6>, the allocation of memory and processing time to components. The governing design rule
is **bounded, block-proportional memory**: peak per-worker memory is set by the configured block/tile
size (C-COM-CHUNK), not by product size (REQ-F-ORC-02, REQ-P-05, REQ-R-04), and wall-time scales with the
number of tiles × workers (REQ-P-04). Absolute numeric budgets (`MEM_BUDGET`, `THRU_SCENE`) are
**per-profile parameters held in the private calibration/auxiliary store** (SRS <5.1>, `DPM-PRM-GEN-02`)
and are verified locally; they are **not reproduced here**. The qualitative allocation and the per-stage
blocking strategy (used by the detailed design of <5.4>):

| PU (component) | DPM module | Memory intensity | Compute intensity | Dominant cost | Blocking strategy (C-COM-CHUNK) |
|---|---|---|---|---|---|
| C-PU-L0 l0_decode | DPM-M-L0 | low–med | low | full-frame assembly | per-band/per-detector line streaming |
| C-PU-RAD radiometric | DPM-M-RAD | low | low | element-wise per band | line-chunked; per-detector vectors broadcast |
| C-PU-ENH enhancement | DPM-M-ENH | med | med–high | MTFC/PSF-deconvolution + denoise kernels | tiled with halo (mandatory) |
| C-PU-TOA toa | DPM-M-TOA | low | low | element-wise scaling | line-chunked |
| C-PU-COR coregistration | DPM-M-COR | med | high | feature detect/match (SIFT/FLANN/RANSAC) | per-band-pair on reference-band overview; full-band warp |
| C-PU-GEO georeference | DPM-M-GEO | **high** | **high** | DEM ortho + resampling to grid | tiled resampling, windowed DEM reads |
| C-PU-PAN pansharpen *(opt)* | DPM-M-PAN | med–high | med | MS↔PAN fusion at PAN resolution | tiled; default-off |
| C-PU-ATM atmospheric | DPM-M-ATM | med | high | RT/retrieval per pixel + classification | grid-chunked; LUT-based RT |
| C-PU-QA qa | DPM-M-QA | low | low | metric reductions | streaming reductions |
| C-COMMON services | DPM-M-PRD | low | low | Zarr I/O, provenance | lazy/chunked store I/O |

`georeference` and `atmospheric` are the design's memory/compute hot-spots and the priority targets for
chunking/Dask validation (REQ-P-04/05). The per-component numeric budget table is delivered with the
per-profile data and verified locally (REQ-Q-03).

### <4.7> Design standards, conventions and procedures

Per Annex F <4.7>a the adopted software methods are summarised here and **refer to the SDP (RD-1) §5.3**
for the toolchain and process detail. The Annex F <4.7>b items:

1. **Architectural design method.** EOPF CPM **processing-unit architecture**: the chain is a DAG of
   `EOProcessingUnit`s over `EOProduct`/Zarr, decomposed by processing stage (one per DPM module), each
   stage realised as **pure Core + thin Wrapper**, specialised by an externalised **sensor-profile**
   layer (SDP §5.3).
2. **Detailed design method.** Structured, per-component description against the Annex F <5.4> aspect set,
   with element-level data structures (dataclasses + numpy dtypes), Python type-annotated **core
   signatures** and **`run()` contracts**, and the CPM computing-model JSON. **This issue (CDR) provides
   that detailed design in <5.4>/<5.5>**; bodies marked `[impl]` are completed in WP-5.
3. **Code documentation standards.** Module/class/function docstrings (NumPy/Sphinx style); the published
   design subset rendered to `docs/sdd/` via Sphinx (SDP §5.4/§5.5).
4. **Naming conventions.** PEP 8 for code; **EOPF data-model conventions** for product variables, bands,
   dimensions and command/payload fields (REQ-I-07); hierarchical component naming
   `package.module.Component` mirroring the package tree (Annex F <5.4.2>c). PU class attributes
   `PROCESSOR_NAME = "msi_<stage>"`.
5. **Programming standards.** Python 3.11, PEP 8 enforced by `black`/`ruff`/`flake8`/`isort`; typing by
   `mypy`; security by `bandit`/`trivy`; complexity bounded by `xenon`; quality gate `SonarQube`; tests
   by `pytest` (SDP §5.4; REQ-D-02, REQ-Q-01).
6. **Intended list of reuse components.** EOPF CPM (`EOProcessingUnit`/`EOProduct`/`EOZarrStore`), numpy,
   xarray, zarr, Dask, scikit-image, OpenCV, GDAL/rasterio, pywt, scikit-learn, plus the prior-work
   algorithm heritage (RD-9). The authoritative reuse declaration and licences are in the SRF (RD-10);
   product I/O is implemented **only** through the CPM abstractions (REQ-D-06).
7. **Main design trade-offs.**
   - **Pure Core + thin Wrapper** (chosen) vs algorithm-in-PU. Cost: a small adapter per stage and a
     stable Core↔Wrapper contract (IF-CORE-01, <5.5>). Benefit: Cores are unit-testable without the CPM
     runtime (CI shell runner, REQ-PORT-03, REQ-D-03), numerically verifiable in isolation, and portable
     across a future platform change (REQ-M-04).
   - **Sensor-agnostic profile layer** (chosen) vs per-sensor code forks. Benefit: a new sensor is a new
     profile + private ADFs, no core change (REQ-D-07, REQ-AD-01); no instrument constants in code
     (REQ-D-04, REQ-S-05). Cost: an up-front profile schema + validation (C-COM-PROFILE).
   - **One PU per stage with optional stages toggleable** (chosen) vs fused mega-stages. Benefit: level
     breakpoints, independent verification and re-run granularity (REQ-F-ORC-01, REQ-REL-02, REQ-M-04);
     pansharpen is optional/default-off, while enhancement is **mandatory** (its MTF-compensation /
     PSF-deconvolution sub-step is a required Level-1 image-quality restoration) with the denoise
     sub-step profile-configurable (REQ-F-ENH-03). Cost: more inter-PU `EOProduct`
     hand-offs (mitigated by lazy Zarr).
   - **Chunked + optional Dask** (chosen) vs whole-product in memory. Benefit: bounded memory and
     horizontal scaling (REQ-F-ORC-02, REQ-P-05). Cost: tiling/halo handling in spatial PUs.
   - **EOProduct/Zarr-exclusive I/O** (chosen) vs custom formats. Benefit: cloud-native, CPM-native, open
     (REQ-D-09, REQ-D-06). Cost: bound to the pinned `eopf` (REQ-M-03).
   - **Atmospheric correction as new development** (no heritage) vs reuse. The only non-reused Core;
     designed interface-first against the DPM (RD-6)/ATBD (RD-7) so the rest of the chain is unaffected;
     the RT engine and classifier are `[impl]`/DPM down-select.

---

## <5> Software design

### <5.1> General

This clause describes the software **architectural** design (<5.2>, <5.3>) and the **detailed** design
(<5.4> per-component element level, <5.5> internal-interface data). The architecture is described
identifying the software components, their hierarchical relationships, dependencies and interfaces
(Annex F <5.1>b). Flight-software in-flight-modification design is **not applicable** (ground software,
REQ-D-08; Annex F <5.1>c). The structure of <5.2>–<5.5> is used (Annex F <5.1>d). The DJF is referenced
in <6>b.

### <5.2> Overall architecture

#### <5.2>a/b Static architecture (summary)

The software item decomposes into the three top-level components of <4.1> and, within `computing`, nine
processing-stage components plus the cross-cutting `common` services. The static hierarchy:

```
msi_processor                                   (software item)
├── computing            C-COMPUTING            (processing chain)
│   ├── l0_decode        C-PU-L0    {core, unit}
│   ├── radiometric      C-PU-RAD   {core, unit}
│   ├── enhancement      C-PU-ENH   {core, unit}   (MTFC mandatory)
│   ├── toa              C-PU-TOA   {core, unit}
│   ├── coregistration   C-PU-COR   {core, unit}
│   ├── georeference     C-PU-GEO   {core, unit}
│   ├── pansharpen       C-PU-PAN   {core, unit}   (opt)
│   ├── atmospheric      C-PU-ATM   {core, unit}
│   └── qa               C-PU-QA    {core, unit}   (cross-cutting)
├── sensors              C-SENSORS                 (profile schema + per-sensor data + ADF bindings)
└── common               C-COMMON
    ├── product          C-COM-PRODUCT  (EOProduct build + EOZarrStore I/O)
    ├── io               C-COM-IO       (URI / store mapping: local FS, POSIX, S3)
    ├── adf              C-COM-ADF      (ADF resolution + read, private, by URI)
    ├── profile          C-COM-PROFILE  (profile schema load + validation)
    ├── provenance       C-COM-PROV     (provenance metadata assembly)
    ├── qaflags          C-COM-QAFLAG   (QA/mask flag bit registry + propagation)
    ├── chunking         C-COM-CHUNK    (tile/chunk planning + Dask wiring)
    ├── config           C-COM-CONFIG   (run configuration / parameter resolution)
    ├── orchestration    C-COM-ORC      (chain runner + triggering/computing-model handling)
    ├── errors          (C-COM-ORC)     (typed exception hierarchy — <5.4.1>)
    └── cli              C-COM-CLI      (`msi-processor` batch entry point)
```

Each `computing` stage subpackage holds exactly two subordinate components — a **`core`** (pure
algorithm, `package.stage.core`) and a **`unit`** (the `EOProcessingUnit`, `package.stage.unit`) —
realising the design pattern of REQ-D-03.

#### <5.2>c/d Dynamic architecture (computational model)

As <4.2>: a passive-component data-flow DAG executed by C-COM-ORC, sequential or Dask-distributed,
communicating through `EOProduct`/Zarr, with the CPM triggering payload + per-PU computing-model JSON as
the declarative wiring. There is no real-time scheduling/analytical model (REQ-R-05); the Annex F <5.2>d
items (scheduling type/model, analytical model, task priorities, timing) are **not applicable** and are
recorded as such.

#### <5.2>e Software behaviour

As <4.3>: the `ConfiguredIdle → Processing → {Completed | ErrorAborted}` automaton, fail-stop on any PU
error, deterministic for a fixed input/ADF/profile/processor quadruple (REQ-F-DEP-02).

#### <5.2>f Consistency with the design method

The static (package/PU), dynamic (DAG/Dask) and behavioural (state machine) views above are all expressed
in the adopted CPM PU + pure-core/thin-wrapper method (<4.7>), satisfying Annex F <5.2>f. The detailed
design of <5.4> instantiates this method uniformly across all components.

#### <5.2>g Error handling and fault tolerance principles

The principles below are specialised, per component, in the `Error/exception handling` aspect of <5.4>;
the typed exception hierarchy is defined in <5.4.1>.

- **Detection.** Inputs/ADFs/profile validated before processing (REQ-F-L0-03, REQ-DAT-03, REQ-S-04);
  per-PU acceptance checks (e.g. co-registration match count REQ-F-COR-03); numerical
  range/saturation/no-data checks (REQ-F-RAD-04, REQ-D-05).
- **Containment region.** The **PU boundary** is the fault-containment region: a Core raises a typed
  `MsiProcessorError` subclass, the Wrapper converts it to a flagged, reported failure; faults do not
  propagate silently across the DAG.
- **Reporting & logging.** Structured logs + a machine-readable processing report (`ICD-IF-DIAG`) carry
  success/failure, parameters and provenance (REQ-O-02/03, REQ-HF-02); per-pixel QA flags carry localised
  defects (REQ-F-QA-02, `C-COM-QAFLAG`).
- **Recovery policy.** **Fail-stop** (REQ-F-DEP-01; CPM `triggering__error_policy: FAIL_FAST`): on any PU
  failure the run exits non-zero and **no partial or misleading product is published**; the chain is
  re-runnable at breakpoint granularity (REQ-REL-02, REQ-F-ORC-01, `DPM-BKP-*`). There is no in-run
  retry/redundancy (ground, reprocessable).
- **Residual-hazard alignment.** The residual hazard class is *product-data integrity* (REQ-SAF-01); the
  QA flags + provenance + fail-stop triad is its design mitigation.

### <5.3> Software components design — General

Per Annex F <5.3>a/b: the components, their relationships, purpose, **development type** (new vs reused),
and the **requirements allocation** (each component uniquely identified). Components written for reuse
expose their function and interfaces externally (the Cores; <5.4>). Handling of reused components is
governed by the SRF (RD-10), per Annex N.

| Id | Component (package path) | Type | Purpose (one line) | Dev type | Allocated `REQ-*` | DPM/ATBD |
|---|---|---|---|---|---|---|
| C-COMPUTING | `msi_processor.computing` | package | Processing chain container | new | REQ-D-01, REQ-F-ORC-01 | — |
| C-PU-L0 | `…computing.l0_decode` | PU (core+unit) | Decode/reformat `L0c`→`L1A`, loss handling, assembly | reuse-adapt (RD-9 `level_0`) | REQ-F-L0-01..05 | DPM-M-L0 / ALG-L0-* |
| C-PU-RAD | `…computing.radiometric` | PU (core+unit) | Dark/DSNU, NUC/PRNU, BPR, saturation/no-data | reuse-adapt (RD-9 `level_1.NUC`) | REQ-F-RAD-01..05 | DPM-M-RAD / ALG-RAD-* |
| C-PU-ENH | `…computing.enhancement` | PU (core+unit) | **MTF compensation (MTFC via PSF deconvolution, mandatory)** + configurable denoise, radiometry-preserving | reuse-adapt (RD-9 `level_1.Denoiser`,`sharpening`) | REQ-F-ENH-01..03 | DPM-M-ENH / ALG-ENH-* |
| C-PU-TOA | `…computing.toa` | PU (core+unit) | DN→TOA radiance (+opt reflectance), emit `L1B` | reuse-adapt (RD-9 `level_1.TOA`) | REQ-F-TOA-01..03 | DPM-M-TOA / ALG-TOA-* |
| C-PU-COR | `…computing.coregistration` | PU (core+unit) | Inter-band co-registration to reference band | reuse-adapt (RD-9 `band_coreg`) | REQ-F-COR-01..03 | DPM-M-COR / ALG-COR-* |
| C-PU-GEO | `…computing.georeference` | PU (core+unit) | Viewing-model geoloc + GCP + DEM ortho → `L1C` | reuse-adapt (RD-9 `georeferencing_v1`) | REQ-F-GEO-01..04 | DPM-M-GEO / ALG-GEO-* |
| C-PU-PAN | `…computing.pansharpen` | PU (core+unit) *(opt)* | MS↔PAN fusion to high-res MS | reuse-adapt (RD-9 `pansharp`) | REQ-F-PAN-01/02 | DPM-M-PAN / ALG-PAN-* |
| C-PU-ATM | `…computing.atmospheric` | PU (core+unit) | AOT/WV, TOA→BOA, scene class + masks → `L2A` | **new** (DPM RD-6/ATBD RD-7) | REQ-F-ATM-01..04 | DPM-M-ATM / ALG-ATM-* |
| C-PU-QA | `…computing.qa` | PU/library (core+unit) | QA metrics + per-pixel flag propagation | reuse-adapt (RD-9 `metrics_ips`) | REQ-F-QA-01/02 | DPM-M-QA / ALG-QA-* |
| C-SENSORS | `msi_processor.sensors` | data + schema | Profile schema + per-sensor profile data + ADF bindings | new | REQ-AD-01..04, REQ-DAT-03 | DPM <7.4> |
| C-COM-PRODUCT | `…common.product` | library | Build `EOProduct`, write/read Zarr via `EOZarrStore` | new (over CPM) | REQ-F-PRD-01, REQ-DAT-01, REQ-D-09 | DPM-M-PRD |
| C-COM-IO | `…common.io` | library | URI resolution / store mapping (local/POSIX/S3) | new (over CPM) | REQ-I-06, REQ-PORT-02/03 | — |
| C-COM-ADF | `…common.adf` | library | Resolve + read private ADFs by URI, validity check | new | REQ-F-RAD-01, REQ-DAT-02, REQ-S-04 | DPM <7.2> |
| C-COM-PROFILE | `…common.profile` | library | Load + schema-validate the sensor profile | new | REQ-AD-01/02, REQ-DAT-03 | ICD <5.3.6> |
| C-COM-PROV | `…common.provenance` | library | Assemble provenance metadata | new | REQ-F-PRD-02, REQ-S-05 | DPM-M-PRD |
| C-COM-QAFLAG | `…common.qaflags` | library | QA/mask flag bit registry + propagation | new | REQ-F-QA-02 | ICD <5.3.3>E |
| C-COM-CHUNK | `…common.chunking` | library | Tile/chunk planning + optional Dask wiring | new (over Dask) | REQ-F-ORC-02, REQ-R-04, REQ-P-05 | DPM-PRM-GEN-02 |
| C-COM-CONFIG | `…common.config` | library | Resolve run config / parameters | new | REQ-AD-04, REQ-O-01 | ICD <5.3.5> |
| C-COM-ORC | `…common.orchestration` | executable | Chain runner; parse/execute triggering payload | new (over CPM) | REQ-F-ORC-01, REQ-F-DEP-01, REQ-I-05 | DPM-M-PRD |
| C-COM-CLI | `…common.cli` | executable | `msi-processor` batch CLI entry point | new | REQ-I-02, REQ-O-01, REQ-HF-01 | ICD <5.3.7> |

**Relationships.** `C-COM-ORC` drives the `C-PU-*` chain; every `C-PU-*` Wrapper uses `C-COM-PRODUCT`,
`C-COM-ADF`, `C-COM-PROFILE`, `C-COM-PROV`, `C-COM-QAFLAG`, `C-COM-CHUNK`; every `C-PU-*` Core uses
**none** of `common` (pure). `C-SENSORS` is consumed (as data) by `C-COM-PROFILE`. `C-COM-CLI` is the
entry point to `C-COM-ORC`. The backward (component→requirement) trace is the inverse of the allocation
column above and is consolidated in <6> and RD-11.

### <5.4> Software components design — Detailed design of each component

Per Annex F <5.4.1>a / <5.4.2>–<5.4.11> each component is described against the aspect set, at
**element-level** for this CDR issue. To avoid repetition, the **common PU aspects** and the **shared
data structures / exception hierarchy** are stated once in <5.4.1>, then specialised per stage in
<5.4.2>–<5.4.10>; the `common`/`sensors` components are in <5.4.11>–<5.4.12>.

> **Reading the per-component blocks.** Each stage block gives: *Identifier/type*; *Purpose & trace*;
> *Pure-core — signatures & data structures* (the CPM-free algorithm, IF-CORE-01, grounded in RD-9 and
> the cited `ALG-*`); *EOProcessingUnit wrapper — `run()` I/O* (inputs/adfs/outputs/parameters/modes,
> ICD <5.3.4>A); *Computing-model JSON* (the per-PU CPM declaration); *Error/exception handling*. Python
> signatures are the **designed public contract**; private helper bodies and tuning are `[impl]`.

#### <5.4.1> Common PU aspects, shared data structures and exception hierarchy

**Common PU aspects (apply to all C-PU-*).**
- **Type (Annex F <5.4.3>).** *Logical:* a stage subpackage in `msi_processor.computing` exposing `core`
  (pure functions, non-executable from the CPM's view) and `unit` (an executable `EOProcessingUnit`
  subclass). *Physical:* Python package with modules `core.py`, `unit.py`, and `models/<name>_<ver>.json`.
- **Subordinates (Annex F <5.4.6>).** `core` (algorithm) and `unit` (CPM adapter); `unit` *uses* `core`
  and the `C-COM-*` services.
- **Dependencies (Annex F <5.4.7>).** The upstream-level `EOProduct` must exist; the required ADFs and
  profile parameters must be resolved (C-COM-PROFILE/ADF) before `unit.run()`; `core` has no precondition
  beyond valid array arguments and a validated parameter object.
- **Interfaces (Annex F <5.4.8>).** *Control flow:* `unit.run()` invoked by C-COM-ORC (start = call,
  terminate = return `Mapping[str, DataType]` or raise `MsiProcessorError`). *Data flow:* in = upstream
  `EOProduct` + ADF mapping + `**kwargs` parameters; out = next product + updated QA layer (detailed in
  <5.5>).
- **Resources (Annex F <5.4.9>).** CPU + RAM bounded by block size (<4.6>); no GPU, no special device;
  the only environmental need beyond the interface is a temp/scratch area for large intermediate Zarr
  (resolved via C-COM-IO).
- **References (Annex F <5.4.10>).** SRS <5.2> (the stage's `REQ-F-*`), DPM <8> (the module), ATBD <5>
  (the algorithm), SRF (RD-10)/prior-work (RD-9) for the reused Core, ICD <5.3.4> for the CPM contract.

**Shared core data structures** (module `msi_processor.computing._types`, pure, no CPM):

```python
# Per-pixel QA bit registry — single source of truth (mirrors ICD <5.3.3>E); see C-COM-QAFLAG.
class QAFlag(enum.IntFlag):
    NO_DATA       = 1 << 0   # fill / no-data
    LOST_PACKET   = 1 << 1   # line/packet loss (REQ-F-L0-02)
    SATURATED     = 1 << 2   # at/above saturation (REQ-F-RAD-04)
    DEFECTIVE     = 1 << 3   # bad pixel replaced (REQ-F-RAD-03)
    COREG_FAIL    = 1 << 4   # co-registration failure (REQ-F-COR-03)
    CLOUD         = 1 << 5   # cloud (REQ-F-ATM-03)
    CLOUD_SHADOW  = 1 << 6   # cloud shadow (REQ-F-ATM-03)
    # bit 7 reserved [TBC@CDR]

@dataclass(frozen=True)
class BandImage:                 # one band in a generic 2-D geometry
    data: np.ndarray             # dtype float32 (working) | uint16 (DN/packed); dims (line|y, detector|x)
    qa:   np.ndarray             # dtype uint16 (QAFlag bitmask), same shape as data
    name: str                    # band id, from PROF:bands[].name (e.g. "b2")
    geom: str                    # "focal_plane" | "instrument" | "map"

@dataclass(frozen=True)
class BandStack:                 # the inter-stage payload of the Cores (one entry per band)
    bands: dict[str, BandImage]
    meta:  dict[str, object]     # acquisition/telemetry & per-stage parameters echoed for provenance

@dataclass(frozen=True)
class MetricSet:                 # QA metrics per band (ALG-QA-*)
    snr: float; rmse: float; psnr: float; mse: float; variance: float
```

- `data` valid range is `[0, 2^bit_depth − 1]` for DN/packed (`bit_depth` from the profile,
  `DPM-PRM-GEN-01`, default 12 → `[0, 4095]`) and `[0.0, 1.0]` for reflectance; intermediate arithmetic
  is `float32` (REQ-D-05, ATBD <4.3>). `qa` initial value = `0`; flags are OR-accumulated only
  (monotone, REQ-F-QA-02). Element-level numpy dtype/dim/range/fill for each variable are tabulated in
  <5.5> (internal interface) and the ICD (external product).

**Typed exception hierarchy** (module `msi_processor.common.errors`; the fault-containment vocabulary of
<5.2>g):

```python
class MsiProcessorError(Exception):            # base; carries .stage, .qa_flag, .report_fields
    ...
class InputValidationError(MsiProcessorError): ...   # REQ-F-L0-03, REQ-DAT-03
class ProfileValidationError(MsiProcessorError): ... # REQ-DAT-03  (C-COM-PROFILE)
class AdfResolutionError(MsiProcessorError): ...     # REQ-S-04    (C-COM-ADF)
class RadiometricError(MsiProcessorError): ...       # REQ-F-RAD-*
class CoregistrationError(MsiProcessorError): ...    # REQ-F-COR-03 (insufficient matches/residual)
class GeolocationError(MsiProcessorError): ...       # REQ-F-GEO-*  (missing DEM/model coverage)
class AtmosphericError(MsiProcessorError): ...       # REQ-F-ATM-*
class ProductWriteError(MsiProcessorError): ...      # REQ-F-PRD-01 (C-COM-PRODUCT)
```

A Core raises the typed error on a precondition/acceptance violation; the Wrapper catches it, attaches the
relevant `QAFlag` and report fields, and re-raises to C-COM-ORC, which applies fail-stop (REQ-F-DEP-01).
Observational deviations (QA metric out of tolerance) are **warnings**, never exceptions (DPM-M-QA).

**EOProcessingUnit wrapper template** (every `unit.py`; ICD <5.3.4>A):

```python
class <Stage>Unit(eopf.computing.EOProcessingUnit):
    PROCESSOR_NAME    = "msi_<stage>"
    PROCESSOR_VERSION = "<semver>"
    PROCESSOR_LEVEL   = "<L1A|L1B|L1C|L2A|intermediate>"
    PROCESSOR_MODEL   = True                      # a models/<name>_<ver>.json is provided

    def run(self, inputs: Mapping[str, DataType],
            adfs: Optional[Mapping[str, AuxiliaryDataFile]] = None,
            mode: Optional[str] = None, **kwargs) -> Mapping[str, DataType]:
        # 1. read parameters (kwargs + resolved profile)        -> C-COM-CONFIG/PROFILE
        # 2. extract input bands + QA from EOProduct(s)          -> C-COM-PRODUCT
        # 3. load+validate required ADFs                         -> C-COM-ADF (raise AdfResolutionError)
        # 4. core call(s) over blocks (BandStack in/out)         -> <stage>.core (raise typed error)
        # 5. attach QA flags + metrics                           -> C-COM-QAFLAG, C-PU-QA
        # 6. build output EOProduct + provenance                 -> C-COM-PRODUCT, C-COM-PROV
        return {"<out_name>": product}
```

The wrapper is intentionally **thin** (no algorithm); its body is the six steps above. Per-stage I/O,
parameters and modes differ and are given below.

#### <5.4.2> C-PU-L0 — `l0_decode` (DPM-M-L0; ALG-L0-DEC, ALG-L0-LOSS)

**Identifier/type.** `msi_processor.computing.l0_decode`; PU (`core`+`unit`); `PROCESSOR_LEVEL="L1A"`.
**Purpose & trace.** Decode the `L0c` stream to per-band/per-detector focal-plane arrays, detect/handle
line loss, assemble the `L1A` `EOProduct`. *Trace:* REQ-F-L0-01..05; DPM-M-L0; ALG-L0-DEC/LOSS;
ICD-IF-L0-*.

**Pure-core — signatures & data structures** (`l0_decode.core`):

```python
@dataclass(frozen=True)
class LineLoss:                       # per-band loss record -> processing report + QA
    band: str; start_line: int; n_lost: int

def decode(raw: "RawL0", codec: "CodecSpec") -> dict[str, np.ndarray]:
    """ALG-L0-DEC. Map L0c source packets to {band: DN[line, detector]} in focal-plane
    geometry, applying the profile focal-plane layout (line order / flips, per-band line_factor).
    Body is sensor/NDA-specific and profile-bound -> [impl]; heritage Decoder.decode is a stub."""

def detect_and_truncate_loss(
    bands: dict[str, np.ndarray],
    line_factor: Mapping[str, int],         # DPM-PRM-L0-01; e.g. PAN band -> 2
) -> tuple[dict[str, np.ndarray], list[LineLoss]]:
    """ALG-L0-LOSS (heritage level_0.lost_package). For each band, first index l with
    DN[l]!=0 and DN[l+1]==0 marks a loss start l*=min over bands; truncate DN[:-(l*·s_b)]
    and record LineLoss. Pure numpy; deterministic."""

def check_legality(bands, telemetry, profile) -> None:
    """REQ-F-L0-03 precondition check; raises InputValidationError on a malformed/mismatched input."""

def initial_qa(bands, losses) -> dict[str, np.ndarray]:
    """Initialise QA bitmask (uint16); set LOST_PACKET on truncated/zero-filled lines, NO_DATA on fill."""
```

Data structures: `RawL0`/`CodecSpec` are profile-bound descriptors `[impl]` (decode internals are NDA,
ATBD <5.1>); the output of the Core is a `BandStack` of `geom="focal_plane"` plus the telemetry `meta`.

**EOProcessingUnit wrapper — `run()` I/O** (`l0_decode.unit.L0DecodeUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"l0": EOProduct}` — opened via a profile-registered CPM store/reader (`store_type`, ICD <5.3.5>); **read-only** (REQ-F-L0-05) |
| `adfs` | none (no calibration at L0) |
| `outputs` | `{"l1a": EOProduct}` — DataTree `ICD <5.3.1>A` (`/measurements/detector/<band>`, `/conditions/{time,orbit,attitude}`, `/quality/l0_flags/<band>`) |
| `parameters` (`**kwargs`) | `profile_id`, `profile_version`, `bit_depth` (`DPM-PRM-GEN-01`), `line_factor` map (`DPM-PRM-L0-01`), `legality_thresholds` |
| `modes` | `"default"` |

**Computing-model JSON** (`models/msi_l0_decode_1.0.0.json`; CPM schema, exact keys bound to 2.8.1
[TBC@CDR]):

```json
{
  "name": "msi_l0_decode", "version": "1.0.0", "level": "L1A",
  "inputs":  [{"name": "l0", "mandatory": true}],
  "adfs":    [],
  "outputs": [{"name": "l1a", "mandatory": true}],
  "parameters": {
    "profile_id":      {"type": "string"},
    "profile_version": {"type": "string"},
    "bit_depth":       {"type": "integer", "default": 12},
    "line_factor":     {"type": "object",  "default": {}}
  },
  "modes": ["default"]
}
```

**Error/exception handling.** Malformed/mismatched input or failed profile/ADF resolution ⇒
`InputValidationError` *before* any radiometric step (REQ-F-L0-03), fail-stop; `L0` never written
(REQ-F-L0-05). Loss is **not** an error: truncate + `LOST_PACKET` flag + report (REQ-F-L0-02). Open point
(ATBD <5.1>): non-zero corruption / CRC handling is `[impl]` beyond the zero-line rule.

#### <5.4.3> C-PU-RAD — `radiometric` (DPM-M-RAD; ALG-RAD-NUC/DARK/BPR/SAT)

**Identifier/type.** `msi_processor.computing.radiometric`; PU; intermediate level (optional breakpoint
`DPM-BKP-RAD`). **Purpose & trace.** Dark/DSNU subtraction, NUC/PRNU equalisation, bad-pixel replacement,
saturation/no-data flagging; optional NUC derivation (calibration mode). *Trace:* REQ-F-RAD-01..05;
DPM-M-RAD; ALG-RAD-*; ICD-IF-ADF-01.

**Pure-core — signatures & data structures** (`radiometric.core`):

```python
@dataclass(frozen=True)
class RadiometricParams:
    bit_depth: int = 12
    g_min: float | None = None         # DPM-PRM-RAD-02 bad-pixel gain bounds
    g_max: float | None = None
    saturation: int | None = None      # else 2**bit_depth - 1
    fill_value: int | None = None
    remove_dark_fft: bool = False      # DPM-PRM-RAD-03

def estimate_nuc(dark: np.ndarray, flat: np.ndarray,
                 cut_dark: int = 0, cut_flat: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """ALG-RAD-NUC (heritage NUC.compute_nuc). Column-mean dark/flat -> per-detector
    g = (mean(F)-mean(D))/(F-D), o = mean(F) - g·F. Returns (gain[detector], offset[detector])."""

def apply_nuc(dn: np.ndarray, gain: np.ndarray, offset: np.ndarray,
              dark_offset: np.ndarray | float) -> np.ndarray:
    """ALG-RAD-DARK (heritage apply_nuc_and_bpr). X = dn·g + o − d  (float32)."""

def detect_bad_pixels(gain: np.ndarray, params: RadiometricParams,
                      bpm: np.ndarray | None) -> np.ndarray:
    """ALG-RAD-BPR detection. bad = (g>=g_max)|(g<=g_min) | bpm. Returns bool[detector]."""

def replace_bad_pixels(corrected: np.ndarray, bad: np.ndarray) -> np.ndarray:
    """ALG-RAD-BPR replacement: across-track neighbour interpolation
    (½(left+right); copy nearest valid at clusters/edges). Flags DEFECTIVE upstream."""

def flag_saturation(corrected: np.ndarray, params: RadiometricParams
                    ) -> tuple[np.ndarray, np.ndarray]:
    """ALG-RAD-SAT. Clip to [0, 2^bit_depth−1]; return (clipped, qa) with SATURATED/NO_DATA set."""

def remove_dark_fft(dn: np.ndarray, dark: np.ndarray) -> np.ndarray:   # optional, DPM-PRM-RAD-03
    """heritage dark_noise_removal: Re{IFFT2(FFT2(dn) − FFT2(dark))}, clipped."""
```

The Core consumes/produces a `BandStack` (`geom="focal_plane"`). Per-detector `gain/offset/dark` are
1-D `float32` vectors broadcast across lines; element-level shapes/ranges in <5.5>.

**EOProcessingUnit wrapper — `run()` I/O** (`radiometric.unit.RadiometricUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"l1a": EOProduct}` |
| `adfs` | `{"dark"}` (mandatory), `{"nuc"}` *or* `{"flatfield"}` (mode-dependent), `{"badpixel"}` (profile) — ICD <5.3.2>A |
| `outputs` | `{"rad": EOProduct}` (corrected DN + QA); optional `{"nuc": EOProduct}` calibration ADF in `calibration` mode |
| `parameters` | `RadiometricParams` fields (`DPM-PRM-RAD-01..04`, `DPM-PRM-GEN-01`) |
| `modes` | `"default"` (read `nuc` ADF), `"calibration"` (derive `nuc` from `dark`+`flatfield`, REQ-F-RAD-05) |

**Computing-model JSON** (`models/msi_radiometric_1.0.0.json`):

```json
{
  "name": "msi_radiometric", "version": "1.0.0", "level": "L1A",
  "inputs":  [{"name": "l1a", "mandatory": true}],
  "adfs":    [{"name": "dark", "mandatory": true},
              {"name": "nuc", "mandatory": false},
              {"name": "flatfield", "mandatory": false},
              {"name": "badpixel", "mandatory": false}],
  "outputs": [{"name": "rad", "mandatory": true},
              {"name": "nuc", "mandatory": false}],
  "parameters": {
    "bit_depth": {"type": "integer", "default": 12},
    "nuc_mode":  {"type": "string", "enum": ["read", "derive"], "default": "read"},
    "g_min": {"type": "number"}, "g_max": {"type": "number"},
    "remove_dark_fft": {"type": "boolean", "default": false}
  },
  "modes": ["default", "calibration"]
}
```

**Error/exception handling.** Missing/validity-mismatched ADF ⇒ `AdfResolutionError` (REQ-S-04),
fail-stop. NUC singularity (`F==D` detector) and out-of-range gain are handled as bad pixels (flagged
`DEFECTIVE`), not exceptions. All outputs clipped to the valid range (REQ-F-RAD-04, REQ-D-05). Open point
(ATBD <5.2>): non-linear response term is `[impl]`.

#### <5.4.4> C-PU-ENH — `enhancement` *(mandatory)* (DPM-M-ENH; ALG-ENH-*)

**Identifier/type.** `msi_processor.computing.enhancement`; PU *(mandatory)*; intermediate (`DPM-BKP-ENH`).
**Purpose & trace.** **Mandatory** Level-1 image-quality restoration: **MTF compensation (MTFC) via PSF
deconvolution** (mandatory sub-step — recovers the high-spatial-frequency content attenuated by the
instrument MTF: optics + detector + platform motion) plus a profile-configurable denoise sub-step,
radiometry-preserving. The stage **always runs** because MTFC is mandatory; MTFC materially affects
radiometric/spatial product quality. **Change note (CR):** enhancement promoted to mandatory;
"sharpening" = MTFC / PSF deconvolution. **Change note (CR-3):** the PSF/MTF kernel is now the
**mandatory** per-band `psf` ADF (DPM-ADF-PSF) — per-band 2-D kernels (focal-plane geometry),
float32, normalised to unit DC gain (sum=1) so radiometry is preserved, referenced by ADF URI
(values not reproduced here) and opened read-only — not a parameter; the optional `dark` ADF
(fft_dark only) is retained. *Trace:* REQ-F-ENH-01..03; DPM-M-ENH;
ALG-ENH-BWLP/WAVE/PCA/MA/GAUSS/FFTDARK/DECONV.

**Pure-core — signatures & data structures** (`enhancement.core`):

```python
DenoiseMethod = Literal["butterworth", "wavelet", "pca", "moving_average", "gaussian", "fft_dark"]

def denoise(image: np.ndarray, method: DenoiseMethod, params: Mapping[str, object],
            dark: np.ndarray | None = None) -> np.ndarray:
    """Dispatch to the selected denoiser (heritage Denoiser.*). Returns clipped float32."""

# concrete kernels (each pure; bodies reuse skimage/scipy/pywt/sklearn — RD-10):
def butterworth_lowpass(image, cutoff_ratio=0.2, order=10.0,
                        squared=False, npad=0) -> np.ndarray: ...     # ALG-ENH-BWLP
def wavelet_visushrink(image, wavelet="db3", levels=20,
                       sigma_scale=1/3, mode="soft") -> np.ndarray: ...# ALG-ENH-WAVE
def pca_denoise(image, n_components: int) -> np.ndarray: ...          # ALG-ENH-PCA
def moving_average(image, n: int = 60) -> np.ndarray: ...             # ALG-ENH-MA ((2N+1) sliding)
def gaussian_smooth(image, ksize=5, sigma=None) -> np.ndarray: ...    # ALG-ENH-GAUSS (σ=std if None)
def fft_dark_subtract(image, dark) -> np.ndarray: ...                 # ALG-ENH-FFTDARK

def mtf_compensate(image: np.ndarray, psf_kernel: np.ndarray) -> np.ndarray:
    """ALG-ENH-DECONV — MTF compensation (MTFC) via PSF deconvolution (MANDATORY sub-step).
    Restores the high-spatial-frequency content attenuated by the instrument MTF
    (optics + detector + platform motion); materially affects radiometric/spatial quality.
    Heritage sharpening.deconvolution_kernel (cv2.filter2D), clipped. PSF-derived per-band
    kernel (broader for the PAN band); `psf_kernel` is sourced at run() from the mandatory
    `psf` ADF (DPM-ADF-PSF), not a parameter."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`enhancement.unit.EnhancementUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"rad": EOProduct}` |
| `adfs` | `{"psf"}` (**mandatory** — `DPM-ADF-PSF`, per-band 2-D PSF/MTF kernel for MTFC, float32, unit-DC-gain normalised, by URI/read-only), `{"dark"}` (optional, only if `fft_dark`) |
| `outputs` | `{"enh": EOProduct}` (MTFC-restored, optionally denoised bands + QA-metric deltas via C-PU-QA) |
| `parameters` | `{mtfc:{regularization}, denoise:{method,params,enabled}}` (`DPM-PRM-ENH-01..05`); per-band overrides. PSF kernel is the mandatory `psf` ADF (`DPM-ADF-PSF`), no longer a parameter |
| `modes` | `"default"`; the stage **always runs** (MTFC mandatory); only the denoise sub-step is profile-configurable (REQ-F-ENH-03) |

**Computing-model JSON** (`models/msi_enhancement_1.0.0.json`): `inputs:[{rad,true}]`, `adfs:[{psf,true},{dark,false}]`,
`outputs:[{enh,true}]`, `parameters` carrying the nested `mtfc` (PSF deconvolution, always applied; kernel
from the `psf` ADF) and `denoise` (configurable) objects, `modes:["default"]`.

**Error/exception handling.** Mandatory stage — MTFC (PSF deconvolution) is always applied; only the
denoise sub-step is profile-configurable (REQ-F-ENH-03). Outputs always clipped to the valid range;
radiometric impact reported via QA metrics (REQ-F-QA-01), never silently applied. A missing/invalid `psf`
ADF (`DPM-ADF-PSF`) or a denoise method-not-in-allowed-set ⇒ `InputValidationError` at profile validation
(C-COM-PROFILE), not at run.

#### <5.4.5> C-PU-TOA — `toa` (DPM-M-TOA; ALG-TOA-RAD/REF)

**Identifier/type.** `msi_processor.computing.toa`; PU; `PROCESSOR_LEVEL="L1B"`. **Purpose & trace.**
DN→TOA radiance (mandatory) and TOA reflectance (optional); emit `L1B`. *Trace:* REQ-F-TOA-01..03;
DPM-M-TOA; ALG-TOA-RAD/REF; ICD-IF-OUT-*.

**Pure-core — signatures & data structures** (`toa.core`):

```python
def dn_to_radiance(dn: np.ndarray, gain: np.ndarray | float,
                   offset: np.ndarray | float) -> np.ndarray:
    """ALG-TOA-RAD (heritage TOA.dn_to_radiance). L = (DN − offset)·gain  (float32).
    NOTE: the heritage `radiance -= radiance.min()` is DROPPED (ATBD <5.3> open point 3)."""

def radiance_to_reflectance(radiance: np.ndarray, esun: float,
                            sun_zenith_rad: float, earth_sun_dist_au: float) -> np.ndarray:
    """ALG-TOA-REF. ρ = π·L·d² / (E·cos θ_s). Clipped to [0,1]."""

def earth_sun_distance(doy: int) -> float:
    """d ≈ 1 − 0.01672·cos(0.9856°·(DOY−4)); or solar ephemeris [impl]."""

def solar_geometry(acq_time: "datetime", lon: float, lat: float) -> tuple[float, float]:
    """Proper solar ephemeris -> (sun_zenith_rad, sun_azimuth_rad).
    Replaces the heritage sub-point conflation (ATBD <5.3> open point 3) -> [impl] ephemeris choice."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`toa.unit.ToaUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"enh": EOProduct}` (enhancement is a mandatory upstream stage) |
| `adfs` | `{"radiometric"}` (mandatory), `{"spectral"}` (for reflectance) — ICD <5.3.2>A |
| `outputs` | `{"l1b": EOProduct}` — `/measurements/radiance/<band>` (+ `/measurements/reflectance/<band>`), QA, provenance |
| `parameters` | `emit_reflectance` (`DPM-PRM-TOA-03`), `esun` per band & geometry source (`DPM-PRM-TOA-01/02`, mostly ADF/derived) |
| `modes` | `"default"` |

**Computing-model JSON** (`models/msi_toa_1.0.0.json`): `inputs:[{enh}]`,
`adfs:[{radiometric,true},{spectral,false}]`, `outputs:[l1b]`,
`parameters:{emit_reflectance:{boolean,default:false}}`, `modes:["default"]`.

**Error/exception handling.** Validity-mismatched radiometric/spectral ADF ⇒ `AdfResolutionError`,
fail-stop. Non-physical (negative) radiance clipped + flagged. ESUN is profile/ADF data — the heritage
hard-coded ESUN table is **not** carried over (REQ-AD-01, ATBD <5.3>).

#### <5.4.6> C-PU-COR — `coregistration` (DPM-M-COR; ALG-COR-FEAT/HOM/WARP)

**Identifier/type.** `msi_processor.computing.coregistration`; PU; intermediate (`DPM-BKP-COR`).
**Purpose & trace.** Feature-based inter-band alignment to a reference band with fail-stop on failure.
*Trace:* REQ-F-COR-01..03; DPM-M-COR; ALG-COR-*.

**Pure-core — signatures & data structures** (`coregistration.core`):

```python
@dataclass(frozen=True)
class CoregParams:
    reference_band: str                       # DPM-PRM-COR-01 (heritage "b2")
    clahe_clip: float = 2.0; clahe_grid: tuple[int, int] = (8, 8)   # DPM-PRM-COR-02
    match_fraction: float = 0.10              # top-fraction matches kept
    min_keypoints: int = 20; min_keypoints_pan: int = 40
    ransac_tau: float = 5.0                   # reprojection threshold (px)
    max_residual: float | None = None         # acceptance vs BAND_COREG (DPM-PRM-COR-04, private)
    seed: int = 0                             # deterministic RANSAC (REQ-F-DEP-02)

@dataclass(frozen=True)
class CoregResidual:
    band: str; n_inliers: int; rms_residual_px: float; accepted: bool

def estimate_homography(band: np.ndarray, reference: np.ndarray, params: CoregParams
                        ) -> tuple[np.ndarray, CoregResidual]:
    """ALG-COR-FEAT+HOM: 8-bit normalise → CLAHE → SIFT → FLANN(top-fraction) → RANSAC H(3×3).
    Raises CoregistrationError on insufficient keypoints/matches. Reuses cv2; tuning [impl]."""

def warp_to_reference(band: np.ndarray, H: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """ALG-COR-WARP: I_reg = warpPerspective(band, H, shape)."""

def coregister(bands: Mapping[str, np.ndarray], params: CoregParams
               ) -> tuple[dict[str, np.ndarray], list[CoregResidual]]:
    """Per non-reference band: estimate H, check residual ≤ max_residual, warp; crop to common
    extent. Raises CoregistrationError if any required band is not accepted (REQ-F-COR-03)."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`coregistration.unit.CoregistrationUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"l1b": EOProduct}` |
| `adfs` | none |
| `outputs` | `{"cor": EOProduct}` (co-registered stack + residual QA) |
| `parameters` | `CoregParams` fields (`DPM-PRM-COR-01..04`) |
| `modes` | `"default"` |

**Computing-model JSON** (`models/msi_coregistration_1.0.0.json`): `inputs:[l1b]`, `adfs:[]`,
`outputs:[cor]`, `parameters:{reference_band, match_fraction, ransac_tau, min_keypoints, …}`,
`modes:["default"]`.

**Error/exception handling.** Insufficient keypoints/matches or residual outside acceptance ⇒
`CoregistrationError`, the affected band flagged `COREG_FAIL`, and fail-stop (REQ-F-COR-03,
REQ-F-DEP-01) — no misregistered product is emitted. RANSAC uses `seed` for reproducibility (REQ-F-DEP-02).

#### <5.4.7> C-PU-GEO — `georeference` (DPM-M-GEO; ALG-GEO-ORBIT/GSD/GCP/ORTHO/RESAMP)

**Identifier/type.** `msi_processor.computing.georeference`; PU; `PROCESSOR_LEVEL="L1C"`. **Purpose &
trace.** Viewing-model geolocation + GSD, optional GCP refinement, DEM orthorectification, resample to
the profile CRS/grid; emit `L1C`. *Trace:* REQ-F-GEO-01..04; DPM-M-GEO; ALG-GEO-*; ICD-IF-OUT-*.

**Pure-core — signatures & data structures** (`georeference.core`):

```python
@dataclass(frozen=True)
class PlatformState:                 # ALG-GEO-ORBIT
    lat: float; lon: float; altitude_m: float; ground_velocity_ms: float
@dataclass(frozen=True)
class Geotransform:                  # GDAL affine [ulx, xres, 0, uly, 0, -yres]
    ulx: float; xres: float; uly: float; yres: float; crs_wkt: str

def compute_gsd(altitude_m: float, pixel_pitch_m: float, focal_length_m: float) -> float:
    """ALG-GEO-GSD (heritage). GSD = altitude·pitch/focal."""

def orbit_state(viewing_model: "ViewingModel", acq_time: "datetime") -> PlatformState:
    """ALG-GEO-ORBIT: propagate orbit (SGP4/ephemeris) to acquisition; sub-point + altitude.
    Engine choice (pyorbital/skyfield) [impl]."""

def geolocate(shape: tuple[int, int], state: PlatformState,
              viewing_model: "ViewingModel", dem: np.ndarray) -> np.ndarray:
    """ALG-GEO-ORTHO. Rigorous collinearity (line-of-sight ∩ ellipsoid+DEM) per pixel.
    CDR-target body -> [impl]; PDR heritage = reference-image homography fallback."""

def refine_with_gcp(image: np.ndarray, reference: np.ndarray, params: CoregParams) -> np.ndarray:
    """ALG-GEO-GCP: reuse coregistration.core machinery against a geolocated reference."""

def resample_to_grid(image: np.ndarray, src_geo, dst: Geotransform,
                     resampling: str) -> tuple[np.ndarray, Geotransform]:
    """ALG-GEO-RESAMP: warp to the profile CRS/grid/resolution (GDAL/rasterio + PROJ/osr)."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`georeference.unit.GeoreferenceUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"cor": EOProduct}` (+ orbit/attitude from the `L1A` `conditions`) |
| `adfs` | `{"viewing_model"}`, `{"dem"}` (mandatory), `{"gcp"}` (optional) — ICD <5.3.2>A |
| `outputs` | `{"l1c": EOProduct}` — gridded `/measurements/reflectance/<band>`, `/conditions/geolocation/{x,y,spatial_ref}`, QA, provenance |
| `parameters` | `crs`, `grid`, `resolution`, `resampling`, `use_gcp` (`DPM-PRM-GEO-01..03`); interior geometry `p,f` from `viewing_model` |
| `modes` | `"default"` |

**Computing-model JSON** (`models/msi_georeference_1.0.0.json`): `inputs:[cor]`,
`adfs:[{viewing_model,true},{dem,true},{gcp,false}]`, `outputs:[l1c]`,
`parameters:{crs, grid, resolution, resampling, use_gcp}`, `modes:["default"]`.

**Error/exception handling.** Missing DEM/viewing-model coverage for the footprint/epoch ⇒
`GeolocationError`, fail-stop. Geolocation error verified locally vs `GEO_CE90` (REQ-F-GEO-03, REQ-Q-03).
Open point (ATBD <5.7> open point 2): the rigorous collinearity body replaces the heritage homography at
implementation `[impl]`.

#### <5.4.8> C-PU-PAN — `pansharpen` *(optional)* (DPM-M-PAN; ALG-PAN-ALIGN/FUSE)

**Identifier/type.** `msi_processor.computing.pansharpen`; PU *(opt)*. **Purpose & trace.** MS↔PAN fusion
to PAN resolution, spectral-fidelity QA, default-off. *Trace:* REQ-F-PAN-01/02; DPM-M-PAN; ALG-PAN-*.

**Pure-core — signatures & data structures** (`pansharpen.core`):

```python
FusionMethod = Literal["simple_mean", "brovey", "gs", "ihs", "atrous"]   # heritage = simple_mean

def align_ms_to_pan(ms_stack: Mapping[str, np.ndarray], pan: np.ndarray,
                    params: CoregParams) -> dict[str, np.ndarray]:
    """ALG-PAN-ALIGN: reuse coregistration.core (CLAHE→SIFT→FLANN→RANSAC→warp) onto the PAN grid."""

def fuse(ms_aligned: Mapping[str, np.ndarray], pan: np.ndarray,
         method: FusionMethod = "simple_mean") -> dict[str, np.ndarray]:
    """ALG-PAN-FUSE. simple_mean: ½(MS_b + PAN), clipped. Other methods [impl] (ATBD <5.9> open point 6)."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`pansharpen.unit.PansharpenUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"l1c"|"cor": EOProduct}` (MS stack + PAN band) |
| `adfs` | none |
| `outputs` | `{"pan": EOProduct}` (pan-sharpened MS + spectral-fidelity QA) |
| `parameters` | `enabled`, `method`, `pan_band` (`DPM-PRM-PAN-01`) |
| `modes` | `"default"`; **skipped** when `optional_stages.pansharpen=false` |

**Computing-model JSON** (`models/msi_pansharpen_1.0.0.json`): `inputs:[l1c]`, `adfs:[]`,
`outputs:[pan]`, `parameters:{enabled, method, pan_band}`, `modes:["default"]`.

**Error/exception handling.** Optional/default-off. Alignment failure ⇒ flag + **skip fusion** (the
product remains valid at MS resolution) rather than fail-stop. Spectral fidelity reported vs the
per-profile budget (REQ-F-PAN-02); if unmet, a spectral-preserving `method` is selected by profile.

#### <5.4.9> C-PU-ATM — `atmospheric` **(new)** (DPM-M-ATM; ALG-ATM-PAR/RT/SCM)

**Identifier/type.** `msi_processor.computing.atmospheric`; PU; `PROCESSOR_LEVEL="L2A"`. **Purpose &
trace.** AOT/WV ingest or retrieval, TOA→BOA inversion, scene classification + cloud/shadow masks; emit
`L2A`. *Trace:* REQ-F-ATM-01..04; DPM-M-ATM; ALG-ATM-*. **No prior-work heritage** — interface-first new
development; RT engine and classifier are down-selected in the DPM/`[impl]`.

**Pure-core — signatures & data structures** (`atmospheric.core`):

```python
@dataclass(frozen=True)
class AtmParams:
    aot: np.ndarray | float; water_vapour: np.ndarray | float; ozone: float | None = None

def get_atmospheric_parameters(toa_refl: Mapping[str, np.ndarray], mode: Literal["ingest","retrieve"],
                               aux: "AtmAux", params: Mapping[str, object]) -> AtmParams:
    """ALG-ATM-PAR: ingest auxiliary AOT/WV or retrieve from imagery (DDV / band-ratio). [impl]/DPM."""

def toa_to_boa(toa_refl: Mapping[str, np.ndarray], atm: AtmParams, geometry: "SceneGeometry",
               dem: np.ndarray, rt_lut: "RTLut") -> dict[str, np.ndarray]:
    """ALG-ATM-RT: invert 6S surface-reflectance eqn per pixel via RT-LUT interpolation
    (ATBD <5.8>). Engine (Py6S/Sen2Cor-LUT/ACOLITE) down-selected -> [impl]. Returns BOA in [0,1]."""

def classify_scene(boa: Mapping[str, np.ndarray], params: Mapping[str, object]
                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ALG-ATM-SCM: returns (scene_class, cloud_mask, cloud_shadow_mask). Classifier -> [impl]."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`atmospheric.unit.AtmosphericUnit`):

| Aspect | Value |
|---|---|
| `inputs` | `{"l1c": EOProduct}` (TOA reflectance) |
| `adfs` | `{"atmospheric"}` (AOT/WV/RT-LUT, ingest mode), `{"dem"}` — ICD <5.3.2>A |
| `outputs` | `{"l2a": EOProduct}` — `/measurements/reflectance/<band>` (BOA), `/quality/scene_classification`, masks, QA, provenance |
| `parameters` | `mode` (retrieve\|ingest), `model`/LUT id, classification options (`DPM-PRM-ATM-01/02`) |
| `modes` | `"default"` |

**Computing-model JSON** (`models/msi_atmospheric_1.0.0.json`): `inputs:[l1c]`,
`adfs:[{atmospheric,false},{dem,true}]`, `outputs:[l2a]`,
`parameters:{mode:{enum:[retrieve,ingest]}, model, classification_opts}`, `modes:["default"]`.

**Error/exception handling.** Missing atmospheric/DEM coverage for the footprint/epoch ⇒
`AtmosphericError`, fail-stop. Cloud / cloud-shadow pixels flagged `CLOUD`/`CLOUD_SHADOW` (REQ-F-ATM-03).
**Open point (ATBD <5.8> open point 1):** parameter-retrieval method, RT engine and classifier are to be
defined and validated in the DPM before/at CDR; this SDD fixes the interface and the candidate algorithm,
the bodies are `[impl]`.

#### <5.4.10> C-PU-QA — `qa` (cross-cutting) (DPM-M-QA; ALG-QA-*)

**Identifier/type.** `msi_processor.computing.qa`; PU/library invoked by every measurement PU. **Purpose
& trace.** Compute per-band metrics and merge/propagate the per-pixel flag layer. *Trace:* REQ-F-QA-01/02;
DPM-M-QA; ALG-QA-*.

**Pure-core — signatures & data structures** (`qa.core`):

```python
def compute_metrics(test: np.ndarray, reference: np.ndarray | None) -> MetricSet:
    """ALG-QA-* (heritage metrics_ips). SNR=20log10(mean/std); referential RMSE/MSE/PSNR vs
    reference (aligned to common extent); variance. Returns MetricSet (∞ PSNR when MSE=0)."""

def align_extent(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Crop both to the common extent before referential comparison (heritage run_validation)."""

def merge_flags(*masks: np.ndarray) -> np.ndarray:
    """QA bit OR-accumulation (monotone, REQ-F-QA-02). Same as C-COM-QAFLAG.merge."""
```

**EOProcessingUnit wrapper — `run()` I/O** (`qa.unit.QaUnit`). Usable standalone (`inputs:{"test",
"reference"?}` → `outputs:{"metrics"}`) and as a library called inline by the other PUs (step 5 of the
wrapper template). `modes:["default"]`. **Computing-model JSON** `models/msi_qa_1.0.0.json`:
`inputs:[{test,true},{reference,false}]`, `outputs:[metrics]`, `parameters:{metric_set, reference_sel}`.

**Error/exception handling.** Metrics are **observational** and never abort the chain; a metric outside
the configured tolerance is a **warning** in the report (REQ-O-02). Metrics carry no private data
(REQ-HF-02).

#### <5.4.11> `common` services (C-COM-*) — detailed design

Library/executable components; the data aspect dominates (Annex F <5.4.11>). The public contracts:

```python
# C-COM-PRODUCT (msi_processor.common.product) — REQ-F-PRD-01, REQ-DAT-01, REQ-D-09
def build_eoproduct(measurements: Mapping[str, BandImage], conditions: Mapping, quality: Mapping,
                    attrs: Mapping) -> EOProduct: ...        # DataTree per ICD <5.3.3>A
def write_product(product: EOProduct, uri: str, store_params: Mapping, mode: str) -> None: ...
def read_product(uri: str, store_type: str = "zarr") -> EOProduct: ...   # via EOZarrStore; raises ProductWriteError
def extract_band_stack(product: EOProduct, bands: list[str]) -> BandStack: ...

# C-COM-IO (…common.io) — REQ-I-06, REQ-PORT-02/03
def resolve_uri(uri: str) -> "StoreHandle": ...             # local FS | posix | s3:: (no container/Dask/S3 needed for local)
def open_store(uri: str, mode: str, store_params: Mapping | None = None) -> EOZarrStore: ...

# C-COM-ADF (…common.adf) — REQ-F-RAD-01, REQ-DAT-02, REQ-S-04
def resolve_adf(binding: "AdfBinding", acq_time, sensor_id, profile_id) -> AuxiliaryDataFile: ...
def load_adf(adf: AuxiliaryDataFile) -> "AdfData": ...      # read-only
def check_validity(adf: AuxiliaryDataFile, acq_time, sensor_id) -> None: ...  # raises AdfResolutionError

# C-COM-PROFILE (…common.profile) — REQ-AD-01/02, REQ-DAT-03
@dataclass(frozen=True)
class Profile: ...                                          # typed mirror of ICD <5.3.6> schema
def load_profile(uri: str) -> Profile: ...
def validate_profile(raw: Mapping, schema_version: str) -> Profile: ...       # JSON-Schema; raises ProfileValidationError

# C-COM-PROV (…common.provenance) — REQ-F-PRD-02, REQ-S-05
def build_provenance(run_ctx: "RunContext") -> dict: ...    # ids/versions/params/timestamp; NO coefficients

# C-COM-QAFLAG (…common.qaflags) — REQ-F-QA-02
class QAFlag(enum.IntFlag): ...                             # the registry of <5.4.1>
def set_flag(mask: np.ndarray, condition: np.ndarray, flag: QAFlag) -> np.ndarray: ...
def merge(a: np.ndarray, b: np.ndarray) -> np.ndarray: ...  # bitwise OR (monotone)

# C-COM-CHUNK (…common.chunking) — REQ-F-ORC-02, REQ-R-04, REQ-P-05
@dataclass(frozen=True)
class ChunkPlan: chunks: tuple[int, ...]; halo: int
def plan_chunks(shape, chunk_size, halo: int = 0) -> ChunkPlan: ...
def map_over_blocks(func, stack: BandStack, plan: ChunkPlan, use_dask: bool) -> BandStack: ...

# C-COM-CONFIG (…common.config) — REQ-AD-04, REQ-O-01
@dataclass(frozen=True)
class RunContext: profile: Profile; adf_ids: dict; params: dict; input_ids: list; processor_version: str
def resolve_config(payload: Mapping, profile: Profile) -> RunContext: ...

# C-COM-ORC (…common.orchestration) — REQ-F-ORC-01, REQ-F-DEP-01, REQ-I-05
@dataclass(frozen=True)
class RunResult: status: int; report: dict; outputs: dict[str, str]
def run_chain(payload: Mapping) -> RunResult: ...          # parse → resolve → validate → execute PUs → publish
                                                           # FAIL_FAST: any MsiProcessorError → status!=0, no publish

# C-COM-CLI (…common.cli) — REQ-I-02, REQ-O-01, REQ-HF-01
def main(argv: list[str]) -> int: ...                      # `msi-processor <payload.{yaml,json}>`; exit code = RunResult.status
```

Per-component element-level data (dtypes/ranges/initial values) for the product DataTree, the ADF content
and the profile schema are governed by the ICD (<5.3.3>/<5.3.2>/<5.3.6>) and reproduced as the internal
data structures of <5.5>; they are not duplicated field-by-field here (Annex F <5.4.10> reference rule).

- **C-COM-PRODUCT.** *Type:* library over CPM `EOProduct`/`EOGroup`/`EOZarrStore`. *Data:* the output
  DataTree (`measurements`/`conditions`/`quality` + root provenance/STAC attrs), chunking and CRS
  encoding per ICD <5.3.3>A/C/D. *Errors:* `ProductWriteError` on a store failure (fail-stop).
- **C-COM-IO.** *Type:* library. *Function:* URI→store handle for local FS / POSIX / S3; guarantees a
  **local-FS path with no container/Dask/S3** for CI (REQ-PORT-03). *Errors:* unresolvable URI ⇒
  `InputValidationError`.
- **C-COM-ADF.** *Type:* library. *Function:* select the validity-/version-matched ADF, open read-only,
  load content. *Errors:* `AdfResolutionError` on missing/mismatched ADF (REQ-S-04).
- **C-COM-PROFILE.** *Type:* library. *Function:* load + JSON-Schema-validate the versioned profile to a
  typed `Profile`; an invalid/incomplete profile ⇒ `ProfileValidationError` **before** processing
  (REQ-DAT-03). *Data:* the profile schema is the in-model id space (paths = item ids, ICD <5.1>b).
- **C-COM-QAFLAG.** *Type:* library. *Data:* the fixed `QAFlag` bitfield (ICD <5.3.3>E); the merge is
  bitwise-OR (monotone accumulation).
- **C-COM-CHUNK.** *Type:* library over Dask. *Function:* compute the block grid + halo per stage (<4.6>)
  and map the Core over blocks sequentially or via Dask; the halo guarantees spatially-coupled stages
  (ENH/COR/GEO/PAN) see sufficient context.
- **C-COM-CONFIG / C-COM-ORC / C-COM-CLI.** *Type:* config library + executables. *Function:* turn the
  triggering payload (ICD <5.3.5>) into a `RunContext`, topologically order and execute the active PUs
  honouring `breakpoints`, enforce FAIL_FAST, publish on success, return exit status + report
  (`ICD-IF-DIAG`). *Interfaces (Annex F <5.4.8>, executable):* control in = `main(argv)` / `run_chain`,
  terminate = exit code; data in = payload + config/profile files, data out = exit status + report +
  `EOProduct`(s).

#### <5.4.12> C-SENSORS — sensor adaptation layer (data + schema)

**Identifier/type.** `msi_processor.sensors`; *logical:* data + schema package; *physical:* a JSON-Schema
file (`sensors/profile.schema.json`), per-sensor profile JSON instances (`sensors/<profile_id>.json`) and
their ADF binding tables. **Non-executable** — no algorithm code (REQ-D-04). **Purpose & trace.**
Externalise all sensor-specific data so the generic chain is sensor-agnostic; a new sensor = a new profile
(+ private ADFs), no core change. *Trace:* REQ-AD-01..04, REQ-DAT-03, REQ-D-07; ICD-IF-PROF-*; DPM <7.4>.
**Data (Annex F <5.4.11>).** The profile object structure is the ICD <5.3.6> schema (id/version/sensor_id,
`bands[]`, `focal_plane`, `adf_bindings`, per-stage parameter blocks, `output`, `optional_stages`,
`breakpoints`); element-level field ids, types, ranges and legality are controlled in the ICD and validated
by C-COM-PROFILE. The first instantiated profile is the project owner's sensor (REQ-AD-02); its numeric
content is **private** (data policy). **Subordinates.** the schema file (parent) ‘composes’ the per-sensor
profile instances and the ADF-binding tables.

### <5.5> Internal interface design

Per Annex F <5.5>a/b the internal interfaces among the identified components, organised as the interfaces
map; per Annex F <5.5>c/e each interface lists its data elements (name, type, dimension, range, initial
value). The previously-postponed file-level data structures (Annex F <5.5>d — the on-disk `EOProduct`/Zarr
layout and the profile-file schema) are now controlled in the ICD (RD-5 <5.3.2/3/6>) and referenced here.

**Interface inventory (component ↔ component).**

| If id | From → To | Mechanism | Data (element level) |
|---|---|---|---|
| IF-CHAIN-01 | C-COM-ORC → C-PU-*.unit | `run(inputs, adfs, mode, **params)` call | `inputs: Mapping[str,DataType]`, `adfs: Mapping[str,AuxiliaryDataFile]`, `params: dict`; return `Mapping[str,DataType]` |
| IF-PROD-01 | C-PU-L0 → C-PU-RAD | in-memory `EOProduct` (`L1A`) | `/measurements/detector/<band>` uint16 `(line,detector)` `[0,2^B−1]`; telemetry; `/quality/l0_flags` uint8 |
| IF-PROD-02 | C-PU-RAD → C-PU-ENH → C-PU-TOA | `EOProduct` (intermediate) | corrected DN float32→uint16; `quality/mask/<band>` uint16 (QAFlag) |
| IF-PROD-03 | C-PU-TOA → C-PU-COR (`L1B`) | `EOProduct` + Zarr breakpoint `DPM-BKP-L1B` | `/measurements/radiance/<band>` (+`reflectance`), instrument geometry, QA, provenance |
| IF-PROD-04 | C-PU-COR → C-PU-GEO → C-PU-PAN (`L1C`) | `EOProduct` + Zarr breakpoint `DPM-BKP-L1C` | co-registered → orthorectified TOA reflectance, `conditions/geolocation/{x,y,spatial_ref}`, QA |
| IF-PROD-05 | C-PU-GEO/PAN → C-PU-ATM (`L2A`) | `EOProduct` + Zarr breakpoint `DPM-BKP-L2A` | BOA reflectance, `quality/scene_classification`, masks, QA, provenance |
| IF-CORE-01 | C-PU-*.unit → C-PU-*.core | pure function call | `BandStack` in / (`BandStack` \| arrays + `MetricSet`/residuals) out; **no CPM/IO** (<5.4.1>) |
| IF-SVC-01 | C-PU-*.unit → C-COM-PRODUCT | function call | `build_eoproduct`/`read`/`write`/`extract_band_stack` |
| IF-SVC-02 | C-PU-*.unit → C-COM-ADF | function call (URI) | `AuxiliaryDataFile` → `AdfData` (dark, PRNU, gain/offset, BPM, PSF/MTF kernel (`DPM-ADF-PSF`), viewing model, DEM, AOT/WV) |
| IF-SVC-03 | C-PU-*.unit → C-COM-PROFILE | function call | `Profile` (per-stage parameter block) |
| IF-SVC-04 | C-PU-*.unit → C-COM-QAFLAG | function call | `np.ndarray` uint16 QA layer (`set_flag`/`merge`) |
| IF-SVC-05 | C-PU-*.unit → C-COM-PROV | function call | provenance `dict` (ids/versions/params/timestamp) |
| IF-SVC-06 | C-COM-ORC/PRODUCT → C-COM-IO | function call | URI→`EOZarrStore` handle (local FS / POSIX / S3) |
| IF-SVC-07 | C-PU-*.unit → C-COM-CHUNK | function call | `ChunkPlan`; `map_over_blocks(core, stack, plan, use_dask)` |
| IF-TRIG-01 | E4 → C-COM-CLI/ORC | triggering JSON (ICD <5.3.5>) | `workflow[]`, `io`, `breakpoints`, `dask_context`, params |

**Element-level data structures of the dominant interfaces** (Annex F <5.5>c/e):

- **Inter-PU `EOProduct`** (IF-PROD-01..05) — the on-disk/in-memory DataTree, dtypes, dims, chunking,
  CRS encoding, QA bitfield, provenance fields, ranges and fill values are defined element-by-element in
  **ICD <5.3.3>** tables A–E and are the normative file-level structure (Annex F <5.5>d). Measurement
  variables: `uint16` packed (`scale_factor`/`add_offset`) or `float32` reflectance `[0.0,1.0]`,
  `_FillValue` = profile sentinel, initial value n/a (computed); QA `quality/mask/<band>` `uint16`
  bitmask, initial value `0`; provenance root attrs (ids/versions/params/timestamp), no coefficients.
- **`BandStack` / `BandImage`** (IF-CORE-01) — the pure-core payload of <5.4.1>: `data` `float32`
  (working) / `uint16` (DN), dims `(line|y, detector|x)`, range `[0,2^B−1]` or `[0,1]`; `qa` `uint16`
  initial `0`; `name`, `geom`. This is deliberately CPM-free so Cores are testable off-platform
  (REQ-D-03, REQ-PORT-03).
- **Profile** (IF-SVC-03) — the typed `Profile` mirrors the ICD <5.3.6> schema; the JSON-Schema file is
  the element-level definition (field ids = dotted paths, ICD <5.1>b).

**Interface-map notes.** The **level-breakpoint `EOProduct`** (IF-PROD-03/04/05, `DPM-BKP-*`) is the
dominant internal interface and the point of optional Zarr persistence (resume semantics, DPM <9>). The
**Core↔Wrapper interface** (IF-CORE-01) is uniform across PUs, which is what lets a new stage or a new
profile slot in without touching the others (REQ-M-04, REQ-D-07). The cross-cutting service interfaces
(IF-SVC-*) are uniform across PUs (the six wrapper steps of <5.4.1>).

---

## <6> Requirements to design components traceability

Per Annex F <6>a this clause gives the forward (requirement→component) and backward
(component→requirement) traceability. The **authoritative, tool-maintained** matrix — including the
downward trace to unit/integration test cases and the upward link to DPM `DPM-M-*` and ATBD `ALG-*` — is
RD-11; per Annex F <6>b this clause is its design-level summary and the DJF reference.

### <6.1> Forward trace — SRS `REQ-*` → design component (+ DPM/ATBD)

| SRS requirement group | Design component(s) | DPM / ATBD |
|---|---|---|
| REQ-F-L0-01..05 | C-PU-L0 (+ C-COM-PRODUCT, C-COM-PROFILE, C-COM-ADF, C-COM-QAFLAG) | DPM-M-L0 / ALG-L0-* |
| REQ-F-RAD-01..05 | C-PU-RAD (+ C-COM-ADF, C-COM-QAFLAG) | DPM-M-RAD / ALG-RAD-* |
| REQ-F-ENH-01..03 | C-PU-ENH (+ C-PU-QA) | DPM-M-ENH / ALG-ENH-* |
| REQ-F-TOA-01..03 | C-PU-TOA (+ C-COM-ADF, C-COM-PRODUCT, C-COM-PROV) | DPM-M-TOA / ALG-TOA-* |
| REQ-F-COR-01..03 | C-PU-COR (+ C-COM-QAFLAG, fail-stop via C-COM-ORC) | DPM-M-COR / ALG-COR-* |
| REQ-F-GEO-01..04 | C-PU-GEO (+ C-COM-ADF, C-COM-PRODUCT) | DPM-M-GEO / ALG-GEO-* |
| REQ-F-PAN-01/02 | C-PU-PAN (+ C-PU-QA) | DPM-M-PAN / ALG-PAN-* |
| REQ-F-ATM-01..04 | C-PU-ATM (+ C-COM-ADF, C-COM-PRODUCT) | DPM-M-ATM / ALG-ATM-* |
| REQ-F-QA-01/02 | C-PU-QA, C-COM-QAFLAG | DPM-M-QA / ALG-QA-* |
| REQ-F-PRD-01/02 | C-COM-PRODUCT, C-COM-PROV | DPM-M-PRD |
| REQ-F-ORC-01/02 | C-COM-ORC, C-COM-CHUNK | DPM-M-PRD / DPM-BKP-* |
| REQ-F-DEP-01/02 | C-COM-ORC (fail-stop), all Cores (determinism, seeds; REQ-D-05) | DPM-M-PRD / ATBD <6> |
| REQ-P-01..05 | C-PU-RAD/TOA (RAD_ACC), C-PU-COR/GEO (GEO_CE90/BAND_COREG), C-PU-ATM (BOA_ACC), C-COM-CHUNK (THRU/MEM) | DPM <7.4> |
| REQ-I-01..07 | C-COM-CLI, C-COM-ORC, C-COM-IO, C-COM-PRODUCT (ICD-bound) | ICD-IF-* |
| REQ-O-01..04 | C-COM-CLI, C-COM-ORC (logs/report/status/modes) | ICD-IF-DIAG |
| REQ-R-01..05 | architecture-wide (pure Python/CPU; C-COM-CHUNK sizing; REQ-R-05 N/A) | — |
| REQ-D-01..09 | the architecture itself (PU pattern, profile layer, reuse, numerics, Zarr) + the typed exception/seed design (<5.4.1>) | — |
| REQ-S-01..05 | C-COM-ADF (private by URI), C-COM-PROV (no calib in output), C-COM-IO | ICD-IF-ADF/OUT |
| REQ-PORT-01..03 | C-COM-IO, Core/Wrapper split, C-COM-CHUNK (local-FS path) | ICD-IF-TRIG-03 |
| REQ-AD-01..05 | C-SENSORS, C-COM-PROFILE, C-COM-CONFIG | ICD-IF-PROF |
| REQ-DAT-01..03 | C-COM-PRODUCT, C-COM-ADF, C-COM-PROFILE | ICD <5.3> |
| REQ-Q/REL/M/SAF/DEL/HF-* | toolchain + C-COM-PROFILE/PROV/QAFLAG + C-SENSORS + <4.5>/<4.7> | — |

### <6.2> Backward trace — component → SRS `REQ-*`

The backward trace is the inverse of the <5.3> allocation table (each component's *Allocated `REQ-*`*
column) and of <6.1>; it is consolidated and kept current in RD-11. Every design component traces to at
least one `REQ-*` (no orphan components), every `REQ-*` is allocated to at least one component (no
unimplemented requirement), and every component additionally links to its DPM module / ATBD algorithm
(the `DPM/ATBD` column of <5.3> and <6.1>). The closure to unit/integration test cases is held in RD-11
and exercised per the V&V plan (RD-8) and the SRS/ICD validation matrices.

### <6.3> Measures for critical software components (Annex F <6>c)

`msi-processor` is **Category C** (degraded/incorrect data only; reprocessable; SDP §5.6). The residual
hazard class is *product-data integrity* (REQ-SAF-01). The design measures, per ECSS-Q-ST-80 6.2.2.4
(minimising critical components), now realised at element level:

- **No hard-coded instrument constants in the core** — all externalised to the profile/ADFs (REQ-D-04,
  <4.1>c, <5.4.1>/<5.4.12>); the Cores take only arrays + a typed parameter object, so a calibration error
  is a data fix, not a code fix.
- **Pure-core isolation behind a tested interface** — the `core`/`unit` split and the CPM-free
  `BandStack` contract (IF-CORE-01) make numerical kernels unit-verifiable in isolation and off-platform
  (REQ-D-03), with per-stage tolerances documented in the DPM/ATBD (REQ-D-05).
- **Bounded cyclomatic complexity** (`xenon` thresholds) per `core`/`unit` module; the thin-wrapper
  template keeps the CPM-facing code trivial (REQ-D-04, REQ-Q-04).
- **Typed fault containment** — the `MsiProcessorError` hierarchy (<5.4.1>) makes every failure a typed,
  flagged, reported event at the PU boundary; no silent cross-DAG propagation.
- **Determinism/reproducibility** for a fixed input/ADF/profile/processor quadruple, including
  profile-fixed RANSAC seeds (REQ-F-DEP-02, REQ-D-05).
- **Fail-stop + QA flags + provenance** as the integrity triad (REQ-F-DEP-01, REQ-F-QA-02, REQ-F-PRD-02);
  no partial product is ever published as complete.

No software-criticality-driven *special* design measures beyond the above (e.g. redundancy, watchdog,
N-version) are levied at Category C; this is recorded to close Annex F <6>c. The detailed justification is
carried in the DJF.

---

*End of SDD (detailed / CDR issue). Authored per ECSS-E-ST-40C Rev.1 Annex F. This issue baselines the
element-level per-component design (<5.4>) and internal-interface data (<5.5>) at CDR, superseding the PDR
architectural issue. Requirements are in the SRS (RD-4); algorithm basis in the DPM (RD-6) / ATBD (RD-7);
concrete interfaces in the ICD (RD-5); reuse heritage in the SRF (RD-10); the maintained traceability
matrix is RD-11. Code internals marked `[impl]` are completed in implementation (SDP WP-5), which starts
only after CDR.*
