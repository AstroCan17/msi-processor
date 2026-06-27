# Interface Control Document (ICD)

| Field | Value |
|---|---|
| **Document** | ICD — Interface Control Document (FINAL / field-level) |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex E |
| **Container** | Technical Specification (TS) — `compliance/drd/` (source), published subset in `docs/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | **CDR** (final — supersedes the PDR preliminary issue) |
| **Status** | Draft for CDR |

> **Final issue (CDR).** This is the **final** issue of the ICD, a major constituent of the Technical
> Specification of `msi-processor` (Annex E.1.2). It gives the **concrete field-level interface
> definitions** that realise the interface requirements `REQ-IF-*` of the IRD (RD-3) and bind the
> software requirements `REQ-*` of the SRS (RD-4). It **supersedes the PDR preliminary issue**: the
> interface inventory, group/variable trees, field-level schemas, encodings, dtypes, chunking, CRS
> encoding, ADF content, the EOPF CPM software signatures, the triggering payload syntax and the
> sensor-profile schema are now **locked** and aligned with the detailed SDD (RD-5, CDR issue;
> components `C-*`, internal interfaces `IF-*`). The CPM software interfaces, the triggering payload
> keys, the `AuxiliaryDataFile` dataclass, the `EOProduct`/`EOGroup`/`EOZarrStore` contracts, the
> computing-model schema and the validation/opening/error-policy enumerations of clauses <5.3.4> and
> <5.3.5> were **re-confirmed against the pinned `eopf == 2.8.1` wheel** (the working `cpm_env`
> install), resolving the prior *"exact 2.8.1 surface"* `[TBC@CDR]` flags. The remaining `[TBC@impl]`
> markers are confined to **genuinely sensor-private encodings** (the NDA-bound L0 on-wire
> packetisation/bit-codec, the viewing-model coefficient form) and a small number of details
> legitimately fixed during implementation (SDP WP-5, post-CDR); these are stated at interface +
> content level here. The EOPF **Product Structure & Format Definition (PSFD)** is the normative
> product-structure reference (AD-3). The footprint is tailored to a Category C, single-developer
> ground-segment processor.

---

## <1> Introduction

**Purpose.** (Annex E <1>a.) This document specifies and controls the external interfaces of
`msi-processor` at field level: the downlinked RAW Level-0 (`L0c`) input, the private
instrument-calibration Auxiliary Data Files (ADF), the Level-1/Level-2 cloud-native Zarr `EOProduct`
outputs, the EOPF CPM software interfaces (`EOProduct`/`EOGroup`, `EOProcessingUnit`, `EOZarrStore`,
triggering), the triggering payload (job order) and the sensor-profile/configuration interface.

**Objective.** The ICD turns the requirement-level interface envelope of the IRD into the concrete,
verifiable interface control that the detailed design (SDD, RD-5), implementation (SDP WP-5) and V&V
(RD-8) build against. Each interface is uniquely identified (`ICD-IF-*`), traced to its parent
`REQ-IF-*` / `REQ-*`, and assigned a validation method (clause <6>) and a forward/backward trace
(clause <7>).

**Content.** Clause <4> points to the software overview in the SRS/SSS (not duplicated, Annex E <4>a).
Clause <5> is the body: <5.1> general provisions (identification, in-model id assignment,
traceability), <5.2> the **interface requirements** — the inventory of external interfaces and the
controlled requirements imposed on each — and <5.3> the **interface design** — the field-level
definitions (data-item tables, group/variable trees, signatures, payload and profile schemas).
Clause <6> gives the per-interface validation approach and matrix; clause <7> the traceability.

**Reason for preparation.** `msi-processor` is an integration and ECSS-productisation effort: the
processing chain is a sequence of EOPF CPM `EOProcessingUnit`s exchanging `EOProduct`s and writing
cloud-native Zarr. Because the chain is sensor-agnostic and the raw/calibration data are private, the
interfaces are fixed concretely — parameterised by the sensor profile and referenced by runtime URI.
This issue finalises that control at CDR so that implementation can begin against fixed, traceable
interfaces.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Space product assurance — Software product assurance | ECSS-Q-ST-80C Rev.2 |
| AD-3 | EOPF CPM — Product Structure & Format Definition (PSFD) / common data model | EOPF CPM docs (`eopf == 2.8.1`) |
| AD-4 | EOPF CPM API — `EOProduct`, `EOGroup`, `EOProcessingUnit`, `EOZarrStore`, triggering | EOPF CPM (`eopf == 2.8.1`) |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Software Design Document (SDD, detailed) — `C-*`, `IF-*` | `compliance/drd/sdd-software-design.md` (CDR) |
| RD-6 | `msi-processor` Data Processing Model (DPM) — `DPM-M-*`, `DPM-PR/ADF/PRM/BKP-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V plan (SVerP/SValP/SUITP merged) | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Traceability matrix | `compliance/traceability/traceability-matrix.md` (CDR) |
| RD-10 | Prior work — multispectral pushbroom preprocessing pipeline (calibration/format heritage; see SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-11 | Cloud-native data conventions | Zarr v2/v3, CF metadata, STAC, GeoZarr |

> **Verification note (Annex E.1.2 / project working principle "verify, don't assume").** The CPM
> signatures, the `AuxiliaryDataFile` dataclass, the `EOProduct`/`EOGroup`/`EOZarrStore` contracts, the
> computing-model (`EOProcessingModel`) schema, the triggering-payload section keys and the
> opening/validation/error-policy enumerations in clause <5.3.4>/<5.3.5> were read from the **installed
> `eopf == 2.8.1`** package (the project `cpm_env`: `eopf/computing/abstract.py`,
> `eopf/product/eo_product.py`, `eopf/store/zarr.py`, `eopf/common/constants.py`,
> `eopf/triggering/parsers.py`, `eopf/computing/validation.py`, `eopf/exceptions/error_handling.py`).
> Because the local runtime **is** the pinned target version, these items are **resolved** (no longer
> `[TBC@CDR]`). Items still flagged `[TBC@impl]` depend on the **sensor-private** instrument definition
> (NDA), not on the CPM, and are confirmed against real data during implementation (SDP WP-5).

---

## <3> Terms, definitions and abbreviated terms

Per Annex E <3>a, only terms/abbreviations not already in the SSS <3>, IRD <3>, SRS <3>, SDD <3>, DPM
<3> and ATBD <3> glossaries (which apply in full) are listed. Enumerated values below are the
**confirmed `eopf == 2.8.1`** sets.

| Term / abbr. | Definition |
|---|---|
| DataTree | The `EOProduct`/`EOGroup` hierarchical (group → group/variable) structure; the EOPF in-memory product model |
| EOObject | Base type of any node in the product tree (`EOGroup` or `EOVariable`) |
| `DataType` | CPM product alias `Union[EOProduct, EOContainer, xarray.DataTree]` |
| `MappingDataType` | CPM alias `Mapping[str, DataType | Iterable[DataType]]` — the keyed product set at a PU boundary |
| `MappingAuxiliary` | CPM alias `Mapping[str, AuxiliaryDataFile]` — the keyed ADF set passed to a PU (alias `ADF = AuxiliaryDataFile`) |
| grid_mapping | CF/GeoZarr attribute carrying the CRS encoding of a gridded variable |
| computing-model JSON | The per-PU CPM declarative model (CPM `EOProcessingModel`: `available_modes`/`default_mode`/`modes_config`) declaring per-mode inputs, ADFs, outputs and parameters; loaded via `EOProcessingUnit.processing_model()` |
| `store_type` | CPM store/format selector in the triggering payload (`zarr`, `safe`, or a profile-registered L0 reader); resolved by `EOStoreFactory` |
| `opening_mode` | CPM output store mode (`OpeningMode`): `CREATE` / `CREATE_OVERWRITE` / `CREATE_NO_OVERWRITE` / `OPEN` / `UPDATE` / `APPEND` |
| `validation_mode` | CPM product-validation level (`ValidationMode`): `STRUCTURE` / `STAC` / `NONE` |
| `error_policy` | CPM workflow error policy (`triggering__error_policy`): `FAIL_FAST` / `FAIL_ON_CRITICAL` / `BEST_EFFORT` (`msi-processor` mandates `FAIL_FAST`) |
| `AnyPath` | CPM location-transparent path type (local FS / POSIX / `s3::…`), `eopf.common.file_utils.AnyPath` |
| `[TBC@impl]` | To-be-confirmed at implementation: a **sensor-private** encoding (NDA) or a code internal legitimately fixed in SDP WP-5 (post-CDR) |

---

## <4> Software overview

The software overview is given in SRS (RD-4) <4> and SSS <4> and is not duplicated here (Annex E <4>a
permits reference). In summary: `msi-processor` is a batch, non-interactive, sensor-agnostic processor
that transforms `L0c` RAW MSI data into Zarr `EOProduct`s up to `L2A` through a chain of EOPF CPM
`EOProcessingUnit`s, driven by a per-sensor profile and private calibration ADFs. The external
boundary (actors E1–E6) is defined in IRD <4.1> and SDD <4.4>; this ICD controls the data and software
interfaces crossing that boundary. The realising design components (`C-PU-*`, `C-COM-*`, `C-SENSORS`)
and the internal interfaces (`IF-PROD-*`, `IF-CORE-*`, `IF-SVC-*`, `IF-TRIG-*`) are in SDD <5.3>–<5.5>.

---

## <5> Requirements and design

### <5.1> General provisions to the requirements in the IRD

- **a. (Annex E <5.1>a — unique identification).** Each interface is identified by `ICD-IF-<group>`
  and each controlled requirement on it by `ICD-IF-<group>-NN`. Groups: `L0` (L0 input), `ADF`
  (calibration ADF), `OUT` (L1/L2 output), `SW` (CPM software), `TRIG` (triggering payload), `PROF`
  (sensor profile), `DIAG` (status/diagnostics), `HMI` (CLI).
- **b. (Annex E <5.1>b — identifiers within models).** Where an interface is expressed as a model
  (Zarr DataTree, profile JSON schema, payload/computing-model schema), identifiers are assigned
  *within* the model by the dotted **path** of the node/field (e.g.
  `OUT:/measurements/reflectance/<band>`, `PROF:bands[].esun`, `TRIG:io.output_products[].opening_mode`);
  these paths are the traceable interface item ids.
- **c. (Annex E <5.1>c — traceability).** Each interface and data item states its parent `REQ-IF-*`
  (IRD) and `REQ-*` (SRS) inline; the consolidated matrices are clause <7> and RD-9.
- **d. (units & conventions).** SI / radiometric physical units are stated per data item; variable,
  band, dimension and field naming follow the EOPF data-model / PSFD conventions (SRS REQ-I-07). All
  product and ADF locations are **URIs** (`AnyPath`, location-transparent local FS / POSIX / S3);
  private inputs are referenced, never embedded (IRD REQ-IF-SEC-02).

### <5.2> Interface requirements

This clause lists and describes the software item's external interfaces (Annex E <5.2>a) and the
controlled requirements imposed on each; the field-level **design** of every interface is in <5.3>.
Per Annex E <5.2>b the three mandated interface classes are covered: software-to-software
(`ICD-IF-SW`, `ICD-IF-TRIG`), software-to-hardware (none — see `ICD-IF-SW-05`) and the man–machine
interface (`ICD-IF-HMI`, `ICD-IF-DIAG`). The Annex E <5.2>b.4 aspects — database structure, logical
interface architecture, signal, communication protocol, timing, behaviour-in-error, observable data —
are covered within the relevant interface (timing/signal: not applicable, no real-time/HW interface,
SDD <5.2>d).

#### <5.2.1> External interface inventory

| Interface id | Name | Direction | Class | Realises (IRD) | Design | Design component (SDD) |
|---|---|---|---|---|---|---|
| `ICD-IF-L0` | Downlinked RAW `L0c` input product | in (E1→) | data | REQ-IF-IN-L0-01..03 | <5.3.1> | C-PU-L0, C-COM-IO |
| `ICD-IF-ADF` | Calibration / auxiliary ADF input | in (E2→) | data | REQ-IF-IN-ADF-01..04 | <5.3.2> | C-COM-ADF |
| `ICD-IF-OUT` | `L1B`/`L1C`/`L2A` Zarr `EOProduct` output | out (→E5) | data | REQ-IF-OUT-01..04, REQ-IF-CAP-03 | <5.3.3> | C-COM-PRODUCT, C-COM-PROV |
| `ICD-IF-SW` | EOPF CPM software interface (PU / product / store) | host (E6) | sw-to-sw | REQ-IF-SW-01..04 | <5.3.4> | C-PU-*.unit, C-COM-PRODUCT |
| `ICD-IF-TRIG` | Triggering payload (job order) | in (E4→) | sw-to-sw / comms | REQ-IF-COM-01..03, REQ-IF-CAP-01 | <5.3.5> | C-COM-ORC, C-COM-CONFIG |
| `ICD-IF-PROF` | Sensor-profile / configuration | in (E3→) | data / adaptation | REQ-IF-AD-01..04 | <5.3.6> | C-SENSORS, C-COM-PROFILE |
| `ICD-IF-DIAG` | Completion status & structured diagnostics | out (→E4) | observable / MMI | REQ-IF-CAP-05 | <5.3.7> | C-COM-ORC, C-COM-CLI |
| `ICD-IF-HMI` | Non-interactive CLI / programmatic entry | in/out | MMI | REQ-IF-HMI-01 | <5.3.7> | C-COM-CLI |

#### <5.2.2> Controlled interface requirements

- **ICD-IF-L0-01** — The `L0c` input shall be presented to the chain, after decode, as an `L1A`
  `EOProduct` DataTree with the group layout of <5.3.1>; the **decoder is profile-bound** (sensor
  packetisation is private, `[TBC@impl]`). *Trace:* REQ-IF-IN-L0-01, REQ-F-L0-01/04. *Verify:* I, T.
- **ICD-IF-L0-02** — The `L0c` input shall carry, or be accompanied by, the selection metadata of
  <5.3.1> table B (sensor id, acquisition time, instrument mode) enabling profile/ADF resolution.
  *Trace:* REQ-IF-IN-L0-02, REQ-F-L0-03. *Verify:* I, T.
- **ICD-IF-L0-03** — The `L0c` source shall be opened **read-only** by the reader (`OpeningMode.OPEN`);
  no write path to the L0 location shall exist. *Trace:* REQ-IF-IN-L0-03, REQ-F-L0-05. *Verify:* A, I.
- **ICD-IF-ADF-01** — Each calibration input shall be supplied as a CPM `AuxiliaryDataFile`
  (`name`, `path` URI, `store_params`) with the content of <5.3.2>; gain/offset, dark and flat-field
  are mandatory, the rest profile-selected. *Trace:* REQ-IF-IN-ADF-01, REQ-F-RAD-01/02, REQ-F-TOA-01.
  *Verify:* I, T.
- **ICD-IF-ADF-02** — Each ADF shall carry id, version and validity (sensor/profile, time range) in
  the attributes of <5.3.2> table B so the correct ADF is selectable for a given `L0c`.
  *Trace:* REQ-IF-IN-ADF-02, REQ-S-04. *Verify:* I, T.
- **ICD-IF-ADF-03** — ADF content shall be referenced by runtime URI only; no ADF content shall be
  committed to the repository or required by public CI. *Trace:* REQ-IF-IN-ADF-03, REQ-S-01.
  *Verify:* I, A.
- **ICD-IF-ADF-04** — ADFs shall be opened **read-only**. *Trace:* REQ-IF-IN-ADF-04. *Verify:* A, I.
- **ICD-IF-OUT-01** — Outputs shall be cloud-native Zarr `EOProduct`s written via `EOZarrStore`, with
  the DataTree of <5.3.3> (`measurements` / `conditions` / `quality` + metadata) and mandatory root
  field `measurements`. *Trace:* REQ-IF-OUT-01/02, REQ-F-PRD-01. *Verify:* T, I.
- **ICD-IF-OUT-02** — Each output shall be chunked per <5.3.3> table C and writable to POSIX and
  S3-compatible backends via the EOPF store abstraction. *Trace:* REQ-IF-OUT-03, REQ-F-ORC-02.
  *Verify:* T.
- **ICD-IF-OUT-03** — Each output shall carry the product+provenance metadata of <5.3.3> table D
  (product id, baseline/version, input/ADF/profile ids+versions, parameters, timestamp) and **no**
  private calibration coefficients. *Trace:* REQ-IF-OUT-04, REQ-IF-CAP-03, REQ-F-PRD-02, REQ-S-05.
  *Verify:* I, T.
- **ICD-IF-SW-01** — Each stage shall be an `EOProcessingUnit` subclass with the class attributes and
  `run(...)` signature of <5.3.4>A and a computing-model declaration (CPM `EOProcessingModel` schema,
  <5.3.4>D) declaring its per-mode inputs/ADFs/outputs/parameters. *Trace:* REQ-IF-SW-01, REQ-F-ORC-01.
  *Verify:* R, I.
- **ICD-IF-SW-02** — Products shall be exchanged as `EOProduct`/`EOGroup` (`MappingDataType`) and
  persisted only via `EOZarrStore`; no product I/O outside these abstractions. *Trace:* REQ-IF-SW-02,
  REQ-D-06. *Verify:* R, T.
- **ICD-IF-SW-03** — The software interfaces shall bind to `eopf == 2.8.1`. *Trace:* REQ-IF-SW-03,
  REQ-R-03. *Verify:* I.
- **ICD-IF-SW-04** — Each stage's pure algorithmic core shall be callable without the CPM runtime
  through the plain signatures of <5.3.4>C (SDD `IF-CORE-01`). *Trace:* REQ-IF-SW-04, REQ-D-03.
  *Verify:* T.
- **ICD-IF-SW-05** — No software-to-hardware interface exists; compute/storage are reached only via the
  OS and the EOPF store abstraction (closes Annex E <5.2>b.2 / <5.3>c.2). *Trace:* REQ-IF-HW-01,
  REQ-R-02. *Verify:* I.
- **ICD-IF-TRIG-01** — A run shall be fully specified by the CPM triggering payload of <5.3.5>
  (`workflow` + `io` + optional `breakpoints`/`dask_context`/`general_configuration`/…), declaring
  inputs, ADFs, output target, profile selection and parameters. *Trace:* REQ-IF-COM-01, REQ-I-05,
  REQ-O-01. *Verify:* I, T.
- **ICD-IF-TRIG-02** — All payload product/ADF/output references shall be URIs (`AnyPath`) resolved
  through the EOPF store/mapper, location-transparent local/remote. *Trace:* REQ-IF-COM-02, REQ-I-06.
  *Verify:* T.
- **ICD-IF-TRIG-03** — A local-filesystem payload variant (`store_type: zarr`, local paths, no
  `dask_context`/S3) shall run on the CI shell runner. *Trace:* REQ-IF-COM-03, REQ-PORT-03.
  *Verify:* T.
- **ICD-IF-TRIG-04** — Chain start/stop at level breakpoints shall be controlled via the payload
  `workflow` (`active`/`step`) and `breakpoints` sections of <5.3.5>. *Trace:* REQ-IF-CAP-01,
  REQ-F-ORC-01. *Verify:* T.
- **ICD-IF-PROF-01** — The sensor profile shall be a versioned JSON object validated on load against
  the schema of <5.3.6>; it shall externalise all sensor-specific interface content. *Trace:*
  REQ-IF-AD-01/04, REQ-AD-01, REQ-DAT-03. *Verify:* T, I.
- **ICD-IF-PROF-02** — The profile shall be uniquely identified and versioned and selectable per run
  via the payload (`profile_id`/`profile_version` in the active unit `parameters`). *Trace:*
  REQ-IF-AD-02, REQ-AD-02. *Verify:* I, T.
- **ICD-IF-DIAG-01** — At its boundary the processor shall expose a completion status and the
  machine-readable diagnostics/QA structure of <5.3.7>. *Trace:* REQ-IF-CAP-05, REQ-O-03. *Verify:* T.
- **ICD-IF-HMI-01** — Human interaction shall be limited to the CLI of <5.3.7>, configuration files
  and logs/reports; no GUI. *Trace:* REQ-IF-HMI-01, REQ-HF-01. *Verify:* I, T.

> **Error behaviour (Annex E <5.2>b.4).** All interfaces obey the fail-stop policy (SRS REQ-F-DEP-01,
> SDD <5.2>g) surfaced through `ICD-IF-DIAG`: on any stage error the run exits non-zero, withholds/flags
> affected outputs and publishes no partial product as complete. The CPM error policy is `FAIL_FAST`
> (`triggering__error_policy`, <5.3.5>); the typed fault vocabulary is the `MsiProcessorError` hierarchy
> (SDD <5.4.1>).

### <5.3> Interface design

Per Annex E <5.3>a/d each interface definition gives at least the **provided service**, the
**description (name, type, dimension)**, the **range** and the **initial/default value**; per Annex E
<5.3>e data items are organised as (Name, description, unique id (path/key), source→destination, unit,
limit/range, accuracy/precision where applicable, legality checks, data type, data representation).
External interfaces are also expressed as **models** where appropriate (Annex E <5.3>b: the Zarr
DataTree, the profile JSON-Schema, the CPM payload/computing-model schemas). Sensor-private numbers are
parameterised by the profile (<5.3.6>); only encodings that are **genuinely private** remain `[TBC@impl]`.

#### <5.3.1> `ICD-IF-L0` — Downlinked RAW `L0c` input product

**Provided service.** Read-only ingestion of one downlinked RAW MSI acquisition (E1), decoded into an
`L1A` `EOProduct` DataTree in focal-plane geometry. The decode step is realised by a profile-registered
CPM store/reader (`store_type` selected in the payload, <5.3.5>) wrapped by C-PU-L0; the on-wire
packetisation/bit-codec is **sensor-private (NDA)** and **`[TBC@impl]`** — only the post-decode
interface is controlled here (SDD <5.4.2>; `IF-PROD-01`).

**A. `L1A` DataTree after decode** (source: E1 / L0 reader → destination: radiometric PU):

| Path (item id) | Description | Type | Dimension | Range | Data representation |
|---|---|---|---|---|---|
| `/measurements/detector/<band>` | Raw detector samples, focal-plane geometry, per band | `EOVariable` int (unsigned) | `(line, detector)` | `0 … 2^B−1` (`B`=`bit_depth`, default **12** from RD-10 → `0…4095`) | Zarr/`xarray`, dtype `uint16`, dims from profile |
| `/conditions/time/line_time` | Per-line acquisition timestamp | `EOVariable` float64 | `(line,)` | UTC since epoch | CF `time` units |
| `/conditions/orbit/{position,velocity}` | Platform ephemeris (orbit) ancillary | `EOVariable` float64 | `(t, 3)` | ECEF m, m/s | CF |
| `/conditions/attitude/quaternion` | Platform attitude ancillary | `EOVariable` float64 | `(t, 4)` | unit quaternion | CF |
| `/quality/l0_flags/<band>` | Initial QA (lost-packet / line-loss / fill) | `EOVariable` uint8 | `(line, detector)` | bit-flags (table <5.3.3>E) | Zarr |

- **Number of bands** `N_b`, **detectors/line**, **per-band `line_factor`** and **`bit_depth`** are
  profile parameters (`PROF:bands`, `PROF:focal_plane`; `DPM-PRM-GEN-01`, `DPM-PRM-L0-01`). Heritage
  note (RD-10): one band may be acquired at a 2× line rate — represented by a per-band `line_factor` in
  the profile, not hard-coded.
- **Legality checks (REQ-F-L0-03):** mandatory groups present; band set equals the profile band list;
  dims consistent with the profile focal-plane geometry; selection metadata (table B) present —
  enforced by `l0_decode.core.check_legality` raising `InputValidationError` (SDD <5.4.2>).
- **Lost-packet detection (REQ-F-L0-02, heritage):** an all-zero line following a non-zero line marks a
  line-loss; affected lines are truncated and flagged `LOST_PACKET` in `/quality/l0_flags`. Non-zero
  corruption / CRC handling beyond the zero-line rule is `[TBC@impl]` (ATBD <5.1>).

**B. L0 selection metadata** (drives profile/ADF resolution; source: E1 → destination: orchestrator/PU):

| Item id | Description | Type | Legality check |
|---|---|---|---|
| `sensor_id` | Instrument/sensor identifier | str | matches a known profile `sensor_id` |
| `acquisition_time` | Acquisition start (UTC) | ISO-8601 str | within an ADF validity range |
| `instrument_mode` | Instrument mode/configuration | str | in profile `modes` |
| `l0_product_id` | Unique L0 identifier | str | non-empty; recorded in provenance |

#### <5.3.2> `ICD-IF-ADF` — Calibration / auxiliary ADF input

**Provided service.** Read-only supply of private instrument-calibration and auxiliary data as CPM
`AuxiliaryDataFile`s. Each ADF is passed to a PU in the `adfs` mapping keyed by the PU's declared ADF
name. The 2.8.1 dataclass (confirmed, `eopf/computing/abstract.py`) is
`AuxiliaryDataFile(name: str, path: str | AnyPath, store_params: dict | None = None, data_ptr: Any = None)`
with a read-only `.path -> AnyPath` property; `store_params` may carry `storage_options` (e.g. S3
credentials). Storage form is cloud-native **Zarr** (preferred, PSFD ADF convention) or
NetCDF/GeoTIFF where heritage dictates; the **content schema** below is normative, the on-disk container
choice is a per-profile/heritage detail (`[TBC@impl]` only for the legacy container).

**A. ADF content by type** (source: E2 → destination: the named PU; SDD `IF-SVC-02`):

| ADF key (item id) | Mandatory | Content / variables | Type · dim | Used by (SRS) |
|---|---|---|---|---|
| `radiometric` | yes | per-band absolute gain `gain[b]`, offset `offset[b]` | float32 · `(band[,detector])` | REQ-F-TOA-01: `radiance=(DN−offset)·gain` |
| `dark` | yes | per-band dark/offset (DSNU) reference frame(s) | float32 · `(band, line, detector)`→reduced | REQ-F-RAD-01 |
| `flatfield` | yes | per-band flat-field (PRNU) reference | float32 · `(band, line, detector)` | REQ-F-RAD-02 (NUC) |
| `nuc` | derived | per-band NUC `gain[detector]`,`offset[detector]` (from dark+flat) | float32 · `(band, detector)` | REQ-F-RAD-02/05 |
| `badpixel` | profile | per-band defective-detector mask | uint8/bool · `(band, detector)` | REQ-F-RAD-03 |
| `spectral` | profile | per-band centre wavelength, ESUN, SRF ref | float32 · `(band,)` | REQ-F-TOA-02 |
| `viewing_model` | profile | viewing/geometric model coefficients (form sensor-private) | model · `[TBC@impl]` | REQ-F-GEO-01 |
| `dem` | profile | digital elevation model | int16/float32 · `(y, x)` | REQ-F-GEO-02 |
| `gcp` | profile | ground-control / reference points | table | REQ-F-GEO-02 |
| `atmospheric` | profile | AOT, water vapour, atmos-model params / RT-LUT | float32 · grid/scalar/LUT | REQ-F-ATM-01/02 |

- **NUC derivation (heritage RD-10, REQ-F-RAD-05), informative:** column-mean dark/flat →
  `gain = (mean(flat) − mean(dark)) / (flat − dark)`, `offset = mean(flat) − gain·flat`; detectors with
  out-of-range gain are flagged into `badpixel`. The algorithm basis is the DPM (RD-6) / ATBD (RD-7)
  (`ALG-RAD-NUC`); the SDD core is `radiometric.core.estimate_nuc` (SDD <5.4.3>).

**B. ADF identification & validity attributes** (every ADF; legality-checked on selection by
`C-COM-ADF.check_validity`, SDD <5.4.11>):

| Item id (attr) | Description | Type | Legality check |
|---|---|---|---|
| `adf_id` | Unique ADF identifier | str | non-empty; recorded in provenance |
| `adf_version` | ADF version | str (SemVer) | non-empty |
| `sensor_id` / `profile_id` | Applicability | str | equals the run's sensor/profile |
| `validity_start` / `validity_stop` | Applicability time range | ISO-8601 | spans `acquisition_time` |
| `adf_type` | One of the keys in table A | enum | in table A |

- **Access:** opened read-only (`ICD-IF-ADF-04`); referenced by URI only, never committed
  (`ICD-IF-ADF-03`); selection mismatch ⇒ `AdfResolutionError` (REQ-S-04, SDD <5.4.1>).

#### <5.3.3> `ICD-IF-OUT` — `L1B`/`L1C`/`L2A` Zarr `EOProduct` output

**Provided service.** Self-describing cloud-native Zarr `EOProduct` written via `EOZarrStore`,
consumable by E5. The product is an `EOGroup` tree whose mandatory root field is `measurements`
(confirmed CPM `EOProduct.MANDATORY_FIELD = ("measurements",)`). The level determines the
`measurements` content; `conditions`, `quality` and the metadata are common (SDD `C-COM-PRODUCT`,
`IF-PROD-03/04/05`).

**A. EOProduct DataTree (group hierarchy)** (source: writer PU → destination: E5):

```
/                                   EOProduct root (attrs: STAC + provenance, table D)
├── measurements/                   (mandatory; EOProduct.MANDATORY_FIELD)
│   ├── radiance/<band>             L1B: TOA spectral radiance        [L1B]
│   └── reflectance/<band>          L1B TOA refl. / L1C ortho TOA / L2A BOA  [L1B|L1C|L2A]
├── conditions/
│   ├── geometry/{sun_zenith,sun_azimuth,view_zenith,view_azimuth}    angles
│   ├── geolocation/{x,y | longitude,latitude} + spatial_ref(grid_mapping)  [L1C+]
│   └── meteorology/{aot,water_vapour}                                  [L2A]
└── quality/
    ├── mask/<band>                 per-pixel QA bit-flags (table E)
    ├── scene_classification        [L2A] scene class map
    └── metrics                     per-band/stage QA metrics (SNR,RMSE,PSNR,MSE,variance)
```

**B. Measurement variable definition** (per band; provided service: calibrated band raster):

| Property | Value |
|---|---|
| Name / id | `OUT:/measurements/{radiance|reflectance}/<band>` (band names from `PROF:bands[].name`) |
| Type | `EOVariable` (Zarr array + CF/GeoZarr attrs) |
| Dimension | `(y, x)` gridded (`L1C`/`L2A`) or `(line, sample)` instrument geom (`L1B`) |
| Data type | reflectance `float32` in `[0,1]` (default); radiance `uint16` packed with `scale_factor`/`add_offset` **or** `float32` — selected per profile via `PROF:output.packing` |
| Range | radiance ≥ 0 (sensor units); reflectance `0.0 … 1.0` (clipped, REQ-D-05) |
| `_FillValue` | sensor no-data sentinel (`PROF:output.fill_value`) |
| Initial value | n/a (computed) |
| Legality / accuracy | per-profile `RAD_ACC` (`L1B`), `BOA_ACC` (`L2A`) budgets, verified locally (REQ-P-01/03) |

**C. Chunking & CRS encoding** (REQ-IF-OUT-03 / REQ-F-ORC-02; SDD `C-COM-CHUNK`):

| Item | Definition |
|---|---|
| Chunking | per-variable Zarr chunks `(y_chunk, x_chunk)` from `PROF:output.chunking` (profile default e.g. 1024×1024); enables larger-than-memory lazy read/write |
| Compression | Zarr codec from payload `store_params.compressor` (e.g. `{id: zstd, level: 3, shuffle}`); `null` = uncompressed |
| CRS encoding | `conditions/geolocation/spatial_ref` variable carrying CF/GeoZarr `grid_mapping` (CRS WKT/EPSG from `PROF:output.crs`); referenced by measurement vars via the `grid_mapping` attribute |
| Grid | output CRS, grid origin and `resolution` from `PROF:output.{crs,grid,resolution}` |

**D. Product & provenance metadata** (root `attrs`; source: writer PU via `C-COM-PROV`;
REQ-IF-CAP-03 / REQ-F-PRD-02):

| Item id (attr) | Description | Representation | Legality |
|---|---|---|---|
| `product_id` | Unique output product identifier | str | non-empty, unique |
| `processing_level` | `L1B`/`L1C`/`L2A` | enum | matches PU `PROCESSOR_LEVEL` |
| `processor_version` / `baseline` | Processor + baseline version | str (SemVer) | present |
| `input_product_ids` | Source product id(s) | list[str] | present |
| `adf_ids` | ADF id(s)+version(s) used | list[str] | present; **no coefficients** (REQ-S-05) |
| `profile_id` / `profile_version` | Sensor profile id+version | str | present |
| `processing_parameters` | Effective parameters | JSON object | present |
| `processing_time` | UTC timestamp | ISO-8601 | present |
| `processing_history` | CPM-appended history entry (processor/version/level) | list[obj] | appended by `run_validating` |
| STAC properties | `datetime`, `bbox`, `proj:epsg`, `eo:bands`, … | STAC/CF | GeoZarr/STAC valid (`ValidationMode.STAC`) |

- **CPM history note (confirmed 2.8.1).** When invoked through `run_validating(...)`, the CPM appends a
  processing-history entry (processor name/version/level) to the output product attrs and validates the
  product (`validate(validation_mode)` / `is_valid(validation_mode)`); the project-level provenance of
  table D is additional and authored by `C-COM-PROV`.

**E. Per-pixel QA flag bit definition** (`quality/mask/<band>`, `uint16` bitmask; propagated across all
stages by `C-COM-QAFLAG`, monotone OR-accumulation, REQ-F-QA-02; mirrors SDD `QAFlag`):

| Bit | Flag (SDD `QAFlag`) | Set by |
|---|---|---|
| 0 | `NO_DATA` — no-data / fill | L0, all stages |
| 1 | `LOST_PACKET` — lost-packet / line-loss | L0 (REQ-F-L0-02) |
| 2 | `SATURATED` — saturated | radiometric (REQ-F-RAD-04) |
| 3 | `DEFECTIVE` — defective-pixel (replaced) | radiometric (REQ-F-RAD-03) |
| 4 | `COREG_FAIL` — co-registration failure | coregistration (REQ-F-COR-03) |
| 5 | `CLOUD` — cloud | atmospheric (REQ-F-ATM-03) |
| 6 | `CLOUD_SHADOW` — cloud-shadow | atmospheric (REQ-F-ATM-03) |
| 7 | reserved | `[TBC@impl]` |

#### <5.3.4> `ICD-IF-SW` — EOPF CPM software interface

**Provided service.** The host CPM contracts (E6) the software realises. **Re-confirmed verbatim
against the installed `eopf == 2.8.1`** (see <2> note); each stage is realised as a thin
`EOProcessingUnit` Wrapper over a pure Core (SDD <5.4.1>, `IF-CORE-01`).

**A. `EOProcessingUnit` (stage) contract** — each stage subclasses `eopf.computing.EOProcessingUnit`:

| Element | Definition (confirmed 2.8.1) |
|---|---|
| Class attributes | `PROCESSOR_NAME: str = ""`, `PROCESSOR_VERSION: str = ""`, `PROCESSOR_LEVEL: str = ""`, `PROCESSOR_MODEL: bool = True` (non-empty NAME+VERSION required; when `PROCESSOR_MODEL` the computing model is auto-loaded at class init) |
| Computing model | `processing_model() -> Optional[EOProcessingModel]`; per-PU declaration resolved by processor name/version + mode (model file `models/<snake_name>_<mode>.json|.toml`), schema in table D |
| Core method | `run(self, inputs: MappingDataType, adfs: Optional[MappingAuxiliary] = None, mode: Optional[str] = None, **kwargs) -> MappingDataType` |
| Validated entry | `run_validating(self, inputs, adfs=None, mode=None, validation_mode: ValidationMode = ValidationMode.STRUCTURE, **kwargs) -> MappingDataType` — validates run params against the model, runs, appends processing-history, validates outputs |
| Modes | `get_available_modes() -> List[str]`, `get_default_mode() -> str` (default `"default"` when no model) |
| Mandatory decls | `get_mandatory_input_list(mode=None, **kwargs) -> list[str]`, `get_mandatory_adf_list(mode=None, **kwargs) -> list[str]` |

- `inputs` keys = the PU's declared input names; values are `DataType` (or an iterable of `DataType`).
- `adfs` keys = the PU's declared ADF names; values are `AuxiliaryDataFile`.
- `**kwargs` = the run **parameters** (sourced from the payload unit `parameters`, <5.3.5>).
- Return = `MappingDataType` of output products keyed by the PU's declared output names.

**B. Product & store contracts** (confirmed 2.8.1):

| Element | Definition |
|---|---|
| `EOProduct(EOGroup)` | dict-like product tree; `MANDATORY_FIELD = ("measurements",)`; `[]` get/set of `EOObject`; `.attrs`; `.validate(validation_mode=None)` (raises on invalid); `.is_valid(validation_mode=None) -> bool` |
| `EOGroup(EOObjectWithDims, MutableMapping[str, EOObject])` | holds sub-groups and `EOVariable`s with dims/coords |
| `EOZarrStore(EOProductStore)` | `EOZarrStore(url)`; `.open(mode: OpeningMode \| str = OpeningMode.OPEN, **store_params) -> EOProductStore`; `product = store[key]`; `store[key] = eo_object`; cloud-native Zarr persistence (POSIX/S3) |
| `AuxiliaryDataFile` (alias `ADF`) | dataclass `(name: str, path: str\|AnyPath, store_params: dict\|None = None, data_ptr: Any = None)`; read-only `.path -> AnyPath` property |
| `OpeningMode` | `CREATE` / `CREATE_OVERWRITE` / `CREATE_NO_OVERWRITE` / `OPEN` / `UPDATE` / `APPEND` (read = `OPEN`, create = `CREATE`) |
| `ValidationMode` | `STRUCTURE` (structure only) / `STAC` (STAC attrs) / `NONE` |

**C. Pure algorithmic-core signatures** (callable without CPM, REQ-IF-SW-04 / REQ-D-03; SDD
`IF-CORE-01`; the PU is a thin adapter). The authoritative per-stage core signatures are in SDD <5.4.2>–
<5.4.10>; indicative cores:

| Core (module, SDD) | Signature (indicative) | Returns |
|---|---|---|
| radiometric (`radiometric.core`) | `apply_nuc(dn, gain, offset, dark_offset) -> ndarray`; `estimate_nuc(dark, flat, …) -> (gain, offset)` | corrected DN / NUC vectors |
| toa (`toa.core`) | `dn_to_radiance(dn, gain, offset) -> ndarray`; `radiance_to_reflectance(rad, esun, sun_zenith_rad, earth_sun_dist_au) -> ndarray` | radiance / reflectance |
| coregistration (`coregistration.core`) | `coregister(bands, params: CoregParams) -> (stack, residuals)` | aligned stack + residual QA |
| georeference (`georeference.core`) | `geolocate(shape, state, viewing_model, dem) -> ndarray`; `resample_to_grid(image, src_geo, dst, resampling) -> (grid, geo)` | gridded product |
| atmospheric (`atmospheric.core`) | `toa_to_boa(toa_refl, atm, geometry, dem, rt_lut) -> dict`; `classify_scene(boa, params) -> (cls, cloud, shadow)` | BOA reflectance + masks |
| qa (`qa.core`) | `compute_metrics(test, reference) -> MetricSet` (SNR/RMSE/PSNR/MSE/variance) | metrics |

**D. Computing-model declaration (CPM `EOProcessingModel` schema — confirmed 2.8.1).** Each PU's
computing model conforms to the `eopf.computing.validation.EOProcessingModel` schema, **not** a flat
input/output list. The schema and a worked example for `msi_l0_decode`:

```jsonc
// CPM EOProcessingModel: per-mode declaration. Dict keys MAY be regex.
{
  "available_modes": ["default"],          // all supported modes
  "default_mode": "default",               // must be in available_modes
  "modes_config": {                        // one config per mode
    "default": {
      "inputs":  { "l0":  { "type": "product", "spec": { /* EOProductModel */ }, "iterable_allowed": false } },
      "adfs":    {  },                       // {<name>: {"spec": {"required": <bool>}}}
      "outputs": { "l1a": { "type": "product", "spec": { /* EOProductModel */ } } },
      "parameters": {                        // optional **kwargs; {"required": <bool>}
        "profile_id":      { "required": true },
        "profile_version": { "required": true },
        "bit_depth":       { "required": false },
        "line_factor":     { "required": false }
      }
    }
  }
}
```

- `inputs`/`outputs` entries are `DataTypeModel` (`type ∈ {product, container}`, a typed `spec`
  (`EOProductModel`/`EOContainerModel`), `iterable_allowed: bool`); `adfs` entries carry
  `spec.required`; `parameters` entries carry `required`. The CPM validates a workflow unit's wiring
  (mandatory inputs/ADFs present, kwargs valid) against this model (`validate_run_parameters`,
  `validate_output_models`). The per-PU logical declarations of the SDD (<5.4.2>–<5.4.10>:
  inputs/adfs/outputs/parameters/modes) **map onto** `modes_config[<mode>]` of this schema; the
  `mandatory` flags map to `spec.required` (adfs) and to the input/output key being present in the
  mode config.

**E. CPM entry points (confirmed 2.8.1).**

| Element | Definition |
|---|---|
| Console (CPM) | `eopf trigger <payload.{yaml,json}>` (`console_scripts: eopf = eopf.cli.cli:eopf_cli`; subcommand `trigger`) |
| Programmatic | `EORunner().run_from_file(payload_file, working_dir=None)` and `EORunner().run(payload: dict)` (`eopf.triggering.runner`) |
| Project wrapper | `msi-processor <payload>` → `C-COM-CLI.main(argv)` delegating to `C-COM-ORC.run_chain` over the CPM runner (SDD <5.4.11>) |

#### <5.3.5> `ICD-IF-TRIG` — Triggering payload (job order)

**Provided service.** A single CPM payload (YAML or JSON; source: E4 → destination: CPM runner /
`C-COM-ORC`) fully specifies a run. Recognised top-level section keys (**confirmed 2.8.1**,
`eopf/triggering/parsers.py`; `#opt` may be absent):

| Key | Required | Content |
|---|---|---|
| `workflow` | yes | ordered list of PU units to run (table A) — the acyclic stage graph |
| `io` | yes | `input_products`, `adfs`, `output_products` descriptors (tables B/C) |
| `breakpoints` | no | `{all: bool, ids: [str], folder: str, store_params}` — intermediate dumps / level breakpoints (`ICD-IF-TRIG-04`) |
| `dask_context` | no | `{cluster_type (default "address"), cluster_config, client_config, dask_config, performance_report_file}`; omit for CI (REQ-PORT-03) |
| `general_configuration` | no | `EOConfiguration` overrides incl. `triggering__error_policy: FAIL_FAST`, `triggering__validate_run: true`, `triggering__validate_mode: STAC`, `triggering__use_datatree` |
| `logging` / `config` / `secret` / `dotenv` / `external_modules` / `eoqc` | no | logging conf files, config files, secret files, env files, dynamic-import modules, quality-control conf |

**A. `workflow[]` unit (`WorkflowRaw` → `WorkFlowUnitDescription`; confirmed 2.8.1):**

| Field | Type | Default | Meaning | Legality |
|---|---|---|---|---|
| `name` | str | — (req) | unique unit name in the run | unique among active units |
| `module` | str | — (req) | Python module exporting the PU | importable |
| `processing_unit` | str | — (req) | `EOProcessingUnit` class name | found in `module` |
| `inputs` | map | `{}` | `pu_input_name → "io.input id"` \| `"unit.outputname"` | mandatory inputs satisfied (`get_mandatory_input_list`) |
| `adfs` | map | `{}` | `pu_adf_name → "io.adf id"` | mandatory ADFs present (`get_mandatory_adf_list`) |
| `outputs` | map | `{}` | `pu_output_name → "io.output id"` (regex allowed) | — |
| `parameters` | map | `{}` | passed as `**kwargs` to `run(...)` | per PU computing model |
| `step` | int | `0` | execution-order index in the DAG | — |
| `active` | bool | `true` | run this unit (inactive ⇒ skipped) | drives sub-chain selection |
| `validate` | bool | `true` | validate outputs when `validate_run` on | — |
| `mode` | str \| null | `null` | PU mode (defaults to `get_default_mode()`) | in `available_modes` |

**B. `io.input_products[]` (`EOInputRaw`) / `io.adfs[]` (`EOADFRaw`)** (source: E1/E2; confirmed 2.8.1):

| Field | input_products | adfs | Notes |
|---|---|---|---|
| `id` | yes | yes | referenced by `workflow.inputs` / `workflow.adfs` |
| `path` | yes (URI) | yes (URI) | local FS or `s3::…` (`AnyPath`, REQ-IF-COM-02); read-only |
| `store_type` | yes | — (n/a) | `safe` / `zarr` / profile-registered L0 reader (`EOStoreFactory`); **ADFs have no `store_type`** (handled inside the ADF) |
| `store_params` | no (`{}`) | no (`{}`) | `storage_options`, regex, etc. |
| `type` | `filename`/`regex` (`PathType`, default `filename`) | — | input resolution mode |

**C. `io.output_products[]` (`EOOutputRaw`)** (destination: E5; confirmed 2.8.1):

| Field | Value / range |
|---|---|
| `id` | referenced by `workflow.outputs` |
| `path` | output URI (local FS / `s3::…`, `AnyPath`) |
| `store_type` | `zarr` (mandated, `ICD-IF-OUT-01`) |
| `type` | `filename` \| `folder` (`PathType`, default `filename`) |
| `opening_mode` | `CREATE` (default) \| `CREATE_OVERWRITE` \| `CREATE_NO_OVERWRITE` \| `UPDATE` \| `APPEND` (`OpeningMode`; must be allowed by the store) |
| `store_params` | e.g. `{compressor: {id: zstd, level, shuffle}, storage_options}` or `{}` |
| `apply_eoqc` | bool (default `false`) — apply CPM quality-control on write |

- **Profile selection (resolved).** Carried as the `profile_id` / `profile_version` entries in the
  relevant active unit's `parameters` map (passed as `**kwargs` to `run(...)`, SDD <5.4.2>); the profile
  JSON itself is referenced via a `config` file or a profile URI parameter and loaded/validated by
  `C-COM-PROFILE`. Resolves the prior PDR placement `[TBC]` (`ICD-IF-PROF-02`).
- **Error policy / validation (resolved).** `general_configuration.triggering__error_policy` ∈
  `{FAIL_FAST, FAIL_ON_CRITICAL, BEST_EFFORT}`; `msi-processor` mandates `FAIL_FAST` (REQ-F-DEP-01).
  `triggering__validate_run` enables per-unit output validation at `triggering__validate_mode`
  (`STRUCTURE`/`STAC`/`NONE`).
- **CI/local variant (`ICD-IF-TRIG-03`):** `store_type: zarr`, local `path`s, no `dask_context` (the
  CPM defaults to a null context), no `secret`/S3 — runnable on the shell runner.

#### <5.3.6> `ICD-IF-PROF` — Sensor-profile / configuration

**Provided service.** A versioned JSON object (source: E3) that specialises the generic chain;
validated on load by `C-COM-PROFILE` (`ICD-IF-PROF-01`, REQ-DAT-03, SDD <5.4.11>/<5.4.12>).
JSON-Schema controlled; invalid/incomplete ⇒ `ProfileValidationError` with diagnostic. Top-level schema
(field id = dotted path):

| Field (id) | Type | Description | Legality |
|---|---|---|---|
| `profile_id` | str | unique profile identifier | required, unique |
| `version` | str (SemVer) | profile version | required |
| `sensor_id` | str | instrument id (matches L0 `sensor_id`) | required |
| `modes[]` | list[str] | supported instrument modes | non-empty |
| `bands[]` | list[obj] | `{name, centre_wavelength_nm, srf_ref, esun, line_factor}` | ≥1; names unique |
| `focal_plane` | obj | `{n_detectors, samples_per_line, bit_depth}` | bit_depth>0 |
| `adf_bindings` | obj | default ADF ids per type (`radiometric,dark,flatfield,badpixel,spectral,viewing_model,dem,gcp,atmospheric`) | mandatory types bound |
| `radiometric` | obj | dark/NUC thresholds (`g_min,g_max`), saturation/no-data values, `remove_dark_fft` | — |
| `enhancement` | obj | `{denoise:{method,params}, sharpen:{kernel}, enabled:bool}` | method ∈ allowed set |
| `coregistration` | obj | `{reference_band, matcher_params, thresholds, seed}` | reference_band ∈ bands |
| `geometry` | obj | `{crs, grid, resolution, resampling, use_gcp}` | valid CRS |
| `pansharpen` | obj | `{enabled, method, pan_band}` | if enabled, pan_band set |
| `atmospheric` | obj | `{mode: retrieve\|ingest, source, classification_opts}` | mode ∈ enum |
| `output` | obj | `{crs, grid, resolution, chunking, packing, fill_value, store_target}` | chunking>0 |
| `optional_stages` | obj | per-stage enable flags (`enhancement,pansharpen,…`) default off where unvalidated (REQ-F-ENH-03) | bool |
| `breakpoints` | obj | default breakpoint levels | — |

- **Adaptation rule (REQ-IF-AD-01 / REQ-AD-01):** the processing core reads all sensor-specific data
  from this profile; adding a sensor = adding a profile (+ private ADFs), no core change (REQ-D-07).
  First instantiated profile = the project owner's sensor (REQ-AD-02); its numeric content is private.
- The typed `Profile` (SDD `C-COM-PROFILE.Profile`) is the in-code mirror of this schema; the
  JSON-Schema file (`sensors/profile.schema.json`) is delivered as configuration (REQ-DEL-03), id/
  version tracked with the profile version.

#### <5.3.7> `ICD-IF-DIAG` & `ICD-IF-HMI` — status, diagnostics and CLI (MMI)

**Provided service (`ICD-IF-DIAG`).** Machine-readable run outcome surfaced to E4 (SDD
`C-COM-ORC.RunResult`):

| Item id | Description | Representation | Range |
|---|---|---|---|
| exit status | process completion | int | `0` success, `≠0` failure (fail-stop, REQ-F-DEP-01) |
| structured diagnostics | errors/warnings | JSON log records | per logging conf |
| processing report | parameters, ADF/profile ids, per-product QA summary | JSON + human-readable | present on every run (REQ-O-02) |
| per-product QA | flags/metrics carried in `quality/` (table <5.3.3>E) | in product | — |

**Provided service (`ICD-IF-HMI`).** Non-interactive entry points (no GUI, REQ-HF-01):

| Item id | Description | Representation |
|---|---|---|
| CLI (project) | `msi-processor <payload.{yaml,json}>` → `C-COM-CLI.main(argv)` | argv |
| CLI (CPM) | `eopf trigger <payload>` (CPM console script) | argv |
| Python API | `EORunner().run_from_file(payload_file, working_dir=None)` / `EORunner().run(payload)` / direct PU `run(...)` (table <5.3.4>A) | function call |
| inputs | triggering payload (<5.3.5>) + config/profile files | files/URIs |
| outputs | exit status + diagnostics (`ICD-IF-DIAG`) + Zarr product (`ICD-IF-OUT`) | files/streams |

---

## <6> Validation requirements

**Approach (Annex E <6>a).** Each uniquely identified interface requirement of <5.2> carries an inline
**Verify:** method (T/A/I/R). Validation reuses the V&V process of SRS <6> / RD-8: schema and structure
checks by **inspection/review** against this ICD and the PSFD; **automated tests** (`pytest`, CPM
`run_validating` / `validate(validation_mode)`) in public CI for everything not needing private data, a
container runtime, a Dask gateway or S3; and **local** tests on real data/ADFs for the field-level
content of the private interfaces. Interfaces needing those services or private data run non-blocking in
CI and are validated locally (REQ-PORT-03). The detailed interface→test-case trace is maintained in RD-9.

**Validation matrix (Annex E <6>b — requirement → method → means).**

| Interface req. | Method | Means / milestone |
|---|---|---|
| ICD-IF-L0-01 | I, T | Decode a sample `L0c` (local); assert `L1A` DataTree vs <5.3.1>A |
| ICD-IF-L0-02 | I, T | Inspect selection metadata; resolve profile/ADF from a sample `L0c` |
| ICD-IF-L0-03 | A, I | Static analysis / inspection: no write path to L0 (`OpeningMode.OPEN`) |
| ICD-IF-ADF-01 | I, T | Load gain/offset, dark, flat-field as `AuxiliaryDataFile`; assert content vs <5.3.2>A (local) |
| ICD-IF-ADF-02 | I, T | Inspect id/version/validity attrs; select valid ADF for a given `L0c` |
| ICD-IF-ADF-03 | I, A | Repo/CI scan: no ADF content committed; runtime-URI resolution |
| ICD-IF-ADF-04 | A, I | Static analysis / inspection: ADFs opened read-only |
| ICD-IF-OUT-01 | T, I | Write `EOProduct` via `EOZarrStore`; assert DataTree vs <5.3.3>A + `MANDATORY_FIELD` |
| ICD-IF-OUT-02 | T | Chunked partial read; write POSIX (CI) + S3 (when available) |
| ICD-IF-OUT-03 | I, T | Inspect provenance/STAC attrs vs <5.3.3>D; assert no private coefficients |
| ICD-IF-SW-01 | R, I | Review PU class attrs + `EOProcessingModel` JSON vs <5.3.4>A/D |
| ICD-IF-SW-02 | R, T | Round-trip `EOProduct`/`EOZarrStore`; review no I/O outside CPM |
| ICD-IF-SW-03 | I | Inspect pinned `eopf == 2.8.1` (done — `cpm_env`) + build image |
| ICD-IF-SW-04 | T | Unit-test pure cores without CPM runtime (<5.3.4>C, `IF-CORE-01`) |
| ICD-IF-SW-05 | I | Inspection: no hardware interface (N/A closure) |
| ICD-IF-TRIG-01 | I, T | Inspect payload vs <5.3.5>; trigger a run from a sample payload |
| ICD-IF-TRIG-02 | T | Trigger with local + remote (when available) URIs |
| ICD-IF-TRIG-03 | T | Trigger + verify on the CI shell runner (local-FS variant) |
| ICD-IF-TRIG-04 | T | Sub-chain run via `active`/`step`/`breakpoints`; assert start/stop at level |
| ICD-IF-PROF-01 | T, I | Load valid + invalid profile vs JSON-Schema; reject-with-diagnostic test |
| ICD-IF-PROF-02 | I, T | Inspect id/version; select profile per run via payload `parameters` |
| ICD-IF-DIAG-01 | T | Assert exit status + diagnostics/QA on success and forced failure |
| ICD-IF-HMI-01 | I, T | Invoke via CLI/API; confirm no GUI dependency |

**Requirements not validated against the baseline.** `ICD-IF-SW-05` (no hardware interface) is an N/A
closure verified by inspection. Field-level items still flagged **`[TBC@impl]`** (the sensor-private L0
on-wire codec, the viewing-model coefficient form, the legacy ADF container, QA bit 7) are confirmed
against real data during implementation (SDP WP-5), not at CDR; the CPM-surface items previously flagged
`[TBC@CDR]` are **resolved** at this issue against the installed `eopf == 2.8.1` (clause <2> note).

---

## <7> Traceability

Per Annex E <7>a the forward and backward interface traceability is reported below; the authoritative,
tool-maintained matrix (incl. trace to design `C-*`/`IF-*` and test cases) is RD-9 (Annex E <7>b — DJF
reference).

### <7.1> Forward — upper-level interface req. (IRD `REQ-IF-*`) → ICD interfaces

| IRD `REQ-IF-*` | Realised by |
|---|---|
| REQ-IF-CAP-01 | ICD-IF-TRIG-01/04, ICD-IF-SW-01 |
| REQ-IF-CAP-02 | ICD-IF-OUT-02, ICD-IF-SW-02 |
| REQ-IF-CAP-03 | ICD-IF-OUT-03 |
| REQ-IF-CAP-04 | ICD-IF-TRIG-01, ICD-IF-SW-01 |
| REQ-IF-CAP-05 | ICD-IF-DIAG-01 |
| REQ-IF-IN-L0-01..03 | ICD-IF-L0-01/02/03 |
| REQ-IF-IN-ADF-01..04 | ICD-IF-ADF-01/02/03/04 |
| REQ-IF-OUT-01..04 | ICD-IF-OUT-01/02/03, ICD-IF-SW-02 |
| REQ-IF-SW-01..04 | ICD-IF-SW-01/02/03/04 |
| REQ-IF-COM-01..03 | ICD-IF-TRIG-01/02/03 |
| REQ-IF-HW-01 | ICD-IF-SW-05 |
| REQ-IF-HMI-01 | ICD-IF-HMI-01 |
| REQ-IF-SEC-01..03 | ICD-IF-ADF-02/03/04, ICD-IF-L0-03, ICD-IF-OUT-03 |
| REQ-IF-AD-01..04 | ICD-IF-PROF-01/02 |

### <7.2> Backward — ICD interfaces → upper-level (IRD `REQ-IF-*` / SRS `REQ-*`)

| ICD interface | Parent IRD | Parent SRS |
|---|---|---|
| ICD-IF-L0-* | REQ-IF-IN-L0-01..03 | REQ-F-L0-01..05, REQ-I-03 |
| ICD-IF-ADF-* | REQ-IF-IN-ADF-01..04, REQ-IF-SEC-01/02 | REQ-F-RAD-01..05, REQ-F-TOA-01, REQ-F-ATM-01, REQ-DAT-02, REQ-S-04, REQ-M-02 |
| ICD-IF-OUT-* | REQ-IF-OUT-01..04, REQ-IF-CAP-03 | REQ-F-PRD-01/02, REQ-F-QA-02, REQ-I-04, REQ-DAT-01, REQ-D-09 |
| ICD-IF-SW-* | REQ-IF-SW-01..04, REQ-IF-HW-01 | REQ-D-01/03/06, REQ-F-ORC-01, REQ-R-02/03 |
| ICD-IF-TRIG-* | REQ-IF-COM-01..03, REQ-IF-CAP-01 | REQ-I-05/06, REQ-O-01, REQ-F-ORC-01, REQ-PORT-03 |
| ICD-IF-PROF-* | REQ-IF-AD-01..04 | REQ-AD-01/02, REQ-DAT-03, REQ-D-07 |
| ICD-IF-DIAG-* | REQ-IF-CAP-05 | REQ-O-03, REQ-F-DEP-01 |
| ICD-IF-HMI-* | REQ-IF-HMI-01 | REQ-HF-01, REQ-I-02 |

> The traceability of clause <7> is consolidated and kept current in RD-9
> (`compliance/traceability/`); this satisfies Annex E <7>b. The downward trace to the design components
> (`C-*`) and internal interfaces (`IF-*`) is in SDD <6> (RD-5).

---

*End of ICD (final / CDR issue). Authored per ECSS-E-ST-40C Rev.1 Annex E. This issue finalises the
field-level interface design at CDR, superseding the PDR preliminary issue. CPM-surface items are
resolved against the installed `eopf == 2.8.1`; only genuinely sensor-private encodings remain
`[TBC@impl]` (confirmed during implementation, SDP WP-5). The EOPF PSFD is the normative
product-structure reference. Upstream interface requirements are in the IRD (RD-3) and SRS (RD-4); the
detailed design is in the SDD (RD-5); the maintained traceability matrix is RD-9.*
