"""Tests for IMO number validation."""

import pytest
from vessel_validator import validate_imo, VesselIdentifierValidator


class TestIMOValidation:
    """Test suite for IMO number validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = VesselIdentifierValidator()

    # Valid IMO numbers
    def test_valid_imo_with_prefix(self):
        """Test valid IMO number with prefix."""
        result = validate_imo("IMO 9074729")
        assert result.valid is True
        assert result.normalized == "IMO9074729"
        assert result.info["check_digit"]["valid"] is True
        assert result.info["check_digit"]["actual"] == 9
        assert result.info["check_digit"]["calculated"] == 9

    def test_valid_imo_without_prefix(self):
        """Test valid IMO number without prefix."""
        result = validate_imo("9074729")
        assert result.valid is True
        assert result.normalized == "IMO9074729"

    def test_valid_imo_lowercase_prefix(self):
        """Test valid IMO number with lowercase prefix."""
        result = validate_imo("imo 9074729")
        assert result.valid is True
        assert result.normalized == "IMO9074729"

    def test_valid_imo_with_hyphen(self):
        """Test valid IMO number with hyphen."""
        result = validate_imo("IMO-9074729")
        assert result.valid is True
        assert result.normalized == "IMO9074729"

    def test_valid_imo_historical(self):
        """Test valid historical IMO number."""
        result = validate_imo("1234567")
        assert result.valid is True
        assert len(result.warnings) > 0
        assert "older vessel" in result.warnings[0]

    # Invalid IMO numbers
    def test_invalid_imo_wrong_check_digit(self):
        """Test invalid IMO number with wrong check digit."""
        result = validate_imo("9074728")
        assert result.valid is False
        assert len(result.errors) > 0
        assert "check digit validation failed" in result.errors[0]

    def test_invalid_imo_too_short(self):
        """Test invalid IMO number - too short."""
        result = validate_imo("IMO 123456")
        assert result.valid is False
        assert "exactly 7 digits" in result.errors[0]

    def test_invalid_imo_too_long(self):
        """Test invalid IMO number - too long."""
        result = validate_imo("IMO 12345678")
        assert result.valid is False
        assert "exactly 7 digits" in result.errors[0]

    def test_invalid_imo_with_letters(self):
        """Test invalid IMO number containing letters."""
        result = validate_imo("IMO 90747AB")
        assert result.valid is False
        assert "only numeric digits" in result.errors[0]

    def test_invalid_imo_leading_zeros(self):
        """Test invalid IMO number with leading zeros."""
        result = validate_imo("IMO 0074729")
        assert result.valid is False
        assert "leading zeros" in result.errors[0]

    def test_invalid_imo_below_range(self):
        """Test invalid IMO number below valid range."""
        result = validate_imo("0999999")
        assert result.valid is False
        assert "leading zeros" in result.errors[0]

    def test_invalid_imo_empty(self):
        """Test empty IMO number."""
        result = validate_imo("")
        assert result.valid is False
        assert "cannot be empty" in result.errors[0]

    # Check digit calculation tests
    def test_imo_check_digit_calculation_example_1(self):
        """Test check digit calculation for IMO 9074729."""
        result = validate_imo("9074729")
        assert result.info["check_digit"]["calculated"] == 9
        assert result.info["check_digit"]["actual"] == 9

    def test_imo_check_digit_calculation_example_2(self):
        """Test check digit calculation for IMO 9176187."""
        result = validate_imo("9176187")
        assert result.info["check_digit"]["calculated"] == 7
        assert result.info["check_digit"]["actual"] == 7

    # Era estimation tests
    def test_imo_era_estimation_modern(self):
        """Test era estimation for modern vessel."""
        result = validate_imo("9500000")
        assert "2020s" in result.info["estimated_era"]

    def test_imo_era_estimation_2010s(self):
        """Test era estimation for 2010s vessel."""
        result = validate_imo("9074729")
        assert "2010s-2020s" in result.info["estimated_era"]

    def test_imo_era_estimation_historical(self):
        """Test era estimation for historical vessel."""
        result = validate_imo("1234567")
        assert "Pre-1960s" in result.info["estimated_era"]

    # Strict format tests
    def test_strict_format_requires_prefix(self):
        """Test strict format mode requires IMO prefix."""
        result = validate_imo("9074729", strict_format=True, allow_without_prefix=False)
        assert result.valid is False
        assert "must start with 'IMO' prefix" in result.errors[0]

    # Batch validation tests
    def test_batch_validation(self):
        """Test batch IMO validation."""
        imo_list = ["9074729", "9176187", "9074728", "999999"]
        result = self.validator.validate_imo_batch(imo_list)

        assert result["summary"]["total"] == 4
        assert result["summary"]["valid"] == 2
        assert result["summary"]["invalid"] == 2
        assert result["summary"]["success_rate"] == "50.0%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
