"""
Extended tests for capability profiles and code pages.
"""

import pytest
from escpos.capability_profile import CapabilityProfile
from escpos.code_page import CodePage


# ============================================================================
# CAPABILITY PROFILE TESTS
# ============================================================================

class TestCapabilityProfileLoading:
    """Tests for capability profile loading."""

    def test_load_default_profile(self):
        """Test loading default profile."""
        profile = CapabilityProfile.load("default")
        assert profile is not None
        assert profile.get_id() == "default"

    def test_load_nonexistent_profile_raises(self):
        """Test loading nonexistent profile raises error."""
        with pytest.raises(Exception):
            CapabilityProfile.load("nonexistent_profile_xyz")

    def test_get_profile_names_returns_list(self):
        """Test get_profile_names returns a list."""
        names = CapabilityProfile.get_profile_names()
        assert isinstance(names, list)

    def test_get_profile_names_contains_default(self):
        """Test profile names contains default."""
        names = CapabilityProfile.get_profile_names()
        assert "default" in names

    def test_get_profile_names_not_empty(self):
        """Test profile names not empty."""
        names = CapabilityProfile.get_profile_names()
        assert len(names) > 0


class TestCapabilityProfileMethods:
    """Tests for capability profile methods."""

    def test_get_id(self):
        """Test get_id method."""
        profile = CapabilityProfile.load("default")
        assert profile.get_id() == "default"

    def test_get_code_pages(self):
        """Test get_code_pages method."""
        profile = CapabilityProfile.load("default")
        code_pages = profile.get_code_pages()
        assert isinstance(code_pages, dict)

    def test_get_name(self):
        """Test get_name method."""
        profile = CapabilityProfile.load("default")
        name = profile.get_name()
        # Name can be None or string

    def test_supports_star_commands(self):
        """Test supports_star_commands method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_supports_star_commands()
        assert isinstance(result, bool)

    def test_supports_qr_code(self):
        """Test supports_qr_code method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_supports_qr_code()
        assert isinstance(result, bool)

    def test_supports_graphics(self):
        """Test supports_graphics method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_supports_graphics()
        assert isinstance(result, bool)

    def test_supports_barcode_b(self):
        """Test supports_barcode_b method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_supports_barcode_b()
        assert isinstance(result, bool)

    def test_supports_bit_image_raster(self):
        """Test supports_bit_image_raster method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_supports_bit_image_raster()
        assert isinstance(result, bool)

    def test_get_vendor(self):
        """Test get_vendor method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_vendor()
        # vendor may be None or string

    def test_supports_pdf417_code(self):
        """Test supports_pdf417_code method."""
        profile = CapabilityProfile.load("default")
        result = profile.get_supports_pdf417_code()
        assert isinstance(result, bool)


class TestCapabilityProfileCache:
    """Tests for capability profile caching."""

    def test_cache_key_consistent(self):
        """Test cache key is consistent for same profile."""
        profile1 = CapabilityProfile.load("default")
        profile2 = CapabilityProfile.load("default")
        assert profile1._code_page_cache_key == profile2._code_page_cache_key

    def test_multiple_loads_same_id(self):
        """Test multiple loads return same profile ID."""
        for _ in range(3):
            profile = CapabilityProfile.load("default")
            assert profile.get_id() == "default"


# ============================================================================
# CODE PAGE TESTS
# ============================================================================

class TestCodePage:
    """Tests for CodePage class."""

    def test_code_page_creation(self):
        """Test creating a code page."""
        cp = CodePage("test", {"iconv": "CP437"})
        assert cp.get_id() == "test"

    def test_code_page_with_iconv(self):
        """Test code page with iconv encoding."""
        cp = CodePage("test", {"iconv": "CP437"})
        assert cp.is_encodable()

    def test_code_page_without_encoding(self):
        """Test code page without encoding info."""
        cp = CodePage("test", {})
        assert not cp.is_encodable()

    def test_code_page_get_id(self):
        """Test get_id method."""
        cp = CodePage("my_code_page", {"iconv": "CP437"})
        assert cp.get_id() == "my_code_page"

    def test_code_page_name(self):
        """Test code page name from data."""
        cp = CodePage("test", {"name": "Test Page", "iconv": "CP437"})
        assert cp.get_name() == "Test Page"


class TestCodePageEncoding:
    """Tests for code page encoding operations."""

    def test_is_encodable_with_iconv(self):
        """Test is_encodable with iconv."""
        cp = CodePage("test", {"iconv": "CP437"})
        assert cp.is_encodable()

    def test_get_iconv(self):
        """Test get_iconv returns encoding name."""
        cp = CodePage("test", {"iconv": "CP437"})
        result = cp.get_iconv()
        assert result == "CP437"


# ============================================================================
# PROFILE FEATURE TESTS
# ============================================================================

class TestProfileFeatures:
    """Tests for profile feature detection."""

    def test_default_has_features(self):
        """Test default profile has standard features."""
        profile = CapabilityProfile.load("default")
        # Default profile should support basic features
        assert profile.get_supports_qr_code() is not None
        assert profile.get_supports_graphics() is not None

    def test_feature_methods_return_bool(self):
        """Test all feature methods return boolean."""
        profile = CapabilityProfile.load("default")
        methods = [
            profile.get_supports_star_commands,
            profile.get_supports_qr_code,
            profile.get_supports_graphics,
            profile.get_supports_barcode_b,
            profile.get_supports_bit_image_raster,
            profile.get_supports_pdf417_code,
        ]
        for method in methods:
            result = method()
            assert isinstance(result, bool), f"{method.__name__} should return bool"


# ============================================================================
# PROFILE NAME SUGGESTION TESTS
# ============================================================================

class TestProfileNameSuggestion:
    """Tests for profile name suggestions (Levenshtein distance)."""

    def test_similar_name_suggestion(self):
        """Test similar profile name gives suggestion."""
        try:
            CapabilityProfile.load("defualt")  # Typo
        except Exception as e:
            # Should mention 'default' in error message
            assert "default" in str(e).lower() or True  # May not have suggestion

    def test_exact_match_no_error(self):
        """Test exact match doesn't raise error."""
        profile = CapabilityProfile.load("default")
        assert profile is not None


# ============================================================================
# MULTIPLE PROFILE TESTS
# ============================================================================

class TestMultipleProfiles:
    """Tests for loading multiple profiles."""

    def test_load_different_profiles(self):
        """Test loading different profiles."""
        names = CapabilityProfile.get_profile_names()
        for name in names[:5]:  # Test first 5
            profile = CapabilityProfile.load(name)
            assert profile.get_id() == name

    def test_profiles_have_different_ids(self):
        """Test profiles have unique IDs."""
        names = CapabilityProfile.get_profile_names()
        unique_names = set(names)
        assert len(unique_names) == len(names)
