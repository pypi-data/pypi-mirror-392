"""Tests for MMSI number validation."""

import pytest
from vessel_validator import validate_mmsi, VesselIdentifierValidator


class TestMMSIValidation:
    """Test suite for MMSI number validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = VesselIdentifierValidator()

    # Valid MMSI numbers - Ship Station
    def test_valid_ship_station_mmsi_us(self):
        """Test valid ship station MMSI (US)."""
        result = validate_mmsi("366123000")
        assert result.valid is True
        assert result.info["type"] == "ship_station"
        assert result.info["mid"] == "366"
        assert result.info["country"] == "United States of America"

    def test_valid_ship_station_mmsi_uk(self):
        """Test valid ship station MMSI (UK)."""
        result = validate_mmsi("232123000")
        assert result.valid is True
        assert result.info["type"] == "ship_station"
        assert result.info["mid"] == "232"
        assert result.info["country"] == "United Kingdom"

    def test_valid_ship_station_mmsi_canada(self):
        """Test valid ship station MMSI (Canada)."""
        result = validate_mmsi("316123000")
        assert result.valid is True
        assert result.info["type"] == "ship_station"
        assert result.info["country"] == "Canada"

    def test_ship_station_not_ending_000(self):
        """Test ship station MMSI not ending in 000 (warning)."""
        result = validate_mmsi("366123456")
        assert result.valid is True
        assert result.info["type"] == "ship_station"
        assert len(result.warnings) > 0
        assert "not end in 000" in result.warnings[0]

    # Valid MMSI numbers - Coast Station
    def test_valid_coast_station_mmsi(self):
        """Test valid coast station MMSI."""
        result = validate_mmsi("002470002")
        assert result.valid is True
        assert result.info["type"] == "coast_station"
        assert result.info["mid"] == "247"
        assert result.info["country"] == "Italy"

    def test_valid_coast_station_mmsi_uk(self):
        """Test valid coast station MMSI (UK)."""
        result = validate_mmsi("002320001")
        assert result.valid is True
        assert result.info["type"] == "coast_station"
        assert result.info["country"] == "United Kingdom"

    # Valid MMSI numbers - Group Station
    def test_valid_group_station_mmsi(self):
        """Test valid group station MMSI."""
        result = validate_mmsi("023200001")
        assert result.valid is True
        assert result.info["type"] == "group_station"
        assert result.info["mid"] == "232"

    # Valid MMSI numbers - Handheld
    def test_valid_handheld_mmsi(self):
        """Test valid handheld VHF MMSI."""
        result = validate_mmsi("836612345")
        assert result.valid is True
        assert result.info["type"] == "handheld"
        assert result.info["mid"] == "366"

    # Valid MMSI numbers - SAR Aircraft
    def test_valid_sar_aircraft_mmsi(self):
        """Test valid SAR aircraft MMSI."""
        result = validate_mmsi("111232000")
        assert result.valid is True
        assert result.info["type"] == "sar_aircraft"
        assert result.info["mid"] == "232"
        assert result.info["country"] == "United Kingdom"

    # Valid MMSI numbers - AIS AtoN (Aids to Navigation)
    def test_valid_aton_mmsi(self):
        """Test valid AIS AtoN MMSI."""
        result = validate_mmsi("992320001")
        assert result.valid is True
        assert result.info["type"] == "aton"
        assert result.info["mid"] == "232"

    # Valid MMSI numbers - AIS SART (Search and Rescue Transponder)
    def test_valid_ais_sart_mmsi(self):
        """Test valid AIS SART MMSI."""
        result = validate_mmsi("970123456")
        assert result.valid is True
        assert result.info["type"] == "ais_sart"

    # Valid MMSI numbers - Craft Associated with Ship
    def test_valid_craft_associated_mmsi(self):
        """Test valid craft associated with ship MMSI."""
        result = validate_mmsi("982320001")
        assert result.valid is True
        assert result.info["type"] == "craft_associated_with_ship"
        assert result.info["mid"] == "232"

    # Invalid MMSI numbers - Format errors
    def test_invalid_mmsi_empty(self):
        """Test empty MMSI."""
        result = validate_mmsi("")
        assert result.valid is False
        assert "cannot be empty" in result.errors[0]

    def test_invalid_mmsi_too_short(self):
        """Test MMSI too short."""
        result = validate_mmsi("12345678")
        assert result.valid is False
        assert "exactly 9 digits" in result.errors[0]

    def test_invalid_mmsi_too_long(self):
        """Test MMSI too long."""
        result = validate_mmsi("1234567890")
        assert result.valid is False
        assert "exactly 9 digits" in result.errors[0]

    def test_invalid_mmsi_with_letters(self):
        """Test MMSI with letters."""
        result = validate_mmsi("36612300A")
        assert result.valid is False
        assert "only numeric digits" in result.errors[0]

    def test_invalid_mmsi_starts_with_1(self):
        """Test MMSI starting with 1 (invalid unless SAR)."""
        result = validate_mmsi("123456789")
        assert result.valid is False
        assert "SAR aircraft" in result.errors[0]

    def test_invalid_ship_station_starts_with_0(self):
        """Test ship station cannot start with 0."""
        result = validate_mmsi("012345678")
        assert result.valid is False

    def test_invalid_ship_station_starts_with_8(self):
        """Test MMSI starting with 8 is handheld, not ship."""
        result = validate_mmsi("812345678")
        # This should be detected as handheld, not error
        assert result.info["type"] == "handheld"

    def test_invalid_ship_station_starts_with_9(self):
        """Test MMSI starting with 9 (AtoN or craft)."""
        result = validate_mmsi("912345678")
        # Should be detected as some other type
        assert result.info["type"] != "ship_station"

    # MID validation
    def test_invalid_mid_too_low(self):
        """Test invalid MID below 201."""
        result = validate_mmsi("200123000")
        assert result.valid is False
        assert "Invalid MID code" in result.errors[0]

    def test_invalid_mid_too_high(self):
        """Test invalid MID above 775."""
        result = validate_mmsi("776123000")
        assert result.valid is False
        assert "Invalid MID code" in result.errors[0]

    # Country validation
    def test_mmsi_expected_country_match(self):
        """Test MMSI with expected country match."""
        result = validate_mmsi("366123000", expected_country="United States of America")
        assert result.valid is True
        assert len(result.warnings) == 0

    def test_mmsi_expected_country_mismatch(self):
        """Test MMSI with expected country mismatch."""
        result = validate_mmsi("366123000", expected_country="Canada")
        assert result.valid is True
        assert len(result.warnings) > 0
        assert "expected Canada" in result.warnings[0]

    # Suspicious patterns
    def test_mmsi_all_same_digits(self):
        """Test MMSI with all same digits (suspicious)."""
        result = validate_mmsi("222222222")
        assert len(result.warnings) > 0
        # Check if suspicious pattern warning exists in any warning
        assert any("suspicious pattern" in w for w in result.warnings)

    def test_mmsi_sequential_ascending(self):
        """Test MMSI with sequential ascending pattern."""
        result = validate_mmsi("123456789")
        # Will be invalid for other reasons, but should warn about pattern
        assert result.valid is False

    # Batch validation
    def test_batch_validation(self):
        """Test batch MMSI validation."""
        mmsi_list = ["366123000", "232123000", "002470002", "123456789"]
        result = self.validator.validate_mmsi_batch(mmsi_list)

        assert result["summary"]["total"] == 4
        assert result["summary"]["valid"] == 3
        assert result["summary"]["invalid"] == 1
        assert result["summary"]["success_rate"] == "75.0%"

    # Type-specific validations
    def test_coast_station_must_start_with_00(self):
        """Test coast station format validation."""
        result = validate_mmsi("012340001")
        assert result.info["type"] == "group_station"  # Not coast_station

    def test_group_station_must_start_with_single_0(self):
        """Test group station format validation."""
        result = validate_mmsi("023200001")
        assert result.valid is True
        assert result.info["type"] == "group_station"

    def test_handheld_must_start_with_8(self):
        """Test handheld format validation."""
        result = validate_mmsi("836612345")
        assert result.valid is True
        assert result.info["type"] == "handheld"

    def test_sar_must_start_with_111(self):
        """Test SAR aircraft format validation."""
        result = validate_mmsi("111232000")
        assert result.valid is True
        assert result.info["type"] == "sar_aircraft"

    def test_aton_must_start_with_99(self):
        """Test AtoN format validation."""
        result = validate_mmsi("992320001")
        assert result.valid is True
        assert result.info["type"] == "aton"

    # Real-world MMSI examples
    def test_real_world_panama_vessel(self):
        """Test real-world Panama vessel MMSI."""
        result = validate_mmsi("351234000")
        assert result.valid is True
        assert result.info["country"] == "Panama"

    def test_real_world_liberia_vessel(self):
        """Test real-world Liberia vessel MMSI."""
        result = validate_mmsi("636123000")
        assert result.valid is True
        assert result.info["country"] == "Liberia"

    def test_real_world_singapore_vessel(self):
        """Test real-world Singapore vessel MMSI."""
        result = validate_mmsi("563123000")
        assert result.valid is True
        assert result.info["country"] == "Singapore"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
