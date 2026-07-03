# Software Configuration File (SCF)

| Field | Value |
|---|---|
| **Document** | SCF — Software Configuration File (as-built configuration record of the SCI) |
| **DRD ref** | ECSS-E-ST-40C Rev.1 (software configuration management activities; Software Configuration File / as-built record); ECSS-M-ST-40C Rev.1 (configuration and information management — CIDL/SCF); ECSS-Q-ST-80C Rev.2 (software configuration management) |
| **Container** | Configuration management records — `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | QR |
| **Status** | Issued at QR |

> This Software Configuration File records the **as-built configuration baseline** of the single
> Software Configuration Item (SCI) `msi_processor` at the **Qualification Review (QR)**. It is the
> physical-configuration companion of the Configuration Item Data List (RD-17, CIDL) and the Software
> Release Note (RD-16, SRN/SRelD): the CIDL enumerates *which* items make up the SCI, the SRN declares
> the *released* version, and this SCF freezes the *exact build, runtime environment, verification
> toolchain and CI execution environment* against which the QR verification evidence (RD-11, SVR) was
> produced — so that the baseline is reconstructible and the validation configuration is confirmed
> (SReVP RD-12 QR exit criterion (c)/(d)). It is **descriptive, not normative**: it states what is, not
> what shall be; the binding requirements live in the SRS (RD-4) and the development/CM rules in the SDP
> (RD-1) and SPAP (RD-13). The QR configuration baseline is `main` at commit **d140599** (pipeline
> **30730** = success). No Git tag exists yet; the release action that stamps the tag and uploads the
> package is taken at the release decision (see <4.3>, <9.3>). The footprint is tailored to a
> Category C, single-developer ground-segment processor whose **code is public but whose raw `L0` data
> and instrument calibration are private** (RD-4 SRS <5.1>, <5.8>).

**DRD clause coverage.** Where this SCF records each expected configuration-management / as-built
content element (ECSS-E-ST-40C Rev.1 CM; ECSS-M-ST-40C Rev.1 SCF/CIDL):

| Expected content | Topic | This document |
|---|---|---|
| SCI identification | Name, repository, criticality | <4.1> |
| Configuration baseline | Commit, branch, pipeline of record | <4.2> |
| Version identification | Dynamic version mechanism; QR release candidate | <4.3> |
| As-built build system | Backend, build invocation, packaging standards | <5.1> |
| As-built source structure | Package layout; processing units | <5.2> |
| Built artefacts | Wheel, documentation package, container image | <5.3> |
| Pinned runtime environment | Python, declared dependencies, resolved closure | <6.1>..<6.3> |
| Dependency-CVE exceptions | Justified `pip-audit` ignore-list | <6.4> |
| Verification toolchain configuration | Tool inventory + pinned configs; pre-commit | <7.1>, <7.2> |
| CI/CD execution environment | CI image, runner, gate configuration | <8.1>, <8.2> |
| Configuration control & status accounting | Control procedure; baseline accounting; CIDL/SRN link | <9.1>..<9.3> |
| Open configuration items | QR deferrals and open items carried to AR | <10> |

---

## <1> Introduction

**Purpose.** This SCF identifies and freezes the as-built configuration of the SCI `msi_processor` at
QR. It captures the configuration data needed to (a) reproduce the exact build, (b) re-create the
pinned runtime and verification environment, and (c) confirm that the configuration under which the
QR verification/validation campaign (RD-8 V&V Plan, RD-10 SUITP, RD-11 SVR) was run is the configuration
being qualified. It thereby supports SReVP RD-12 QR exit criteria (c) "the SCI is a formal version
under configuration control" and (d) "confirm test/RB-validation configuration".

**Objective.** Per the ECSS configuration-management process (ECSS-E-ST-40C Rev.1; ECSS-M-ST-40C
Rev.1) and ECSS-Q-ST-80C Rev.2, the SCF records: the SCI identification and naming (<4>); the
as-built physical configuration — build system, source structure and produced artefacts (<5>); the
pinned runtime environment, eopf closure and dependency-CVE exception list (<6>); the verification
toolchain and its pinned configurations (<7>); the CI/CD execution environment, runner and gate
configuration (<8>); the configuration-control and status-accounting record for this baseline (<9>);
and the open configuration items deferred to AR (<10>).

**Content.** Clauses <2>/<3> give the document references and terms. Clause <4> is the SCI
identification and the configuration baseline of record. Clauses <5>–<8> are the as-built record
proper (build, runtime, toolchain, CI). Clause <9> is the configuration control/status-accounting
section and the relationship to the CIDL (RD-17) and SRN (RD-16). Clause <10> lists the open items.

**Reason for preparation.** The SCF is a QR data-package deliverable (RD-1 SDP §5.2; SReVP RD-12). It
is produced light (Category C, single-developer) but completely, because the configuration baseline is
the object on which the qualification verdict is taken. All values in this file are **read from the
baselined source tree at commit d140599** (`pyproject.toml`, `.gitlab-ci.yml`, `.flake8`, `.mypy.ini`,
`bandit.yml`, `.hadolint.yml`, `.pre-commit-config.yaml`, `docs/conf.py`, `Dockerfile`), not asserted
from memory.

---

## <2> Applicable and reference documents

### Applicable documents (AD)

| Id | Document | Reference |
|---|---|---|
| AD-1 | ECSS Space engineering — Software (software configuration management activities; SCF / as-built record) | ECSS-E-ST-40C Rev.1 (30 April 2025) |
| AD-2 | ECSS Configuration and information management (configuration management; CIDL / SCF concept) | ECSS-M-ST-40C Rev.1 |
| AD-3 | ECSS Space product assurance — Software (software configuration management requirements) | ECSS-Q-ST-80C Rev.2 |
| AD-4 | EOPF CPM — Product Structure & Format Definition / data model and runtime | EOPF CPM docs (`eopf == 2.8.1`) |
| AD-5 | Python packaging standards — PEP 517 (build-backend interface), PEP 518/PEP 621 (build-system & project metadata) | python.org PEPs |

### Reference documents (RD)

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Development Plan (SDP) | `compliance/software-development-plan.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-5 | `msi-processor` Interface Control Document (ICD) | `compliance/drd/icd-interface-control.md` |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — `DPM-M-*` | `compliance/drd/dpm-data-processing-model.md` |
| RD-7 | `msi-processor` Algorithm Theoretical Basis Document (ATBD) — `ALG-*` | `compliance/drd/atbd-algorithm-theoretical-basis.md` |
| RD-8 | `msi-processor` V&V Plan (SVerP + SValP) | `compliance/drd/vv-plan.md` |
| RD-9 | `msi-processor` Software Design Document (SDD) — `C-*`, `IF-*` | `compliance/drd/sdd-software-design.md` |
| RD-10 | `msi-processor` SUITP (unit/integration test specifications & procedures) | `compliance/drd/suitp-unit-integration-test-plan.md` |
| RD-11 | `msi-processor` Software Verification Report (SVR) | `compliance/drd/vv-report.md` (QR) |
| RD-12 | `msi-processor` Software Review Plan (SReVP) | `compliance/drd/srevp-software-review-plan.md` |
| RD-13 | `msi-processor` Software Product Assurance Plan (SPAP) | `compliance/drd/spa-plan.md` |
| RD-14 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| RD-15 | `msi-processor` Requirements Traceability Matrix (RTM) | `compliance/traceability/traceability-matrix.md` |
| RD-16 | `msi-processor` Software Release Note (SRN / SRelD) | `docs/srn.md` + GitLab Releases |
| RD-17 | `msi-processor` Configuration Item Data List (CIDL) | `docs/cidl.md` |
| RD-18 | `msi-processor` Risk Register | `compliance/drd/risk-register.md` |

---

## <3> Terms, definitions and abbreviated terms

The SDP §3, SSS <3> and SRS <3> glossaries apply in full. Only terms specific to configuration
management are listed.

| Term / abbr. | Definition |
|---|---|
| SCI | Software Configuration Item — the single deliverable software item `msi_processor` |
| SCF | Software Configuration File — this document; the as-built physical-configuration record |
| CIDL | Configuration Item Data List — the enumeration of the items constituting the SCI (RD-17) |
| SRN / SRelD | Software Release Note / Software Release Document — declares the released version (RD-16) |
| Configuration baseline | A formally identified, frozen state of the SCI (here: `main` @ d140599) |
| Baseline of record | The commit + CI pipeline whose evidence underwrites the QR verdict (d140599 / pipeline 30730) |
| Build backend | The PEP 517 backend that turns the source tree into a distribution (here: `flit_core`) |
| Resolved closure | The full transitive set of installed dependencies pinned by the SDE build image |
| Gate (blocking) | A CI job whose failure fails the pipeline (no `allow_failure`) |
| `allow_failure` job | A CI job whose failure is recorded but does not gate the pipeline (justified, non-gating) |
| SDE | EOPF Software Development Environment (Studio VM; `cpm-build-environment` image) |
| QR / AR | Qualification Review / Acceptance Review |

---

## <4> Software Configuration Item identification

### <4.1> SCI identity and naming

| Attribute | Value |
|---|---|
| SCI name (distribution) | `msi-processor` |
| Python import package | `msi_processor` |
| Repository | `gitlab.eopf.copernicus.eu/ipf/msi-processor` (GitLab group `ipf`) |
| Authors / vendor | `AstroCan17` / ESA (`pyproject.toml`, Dockerfile OCI `vendor` label) |
| Licence | Apache-2.0 (`LICENSE`; `pyproject.toml` `license = {file = "LICENSE"}`) |
| Software criticality | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| Distribution policy | `Private :: Do Not Upload` classifier; published only to the project's GitLab package registry (not public PyPI) |
| `requires-python` | `>= 3.11` |

The SCI is a **single software item** (one Python distribution producing one importable package). The
distribution name uses the hyphen form (`msi-processor`) and the import package the underscore form
(`msi_processor`); both denote the same SCI.

### <4.2> Configuration baseline of record

| Attribute | Value |
|---|---|
| Baseline branch | `main` |
| Baseline commit (short) | `d140599` |
| Baseline commit (full SHA-1) | `d140599293ac083dc3da04e63e645da54b8f0b5b` |
| Baseline commit subject | `Merge branch 'test/integration-chain' into 'main'` |
| CI pipeline of record | `30730` — **success** |
| VCS | Git on GitLab; changes to `main` only via reviewed Merge Requests (SPAP RD-13 §6.5) |

This is the configuration baselined at QR. The QR verification evidence (RD-11 SVR), the V&V campaign
(RD-8/RD-10) and all numbers in this SCF refer to this commit and this pipeline.

### <4.3> Version identification and QR release candidate

The distribution version is **dynamic** (`pyproject.toml` `dynamic = ["version", "description"]`,
`flit_core` backend): `flit_core` resolves the version and summary from the package module
`msi_processor/__init__.py` at build time. The as-built tree at d140599 carries the template default
`__version__ = "0.0.1"` in that module.

The **proposed QR release-candidate version is `v0.1.0-rc1`**, referenced to baseline commit d140599.
Per the release strategy (RD-1 SDP; RD-16 SRN), creating the Git tag and uploading the package is the
**release action taken at the release decision** (AR / release gate), not at QR authoring: **no Git
tag exists yet** at QR. The SRN (RD-16) states the release candidate and the baseline commit; the SCF
records the as-built version mechanism and the proposed RC. When the tag is created, the
`deliver-package` and `upload-documentation`/`pages` jobs (tag-gated, <8.2>) publish the wheel and the
versioned documentation, and `__version__` is set to the release value as part of that action.

---

## <5> As-built physical configuration

### <5.1> Build system (PEP 517)

| Attribute | Value (`pyproject.toml`) |
|---|---|
| Build backend | `flit_core.buildapi` |
| Build-system requires | `flit_core >= 3.2, < 4` |
| Metadata standard | PEP 621 (`[project]` table); PEP 517 build interface |
| Dynamic fields | `version`, `description` (resolved from `msi_processor.__init__`) |
| Wheel build (CI `build-package`) | `pip wheel -w dist --no-deps .` |
| Tag-gated upload (CI `deliver-package`) | `twine upload` to the project GitLab PyPI registry (`rules: if $CI_COMMIT_TAG`) |

The build is dependency-free at wheel time (`--no-deps`); the runtime closure (<6>) is resolved at
install time against the pinned `eopf` stack.

### <5.2> As-built source structure

The SCI source tree (`msi_processor/`) at d140599:

| Path | Role |
|---|---|
| `msi_processor/__init__.py` | Package root; carries `__version__` (dynamic-version source) |
| `msi_processor/common/types.py`, `common/metrics.py` | Shared types and the QA-metrics module (SNR/RMSE/PSNR/MSE/variance) |
| `msi_processor/sensors/profile.py` | Sensor-profile model (sensor-agnostic externalisation) |
| `msi_processor/exceptions/` | Specific error/warning classes |
| `msi_processor/computing/<unit>/` | The eight processing units (pure core + `EOProcessingUnit` wrapper + computing-model JSON) |
| `tests/ut/`, `tests/it/` | Unit (Tier A) and integration (Tier B) test suites |

The eight processing units and their output levels (RD-9 SDD, RD-6 DPM):

| Unit (`computing/<unit>`) | Level | Note |
|---|---|---|
| `l0_decode` | L1A | Level-0 → L1A decode |
| `radiometric` | L1A | Radiometric correction |
| `enhancement` | L1B | MTF compensation mandatory (always applied) |
| `toa` | L1B | TOA radiance/reflectance |
| `coregistration` | L1B → L1C | Inter-band co-registration |
| `georeference` | L1C | Geolocation / geocoding |
| `atmospheric` | L2A | Surface-reflectance retrieval |
| `pansharpen` | post-L2A | Optional derivative (`simple_mean` operational) |

### <5.3> Built artefacts

| Artefact | Produced by | Notes |
|---|---|---|
| Python wheel | `build-package` (`pip wheel`) | Blocking gate; tag-gated upload to GitLab PyPI registry by `deliver-package` |
| Documentation package | `sphinx-build` → `upload-documentation` → `pages` | `msi-processor-docs.tar.gz`; Sphinx autodoc; versioned via GitLab Pages (main/tag only) |
| Container image | `Dockerfile` (multi-stage), built by `deliver-image` (kaniko) | Build stage `python:3.11.7-bullseye`; runtime base `registry.eopf.copernicus.eu/sde/dask-container-images/dask-scheduler-worker:latest`; OCI labels carry `revision = $CI_COMMIT_SHA`. **Non-blocking** on the shell runner (no container runtime; see <8>) |

The image installs the SCI with the `cluster-plugin` extra (`pip install .[cluster-plugin]`) and is the
Dask runtime for distributed execution. The wheel is the primary deliverable; the image and docs are
auxiliary delivery artefacts.

---

## <6> Pinned runtime environment configuration

### <6.1> Python runtime

| Attribute | Value |
|---|---|
| Language | Python, `requires-python >= 3.11`; target/classifier 3.11 (CPython) |
| Build-stage interpreter (Docker) | `python:3.11.7-bullseye` |
| Tool target version | `black` `target-version = py311`; `mypy` `python_version = 3.11`; SonarQube `sonar.python.version = 3.11` |

### <6.2> Declared runtime dependencies

Declared in `pyproject.toml` `[project].dependencies`:

| Dependency | Pin / constraint | Reason (as documented in `pyproject.toml`) |
|---|---|---|
| `eopf` | `== 2.8.1` | **Hard pin** to the EOPF CPM version in the SDE `cpm-build-environment` image (same pin as the sibling `eo-data-embedding` project) |
| `opencv-python-headless` | `>= 4.8` | Genuine runtime dependency of coregistration / pan-sharpening (SIFT/FLANN/RANSAC/`warpPerspective`); headless wheel (no display on CI/target); ships PEP 561 stubs so `mypy` resolves `cv2` natively |
| `rasterio` | `>= 1.3` | GDAL/PROJ binding for the georeference affine geotransform + reprojection (`ALG-GEO-RESAMP`); already an `eopf` transitive, declared explicitly because imported directly; no PEP 561 stubs (see `.mypy.ini` overrides) |

Optional-dependency groups (all sourced from the matching `eopf[...] >= 1.5.0` extra, so the tool
versions track the pinned CPM stack): `cluster-plugin`, `tests`, `linter`, `typing`, `formatter`,
`security`, `notebook`, `doc` (+ `sphinxcontrib-mermaid`), `complexity`, `doc-cov`, `dev`.

### <6.3> Resolved dependency closure and SDE image

The runtime closure is **resolved and pinned by the SDE build image**
`registry.eopf.copernicus.eu/sde/cpm-build-environment:latest`, which ships the `eopf == 2.8.1` CPM
stack. In CI, the `security` job records the resolved closure as an artefact
(`pip freeze > requirements.txt`), and `deps-sec` re-resolves the project's own closure in an isolated
virtual environment (`.audit-venv`) and freezes it (`audit-requirements.txt`, excluding the
first-party `msi-processor`) as the CVE-scan target. The closure is therefore an externally controlled
configuration item: it is fixed for as long as `eopf == 2.8.1` is pinned, and is only allowed to change
through a deliberate eopf bump (REQ-M-03), which re-runs the full V&V before re-baselining (RD-8 §<5.6>).

### <6.4> Dependency-CVE exception list (justified)

`deps-sec` runs `pip-audit` against the resolved closure with a documented ignore-list. These are
**transitive** vulnerabilities introduced via the pinned `eopf == 2.8.1` stack (transitive
`starlette 1.0.1`), currently **unfixable without diverging from the SDE build image** (fix is
`starlette >= 1.1.0`):

| Ignored advisory | Component | Status |
|---|---|---|
| `PYSEC-2026-248` | `starlette 1.0.1` (eopf-transitive) | Accepted exception; revisit on eopf bump |
| `PYSEC-2026-249` | `starlette 1.0.1` (eopf-transitive) | Accepted exception; revisit on eopf bump |
| `CVE-2026-48817` | `starlette 1.0.1` (eopf-transitive) | Accepted exception; revisit on eopf bump |
| `CVE-2026-48818` | `starlette 1.0.1` (eopf-transitive) | Accepted exception; revisit on eopf bump |

The ignore-list is encoded in `.gitlab-ci.yml` (`deps-sec`: `--ignore-vuln PYSEC-2026-248 …`) with an
inline rationale and an explicit "revisit whenever the eopf pin is raised" condition. Any other HIGH/
CRITICAL finding fails the (blocking) `deps-sec` gate.

---

## <7> Verification toolchain configuration

### <7.1> Tool inventory and pinned configurations

The verification toolchain runs on the SDE `cpm-build-environment` image via the shell runner (<8>).
Tools and their as-built configuration files at d140599:

| Tool | Role | Configuration (as-built) |
|---|---|---|
| `pytest` + `coverage` | Unit tests (`-m unit`) + Cobertura/JUnit reports | `[tool.pytest.ini_options]` markers `unit`, `integration`, `need_files`; coverage → `coverage.xml`, JUnit → `TEST-pytests.xml` |
| `flake8` | Style/lint | `.flake8`: `max-line-length = 120`; `per-file-ignores` `__init__.py: F401` |
| `black` | Formatting | `[tool.black]`: `line-length = 120`, `target-version = ['py311']` (CI runs `--check --diff`) |
| `isort` | Import ordering | `[tool.isort]`: `profile = "black"` (CI runs `--check --diff`) |
| `mypy` | Static typing | `.mypy.ini`: `python_version = 3.11`; strict block for `msi_processor.*` (`disallow_untyped_defs`, `disallow_incomplete_defs`, `disallow_any_generics`, `no_implicit_reexport`, …); `ignore_missing_imports` for `fsspec`, `zarr.*`, `jinja2.*`, `rasterio`/`rasterio.*`, `affine` |
| `bandit` | SAST | `bandit.yml`: `exclude_dirs: tests/*.py`; `skips: ['B314','B405','B320','B410']` |
| `pip-audit` | Dependency CVE scan | Isolated `.audit-venv`; ignore-list per <6.4> (replaces the prior no-op `trivy` job on the shell runner) |
| `xenon` | Cyclomatic-complexity bound | `--max-average B --max-modules C --max-absolute D` (advisory) |
| `hadolint` | Dockerfile lint | Binary v`2.12.0` fetched in-job; `.hadolint.yml`: `failure-threshold: warning`, override `info` `DL3007` |
| `docstr-coverage` | Docstring density | `-F 30` (≥ 30 %), advisory |
| `sphinx` | Docs build (autodoc) | `docs/conf.py`: `sphinx.ext.autodoc`, `sphinx_autodoc_typehints`, `sphinxcontrib-mermaid` (`mermaid_version = 10.9.1`); `release` patched from branch/tag at build |
| SonarQube | Quality-gate adjudication | `sonar.python.version = 3.11`; ingests flake8/bandit/xunit/coverage reports (advisory) |

Test-suite size of the as-built configuration (authoritative pass/fail is RD-11 SVR): **248 test
cases** — 246 unit (244 passed, 2 xfailed) + 2 integration (2 passed) — from 238 test functions. The
2 xfails are in `tests/ut/computing/test_georeference_core.py` and intentionally verify the
`orthorectify` fail-stop (see <10>).

### <7.2> Pre-commit hook pinning (`.pre-commit-config.yaml`)

Local shift-left hooks are version-pinned so developer and CI checks agree:

| Hook repo | Pinned rev |
|---|---|
| `pre-commit/pre-commit-hooks` | `v4.3.0` |
| `commitizen-tools/commitizen` (commit-msg) | `v2.20.4` |
| `psf/black` | `24.3.0` |
| `PyCQA/bandit` (config `bandit.yml`) | `1.7.5` |
| `PyCQA/flake8` | `6.0.0` |
| `PyCQA/isort` | `5.12.0` |
| `asottile/add-trailing-comma` | `v2.2.3` |

`default_language_version.python = python3.11`.

---

## <8> CI/CD execution environment

### <8.1> CI image and runner

| Attribute | Value (`.gitlab-ci.yml`) |
|---|---|
| Declared CI image | `registry.eopf.copernicus.eu/sde/cpm-build-environment:latest` (`default.image`) |
| Registered runner | A **single Studio VM with a SHELL executor** |
| Consequence | The runner **ignores `image:` directives**; jobs run directly in the SDE shell environment. Jobs needing a container runtime, Dask gateway or S3 cannot run here (see `allow_failure` jobs in <8.2>). The `docker-linter` job fetches the `hadolint` binary in-job for this reason; `deps-sec` replaced the image-dependent `trivy` job |

### <8.2> Pipeline gate configuration

**Blocking verification, build and documentation gates (nine), all green on pipeline 30730**, preceded
by the `validate-variables` pipeline-entry guard (also blocking):

| Job | Stage | Method / tool |
|---|---|---|
| `validate-variables` | unit tests | Pipeline-entry guard: required CI variables present (SQ + Dask-gateway + JupyterHub token) |
| `linter` | unit tests | `flake8` (blocking) |
| `docker-linter` | unit tests | `hadolint` v2.12.0 (blocking) |
| `formater` | unit tests | `black --check` + `isort --check` (blocking) |
| `typing` | unit tests | `mypy` (blocking) |
| `unit-tests` | unit tests | `pytest -m unit` + coverage Cobertura/JUnit (blocking) |
| `security` | unit tests | `bandit` SAST (blocking) |
| `deps-sec` | unit tests | `pip-audit` in isolated venv (blocking) |
| `build-package` | build | `pip wheel` (blocking) |
| `sphinx-build` | documentation generation | Sphinx docs build (blocking) |

**Allow-failure (non-gating) jobs (five), justified:**

| Job | Why non-blocking |
|---|---|
| `docs-cov` | `docstr-coverage` informational (≥ 30 %) |
| `complexity` | `xenon` advisory |
| `sonarqube` | External service (`sonar-scanner` image; needs `SQ_URL`/`SQ_LOGIN`) |
| `integration-tests` | Template Dask-gateway/S3 path unavailable on the shell runner (tests themselves now pass; promote to blocking on a K8s runner) |
| `deliver-image` | kaniko needs a container runtime, absent on the shell runner |

**Conditional release jobs (rules-gated, not `allow_failure`):** `deliver-package`
(`if $CI_COMMIT_TAG`) uploads the wheel to the GitLab PyPI registry; `upload-documentation` and
`pages` run on `main`/tags to publish versioned docs to GitLab Pages.

The `allow_failure`/non-blocking status of the five jobs is a **deliberate, justified configuration
choice** for the current shell-runner infrastructure (RD-8 §<4>; Risk Register RD-18), not a defect.
The `integration-tests` and `deliver-image` jobs become candidates for blocking when the SDE
Kubernetes runner replaces the shell executor.

---

## <9> Configuration control and status accounting

### <9.1> Configuration control

All configuration items (source, tests, CI pipeline, tool configs, compliance documents) are under Git
and changed **only through reviewed Merge Requests to `main`** under ECSS-M-ST-40C Rev.1 (SPAP RD-13
§6.5; RD-1 SDP §5.4). Each MR must pass the full blocking gate set (<8.2>) or carry a recorded waiver.
The repository history is the configuration-status record. Branch protection prevents direct pushes to
`main`.

### <9.2> Configuration status accounting (this baseline)

| Item | As-built status at QR |
|---|---|
| Baseline | `main` @ d140599 (`d140599293ac083dc3da04e63e645da54b8f0b5b`) |
| CI pipeline of record | 30730 — success; 9 blocking gates green (+ `validate-variables` guard) |
| SCI version | dynamic via `flit_core`; module `__version__ = "0.0.1"` (template default); QR RC proposed `v0.1.0-rc1` |
| Git tag | none yet (created at the release action; see <4.3>) |
| Implementation completeness | 8/8 processing units implemented, CI-green |
| Test configuration | 248 cases (246 unit: 244 pass/2 xfail; 2 integration: 2 pass) — verdicts in RD-11 SVR |
| Open NCR/SPR | tracked to closure at QR/AR (SReVP RD-12; SPAP RD-13) |

### <9.3> Relationship to CIDL and SRN

This SCF is one of three coupled configuration deliverables in the QR data package:

- **CIDL (RD-17, `docs/cidl.md`)** — enumerates the configuration items that constitute the SCI
  (source modules, tests, CI, docs, compliance set) and their identification.
- **SCF (this document)** — records the as-built *physical configuration* (build, runtime, toolchain,
  CI) frozen at the baseline of record.
- **SRN / SRelD (RD-16, `docs/srn.md` + GitLab Releases)** — declares the released version
  (`v0.1.0-rc1` referenced to d140599), the contents and the open items.

The three are mutually consistent against commit d140599 and pipeline 30730.

---

## <10> Open configuration items at QR

The following are recorded as open configuration items carried to AR; they do not alter the
Category-C qualification verdict for the software item.

**(a) Numeric performance-budget validation withheld (QR open item → AR).** The Tier-C numeric
validation of `REQ-P-01..05` (`RAD_ACC`, `GEO_CE90` + `BAND_COREG`, `BOA_ACC`, `THRU_SCENE`,
`MEM_BUDGET`) requires the operator's private real RAW + calibration data (data policy SSS <5.1>) which
is never in public CI. These requirements are verified at QR by analysis/design and the algorithm
V&V; the numeric budget closure is performed on operator data at AR (RD-8 §<8.8>; RD-11 SVR). This is
the single most important QR configuration limitation.

**(b) Deferred fail-stop algorithm paths (`[impl]`).** The as-built tree contains **six deliberately
deferred, fail-stop algorithm implementations**, all recorded as waivers traced in the RTM (RD-15,
G-1/G-6); the operational baseline never executes them:

| # | Unit / algorithm | Reason |
|---|---|---|
| 1 | `l0_decode` `decode_source_packets` (`ALG-L0-DEC`) | Sensor-private on-wire forms only; the documented canonical L0 ground-decodes in `ground_decode` (REQ-F-L0-06); open-container path unchanged |
| 2 | `georeference` `orbit_state` (`ALG-GEO-ORBIT`) | Ephemeris/orbit propagation (CDR-target; GPL TLE path dropped) |
| 3 | `georeference` `orthorectify` (`ALG-GEO-ORTHO`) | Rigorous collinearity/DEM line-of-sight needs the sensor-private viewing model (CDR-target); operational L1C uses GCP reference-image refinement; 2 xfail tests verify the fail-stop |
| 4 | `atmospheric` `retrieve_atmospheric_parameters` (`ALG-ATM-PAR`) | Image-based AOT/water-vapour retrieval |
| 5 | `atmospheric` `resolve_rt_lut` (`ALG-ATM-RT`) | Radiative-transfer-engine LUT build |
| 6 | `atmospheric` `classify_scene_ml` (`ALG-ATM-SCM`) | ML scene-classifier refinement |

Additionally, the pan-sharpen component-substitution fusion methods (`brovey`/`gs`/`ihs`/`atrous`) are
deferred; only `simple_mean` is operational.

**(c) CI promotion pending K8s runner.** The five `allow_failure` jobs (<8.2>) — notably
`integration-tests` and `deliver-image` — are non-blocking only because the registered runner is a
shell executor; they are candidates for promotion to blocking gates once the SDE Kubernetes runner
lands (Risk Register RD-18).

**(d) Release tag.** No Git tag exists at QR; the `v0.1.0-rc1` tag and the package/docs publication are
the release action taken at the release decision (<4.3>, <9.3>).

---

*End of Software Configuration File. Authored per ECSS-E-ST-40C Rev.1 (software configuration
management; SCF / as-built record), ECSS-M-ST-40C Rev.1 (CIDL/SCF) and ECSS-Q-ST-80C Rev.2, tailored
for Category C, single-developer. The as-built baseline of record is `main` @ d140599 (pipeline 30730 =
success). The CIDL (RD-17) enumerates the configuration items; the SRN (RD-16) declares the release
candidate `v0.1.0-rc1`; the QR verification evidence is the SVR (RD-11).*
