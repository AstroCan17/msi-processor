# Interface Control Document (ICD)

| Field | Value |
|---|---|
| **Document** | ICD — Interface Control Document |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex E |
| **Container** | Technical Specification (TS) — `compliance/drd/` (source), published subset in `docs/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | PDR (Preliminary Design Review) — finalised at CDR |
| **Status** | Draft for PDR |

> This ICD is a major constituent of the Technical Specification of `msi-processor`. It gives the
> **concrete interface definitions** that realise the interface requirements `REQ-IF-*` of the IRD
> (RD-3) and bind the software requirements `REQ-*` of the SRS (RD-4). It follows the
> ECSS-E-ST-40C Rev.1 Annex E section structure and the heading style of the SDP (RD-1). Where the
> IRD states *what* an interface shall do, this ICD states *how it is controlled*: group/variable
> trees, field-level schemas, encodings, dtypes, chunking, CRS encoding, ADF content, the EOPF CPM
> software signatures, the triggering payload syntax and the sensor-profile schema. The EOPF
> **Product Structure & Format Definition (PSFD)** is the normative product-structure reference
> (AD-4). Per Annex E.1.2 this ICD is **preliminary at PDR** and **finalised at CDR**: items whose
> exact encoding depends on the private owner sensor or on the pinned CPM wheel are flagged
> **[TBC@CDR]**. The footprint is tailored to a Category C, single-developer ground-segment
> processor.

---

## <1> Introduction

**Purpose.** This document specifies and controls the external interfaces of `msi-processor` at
field level: the downlinked RAW Level-0 (`L0c`) input, the private instrument-calibration Auxiliary
Data Files (ADF), the Level-1/Level-2 cloud-native Zarr `EOProduct` outputs, the EOPF CPM software
interfaces (`EOProduct`/`EOGroup`, `EOProcessingUnit`, `EOZarrStore`), the triggering payload
(job order) and the sensor-profile/configuration interface.

**Objective.** The ICD turns the requirement-level interface envelope of the IRD into the concrete,
verifiable interface control that the detailed design (SDD, RD-5), implementation and V&V (RD-8)
build against. Each interface is uniquely identified (`ICD-IF-*`), traced to its parent
`REQ-IF-*` / `REQ-*`, and assigned a validation method (clause <6>) and a forward/backward trace
(clause <7>).

**Content.** Clause <4> points to the software overview in the SRS/SSS (not duplicated). Clause <5>
is the body: <5.1> general provisions (identification, in-model id assignment, traceability),
<5.2> the **interface requirements** — the inventory of external interfaces and the controlled
requirements imposed on each — and <5.3> the **interface design** — the field-level definitions
(data-item tables, group/variable trees, signatures, payload and profile schemas). Clause <6> gives
the per-interface validation approach and matrix; clause <7> the traceability.

**Reason for preparation.** `msi-processor` is an integration and ECSS-productisation effort: the
processing chain is a sequence of EOPF CPM `EOProcessingUnit`s exchanging `EOProduct`s and writing
cloud-native Zarr. Because the chain is sensor-agnostic and the raw/calibration data are private,
the interfaces must be fixed concretely — but parameterised by the sensor profile and referenced by
runtime URI — before detailed design begins. This ICD is produced at PDR to start that control and
is finalised at CDR.

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
| RD-5 | `msi-processor` Software Design Document (SDD) | `compliance/drd/sdd-software-design.md` (CDR) |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — per-level algorithm basis | `docs/dpm/` |
| RD-7 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-8 | `msi-processor` V&V plan (SVerP/SValP/SUITP merged) | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Traceability matrix | `compliance/traceability/traceability-matrix.md` (CDR) |
| RD-10 | Prior work — multispectral pushbroom preprocessing pipeline (calibration/format heritage; see SRF) | RD-7 |
| RD-11 | Cloud-native data conventions | Zarr v2/v3, CF metadata, STAC, GeoZarr |

> **Verification note (Annex E.1.2 / project working principle "verify, don't assume").** The CPM
> signatures, the `AuxiliaryDataFile` dataclass, the `EOProduct`/`EOGroup` contracts and the
> triggering-payload keys in clause <5.3> were read from the EOPF CPM source tree (`eopf/computing`,
> `eopf/product`, `eopf/store`, `eopf/triggering`). The exact API surface is **pinned to
> `eopf == 2.8.1`** for this project and is re-confirmed against that wheel at CDR finalisation
> (**[TBC@CDR]** where minor-version drift is possible).

---

## <3> Terms, definitions and abbreviated terms

Only terms/abbreviations not already in the SSS <3>, IRD <3> and SRS <3> glossaries (which apply in
full) are listed.

| Term / abbr. | Definition |
|---|---|
| DataTree | The `EOProduct`/`EOGroup` hierarchical (group → group/variable) structure; the EOPF in-memory product model |
| EOObject | Base type of any node in the product tree (`EOGroup` or `EOVariable`) |
| `MappingDataType` | CPM type alias `Mapping[str, DataType]` — the keyed product set exchanged at a PU boundary |
| `MappingAuxiliary` | CPM type alias `Mapping[str, AuxiliaryDataFile]` — the keyed ADF set passed to a PU |
| grid_mapping | CF/GeoZarr attribute carrying the CRS encoding of a gridded variable |
| computing-model JSON | The per-PU model file (`PROCESSOR_NAME`/`PROCESSOR_VERSION`) declaring mandatory inputs, ADFs, outputs, parameters and modes |
| store_type | CPM store/format selector in the triggering payload (`zarr`, `safe`, or a profile-registered L0 reader) |
| opening_mode | CPM output store mode: `CREATE` / `CREATE_OVERWRITE` / `UPDATE` |
| validation_mode | CPM product-validation level: `STRUCTURE` / `STAC` |
| `[TBC@CDR]` | To-be-confirmed: detail fixed at CDR finalisation (sensor-private encoding or exact 2.8.1 surface) |

---

## <4> Software overview

The software overview is given in SRS (RD-4) <4> and SSS <4> and is not duplicated here (Annex E
<4>a permits reference). In summary: `msi-processor` is a batch, non-interactive, sensor-agnostic
processor that transforms `L0c` RAW MSI data into Zarr `EOProduct`s up to `L2A` through a chain of
EOPF CPM `EOProcessingUnit`s, driven by a per-sensor profile and private calibration ADFs. The
external boundary (actors E1–E6) is defined in IRD <4.1>; this ICD controls the data and software
interfaces crossing that boundary.

---

## <5> Requirements and design

### <5.1> General provisions to the requirements in the IRD

- **a. (Annex E <5.1>a — unique identification).** Each interface is identified by
  `ICD-IF-<group>` and each controlled requirement on it by `ICD-IF-<group>-NN`. Groups:
  `L0` (L0 input), `ADF` (calibration ADF), `OUT` (L1/L2 output), `SW` (CPM software),
  `TRIG` (triggering payload), `PROF` (sensor profile), `DIAG` (status/diagnostics), `HMI` (CLI).
- **b. (Annex E <5.1>b — identifiers within models).** Where an interface is expressed as a model
  (Zarr DataTree, profile JSON schema, payload schema), identifiers are assigned *within* the model
  by the dotted **path** of the node/field (e.g. `OUT:/measurements/reflectance/<band>`,
  `PROF:bands[].esun`); these paths are the traceable interface item ids.
- **c. (Annex E <5.1>c — traceability).** Each interface and data item states its parent
  `REQ-IF-*` (IRD) and `REQ-*` (SRS) inline; the consolidated matrices are clause <7> and RD-9.
- **d. (units & conventions).** SI / radiometric physical units are stated per data item; variable,
  band, dimension and field naming follow the EOPF data-model / PSFD conventions (SRS REQ-I-07).
  All product and ADF locations are **URIs** (location-transparent local FS / S3); private inputs
  are referenced, never embedded (IRD REQ-IF-SEC-02).

### <5.2> Interface requirements

This clause lists and describes the software item's external interfaces (Annex E <5.2>a) and the
controlled requirements imposed on each; the field-level **design** of every interface is in <5.3>.
Per Annex E <5.2>b the three mandated interface classes are covered: software-to-software
(`ICD-IF-SW`, `ICD-IF-TRIG`), software-to-hardware (none — see `ICD-IF-SW-05`) and the man–machine
interface (`ICD-IF-HMI`, `ICD-IF-DIAG`). Data, logical interface architecture, error behaviour and
observable data (Annex E <5.2>b.4) are covered within the relevant interface.

#### <5.2.1> External interface inventory

| Interface id | Name | Direction | Class | Realises (IRD) | Design |
|---|---|---|---|---|---|
| `ICD-IF-L0` | Downlinked RAW `L0c` input product | in (E1→) | data | REQ-IF-IN-L0-01..03 | <5.3.1> |
| `ICD-IF-ADF` | Calibration / auxiliary ADF input | in (E2→) | data | REQ-IF-IN-ADF-01..04 | <5.3.2> |
| `ICD-IF-OUT` | `L1B`/`L1C`/`L2A` Zarr `EOProduct` output | out (→E5) | data | REQ-IF-OUT-01..04, REQ-IF-CAP-03 | <5.3.3> |
| `ICD-IF-SW` | EOPF CPM software interface (PU / product / store) | host (E6) | sw-to-sw | REQ-IF-SW-01..04 | <5.3.4> |
| `ICD-IF-TRIG` | Triggering payload (job order) | in (E4→) | sw-to-sw / comms | REQ-IF-COM-01..03, REQ-IF-CAP-01 | <5.3.5> |
| `ICD-IF-PROF` | Sensor-profile / configuration | in (E3→) | data / adaptation | REQ-IF-AD-01..04 | <5.3.6> |
| `ICD-IF-DIAG` | Completion status & structured diagnostics | out (→E4) | observable / MMI | REQ-IF-CAP-05 | <5.3.7> |
| `ICD-IF-HMI` | Non-interactive CLI / programmatic entry | in/out | MMI | REQ-IF-HMI-01 | <5.3.7> |

#### <5.2.2> Controlled interface requirements

- **ICD-IF-L0-01** — The `L0c` input shall be presented to the chain, after decode, as an `L1A`
  `EOProduct` DataTree with the group layout of <5.3.1>; the **decoder is profile-bound** (sensor
  packetisation is private). *Trace:* REQ-IF-IN-L0-01, REQ-F-L0-01/04. *Verify:* I, T.
- **ICD-IF-L0-02** — The `L0c` input shall carry, or be accompanied by, the selection metadata of
  <5.3.1> table B (sensor id, acquisition time, instrument mode) enabling profile/ADF resolution.
  *Trace:* REQ-IF-IN-L0-02, REQ-F-L0-03. *Verify:* I, T.
- **ICD-IF-L0-03** — The `L0c` source shall be opened **read-only** by the reader; no write path to
  the L0 location shall exist. *Trace:* REQ-IF-IN-L0-03, REQ-F-L0-05. *Verify:* A, I.
- **ICD-IF-ADF-01** — Each calibration input shall be supplied as a CPM `AuxiliaryDataFile`
  (`name`, `path` URI, `store_params`) with the content of <5.3.2>; gain/offset, dark and
  flat-field are mandatory, the rest profile-selected. *Trace:* REQ-IF-IN-ADF-01, REQ-F-RAD-01/02,
  REQ-F-TOA-01. *Verify:* I, T.
- **ICD-IF-ADF-02** — Each ADF shall carry id, version and validity (sensor/profile, time range) in
  the attributes of <5.3.2> table B so the correct ADF is selectable for a given `L0c`.
  *Trace:* REQ-IF-IN-ADF-02, REQ-S-04. *Verify:* I, T.
- **ICD-IF-ADF-03** — ADF content shall be referenced by runtime URI only; no ADF content shall be
  committed to the repository or required by public CI. *Trace:* REQ-IF-IN-ADF-03, REQ-S-01.
  *Verify:* I, A.
- **ICD-IF-ADF-04** — ADFs shall be opened **read-only**. *Trace:* REQ-IF-IN-ADF-04. *Verify:* A, I.
- **ICD-IF-OUT-01** — Outputs shall be cloud-native Zarr `EOProduct`s written via `EOZarrStore`,
  with the DataTree of <5.3.3> (`measurements` / `conditions` / `quality` + metadata).
  *Trace:* REQ-IF-OUT-01/02, REQ-F-PRD-01. *Verify:* T, I.
- **ICD-IF-OUT-02** — Each output shall be chunked per <5.3.3> table C and writable to POSIX and
  S3-compatible backends via the EOPF store abstraction. *Trace:* REQ-IF-OUT-03, REQ-F-ORC-02.
  *Verify:* T.
- **ICD-IF-OUT-03** — Each output shall carry the product+provenance metadata of <5.3.3> table D
  (product id, baseline/version, input/ADF/profile ids+versions, parameters, timestamp) and **no**
  private calibration coefficients. *Trace:* REQ-IF-OUT-04, REQ-IF-CAP-03, REQ-F-PRD-02, REQ-S-05.
  *Verify:* I, T.
- **ICD-IF-SW-01** — Each stage shall be an `EOProcessingUnit` subclass with the class attributes
  and `run(...)` signature of <5.3.4> and a computing-model JSON declaring its inputs/ADFs/outputs/
  parameters/modes. *Trace:* REQ-IF-SW-01, REQ-F-ORC-01. *Verify:* R, I.
- **ICD-IF-SW-02** — Products shall be exchanged as `EOProduct`/`EOGroup` (`MappingDataType`) and
  persisted only via `EOZarrStore`; no product I/O outside these abstractions. *Trace:* REQ-IF-SW-02,
  REQ-D-06. *Verify:* R, T.
- **ICD-IF-SW-03** — The software interfaces shall bind to `eopf == 2.8.1`. *Trace:* REQ-IF-SW-03,
  REQ-R-03. *Verify:* I.
- **ICD-IF-SW-04** — Each stage's pure algorithmic core shall be callable without the CPM runtime
  through the plain signatures of <5.3.4> table C. *Trace:* REQ-IF-SW-04, REQ-D-03. *Verify:* T.
- **ICD-IF-SW-05** — No software-to-hardware interface exists; compute/storage are reached only via
  the OS and the EOPF store abstraction (closes Annex E <5.2>b.2 / <5.3>c.2). *Trace:* REQ-IF-HW-01,
  REQ-R-02. *Verify:* I.
- **ICD-IF-TRIG-01** — A run shall be fully specified by the CPM triggering payload of <5.3.5>
  (`workflow` + `io` + optional `breakpoints`/`dask_context`/config), declaring inputs, ADFs, output
  target, profile selection and parameters. *Trace:* REQ-IF-COM-01, REQ-I-05, REQ-O-01.
  *Verify:* I, T.
- **ICD-IF-TRIG-02** — All payload product/ADF/output references shall be URIs resolved through the
  EOPF store/mapper, location-transparent local/remote. *Trace:* REQ-IF-COM-02, REQ-I-06.
  *Verify:* T.
- **ICD-IF-TRIG-03** — A local-filesystem payload variant (`store_type: zarr`, local paths, no Dask
  gateway/S3) shall run on the CI shell runner. *Trace:* REQ-IF-COM-03, REQ-PORT-03. *Verify:* T.
- **ICD-IF-TRIG-04** — Chain start/stop at level breakpoints shall be controlled via the payload
  `workflow` (`active`) and `breakpoints` sections of <5.3.5>. *Trace:* REQ-IF-CAP-01,
  REQ-F-ORC-01. *Verify:* T.
- **ICD-IF-PROF-01** — The sensor profile shall be a versioned JSON object validated on load against
  the schema of <5.3.6>; it shall externalise all sensor-specific interface content. *Trace:*
  REQ-IF-AD-01/04, REQ-AD-01, REQ-DAT-03. *Verify:* T, I.
- **ICD-IF-PROF-02** — The profile shall be uniquely identified and versioned and selectable per run
  via the payload. *Trace:* REQ-IF-AD-02, REQ-AD-02. *Verify:* I, T.
- **ICD-IF-DIAG-01** — At its boundary the processor shall expose a completion status and the
  machine-readable diagnostics/QA structure of <5.3.7>. *Trace:* REQ-IF-CAP-05, REQ-O-03.
  *Verify:* T.
- **ICD-IF-HMI-01** — Human interaction shall be limited to the CLI of <5.3.7>, configuration files
  and logs/reports; no GUI. *Trace:* REQ-IF-HMI-01, REQ-HF-01. *Verify:* I, T.

> **Error behaviour (Annex E <5.2>b.4).** All interfaces obey the fail-stop policy (SRS REQ-F-DEP-01)
> surfaced through `ICD-IF-DIAG`: on any stage error the run exits non-zero, withholds/flags affected
> outputs and publishes no partial product as complete. The CPM error policy is `FAIL_FAST` (<5.3.5>).

### <5.3> Interface design

Per Annex E <5.3>d each interface definition gives at least the **provided service**, the
**description (name, type, dimension)**, the **range** and the **initial/default value**; per Annex
E <5.3>e data items are organised as (Name, description, unique id (path/key), source→destination,
unit, limit/range, accuracy/precision where applicable, legality checks, data type, data
representation). Sensor-private numbers are parameterised by the profile (<5.3.6>) and flagged
**[TBC@CDR]** where the exact encoding is private.

#### <5.3.1> `ICD-IF-L0` — Downlinked RAW `L0c` input product

**Provided service.** Read-only ingestion of one downlinked RAW MSI acquisition (E1), decoded into
an `L1A` `EOProduct` DataTree in focal-plane geometry. The decode step is realised by a
profile-registered CPM store/reader (`store_type` selected in the payload, <5.3.5>); the on-wire
packetisation is private and **[TBC@CDR]** — only the post-decode interface is controlled here.

**A. `L1A` DataTree after decode** (source: E1 / L0 reader → destination: radiometric PU):

| Path (item id) | Description | Type | Dimension | Range | Data representation |
|---|---|---|---|---|---|
| `/measurements/detector/<band>` | Raw detector samples, focal-plane geometry, per band | `EOVariable` int (unsigned) | `(line, detector)` | `0 … 2^B−1` (`B`=`bit_depth`, default **12** from RD-10) | Zarr/`xarray`, dtype `uint16`, dims from profile |
| `/conditions/time/line_time` | Per-line acquisition timestamp | `EOVariable` float64 | `(line,)` | UTC since epoch | CF `time` units |
| `/conditions/orbit/{position,velocity}` | Platform ephemeris (orbit) ancillary | `EOVariable` float64 | `(t, 3)` | ECEF m, m/s | CF |
| `/conditions/attitude/quaternion` | Platform attitude ancillary | `EOVariable` float64 | `(t, 4)` | unit quaternion | CF |
| `/quality/l0_flags/<band>` | Initial QA (lost-packet / line-loss / fill) | `EOVariable` uint8 | `(line, detector)` | bit-flags (table <5.3.3>E) | Zarr |

- **Number of bands** `N_b`, **detectors/line**, **line-rate factor per band** and **`bit_depth`**
  are profile parameters (`PROF:bands`, `PROF:focal_plane`). Heritage note (RD-10): one band may be
  acquired at a 2× line rate — represented by a per-band `line_factor` in the profile, not hard-coded.
- **Legality checks (REQ-F-L0-03):** mandatory groups present; band set equals the profile band
  list; dims consistent with the profile focal-plane geometry; selection metadata (table B) present.
- **Lost-packet detection (REQ-F-L0-02, heritage):** an all-zero line following a non-zero line
  marks a line-loss; affected lines are truncated/flagged in `/quality/l0_flags`.

**B. L0 selection metadata** (drives profile/ADF resolution; source: E1 → destination: orchestrator/PU):

| Item id | Description | Type | Legality check |
|---|---|---|---|
| `sensor_id` | Instrument/sensor identifier | str | matches a known profile `sensor_id` |
| `acquisition_time` | Acquisition start (UTC) | ISO-8601 str | within an ADF validity range |
| `instrument_mode` | Instrument mode/configuration | str | in profile `modes` |
| `l0_product_id` | Unique L0 identifier | str | non-empty; recorded in provenance |

#### <5.3.2> `ICD-IF-ADF` — Calibration / auxiliary ADF input

**Provided service.** Read-only supply of private instrument-calibration and auxiliary data as CPM
`AuxiliaryDataFile`s. Each ADF is passed to a PU in the `adfs` mapping keyed by the PU's declared
ADF name (`AuxiliaryDataFile(name, path, store_params)`; `path` is a URI). Storage form is
cloud-native **Zarr** (preferred, PSFD ADF convention) or NetCDF/GeoTIFF where heritage dictates;
the **content schema** below is normative, the on-disk container is **[TBC@CDR]**.

**A. ADF content by type** (source: E2 → destination: the named PU):

| ADF key (item id) | Mandatory | Content / variables | Type · dim | Used by (SRS) |
|---|---|---|---|---|
| `radiometric` | yes | per-band absolute gain `gain[b]`, offset `offset[b]` | float32 · `(band[,detector])` | REQ-F-TOA-01: `radiance=(DN−offset)·gain` |
| `dark` | yes | per-band dark/offset (DSNU) reference frame(s) | float32 · `(band, line, detector)`→reduced | REQ-F-RAD-01 |
| `flatfield` | yes | per-band flat-field (PRNU) reference | float32 · `(band, line, detector)` | REQ-F-RAD-02 (NUC) |
| `nuc` | derived | per-band NUC `gain[b]`,`offset[b]` (from dark+flat) | float32 · `(band, detector)` | REQ-F-RAD-02/05 |
| `badpixel` | profile | per-band defective-detector mask | uint8/bool · `(band, detector)` | REQ-F-RAD-03 |
| `spectral` | profile | per-band centre wavelength, ESUN, SRF ref | float32 · `(band,)` | REQ-F-TOA-02 |
| `viewing_model` | profile | viewing/geometric model coefficients | model · [TBC@CDR] | REQ-F-GEO-01 |
| `dem` | profile | digital elevation model | int16/float32 · `(y, x)` | REQ-F-GEO-02 |
| `gcp` | profile | ground-control / reference points | table | REQ-F-GEO-02 |
| `atmospheric` | profile | AOT, water vapour, atmos-model params | float32 · grid/scalar | REQ-F-ATM-01/02 |

- **NUC derivation (heritage RD-10, REQ-F-RAD-05), informative:**
  `gain = (mean(flat) − mean(dark)) / (flat − dark)`, `offset = mean(flat) − gain·flat`; detectors
  with out-of-range gain are flagged into `badpixel`. The full algorithm basis is the DPM (RD-6).

**B. ADF identification & validity attributes** (every ADF; legality-checked on selection):

| Item id (attr) | Description | Type | Legality check |
|---|---|---|---|
| `adf_id` | Unique ADF identifier | str | non-empty; recorded in provenance |
| `adf_version` | ADF version | str (SemVer) | non-empty |
| `sensor_id` / `profile_id` | Applicability | str | equals the run's sensor/profile |
| `validity_start` / `validity_stop` | Applicability time range | ISO-8601 | spans `acquisition_time` |
| `adf_type` | One of the keys in table A | enum | in table A |

- **Access:** opened read-only (`ICD-IF-ADF-04`); referenced by URI only, never committed
  (`ICD-IF-ADF-03`); selection mismatch ⇒ reject/flag (REQ-S-04).

#### <5.3.3> `ICD-IF-OUT` — `L1B`/`L1C`/`L2A` Zarr `EOProduct` output

**Provided service.** Self-describing cloud-native Zarr `EOProduct` written via `EOZarrStore`,
consumable by E5. The product is an `EOGroup` tree whose mandatory root field is `measurements`
(CPM `EOProduct.MANDATORY_FIELD = ("measurements",)`). The level determines the `measurements`
content; `conditions` and `quality` and the metadata are common.

**A. EOProduct DataTree (group hierarchy)** (source: writer PU → destination: E5):

```
/                                   EOProduct root (attrs: STAC + provenance, table D)
├── measurements/                   (mandatory)
│   ├── radiance/<band>             L1B: TOA spectral radiance        [L1B]
│   └── reflectance/<band>          L1B TOA refl. / L1C ortho TOA / L2A BOA  [L1B|L1C|L2A]
├── conditions/
│   ├── geometry/{sun_zenith,sun_azimuth,view_zenith,view_azimuth}    angles
│   ├── geolocation/{x,y | longitude,latitude}  + spatial_ref(grid_mapping)  [L1C+]
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
| Data type | `uint16` packed with `scale_factor`/`add_offset`, or `float32` reflectance `[0,1]` [TBC@CDR per profile] |
| Range | radiance ≥ 0 (sensor units); reflectance `0.0 … 1.0` (clipped, REQ-D-05) |
| `_FillValue` | sensor no-data sentinel (profile) |
| Initial value | n/a (computed) |
| Legality / accuracy | per-profile `RAD_ACC` (`L1B`), `BOA_ACC` (`L2A`) budgets, verified locally (REQ-P-01/03) |

**C. Chunking & CRS encoding** (REQ-IF-OUT-03 / REQ-F-ORC-02):

| Item | Definition |
|---|---|
| Chunking | per-variable Zarr chunks `(y_chunk, x_chunk)` from `PROF:output.chunking` (default e.g. 1024×1024 [TBC@CDR]); enables larger-than-memory lazy read/write |
| Compression | Zarr codec from payload `store_params` (e.g. `zstd` level 3); `null` = uncompressed |
| CRS encoding | `conditions/geolocation/spatial_ref` variable carrying CF/GeoZarr `grid_mapping` (CRS WKT/EPSG from `PROF:output.crs`); referenced by measurement vars via `grid_mapping` attr |
| Grid | output CRS, grid origin, `resolution` from `PROF:output.{crs,grid,resolution}` |

**D. Product & provenance metadata** (root `attrs`; source: writer PU; REQ-IF-CAP-03 / REQ-F-PRD-02):

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
| STAC properties | `datetime`, `bbox`, `proj:epsg`, `eo:bands`, … | STAC/CF | GeoZarr/STAC valid |

**E. Per-pixel QA flag bit definition** (`quality/mask/<band>`, uint8/uint16 bitmask;
propagated across all stages, REQ-F-QA-02):

| Bit | Flag | Set by |
|---|---|---|
| 0 | no-data / fill | L0, all stages |
| 1 | lost-packet / line-loss | L0 (REQ-F-L0-02) |
| 2 | saturated | radiometric (REQ-F-RAD-04) |
| 3 | defective-pixel (replaced) | radiometric (REQ-F-RAD-03) |
| 4 | co-registration failure | geometric (REQ-F-COR-03) |
| 5 | cloud | atmospheric (REQ-F-ATM-03) |
| 6 | cloud-shadow | atmospheric (REQ-F-ATM-03) |
| 7 | reserved | [TBC@CDR] |

#### <5.3.4> `ICD-IF-SW` — EOPF CPM software interface

**Provided service.** The host CPM contracts (E6) the software realises. Verified against the CPM
source tree; bound to `eopf == 2.8.1` (re-confirmed at CDR, see <2> note).

**A. `EOProcessingUnit` (stage) contract** — each stage subclasses `eopf.computing.EOProcessingUnit`:

| Element | Definition |
|---|---|
| Class attributes | `PROCESSOR_NAME: str`, `PROCESSOR_VERSION: str`, `PROCESSOR_LEVEL: str`, `PROCESSOR_MODEL: bool` |
| Computing model | `models/<name>_<version>.json` declaring mandatory inputs, ADFs, outputs, parameters, modes; loaded via `processing_model()` |
| Core method | `run(self, inputs: Mapping[str, DataType], adfs: Optional[Mapping[str, AuxiliaryDataFile]] = None, mode: Optional[str] = None, **kwargs) -> Mapping[str, DataType]` |
| Validated entry | `run_validating(self, inputs, adfs=None, mode=None, validation_mode=ValidationMode.STRUCTURE, **kwargs)` — validates params, runs, appends processing history, validates outputs |
| Modes | `get_available_modes()`, `get_default_mode()` (default `"default"` if no model) |
| Mandatory decls | `get_mandatory_input_list()`, `get_mandatory_adf_list()` |

- `inputs` keys = the PU's declared input names; values are `EOProduct`/`EOGroup` (`DataType`).
- `adfs` keys = the PU's declared ADF names; values are `AuxiliaryDataFile`.
- `**kwargs` = the run **parameters** (sourced from the payload `parameters`, <5.3.5>).
- Return = `Mapping[str, DataType]` of output products keyed by the PU's declared output names.

**B. Product & store contracts:**

| Element | Definition |
|---|---|
| `EOProduct(EOGroup)` | dict-like product tree; `MANDATORY_FIELD = ("measurements",)`; `[]` get/set of `EOObject`; `.attrs`; `.validate(validation_mode)` |
| `EOGroup` | `MutableMapping[str, EOObject]`; holds sub-groups and `EOVariable`s with dims/coords |
| `EOZarrStore(EOProductStore)` | `EOZarrStore(url)`; `.open(mode=…, **store_params)`; `product = store[key]`; `store[key] = eo_object`; cloud-native Zarr persistence (POSIX/S3) |
| `AuxiliaryDataFile` / `ADF` | dataclass `(name: str, path: AnyPath, store_params: dict|None=None, data_ptr: Any=None)`; `.path` property |

**C. Pure algorithmic-core signatures** (callable without CPM, REQ-IF-SW-04 / REQ-D-03;
the PU is a thin adapter). Indicative per-stage cores (final names in SDD RD-5):

| Core (module) | Signature (indicative) | Returns |
|---|---|---|
| radiometric | `correct_radiometry(dn, gain, offset, dark, bad_pixel_map, params) -> ndarray` | corrected DN + QA |
| toa | `dn_to_radiance(dn, gain, offset) -> ndarray`; `radiance_to_reflectance(rad, esun, sun_zenith, earth_sun_dist) -> ndarray` | radiance / reflectance |
| coregistration | `coregister(bands, ref_band, params) -> (stack, residuals)` | aligned stack + QA |
| georeferencing | `orthorectify(bands, viewing_model, dem, gcps, crs, grid, resampling) -> (grid, geo)` | gridded product |
| atmospheric | `toa_to_boa(toa_refl, aot, water_vapour, model, dem) -> ndarray` | BOA reflectance |
| qa | `compute_metrics(ref, test) -> dict` (SNR/RMSE/PSNR/MSE/variance) | metrics dict |

#### <5.3.5> `ICD-IF-TRIG` — Triggering payload (job order)

**Provided service.** A single CPM payload (YAML or JSON; source: E4 → destination: CPM runner)
fully specifies a run. Top-level keys (CPM-defined; `#Optional` ones may be absent):

| Key | Required | Content |
|---|---|---|
| `workflow` | yes | ordered list of PU units to run (table A) — the acyclic stage graph |
| `io` | yes | `input_products`, `adfs`, `output_products` descriptors (tables B/C) |
| `breakpoints` | no | `{all: bool, ids: [..], folder, store_params}` — intermediate dumps / level breakpoints (`ICD-IF-TRIG-04`) |
| `dask_context` | no | `{cluster_type, cluster_config, client_config}`; omit / `local` for CI (REQ-PORT-03) |
| `general_configuration` | no | EOConfiguration incl. `triggering__error_policy: FAIL_FAST`, `triggering__validate_run`, `triggering__validate_mode: STAC` |
| `logging` / `config` / `secret` / `dotenv` / `eoqc` | no | logging conf, config files, secret files, env, quality-control conf |

**A. `workflow[]` unit (`WorkFlowUnitDescription`):**

| Field | Type | Meaning | Legality |
|---|---|---|---|
| `name` | str | unique unit name in the run | unique among active units |
| `active` | bool | run this unit (drives sub-chain selection) | — |
| `validate` | bool | validate outputs when `validate_run` on | — |
| `module` | str | Python module exporting the PU | importable |
| `processing_unit` | str | `EOProcessingUnit` class name | found in `module` |
| `inputs` | map | `pu_input_name → "io.input id"` \| `"unit.outputname"` | declared inputs satisfied |
| `adfs` | map | `pu_adf_name → "io.adf id"` | mandatory ADFs present |
| `outputs` | map | `pu_output_name → "io.output id"` (regex allowed) | — |
| `parameters` | map | passed as `**kwargs` to `run(...)` | per PU computing model |

**B. `io.input_products[]` / `io.adfs[]`** (source: E1/E2):

| Field | input_products | adfs | Notes |
|---|---|---|---|
| `id` | yes | yes | referenced by `workflow.inputs` / `workflow.adfs` |
| `path` | yes (URI) | yes (URI) | local FS or `s3::…` (REQ-IF-COM-02); read-only |
| `store_type` | yes | — | `safe` / `zarr` / profile-registered L0 reader |
| `store_params` | no | no | `storage_options`, regex, etc. |
| `type` | `filename`/`regex` | — | input resolution mode |

**C. `io.output_products[]`** (destination: E5):

| Field | Value / range |
|---|---|
| `id` | referenced by `workflow.outputs` |
| `path` | output URI (local FS / `s3::…`) |
| `type` | `filename` \| `folder` |
| `opening_mode` | `CREATE` \| `CREATE_OVERWRITE` \| `UPDATE` |
| `store_type` | `zarr` (mandated, `ICD-IF-OUT-01`) |
| `store_params` | e.g. `{compressor: zstd/clevel/shuffle}` or `null` |

- **Profile selection** is carried as a payload parameter resolved per run — `profile_id` /
  `profile_version` in the relevant unit `parameters` (and/or an `io` config reference), per
  `ICD-IF-PROF-02`. Exact placement is fixed in the SDD/profile loader and **[TBC@CDR]**.
- **CI/local variant (`ICD-IF-TRIG-03`):** `store_type: zarr`, local `path`s, no `dask_context`
  (or `cluster_type: local`), no `secret`/S3 — runnable on the shell runner.

#### <5.3.6> `ICD-IF-PROF` — Sensor-profile / configuration

**Provided service.** A versioned JSON object (source: E3) that specialises the generic chain;
validated on load (`ICD-IF-PROF-01`, REQ-DAT-03). JSON-Schema controlled; invalid/incomplete ⇒
reject with diagnostic. Top-level schema (field id = dotted path):

| Field (id) | Type | Description | Legality |
|---|---|---|---|
| `profile_id` | str | unique profile identifier | required, unique |
| `version` | str (SemVer) | profile version | required |
| `sensor_id` | str | instrument id (matches L0 `sensor_id`) | required |
| `modes[]` | list[str] | supported instrument modes | non-empty |
| `bands[]` | list[obj] | `{name, centre_wavelength_nm, srf_ref, esun, line_factor}` | ≥1; names unique |
| `focal_plane` | obj | `{n_detectors, samples_per_line, bit_depth}` | bit_depth>0 |
| `adf_bindings` | obj | default ADF ids per type (`radiometric,dark,flatfield,badpixel,spectral,viewing_model,dem,gcp,atmospheric`) | mandatory types bound |
| `radiometric` | obj | dark/NUC thresholds, saturation/no-data values | — |
| `enhancement` | obj | `{denoise:{method,params}, sharpen:{kernel}, enabled:bool}` | method ∈ allowed set |
| `coregistration` | obj | `{reference_band, matcher_params, thresholds}` | reference_band ∈ bands |
| `geometry` | obj | `{crs, grid, resolution, resampling, use_gcp}` (= `output.crs/grid/resolution`) | valid CRS |
| `pansharpen` | obj | `{enabled, method, pan_band}` | if enabled, pan_band set |
| `atmospheric` | obj | `{mode: retrieve\|ingest, source, classification_opts}` | mode ∈ enum |
| `output` | obj | `{crs, grid, resolution, chunking, store_target}` | chunking>0 |
| `optional_stages` | obj | per-stage enable flags (`enhancement,pansharpen,…`) default off where unvalidated (REQ-F-ENH-03) | bool |
| `breakpoints` | obj | default breakpoint levels | — |

- **Adaptation rule (REQ-IF-AD-01 / REQ-AD-01):** the processing core reads all sensor-specific
  data from this profile; adding a sensor = adding a profile (+ private ADFs), no core change
  (REQ-D-07). First instantiated profile = the project owner's sensor (REQ-AD-02).
- The JSON-Schema file is delivered as configuration (REQ-DEL-03); schema id/version tracked with
  the profile version.

#### <5.3.7> `ICD-IF-DIAG` & `ICD-IF-HMI` — status, diagnostics and CLI (MMI)

**Provided service (`ICD-IF-DIAG`).** Machine-readable run outcome surfaced to E4:

| Item id | Description | Representation | Range |
|---|---|---|---|
| exit status | process completion | int | `0` success, `≠0` failure (fail-stop, REQ-F-DEP-01) |
| structured diagnostics | errors/warnings | JSON log records | per logging conf |
| processing report | parameters, ADF/profile ids, per-product QA summary | JSON + human-readable | present on every run (REQ-O-02) |
| per-product QA | flags/metrics carried in `quality/` (table <5.3.3>E) | in product | — |

**Provided service (`ICD-IF-HMI`).** Non-interactive entry points (no GUI, REQ-HF-01):

| Item id | Description | Representation |
|---|---|---|
| CLI | `msi-processor <payload.{yaml,json}>` style invocation via the CPM runner | argv |
| Python API | `EORunner(...).run(payload)` / direct PU `run(...)` (table <5.3.4>A) | function call |
| inputs | triggering payload (<5.3.5>) + config/profile files | files/URIs |
| outputs | exit status + diagnostics (`ICD-IF-DIAG`) + Zarr product (`ICD-IF-OUT`) | files/streams |

---

## <6> Validation requirements

**Approach (Annex E <6>a).** Each uniquely identified interface requirement of <5.2> carries an
inline **Verify:** method (T/A/I/R). Validation reuses the V&V process of SRS <6> / RD-8: schema and
structure checks by **inspection/review** against this ICD and the PSFD; **automated tests**
(`pytest`, CPM `run_validating` / `validate(validation_mode)`) in public CI for everything not
needing private data, a container runtime, a Dask gateway or S3; and **local** tests on real
data/ADFs for the field-level content of the private interfaces. Interfaces needing those services
or private data run non-blocking in CI and are validated locally (REQ-PORT-03). The detailed
interface→test-case trace is maintained in RD-9 at CDR.

**Validation matrix (Annex E <6>b — requirement → method → means).**

| Interface req. | Method | Means / milestone |
|---|---|---|
| ICD-IF-L0-01 | I, T | Decode a sample `L0c` (local); assert `L1A` DataTree vs <5.3.1>A (PDR→CDR) |
| ICD-IF-L0-02 | I, T | Inspect selection metadata; resolve profile/ADF from a sample `L0c` |
| ICD-IF-L0-03 | A, I | Static analysis / inspection: no write path to L0 |
| ICD-IF-ADF-01 | I, T | Load gain/offset, dark, flat-field as `AuxiliaryDataFile`; assert content vs <5.3.2>A (local) |
| ICD-IF-ADF-02 | I, T | Inspect id/version/validity attrs; select valid ADF for a given `L0c` |
| ICD-IF-ADF-03 | I, A | Repo/CI scan: no ADF content committed; runtime-URI resolution |
| ICD-IF-ADF-04 | A, I | Static analysis / inspection: ADFs opened read-only |
| ICD-IF-OUT-01 | T, I | Write `EOProduct` via `EOZarrStore`; assert DataTree vs <5.3.3>A |
| ICD-IF-OUT-02 | T | Chunked partial read; write POSIX (CI) + S3 (when available) |
| ICD-IF-OUT-03 | I, T | Inspect provenance/STAC attrs vs <5.3.3>D; assert no private coefficients |
| ICD-IF-SW-01 | R, I | Review PU class attrs + computing-model JSON vs <5.3.4>A |
| ICD-IF-SW-02 | R, T | Round-trip `EOProduct`/`EOZarrStore`; review no I/O outside CPM |
| ICD-IF-SW-03 | I | Inspect pinned `eopf == 2.8.1` + build image |
| ICD-IF-SW-04 | T | Unit-test pure cores without CPM runtime (<5.3.4>C) |
| ICD-IF-SW-05 | I | Inspection: no hardware interface (N/A closure) |
| ICD-IF-TRIG-01 | I, T | Inspect payload vs <5.3.5>; trigger a run from a sample payload |
| ICD-IF-TRIG-02 | T | Trigger with local + remote (when available) URIs |
| ICD-IF-TRIG-03 | T | Trigger + verify on the CI shell runner (local-FS variant) |
| ICD-IF-TRIG-04 | T | Sub-chain run via `active`/`breakpoints`; assert start/stop at level |
| ICD-IF-PROF-01 | T, I | Load valid + invalid profile vs JSON-Schema; reject-with-diagnostic test |
| ICD-IF-PROF-02 | I, T | Inspect id/version; select profile per run via payload |
| ICD-IF-DIAG-01 | T | Assert exit status + diagnostics/QA on success and forced failure |
| ICD-IF-HMI-01 | I, T | Invoke via CLI/API; confirm no GUI dependency |

**Requirements not validated against the baseline.** `ICD-IF-SW-05` (no hardware interface) is an
N/A closure verified by inspection. Field-level items flagged **[TBC@CDR]** (sensor-private
encodings, exact 2.8.1 surface, chunk/dtype defaults) are confirmed at CDR finalisation, not at PDR.

---

## <7> Traceability

Per Annex E <7>a the forward and backward interface traceability is reported below; the
authoritative, tool-maintained matrix (incl. trace to design and test cases) is RD-9 (Annex E <7>b
— DJF reference).

### <7.1> Forward — upper-level interface req. (IRD `REQ-IF-*`) → ICD interfaces

| IRD `REQ-IF-*` | Realised by |
|---|---|
| REQ-IF-CAP-01 | ICD-IF-TRIG-01/04, ICD-IF-SW-01 |
| REQ-IF-CAP-03 | ICD-IF-OUT-03 |
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
> (`compliance/traceability/`); this satisfies Annex E <7>b.

---

*End of ICD. Authored per ECSS-E-ST-40C Rev.1 Annex E. Preliminary at PDR; field-level items flagged
[TBC@CDR] are finalised at CDR. The EOPF PSFD is the normative product-structure reference; CPM
signatures are bound to `eopf == 2.8.1`. Upstream interface requirements are in the IRD (RD-3) and
SRS (RD-4); the maintained traceability matrix is RD-9.*
