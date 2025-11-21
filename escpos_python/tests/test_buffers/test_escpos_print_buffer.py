"""
Tests for the EscposPrintBuffer class.
"""

import pytest
from escpos_printer.buffers.escpos_print_buffer import EscposPrintBuffer
from escpos_printer.printer import Printer
from escpos_printer.connectors.dummy_connector import DummyConnector


class TestEscposPrintBuffer:
    """Tests for EscposPrintBuffer."""

    def test_create_buffer(self):
        """Test creating a buffer."""
        buffer = EscposPrintBuffer()
        assert buffer is not None
        assert buffer.get_printer() is None

    def test_write_text_without_printer_raises(self):
        """Test that writing without printer raises error."""
        buffer = EscposPrintBuffer()
        with pytest.raises(RuntimeError):
            buffer.write_text("Test")

    def test_write_text_raw_without_printer_raises(self):
        """Test that writing raw without printer raises error."""
        buffer = EscposPrintBuffer()
        with pytest.raises(RuntimeError):
            buffer.write_text_raw("Test")

    def test_flush_without_printer_raises(self):
        """Test that flush without printer raises error."""
        buffer = EscposPrintBuffer()
        with pytest.raises(RuntimeError):
            buffer.flush()

    def test_set_printer(self):
        """Test setting a printer."""
        buffer = EscposPrintBuffer()
        connector = DummyConnector()
        printer = Printer(connector)

        # The printer automatically sets its buffer
        assert printer.get_print_buffer() is not None

        connector.finalize()


class TestEscposPrintBufferWithPrinter:
    """Tests for EscposPrintBuffer with a printer attached."""

    @pytest.fixture
    def setup(self):
        """Set up connector, printer, and buffer."""
        connector = DummyConnector()
        printer = Printer(connector)
        buffer = printer.get_print_buffer()
        yield connector, printer, buffer
        connector.finalize()

    def test_write_text_ascii(self, setup):
        """Test writing ASCII text."""
        connector, printer, buffer = setup
        printer.text("Hello World\n")
        data = connector.get_data()
        assert b"Hello World\n" in data

    def test_write_text_raw(self, setup):
        """Test writing raw text."""
        connector, printer, buffer = setup
        buffer.write_text_raw("Test\n")
        data = connector.get_data()
        assert b"Test\n" in data

    def test_write_text_empty(self, setup):
        """Test writing empty text."""
        connector, printer, buffer = setup
        buffer.write_text_raw("")
        # Should not crash

    def test_replacement_char(self):
        """Test the replacement character constant."""
        assert EscposPrintBuffer.REPLACEMENT_CHAR == "?"
