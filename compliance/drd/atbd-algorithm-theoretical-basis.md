# Algorithm Theoretical Basis Document (ATBD)

| Field | Value |
|---|---|
| **Document** | ATBD — Algorithm Theoretical Basis Document |
| **DRD ref** | EO-domain ATBD convention (no ECSS-E-ST-40C Rev.1 annex); algorithm constituent of the DPM (RD-6), supporting the SRS (RD-1) |
| **Container** | Technical documentation — `docs/atbd/` (published); source in `compliance/drd/` |
| **Project** | `msi-processor` (gitlab.eopf.copernicus.eu/ipf/msi-processor) |
| **Software criticality** | Category C (ECSS-Q-ST-80C Rev.2 / ECSS-E-ST-40C Annex R) |
| **Baselined at** | PDR (Preliminary Design Review) |
| **Status** | Draft for PDR |

> This ATBD records the **theoretical and mathematical basis** of every processing stage of
> `msi-processor`, the generic high-resolution pushbroom **multispectral imager (MSI)** ground-segment
> processor. It is the algorithm-level companion to the SRS (RD-1, which states *what the software
> shall do* via `REQ-*`) and the per-level **Detailed Processing Model** (DPM, RD-6, which records the
> concrete per-sensor numeric realisation). The ATBD answers *why each algorithm is correct and how it
> is derived*. Each stage is described as **Purpose / Theoretical background / Governing equations /
> Inputs (incl. calibration) / Parameters / Assumptions & limitations / Heritage & traceability**.
> The mathematical heritage is the prior-work pushbroom-MSI preprocessing pipeline (RD-10, see SRF
> RD-11); this document re-expresses that heritage in sensor-agnostic, profile-externalised form and
> marks the **atmospheric-correction** stage as **new / to-be-defined**. No private calibration
> coefficients (gain/offset, dark, flat-field, ESUN, viewing model) appear here: they are supplied at
> run time through the active profile and its ADFs, per the data policy (SRS <5.8>, REQ-S-01).

> **Change note (CR):** the image-quality **enhancement** stage is **mandatory** (not optional) — its
> "sharpening" sub-step is **MTF Compensation (MTFC) via PSF deconvolution** (`ALG-ENH-DECONV`, <5.5>),
> a critical Level-1 radiometric/spatial restoration step that always runs; **denoising** (<5.4>)
> remains a sensor-profile-configurable sub-step; **pan-sharpening** (<5.9>) is unchanged (optional).

---

## <1> Introduction

### <1.1> Purpose

This document establishes the algorithm theoretical basis for the `L0c → L2A` processing chain of
`msi-processor`. For each algorithm it gives the governing physics/mathematics, the closed-form
equations as implemented, the calibration and auxiliary inputs consumed, the tunable parameters, and
the assumptions and limitations under which the algorithm is valid. It is the scientific reference for
the numerical-accuracy requirements (REQ-P-01..03, REQ-D-05) and for the local validation of
radiometric, geometric and surface-reflectance budgets (REQ-Q-03).

### <1.2> Scope

The ATBD covers the ten algorithmic subjects realised in the chain:

| # | Stage (ATBD clause) | Level transition | SRS functional group |
|---|---|---|---|
| 1 | L0 decoding & loss handling (<5.1>) | `L0c → L1A` | REQ-F-L0-* |
| 2 | Non-uniformity correction — dark/offset, PRNU, BPR (<5.2>) | `L1A →` | REQ-F-RAD-* |
| 3 | TOA radiance & reflectance (<5.3>) | `→ L1B` | REQ-F-TOA-* |
| 4 | Denoising — sensor-profile-configurable (<5.4>) | within `L1A→L1B` | REQ-F-ENH-01 |
| 5 | MTF compensation (MTFC) / PSF deconvolution — **mandatory** (<5.5>) | within `L1A→L1B` | REQ-F-ENH-02 |
| 6 | Inter-band co-registration (<5.6>) | `L1B →` | REQ-F-COR-* |
| 7 | Geo-referencing / orthorectification (<5.7>) | `→ L1C` | REQ-F-GEO-* |
| 8 | Atmospheric correction (<5.8>) — **new / TBD** | `L1C → L2A` | REQ-F-ATM-* |
| 9 | Pan-sharpening (<5.9>) | within `L1B→L1C` | REQ-F-PAN-* |
| 10 | QA metrics (<5.10>) | all levels | REQ-F-QA-* |

It does **not** re-specify software requirements (SRS, RD-1), interfaces (ICD/IRD), or the per-sensor
numeric values (DPM, RD-6, and private ADFs). The L0 source-packet *bit-level* decode is sensor- and
NDA-specific and is treated abstractly (<5.1>).

### <1.3> Document conventions

Algorithms are given uniquely identified tags **`ALG-<group>-<name>`** for downward traceability
(clause <7>). Equations use standard SI; radiometric quantities follow the spectral-radiance
convention (W m⁻² sr⁻¹ µm⁻¹). The notation table is in <4.2>. Where the heritage implementation
(RD-10) differs from the canonical/rigorous form, the difference is stated explicitly in the stage's
*Assumptions & limitations* and, where it is a known simplification to be improved, flagged as an
**open point** (consolidated in <8>).

---

## <2> Applicable and reference documents

The AD/RD set of the SRS (RD-1 <2>) applies in full. The references most used here:

| Id | Document | Reference |
|---|---|---|
| RD-1 | `msi-processor` Software Requirements Specification (SRS) — `REQ-*` | `compliance/drd/srs-software-requirements.md` |
| RD-2 | `msi-processor` Software System Specification (SSS) — `SYS-*` | `compliance/drd/sss-software-system-specification.md` |
| RD-3 | `msi-processor` Interface Requirements Document (IRD) — `REQ-IF-*` | `compliance/drd/ird-interface-requirements.md` |
| RD-4 | `msi-processor` Interface Control Document (ICD) — concrete interfaces & ADF schemas | `compliance/drd/icd-interface-control.md` (PDR/CDR) |
| RD-6 | `msi-processor` Detailed Processing Model (DPM) — per-level numeric realisation | `docs/dpm/` |
| RD-10 | Prior work — multispectral pushbroom preprocessing pipeline (algorithm heritage) | `02_scripts/`: `level_0.py`, `level_1.py`, `band_coreg.py`, `georeferencing_v1.py`, `pansharp.py`, `metrics_ips.py` |
| RD-11 | `msi-processor` Software Reuse File (SRF) | `compliance/drd/srf-software-reuse-file.md` |
| EX-1 | Vermote et al., *Second Simulation of the Satellite Signal in the Solar Spectrum (6S)*, IEEE TGRS, 1997 | atmospheric RT basis (candidate, <5.8>) |
| EX-2 | Lowe, *Distinctive Image Features from Scale-Invariant Keypoints*, IJCV, 2004 | SIFT basis (<5.6>, <5.7>, <5.9>) |
| EX-3 | Fischler & Bolles, *Random Sample Consensus*, CACM, 1981 | RANSAC robust estimation (<5.6>, <5.7>, <5.9>) |
| EX-4 | Donoho & Johnstone, *Ideal spatial adaptation by wavelet shrinkage*, Biometrika, 1994 | VisuShrink wavelet denoising (<5.4>) |

---

## <3> Terms, definitions and abbreviated terms

The SSS <3> and SRS <3> glossaries apply in full. ATBD-specific symbols are in the notation table
<4.2>. Key abbreviations reused: **DN** digital number; **NUC** non-uniformity correction; **DSNU /
PRNU** dark-signal / photo-response non-uniformity; **BPR** bad-pixel replacement; **TOA / BOA**
top- / bottom-of-atmosphere; **ESUN** band-integrated exo-atmospheric solar irradiance; **GSD** ground
sampling distance; **GCP** ground control point; **DEM** digital elevation model; **AOT** aerosol
optical thickness; **RT** radiative transfer; **DWT** discrete wavelet transform; **DoG** difference of
Gaussians; **CLAHE** contrast-limited adaptive histogram equalisation; **ADF** auxiliary data file
(private calibration/auxiliary input).

---

## <4> Algorithm overview

### <4.1> Processing chain and product breakpoints

`msi-processor` is a sequence of EOPF CPM `EOProcessingUnit`s, each a thin adapter over a pure
algorithmic core (REQ-D-03). The chain and its level breakpoints:

```
L0c ──[decode/loss/assemble]──► L1A ──[dark/PRNU/BPR ▸ (denoise) ▸ MTFC ▸ DN→TOA]──► L1B
    ──[band co-reg ▸ georef/ortho ▸ (pan-sharpen)]──► L1C ──[atm. correction ▸ scene class/masks]──► L2A
```

Stages in parentheses are profile-toggleable: **denoise** (<5.4>) is sensor-profile-configurable and
**pan-sharpen** (<5.9>) is optional. **MTF compensation (MTFC / PSF deconvolution, <5.5>) is a mandatory
Level-1 image-quality step and always runs**, so the enhancement stage is mandatory. The chain is
sensor-agnostic: every instrument constant — band set and centre wavelengths, detector/focal-plane
geometry, calibration-ADF bindings, ESUN, viewing model, output CRS/grid, filter parameters — is
supplied by the active profile (REQ-AD-01), never hard-coded in the core (REQ-D-04).

### <4.2> Common notation

| Symbol | Meaning |
|---|---|
| $b$ | spectral band index |
| $l, d$ | along-track line index, across-track detector (column) index in focal-plane geometry |
| $\mathrm{DN}_{l,d}^{(b)}$ | raw digital number at line $l$, detector $d$, band $b$ |
| $L^{(b)}$ | at-sensor (TOA) spectral radiance, band $b$ [W m⁻² sr⁻¹ µm⁻¹] |
| $\rho_{\mathrm{TOA}}^{(b)},\ \rho_{\mathrm{BOA}}^{(b)}$ | TOA / surface (BOA) reflectance, band $b$ [unitless] |
| $g_d^{(b)},\ o_d^{(b)}$ | per-detector NUC gain / offset (PRNU/DSNU correction) |
| $g^{\mathrm{rad},(b)},\ o^{\mathrm{rad},(b)}$ | radiometric (radiance) gain / offset from the calibration ADF |
| $k^{(b)}$ | per-band dark-offset term |
| $E_{\mathrm{SUN}}^{(b)}$ | band-integrated exo-atmospheric solar irradiance (profile) |
| $\theta_s,\ \theta_v,\ \phi$ | solar zenith, view zenith, relative azimuth |
| $d_{\mathrm{ES}}$ | Earth–Sun distance [AU] |
| $N_{\mathrm{bit}}$ | sensor radiometric depth; valid DN range $[0,\,2^{N_{\mathrm{bit}}}-1]$ (heritage RD-10: $N_{\mathrm{bit}}=12$) |
| $\mathcal F,\ \mathcal F^{-1}$ | forward / inverse 2-D Fourier transform |
| $H$ | $3\times3$ projective homography matrix |
| $\mu,\ R_\oplus$ | Earth gravitational parameter, mean Earth radius |

### <4.3> Common conventions

- **Dynamic-range clipping.** Every stage that can over/under-shoot clips to the valid range
  $[0,\,2^{N_{\mathrm{bit}}}-1]$ and records saturated/no-data pixels in the QA layer (REQ-F-RAD-04,
  REQ-D-05). $N_{\mathrm{bit}}$ is a profile parameter.
- **Float precision.** Intermediate arithmetic is in IEEE-754 `float32` (heritage uses `np.float32`);
  outputs are cast to the profile dtype after clipping. Deterministic operation order is required for
  reproducibility (REQ-F-DEP-02, REQ-D-05).
- **QA propagation.** Per-pixel flags (saturation, defective, no-data, lost-packet, cloud,
  cloud-shadow) accumulate monotonically through stages (REQ-F-QA-02); a flagged input pixel remains
  flagged downstream.
- **Focal-plane vs map geometry.** Stages <5.1>–<5.5> operate in **instrument (focal-plane)**
  geometry; <5.6>–<5.7> move the data to a **cartographic grid**; <5.8>–<5.9> operate on that grid.

---

## <5> Per-stage algorithm basis

### <5.1> L0 decoding, loss handling and assembly

**Purpose.** Convert the consolidated downlinked Level-0 (`L0c`) stream into per-band, per-detector
sample arrays in focal-plane geometry, detect and handle telemetry loss, and assemble a self-describing
`L1A` product. (Heritage: `level_0.py` `Decoder.decode`, `lost_package`.)

**Theoretical background.** A pushbroom MSI builds an image one across-track *line* at a time as the
platform advances; the downlink is a stream of source packets carrying detector samples plus ancillary
telemetry (timing, instrument mode, orbit/attitude). Decoding inverts the on-board
packetisation/encoding to reconstruct, for each band $b$, the 2-D array $\mathrm{DN}^{(b)}_{l,d}$ with
$l$ the along-track line and $d$ the detector index. The bit-level packet format is sensor- and
NDA-specific; in the heritage it is intentionally abstracted (`Decoder.decode` returns a placeholder).
In `msi-processor` it is realised per profile.

**Governing algorithm.**

- **`ALG-L0-DEC` (decode/reformat).** A profile-bound codec maps source packets to
  $\{\mathrm{DN}^{(b)}_{l,d}\}$. Band $b$ with a higher native resolution (heritage: the panchromatic
  band, index 6, sampled at $2\times$) is reconstructed on its own grid; the detector/focal-plane
  layout (line order, flips) is applied from the profile so that $(l,d)$ is consistent across bands.
- **`ALG-L0-LOSS` (line/packet-loss detection).** A line $l$ is declared the start of a lost segment
  when a non-empty line is immediately followed by an all-zero line:

$$
\text{loss at } l+1 \iff \big(\exists d:\ \mathrm{DN}^{(b)}_{l,d}\neq 0\big)\ \wedge\ \big(\forall d:\ \mathrm{DN}^{(b)}_{l+1,d}=0\big).
$$

  Let $l^\star=\min\{\text{loss starts}\}$. The affected tail is removed deterministically,

$$
\mathrm{DN}^{(b)} \leftarrow \mathrm{DN}^{(b)}_{0:\,l^\star\cdot s_b,\ :},\qquad
s_b=\begin{cases}2 & b \text{ at } 2\times \text{ resolution}\\ 1 & \text{otherwise,}\end{cases}
$$

  the $s_b$ factor keeping the higher-resolution band's truncation co-registered with the others. The
  loss is recorded in the QA layer and processing report (REQ-F-L0-02).
- **Assembly.** Decoded bands plus required telemetry are packed into the `L1A` `EOProduct`; legality
  checks reject/flag malformed inputs *before* radiometric processing (REQ-F-L0-03).

**Inputs.** `L0c` product (image source data + ancillary telemetry); active profile (codec binding,
focal-plane layout, per-band resolution factor $s_b$). No calibration ADF at this stage.

**Parameters.** Profile: codec/format id, band list, $s_b$ per band, line/flip orientation, legality
thresholds. The input is treated **read-only** (REQ-F-L0-05).

**Assumptions & limitations.** (i) `L0c` is decompressed and source-packet-reassembled upstream
(SSS A-1). (ii) Loss detection assumes lost lines are zero-filled; partially corrupted (non-zero)
lines are not caught by `ALG-L0-LOSS` and are an **open point** (richer CRC/sequence-counter checks to
be specified in the DPM). (iii) Truncation discards from the first loss to end-of-strip; gap-preserving
handling is out of scope at PDR.

*Trace:* REQ-F-L0-01..05, SYS-CAP-01.

---

### <5.2> Non-uniformity correction — dark/offset, PRNU, bad-pixel replacement

**Purpose.** Turn raw detector samples into a uniform, defect-free detector response by removing the
dark signal, equalising detector-to-detector gain (flat-field / PRNU), and repairing defective
detectors. (Heritage: `level_1.py` `NUC.compute_nuc`, `apply_nuc_and_bpr`, `noise_remover`.)

**Theoretical background.** Each detector $d$ of a pushbroom array has its own radiometric transfer
$\mathrm{DN}_d = a_d\,\Phi + c_d + n_d$, with photo-response slope $a_d$ (PRNU), dark/offset term $c_d$
(DSNU) and noise $n_d$. Left uncorrected, the per-detector spread of $(a_d,c_d)$ appears as fixed
along-track **striping**. NUC estimates a per-detector affine correction $(g_d,o_d)$ from a **dark
acquisition** $D$ (uniform zero illumination → isolates $c_d$) and a **flat-field acquisition** $F$
(uniform illumination → isolates $a_d$), so that all detectors map to the common array mean — a
combined flat-field + offset normalisation (the heritage performs flat-fielding and NUC simultaneously
and labels the pair "NUC").

**Governing equations.**

- **`ALG-RAD-NUC` (gain/offset estimation).** From dark and flat frames, reduce to per-detector
  column means (averaging out along-track noise),

$$
\bar D_d=\frac{1}{L}\sum_{l} D_{l,d},\qquad \bar F_d=\frac{1}{L}\sum_{l} F_{l,d},
$$

  with array means $\mu_D=\langle\bar D_d\rangle_d$, $\mu_F=\langle\bar F_d\rangle_d$. The
  normalising gain and offset are

$$
\boxed{\,g_d=\dfrac{\mu_F-\mu_D}{\bar F_d-\bar D_d}\,},\qquad
\boxed{\,o_d=\mu_F-g_d\,\bar F_d\,}.
$$

  This maps each detector's flat response to $\mu_F$ and its dark to $\mu_D$, removing PRNU and DSNU in
  one affine step.
- **`ALG-RAD-DARK` + application.** The corrected detector value applies the per-detector affine plus a
  per-band dark-offset term $k^{(b)}$ from the calibration ADF:

$$
\boxed{\,X^{(b)}_{l,d}=\mathrm{DN}^{(b)}_{l,d}\,g^{(b)}_d+o^{(b)}_d-k^{(b)}\,}.
$$

- **`ALG-RAD-BPR` (bad-pixel detection & replacement).** A detector is *bad* if it is listed in the
  bad-pixel-map ADF or if its gain falls outside admissible bounds,

$$
\text{bad}(d)\iff g_d\ge g_{\max}\ \vee\ g_d\le g_{\min}.
$$

  Heritage option: substitute $g_d,o_d$ of bad detectors by the array means before application. The
  applied-domain repair is **across-track neighbour interpolation**:

$$
X_{:,d}\leftarrow
\begin{cases}
X_{:,d_{\text{next valid}}}, & d=0,\\[2pt]
X_{:,d-1}, & d \text{ and } d{+}1 \text{ both bad},\\[2pt]
\tfrac12\big(X_{:,d-1}+X_{:,d+1}\big), & d \text{ bad, } d{+}1 \text{ valid},\\[2pt]
X_{:,d-1}, & d=N_d-1,
\end{cases}
$$

  every replaced detector being flagged in the QA layer (REQ-F-RAD-03).
- **`ALG-RAD-SAT` (saturation/no-data).** After correction, values are clipped to
  $[0,2^{N_{\mathrm{bit}}}-1]$ and out-of-range / no-data samples flagged (REQ-F-RAD-04).

**Inputs.** `L1A` product; **ADFs**: dark/offset reference $D$, flat-field/PRNU reference $F$ (or a
pre-computed per-detector $g_d,o_d$ table), per-band dark-offset $k^{(b)}$, bad-pixel map; profile
thresholds $g_{\min},g_{\max}$. A calibration-support mode (`ALG-RAD-NUC` run on dedicated dark+flat
acquisitions) can emit a versioned NUC ADF (REQ-F-RAD-05).

**Parameters.** $g_{\min},g_{\max}$ (bad-pixel bounds), edge-cut rows for dark/flat alignment,
$N_{\mathrm{bit}}$, optional pre-NUC noise removal toggle.

**Assumptions & limitations.** (i) Linear detector response over the working range; non-linearity is
not modelled at PDR (open point — quadratic term candidate). (ii) Dark and flat are valid for the
acquisition's instrument mode/temperature; mismatch is rejected/flagged (REQ-S-04). (iii) Column-mean
reduction assumes the non-uniformity is dominated by the per-detector (across-track) component, which
holds for pushbroom arrays. (iv) Neighbour interpolation degrades when adjacent detectors are
simultaneously bad (clusters); the QA flag records this.

*Trace:* REQ-F-RAD-01..05, SYS-CAP-02.

---

### <5.3> TOA radiance and reflectance

**Purpose.** Convert corrected DN to physical at-sensor (TOA) spectral radiance and, optionally, to TOA
reflectance; emit the `L1B` product. (Heritage: `level_1.py` `TOA.dn_to_radiance`, `get_ESUN`,
`get_sun_el_esdist`, `toa_rad_to_ref`.)

**Theoretical background.** Detector DN is linear in incident at-sensor radiance through the
radiometric calibration $(g^{\mathrm{rad}},o^{\mathrm{rad}})$ established by on-ground / vicarious
calibration. Reflectance normalises radiance by the incoming solar irradiance and illumination
geometry, removing the solar spectrum and sun-angle/season dependence so that bands and acquisitions
are comparable.

**Governing equations.**

- **`ALG-TOA-RAD` (DN → radiance).** Linear inversion of the radiometric model:

$$
\boxed{\,L^{(b)}_{l,d}=\big(\mathrm{DN}^{(b)}_{l,d}-o^{\mathrm{rad},(b)}\big)\,g^{\mathrm{rad},(b)}\,}.
$$

  ($g^{\mathrm{rad}},o^{\mathrm{rad}}$ may be per-detector or per-band, per the calibration ADF.)
  Results are clipped to the valid range and flagged on overflow.
- **`ALG-TOA-REF` (radiance → TOA reflectance).** The canonical normalisation:

$$
\boxed{\,\rho^{(b)}_{\mathrm{TOA}}=\dfrac{\pi\,L^{(b)}\,d_{\mathrm{ES}}^{\,2}}{E^{(b)}_{\mathrm{SUN}}\,\cos\theta_s}\,},
$$

  with $E^{(b)}_{\mathrm{SUN}}$ the band-integrated solar irradiance (profile), $d_{\mathrm{ES}}$ the
  Earth–Sun distance in AU at acquisition, and $\theta_s$ the **solar** zenith angle. $d_{\mathrm{ES}}$
  follows from the day-of-year,

$$
d_{\mathrm{ES}}\approx 1-0.01672\cos\!\big(0.9856^\circ\,(\mathrm{DOY}-4)\big),
$$

  or from a solar ephemeris; $\theta_s$ is computed from the acquisition time and sub-point via a solar
  ephemeris.

**Inputs.** Radiometrically corrected detector array (from <5.2>); **ADF**: radiometric gain/offset;
profile: $E^{(b)}_{\mathrm{SUN}}$ per band, illumination-geometry source (solar zenith, Earth–Sun
distance), $N_{\mathrm{bit}}$.

**Parameters.** Reflectance toggle (optional stage, REQ-F-TOA-02); per-band ESUN; geometry source.

**Assumptions & limitations.** (i) The radiometric response is linear and stable for the calibration
validity window. (ii) **Heritage simplifications corrected here, flagged as open points:** the
prior-work code (a) subtracts the per-image minimum (`radiance -= radiance.min()`) before casting —
this is *not* radiometrically rigorous and is **dropped** from the canonical model (kept only as an
optional cosmetic display transform, never on the physical product); and (b) derived the "sun
elevation" from the satellite sub-point rather than from a solar ephemeris — `msi-processor` uses a
proper solar-geometry computation for $\theta_s$. (iii) ESUN values are sensor-specific and supplied by
the profile (the heritage hard-coded table is **not** carried over, per REQ-AD-01 / data policy).

*Trace:* REQ-F-TOA-01..03, SYS-CAP-02, SYS-CAP-03.

---

### <5.4> Image-quality enhancement — denoising

**Purpose.** Suppress sensor/acquisition noise (read noise, dark-current patterns, periodic/striping
artefacts) without compromising radiometric integrity. This is a **sensor-profile-configurable**
sub-step of the mandatory enhancement stage (it may be enabled/disabled per sensor; the stage still runs
because MTF compensation, <5.5>, is mandatory). (Heritage:
`level_1.py` `Denoiser` — Butterworth LP, wavelet VisuShrink, PCA, moving-average, Gaussian, FFT
dark-noise removal.)

**Theoretical background.** Noise is separated from signal either in the **frequency domain** (noise
concentrated at high/specific frequencies → low-pass / notch filtering), in a **multiresolution basis**
(noise spread across small wavelet coefficients → shrinkage), in a **statistical subspace** (signal in
the leading principal components → PCA truncation), or in the **spatial domain** (local averaging). The
processor offers a menu; the profile selects the method validated for the active sensor and may disable
this denoise sub-step where not validated — the enhancement stage still runs because MTF compensation
(<5.5>) is mandatory (REQ-F-ENH-03).

**Governing equations.**

- **`ALG-ENH-BWLP` (Butterworth low-pass).** Frequency-domain attenuation with maximally-flat
  passband. Two equivalent forms are supported. The library form (squared Butterworth):

$$
|H(f)|^2=\dfrac{1}{1+(f/f_c)^{2n}},
$$

  with $f_c$ the cutoff-frequency ratio and $n$ the order. The explicit radial form used in the
  heritage notch/LP implementation,

$$
H(u,v)=\dfrac{1}{1+(\sqrt{2}-1)\,\big(D(u,v)/D_0\big)^{2n}},\qquad
D(u,v)=\sqrt{(u-u_c)^2+(v-v_c)^2},
$$

  is calibrated so that $|H|=1/\sqrt2$ (i.e. $-3$ dB) exactly at $D=D_0$ (the $(\sqrt2-1)$ factor).
  Filtering: $\hat I=\mathcal F^{-1}\{H\cdot\mathcal F\{I\}\}$, real part retained, clipped.
- **`ALG-ENH-WAVE` (wavelet VisuShrink).** DWT (heritage: Daubechies `db3`, soft mode, up to 20
  levels), soft-threshold the detail coefficients, inverse DWT. Universal threshold and soft operator:

$$
\lambda=\hat\sigma\sqrt{2\ln M},\qquad
\eta_\lambda(w)=\operatorname{sgn}(w)\,\max(|w|-\lambda,\,0),
$$

  with $M$ the number of coefficients and the noise level $\hat\sigma$ estimated robustly from the
  finest detail band, $\hat\sigma=\operatorname{median}(|w_{HH}|)/0.6745$ (heritage scales the estimate
  by $1/3$ to under-shrink and preserve detail).
- **`ALG-ENH-PCA` (PCA denoising).** With per-row (or per-tile) mean $\bar I$ and the leading $k$
  principal directions $V_k$,

$$
\hat I=\bar I+(I-\bar I)\,V_kV_k^{\!\top},
$$

  discarding low-variance components assumed noise-dominated.
- **`ALG-ENH-MA` (moving average).** Along-track $(2N+1)$-line mean,

$$
\hat I_{l,d}=\frac{1}{2N+1}\sum_{j=-N}^{N} I_{l+j,d}.
$$

- **`ALG-ENH-GAUSS` (Gaussian smoothing).** Convolution with an isotropic Gaussian (heritage: $5\times5$,
  $\sigma=\operatorname{std}(I)$):

$$
G(x,y)=\frac{1}{2\pi\sigma^2}\exp\!\Big(-\frac{x^2+y^2}{2\sigma^2}\Big),\qquad \hat I=I*G.
$$

- **`ALG-ENH-FFTDARK` (FFT dark-noise removal).** Frequency-domain subtraction of a co-registered dark
  reference $D$:

$$
\hat I=\Re\big\{\mathcal F^{-1}\big(\mathcal F(I)-\mathcal F(D)\big)\big\}=I-D,
$$

  the equality holding by linearity of $\mathcal F$ (so this is equivalent to spatial dark subtraction;
  the FFT route is retained where a frequency-selective dark notch is desired).

**Inputs.** Corrected band(s); profile: method selection and parameters; for `ALG-ENH-FFTDARK` a dark
reference ADF.

**Parameters.** Per method: $f_c,n$ (Butterworth, `D0`); wavelet family/levels/mode and $\hat\sigma$
scaling; $k$ (PCA); $N$ (moving average); $\sigma$/kernel (Gaussian). All per-band-overridable.

**Assumptions & limitations.** (i) Denoising trades resolution/radiometry for noise reduction; its
radiometric impact is quantified by QA metrics (REQ-F-ENH-03, <5.10>). (ii) This denoise sub-step is
**sensor-profile-configurable** (enabled/disabled per sensor); the enhancement stage itself is mandatory
because MTF compensation (<5.5>) always runs. (iii) The heritage moving-average implementation reduces a row block
to a scalar mean; `msi-processor` adopts the canonical $(2N+1)$ sliding mean above. (iv) Global
frequency filters can introduce ringing near strong edges (Gibbs) — mitigated by padding (`npad`).

*Trace:* REQ-F-ENH-01, REQ-F-ENH-03, SYS-CAP-02.

---

### <5.5> Image-quality enhancement — MTF compensation (MTFC) via PSF deconvolution

> **Change note (CR):** this sub-step is **MTF Compensation (MTFC)** — a **mandatory**, critical
> Level-1 image-quality restoration step (formerly framed as optional "sharpening"). It materially
> affects radiometric and spatial product quality and therefore **always runs**.

**Purpose.** Recover the high-spatial-frequency scene content attenuated by the end-to-end instrument
**Modulation Transfer Function (MTF)** — optics, detector footprint/sampling and platform-motion smear —
by deconvolving the system **point-spread function (PSF)**, per band. This is a **mandatory** Level-1
restoration step (not optional): the as-acquired image is MTF-degraded, so MTFC is required to meet the
spatial-resolution and radiometric-fidelity specification of the L1 product. (Heritage: `level_1.py`
`sharpening.deconvolution_kernel`; product naming indicates **Wiener deconvolution**.)

**Theoretical background.** A linear shift-invariant (LSI) imaging chain forms the acquired image as the
convolution of the true at-aperture scene $f$ with the system PSF $h$ plus noise $n$:

$$
g = h * f + n,\qquad \text{equivalently}\qquad G(u,v)=H(u,v)\,F(u,v)+N(u,v),
$$

where $H=\mathcal F\{h\}$ is the **optical/system transfer function (OTF)** and the **MTF** is its
modulus, $\mathrm{MTF}(u,v)=|H(u,v)|$. The system MTF factorises into the component MTFs,

$$
\mathrm{MTF}_{\mathrm{sys}}=\mathrm{MTF}_{\mathrm{opt}}\cdot\mathrm{MTF}_{\mathrm{det}}\cdot\mathrm{MTF}_{\mathrm{smear}}\cdot\ldots,
$$

(diffraction-limited optics, detector spatial integration $\operatorname{sinc}$, and along-track motion
smear being the dominant terms for a pushbroom MSI). Because $\mathrm{MTF}<1$ at non-zero frequency, the
instrument attenuates fine detail; **MTFC restores** it by an (approximate, regularised) inversion of
$h$. Naive inverse filtering $\hat F=G/H$ amplifies noise wherever $H\!\to\!0$, so a regularised
restoration is mandatory.

**Governing algorithm.**

- **`ALG-ENH-DECONV` (MTF compensation / PSF deconvolution).** The mandatory restoration. The reference
  (heritage) realisation applies a pre-computed, profile-bound spatial **deconvolution kernel** $k$ —
  derived offline from the sensor PSF/MTF so that $k\approx\mathcal F^{-1}\{1/H\}$ regularised — by
  convolution,

$$
\hat I = I * k\qquad(\text{heritage: } \texttt{cv2.filter2D}),
$$

  with a separate, broader kernel for the higher-resolution (panchromatic) band; the result is clipped
  to $[0,2^{N_{\mathrm{bit}}}-1]$. The kernel is the spatial-domain image of one of the following
  candidate restoration filters (down-selected per sensor in the DPM, RD-6):

  - **Wiener (parametric) deconvolution** — regularises by the noise-to-signal ratio $K=S_n/S_f$:

$$
\hat F(u,v)=\dfrac{H^{*}(u,v)}{|H(u,v)|^2+K}\,G(u,v),\qquad \hat I=\Re\{\mathcal F^{-1}\{\hat F\}\}.
$$

  - **Constrained inverse / Tikhonov MTF compensation** — a regularised inverse boosted only up to a
    frequency/gain cap, $\hat F = \big(H^{*}/(|H|^2+\gamma|C|^2)\big)\,G$ with smoothness operator $C$
    and weight $\gamma$, to avoid noise blow-up where the MTF is small.
  - **Richardson–Lucy deconvolution** — iterative, non-negativity-preserving maximum-likelihood
    restoration for a Poisson noise model:

$$
f^{(t+1)}=f^{(t)}\cdot\left[h^{\!*}*\dfrac{g}{h*f^{(t)}}\right],
$$

    with $h^{\!*}$ the flipped PSF; the iteration count trades restoration sharpness against noise
    amplification.

**Inputs.** Corrected/denoised band(s); **ADF**: per-band **PSF / MTF** characterisation — the
PSF-derived deconvolution kernel $k$, or, in full-deconvolution mode, the PSF $h$ / sampled MTF and the
noise-to-signal ratio $K$; profile binding of kernel/PSF and of the higher-resolution (panchromatic)
band.

**Parameters.** Per-band PSF/MTF and derived kernel; regularisation / NSR $K$ (Wiener) or Tikhonov
weight $\gamma$; iteration count (Richardson–Lucy); panchromatic-band kernel; restoration-gain /
frequency cap (anti noise-boost).

**Assumptions & limitations.** (i) Spatially invariant PSF over the band/tile (LSI assumption);
field-dependent (across-swath) PSF variation is an open point (tile-wise kernels candidate). (ii) The
PSF/MTF and kernel are sensor-specific and supplied by the profile/ADF (heritage kernels are NDA
placeholders, not carried over). (iii) MTFC is **mandatory** but **bounded**: the restoration gain is
capped and its radiometric/noise impact is quantified by QA metrics (<5.10>) and held within the
`RAD_ACC` budget, since over-restoration amplifies noise and can bias radiometry. (iv) The denoise
sub-step (<5.4>) is normally ordered with MTFC so the restoration does not amplify residual noise.

*Trace:* REQ-F-ENH-02, REQ-F-ENH-03, SYS-CAP-02.

---

### <5.6> Inter-band co-registration

**Purpose.** Spatially align the spectral bands to a profile-defined reference band so a pixel maps to
the same ground location across bands. (Heritage: `band_coreg.py` — CLAHE → SIFT → FLANN → RANSAC
homography → `warpPerspective`.)

**Theoretical background.** Spectral bands of a pushbroom MSI are offset by detector layout on the focal
plane and by band-dependent acquisition timing, producing inter-band misregistration. Co-registration
estimates a geometric transform per band from automatically matched tie points and resamples the band
onto the reference grid. A **feature-based** pipeline is robust to radiometric differences between
bands: contrast is normalised, scale/rotation-invariant keypoints are matched, and a robust estimator
rejects outliers.

**Governing algorithm.**

- **`ALG-COR-FEAT` (feature detection & matching).** Each band is normalised to 8-bit and contrast-
  enhanced by **CLAHE** (heritage: clip limit 2.0, $8\times8$ tiles) so SIFT responds consistently
  across bands. **SIFT** keypoints are scale-space DoG extrema; for each keypoint a 128-D
  gradient-orientation descriptor is computed. Descriptors of band $b$ are matched to the reference band
  by nearest neighbour (**FLANN**); matches are sorted by descriptor distance and the best fraction
  retained (heritage: top 10%).
- **`ALG-COR-HOM` (robust transform estimation).** A $3\times3$ projective **homography** relates
  reference $(x',y')$ and band $(x,y)$ tie points in homogeneous coordinates,

$$
\begin{bmatrix}x'\\y'\\1\end{bmatrix}\sim H\begin{bmatrix}x\\y\\1\end{bmatrix},\qquad
x'=\frac{h_{11}x+h_{12}y+h_{13}}{h_{31}x+h_{32}y+h_{33}},\quad
y'=\frac{h_{21}x+h_{22}y+h_{23}}{h_{31}x+h_{32}y+h_{33}}.
$$

  $H$ is estimated with **RANSAC** (heritage: reprojection-inlier threshold $\tau=5$ px): iteratively
  fit $H$ on minimal random samples, score by the inlier count
  $\#\{i:\|x'_i-H x_i\|<\tau\}$, keep the maximal-consensus model, refine on its inliers.
- **`ALG-COR-WARP` (resampling).** The band is warped to the reference grid,
  $I^{\mathrm{reg}}_b(x',y')=I_b\big(H^{-1}(x',y')\big)$ (heritage: `warpPerspective`), and the stack is
  cropped to the common valid extent.

**Inputs.** `L1B` bands; profile: reference band, CLAHE/SIFT/FLANN parameters, match fraction,
RANSAC threshold $\tau$, acceptance thresholds.

**Parameters.** Reference-band id (heritage: blue, `b2`); CLAHE clip/tile; SIFT contrast/edge
thresholds; match fraction; $\tau$; minimum inliers / maximum residual for acceptance.

**Assumptions & limitations.** (i) A homography is exact only for planar scenes or pure
camera-rotation; residual parallax over high relief requires the DEM-based ortho of <5.7> — co-reg here
removes the bulk inter-band shift, ortho removes terrain-induced residuals. (ii) Feature matching
needs sufficient texture; on insufficient/failed matches the band is flagged and the fail-stop policy
applies rather than emitting a misregistered product (REQ-F-COR-03). (iii) The residual must meet the
per-profile `BAND_COREG` budget, validated locally (REQ-F-COR-02).

*Trace:* REQ-F-COR-01..03, SYS-CAP-04, SYS-CAP-05.

---

### <5.7> Geo-referencing and orthorectification

**Purpose.** Assign each pixel a ground coordinate using the viewing/geometric model and orbit/attitude,
refine with GCPs, orthorectify with a DEM, and resample to the profile cartographic grid/CRS; emit the
`L1C` product. (Heritage: `georeferencing_v1.py` — TLE sub-point, GSD, GCP/reference matching, GDAL/
`osr` CRS, georeferenced output.)

**Theoretical background.** Geolocation maps focal-plane $(l,d)$ to ground $(X,Y,Z)$ through the
platform position/attitude (from orbit propagation + attitude telemetry) and the line-of-sight model of
each detector. Terrain relief displaces the apparent position of off-nadir pixels; orthorectification
removes this by intersecting each line-of-sight with the DEM. Absolute accuracy is improved by tying
the image to ground control (GCP chips or a reference image).

**Governing equations.**

- **`ALG-GEO-ORBIT` (orbit/platform state).** The TLE is propagated (SGP4) to the acquisition time to
  give the sub-satellite point (lat, lon) and altitude $H$. For a near-circular orbit the kinematics
  used for line timing/GSD are

$$
v=\sqrt{\dfrac{\mu}{R_\oplus+H}},\qquad
\omega=\dfrac{v}{R_\oplus+H},\qquad
v_{g}=R_\oplus\,\omega,
$$

  with $v$ orbital speed, $\omega$ angular rate, $v_g$ ground-track velocity.
- **`ALG-GEO-GSD` (ground sampling distance).** From the pinhole relation with detector pitch $p$ and
  focal length $f$,

$$
\boxed{\,\mathrm{GSD}=\dfrac{H\,p}{f}\,}.
$$

- **`ALG-GEO-GCP` (ground-control refinement).** Tie points between the image and a geolocated reference
  (heritage: a Sentinel-2 band) are found by the same `ALG-COR-FEAT`/`ALG-COR-HOM` pipeline
  (CLAHE→SIFT→FLANN→RANSAC homography), yielding a planimetric correction that registers the image to
  the reference CRS.
- **`ALG-GEO-ORTHO` (orthorectification).** The rigorous target model intersects each detector
  line-of-sight with the DEM via the collinearity relation: for ground point $\mathbf X=(X,Y,Z)$,
  platform position $\mathbf X_0$, attitude rotation $R(\omega,\varphi,\kappa)$ and interior geometry,

$$
\begin{bmatrix}x\\y\\-f\end{bmatrix}=\lambda\,R^{\!\top}\big(\mathbf X-\mathbf X_0\big),\qquad Z=\mathrm{DEM}(X,Y),
$$

  solved per pixel so terrain-induced displacement is removed. The PDR heritage realises a 2-D
  reference-image homography as a first approximation; the full DEM-based collinearity model is the CDR
  target (open point).
- **`ALG-GEO-RESAMP` (grid/CRS resampling).** Output samples lie on the profile cartographic grid via
  the GDAL affine geotransform

$$
\begin{bmatrix}X\\Y\end{bmatrix}=\begin{bmatrix}X_0\\Y_0\end{bmatrix}+\begin{bmatrix}p_x & r_1\\ r_2 & -p_y\end{bmatrix}\begin{bmatrix}c\\r\end{bmatrix},
$$

  ($c,r$ column/row; $p_x,p_y$ pixel size; $r_1,r_2$ rotation, zero for north-up), with the CRS set from
  the profile/reference and coordinates transformed by PROJ/`osr`; resampling kernel (nearest/bilinear/
  cubic) per profile.

**Inputs.** Co-registered `L1B`; **ADFs**: viewing/geometric model, DEM, GCP/reference; profile: output
CRS, grid, resolution, resampling method; orbit/attitude telemetry from `L1A`.

**Parameters.** $p,f$ (interior geometry); resampling method; GCP match/RANSAC parameters and $\tau$;
target CRS/grid/GSD.

**Assumptions & limitations.** (i) DEM and reference coverage exist for the footprint/epoch (SSS A-5).
(ii) The heritage uses constants and a reference-image homography as a stand-in for the rigorous sensor
model and a static target GSD; the rigorous orbit+attitude+DEM collinearity model is the CDR target.
(iii) Geolocation must meet the per-profile `GEO_CE90` budget, validated locally against ground
reference (REQ-F-GEO-03). (iv) Attitude/timing telemetry quality bounds achievable accuracy.

*Trace:* REQ-F-GEO-01..04, SYS-CAP-04, SYS-CAP-05.

---

### <5.8> Atmospheric correction (L1C → L2A) — **new / to-be-defined**

**Purpose.** Remove atmospheric scattering/absorption to derive bottom-of-atmosphere (surface)
reflectance and classify the scene (incl. cloud/cloud-shadow masks); emit the `L2A` product. **This
stage has no prior-work heritage** (`toa_rad_to_ref` in RD-10 is a stub); it is specified here at the
theoretical level and its concrete algorithm/implementation is **to be defined** in the DPM before CDR.

**Theoretical background.** The TOA reflectance observed over a Lambertian surface of reflectance
$\rho_s$ is, after Vermote/6S (EX-1), the sum of atmospheric path reflectance plus the surface
contribution attenuated by two-way transmittance and amplified by atmosphere–surface multiple
scattering:

$$
\rho_{\mathrm{TOA}}(\theta_s,\theta_v,\phi)=\rho_{\mathrm{atm}}+\dfrac{T(\theta_s)\,T(\theta_v)\,\rho_s}{1-S\,\rho_s},
$$

with $\rho_{\mathrm{atm}}$ path (intrinsic) reflectance, $T(\theta_s),T(\theta_v)$ downward/upward total
transmittances, and $S$ the atmospheric spherical albedo — all functions of band, geometry,
AOT, water vapour, ozone and surface altitude, obtained from an RT model or a pre-computed LUT.

**Governing equations (candidate).**

- **`ALG-ATM-PAR` (parameter ingest/retrieval).** AOT and water vapour are either ingested from
  auxiliary meteorology or retrieved from the imagery (candidate: dark-dense-vegetation inversion for
  AOT; differential band-ratio absorption for water vapour), per the DPM and profile (REQ-F-ATM-01).
- **`ALG-ATM-RT` (TOA → BOA inversion).** Invert the equation above for surface reflectance:

$$
\boxed{\,\rho_{\mathrm{BOA}}=\rho_s=\dfrac{\rho_{\mathrm{TOA}}-\rho_{\mathrm{atm}}}{T(\theta_s)\,T(\theta_v)+S\,(\rho_{\mathrm{TOA}}-\rho_{\mathrm{atm}})}\,},
$$

  with $\{\rho_{\mathrm{atm}},T,S\}$ interpolated from the RT-LUT for the per-pixel geometry, AOT, water
  vapour and DEM altitude (REQ-F-ATM-02).
- **`ALG-ATM-SCM` (scene classification & masks).** A per-pixel classifier (candidate: Sen2Cor-style
  spectral-threshold scene classification) produces a scene-class layer and cloud / cloud-shadow masks
  (REQ-F-ATM-03).

**Candidate realisations (to be down-selected in the DPM).** Py6S / 6SV (rigorous RT), a Sen2Cor-style
LUT + scene classification, or ACOLITE-style dark-spectrum fitting. The selection criteria are
accuracy vs the per-profile `BOA_ACC` budget (REQ-P-03), runtime within `THRU_SCENE`, EOPF/CPM
integration cost, and licence compatibility (SRF).

**Inputs.** `L1C` TOA reflectance; **ADFs/auxiliaries**: AOT, water vapour, ozone, RT-LUT/atmospheric
model parameters, DEM; profile: retrieval-vs-ingest mode, classification options.

**Parameters.** Atmospheric model/LUT id, aerosol model, default/retrieved AOT & water vapour,
classification thresholds.

**Assumptions & limitations.** (i) Lambertian surface and plane-parallel atmosphere (standard 6S
assumptions); BRDF and adjacency effects are not modelled at first baseline. (ii) RT-LUT validity
covers the scene geometry/altitude range. (iii) **Open point:** the entire stage (parameter-retrieval
method, RT engine, classifier) is to be defined and validated in the DPM before CDR; until then it is a
specified interface with a candidate algorithm.

*Trace:* REQ-F-ATM-01..04, SYS-CAP-06, SYS-CAP-07.

---

### <5.9> Pan-sharpening

**Purpose.** Fuse the co-registered multispectral bands with the higher-resolution panchromatic (PAN)
band to produce a high-resolution multispectral product; optional. (Heritage: `pansharp.py`
`PanSharpening.pan_sharpen` — SIFT/FLANN/RANSAC alignment + simple-mean fusion.)

**Theoretical background.** A PAN band offers higher spatial resolution but no spectral discrimination;
the MS bands offer the reverse. Pan-sharpening injects PAN spatial detail into each up-sampled MS band
while aiming to preserve spectral fidelity. The heritage uses a **simple-mean** fusion after geometric
alignment of MS to PAN.

**Governing algorithm.**

- **`ALG-PAN-ALIGN` (MS↔PAN registration).** MS (CLAHE-enhanced) and PAN keypoints are matched
  (SIFT→FLANN→RANSAC homography, threshold 5 px) and the MS stack is warped to the PAN grid
  (`warpPerspective`) — the same `ALG-COR-*` machinery (<5.6>).
- **`ALG-PAN-FUSE` (fusion).** Per band, the heritage fuses by the arithmetic mean of the aligned MS
  band and PAN:

$$
\widehat{\mathrm{MS}}^{(b)}=\tfrac12\big(\mathrm{MS}^{(b)}_{\mathrm{aligned}}+\mathrm{PAN}\big),
$$

  clipped to $[0,2^{N_{\mathrm{bit}}}-1]$. (Higher-fidelity component-substitution / MRA methods —
  Brovey, GS, IHS, à-trous wavelet — are candidate profile options for better spectral preservation.)

**Inputs.** Co-registered MS stack; PAN band; profile: enable flag, fusion method, alignment
parameters.

**Parameters.** Fusion method, alignment/RANSAC parameters, output dtype.

**Assumptions & limitations.** (i) Simple-mean fusion is spectrally lossy (it blends PAN radiometry
into every band); spectral fidelity must meet the per-profile budget and is reported via QA (REQ-F-PAN-02)
— if unmet, a spectral-preserving method is selected. (ii) Requires accurate MS↔PAN registration; poor
alignment produces edge artefacts. (iii) Optional and default-off unless validated for the sensor.

*Trace:* REQ-F-PAN-01..02, SYS-CAP-04.

---

### <5.10> Quality-assurance metrics

**Purpose.** Quantify per-band/per-stage quality and the radiometric impact of processing, for the
processing report and for accuracy verification. (Heritage: `metrics_ips.py` — SNR, RMSE, PSNR, MSE,
variance, `run_validation`.)

**Theoretical background.** Quality is measured either *referentially* (against a reference/input
product: RMSE, MSE, PSNR) or *non-referentially* (from image statistics: SNR, variance). They jointly
bound radiometric fidelity and noise.

**Governing equations.** For a processed image $I$ of $M$ pixels and reference $R$:

- **`ALG-QA-SNR`** (non-referential signal-to-noise, dB):
$$
\mathrm{SNR}=20\log_{10}\!\frac{\bar I}{\sigma_I},\qquad \bar I=\tfrac1M\textstyle\sum I,\ \ \sigma_I=\mathrm{std}(I).
$$
- **`ALG-QA-MSE` / `ALG-QA-RMSE`** (referential error):
$$
\mathrm{MSE}=\frac1M\sum_{i}(I_i-R_i)^2,\qquad \mathrm{RMSE}=\sqrt{\mathrm{MSE}}.
$$
- **`ALG-QA-PSNR`** (peak SNR, dB, peak $=2^{N_{\mathrm{bit}}}-1$):
$$
\mathrm{PSNR}=20\log_{10}\!\frac{2^{N_{\mathrm{bit}}}-1}{\sqrt{\mathrm{MSE}}}\quad(\infty\text{ if }\mathrm{MSE}=0).
$$
- **`ALG-QA-VAR`** (variance, computed for processed and reference):
$$
\mathrm{Var}(I)=\frac1M\sum_i\big(I_i-\bar I\big)^2.
$$

`run_validation` aligns $I$ and $R$ to a common extent, then tabulates all metrics per band in the
processing report.

**Inputs.** Stage input/output products; optional reference/raw product.

**Parameters.** $N_{\mathrm{bit}}$ (PSNR peak); reference selection; per-band reporting.

**Assumptions & limitations.** (i) Referential metrics need a spatially aligned reference of equal
extent (enforced by cropping). (ii) SNR via $\bar I/\sigma_I$ is a scene-content proxy, not a pure
detector-noise figure; it is reported as a relative indicator. (iii) Metrics are diagnostic and carry
no private data, satisfying the report's confidentiality (REQ-HF-02).

*Trace:* REQ-F-QA-01..02, SYS-OBS-02, SYS-OBS-03, SYS-QUA-04.

---

## <6> Numerical conventions and error-budget management

- **Precision & determinism.** All processing is `float32` with a fixed operation order; random
  components (RANSAC) use a profile-fixed seed so that re-runs are bit-identical or within a documented
  tolerance (REQ-F-DEP-02, REQ-D-05).
- **Clipping & flagging.** Every stage clips to $[0,2^{N_{\mathrm{bit}}}-1]$ and flags saturated/no-data
  pixels; flags propagate (REQ-F-QA-02).
- **Error budgets.** The end-to-end accuracy budgets — `RAD_ACC` (radiometric), `BAND_COREG`
  (inter-band), `GEO_CE90` (geolocation), `BOA_ACC` (surface reflectance) — are per-profile parameters
  held privately and verified locally against reference products (REQ-P-01..03, REQ-Q-03). Each stage's
  documented tolerance contributes to the corresponding budget; the consolidated budget allocation is in
  the DPM (RD-6).
- **Sensor-agnosticism.** No equation in this ATBD contains an instrument constant; all coefficients
  ($g,o,k,E_{\mathrm{SUN}},p,f$, kernels, LUTs) are profile/ADF inputs (REQ-AD-01, REQ-D-04).

---

## <7> Traceability — algorithms to requirements

| ATBD algorithm(s) | SRS `REQ-*` | SSS `SYS-*` |
|---|---|---|
| ALG-L0-DEC, ALG-L0-LOSS | REQ-F-L0-01..05 | SYS-CAP-01 |
| ALG-RAD-NUC, ALG-RAD-DARK, ALG-RAD-BPR, ALG-RAD-SAT | REQ-F-RAD-01..05 | SYS-CAP-02 |
| ALG-TOA-RAD, ALG-TOA-REF | REQ-F-TOA-01..03 | SYS-CAP-02, SYS-CAP-03 |
| ALG-ENH-BWLP, -WAVE, -PCA, -MA, -GAUSS, -FFTDARK | REQ-F-ENH-01, REQ-F-ENH-03 | SYS-CAP-02 |
| ALG-ENH-DECONV | REQ-F-ENH-02, REQ-F-ENH-03 | SYS-CAP-02 |
| ALG-COR-FEAT, ALG-COR-HOM, ALG-COR-WARP | REQ-F-COR-01..03 | SYS-CAP-04, SYS-CAP-05 |
| ALG-GEO-ORBIT, -GSD, -GCP, -ORTHO, -RESAMP | REQ-F-GEO-01..04 | SYS-CAP-04, SYS-CAP-05 |
| ALG-ATM-PAR, ALG-ATM-RT, ALG-ATM-SCM | REQ-F-ATM-01..04 | SYS-CAP-06, SYS-CAP-07 |
| ALG-PAN-ALIGN, ALG-PAN-FUSE | REQ-F-PAN-01..02 | SYS-CAP-04 |
| ALG-QA-SNR, -RMSE, -PSNR, -MSE, -VAR | REQ-F-QA-01..02 | SYS-OBS-02/03, SYS-QUA-04 |

Each algorithm thus supports at least one `REQ-*` and its upstream `SYS-*`; the maintained bidirectional
matrix is RD-9 (CDR).

---

## <8> Consolidated assumptions, limitations and open points

**Cross-cutting assumptions.** Linear, stable detector response within calibration validity (<5.2>,
<5.3>); valid, version-matched ADFs per acquisition (REQ-S-04); DEM/atmospheric/reference coverage for
the footprint and epoch (SSS A-2, A-5); reference/cal-val data available locally for the first profile
(SSS A-6).

**Open points to be closed in the DPM (RD-6) before/at CDR:**

1. **Atmospheric correction (<5.8>)** — full stage (parameter retrieval, RT engine, scene classifier)
   to be defined and validated; new development, no heritage.
2. **Rigorous geometric model (<5.7>)** — replace the heritage reference-image homography with the
   orbit+attitude+DEM collinearity model; allocate the `GEO_CE90` budget.
3. **TOA reflectance geometry (<5.3>)** — solar zenith / Earth–Sun distance from a proper solar
   ephemeris (heritage conflated satellite sub-point with solar geometry); drop the non-physical
   per-image minimum subtraction from the radiance product.
4. **L0 loss handling (<5.1>)** — extend beyond zero-line detection to CRC/sequence-counter-based
   corruption detection and gap-preserving handling.
5. **Detector non-linearity (<5.2>)** — assess a non-linear (e.g. quadratic) response term beyond the
   affine NUC.
6. **Pan-sharpening fidelity (<5.9>)** — provide a spectral-preserving fusion option (Brovey / GS / IHS
   / à-trous) where simple-mean does not meet the spectral-fidelity budget.

---

*End of ATBD. Algorithm IDs (`ALG-*`) are this document's controlled identifiers; per-sensor numeric
realisation and budget allocation are in the DPM (RD-6); software behaviour is bound in the SRS (RD-1);
no private calibration data appears here (REQ-S-01).*
