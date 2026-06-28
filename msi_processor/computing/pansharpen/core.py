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

r"""Pure pan-sharpening core (C-PU-PAN; ALG-PAN-ALIGN/FUSE).

CPM-free, I/O-free functions implementing the optional pan-sharpening algorithms
of ATBD <5.9>. Pan-sharpening is a **terminal, post-L2A derivative** (CR-4): it
runs *after* atmospheric correction, fusing the BOA (surface) reflectance stack
with the high-resolution panchromatic (PAN) band to trade spectral/radiometric
fidelity for spatial sharpness. It is optional and default-off, and the product
it emits (``DPM-PR-L2A-PAN``) is a visual/derivative product, **not** a
science-grade input to quantitative retrieval (DPM <8.9>).

Algorithm split (operational baseline vs ``[impl]``)
----------------------------------------------------
* ``ALG-PAN-ALIGN`` (MS -> PAN registration). The multispectral bands are
  resampled onto the PAN grid by **reusing the co-registration core** (CLAHE ->
  SIFT -> FLANN -> RANSAC homography -> ``warpPerspective``); see
  :func:`align_ms_to_pan`. No new matching code lives here -- alignment is the
  same heritage estimator the ``coregister`` unit uses, with the PAN band as the
  reference (SDD <5.4.10>).

* ``ALG-PAN-FUSE`` (fusion). The **simple-mean** fusion
  :math:`\hat{P}_b = \tfrac{1}{2}(\mathrm{MS}^{\mathrm{reg}}_b + \mathrm{PAN})`
  (heritage, ATBD <5.9>) is realised here (:func:`fuse`, ``method="simple_mean"``)
  and fully unit-tested. The sharper component-substitution methods (Brovey,
  Gram-Schmidt, IHS, a-trous wavelet -- down-selected per sensor profile in the
  DPM) are the deferred bodies (``[impl]``); requesting one raises
  :class:`~msi_processor.exceptions.errors.PansharpenError` (ATBD <5.9> open
  point 6).

Spectral fidelity (REQ-F-PAN-02)
--------------------------------
Fusion is lossy by construction. :func:`spectral_fidelity` quantifies, per band,
how much of the input MS radiometry survives the fusion -- the Pearson
correlation between the aligned MS band and its fused counterpart. The wrapper
reports these scalars as QA metrics and checks them against the per-profile
fidelity budget (the budget itself is private; ``None`` accepts any value).

PAN-reflectance handling (ATBD <5.9> open point 7, **unresolved**)
------------------------------------------------------------------
Rigorous atmospheric correction is band-specific, but the broadband PAN response
is too wide for a well-defined per-band correction. Whether the PAN passed to
:func:`fuse` is a synthesised BOA-PAN (approximated from the corrected MS bands)
or the raw TOA-PAN (a TOA/BOA domain mismatch) is an open ``[impl]``/profile
decision; this core operates on **whatever PAN array the wrapper supplies** and
does not itself resolve that choice. The settled part is only the order
(atmospheric correction precedes fusion, ATBD <5.9>).

*Trace:* REQ-F-PAN-01..02; DPM-M-PAN; ALG-PAN-ALIGN/FUSE; SYS-CAP-04.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, get_args

import numpy as np
import numpy.typing as npt

from msi_processor.computing.coregistration.core import (
    CoregParams,
    estimate_homography,
    warp_to_reference,
)
from msi_processor.exceptions.errors import CoregistrationError, PansharpenError

__all__ = [
    "FusionMethod",
    "OPERATIONAL_METHODS",
    "align_ms_to_pan",
    "fuse",
    "spectral_fidelity",
]

FloatArray = npt.NDArray[np.float32]

#: Fusion methods recognised by the unit; only :data:`OPERATIONAL_METHODS` are
#: realised, the rest are ``[impl]`` (ATBD <5.9> open point 6).
FusionMethod = Literal["simple_mean", "brovey", "gs", "ihs", "atrous"]

#: The operational baseline realised in this increment (PDR/CDR target). The
#: component-substitution methods are deferred ``[impl]`` bodies.
OPERATIONAL_METHODS: tuple[FusionMethod, ...] = ("simple_mean",)

_STAGE = "pansharpen"


def align_ms_to_pan(
    ms_stack: Mapping[str, npt.NDArray[Any]],
    pan: npt.NDArray[Any],
    params: CoregParams,
) -> dict[str, FloatArray]:
    r"""ALG-PAN-ALIGN -- resample each MS band onto the PAN grid.

    Reuses the co-registration estimator (:func:`estimate_homography` +
    :func:`warp_to_reference` from :mod:`msi_processor.computing.coregistration.core`)
    with the panchromatic band as the reference: for every MS band a projective
    homography :math:`H_b` (band :math:`\to` PAN) is fitted by CLAHE-enhanced SIFT
    + FLANN + RANSAC, then the **original (radiometric) band** is warped onto the
    PAN :math:`(\text{rows}, \text{cols})` extent. This is the same heritage
    alignment the ``coregister`` unit performs, so no matching logic is
    re-implemented (SDD <5.4.10>).

    Parameters
    ----------
    ms_stack:
        Mapping of MS band id to its 2-D BOA-reflectance array (post atmospheric
        correction). Must be non-empty.
    pan:
        2-D panchromatic array; its shape defines the output grid.
    params:
        Co-registration parameters (reference band is ignored here -- PAN is the
        reference; the RANSAC threshold, CLAHE and keypoint gates apply).

    Returns
    -------
    dict
        Mapping of band id to its PAN-grid ``float32`` array, in input order.

    Raises
    ------
    PansharpenError
        If ``ms_stack`` is empty, ``pan`` is not 2-D, or alignment fails for any
        band (insufficient keypoints/matches/inliers) -- fail-stop (REQ-F-PAN-01).
    """
    if not ms_stack:
        raise PansharpenError("Pan-sharpening requires at least one MS band", stage=_STAGE)
    pan_arr = np.asarray(pan)
    if pan_arr.ndim != 2:
        raise PansharpenError(
            f"PAN band must be a 2-D array, got shape {pan_arr.shape}",
            stage=_STAGE,
        )
    shape = (int(pan_arr.shape[0]), int(pan_arr.shape[1]))

    aligned: dict[str, FloatArray] = {}
    for band, data in ms_stack.items():
        band_arr = np.asarray(data)
        try:
            homography, _residual = estimate_homography(band_arr, pan_arr, params)
        except CoregistrationError as exc:
            raise PansharpenError(
                f"MS->PAN alignment failed for band '{band}': {exc}",
                stage=_STAGE,
            ) from exc
        warped = warp_to_reference(band_arr.astype(np.float32), homography, shape)
        aligned[band] = np.asarray(warped, dtype=np.float32)
    return aligned


def fuse(
    ms_aligned: Mapping[str, npt.NDArray[Any]],
    pan: npt.NDArray[Any],
    method: FusionMethod = "simple_mean",
) -> dict[str, FloatArray]:
    r"""ALG-PAN-FUSE -- fuse PAN-grid MS bands with the PAN band.

    For the operational ``"simple_mean"`` method each fused band is the per-pixel
    average of the aligned MS band and the PAN band,

    .. math::

        \hat{P}_b = \tfrac{1}{2}\big(\mathrm{MS}^{\mathrm{reg}}_b + \mathrm{PAN}\big),

    clipped to the reflectance range :math:`[0, 1]` (the operating domain is BOA
    reflectance; the heritage DN clip ``[0, 2^{12}-1]`` is the same operation in
    DN units, DPM <8.9>). The component-substitution methods (``"brovey"``,
    ``"gs"``, ``"ihs"``, ``"atrous"``) are deferred ``[impl]`` (ATBD <5.9> open
    point 6).

    Parameters
    ----------
    ms_aligned:
        Mapping of band id to its PAN-grid array (output of
        :func:`align_ms_to_pan`). Must be non-empty.
    pan:
        2-D panchromatic array; every aligned band must share its shape.
    method:
        Fusion method; only :data:`OPERATIONAL_METHODS` are realised.

    Returns
    -------
    dict
        Mapping of band id to its fused ``float32`` array, in input order.

    Raises
    ------
    PansharpenError
        On an unknown method, a deferred ``[impl]`` method, an empty stack, or a
        band whose shape does not match ``pan``.
    """
    if method not in get_args(FusionMethod):
        raise PansharpenError(
            f"Unknown fusion method '{method}'; expected one of {get_args(FusionMethod)}",
            stage=_STAGE,
        )
    if method not in OPERATIONAL_METHODS:
        raise PansharpenError(
            f"Fusion method '{method}' is not implemented (component-substitution "
            "methods are [impl], ATBD <5.9> open point 6); operational methods are "
            f"{OPERATIONAL_METHODS}",
            stage=_STAGE,
        )
    if not ms_aligned:
        raise PansharpenError("Pan-sharpening requires at least one aligned MS band", stage=_STAGE)

    pan_arr = np.asarray(pan, dtype=np.float32)
    fused: dict[str, FloatArray] = {}
    for band, data in ms_aligned.items():
        band_arr = np.asarray(data, dtype=np.float32)
        if band_arr.shape != pan_arr.shape:
            raise PansharpenError(
                f"Aligned band '{band}' shape {band_arr.shape} does not match PAN " f"shape {pan_arr.shape}",
                stage=_STAGE,
            )
        merged = 0.5 * (band_arr + pan_arr)
        fused[band] = np.clip(merged, 0.0, 1.0).astype(np.float32)
    return fused


def spectral_fidelity(
    ms_aligned: Mapping[str, npt.NDArray[Any]],
    fused: Mapping[str, npt.NDArray[Any]],
) -> dict[str, float]:
    r"""Per-band spectral-fidelity metric (REQ-F-PAN-02).

    Reports, for each fused band, the **Pearson correlation coefficient** between
    the aligned MS band (the spectral reference) and its fused counterpart -- a
    value in :math:`[-1, 1]` where ``1`` means the fusion preserved the band's
    spatial-spectral structure perfectly. Fusion necessarily lowers it; the
    wrapper checks the per-band value against the per-profile fidelity budget and
    records it as QA (the budget is private).

    A band whose MS or fused array is constant (zero variance) has an undefined
    correlation; ``0.0`` is reported for it (no linear structure to preserve).

    Parameters
    ----------
    ms_aligned, fused:
        Matching mappings of band id to PAN-grid arrays (same keys/shapes).

    Returns
    -------
    dict
        Mapping of band id to its fidelity coefficient, in ``fused`` order.
    """
    fidelity: dict[str, float] = {}
    for band, fused_data in fused.items():
        reference = ms_aligned.get(band)
        if reference is None:
            fidelity[band] = 0.0
            continue
        ref = np.asarray(reference, dtype=np.float64).ravel()
        out = np.asarray(fused_data, dtype=np.float64).ravel()
        if ref.size == 0 or ref.std() == 0.0 or out.std() == 0.0:
            fidelity[band] = 0.0
            continue
        coeff = float(np.corrcoef(ref, out)[0, 1])
        fidelity[band] = 0.0 if np.isnan(coeff) else coeff
    return fidelity
