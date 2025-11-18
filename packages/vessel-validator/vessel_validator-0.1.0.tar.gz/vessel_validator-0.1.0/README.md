# IMO and MMSI Validator

[![PyPI version](https://badge.fury.io/py/vessel-validator.svg)](https://badge.fury.io/py/vessel-validator)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for validating **International Maritime Organization (IMO) numbers** and **Maritime Mobile Service Identity (MMSI) numbers** according to international maritime standards.

Developed by **[Scitus Solutions Ltd.](https://scitus.ca)** - Maritime Software Solutions.

---

## Features

### IMO Number Validation
✅ **Mathematical check digit verification** (catches ~90% of typos)
✅ Format validation (7 digits after "IMO" prefix)
✅ Range validation (>= 1000000)
✅ Era estimation (vessel construction period)
✅ Historical warnings for older vessels (< 6000000)
✅ Support for both ship and company IMO numbers

### MMSI Number Validation
✅ **MID (Maritime Identification Digits) country code verification**
✅ **8 MMSI type detection** (ship, coast, group, handheld, SAR, AtoN, SART, craft)
✅ **200+ MID to country mappings**
✅ Type-specific format validation
✅ International voyage compliance warnings
✅ Suspicious pattern detection

---

## Installation

```bash
pip install vessel-validator
```

---

## Quick Start

### IMO Number Validation

```python
from vessel_validator import validate_imo

# Validate an IMO number
result = validate_imo("9074729")

print(f"Valid: {result.valid}")
print(f"Normalized: {result.normalized}")  # "IMO9074729"
print(f"Check digit: {result.info['check_digit']}")
# {'calculated': 9, 'actual': 9, 'valid': True}

if result.errors:
    print(f"Errors: {result.errors}")
if result.warnings:
    print(f"Warnings: {result.warnings}")
```

### MMSI Number Validation

```python
from vessel_validator import validate_mmsi

# Validate an MMSI number
result = validate_mmsi("366123000")

print(f"Valid: {result.valid}")
print(f"Type: {result.info['type']}")          # "ship_station"
print(f"Country: {result.info['country']}")    # "United States of America"
print(f"MID: {result.info['mid']}")            # "366"
```

### Using the Validator Class

```python
from vessel_validator import VesselIdentifierValidator

validator = VesselIdentifierValidator()

# Validate IMO
imo_result = validator.validate_imo("IMO 9074729")

# Validate MMSI
mmsi_result = validator.validate_mmsi("232123000")

# Batch validation
imo_batch = validator.validate_imo_batch(["9074729", "9176187", "8814275"])
print(f"Success rate: {imo_batch['summary']['success_rate']}")
```

---

## Validation Examples

### ✅ Valid IMO Number

```python
result = validate_imo("9074729")
# ✓ Valid
# Check digit: 9 (calculated: 9) ✓
# Era: 2010s-2020s
```

### ❌ Invalid IMO Number (Wrong Check Digit)

```python
result = validate_imo("9074728")
# ✗ Invalid
# Error: "Invalid IMO number: check digit validation failed. Expected 9, got 8"
```

### ✅ Valid Ship Station MMSI

```python
result = validate_mmsi("366123000")
# ✓ Valid
# Type: ship_station
# Country: United States of America
# MID: 366
```

### ✅ Valid SAR Aircraft MMSI

```python
result = validate_mmsi("111232000")
# ✓ Valid
# Type: sar_aircraft
# Country: United Kingdom
# MID: 232
```

### ❌ Invalid MMSI (Unknown Type)

```python
result = validate_mmsi("123456789")
# ✗ Invalid
# Error: "Invalid MMSI format: MMSI starting with '1' must be SAR aircraft (111XXXXXX)"
```

---

## API Reference

### `validate_imo(imo, **kwargs)`

Validate an IMO number.

**Parameters:**
- `imo` (str): The IMO number to validate (e.g., "IMO 9074729" or "9074729")
- `number_type` (str, optional): Type of IMO number ('ship', 'company', 'auto'). Default: 'ship'
- `strict_format` (bool, optional): If True, require "IMO" prefix. Default: False
- `allow_without_prefix` (bool, optional): If True, accept numbers without "IMO" prefix. Default: True

**Returns:** `ValidationResult`

---

### `validate_mmsi(mmsi, **kwargs)`

Validate an MMSI number.

**Parameters:**
- `mmsi` (str): The MMSI number to validate (9 digits)
- `mmsi_type` (str, optional): Expected MMSI type ('auto' to detect automatically). Default: 'auto'
- `expected_country` (str, optional): Expected country name for MID validation
- `strict_format` (bool, optional): If True, reject any formatting issues. Default: False

**Returns:** `ValidationResult`

---

### `ValidationResult`

Dataclass containing validation results:

```python
@dataclass
class ValidationResult:
    valid: bool                    # True if validation passed
    normalized: str                # Normalized format (e.g., "IMO9074729")
    errors: List[str]              # List of error messages
    warnings: List[str]            # List of warning messages
    info: Dict[str, Any]           # Additional information
```

---

## MMSI Types Supported

| Type | Format | Example | Description |
|------|--------|---------|-------------|
| Ship Station | `2-7XXXXXX` | `366123000` | Most common - vessel identification |
| Coast Station | `00MIDXXXX` | `002470002` | Shore-based communication |
| Group Station | `0MIDXXXXX` | `023200002` | Fleet operations |
| Handheld VHF | `8MIDXXXXX` | `836612345` | Personal VHF radios |
| SAR Aircraft | `111MIDXXX` | `111232000` | Search and rescue aircraft |
| AIS AtoN | `99MIDXXXX` | `992320001` | Navigation aids (buoys, beacons) |
| AIS SART | `970XXYYYY` | `970123456` | Emergency beacons |
| Craft Associated | `98MIDXXXX` | `982320001` | Tenders, pilot boats |

---

## MID Country Mapping

The validator includes mappings for 200+ MID codes to their respective countries:

| MID Range | Country | Example |
|-----------|---------|---------|
| 201-210 | Albania, Andorra, Austria, etc. | 203 → Austria |
| 232-235 | United Kingdom | 232 → United Kingdom |
| 303-369 | United States of America | 366 → USA |
| 316 | Canada | 316 → Canada |
| 503 | Australia | 503 → Australia |
| 636-637 | Liberia | 636 → Liberia |

Full MID list available at: https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/mid.aspx

---

## IMO Check Digit Algorithm

### Ship IMO Numbers

Formula: `(d1×7 + d2×6 + d3×5 + d4×4 + d5×3 + d6×2) mod 10`

**Example: IMO 9074729**
```
Digits:    9    0    7    4    7    2    [9]
Weights:   ×7   ×6   ×5   ×4   ×3   ×2
Products:  63 + 0 + 35 + 16 + 21 + 4 = 139
Check:     139 mod 10 = 9 ✓
```

### Company IMO Numbers

Formula: `(11 - ((d1×8 + d2×6 + d3×4 + d4×2 + d5×9 + d6×7) mod 11)) mod 10`

---

## Use Cases

### Maritime Software Development
- Ballast Water Reporting Forms (BWRF) validation
- Port State Control systems
- Vessel tracking and identification
- Maritime regulatory compliance systems
- Ship registration databases

### Data Quality & Cleaning
- Validate vessel identifiers in databases
- Detect typos and data entry errors
- Standardize IMO/MMSI formats
- Enrich vessel data with country information

### API Integration
- Validate user input in web forms
- API endpoint data validation
- Batch import validation
- Data migration quality checks

---

## Development

### Running Tests

```bash
git clone https://github.com/scitus-ca/vessel-validator.git
cd vessel-validator
python -m pytest tests/
```

### Running Examples

```bash
python examples/basic_usage.py
python examples/batch_validation.py
```

---

## Standards Compliance

- ✅ **IMO Compliance**: Check digit verification per IMO standards
- ✅ **ITU Compliance**: MID validation per ITU-R M.585 recommendation
- ✅ **SOLAS Compliance**: International voyage MMSI validation

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## About Scitus Solutions Ltd.

**Scitus Solutions Ltd.** specializes in maritime software solutions, including ballast water management systems, port state control applications, and vessel tracking systems.

- **Website**: https://scitus.ca
- **Email**: info@scitus.ca
- **GitHub**: https://github.com/scitus-ca

---

## Changelog

### Version 1.0.0 (2025-01-16)
- ✨ Initial release
- ✅ IMO number validation with check digit verification
- ✅ MMSI number validation with MID country mapping
- ✅ Support for 8 MMSI types
- ✅ 200+ MID to country mappings
- ✅ Batch validation support
- ✅ Comprehensive test suite
- ✅ Full documentation

---

## Support

If you encounter any issues or have questions:

- 📫 Email: info@scitus.ca
- 🐛 Bug Reports: https://github.com/scitus-ca/vessel-validator/issues
- 📖 Documentation: https://github.com/scitus-ca/vessel-validator#readme

---

**Made with ❤️ by Scitus Solutions Ltd. for the maritime community**
