"""
Extended tests for connectors.
"""

import pytest
import tempfile
import os
from escpos_printer.connectors.dummy_connector import DummyConnector
from escpos_printer.connectors.file_connector import FileConnector
from escpos_printer.connectors.multiple_connector import MultipleConnector
from escpos_printer.connectors.uri_connector import UriConnector


# ============================================================================
# DUMMY CONNECTOR EXTENDED TESTS
# ============================================================================

class TestDummyConnectorExtended:
    """Extended tests for DummyConnector."""

    def test_write_bytes(self):
        """Test writing bytes."""
        connector = DummyConnector()
        connector.write(b"Hello")
        assert connector.get_data() == b"Hello"

    def test_write_multiple(self):
        """Test writing multiple times accumulates."""
        connector = DummyConnector()
        connector.write(b"Hello")
        connector.write(b" ")
        connector.write(b"World")
        # get_data returns accumulated data
        assert b"Hello" in connector.get_data()

    def test_finalize_works(self):
        """Test finalize doesn't raise."""
        connector = DummyConnector()
        connector.write(b"Test")
        connector.finalize()  # Should not raise

    def test_read_returns_empty(self):
        """Test read returns empty bytes."""
        connector = DummyConnector()
        assert connector.read(10) == b""

    def test_write_empty(self):
        """Test writing empty bytes."""
        connector = DummyConnector()
        connector.write(b"")
        connector.finalize()

    def test_large_write(self):
        """Test writing large data."""
        connector = DummyConnector()
        data = b"X" * 10000
        connector.write(data)
        assert len(connector.get_data()) == 10000


# ============================================================================
# FILE CONNECTOR TESTS
# ============================================================================

class TestFileConnectorExtended:
    """Extended tests for FileConnector."""

    def test_write_to_temp_file(self):
        """Test writing to temporary file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.write(b"Test data")
            connector.finalize()

            with open(temp_path, 'rb') as f:
                assert f.read() == b"Test data"
        finally:
            os.unlink(temp_path)

    def test_multiple_writes(self):
        """Test multiple writes to file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.write(b"First ")
            connector.write(b"Second")
            connector.finalize()

            with open(temp_path, 'rb') as f:
                assert f.read() == b"First Second"
        finally:
            os.unlink(temp_path)

    def test_finalize_closes_file(self):
        """Test that finalize closes the file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.write(b"Test")
            connector.finalize()
            # Should be able to finalize again without error
            connector.finalize()
        finally:
            os.unlink(temp_path)


# ============================================================================
# MULTIPLE CONNECTOR TESTS
# ============================================================================

class TestMultipleConnectorExtended:
    """Extended tests for MultipleConnector."""

    def test_write_to_multiple(self):
        """Test writing to multiple connectors."""
        conn1 = DummyConnector()
        conn2 = DummyConnector()
        multi = MultipleConnector(conn1, conn2)  # Uses *args

        multi.write(b"Test")

        assert conn1.get_data() == b"Test"
        assert conn2.get_data() == b"Test"

    def test_finalize_all(self):
        """Test finalizing all connectors."""
        conn1 = DummyConnector()
        conn2 = DummyConnector()
        multi = MultipleConnector(conn1, conn2)

        multi.write(b"Data")
        multi.finalize()  # Should not raise

    def test_three_connectors(self):
        """Test with three connectors."""
        conn1 = DummyConnector()
        conn2 = DummyConnector()
        conn3 = DummyConnector()
        multi = MultipleConnector(conn1, conn2, conn3)

        multi.write(b"Data")

        assert conn1.get_data() == b"Data"
        assert conn2.get_data() == b"Data"
        assert conn3.get_data() == b"Data"


# ============================================================================
# URI CONNECTOR TESTS
# ============================================================================

class TestUriConnectorExtended:
    """Extended tests for UriConnector factory."""

    def test_file_uri(self):
        """Test file:// URI."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = UriConnector.get(f"file://{temp_path}")
            assert isinstance(connector, FileConnector)
            connector.finalize()
        finally:
            os.unlink(temp_path)

    def test_invalid_scheme_raises(self):
        """Test invalid URI scheme raises error."""
        with pytest.raises(Exception):
            UriConnector.get("invalid://something")

    def test_empty_uri_raises(self):
        """Test empty URI raises error."""
        with pytest.raises(Exception):
            UriConnector.get("")


# ============================================================================
# CONNECTOR INTERFACE TESTS
# ============================================================================

class TestConnectorInterface:
    """Tests for connector interface compliance."""

    def test_dummy_has_write(self):
        """Test DummyConnector has write method."""
        connector = DummyConnector()
        assert hasattr(connector, 'write')
        assert callable(connector.write)
        connector.finalize()

    def test_dummy_has_read(self):
        """Test DummyConnector has read method."""
        connector = DummyConnector()
        assert hasattr(connector, 'read')
        assert callable(connector.read)
        connector.finalize()

    def test_dummy_has_finalize(self):
        """Test DummyConnector has finalize method."""
        connector = DummyConnector()
        assert hasattr(connector, 'finalize')
        assert callable(connector.finalize)
        connector.finalize()

    def test_file_has_write(self):
        """Test FileConnector has write method."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            connector = FileConnector(temp_path)
            assert hasattr(connector, 'write')
            connector.finalize()
        finally:
            os.unlink(temp_path)
