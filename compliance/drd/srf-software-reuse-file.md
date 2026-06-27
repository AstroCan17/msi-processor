# Software Reuse File (SRF)

| Field | Value |
|---|---|
| **Document** | SRF — Software Reuse File |
| **DRD ref** | ECSS-E-ST-40C Rev.1, Annex N (SRF DRD); ECSS-Q-ST-80C Rev.2 §6.2.7 |
| **Container** | Design Justification File (DJF) — `compliance/drd/` (source), published subset in `docs/srf.md` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | **CDR** |
| **Status** | Draft for CDR |

> **Purpose of this issue.** `msi-processor` is explicitly an **integration and ECSS-productisation**
> effort: the processing *mathematics* already exists as prior work (RD-9) and the runtime *platform* is
> the EOPF CPM (`eopf == 2.8.1`), over a standard scientific-Python stack. This SRF is the Annex N
> constituent of the DJF that records the analysis behind every reuse decision — what is reused, on what
> licence, at what quality level against the Category C requirements baseline, how its correctness is
> (re)verified, and which corrective actions turn research-grade heritage into a verifiable CPM product.
> It is authored at CDR, **before** implementation (SDP RD-1, WP-5) starts, so the reuse strategy is
> baselined together with the detailed design (SDD, RD-2). Sensor-private content (calibration
> coefficients, the NDA-bound L0 bit-codec body) is **not** reproduced here (data policy, SRS RD-4 <5.8>).

---

## <1> Introduction

**Purpose.** This SRF documents the analysis performed on existing software intended to be reused by
`msi-processor`, and records the decision, level and conditions of that reuse, per Annex N <1>a.

**Objective.** Per Annex N N.1.2 the SRF (a) documents all information used to decide *whether* and *how*
to reuse existing software, (b) plans the specific actions ensuring the reused software meets the project
requirements (the corrective actions of <8>), and (c) is the authoritative licence/compatibility record
for the public-code, private-data constraint of this project.

**Content.** Clause <2> lists applicable/reference documents; <3> adds SRF-specific terms. Clause <4>
**presents the software intended for reuse** (the prior-work algorithm heritage, the EOPF CPM, and the
third-party OSS stack) with the Annex N <4>b technical/management fields. Clause <5> assesses
**compatibility with the project requirements** — which requirements are met by reuse, and the
availability/quality status of each reused item against Category C. Clause <6> gives the **reuse analysis
conclusion** (reuse/not-reuse decision, level, method) per item. Clause <7> is the detailed per-module
evaluation (appendix). Clause <8> lists the **corrective actions** that re-engineer the heritage to
Category-C quality. Clause <9> records the **configuration status** of every reused baseline.

**Reason for preparation.** Three distinct bodies of existing software are candidates for reuse and each
needs a different treatment, which only an explicit Annex N analysis makes defensible: (i) the owner's
prior-work pushbroom-preprocessing pipeline (RD-9) — research-grade Python carrying the *mathematical*
heritage but not the quality, structure or licence hygiene required at Category C; (ii) the EOPF CPM —
the mandated runtime platform, reused as-is; (iii) the scientific-Python numerical stack — mature OSS
libraries providing the kernels (FFT, wavelets, feature matching, resampling). This SRF separates
**algorithmic reuse** (heritage, re-engineered) from **as-is reuse** (CPM + OSS) and from **new
development** (the atmospheric stage, which has no heritage).

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software | ECSS-E-ST-40C Rev.1 (30 April 2025), Annex N |
| AD-2 | ECSS Space product assurance — Software product assurance | ECSS-Q-ST-80C Rev.2, §6.2.7 |
| AD-3 | ECSS-E-ST-40C Rev.1 Annex R — Tailoring based on software criticality (Category C) | AD-1 |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software Design Document (SDD, detailed/CDR) — `C-*` | `compliance/drd/sdd-software-design.md` |
| RD-3 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — `DPM-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V plan (SVerP/SValP/SUITP merged) | `compliance/drd/vv-plan.md` |
| RD-9 | **Prior work** — multispectral pushbroom preprocessing pipeline (`02_scripts/`) — the algorithmic/mathematical heritage reused by this project | `previous-work/multispectral_demo_satellite_preprocessing_pipeline/02_scripts/` (`level_0.py`, `level_1.py`, `band_coreg.py`, `georeferencing_v1.py`, `pansharp.py`, `metrics_ips.py`, `main_ips_v6.py`) |
| RD-10 | `msi-processor` Interface Control Document (ICD) — `ICD-IF-*` | `compliance/drd/icd-interface-control.md` |
| RD-11 | `msi-processor` Risk register — `RSK-*` | `compliance/drd/risk-register.md` |
| RD-12 | EOPF CPM documentation (`EOProduct`, `EOProcessingUnit`, `EOZarrStore`, triggering/computing model) | EOPF CPM (`eopf == 2.8.1`) |
| RD-13 | `msi-processor` build/dependency manifest + licence | `pyproject.toml`, `LICENSE` (Apache-2.0, © 2026 ESA) |
| RD-14 | Cloud-native data conventions | Zarr v2/v3, CF metadata, STAC, GeoZarr |

---

## <3> Terms, definitions and abbreviated terms

The SSS <3>, SRS <3>, SDD <3>, DPM <3> and ATBD <3> glossaries apply in full. SRF-specific additions
(Annex N <3>):

| Term / abbr. | Definition |
|---|---|
| Heritage (reuse category) | Existing project-owned software reused for its **algorithm/mathematics**, re-engineered (not copied verbatim) into the new design |
| OSS (reuse category) | Third-party open-source library reused **as-is** by dependency, unmodified |
| COTS/platform (reuse category) | The framework runtime (EOPF CPM) reused **as-is** as the execution platform |
| As-is reuse | Reuse without modification of the reused source/binary (CPM, OSS) |
| Algorithmic reuse | Reuse of the *equations/method* of an item while its *code* is rewritten (heritage → pure Core) |
| Core | The pure, CPM-free algorithmic function set of a stage (SDD <3>); the unit into which heritage is re-engineered |
| PU / Wrapper | EOPF CPM `EOProcessingUnit` and its thin adapter (SDD <3>) |
| Level of reuse | Estimated fraction of an item carried into the product, split into **algorithm-level** and **code-level** reuse (Annex N <6>b.2) |
| RB | Requirements baseline (the `REQ-*` set of RD-4, traced from `SYS-*`/`REQ-IF-*`) |
| `SRF-RU-*` | Reuse-item identifier defined by this SRF for traceability |
| `[TBC@impl]` | A value (e.g. an OSS pinned version) fixed in the lockfile when implementation (WP-5) starts |
| DJF | Design Justification File (ECSS-E-ST-40C) — the container of this SRF |

**Reuse-item register (IDs defined here).**

| Id | Reuse item | Category |
|---|---|---|
| SRF-RU-HER | Prior-work pushbroom-preprocessing pipeline (RD-9) | heritage |
| ↳ SRF-RU-HER-L0 | `level_0.py` → `l0_decode` Core | heritage |
| ↳ SRF-RU-HER-RAD | `level_1.py::NUC` → `radiometric` Core | heritage |
| ↳ SRF-RU-HER-ENH | `level_1.py::sharpening`,`Denoiser` → `enhancement` Core | heritage |
| ↳ SRF-RU-HER-TOA | `level_1.py::TOA` → `toa` Core | heritage |
| ↳ SRF-RU-HER-COR | `band_coreg.py::BandRegister` → `coregistration` Core | heritage |
| ↳ SRF-RU-HER-GEO | `georeferencing_v1.py` → `georeference` Core | heritage |
| ↳ SRF-RU-HER-PAN | `pansharp.py::PanSharpening` → `pansharpen` Core | heritage |
| ↳ SRF-RU-HER-QA | `metrics_ips.py::calculateMetrics` → `qa` Core | heritage |
| SRF-RU-CPM | EOPF Common Python Modules (CPM), `eopf == 2.8.1` | COTS/platform |
| SRF-RU-OSS-* | Third-party OSS stack (numpy, scipy, scikit-image, scikit-learn, xarray, zarr, dask, pandas, rasterio, GDAL, OpenCV, PyWavelets) | OSS |

---

## <4> Presentation of the software intended to be reused

### <4.1> Overview and technical/management information available (Annex N <4>a)

Three reuse bodies, each with a different category and treatment:

| # | Reuse body | Id | Category | Treatment | Realises |
|---|---|---|---|---|---|
| 1 | Prior-work pipeline (RD-9) | SRF-RU-HER | heritage | **algorithm reused, code re-engineered** into pure Cores | the functional chain `REQ-F-{L0,RAD,ENH,TOA,COR,GEO,PAN,QA}` via `DPM-M-*` / `ALG-*` |
| 2 | EOPF CPM (`eopf == 2.8.1`) | SRF-RU-CPM | COTS/platform | **reused as-is** (mandated runtime) | product/IO/orchestration `REQ-F-PRD`, `REQ-F-ORC`, `REQ-D-06/09`, `REQ-I-*`, `REQ-PORT-*` |
| 3 | Scientific-Python OSS stack | SRF-RU-OSS-* | OSS | **reused as-is** (libraries, by dependency) | numerical kernels inside the Cores (FFT, wavelet, feature match, resampling, raster I/O) |

The **atmospheric** stage (`C-PU-ATM`, `REQ-F-ATM-*`, `DPM-M-ATM`, `ALG-ATM-*`) is **new development**
with no heritage and is therefore *not* a reuse item; it is listed here only to scope the reuse boundary
(SDD <5.3>, <4.7>7). The information available per body:

- **SRF-RU-HER:** full source (the seven `02_scripts/` modules, RD-9), an informal `README.txt`, and the
  derived ECSS algorithm documentation authored for this project (DPM RD-6, ATBD RD-7) that captures the
  mathematics rigorously. No prior requirements/design/test documentation exists (assessed in <5>).
- **SRF-RU-CPM:** the published EOPF CPM API documentation (RD-12), the pinned distribution and its CI,
  and the SDE `cpm-build-environment` image that fixes the qualified version.
- **SRF-RU-OSS-*:** upstream project documentation, release notes, public test suites and `LICENSE`/
  `NOTICE` files; versions are resolved transitively through `eopf == 2.8.1` and frozen in the project
  lockfile at implementation (`[TBC@impl]`).

### <4.2> SRF-RU-HER — Prior-work algorithm heritage (Annex N <4>b)

| Annex N <4>b field | Value |
|---|---|
| 1. Name & main features | *Multispectral pushbroom preprocessing pipeline* (RD-9). A research/demo `L0→L2`-style pipeline for a high-resolution pushbroom MSI: L0 loss handling, dark/NUC/PRNU + bad-pixel radiometric correction, denoise/sharpen, DN→TOA radiance/reflectance, inter-band co-registration, georeferencing/orthorectification, pansharpening, and QA metrics. Main value = the **mathematical method** per stage. |
| 2. Developer identification | The project owner (GitLab `AstroCan17`; ESA-affiliated authorship), as prior personal/academic work. Single author; same developer as `msi-processor`. |
| 3. Considered version & components | The frozen `02_scripts/` snapshot (RD-9). Components & size — `level_0.py` (62 SLOC), `level_1.py` (860), `band_coreg.py` (223), `georeferencing_v1.py` (691), `pansharp.py` (137), `metrics_ips.py` (183), `main_ips_v6.py` (402, orchestration — **not reused**). Reused total ≈ **2,156 SLOC** of algorithmic code. |
| 4. Licensing conditions | Owner-held, **not previously released under any public licence**; reused as the project's own IP. The *re-engineered output* (the Cores) ships under the project licence **Apache-2.0** (RD-13). No third-party copyright in the reused algorithmic code (the imported libraries are handled separately, <4.4>). |
| 5. Industrial property / exportability | Owner holds the rights. **One exportability constraint:** the `level_0.py::Decoder.decode` body is **NDA/sensor-private** (it is a stub `return None` in RD-9 by design) and the calibration data it ultimately consumes is private — the public re-engineered Core keeps the bit-codec body `[impl]`/private (SDD <5.4.2>; SRS <5.8>; data policy: *code public, raw + calibration private*). |
| 6. Implementation language | Python 3 (research-grade; CPython). |
| 7. Development & execution environment | Desktop Python with **interactive** elements (`tkinter` file dialogs), OpenCV, GDAL/rasterio, `matplotlib` plots, and **external services** (Google Earth Engine `ee`, `pyorbital`/`skyfield` TLE/ephemeris, `requests`/`urllib` downloads). None of these execution assumptions is carried into `msi-processor` (replaced — see <4.4>, <8>). |
| 8. Warranty / maintenance / installation / training | **None.** No support contract, no maintenance commitment, no installer, no training material; `README.txt` explicitly lists unfinished items ("Unit tests, on-orbit MTF estimation, PSF sharpening, different pansharpening methods, and atmospheric correction will be added soon"). |
| 9. Commercial software needed to execute | The original execution path used **Google Earth Engine** (account-gated cloud service) for reference imagery and TLE sources for geometry — **commercial/external dependencies that are removed**; the re-engineered Cores need no commercial software (geometry comes from `L0c` telemetry + private ADF `DPM-ADF-GEOM`). |
| 10. Size | ≈ 2,558 SLOC across 7 files (≈ 2,156 SLOC reused for algorithm extraction; no compiled/executable artefact — pure Python). |

**Component → design mapping (the algorithmic heritage, per stage).** Each module is re-engineered into a
**pure Core** behind a CPM Wrapper (SDD <5.4>); the equations are captured in the ATBD (`ALG-*`) and DPM
(`DPM-M-*`).

| Id | Heritage source (RD-9) | Re-engineered into (SDD) | DPM / ATBD | Requirements (RD-4) | What is reused vs dropped |
|---|---|---|---|---|---|
| SRF-RU-HER-L0 | `level_0.py` (`Decoder.decode` [NDA stub], `lost_package`) | `C-PU-L0` `l0_decode.core` | DPM-M-L0 / ALG-L0-DEC, ALG-L0-LOSS | REQ-F-L0-01..05 | Reuse: zero-line loss-detection/truncation logic. Drop: `tkinter` save dialog, `cv2.imwrite`. Codec body stays NDA `[impl]`. |
| SRF-RU-HER-RAD | `level_1.py::NUC` (`compute_nuc`, `apply_nuc_and_bpr`, `dark_noise_removal`, `analyse_dark_current`) | `C-PU-RAD` `radiometric.core` | DPM-M-RAD / ALG-RAD-DARK,NUC,BPR,SAT | REQ-F-RAD-01..05 | Reuse: dark/DSNU, NUC/PRNU gain-offset, bad-pixel replacement, saturation logic. Drop: file dialogs, generator/disk plumbing, hardcoded band names; **calibration constants → private ADF**. |
| SRF-RU-HER-ENH | `level_1.py::sharpening` (`deconvolution_kernel`), `Denoiser` (`pca`, `moving_avarage_filter`, `wavelet_denoising_cdk`, `gaussian_filter_ips`, `get_filtered_butterworth`, `butterworth_LP_ips`) | `C-PU-ENH` `enhancement.core` *(mandatory)* | DPM-M-ENH / ALG-ENH-DECONV,PCA,MA,WAVE,GAUSS,BWLP,FFTDARK | REQ-F-ENH-01..03 | Reuse: PSF-deconvolution (MTF compensation) + denoise/sharpen kernels (radiometry-preserving). Drop: interactive I/O, `matplotlib`. MTFC mandatory/always-run; denoise method profile-configurable (REQ-F-ENH-03). |
| SRF-RU-HER-TOA | `level_1.py::TOA` (`dn_to_radiance`, `toa_rad_to_ref`, `get_ESUN`, `get_sun_el_esdist`) | `C-PU-TOA` `toa.core` | DPM-M-TOA / ALG-TOA-RAD, ALG-TOA-REF | REQ-F-TOA-01..03 | Reuse: DN→radiance and radiance→reflectance with solar geometry/ESUN. Drop: `pyorbital` TLE fetch for Sun-Earth distance → **telemetry/ephemeris from `L0c` + ADF** (removes GPL dep). |
| SRF-RU-HER-COR | `band_coreg.py::BandRegister` (`shifting_sift`, CLAHE, homography warp) | `C-PU-COR` `coregistration.core` | DPM-M-COR / ALG-COR-FEAT, ALG-COR-HOM, ALG-COR-WARP | REQ-F-COR-01..03 | Reuse: SIFT feature match → homography → warp to reference band; match-count acceptance gate. Drop: `tkinter`, `matplotlib`, hardcoded `b6`-as-PAN exclusion → profile-driven band roles. |
| SRF-RU-HER-GEO | `georeferencing_v1.py` (`getSatelliteInfo`, `geoReferencing`, `reprojection`) | `C-PU-GEO` `georeference.core` | DPM-M-GEO / ALG-GEO-ORBIT,GSD,GCP,ORTHO,RESAMP | REQ-F-GEO-01..04 | Reuse: viewing-model geolocation, GCP refinement, DEM orthorectification, resampling/reprojection. **Drop: `referenceDownload` (Google Earth Engine) + `pyorbital`/`skyfield` TLE** → geometry from `L0c` telemetry + private ADFs (`DPM-ADF-GEOM`/DEM). The rigorous collinearity kernel is `[impl]`. |
| SRF-RU-HER-PAN | `pansharp.py::PanSharpening` (`pan_sharpen`) | `C-PU-PAN` `pansharpen.core` *(opt, default-off)* | DPM-M-PAN / ALG-PAN-ALIGN, ALG-PAN-FUSE | REQ-F-PAN-01/02 | Reuse: MS↔PAN alignment + fusion. Drop: `PIL`/`cv2` file I/O, interactive paths. |
| SRF-RU-HER-QA | `metrics_ips.py::calculateMetrics` (`calculate_SNR/RMSE/PSNR`, `mse`, `calculate_variance`, `run_validation`) | `C-PU-QA` `qa.core` (cross-cutting) | DPM-M-QA / ALG-QA-SNR,RMSE,PSNR,MSE,VAR | REQ-F-QA-01/02 | Reuse: the metric formulas. Drop: generator/file plumbing; reformulated as pure reductions over `BandStack`. |

> **`main_ips_v6.py` is explicitly NOT reused** — its orchestration (manual stage sequencing,
> `memory_profiler`, file dialogs) is fully superseded by the CPM triggering/computing-model and the
> chain runner `C-COM-ORC` (SDD <4.2>, <5.4.11>). Decision recorded in <6>.

### <4.3> SRF-RU-CPM — EOPF CPM (`eopf == 2.8.1`) (Annex N <4>b)

| Annex N <4>b field | Value |
|---|---|
| 1. Name & main features | **EOPF Common Python Modules (CPM)** — the Copernicus EOPF processing framework: `EOProduct`/`EOGroup`/`EOVariable` data model, `EOProcessingUnit` execution contract, `EOZarrStore` cloud-native I/O, URI/store abstraction, triggering payload + per-PU computing model, optional Dask distribution. The mandated runtime platform (SDD <4.1>). |
| 2. Developer identification | ESA / EOPF programme and its industrial consortium (CS Group and partners), maintained under the EOPF project. |
| 3. Considered version & components | **2.8.1** (pinned in `pyproject.toml`, RD-13), the version provided by the SDE `cpm-build-environment` image (same pin as the sibling `eo-data-embedding` project on this SDE). Components used: `eopf.computing.EOProcessingUnit`, `eopf.product` (`EOProduct`/`EOGroup`/`EOVariable`), `EOZarrStore` + store factory, triggering/`processing_model()`, Dask wiring. |
| 4. Licensing conditions | **Apache-2.0** (permissive; patent grant + NOTICE retention). Compatible with the project Apache-2.0 (RD-13); see <4.5>. |
| 5. Industrial property / exportability | Open-source, ESA-sponsored; no export constraint. Optional extras (`eopf[cluster-plugin]`, `eopf[tests]`, …) carry the same family licence (confirm in <8>). |
| 6. Implementation language | Python (3.11 target). |
| 7. Development & execution environment | Python 3.11 on POSIX x86-64 Linux; the EOPF SDE / `cpm-build-environment` container (SDP RD-1). No GPU. |
| 8. Warranty / maintenance / installation / training | Community/ESA-maintained OSS — **no formal warranty**; installation by `pip`/extras from `pyproject.toml`; EOPF training material/docs (RD-12). Version churn risk mitigated by a single pinned dependency + a V&V-gated bump procedure (REQ-M-03), tracked in the risk register (RD-11). |
| 9. Commercial software needed to execute | None. |
| 10. Size | Large external framework (full size n/a — not vendored; obtained as a pinned dependency). |

### <4.4> SRF-RU-OSS-* — Third-party open-source stack (Annex N <4>b)

These provide the numerical kernels called *inside* the pure Cores and the platform services in
`common` (SDD <5.4.11>). They are reused **as-is** (unmodified, by dependency), resolved transitively
through `eopf == 2.8.1` and frozen at implementation (`[TBC@impl]` versions in the lockfile). Annex N
<4>b fields, tabulated (developer = the named OSS community; warranty = none/OSS; commercial software
needed = none; language = Python with C/C++ extensions; environment = Python 3.11 / POSIX x86-64):

| Id (SRF-RU-OSS-) | Item | Used by (Core / service) | Licence (well-known) | Reuse role |
|---|---|---|---|---|
| NUMPY | NumPy | all Cores; `_types` | BSD-3-Clause | array backbone, `float32` working type (REQ-D-05) |
| SCIPY | SciPy | ENH, COR, GEO | BSD-3-Clause | signal/filters, interpolation, linear algebra |
| SKIMAGE | scikit-image | ENH (`restoration`, `filters`), COR | BSD-3-Clause | wavelet/Butterworth denoise, deconvolution, registration helpers |
| SKLEARN | scikit-learn | ENH (`decomposition.PCA`); ATM scene-class candidate | BSD-3-Clause | PCA denoise; classifier option (ATM is new dev) |
| XARRAY | xarray | `C-COM-PRODUCT`, chunking | Apache-2.0 | labelled n-D arrays behind `EOProduct` |
| ZARR | zarr (zarr-python) | `C-COM-PRODUCT`/`IO` | MIT | cloud-native chunked store (REQ-F-PRD-01, REQ-D-09) |
| DASK | Dask | `C-COM-CHUNK`, distributed mode | BSD-3-Clause | block/tile task graph, optional distribution (REQ-F-ORC-02, REQ-R-04) |
| PANDAS | pandas | metadata/tabular handling | BSD-3-Clause | tabular auxiliary handling/provenance (where needed) |
| RASTERIO | rasterio | GEO | BSD-3-Clause | geospatial raster read/reproject helpers |
| GDAL | GDAL/OGR/OSR | GEO | MIT/X11 (core) | reprojection, CRS, DEM/ortho geotransforms |
| OPENCV | OpenCV (`opencv-python-headless`) | COR, ENH, PAN | Apache-2.0 (library; PyPI wrapper MIT) | SIFT/FLANN feature match, CLAHE, homography, warp/resample |
| PYWT | PyWavelets (`pywt`) | ENH | MIT | wavelet denoising (ALG-ENH-WAVE) |

> **Deliberately NOT reused (dropped from the heritage execution stack)** — recorded so the reuse
> boundary is explicit and the licence audit is closed: `pyorbital` (**GPL-3.0 — copyleft, incompatible
> with public Apache-2.0 distribution**), `skyfield` (MIT, but external ephemeris), `earthengine-api`/`ee`
> (account-gated cloud service), `tkinter` (interactive GUI — batch processor is non-interactive,
> REQ-O-04), `matplotlib`/`memory_profiler` (dev/debug only), `requests`/`urllib`/`Pillow` (ad-hoc
> download/IO — replaced by CPM URI I/O). Their function is supplied instead by `L0c` telemetry + private
> ADFs and the CPM/OSS stack above (see <8>). Removing `pyorbital` in particular eliminates the only
> copyleft dependency.

### <4.5> Licence compatibility (project code is public)

Project licence: **Apache-2.0** (`LICENSE`, © 2026 ESA; RD-13). All reused **runtime** software is
permissive and Apache-2.0-compatible:

- **EOPF CPM** — Apache-2.0 (identical to the project licence; patent grant + NOTICE retention).
- **OSS stack** — BSD-3-Clause (NumPy, SciPy, scikit-image, scikit-learn, Dask, pandas, rasterio),
  Apache-2.0 (xarray, OpenCV library), MIT (zarr, PyWavelets), MIT/X11 (GDAL core). All are non-copyleft
  and freely redistributable under Apache-2.0; Apache-2.0/MIT-licensed items impose only
  attribution/NOTICE retention.
- **Heritage (SRF-RU-HER)** — owner IP; the re-engineered output ships Apache-2.0. No third-party
  copyright is inherited because the imported research-time libraries are *not* vendored (only the
  algorithms are reused).
- **No strong copyleft (GPL/LGPL/AGPL) in the runtime set.** The one GPL dependency of the heritage
  (`pyorbital`) is **dropped** (<4.4>), so no reciprocal-licence obligation propagates to the public code.

Two items for the release-time licence audit (<8>, RSK in RD-11): (i) the `opencv-python*` wheels may
bundle **FFmpeg (LGPL-2.1)** and other codecs — use `opencv-python-headless` and confirm the bundled-codec
licences, or build without them; (ii) **GDAL** can be built with optional GPL/LGPL drivers — keep to the
permissive/core driver set. Each library's `LICENSE`/`NOTICE` is confirmed against its pinned version
before release (marked *confirm-before-release*).

---

## <5> Compatibility of existing software with project requirements

### <5.1> Project requirements (RB) implemented through reuse (Annex N <5>a)

| RB area (RD-4) | Implemented through | Reuse body |
|---|---|---|
| Functional algorithm chain — REQ-F-L0/RAD/ENH/TOA/COR/GEO/PAN/QA (via `DPM-M-*`, `ALG-*`) | **algorithm reuse + re-engineering** | SRF-RU-HER (+ OSS kernels) |
| Numerical kernels (FFT/wavelet/PCA, SIFT/FLANN/homography, reproject/resample/DEM) | **as-is OSS** | SRF-RU-OSS-* |
| Product/IO/format — REQ-F-PRD-01/02, REQ-D-06, REQ-D-09, REQ-DAT-01 | **as-is platform** | SRF-RU-CPM (+ zarr/xarray) |
| Orchestration/triggering — REQ-F-ORC-01/02, REQ-F-DEP-01, REQ-I-05 | **as-is platform** | SRF-RU-CPM (+ Dask) |
| Portability/IO transparency — REQ-PORT-02/03, REQ-I-06 | **as-is platform** | SRF-RU-CPM |
| Atmospheric correction — REQ-F-ATM-01..04 | **new development** (no reuse) | — (`C-PU-ATM`) |
| Sensor-agnostic adaptation — REQ-AD-01..04 | **new development** (profile schema + data) | — (`C-SENSORS`) |

So the **functional core and the platform are reuse-dominated**; the new development is the atmospheric
stage, the sensor-profile layer, the thin CPM Wrappers, and the `common` services that bind heritage
algorithms to the CPM data model.

### <5.2> Availability and quality status of each reused item (Annex N <5>b)

Status of the Annex N <5>b.1–13 information items (Y = available/adequate, P = partial, N = absent):

| Annex N <5>b item | SRF-RU-HER (heritage) | SRF-RU-CPM (EOPF) | SRF-RU-OSS-* |
|---|---|---|---|
| 1. SW requirements documentation | **N** — no SRS existed; now supplied by this project (RD-4) | Y — EOPF docs (RD-12) | Y — upstream docs |
| 2. Architectural & detailed design doc | **N** — none; now supplied by SDD (RD-2) | Y — EOPF API/architecture | Y — upstream design docs |
| 3. Forward/backward traceability to system req. | **N** — none; established here (RD-2 <6>, traceability matrix) | n/a (external product) | n/a |
| 4. SW requirements, design **and code** | P — **code only** (RD-9), no req/design | Y | Y |
| 5. Unit tests doc & coverage | **N** — README: "unit tests … will be added"; none present | Y — EOPF CI test suite | Y — large public test suites |
| 6. Integration tests doc & coverage | **N** | Y — EOPF CI | Y |
| 7. Validation doc & coverage | P — informal/visual demo only | Y | Y |
| 8. Verification reports | **N** | P — EOPF release notes/CI | P — release notes |
| 9. Performance (memory / PU load) | P — ad-hoc (`memory_profiler` in `main_ips_v6`) | Y — documented, Dask-scalable | Y — well-characterised |
| 10. Operational performance | P — demo-grade | Y — operational in EOPF | Y — production-grade |
| 11. Residual non-conformance / waivers | **N** — not tracked | P — via EOPF issues | P — via upstream trackers/CVEs |
| 12. User operational documentation | P — minimal `README.txt` | Y — EOPF user docs | Y — upstream docs |
| 13. Code quality (standards, metrics) | **N** — research-grade: interactive GUI, no typing, hardcoded constants, no PEP-8/lint gate | Y — PEP-8, typed, linted | Y — mature, CI-enforced |

### <5.3> Quality level vs project requirements, by criticality (Annex N <5>c)

Category C tailoring (AD-3): unit + integration verification, deterministic reproducibility, coding-
standard conformance (REQ-Q-01), and requirements/design traceability are required; independent IV&V is
not.

- **SRF-RU-HER — quality level: LOW vs Category C.** Adequate as an *algorithmic reference* (the
  mathematics is sound and now rigorously captured in DPM/ATBD), but **inadequate for as-is reuse**: no
  requirements/design/test documentation, no traceability, no coding-standard conformance, interactive
  and external-service execution assumptions, and instrument constants embedded in code (violating
  REQ-AD-01/REQ-D-04/REQ-S-05). ⇒ **Reuse the algorithms, not the code**: re-engineer into pure Cores and
  re-verify under the project V&V (RD-8). Corrective actions in <8>.
- **SRF-RU-CPM — quality level: HIGH, acceptable for as-is reuse.** The mandated platform, maturely
  documented, tested and operated; pinned at 2.8.1. The project verifies *its use* of the CPM (Wrapper
  contracts, computing-model JSON, Zarr round-trips) at integration level (RD-8); it does not re-verify
  CPM internals. Version-bump risk is gated (REQ-M-03, RD-11).
- **SRF-RU-OSS-* — quality level: HIGH, acceptable for as-is reuse.** Mature, widely deployed,
  extensively tested, semantically versioned. The project verifies *its use* (kernel call correctness vs
  the ATBD via unit tests with reference vectors, RD-8), pins versions in the lockfile, and confirms
  licences before release. It does not re-verify library internals — appropriate at Category C for
  well-established OSS used through stable public APIs.

---

## <6> Software reuse analysis conclusion

### <6.1> Results of the reuse analysis (Annex N <6>a)

The analysis confirms the project's founding premise: `msi-processor` is built by **reuse, not
reinvention** (SDP RD-1 §4) — (i) the prior-work **algorithms are reused** and re-engineered into
CPM-free Cores; (ii) the **EOPF CPM is reused as-is** as the platform; (iii) the **OSS numerical stack is
reused as-is** as the kernels. The **only new algorithmic development** is the atmospheric stage
(`C-PU-ATM`), plus the integration glue (Wrappers, `common` services) and the sensor-profile layer
(`C-SENSORS`). All reuse is **licence-compatible** with the public Apache-2.0 distribution after dropping
the single GPL dependency (`pyorbital`).

### <6.2> Per-item conclusion: decision, level, method (Annex N <6>b)

| Reuse item | Decision (<6>b.1) | Estimated level of reuse (<6>b.2) | Assumptions & method (<6>b.3) |
|---|---|---|---|
| **SRF-RU-HER** (heritage) | **Reuse — algorithmically; re-engineer the code** | **Algorithm-level ≈ 70–90 %/stage** (math carried into ATBD/DPM); **code-level ≈ 0–15 %** (full rewrite to pure Cores) | Method: per-stage mapping table (<4.2>) + expert judgement by the single author; assumes the math in DPM/ATBD is the authoritative spec and that ECSS quality is reached only by rewriting (<8>). |
| ↳ HER-L0 | Reuse algorithm (loss); codec stays NDA `[impl]` | algo ~80 % (loss rule) / code ~10 % | NDA codec excluded from public metric |
| ↳ HER-RAD | Reuse algorithm | algo ~90 % / code ~10 % | constants externalised to ADF |
| ↳ HER-ENH | Reuse algorithm (mandatory stage) | algo ~85 % / code ~10 % | MTFC always-run; denoise method profile-configurable; kernels validated per profile (REQ-F-ENH-03) |
| ↳ HER-TOA | Reuse algorithm | algo ~85 % / code ~10 % | solar geometry from telemetry/ADF (no `pyorbital`) |
| ↳ HER-COR | Reuse algorithm | algo ~80 % / code ~15 % | band roles from profile, not hardcoded |
| ↳ HER-GEO | Reuse algorithm; rigorous kernel `[impl]` | algo ~70 % / code ~10 % | GEE/TLE acquisition dropped; geometry from ADF |
| ↳ HER-PAN | Reuse algorithm (opt, default-off) | algo ~85 % / code ~10 % | — |
| ↳ HER-QA | Reuse algorithm | algo ~90 % / code ~15 % | reformulated as pure reductions |
| **SRF-RU-CPM** (EOPF CPM) | **Reuse as-is** (mandated platform) | **100 %** (unmodified) | Pinned `eopf == 2.8.1`; verify *use* not internals; bump gated (REQ-M-03). |
| **SRF-RU-OSS-*** | **Reuse as-is** (libraries) | **100 %** (unmodified) | Kernels not re-implemented; versions pinned in lockfile; licences confirmed before release. |
| `main_ips_v6.py` | **Do NOT reuse** | 0 % | Superseded by CPM triggering + `C-COM-ORC`. |
| `pyorbital` / `skyfield` / `ee` / `tkinter` / `matplotlib` | **Do NOT reuse** | 0 % | Copyleft / external-service / interactive — incompatible with public, non-interactive, ADF-driven design. |
| Atmospheric (`C-PU-ATM`) | **New development** (not a reuse item) | 0 % reuse | No heritage; designed interface-first vs DPM/ATBD (SDD <4.7>7). |

---

## <7> Detailed results of evaluation (appendix)

Per-module evaluation summary (Annex N <7>a; expands <4.2>/<5.2>). For each heritage module: keep / drop
/ re-verify and the binding `ALG-*`.

| Module (RD-9) | Keep (algorithm) | Drop (non-conformant) | Re-verify (RD-8 means) | Binding |
|---|---|---|---|---|
| `level_0.py` | zero-line loss detect + per-band `line_factor` truncation | `tkinter`, `cv2.imwrite`; (codec = NDA stub) | unit test: synthetic loss patterns → correct truncation + `LOST_PACKET` flag | ALG-L0-LOSS (DEC `[impl]`) |
| `level_1.py::NUC` | dark/DSNU, NUC/PRNU gain-offset, BPR, saturation | dialogs, disk generators, hardcoded bands | unit test vs reference frames; constants from ADF | ALG-RAD-DARK/NUC/BPR/SAT |
| `level_1.py::sharpening`,`Denoiser` | deconvolution, PCA/MA/wavelet/Gaussian/Butterworth denoise | interactive I/O, plotting | radiometry-preservation test; default-off | ALG-ENH-* |
| `level_1.py::TOA` | DN→radiance, radiance→reflectance, ESUN/solar geom | `pyorbital` TLE fetch | unit test vs known DN→reflectance vectors | ALG-TOA-RAD/REF |
| `band_coreg.py` | SIFT match → homography → warp; match-count gate | `tkinter`, `matplotlib`, `b6` hardcode | unit test: synthetic shift recovery; acceptance gate (REQ-F-COR-03) | ALG-COR-FEAT/HOM/WARP |
| `georeferencing_v1.py` | viewing-model geoloc, GCP, DEM ortho, resample/reproject | **GEE `referenceDownload`**, `pyorbital`/`skyfield` TLE | geolocation-accuracy test vs reference; rigorous kernel `[impl]` | ALG-GEO-ORBIT/GSD/GCP/ORTHO/RESAMP |
| `pansharp.py` | MS↔PAN align + fuse | `PIL`/`cv2` file I/O | spectral/spatial fidelity test; default-off | ALG-PAN-ALIGN/FUSE |
| `metrics_ips.py` | SNR/RMSE/PSNR/MSE/variance formulas | generator/file plumbing | unit test vs analytic values | ALG-QA-SNR/RMSE/PSNR/MSE/VAR |

**EOPF CPM / OSS evaluation:** accepted as-is on the basis of upstream maturity (extensive public tests,
documentation, operational use); evaluation reduces to (a) pinning the qualified versions and (b)
verifying the project's *use* at unit/integration level (RD-8). No internal re-evaluation is warranted at
Category C for these established components.

---

## <8> Corrective actions

### <8.1> Identified corrective actions (Annex N <8>a)

Actions required to raise the reused software (chiefly SRF-RU-HER) to the Category-C quality of the RB;
each is executed in implementation (SDP WP-5, post-CDR) and verified per RD-8.

| Id | Corrective action | Applies to | Closes gap | Verified by |
|---|---|---|---|---|
| CA-01 | Extract **pure Cores** (strip `tkinter`/`cv2`/file I/O; algorithm-only, array-in/array-out) | SRF-RU-HER | <5.2>13, <5.3> | code review, lint, unit tests (RD-8) |
| CA-02 | **Externalise all instrument constants** to the sensor profile + private ADFs (no constants in code) | SRF-RU-HER-RAD/TOA/GEO | REQ-AD-01, REQ-D-04, REQ-S-05 | review + profile-swap test |
| CA-03 | Add **typing, docstrings, PEP-8** + lint/format/complexity/security gates (`black`/`ruff`/`mypy`/`bandit`/`xenon`) | SRF-RU-HER | <5.2>13, REQ-Q-01 | CI quality gate (SDP §5.4) |
| CA-04 | Author **unit tests with reference vectors** + (where data permits) reference-product validation | SRF-RU-HER | <5.2>5/7 | coverage report (RD-8) |
| CA-05 | Establish **requirements→design→code→test traceability** for the re-engineered Cores | SRF-RU-HER | <5.2>1/2/3 | traceability matrix |
| CA-06 | **Replace `pyorbital`/`skyfield`/GEE** geometry sourcing with `L0c` telemetry + private ADF (`DPM-ADF-GEOM`) | SRF-RU-HER-GEO/TOA | licence (GPL) + external-service removal | integration test, licence audit |
| CA-07 | **Replace file/format I/O with `EOProduct`/Zarr** via CPM (`C-COM-PRODUCT`/`IO`) | SRF-RU-HER (all) | REQ-D-06, REQ-F-PRD-01 | integration test |
| CA-08 | **Confirm OSS + CPM licences** against each pinned `LICENSE`/`NOTICE`; resolve OpenCV/FFmpeg + GDAL-driver items (<4.5>) | SRF-RU-OSS-*, SRF-RU-CPM | <5.2>11, licence | release-time licence audit |
| CA-09 | **Pin OSS versions** in a lockfile (resolve `[TBC@impl]`); document the **CPM bump procedure** | SRF-RU-OSS-*, SRF-RU-CPM | reproducibility, REQ-M-03 | lockfile + V&V re-run |
| CA-10 | Keep the **NDA L0 codec body private** (`[impl]`), public Core exposes interface only | SRF-RU-HER-L0 | SRS <5.8>, data policy | review (private repo path) |

### <8.2> Results of implementation of corrective actions (Annex N <8>b)

**Status at CDR: PLANNED / not yet executed.** Per the SDP (RD-1) and the project lifecycle,
**implementation (code) starts only after CDR**; therefore CA-01..CA-10 are baselined here as the reuse
work-plan and their implementation results will be recorded at the next review (post-CDR), in the V&V
report and the traceability matrix. No corrective action is closed at this issue. (Licence-audit items
CA-08 and supply-chain pinning CA-09 are cross-referenced to the risk register, RD-11.)

---

## <9> Configuration status of the reused baselines (Annex N <9>a)

| Reuse item | Baseline identifier | Source of truth | Status at CDR |
|---|---|---|---|
| SRF-RU-HER | Frozen `02_scripts/` snapshot (RD-9): `level_0.py` (62), `level_1.py` (860), `band_coreg.py` (223), `georeferencing_v1.py` (691), `pansharp.py` (137), `metrics_ips.py` (183) — `main_ips_v6.py` (402) **excluded** | `previous-work/multispectral_demo_satellite_preprocessing_pipeline/02_scripts/` | Frozen reference; re-engineering CA-01..CA-07/CA-10 **planned** (WP-5) |
| SRF-RU-CPM | `eopf == 2.8.1` | `pyproject.toml` (RD-13); SDE `cpm-build-environment` image | **Pinned/baselined**; bump gated (REQ-M-03, CA-09) |
| SRF-RU-OSS-* | Transitive closure of `eopf == 2.8.1` (numpy, scipy, scikit-image, scikit-learn, xarray, zarr, dask, pandas, rasterio, GDAL, OpenCV, PyWavelets) | lockfile (to be generated at WP-5) | Versions `[TBC@impl]`; to be **frozen in lockfile** (CA-09) |
| Project licence | Apache-2.0, © 2026 ESA | `LICENSE` | Baselined |
| Dropped (not reused) | `pyorbital` (GPL-3.0), `skyfield`, `earthengine-api`, `tkinter`, `matplotlib`, `memory_profiler`, `requests`/`urllib`/`Pillow` | — | Excluded by decision (<4.4>, <6.2>) |

> Configuration control of these baselines is exercised through the project VCS and `pyproject.toml`/
> lockfile (SDP RD-1); changes to the CPM pin or the OSS closure follow the V&V-gated dependency-change
> procedure (REQ-M-03) and are reflected in this SRF at the next baseline.
