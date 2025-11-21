"""
Tests for the CodePage class.
"""

import pytest
from escpos_printer.code_page import CodePage


class TestCodePageBasics:
    """Basic tests for CodePage class."""

    def test_create_with_iconv(self):
        """Test creating a CodePage with iconv encoding."""
        cp = CodePage('CP437', {'name': 'Code Page 437', 'iconv': 'CP437'})
        assert cp.get_id() == 'CP437'
        assert cp.get_name() == 'Code Page 437'
        assert cp.get_iconv() == 'CP437'

    def test_create_with_data(self):
        """Test creating a CodePage with explicit data."""
        # Create a simple code page with some characters
        data = ['ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß',
                'àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ',
                '                                ',
                '                                ']
        cp = CodePage('TEST', {'name': 'Test Page', 'data': data})
        assert cp.get_id() == 'TEST'
        assert cp.get_name() == 'Test Page'
        assert cp.is_encodable()

    def test_create_without_encoding(self):
        """Test creating a CodePage without encoding info."""
        cp = CodePage('UNKNOWN', {'name': 'Unknown Page'})
        assert cp.get_id() == 'UNKNOWN'
        assert not cp.is_encodable()

    def test_get_notes(self):
        """Test getting notes from a CodePage."""
        cp = CodePage('TEST', {'name': 'Test', 'notes': 'Some notes'})
        assert cp.get_notes() == 'Some notes'

    def test_get_notes_none(self):
        """Test getting notes when not set."""
        cp = CodePage('TEST', {'name': 'Test'})
        assert cp.get_notes() is None


class TestCodePageEncoding:
    """Tests for CodePage encoding functionality."""

    def test_is_encodable_with_iconv(self):
        """Test is_encodable with iconv."""
        cp = CodePage('CP437', {'iconv': 'CP437'})
        assert cp.is_encodable()

    def test_is_encodable_with_python_encode(self):
        """Test is_encodable with python_encode."""
        cp = CodePage('CP437', {'python_encode': 'cp437'})
        assert cp.is_encodable()

    def test_is_encodable_without_info(self):
        """Test is_encodable without encoding info."""
        cp = CodePage('TEST', {})
        assert not cp.is_encodable()

    def test_get_data_array_with_iconv(self):
        """Test getting data array with iconv encoding."""
        cp = CodePage('CP437', {'iconv': 'CP437'})
        data = cp.get_data_array()
        assert isinstance(data, list)
        assert len(data) == 128

    def test_get_data_array_raises_for_unencodable(self):
        """Test that get_data_array raises for unencodable page."""
        cp = CodePage('TEST', {})
        with pytest.raises(ValueError):
            cp.get_data_array()


class TestCodePageMissingChar:
    """Tests for missing character handling."""

    def test_missing_char_code(self):
        """Test the MISSING_CHAR_CODE constant."""
        assert CodePage.MISSING_CHAR_CODE == 0x20  # Space
