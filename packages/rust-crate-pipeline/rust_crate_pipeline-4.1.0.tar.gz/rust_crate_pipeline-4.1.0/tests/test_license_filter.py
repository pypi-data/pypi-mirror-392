"""Tests for license filtering module."""

import pytest

from rust_crate_pipeline.utils.license_filter import (
    LicenseCheckResult,
    LicenseFilter,
)


class TestLicenseCheckResult:
    """Test LicenseCheckResult dataclass."""
    
    def test_is_allowed(self):
        """Test is_allowed method."""
        result = LicenseCheckResult(
            detected_licenses=["MIT"],
            status="allowed",
            message="License is allowed",
            confidence=1.0
        )
        assert result.is_allowed() is True
        assert result.is_forbidden() is False
        assert result.requires_review() is False
    
    def test_is_forbidden(self):
        """Test is_forbidden method."""
        result = LicenseCheckResult(
            detected_licenses=["GPL-3.0"],
            status="forbidden",
            message="License is forbidden",
            confidence=1.0
        )
        assert result.is_allowed() is False
        assert result.is_forbidden() is True
        assert result.requires_review() is False
    
    def test_requires_review(self):
        """Test requires_review method."""
        result = LicenseCheckResult(
            detected_licenses=["Unknown"],
            status="unknown",
            message="License requires review",
            confidence=0.5
        )
        assert result.is_allowed() is False
        assert result.is_forbidden() is False
        assert result.requires_review() is True


class TestLicenseFilter:
    """Test LicenseFilter class."""
    
    def test_init_defaults(self):
        """Test initialization with default values."""
        filter_obj = LicenseFilter()
        assert isinstance(filter_obj.allowed_licenses, set)
        assert isinstance(filter_obj.denied_licenses, set)
        assert filter_obj.require_explicit_allow is False
    
    def test_init_custom(self):
        """Test initialization with custom values."""
        filter_obj = LicenseFilter(
            allowed_licenses=["MIT", "Apache-2.0"],
            denied_licenses=["GPL-3.0"],
            require_explicit_allow=True
        )
        assert "mit" in filter_obj.allowed_licenses
        assert "apache-2.0" in filter_obj.allowed_licenses
        assert "gpl-3.0" in filter_obj.denied_licenses
        assert filter_obj.require_explicit_allow is True
    
    def test_split_license_expression_simple(self):
        """Test splitting simple license expressions."""
        filter_obj = LicenseFilter()
        assert filter_obj._split_license_expression("MIT") == ["MIT"]
        assert filter_obj._split_license_expression("Apache-2.0") == ["Apache-2.0"]
    
    def test_split_license_expression_or(self):
        """Test splitting OR expressions."""
        filter_obj = LicenseFilter()
        licenses = filter_obj._split_license_expression("MIT OR Apache-2.0")
        assert "MIT" in licenses
        assert "Apache-2.0" in licenses
    
    def test_split_license_expression_and(self):
        """Test splitting AND expressions."""
        filter_obj = LicenseFilter()
        licenses = filter_obj._split_license_expression("MIT AND BSD-3-Clause")
        assert "MIT" in licenses
        assert "BSD-3-Clause" in licenses
    
    def test_split_license_expression_empty(self):
        """Test splitting empty expressions."""
        filter_obj = LicenseFilter()
        assert filter_obj._split_license_expression("") == []
        assert filter_obj._split_license_expression(None) == []
    
    def test_check_license_allowed(self):
        """Test checking allowed licenses."""
        filter_obj = LicenseFilter()
        result = filter_obj.check_license("MIT")
        assert result.is_allowed() is True
        assert result.status == "allowed"
        assert "MIT" in result.detected_licenses
    
    def test_check_license_forbidden(self):
        """Test checking forbidden licenses."""
        filter_obj = LicenseFilter()
        result = filter_obj.check_license("GPL-3.0")
        assert result.is_forbidden() is True
        assert result.status == "forbidden"
    
    def test_check_license_unknown(self):
        """Test checking unknown licenses."""
        filter_obj = LicenseFilter(require_explicit_allow=True)
        result = filter_obj.check_license("Custom-License")
        assert result.requires_review() is True
        assert result.status in ("unknown", "warning")
    
    def test_check_license_from_text(self):
        """Test license detection from text."""
        filter_obj = LicenseFilter()
        
        # Test with Cargo.toml style text
        cargo_text = 'license = "MIT"'
        result = filter_obj.check_license_from_text(cargo_text)
        assert result.is_allowed() is True
        
        # Test with README style text
        readme_text = "This project is licensed under the MIT License."
        result = filter_obj.check_license_from_text(readme_text)
        assert result.is_allowed() is True
    
    def test_check_license_from_text_forbidden(self):
        """Test detecting forbidden licenses from text."""
        filter_obj = LicenseFilter()
        text = "This project is licensed under GPL-3.0"
        result = filter_obj.check_license_from_text(text)
        assert result.is_forbidden() is True
    
    def test_check_license_from_text_multiple(self):
        """Test detecting multiple licenses."""
        filter_obj = LicenseFilter()
        text = "Licensed under MIT OR Apache-2.0"
        result = filter_obj.check_license_from_text(text)
        assert len(result.detected_licenses) >= 1
    
    def test_check_license_from_text_no_license(self):
        """Test text with no license information."""
        filter_obj = LicenseFilter()
        text = "This is just some random text without license information."
        result = filter_obj.check_license_from_text(text)
        assert result.status in ("unknown", "warning")
        assert result.confidence < 0.5
    
    def test_check_license_case_insensitive(self):
        """Test that license checking is case-insensitive."""
        filter_obj = LicenseFilter()
        result1 = filter_obj.check_license("MIT")
        result2 = filter_obj.check_license("mit")
        result3 = filter_obj.check_license("Mit")
        
        assert result1.status == result2.status == result3.status
    
    def test_check_license_with_custom_allowed(self):
        """Test with custom allowed licenses."""
        filter_obj = LicenseFilter(
            allowed_licenses=["Custom-License"],
            require_explicit_allow=True
        )
        result = filter_obj.check_license("Custom-License")
        assert result.is_allowed() is True
    
    def test_check_license_with_custom_denied(self):
        """Test with custom denied licenses."""
        filter_obj = LicenseFilter(denied_licenses=["Proprietary"])
        result = filter_obj.check_license("Proprietary")
        assert result.is_forbidden() is True

