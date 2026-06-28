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

"""Optional pan-sharpening processing unit (C-PU-PAN; DPM-M-PAN).

Terminal, default-off post-L2A derivative (CR-4): fuses the BOA (surface)
reflectance stack with the panchromatic band to trade spectral fidelity for
spatial sharpness, emitting the ``DPM-PR-L2A-PAN`` product. Not science-grade.
"""
