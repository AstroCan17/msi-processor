# Software System Specification (SSS)

| Field | Value |
|---|---|
| **Document** | SSS — Software System Specification |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex B |
| **Container** | EOPF SDE — `compliance/drd/` (source), published in online documentation (`docs/`) |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | SRR (System Requirements Review) |
| **Status** | Draft for SRR |

> This SSS is the highest-level specification of `msi-processor` and, together with the ICD,
> forms the requirements baseline and the primary input to the SRR. Per the SDP tailoring for a
> single-developer Category C project there is no external customer or separate system tier:
> the mission/ground-segment context that would otherwise sit in a parent system specification is
> folded into this document (clauses <1> and <4>). System-level requirements defined here
> (`SYS-*`) are decomposed into software requirements in the SRS (Annex D).

---

## <1> Introduction

**Purpose.** This document specifies, at system level, the `msi-processor` software product: a
generic, high-resolution **pushbroom multispectral imager (MSI)** ground-segment data processor.
It transforms downlinked **RAW (Level-0)** MSI data into **Level-2** products through radiometric,
geometric and atmospheric correction. The SSS captures *what* the processor must do as a product
within an Earth-observation ground segment — its capabilities, performance and quality objectives,
operational environment and system-level constraints — independent of internal software design
(which is the subject of the SDD, Annex F).

**Objective.** The SSS establishes the requirements baseline against which the software is
validated and accepted. It is the parent of the SRS: every software requirement traces back to a
system requirement (`SYS-*`) defined here, and every system requirement is associated with a
validation method (clause <5.1>, <6>).

**Content.** Clause <4> gives the general description (product perspective, capabilities,
constraints, operational environment, assumptions). Clause <5> states the specific system
requirements grouped by type. Clause <6> defines the verification, validation and integration
requirements. Clause <7> addresses system models.

**Reason for preparation.** The project is an **integration and ECSS productisation** effort: the
processing chain's mathematical basis already exists in prior work (referenced via the SRF and the
Detailed Processing Model, RD-04/RD-05) and is *not* new-algorithm research. The SSS exists to
turn that prior algorithmic basis plus the EOPF platform into a documented, verifiable,
configuration-driven product. The chain is **sensor-agnostic**, driven by a per-sensor
configuration *profile*; the first profile instantiated is the project owner's own sensor.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-01 | ECSS Space engineering — Software | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-02 | ECSS Space product assurance — Software product assurance | ECSS-Q-ST-80C Rev.2 |
| AD-03 | ECSS System engineering — General requirements | ECSS-E-ST-10C Rev.1 |
| AD-04 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| AD-05 | EOPF Core Python Modules (CPM) — Product Structure and Format Definition (PSFD) / common data model | EOPF CPM documentation (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-01 | ECSS Software engineering handbook | ECSS-E-HB-40A |
| RD-02 | ECSS Technical requirements specification | ECSS-E-ST-10-06C |
| RD-03 | ECSS Risk management | ECSS-M-ST-80C |
| RD-04 | `msi-processor` Software Reuse File (SRF) | `docs/srf.md` |
| RD-05 | `msi-processor` Detailed Processing Model (DPM) — per-sensor algorithm basis | `docs/dpm/index` |
| RD-06 | `msi-processor` Interface Control Document (ICD) | `docs/icd.md` |
| RD-07 | EOPF CPM API documentation | EOPF CPM API (`eopf == 2.8.1`) |
| RD-08 | Cloud-native data conventions | Zarr v2/v3, CF metadata, STAC |

---

## <3> Terms, definitions and abbreviated terms

Only terms not already defined in the AD/RD are listed.

| Term / abbr. | Definition |
|---|---|
| MSI | Multispectral imager (pushbroom / along-track scanning instrument) |
| Profile | Per-sensor configuration set (bands, geometry, calibration references, processing parameters, output grid) that specialises the generic chain for one instrument |
| L0 / L0c | Level-0 / consolidated Level-0: decompressed, source-packet-reassembled raw instrument data with ancillary and telemetry |
| L1A | Reformatted, geo-annotated detector samples in instrument (focal-plane) geometry, radiometrically uncorrected |
| L1B | Radiometrically corrected at-sensor product (top-of-atmosphere radiance) in instrument geometry |
| L1C | Geometrically corrected, orthorectified top-of-atmosphere reflectance on a cartographic grid |
| L2A | Atmospherically corrected bottom-of-atmosphere (surface) reflectance with scene classification and cloud/shadow masks |
| TOA / BOA | Top-of-atmosphere / bottom-of-atmosphere |
| NUC / PRNU / DSNU | Non-uniformity correction / photo-response non-uniformity / dark-signal non-uniformity |
| SRF | Spectral response function (instrument); also Software Reuse File (RD-04) where stated |
| AOT | Aerosol optical thickness |
| DEM | Digital elevation model |
| CRS | Coordinate reference system |
| QA | Quality assurance / quality indicators (per-pixel flags and masks) |
| CPM | EOPF Core Python Modules (the `eopf` library) |
| EOProduct / EOProcessingUnit | CPM in-memory product object / CPM processing-stage unit |
| Zarr | Cloud-native chunked array storage format (product output format) |
| EOPF | Earth Observation Processing Framework (ESA) |
| SDE | The EOPF cloud development and processing environment (GitLab + Studio + Dask gateway + object storage), per CI image `registry.eopf.copernicus.eu/sde/...` |
| DPM | Detailed Processing Model (RD-05) — the algorithm theoretical basis per processing level |
| T / A / I / R | Validation/verification methods: Test / Analysis / Inspection / Review of design |

---

## <4> General description

### <4.1> Product perspective

`msi-processor` is a **software product within an Earth-observation ground segment**. In the wider
mission, a high-resolution pushbroom MSI satellite acquires multispectral imagery and downlinks
RAW data to the ground; the ground segment ingests, archives and processes that data into
user-facing products. `msi-processor` occupies the **payload data processing** function of that
ground segment: it consumes consolidated Level-0 (`L0c`) raw MSI data plus auxiliary/calibration
data and produces calibrated, orthorectified, atmospherically corrected products up to Level-2.

The product is **sensor-agnostic by design**: the processing chain is fixed, while the
instrument-specific behaviour is supplied as a per-sensor *profile*. This allows the same software
to serve multiple MSI instruments; the first instantiated profile is the project owner's own
sensor.

The product does **not** replace a specific legacy system; it is a new, EOPF-native
implementation. Where a prior reference processor exists for a given sensor, that reference is used
for numerical cross-validation (clause <6.2>) rather than being replaced in place. Upstream
(reception, demodulation, decompression to `L0c`) and downstream (archiving, cataloguing,
dissemination) ground-segment functions are external to this product and are not specified here.

### <4.2> General capabilities

The software provides the end-to-end raw→L2 capability, decomposed by processing level:

- **Ingestion** of `L0`/`L0c` raw MSI data and the associated auxiliary/calibration data selected
  through the active profile.
- **Radiometric correction** (L0 → L1B): dark/offset subtraction, non-uniformity / flat-field
  correction (PRNU/DSNU), gain application to physical radiance, defective-pixel detection and
  handling, per-detector / per-band assembly.
- **Geometric correction** (L1B → L1C): application of the viewing/geometric model, DEM-based
  orthorectification, resampling to a cartographic grid, geolocation and inter-band
  co-registration.
- **Atmospheric correction** (L1C → L2A): retrieval or ingestion of atmospheric parameters (AOT,
  water vapour), conversion to bottom-of-atmosphere reflectance, scene classification and
  cloud / cloud-shadow masking.
- **Product generation**: output of cloud-native **Zarr** `EOProduct`s conformant to the EOPF data
  model, carrying metadata, processing provenance and per-pixel QA flags.
- **Configuration / profile management**: a single mechanism that specialises the generic chain
  for one sensor and one production scenario.
- **Pipeline orchestration**: each level is realised as a CPM `EOProcessingUnit`; stages are
  chainable, individually runnable and chunked for parallel execution.

**States and modes (informative).** At system level the processor exhibits: *configured/idle*
(profile and inputs resolved, ready), *processing* (one or more stages executing), and
*error/aborted* (a stage failed; outputs flagged, no partial product silently published). The
processor is a non-resident batch component — there is no continuous resident or real-time mode.

### <4.3> General constraints

The following items constrain the supplier's design and development options and are therefore
fixed at system level (detailed as requirements in clause <5.10>):

- The product **shall be built on the EOPF CPM** (`EOProcessingUnit`, `EOProduct`) pinned to
  `eopf == 2.8.1`, matching the SDE `cpm-build-environment` image.
- Products **shall be cloud-native Zarr** conforming to the EOPF data model (AD-05).
- The implementation language is **Python 3.11**.
- The processing algorithms **reuse the existing mathematical basis** (RD-05); the project is an
  integration/productisation effort, not new-algorithm research.
- **Data policy:** source code is public (Apache-2.0); raw input data and instrument calibration
  (gain/offset, dark, flat-field, geometric/atmospheric auxiliaries) are **private** — never
  committed, never used in public CI.
- The project is **single-developer, Category C**; process rigour is achieved through automated
  tooling and checklists rather than independent organisational roles.

### <4.4> Operational environment

**Narrative.** `msi-processor` runs as a batch payload-data processor in a cloud-native Linux
environment. The reference operational and development environment is the **EOPF SDE**: a
container image based on `registry.eopf.copernicus.eu/sde/cpm-build-environment`, with optional
Dask-based parallelism (Dask gateway/cluster) and object storage (S3-compatible) or POSIX
filesystem for Zarr input/output. The same software also runs locally on a developer workstation
for numerical verification against private real data.

**Context (external exchanges).** The processor exchanges data with the following external
ground-segment actors (detailed in the ICD, RD-06):

| Direction | Counterpart | Exchange |
|---|---|---|
| Input | Upstream L0 production (reception/decompression) | `L0`/`L0c` raw MSI product |
| Input | Auxiliary/calibration store (**private**) | Gain/offset, dark, flat-field/NUC tables, spectral response, geometric/viewing model, DEM, atmospheric auxiliaries |
| Input | Configuration store | Per-sensor profile + production parameters |
| Output | Downstream archive / dissemination | `L1B` / `L1C` / `L2A` `EOProduct` (Zarr) + QA + metadata |
| Output | Operations / monitoring | Processing logs, reports, QA summaries |

**Activities supported by external systems.** Upstream systems perform satellite contact,
demodulation, decompression and `L0c` consolidation; downstream systems perform archiving,
cataloguing and user dissemination; the auxiliary/calibration store is maintained by the
instrument calibration process (private). These activities are *not* in the scope of this product.

**Interface documents.** External interfaces are defined in the ICD (RD-06); this SSS lists the
interface *requirements* in clause <5.3> and refers to the ICD for their detailed design.

**Computer infrastructure.** Target: x86-64 Linux, multi-core CPU, no GPU required; RAM and
storage scale with tile size and chunking; optional Dask cluster for horizontal scaling.
Constraint: the public **CI runner is a shell executor** with no container runtime, Dask gateway
or S3 — jobs requiring those are non-blocking in CI, and numerical verification on real data is
performed locally (clause <6>).

### <4.5> Assumptions and dependencies

The specific requirements rely on the following assumptions (risks of invalidity are tracked in
the project risk register per RD-03):

- **A-1** — Consolidated Level-0 (`L0c`) is available and well-formed; reception/decompression are
  done upstream and out of scope.
- **A-2** — A complete, version-controlled auxiliary/calibration set exists per profile (gain,
  dark, flat-field, spectral response, geometric model, DEM, atmospheric auxiliaries). This data is
  private and supplied at run time, not embedded in the software.
- **A-3** — The pre-existing algorithm mathematical basis (RD-05) is correct and sufficient for the
  targeted accuracy; the project integrates rather than re-derives it.
- **A-4** — `eopf == 2.8.1` (CPM) and the EOPF Zarr data model are stable for the development
  baseline.
- **A-5** — DEM and atmospheric auxiliary coverage exist for the processed scene's footprint and
  epoch.
- **A-6** — Reference products / cal-val targets are available locally for the first sensor profile
  to support numerical validation (clause <6.2>).

---

## <5> Specific requirements

### <5.1> General

- **a.** Each system requirement is uniquely identified by a `SYS-<group>-<nn>` tag.
- **b.** Where requirements are expressed through schemas/models (e.g. the profile JSON/YAML schema
  or the EOProduct data model), identifiers are assigned within the schema for traceability.
- **c.** Each requirement is associated with a **validation method** — **T** (Test), **A**
  (Analysis), **I** (Inspection), **R** (Review of design) — and is baselined at version 1.0
  (this issue). The requirement-to-method mapping is consolidated in the project traceability
  matrix (`compliance/traceability/`).

> Performance figures that depend on instrument calibration (radiometric, geolocation and spectral
> accuracy budgets) are expressed as **per-profile budget parameters**. Their baseline numerical
> values are held in the private auxiliary/calibration repository and verified locally; they are
> not reproduced here, in conformance with the data policy (clause <4.3>).

### <5.2> Capabilities requirements

System behaviour and associated performance, organised by capability (processing level).

**Ingestion**

- **SYS-CAP-01** — The system shall ingest `L0`/`L0c` raw MSI data and the auxiliary/calibration
  data resolved by the active profile, and shall reject or flag inputs that fail structural and
  metadata legality checks before processing. *(Validation: T)*

**Radiometric correction (L0 → L1B)**

- **SYS-CAP-02** — The system shall perform radiometric correction comprising dark/offset
  subtraction, non-uniformity / flat-field correction (PRNU/DSNU), gain application to physical
  TOA radiance, and defective-pixel detection and handling, per the DPM (RD-05) and the active
  profile. *(Validation: T, A)*
- **SYS-CAP-03** — Radiometric output (L1B) shall meet the per-profile radiometric accuracy budget
  `RAD_ACC` when processing reference inputs, verified locally on real data. *(Validation: A, T)*

**Geometric correction (L1B → L1C)**

- **SYS-CAP-04** — The system shall geometrically correct the product by applying the viewing /
  geometric model, performing DEM-based orthorectification, resampling to the profile-defined
  cartographic grid and CRS, and co-registering bands. *(Validation: T, A)*
- **SYS-CAP-05** — Geolocation error of the L1C product shall meet the per-profile budget
  `GEO_CE90` (circular error, 90 %), and inter-band co-registration shall meet `BAND_COREG`,
  verified locally against ground reference. *(Validation: A, T)*

**Atmospheric correction (L1C → L2A)**

- **SYS-CAP-06** — The system shall perform atmospheric correction to bottom-of-atmosphere
  (surface) reflectance, retrieving or ingesting atmospheric parameters (AOT, water vapour) per the
  DPM and profile. *(Validation: T, A)*
- **SYS-CAP-07** — The system shall produce a scene classification and cloud / cloud-shadow mask as
  part of the L2A product. *(Validation: T)*

**Product generation, configuration and orchestration**

- **SYS-CAP-08** — The system shall write outputs as cloud-native **Zarr** `EOProduct`s conformant
  to the EOPF data model (AD-05), each carrying acquisition/processing metadata, processing
  provenance, and per-pixel QA flags. *(Validation: I, T)*
- **SYS-CAP-09** — The system shall be **sensor-agnostic**: all instrument-specific behaviour shall
  be supplied through the per-sensor profile, with no instrument constants hard-coded in the
  processing core. *(Validation: R, T)*
- **SYS-CAP-10** — Each processing level shall be implemented as a CPM `EOProcessingUnit`; stages
  shall be runnable individually (a single level), as a sub-chain, or as the full raw→L2 chain.
  *(Validation: T)*
- **SYS-CAP-11** — The system shall support chunked / tiled processing so that large scenes are
  processed within bounded memory, optionally distributed via Dask. *(Validation: T, A)*

**Real-time behaviour and constraints.** The processor has **no hard real-time constraints**; it is
a throughput-oriented batch component. Timing is expressed as a throughput objective in clause
<5.5.2>, not as a real-time deadline.

*HMI capability and on-board control procedures (OBCP) are not applicable: the product has no
graphical HMI (CLI / Python API only, clause <5.3>) and no on-board element.*

### <5.3> System interface requirements

Interface requirements are listed here and detailed in the ICD (RD-06).

- **SYS-IF-01 (software interfaces)** — The system shall expose its capabilities through a Python
  API built on the CPM (`EOProcessingUnit`, `EOProduct`, EOPF Zarr store) and a command-line
  interface for batch invocation. *(Validation: T, I)*
- **SYS-IF-02 (data — input)** — The system shall consume `L0`/`L0c` products and auxiliary /
  calibration data in the formats defined in the ICD; the profile selects the concrete sources and
  versions. *(Validation: T)*
- **SYS-IF-03 (data — output)** — The system shall produce `L1B`/`L1C`/`L2A` `EOProduct`s as Zarr
  stores on object storage (S3-compatible) or POSIX filesystem, per the ICD. *(Validation: T, I)*
- **SYS-IF-04 (communication / storage)** — Storage and (optional) Dask cluster interfaces shall be
  configurable (endpoint, credentials via environment/CI variables) and shall not require a
  resident network service for single-host operation. *(Validation: T)*
- **SYS-IF-05 (HMI)** — Human interaction shall be limited to the CLI, configuration files and
  logs/reports; no graphical user interface is provided. *(Validation: I)*

### <5.4> Adaptation and missionization requirements

- **SYS-ADP-01** — All data that varies by sensor or production scenario shall be externalised into
  the **profile**, including at least: band list and centre wavelengths / spectral response
  references; detector and focal-plane geometry; references to calibration tables (gain, dark,
  flat-field/NUC); viewing/geometric model reference; output CRS, grid, resolution and tiling;
  per-stage processing parameters and toggles. *(Validation: R, T)*
- **SYS-ADP-02** — Site- and epoch-dependent data (DEM, atmospheric auxiliaries) shall be selected
  by reference from the profile / run configuration, not embedded in the software. *(Validation: T)*
- **SYS-ADP-03** — The profile schema shall be versioned and validated at load time; an invalid or
  incomplete profile shall cause a controlled, reported failure before processing. *(Validation: T)*

> The auxiliary/calibration store acts as the "system database" of ECSS-E-ST-40 5.2.4.4; it is
> private and out of the source repository (clause <4.3>).

### <5.5> Computer resource requirements

#### <5.5.1> Computer hardware resource requirements

- **SYS-RES-01** — The system shall run on x86-64 Linux with a multi-core CPU and shall not require
  a GPU. *(Validation: T)*
- **SYS-RES-02** — The system shall operate against object storage (S3-compatible) or a POSIX
  filesystem for input/output; no other specialised hardware is required. *(Validation: T)*

#### <5.5.2> Computer hardware resource utilization requirements

- **SYS-RES-03** — Peak memory shall be bounded by the configured chunk/tile size so that a scene
  can be processed within a per-worker memory budget `MEM_BUDGET` defined in the profile/run
  configuration. *(Validation: A, T)*
- **SYS-RES-04** — End-to-end raw→L2 throughput shall meet the per-profile objective `THRU_SCENE`
  (scenes or km²/hour on a stated reference configuration), measured locally. *(Validation: A, T)*

#### <5.5.3> Computer software resource requirements

- **SYS-RES-05** — The system shall run on Python 3.11 with EOPF CPM `eopf == 2.8.1` and its
  declared dependency stack (xarray, zarr, numpy, Dask), as recorded in the SRF (RD-04) and
  `pyproject.toml`. No proprietary runtime is required. *(Validation: I, T)*

### <5.6> Security requirements

- **SYS-SEC-01** — Source code shall be public under Apache-2.0; raw input data and instrument
  calibration data shall remain **private** and shall never be committed to the repository nor used
  in public CI. *(Validation: I, R)*
- **SYS-SEC-02** — Credentials and access tokens (storage, registry, Dask, SonarQube) shall be
  provided exclusively via environment / CI variables and shall never appear in source or product
  artefacts. *(Validation: I, T)*
- **SYS-SEC-03** — Access to the private auxiliary/calibration store shall be controlled and
  independent of the public code repository. *(Validation: R)*

### <5.7> Safety requirements

- **SYS-SAF-01** — The product is a ground-segment data processor with no command authority over
  the space segment and no direct human-safety hazard; therefore no safety-critical functions are
  defined. The principal residual hazard class is **product-data integrity** (e.g. a mislabelled or
  silently corrupted product); this shall be mitigated by QA flags, provenance metadata and
  fail-stop behaviour (SYS-CAP-08, SYS-OPS-02). *(Validation: R)*

### <5.8> Reliability and availability requirements

- **SYS-RAM-01** — Processing shall be **deterministic and reproducible**: identical inputs,
  auxiliary data and profile version shall yield identical products. *(Validation: T, A)*
- **SYS-RAM-02** — Processing shall be **resumable / re-runnable** at processing-level granularity;
  a failed run shall not leave a partial product presented as complete. *(Validation: T)*
- **SYS-RAM-03** — Service availability is a property of the hosting ground segment, not of this
  batch component; no continuous-availability target is levied on the software itself.
  *(Validation: R)*

### <5.9> Quality requirements

- **SYS-QUA-01** — The software shall conform to ECSS-Q-ST-80C Rev.2 for Category C and to the
  project coding standards enforced by the toolchain (black, isort, flake8, mypy, bandit, xenon).
  *(Validation: I)*
- **SYS-QUA-02** — Automated test coverage shall meet the project gate (inherited EOPF threshold),
  measured by the unit-test CI job. *(Validation: T)*
- **SYS-QUA-03** — The software shall be **portable / relocatable** between the EOPF SDE and a local
  workstation without code changes (configuration only). *(Validation: T, I)*
- **SYS-QUA-04** — Numerical product-quality objectives (radiometric, geolocation, spectral
  fidelity) shall be met per the per-profile budgets referenced in clause <5.2>, validated locally
  on mission-representative real data. *(Validation: A, T)*
- **SYS-QUA-05** — Maintainability shall be supported by reusability of the generic chain across
  profiles and by bounded cyclomatic complexity (xenon thresholds). *(Validation: I, A)*

### <5.10> Design requirements and constraints

At least the following constrain the design and production of the system:

- **SYS-DES-01 (architecture)** — Each processing level shall be a CPM `EOProcessingUnit` and
  products shall be `EOProduct` instances; the architecture shall be a config-driven, sensor-
  agnostic pipeline. *(Validation: R)*
- **SYS-DES-02 (standards)** — The software shall conform to ECSS-E-ST-40C / Q-ST-80C tailoring in
  the SDP (AD-04) and to PEP 8 (enforced by the toolchain). *(Validation: I)*
- **SYS-DES-03 (existing components / COTS)** — The software shall reuse EOPF CPM, xarray, zarr,
  numpy and Dask per the SRF (RD-04); no customer-furnished components are levied. *(Validation: I)*
- **SYS-DES-04 (data standard)** — Outputs shall use Zarr with EOPF/CF-style metadata and STAC-
  compatible cataloguing fields (RD-08, AD-05). *(Validation: I, T)*
- **SYS-DES-05 (language / version pin)** — Implementation shall be Python 3.11 with
  `eopf == 2.8.1` pinned. *(Validation: I)*
- **SYS-DES-06 (naming)** — Product, variable and metadata naming shall follow the EOPF data-model
  conventions. *(Validation: I)*
- **SYS-DES-07 (flexibility and expansion)** — Adding a new sensor shall be achievable by adding a
  profile (and its private auxiliaries) without modifying the processing core. *(Validation: T, R)*
- **SYS-DES-08 (data confidentiality)** — No raw or calibration data shall be required at build time
  or embedded in any delivered artefact. *(Validation: I)*

*Utilization of HMI standards is not applicable (no GUI).*

### <5.11> Software operations requirements

- **SYS-OPS-01** — The system shall be operable as a batch job (CLI or Python API), invoked with a
  profile, an input reference and an auxiliary-data reference, optionally restricted to a single
  processing level or sub-chain. *(Validation: T)*
- **SYS-OPS-02** — Each run shall emit structured logs and a processing report sufficient to
  determine success/failure, parameters used and product provenance; on failure it shall exit with
  a non-zero status and shall not publish a misleading product. *(Validation: T)*

> The supplier's operational response is the SUM / operations documentation; this clause states the
> operational *requirements* only.

### <5.12> Software maintenance requirements

- **SYS-MNT-01** — Maintenance shall be performed under a GitLab issue → branch → merge-request
  workflow with SemVer releases, by the single developer acting in the supplier roles.
  *(Validation: R)*
- **SYS-MNT-02** — Calibration/auxiliary updates shall be deliverable by replacing the referenced
  private data, without changing the software (clause <5.4>). *(Validation: T, R)*
- **SYS-MNT-03** — A documented procedure shall govern bumping the pinned `eopf` version and
  re-running the full V&V before re-baselining. *(Validation: R)*

*No in-flight / in-orbit modification capability is required (ground software).*

### <5.13> System and software observability requirements

- **SYS-OBS-01** — The system shall record, in the product and/or report, the processing chain
  version, profile version, auxiliary-data versions and key parameters (processing provenance) so
  that any product can be reproduced. *(Validation: I, T)*
- **SYS-OBS-02** — Per-pixel QA flags and per-stage quality indicators (e.g. saturation, defective
  pixels, no-data, cloud) shall be carried through to the output product. *(Validation: T)*
- **SYS-OBS-03** — Unit and integration test reports shall be generated and published with the
  documentation (SUITR). *(Validation: I)*

### <5.14> Security constraints for the software development and integration environment

- **SYS-DEVSEC-01** — Development and integration shall use the self-hosted EOPF SDE GitLab; CI
  shall run on the SDE shell executor with secrets injected as masked CI variables. *(Validation: I)*
- **SYS-DEVSEC-02** — The CI pipeline shall run dependency and code security scanning (bandit,
  Trivy) and quality gating (SonarQube); private real data shall never be introduced into the CI
  environment. *(Validation: I, T)*
- **SYS-DEVSEC-03** — Pre-commit hooks shall enforce hygiene (formatting, large-file and
  secret-leak prevention) before code enters the repository. *(Validation: I)*

### <5.15> Secure software delivery requirements

- **SYS-DEL-01** — Releases shall be delivered as versioned Python wheels published to the GitLab
  package registry and as versioned documentation via GitLab Pages, built reproducibly by CI from a
  tagged commit. *(Validation: T, I)*
- **SYS-DEL-02** — Delivered artefacts shall contain no private data; integrity is anchored to the
  Git tag and registry record of the delivered version (cf. SCF / SRN). *(Validation: I)*

---

## <6> Verification, validation and system integration

### <6.1> Verification and validation process requirements

- **SYS-VV-01** — The V&V process shall combine **T/A/I/R** methods (clause <5.1>): automated
  unit/integration tests, static analysis, design/inspection review against this SSS, and numerical
  analysis against the DPM (RD-05). *(Validation: R)*
- **SYS-VV-02** — Public CI shall execute all tests that do **not** require private data, a
  container runtime, a Dask gateway or S3; tests needing those shall be marked non-blocking in CI
  and executed locally. *(Validation: I)*
- **SYS-VV-03** — Security V&V (dependency/code scanning, secret-leak prevention, confidentiality of
  private data) shall be part of the V&V process. *(Validation: I, T)*

### <6.2> Validation approach

- **SYS-VV-04** — The software shall be validated against this requirements baseline and the DPM
  using **mission-representative real data and scenarios**, processed locally. For the first sensor
  profile, L1B/L1C/L2A outputs shall be compared against reference products and/or cal-val targets
  (radiometric, geolocation, surface-reflectance accuracy). Operational procedures (CLI runs,
  configuration) shall be exercised as part of validation. *(Validation: A, T)*

### <6.3> Validation requirements

- **SYS-VV-05** — Each requirement in clause <5> shall carry a validation method (assigned inline
  and consolidated in the traceability matrix). A requirement excluded from validation against the
  baseline shall be explicitly identified there with rationale. *(Validation: R)*

### <6.4> Verification requirements

The SSS levies verification requirements for:

- **SYS-VV-06 (installation & acceptance)** — Clean installation (`pip install`) into the SDE and a
  local environment, and successful execution of the acceptance test set, shall be verified.
  *(Validation: T, I)*
- **SYS-VV-07 (versions, content, medium)** — The delivered versions, their content and medium
  (Zarr `EOProduct`s, Python wheel, versioned documentation) shall be verified against the SCF /
  SRN. *(Validation: I)*
- **SYS-VV-08 (integration support)** — The single developer shall provide the support needed for
  integration of the product into the ground segment / SDE. *(Validation: R)*
- **SYS-VV-09 (exchanged-data format & medium)** — The format and delivery medium of all exchanged
  data — input `L0c`, private auxiliaries, and output products — shall be verified against the ICD
  (RD-06). *(Validation: I, T)*

---

## <7> System models

Formal system-specification-language models (computational, data, event, failure) are **tailored
out** for this Category C, single-developer project. The role of the system model is served by
concrete project artefacts, maintained as the design matures:

- the **EOProcessingUnit pipeline graph** (functional/processing model) — detailed in the SDD;
- the **per-sensor profile schema** (configuration/data model) — clause <5.4>;
- the **EOProduct / Zarr data model** (product data model, AD-05) — referenced by the ICD;
- the **DPM** (RD-05) as the algorithm/behavioural model per processing level.

No schedulability analysis or model checking is required (no real-time or on-board element,
clause <5.2>).
