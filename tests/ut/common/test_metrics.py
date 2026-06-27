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

"""Unit tests for the QA metrics (ATBD <5.10>, ALG-QA-*)."""

import math

import numpy as np
import pytest

from msi_processor.common.metrics import (
    MetricSet,
    align_extent,
    compute_metrics,
    mse,
    psnr,
    rmse,
    snr,
    variance,
)


@pytest.mark.unit
def test_snr_hand_computed():
    """mean=3, std=1 -> SNR = 20*log10(3)."""
    image = np.array([[2.0, 4.0], [4.0, 2.0]], dtype=np.float32)
    assert snr(image) == pytest.approx(20.0 * math.log10(3.0))


@pytest.mark.unit
def test_snr_constant_image_is_infinite():
    """Zero standard deviation -> +inf SNR."""
    assert snr(np.full((4, 4), 7.0, dtype=np.float32)) == math.inf


@pytest.mark.unit
def test_variance_hand_computed():
    """Population variance of [[2,4],[4,2]] is exactly 1.0."""
    image = np.array([[2.0, 4.0], [4.0, 2.0]], dtype=np.float32)
    assert variance(image) == pytest.approx(1.0)


@pytest.mark.unit
def test_mse_and_rmse_hand_computed():
    """Every pixel off by 2 -> MSE = 4, RMSE = 2."""
    test = np.full((2, 2), 10.0, dtype=np.float32)
    reference = np.array([[8.0, 8.0], [8.0, 12.0]], dtype=np.float32)
    assert mse(test, reference) == pytest.approx(4.0)
    assert rmse(test, reference) == pytest.approx(2.0)


@pytest.mark.unit
def test_psnr_hand_computed_default_bit_depth():
    """PSNR = 20*log10((2**12 - 1) / sqrt(MSE)) with MSE = 4."""
    test = np.full((2, 2), 10.0, dtype=np.float32)
    reference = np.array([[8.0, 8.0], [8.0, 12.0]], dtype=np.float32)
    assert psnr(test, reference) == pytest.approx(20.0 * math.log10(4095.0 / 2.0))


@pytest.mark.unit
def test_psnr_respects_bit_depth():
    """An 8-bit peak (255) changes the PSNR accordingly."""
    test = np.full((2, 2), 10.0, dtype=np.float32)
    reference = np.array([[8.0, 8.0], [8.0, 12.0]], dtype=np.float32)
    assert psnr(test, reference, bit_depth=8) == pytest.approx(20.0 * math.log10(255.0 / 2.0))


@pytest.mark.unit
def test_psnr_identical_images_is_infinite():
    """MSE = 0 -> +inf PSNR."""
    image = np.arange(9, dtype=np.float32).reshape(3, 3)
    assert psnr(image, image.copy()) == math.inf


@pytest.mark.unit
def test_align_extent_crops_to_common_shape():
    """Both arrays are cropped to the common top-left extent."""
    a = np.ones((3, 3), dtype=np.float32)
    b = np.ones((2, 4), dtype=np.float32)
    cropped_a, cropped_b = align_extent(a, b)
    assert cropped_a.shape == (2, 3)
    assert cropped_b.shape == (2, 3)


@pytest.mark.unit
def test_compute_metrics_without_reference_has_nan_referential():
    """Without a reference, referential metrics are nan; non-referential are finite."""
    image = np.array([[2.0, 4.0], [4.0, 2.0]], dtype=np.float32)
    metrics = compute_metrics(image)
    assert isinstance(metrics, MetricSet)
    assert metrics.snr == pytest.approx(20.0 * math.log10(3.0))
    assert metrics.variance == pytest.approx(1.0)
    assert math.isnan(metrics.mse)
    assert math.isnan(metrics.rmse)
    assert math.isnan(metrics.psnr)


@pytest.mark.unit
def test_compute_metrics_with_reference_aligns_extent():
    """compute_metrics aligns mismatched shapes before referential metrics."""
    test = np.full((2, 3), 10.0, dtype=np.float32)
    reference = np.full((2, 2), 8.0, dtype=np.float32)  # cropped to (2, 2)
    metrics = compute_metrics(test, reference)
    assert metrics.mse == pytest.approx(4.0)
    assert metrics.rmse == pytest.approx(2.0)
