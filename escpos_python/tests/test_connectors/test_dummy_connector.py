"""
Tests for the DummyConnector class.
"""

import pytest
from escpos_thermal.connectors.dummy_connector import DummyConnector


class TestDummyConnector:
    """Tests for DummyConnector."""

    def test_create_connector(self):
        """Test creating a DummyConnector."""
        connector = DummyConnector()
        assert connector is not None
        connector.finalize()

    def test_write_and_get_data(self):
        """Test writing data and retrieving it."""
        connector = DummyConnector()
        connector.write(b"Hello")
        connector.write(b"World")
        assert connector.get_data() == b"HelloWorld"
        connector.finalize()

    def test_get_data_empty(self):
        """Test getting data when nothing written."""
        connector = DummyConnector()
        assert connector.get_data() == b""
        connector.finalize()

    def test_clear(self):
        """Test clearing the buffer."""
        connector = DummyConnector()
        connector.write(b"Hello")
        connector.clear()
        assert connector.get_data() == b""
        connector.finalize()

    def test_read_with_set_data(self):
        """Test reading with pre-set data."""
        connector = DummyConnector()
        connector.set_read_data(b"Response")
        assert connector.read(8) == b"Response"
        connector.finalize()

    def test_read_partial(self):
        """Test reading partial data."""
        connector = DummyConnector()
        connector.set_read_data(b"Response")
        assert connector.read(4) == b"Resp"
        connector.finalize()

    def test_finalize(self):
        """Test finalizing the connector."""
        connector = DummyConnector()
        connector.write(b"Test")
        connector.finalize()
        # After finalize, get_data returns empty
        assert connector.get_data() == b""


class TestDummyConnectorMultipleWrites:
    """Tests for multiple write operations."""

    def test_multiple_writes(self):
        """Test multiple write calls."""
        connector = DummyConnector()
        for i in range(10):
            connector.write(f"Line {i}\n".encode())
        data = connector.get_data()
        assert b"Line 0" in data
        assert b"Line 9" in data
        connector.finalize()
