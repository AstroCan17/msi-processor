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

"""Typed exception hierarchy — the fault-containment vocabulary of SDD <5.2>g.

A pure core raises a typed :class:`MsiProcessorError` subclass on a
precondition / acceptance violation; the ``EOProcessingUnit`` wrapper catches
it, attaches the relevant ``QAFlag`` and report fields, and re-raises to the
chain runner, which applies fail-stop (REQ-F-DEP-01). Observational
deviations (a QA metric out of tolerance) are warnings, never exceptions.

The class set mirrors SDD <5.4.1>. ``MsiProcessorError`` carries ``.stage``,
``.qa_flag`` and ``.report_fields`` for structured reporting.
"""

from __future__ import annotations

from typing import Any, Optional

__all__ = [
    "MyError",
    "MsiProcessorError",
    "InputValidationError",
    "ProfileValidationError",
    "AdfResolutionError",
    "L0DecodeError",
    "RadiometricError",
    "CoregistrationError",
    "GeolocationError",
    "AtmosphericError",
    "PansharpenError",
    "ProductWriteError",
]


class MyError(Exception):
    """Raised when an error occurs.

    Retained from the project template for backward compatibility; new code
    should raise a :class:`MsiProcessorError` subclass instead.
    """


class MsiProcessorError(Exception):
    """Base class of all ``msi-processor`` typed errors (SDD <5.2>g, <5.4.1>).

    Parameters
    ----------
    message:
        Human-readable description of the failure.
    stage:
        The processing stage that raised the error (e.g. ``"radiometric"``),
        used in the structured processing report.
    qa_flag:
        The QA bit to attach to affected pixels, if any.
    report_fields:
        Extra machine-readable fields for the processing report
        (``ICD-IF-DIAG``); never contains private calibration values.
    """

    def __init__(
        self,
        message: str = "",
        *,
        stage: Optional[str] = None,
        qa_flag: Optional[int] = None,
        report_fields: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.qa_flag = qa_flag
        self.report_fields: dict[str, Any] = report_fields if report_fields is not None else {}


class InputValidationError(MsiProcessorError):
    """Malformed / mismatched input product (REQ-F-L0-03, REQ-DAT-03)."""


class ProfileValidationError(MsiProcessorError):
    """Invalid / incomplete sensor profile (REQ-DAT-03; C-COM-PROFILE)."""


class AdfResolutionError(MsiProcessorError):
    """Missing or validity-mismatched ADF (REQ-S-04; C-COM-ADF)."""


class L0DecodeError(MsiProcessorError):
    """Level-0 decode failure / sensor-private decode body unavailable (REQ-F-L0-*).

    Raised by the public scaffolding when the source-packet decode cannot be
    performed because the sensor/NDA-specific decode body is a private
    ``[impl]`` backend not present in this distribution, or when a decoded
    open-container frame fails Level-0 legality (REQ-F-L0-03).
    """


class RadiometricError(MsiProcessorError):
    """Radiometric-stage failure (REQ-F-RAD-*)."""


class CoregistrationError(MsiProcessorError):
    """Insufficient matches / residual out of acceptance (REQ-F-COR-03)."""


class GeolocationError(MsiProcessorError):
    """Missing DEM / viewing-model coverage (REQ-F-GEO-*)."""


class AtmosphericError(MsiProcessorError):
    """Atmospheric-correction failure (REQ-F-ATM-*)."""


class PansharpenError(MsiProcessorError):
    """Pan-sharpening failure / unimplemented fusion method (REQ-F-PAN-*)."""


class ProductWriteError(MsiProcessorError):
    """Product store / write failure (REQ-F-PRD-01; C-COM-PRODUCT)."""
