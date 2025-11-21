"""
Tests for the Printer class.
"""

import pytest
from escpos.printer import Printer
from escpos.connectors.dummy_connector import DummyConnector
from tests.conftest import check_output


class TestPrinterInitialization:
    """Tests for printer initialization."""

    def test_initialize_output(self, printer, dummy_connector):
        """Test that initialize() sends correct ESC command."""
        check_output(dummy_connector, b"\x1b@")

    def test_initialize_resets_character_table(self, printer):
        """Test that initialize() resets character table to 0."""
        assert printer.get_character_table() == 0


class TestPrinterText:
    """Tests for text output."""

    def test_text_string_output(self, printer, dummy_connector):
        """Test basic text output."""
        printer.text("The quick brown fox jumps over the lazy dog\n")
        check_output(dummy_connector, b"\x1b@The quick brown fox jumps over the lazy dog\n")

    def test_text_raw(self, printer, dummy_connector):
        """Test raw text output without encoding conversion."""
        printer.text_raw("Test\n")
        check_output(dummy_connector, b"\x1b@Test\n")

    def test_text_empty(self, printer, dummy_connector):
        """Test empty text."""
        printer.text("")
        check_output(dummy_connector, b"\x1b@")


class TestPrinterFeed:
    """Tests for feed operations."""

    def test_feed_default(self, printer, dummy_connector):
        """Test default feed (1 line)."""
        printer.feed()
        check_output(dummy_connector, b"\x1b@\x0a")

    def test_feed_3_lines(self, printer, dummy_connector):
        """Test feeding 3 lines."""
        printer.feed(3)
        check_output(dummy_connector, b"\x1b@\x1bd\x03")

    def test_feed_zero_raises(self, printer):
        """Test that feed(0) raises an error."""
        with pytest.raises(ValueError):
            printer.feed(0)

    def test_feed_too_large_raises(self, printer):
        """Test that feed(256) raises an error."""
        with pytest.raises(ValueError):
            printer.feed(256)

    def test_feed_reverse(self, printer, dummy_connector):
        """Test reverse feed."""
        printer.feed_reverse(2)
        check_output(dummy_connector, b"\x1b@\x1be\x02")


class TestPrinterPrintMode:
    """Tests for print mode selection."""

    def test_select_print_mode_default(self, printer, dummy_connector):
        """Test default print mode."""
        printer.select_print_mode()
        check_output(dummy_connector, b"\x1b@\x1b!\x00")

    def test_select_print_mode_font_b(self, printer, dummy_connector):
        """Test Font B print mode."""
        printer.select_print_mode(Printer.MODE_FONT_B)
        check_output(dummy_connector, b"\x1b@\x1b!\x01")

    def test_select_print_mode_emphasized(self, printer, dummy_connector):
        """Test emphasized print mode."""
        printer.select_print_mode(Printer.MODE_EMPHASIZED)
        check_output(dummy_connector, b"\x1b@\x1b!\x08")

    def test_select_print_mode_combined(self, printer, dummy_connector):
        """Test combined print modes."""
        printer.select_print_mode(Printer.MODE_DOUBLE_HEIGHT | Printer.MODE_DOUBLE_WIDTH)
        check_output(dummy_connector, b"\x1b@\x1b!\x30")

    def test_select_print_mode_invalid_raises(self, printer):
        """Test that invalid mode raises an error."""
        with pytest.raises(ValueError):
            printer.select_print_mode(-1)


class TestPrinterUnderline:
    """Tests for underline settings."""

    def test_set_underline_default(self, printer, dummy_connector):
        """Test default underline (single)."""
        printer.set_underline()
        check_output(dummy_connector, b"\x1b@\x1b-\x01")

    def test_set_underline_off(self, printer, dummy_connector):
        """Test underline off."""
        printer.set_underline(Printer.UNDERLINE_NONE)
        check_output(dummy_connector, b"\x1b@\x1b-\x00")

    def test_set_underline_single(self, printer, dummy_connector):
        """Test single underline."""
        printer.set_underline(Printer.UNDERLINE_SINGLE)
        check_output(dummy_connector, b"\x1b@\x1b-\x01")

    def test_set_underline_double(self, printer, dummy_connector):
        """Test double underline."""
        printer.set_underline(Printer.UNDERLINE_DOUBLE)
        check_output(dummy_connector, b"\x1b@\x1b-\x02")

    def test_set_underline_too_large_raises(self, printer):
        """Test that invalid underline value raises an error."""
        with pytest.raises(ValueError):
            printer.set_underline(3)


class TestPrinterEmphasis:
    """Tests for emphasis settings."""

    def test_set_emphasis_default(self, printer, dummy_connector):
        """Test default emphasis (on)."""
        printer.set_emphasis()
        check_output(dummy_connector, b"\x1b@\x1bE\x01")

    def test_set_emphasis_on(self, printer, dummy_connector):
        """Test emphasis on."""
        printer.set_emphasis(True)
        check_output(dummy_connector, b"\x1b@\x1bE\x01")

    def test_set_emphasis_off(self, printer, dummy_connector):
        """Test emphasis off."""
        printer.set_emphasis(False)
        check_output(dummy_connector, b"\x1b@\x1bE\x00")


class TestPrinterDoubleStrike:
    """Tests for double strike settings."""

    def test_set_double_strike_default(self, printer, dummy_connector):
        """Test default double strike (on)."""
        printer.set_double_strike()
        check_output(dummy_connector, b"\x1b@\x1bG\x01")

    def test_set_double_strike_on(self, printer, dummy_connector):
        """Test double strike on."""
        printer.set_double_strike(True)
        check_output(dummy_connector, b"\x1b@\x1bG\x01")

    def test_set_double_strike_off(self, printer, dummy_connector):
        """Test double strike off."""
        printer.set_double_strike(False)
        check_output(dummy_connector, b"\x1b@\x1bG\x00")


class TestPrinterFont:
    """Tests for font settings."""

    def test_set_font_a(self, printer, dummy_connector):
        """Test Font A."""
        printer.set_font(Printer.FONT_A)
        check_output(dummy_connector, b"\x1b@\x1bM\x00")

    def test_set_font_b(self, printer, dummy_connector):
        """Test Font B."""
        printer.set_font(Printer.FONT_B)
        check_output(dummy_connector, b"\x1b@\x1bM\x01")

    def test_set_font_c(self, printer, dummy_connector):
        """Test Font C."""
        printer.set_font(Printer.FONT_C)
        check_output(dummy_connector, b"\x1b@\x1bM\x02")


class TestPrinterJustification:
    """Tests for justification settings."""

    def test_set_justification_left(self, printer, dummy_connector):
        """Test left justification."""
        printer.set_justification(Printer.JUSTIFY_LEFT)
        check_output(dummy_connector, b"\x1b@\x1ba\x00")

    def test_set_justification_center(self, printer, dummy_connector):
        """Test center justification."""
        printer.set_justification(Printer.JUSTIFY_CENTER)
        check_output(dummy_connector, b"\x1b@\x1ba\x01")

    def test_set_justification_right(self, printer, dummy_connector):
        """Test right justification."""
        printer.set_justification(Printer.JUSTIFY_RIGHT)
        check_output(dummy_connector, b"\x1b@\x1ba\x02")


class TestPrinterTextSize:
    """Tests for text size settings."""

    def test_set_text_size_normal(self, printer, dummy_connector):
        """Test normal text size."""
        printer.set_text_size(1, 1)
        check_output(dummy_connector, b"\x1b@\x1d!\x00")

    def test_set_text_size_double_width(self, printer, dummy_connector):
        """Test double width."""
        printer.set_text_size(2, 1)
        check_output(dummy_connector, b"\x1b@\x1d!\x10")

    def test_set_text_size_double_height(self, printer, dummy_connector):
        """Test double height."""
        printer.set_text_size(1, 2)
        check_output(dummy_connector, b"\x1b@\x1d!\x01")

    def test_set_text_size_max(self, printer, dummy_connector):
        """Test maximum text size (8x8)."""
        printer.set_text_size(8, 8)
        check_output(dummy_connector, b"\x1b@\x1d!\x77")

    def test_set_text_size_invalid_raises(self, printer):
        """Test that invalid size raises an error."""
        with pytest.raises(ValueError):
            printer.set_text_size(0, 1)
        with pytest.raises(ValueError):
            printer.set_text_size(9, 1)


class TestPrinterColor:
    """Tests for color settings."""

    def test_set_color_1(self, printer, dummy_connector):
        """Test color 1 (usually black)."""
        printer.set_color(Printer.COLOR_1)
        check_output(dummy_connector, b"\x1b@\x1br\x00")

    def test_set_color_2(self, printer, dummy_connector):
        """Test color 2 (usually red)."""
        printer.set_color(Printer.COLOR_2)
        check_output(dummy_connector, b"\x1b@\x1br\x01")


class TestPrinterReverseColors:
    """Tests for reverse color settings."""

    def test_set_reverse_colors_on(self, printer, dummy_connector):
        """Test reverse colors on."""
        printer.set_reverse_colors(True)
        check_output(dummy_connector, b"\x1b@\x1dB\x01")

    def test_set_reverse_colors_off(self, printer, dummy_connector):
        """Test reverse colors off."""
        printer.set_reverse_colors(False)
        check_output(dummy_connector, b"\x1b@\x1dB\x00")


class TestPrinterUpsideDown:
    """Tests for upside down settings."""

    def test_set_upside_down_on(self, printer, dummy_connector):
        """Test upside down on."""
        printer.set_upside_down(True)
        check_output(dummy_connector, b"\x1b@\x1b{\x01")

    def test_set_upside_down_off(self, printer, dummy_connector):
        """Test upside down off."""
        printer.set_upside_down(False)
        check_output(dummy_connector, b"\x1b@\x1b{\x00")


class TestPrinterCut:
    """Tests for paper cutting."""

    def test_cut_full(self, printer, dummy_connector):
        """Test full cut."""
        printer.cut(Printer.CUT_FULL)
        check_output(dummy_connector, b"\x1b@\x1dVA\x03")

    def test_cut_partial(self, printer, dummy_connector):
        """Test partial cut."""
        printer.cut(Printer.CUT_PARTIAL)
        check_output(dummy_connector, b"\x1b@\x1dVB\x03")

    def test_cut_with_lines(self, printer, dummy_connector):
        """Test cut with custom line feed."""
        printer.cut(Printer.CUT_FULL, 5)
        check_output(dummy_connector, b"\x1b@\x1dVA\x05")


class TestPrinterPulse:
    """Tests for cash drawer pulse."""

    def test_pulse_default(self, printer, dummy_connector):
        """Test default pulse."""
        printer.pulse()
        check_output(dummy_connector, b"\x1b@\x1bp0<x")

    def test_pulse_pin_1(self, printer, dummy_connector):
        """Test pulse on pin 1."""
        printer.pulse(pin=1)
        check_output(dummy_connector, b"\x1b@\x1bp1<x")


class TestPrinterBarcode:
    """Tests for barcode printing."""

    def test_set_barcode_height(self, printer, dummy_connector):
        """Test setting barcode height."""
        printer.set_barcode_height(100)
        check_output(dummy_connector, b"\x1b@\x1dhd")

    def test_set_barcode_width(self, printer, dummy_connector):
        """Test setting barcode width."""
        printer.set_barcode_width(3)
        check_output(dummy_connector, b"\x1b@\x1dw\x03")

    def test_set_barcode_text_position_none(self, printer, dummy_connector):
        """Test barcode text position none."""
        printer.set_barcode_text_position(Printer.BARCODE_TEXT_NONE)
        check_output(dummy_connector, b"\x1b@\x1dH\x00")

    def test_set_barcode_text_position_below(self, printer, dummy_connector):
        """Test barcode text position below."""
        printer.set_barcode_text_position(Printer.BARCODE_TEXT_BELOW)
        check_output(dummy_connector, b"\x1b@\x1dH\x02")

    def test_barcode_code39(self, printer, dummy_connector):
        """Test CODE39 barcode."""
        printer.barcode("ABC123", Printer.BARCODE_CODE39)
        check_output(dummy_connector, b"\x1b@\x1dkE\x06ABC123")

    def test_barcode_invalid_type_raises(self, printer):
        """Test that invalid barcode type raises an error."""
        with pytest.raises(ValueError):
            printer.barcode("123", 100)


class TestPrinterLineSpacing:
    """Tests for line spacing settings."""

    def test_set_line_spacing_default(self, printer, dummy_connector):
        """Test resetting line spacing to default."""
        printer.set_line_spacing()
        check_output(dummy_connector, b"\x1b@\x1b2")

    def test_set_line_spacing_custom(self, printer, dummy_connector):
        """Test custom line spacing."""
        printer.set_line_spacing(24)
        check_output(dummy_connector, b"\x1b@\x1b3\x18")


class TestPrinterMargins:
    """Tests for margin settings."""

    def test_set_print_left_margin(self, printer, dummy_connector):
        """Test setting left margin."""
        printer.set_print_left_margin(50)
        check_output(dummy_connector, b"\x1b@\x1dL2\x00")

    def test_set_print_width(self, printer, dummy_connector):
        """Test setting print width."""
        printer.set_print_width(400)
        check_output(dummy_connector, b"\x1b@\x1dW\x90\x01")


class TestPrinterConstants:
    """Tests for printer constants."""

    def test_control_characters(self):
        """Test control character constants."""
        assert Printer.NUL == b"\x00"
        assert Printer.LF == b"\x0a"
        assert Printer.ESC == b"\x1b"
        assert Printer.FS == b"\x1c"
        assert Printer.FF == b"\x0c"
        assert Printer.GS == b"\x1d"
        assert Printer.DLE == b"\x10"
        assert Printer.EOT == b"\x04"

    def test_barcode_type_constants(self):
        """Test barcode type constants."""
        assert Printer.BARCODE_UPCA == 65
        assert Printer.BARCODE_CODE39 == 69
        assert Printer.BARCODE_CODE128 == 73

    def test_cut_mode_constants(self):
        """Test cut mode constants."""
        assert Printer.CUT_FULL == 65
        assert Printer.CUT_PARTIAL == 66

    def test_font_constants(self):
        """Test font constants."""
        assert Printer.FONT_A == 0
        assert Printer.FONT_B == 1
        assert Printer.FONT_C == 2

    def test_justification_constants(self):
        """Test justification constants."""
        assert Printer.JUSTIFY_LEFT == 0
        assert Printer.JUSTIFY_CENTER == 1
        assert Printer.JUSTIFY_RIGHT == 2

    def test_qr_constants(self):
        """Test QR code constants."""
        assert Printer.QR_ECLEVEL_L == 0
        assert Printer.QR_ECLEVEL_H == 3
        assert Printer.QR_MODEL_1 == 1
        assert Printer.QR_MODEL_2 == 2
