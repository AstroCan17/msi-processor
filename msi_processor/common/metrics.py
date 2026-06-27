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

"""Quality-assurance metrics (DPM-M-QA; ALG-QA-*; ATBD <5.10>).

Pure, I/O-free implementations of the quality metrics, ported from the
heritage ``metrics_ips.py`` (RD-9). Referential metrics (MSE/RMSE/PSNR) are
computed against a reference aligned to the common extent; non-referential
metrics (SNR/variance) are computed from image statistics. Internal
arithmetic is float64 for stability; results are returned as Python floats.

*Trace:* REQ-F-QA-01..02; ATBD <5.10>; SDD <5.4.10>.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt

__all__ = [
    "MetricSet",
    "snr",
    "mse",
    "rmse",
    "psnr",
    "variance",
    "align_extent",
    "compute_metrics",
]


@dataclass(frozen=True)
class MetricSet:
    """QA metrics per band (ALG-QA-*, SDD <5.4.1>).

    ``rmse``/``psnr``/``mse`` are ``nan`` when no reference is supplied.
    """

    snr: float
    rmse: float
    psnr: float
    mse: float
    variance: float


def snr(image: npt.NDArray[Any]) -> float:
    r"""ALG-QA-SNR — non-referential signal-to-noise ratio in dB.

    :math:`\mathrm{SNR} = 20\log_{10}(\bar I / \sigma_I)`. Returns ``+inf``
    when the standard deviation is zero (a constant image).
    """
    arr = np.asarray(image, dtype=np.float64)
    mean = float(arr.mean())
    std = float(arr.std())
    if std == 0.0:
        return math.inf
    return 20.0 * math.log10(mean / std)


def mse(image: npt.NDArray[Any], reference: npt.NDArray[Any]) -> float:
    r"""ALG-QA-MSE — mean squared error against ``reference``."""
    a = np.asarray(image, dtype=np.float64)
    b = np.asarray(reference, dtype=np.float64)
    return float(np.mean((a - b) ** 2))


def rmse(image: npt.NDArray[Any], reference: npt.NDArray[Any]) -> float:
    r"""ALG-QA-RMSE — root mean squared error against ``reference``."""
    return math.sqrt(mse(image, reference))


def psnr(image: npt.NDArray[Any], reference: npt.NDArray[Any], bit_depth: int = 12) -> float:
    r"""ALG-QA-PSNR — peak signal-to-noise ratio in dB.

    Peak is :math:`2^{\mathrm{bit\_depth}} - 1`; returns ``+inf`` when the
    images are identical (MSE = 0).
    """
    error = mse(image, reference)
    if error == 0.0:
        return math.inf
    peak = float(2**bit_depth - 1)
    return 20.0 * math.log10(peak / math.sqrt(error))


def variance(image: npt.NDArray[Any]) -> float:
    r"""ALG-QA-VAR — population variance of ``image``."""
    arr = np.asarray(image, dtype=np.float64)
    return float(np.var(arr))


def align_extent(a: npt.NDArray[Any], b: npt.NDArray[Any]) -> tuple[npt.NDArray[Any], npt.NDArray[Any]]:
    """Crop both arrays to their common (top-left) extent.

    Mirrors the heritage ``run_validation`` size equalisation so referential
    metrics compare equal-shaped arrays (ATBD <5.10>).
    """
    rows = min(a.shape[0], b.shape[0])
    cols = min(a.shape[1], b.shape[1])
    return a[:rows, :cols], b[:rows, :cols]


def compute_metrics(
    test: npt.NDArray[Any],
    reference: npt.NDArray[Any] | None = None,
    bit_depth: int = 12,
) -> MetricSet:
    """Compute the full :class:`MetricSet` for ``test`` (vs optional reference).

    SNR and variance are always computed; RMSE/MSE/PSNR require a reference
    (otherwise ``nan``). ``test`` and ``reference`` are aligned to the common
    extent before the referential comparison.
    """
    snr_value = snr(test)
    var_value = variance(test)
    if reference is None:
        return MetricSet(snr_value, math.nan, math.nan, math.nan, var_value)
    aligned_test, aligned_ref = align_extent(test, reference)
    mse_value = mse(aligned_test, aligned_ref)
    rmse_value = math.sqrt(mse_value)
    psnr_value = psnr(aligned_test, aligned_ref, bit_depth)
    return MetricSet(snr_value, rmse_value, psnr_value, mse_value, var_value)
