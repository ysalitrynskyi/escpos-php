"""
Tests for the MultipleConnector class.
"""

import pytest
from escpos_thermal.connectors.dummy_connector import DummyConnector
from escpos_thermal.connectors.multiple_connector import MultipleConnector


class TestMultipleConnector:
    """Tests for MultipleConnector."""

    def test_create_empty(self):
        """Test creating an empty MultipleConnector."""
        connector = MultipleConnector()
        connector.finalize()

    def test_create_with_connectors(self):
        """Test creating with multiple connectors."""
        d1 = DummyConnector()
        d2 = DummyConnector()
        connector = MultipleConnector(d1, d2)
        connector.finalize()

    def test_write_to_all(self):
        """Test writing to all connected connectors."""
        d1 = DummyConnector()
        d2 = DummyConnector()
        connector = MultipleConnector(d1, d2)

        connector.write(b"Hello")

        assert d1.get_data() == b"Hello"
        assert d2.get_data() == b"Hello"
        connector.finalize()

    def test_read_returns_false(self):
        """Test that read returns False."""
        d1 = DummyConnector()
        connector = MultipleConnector(d1)

        result = connector.read(10)
        assert result is False
        connector.finalize()

    def test_finalize_all(self):
        """Test that finalize closes all connectors."""
        d1 = DummyConnector()
        d2 = DummyConnector()
        connector = MultipleConnector(d1, d2)

        d1.write(b"Test1")
        d2.write(b"Test2")

        connector.finalize()

        # After finalize, both should be empty
        assert d1.get_data() == b""
        assert d2.get_data() == b""
