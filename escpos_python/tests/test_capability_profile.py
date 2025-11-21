"""
Tests for the CapabilityProfile class.
"""

import pytest
from escpos_thermal.capability_profile import CapabilityProfile


class TestCapabilityProfileLoading:
    """Tests for loading capability profiles."""

    def test_load_default_profile(self):
        """Test loading the default profile."""
        profile = CapabilityProfile.load('default')
        assert profile is not None
        assert profile.get_id() == 'default'

    def test_load_simple_profile(self):
        """Test loading the simple profile."""
        profile = CapabilityProfile.load('simple')
        assert profile is not None
        assert profile.get_id() == 'simple'

    def test_load_invalid_profile_raises(self):
        """Test that loading an invalid profile raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            CapabilityProfile.load('nonexistent_profile_xyz')
        assert 'does not exist' in str(exc_info.value)

    def test_get_profile_names(self):
        """Test getting all profile names."""
        names = CapabilityProfile.get_profile_names()
        assert isinstance(names, list)
        assert 'default' in names
        assert 'simple' in names
        assert len(names) > 0


class TestCapabilityProfileFeatures:
    """Tests for profile features."""

    def test_get_supports_barcode_b(self, default_profile):
        """Test getting barcodeB support."""
        result = default_profile.get_supports_barcode_b()
        assert isinstance(result, bool)

    def test_get_supports_qr_code(self, default_profile):
        """Test getting QR code support."""
        result = default_profile.get_supports_qr_code()
        assert isinstance(result, bool)

    def test_get_supports_graphics(self, default_profile):
        """Test getting graphics support."""
        result = default_profile.get_supports_graphics()
        assert isinstance(result, bool)

    def test_get_supports_pdf417_code(self, default_profile):
        """Test getting PDF417 support."""
        result = default_profile.get_supports_pdf417_code()
        assert isinstance(result, bool)

    def test_get_supports_star_commands(self, default_profile):
        """Test getting Star commands support."""
        result = default_profile.get_supports_star_commands()
        assert isinstance(result, bool)

    def test_get_invalid_feature_raises(self, default_profile):
        """Test that getting an invalid feature raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            default_profile.get_feature('nonexistent_feature_xyz')
        assert 'does not exist' in str(exc_info.value)


class TestCapabilityProfileProperties:
    """Tests for profile properties."""

    def test_get_id(self, default_profile):
        """Test getting profile ID."""
        assert default_profile.get_id() == 'default'

    def test_get_name(self, default_profile):
        """Test getting profile name."""
        name = default_profile.get_name()
        assert isinstance(name, str)
        assert len(name) > 0

    def test_get_vendor(self, default_profile):
        """Test getting profile vendor."""
        vendor = default_profile.get_vendor()
        assert isinstance(vendor, str)

    def test_get_code_pages(self, default_profile):
        """Test getting code pages."""
        code_pages = default_profile.get_code_pages()
        assert isinstance(code_pages, dict)

    def test_get_code_page_cache_key(self, default_profile):
        """Test getting code page cache key."""
        key = default_profile.get_code_page_cache_key()
        assert isinstance(key, str)
        assert len(key) > 0


class TestCapabilityProfileSuggestions:
    """Tests for profile name suggestions."""

    def test_suggest_nearest(self):
        """Test the suggest_nearest method."""
        suggestions = CapabilityProfile._suggest_nearest(
            'dafault',  # Typo
            ['default', 'simple', 'complex'],
            2
        )
        assert 'default' in suggestions

    def test_invalid_profile_suggests_alternatives(self):
        """Test that invalid profile names suggest alternatives."""
        with pytest.raises(ValueError) as exc_info:
            CapabilityProfile.load('defalt')  # Typo
        error_message = str(exc_info.value)
        assert 'default' in error_message or 'simple' in error_message
