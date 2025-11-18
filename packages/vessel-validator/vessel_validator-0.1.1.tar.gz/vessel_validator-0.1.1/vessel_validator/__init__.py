"""IMO and MMSI Validator - Maritime Vessel Identifier Validation.

A comprehensive Python library for validating International Maritime Organization (IMO) numbers
and Maritime Mobile Service Identity (MMSI) numbers according to international maritime standards.

Features:
- IMO number validation with mathematical check digit verification
- MMSI number validation with MID (Maritime Identification Digits) country code verification
- Support for 8 MMSI types (ship, coast, group, handheld, SAR, AtoN, SART, craft)
- 200+ MID to country mappings
- Type detection and classification
- Batch validation support
- Detailed error messages and warnings

Author: Scitus Solutions Ltd.
License: MIT
Version: 1.0.0
"""

from .validator import (
    ValidationResult,
    VesselIdentifierValidator,
    vessel_validator,
    validate_imo,
    validate_mmsi,
    __version__,
    __author__,
    __license__,
)

__all__ = [
    "ValidationResult",
    "VesselIdentifierValidator",
    "vessel_validator",
    "validate_imo",
    "validate_mmsi",
    "__version__",
    "__author__",
    "__license__",
]
