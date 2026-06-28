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

"""Atmospheric-correction processing unit (C-PU-ATM; DPM-M-ATM).

TOA -> BOA (surface) reflectance inversion (6S/Vermote, ATBD <5.8>) plus scene
classification and cloud / cloud-shadow masking; emits the ``L2A`` product.
"""
