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

"""Image-quality-enhancement stage (C-PU-ENH; DPM-M-ENH; ALG-ENH-*).

Mandatory Level-1 image-quality restoration: a profile-configurable denoise
sub-step followed by the mandatory MTF compensation (MTFC) via PSF
deconvolution. The stage always runs because MTFC is mandatory (REQ-F-ENH-03).
It is a pure :mod:`~msi_processor.computing.enhancement.core` plus a thin
:class:`~msi_processor.computing.enhancement.unit.EnhancementUnit` wrapper.
"""

from msi_processor.computing.enhancement.core import (
    DenoiseMethod,
    EnhancementParams,
    butterworth_lowpass,
    denoise,
    fft_dark_subtract,
    flag_enhanced,
    gaussian_smooth,
    moving_average,
    mtf_compensate,
    pca_denoise,
    wavelet_visushrink,
)
from msi_processor.computing.enhancement.unit import EnhancementUnit

__all__ = [
    "DenoiseMethod",
    "EnhancementParams",
    "denoise",
    "butterworth_lowpass",
    "wavelet_visushrink",
    "pca_denoise",
    "moving_average",
    "gaussian_smooth",
    "fft_dark_subtract",
    "mtf_compensate",
    "flag_enhanced",
    "EnhancementUnit",
]
