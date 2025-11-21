"""
Tests for the UriConnector class.
"""

import pytest
import tempfile
import os
from escpos_thermal.connectors.uri_connector import UriConnector
from escpos_thermal.connectors.file_connector import FileConnector
from escpos_thermal.connectors.network_connector import NetworkConnector


class TestUriConnector:
    """Tests for UriConnector factory."""

    def test_file_uri(self):
        """Test creating a FileConnector from file:// URI."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = UriConnector.get(f"file://{temp_path}")
            assert isinstance(connector, FileConnector)
            connector.finalize()
        finally:
            os.unlink(temp_path)

    def test_tcp_uri_invalid_host(self):
        """Test that tcp:// with invalid host raises an error."""
        with pytest.raises(ValueError):
            UriConnector.get("tcp://")

    def test_unsupported_scheme_raises(self):
        """Test that unsupported URI scheme raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            UriConnector.get("ftp://example.com/printer")
        assert 'Unsupported URI scheme' in str(exc_info.value)

    def test_empty_file_path_raises(self):
        """Test that empty file path raises ValueError."""
        with pytest.raises(ValueError):
            UriConnector.get("file://")


class TestUriConnectorParsing:
    """Tests for URI parsing."""

    def test_parse_file_uri(self):
        """Test parsing file:// URI."""
        # The path should be extracted correctly
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            connector = UriConnector.get(f"file://{temp_path}")
            assert connector is not None
            connector.finalize()
        finally:
            os.unlink(temp_path)
