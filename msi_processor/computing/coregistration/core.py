# Copyright 2026 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pure inter-band co-registration core (C-PU-COR; ALG-COR-FEAT/HOM/WARP).

CPM-free, I/O-free functions implementing the feature-based inter-band
alignment of ATBD <5.6>, ported faithfully from the heritage ``band_coreg.py``
(``BandRegister.shifting_sift``; RD-10): each band is 8-bit normalised, contrast
enhanced with **CLAHE**, **SIFT** keypoints/descriptors are detected, matched to
the reference band by **FLANN** with a top-fraction selection, a projective
homography is fitted with **RANSAC**, and the band is warped to the reference
grid with ``warpPerspective`` (ATBD <5.6>; SDD <5.4.6>).

**Library policy — this core uses OpenCV.** Unlike the ``radiometric`` / ``toa``
cores (pure ``numpy``) and the ``enhancement`` core (kernels re-implemented in
``numpy`` to avoid ``scikit-image`` / ``PyWavelets``), the co-registration
algorithms are *defined by* OpenCV primitives in the baselined design — SDD
<5.4.6> states "Reuses cv2" and ATBD <5.6> specifies SIFT / FLANN / RANSAC /
``warpPerspective`` by name. Re-implementing scale-invariant feature detection
in ``numpy`` would be neither faithful nor maintainable, so ``opencv`` is a
genuine runtime dependency of this stage (declared in ``pyproject.toml``; the
headless wheel is used as there is no display in the target/CI runtime).

**Radiometry preservation.** CLAHE / 8-bit normalisation are applied only to a
throw-away *matching surrogate*; the homography is then applied to the **original
radiometric band** (:func:`warp_to_reference`), so the output radiometry is the
input radiometry resampled onto the reference grid — never the contrast-stretched
surrogate.

**Determinism.** RANSAC and the FLANN index draw on OpenCV's global RNG, which is
seeded from :attr:`CoregParams.seed` before every detection/estimation so re-runs
are reproducible (REQ-F-DEP-02; SDD <5.4.6> error-handling note).

Geometry convention: arrays are 2-D ``(line|y, detector|x)``; a homography maps a
band point to the reference point, and ``shape`` is the reference ``(rows, cols)``
(ATBD <4.2>, SDD <5.4.6>).

*Trace:* REQ-F-COR-01..03; DPM-M-COR; ALG-COR-FEAT/HOM/WARP.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional

import cv2
import numpy as np
import numpy.typing as npt

from msi_processor.common.types import QAFlag
from msi_processor.exceptions.errors import CoregistrationError

__all__ = [
    "CoregParams",
    "CoregResidual",
    "detect_and_match",
    "estimate_homography",
    "warp_to_reference",
    "warp_qa",
    "coregister",
]

FloatArray = npt.NDArray[np.float32]
QAArray = npt.NDArray[np.uint16]
HomographyArray = npt.NDArray[np.float64]
PointArray = npt.NDArray[np.float32]

# A projective homography is determined by four point correspondences; RANSAC
# needs at least this many kept matches to fit a candidate model.
_MIN_HOMOGRAPHY_POINTS = 4
_STAGE = "coregistration"


@dataclass(frozen=True)
class CoregParams:
    """Tunable co-registration parameters (SDD <5.4.6>; DPM-PRM-COR-01..04).

    Parameters
    ----------
    reference_band:
        Profile-defined reference band id every other band is aligned to
        (``DPM-PRM-COR-01``; heritage ``"b2"``).
    clahe_clip, clahe_grid:
        CLAHE clip limit and tile grid for the matching surrogate
        (``DPM-PRM-COR-02``; heritage ``2.0`` / ``(8, 8)``).
    match_fraction:
        Fraction of the FLANN matches, sorted by descriptor distance, retained
        as tie points (heritage top ``0.10``).
    min_keypoints, min_keypoints_pan:
        Minimum SIFT keypoints each image must yield for a band to be matched;
        the (typically higher-resolution) panchromatic bands listed in
        :attr:`pan_bands` use ``min_keypoints_pan`` (heritage ``20`` / ``40``).
    pan_bands:
        Band ids treated as panchromatic for the keypoint gate. Empty by default;
        the wrapper populates it from the sensor profile (generic-processor
        extension of the heritage hard-coded ``"b6"`` rule).
    ransac_tau:
        RANSAC reprojection-inlier threshold in pixels (heritage ``5.0``).
    max_residual:
        Acceptance gate on the inlier RMS reprojection residual in pixels
        (``DPM-PRM-COR-04``, the per-profile ``BAND_COREG`` budget, private).
        ``None`` accepts any solution that has enough inliers.
    seed:
        Seed for OpenCV's global RNG (deterministic RANSAC / FLANN,
        REQ-F-DEP-02).
    """

    reference_band: str
    clahe_clip: float = 2.0
    clahe_grid: tuple[int, int] = (8, 8)
    match_fraction: float = 0.10
    min_keypoints: int = 20
    min_keypoints_pan: int = 40
    pan_bands: tuple[str, ...] = ()
    ransac_tau: float = 5.0
    max_residual: Optional[float] = None
    seed: int = 0

    def min_keypoints_for(self, band: str) -> int:
        """Return the keypoint gate for ``band`` (pan-aware)."""
        return self.min_keypoints_pan if band in self.pan_bands else self.min_keypoints


@dataclass(frozen=True)
class CoregResidual:
    """Per-band co-registration outcome (SDD <5.4.6>; ICD-IF-DIAG).

    Parameters
    ----------
    band:
        Band id the residual refers to (``""`` until set by :func:`coregister`).
    n_inliers:
        Number of RANSAC inlier tie points supporting the homography.
    rms_residual_px:
        Root-mean-square inlier reprojection residual in pixels.
    accepted:
        Whether ``rms_residual_px`` met :attr:`CoregParams.max_residual`.
    """

    band: str
    n_inliers: int
    rms_residual_px: float
    accepted: bool


def detect_and_match(
    band: npt.NDArray[Any],
    reference: npt.NDArray[Any],
    params: CoregParams,
    *,
    min_keypoints: Optional[int] = None,
) -> tuple[PointArray, PointArray]:
    r"""ALG-COR-FEAT — CLAHE-enhanced SIFT detection + FLANN top-fraction matching.

    Both images are normalised to 8-bit and CLAHE contrast-enhanced (the
    *matching surrogate* only), SIFT keypoints/descriptors are detected, and the
    band descriptors are matched to the reference by FLANN. Matches are sorted by
    descriptor distance and the best :attr:`CoregParams.match_fraction` retained
    (heritage top 10 %).

    Parameters
    ----------
    band, reference:
        2-D band and reference arrays, ``(line, detector)``.
    params:
        Co-registration parameters.
    min_keypoints:
        Override for the keypoint gate (defaults to
        :attr:`CoregParams.min_keypoints`); :func:`coregister` passes the
        pan-aware value.

    Returns
    -------
    tuple of numpy.ndarray
        ``(src_pts, dst_pts)`` as ``(N, 1, 2)`` ``float32`` correspondences,
        ``src_pts`` in the band frame and ``dst_pts`` in the reference frame.

    Raises
    ------
    CoregistrationError
        If either image yields fewer than ``min_keypoints`` keypoints, or fewer
        than four tie points survive selection (REQ-F-COR-03).
    """
    cv2.setRNGSeed(int(params.seed))
    gate = params.min_keypoints if min_keypoints is None else int(min_keypoints)

    band_surrogate = _clahe(_to_uint8(band), params)
    ref_surrogate = _clahe(_to_uint8(reference), params)

    sift = cv2.SIFT.create()
    kp_band, des_band = sift.detectAndCompute(band_surrogate, None)
    kp_ref, des_ref = sift.detectAndCompute(ref_surrogate, None)

    if des_band is None or des_ref is None or len(kp_band) < gate or len(kp_ref) < gate:
        raise CoregistrationError(
            f"Insufficient SIFT keypoints for co-registration "
            f"(band={len(kp_band)}, reference={len(kp_ref)}, required>={gate})",
            stage=_STAGE,
            qa_flag=int(QAFlag.COREG_FAIL),
            report_fields={"n_keypoints_band": len(kp_band), "n_keypoints_reference": len(kp_ref)},
        )

    matcher = cv2.FlannBasedMatcher()
    matches = sorted(matcher.match(des_band, des_ref), key=lambda m: m.distance)
    n_keep = max(_MIN_HOMOGRAPHY_POINTS, int(round(len(matches) * params.match_fraction)))
    matches = matches[:n_keep]
    if len(matches) < _MIN_HOMOGRAPHY_POINTS:
        raise CoregistrationError(
            f"Too few matches to fit a homography ({len(matches)} < {_MIN_HOMOGRAPHY_POINTS})",
            stage=_STAGE,
            qa_flag=int(QAFlag.COREG_FAIL),
            report_fields={"n_matches": len(matches)},
        )

    src_pts = np.array([kp_band[m.queryIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
    dst_pts = np.array([kp_ref[m.trainIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
    return src_pts, dst_pts


def estimate_homography(
    band: npt.NDArray[Any],
    reference: npt.NDArray[Any],
    params: CoregParams,
    *,
    min_keypoints: Optional[int] = None,
) -> tuple[HomographyArray, CoregResidual]:
    r"""ALG-COR-FEAT+HOM — robust homography from band to reference.

    Calls :func:`detect_and_match` then fits a :math:`3\times3` projective
    homography :math:`H` (band :math:`\to` reference) with **RANSAC** at the
    :attr:`CoregParams.ransac_tau` reprojection threshold, and reports the
    inlier-RMS residual and its acceptance against
    :attr:`CoregParams.max_residual`.

    Returns
    -------
    tuple
        ``(H[float64 3x3], CoregResidual)``; the residual's ``band`` field is
        ``""`` here and filled in by :func:`coregister`.

    Raises
    ------
    CoregistrationError
        On insufficient keypoints/matches (from :func:`detect_and_match`) or if
        RANSAC cannot fit a model with at least four inliers (REQ-F-COR-03). The
        acceptance gate itself is *not* raised here (it is reported via
        :attr:`CoregResidual.accepted`); :func:`coregister` enforces fail-stop.
    """
    src_pts, dst_pts = detect_and_match(band, reference, params, min_keypoints=min_keypoints)

    cv2.setRNGSeed(int(params.seed))
    homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, float(params.ransac_tau))
    if homography is None or mask is None:
        raise CoregistrationError(
            "RANSAC failed to estimate a co-registration homography",
            stage=_STAGE,
            qa_flag=int(QAFlag.COREG_FAIL),
        )

    inliers = np.asarray(mask, dtype=np.uint8).ravel().astype(bool)
    n_inliers = int(inliers.sum())
    if n_inliers < _MIN_HOMOGRAPHY_POINTS:
        raise CoregistrationError(
            f"Too few RANSAC inliers ({n_inliers} < {_MIN_HOMOGRAPHY_POINTS})",
            stage=_STAGE,
            qa_flag=int(QAFlag.COREG_FAIL),
            report_fields={"n_inliers": n_inliers},
        )

    h_matrix = np.asarray(homography, dtype=np.float64)
    rms = _reprojection_rms(src_pts[inliers], dst_pts[inliers], h_matrix)
    accepted = params.max_residual is None or rms <= float(params.max_residual)
    residual = CoregResidual(band="", n_inliers=n_inliers, rms_residual_px=rms, accepted=accepted)
    return h_matrix, residual


def warp_to_reference(
    band: npt.NDArray[Any],
    homography: npt.NDArray[Any],
    shape: tuple[int, int],
) -> npt.NDArray[Any]:
    r"""ALG-COR-WARP — resample a band onto the reference grid.

    :math:`I^{\mathrm{reg}}(x',y') = I\big(H^{-1}(x',y')\big)` via
    ``cv2.warpPerspective`` with bilinear interpolation (heritage). The
    **original radiometric band** is warped (radiometry-preserving up to
    resampling); the input dtype is preserved. Out-of-source pixels are filled
    with ``0`` (their no-data status is recorded in the QA mask by the wrapper).
    """
    rows, cols = int(shape[0]), int(shape[1])
    src = np.asarray(band)
    matrix = np.asarray(homography, dtype=np.float64)
    warped = cv2.warpPerspective(src, matrix, (cols, rows), flags=cv2.INTER_LINEAR)
    return np.asarray(warped, dtype=src.dtype)


def warp_qa(
    qa: npt.NDArray[Any],
    homography: npt.NDArray[Any],
    shape: tuple[int, int],
) -> QAArray:
    """Resample a QA bitmask onto the reference grid (nearest-neighbour).

    Companion to :func:`warp_to_reference` for :class:`QAFlag` masks: bilinear
    interpolation would blend bit patterns into meaningless values, so the mask
    is warped with ``INTER_NEAREST`` to preserve exact flag values. Out-of-source
    pixels become ``0`` (the wrapper ORs :attr:`QAFlag.NO_DATA` there).
    """
    rows, cols = int(shape[0]), int(shape[1])
    mask = np.asarray(qa, dtype=np.uint16)
    matrix = np.asarray(homography, dtype=np.float64)
    warped = cv2.warpPerspective(mask, matrix, (cols, rows), flags=cv2.INTER_NEAREST)
    return np.asarray(warped, dtype=np.uint16)


def coregister(
    bands: Mapping[str, npt.NDArray[Any]],
    params: CoregParams,
) -> tuple[dict[str, npt.NDArray[Any]], list[CoregResidual]]:
    """Co-register every band to the reference band (SDD <5.4.6> pipeline).

    For each non-reference band: estimate the homography, check its residual
    against :attr:`CoregParams.max_residual`, and warp it onto the reference
    grid. The reference band passes through unchanged; the stack therefore shares
    the reference ``(rows, cols)`` extent.

    Parameters
    ----------
    bands:
        Mapping of band id to 2-D array; must contain
        :attr:`CoregParams.reference_band`.
    params:
        Co-registration parameters.

    Returns
    -------
    tuple
        ``(registered, residuals)`` — ``registered`` maps every band id to its
        reference-grid array (reference included); ``residuals`` lists the
        per-(non-reference-)band :class:`CoregResidual` in input order.

    Raises
    ------
    CoregistrationError
        If the reference band is absent, or any band fails the keypoint/match
        gate or its acceptance residual (fail-stop, REQ-F-COR-03) — no
        misregistered stack is returned.
    """
    if params.reference_band not in bands:
        raise CoregistrationError(
            f"Reference band '{params.reference_band}' is not among the inputs",
            stage=_STAGE,
            qa_flag=int(QAFlag.COREG_FAIL),
        )

    reference = np.asarray(bands[params.reference_band])
    ref_shape = (int(reference.shape[0]), int(reference.shape[1]))
    registered: dict[str, npt.NDArray[Any]] = {params.reference_band: reference}
    residuals: list[CoregResidual] = []

    for name, band in bands.items():
        if name == params.reference_band:
            continue
        gate = params.min_keypoints_for(name)
        h_matrix, residual = estimate_homography(band, reference, params, min_keypoints=gate)
        residual = dataclasses.replace(residual, band=name)
        residuals.append(residual)
        if not residual.accepted:
            raise CoregistrationError(
                f"Co-registration residual for band '{name}' "
                f"({residual.rms_residual_px:.3f} px) exceeds acceptance",
                stage=_STAGE,
                qa_flag=int(QAFlag.COREG_FAIL),
                report_fields={"band": name, "rms_residual_px": residual.rms_residual_px},
            )
        registered[name] = warp_to_reference(band, h_matrix, ref_shape)

    return registered, residuals


# --------------------------------------------------------------------------- #
# Private helpers (CPM-free)                                                   #
# --------------------------------------------------------------------------- #


def _to_uint8(image: npt.NDArray[Any]) -> npt.NDArray[np.uint8]:
    """Min-max normalise a band to 8-bit for feature matching (heritage)."""
    img = np.asarray(image, dtype=np.float32)
    lo = float(img.min())
    hi = float(img.max())
    if hi <= lo:
        return np.zeros(img.shape, dtype=np.uint8)
    scaled = (img - lo) / (hi - lo) * 255.0
    return scaled.astype(np.uint8)


def _clahe(image_u8: npt.NDArray[np.uint8], params: CoregParams) -> npt.NDArray[np.uint8]:
    """Apply CLAHE to the 8-bit matching surrogate (heritage clip 2.0 / 8x8)."""
    clahe = cv2.createCLAHE(clipLimit=float(params.clahe_clip), tileGridSize=params.clahe_grid)
    return np.asarray(clahe.apply(image_u8), dtype=np.uint8)


def _reprojection_rms(
    src_pts: npt.NDArray[Any],
    dst_pts: npt.NDArray[Any],
    homography: HomographyArray,
) -> float:
    """Root-mean-square reprojection residual (px) of ``H @ src`` versus ``dst``."""
    src = np.asarray(src_pts, dtype=np.float64).reshape(-1, 2)
    dst = np.asarray(dst_pts, dtype=np.float64).reshape(-1, 2)
    homogeneous = np.hstack([src, np.ones((src.shape[0], 1), dtype=np.float64)])
    projected = homogeneous @ homography.T
    weights = projected[:, 2:3]
    with np.errstate(divide="ignore", invalid="ignore"):
        projected_xy = projected[:, :2] / weights
    projected_xy = np.nan_to_num(projected_xy, nan=0.0, posinf=0.0, neginf=0.0)
    errors = np.sqrt(np.sum((projected_xy - dst) ** 2, axis=1))
    return float(np.sqrt(np.mean(errors**2)))
