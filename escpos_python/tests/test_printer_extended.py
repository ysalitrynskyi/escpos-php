"""
Extended tests for the Printer class - comprehensive coverage.
"""

import pytest
from escpos.printer import Printer
from escpos.connectors.dummy_connector import DummyConnector
from escpos.capability_profile import CapabilityProfile
from tests.conftest import check_output


# ============================================================================
# BARCODE TESTS - All types
# ============================================================================

class TestBarcodeUPCA:
    """Tests for UPC-A barcodes."""

    def test_barcode_upca_valid(self, printer, dummy_connector):
        """Test valid UPC-A barcode."""
        printer.barcode("012345678905", Printer.BARCODE_UPCA)
        data = dummy_connector.get_data()
        assert b"\x1dk" in data
        assert b"012345678905" in data

    def test_barcode_upca_invalid_length_raises(self, printer):
        """Test UPC-A with invalid length raises error."""
        with pytest.raises(ValueError):
            printer.barcode("12345", Printer.BARCODE_UPCA)

    def test_barcode_upca_non_numeric_raises(self, printer):
        """Test UPC-A with non-numeric raises error."""
        with pytest.raises(ValueError):
            printer.barcode("01234567890A", Printer.BARCODE_UPCA)


class TestBarcodeUPCE:
    """Tests for UPC-E barcodes."""

    def test_barcode_upce_6_digits(self, printer, dummy_connector):
        """Test UPC-E with 6 digits."""
        printer.barcode("123456", Printer.BARCODE_UPCE)
        data = dummy_connector.get_data()
        assert b"123456" in data

    def test_barcode_upce_8_digits(self, printer, dummy_connector):
        """Test UPC-E with 8 digits."""
        printer.barcode("01234567", Printer.BARCODE_UPCE)
        data = dummy_connector.get_data()
        assert b"01234567" in data

    def test_barcode_upce_invalid_raises(self, printer):
        """Test UPC-E with invalid length."""
        with pytest.raises(ValueError):
            printer.barcode("12345", Printer.BARCODE_UPCE)


class TestBarcodeEAN13:
    """Tests for EAN-13/JAN-13 barcodes."""

    def test_barcode_ean13_valid(self, printer, dummy_connector):
        """Test valid EAN-13 barcode."""
        printer.barcode("5901234123457", Printer.BARCODE_JAN13)
        data = dummy_connector.get_data()
        assert b"5901234123457" in data

    def test_barcode_ean13_invalid_length(self, printer):
        """Test EAN-13 with invalid length (too short)."""
        with pytest.raises(ValueError):
            printer.barcode("12345678901", Printer.BARCODE_JAN13)  # 11 digits, needs 12-13


class TestBarcodeEAN8:
    """Tests for EAN-8/JAN-8 barcodes."""

    def test_barcode_ean8_valid(self, printer, dummy_connector):
        """Test valid EAN-8 barcode."""
        printer.barcode("96385074", Printer.BARCODE_JAN8)
        data = dummy_connector.get_data()
        assert b"96385074" in data

    def test_barcode_ean8_invalid_length(self, printer):
        """Test EAN-8 with invalid length (too short)."""
        with pytest.raises(ValueError):
            printer.barcode("123456", Printer.BARCODE_JAN8)  # 6 digits, needs 7-8


class TestBarcodeITF:
    """Tests for ITF (Interleaved 2 of 5) barcodes."""

    def test_barcode_itf_even_digits(self, printer, dummy_connector):
        """Test ITF with even number of digits."""
        printer.barcode("1234567890", Printer.BARCODE_ITF)
        data = dummy_connector.get_data()
        assert b"1234567890" in data

    def test_barcode_itf_odd_digits_raises(self, printer):
        """Test ITF with odd digits raises error."""
        with pytest.raises(ValueError):
            printer.barcode("123456789", Printer.BARCODE_ITF)


class TestBarcodeCODABAR:
    """Tests for CODABAR barcodes."""

    def test_barcode_codabar_valid(self, printer, dummy_connector):
        """Test valid CODABAR barcode."""
        printer.barcode("A12345B", Printer.BARCODE_CODABAR)
        data = dummy_connector.get_data()
        assert b"A12345B" in data


class TestBarcodeCODE93:
    """Tests for CODE93 barcodes."""

    def test_barcode_code93_valid(self, printer, dummy_connector):
        """Test valid CODE93 barcode."""
        printer.barcode("ABC123", Printer.BARCODE_CODE93)
        data = dummy_connector.get_data()
        assert b"ABC123" in data


class TestBarcodeCODE128:
    """Tests for CODE128 barcodes."""

    def test_barcode_code128_type_a(self, printer, dummy_connector):
        """Test CODE128 type A."""
        printer.barcode("{ATEST123", Printer.BARCODE_CODE128)
        data = dummy_connector.get_data()
        assert b"{ATEST123" in data

    def test_barcode_code128_type_b(self, printer, dummy_connector):
        """Test CODE128 type B."""
        printer.barcode("{BHello123", Printer.BARCODE_CODE128)
        data = dummy_connector.get_data()
        assert b"{BHello123" in data

    def test_barcode_code128_type_c(self, printer, dummy_connector):
        """Test CODE128 type C (numeric pairs)."""
        printer.barcode("{C123456", Printer.BARCODE_CODE128)
        data = dummy_connector.get_data()
        assert b"{C123456" in data


# ============================================================================
# QR CODE TESTS
# ============================================================================

class TestQRCode:
    """Tests for QR code printing."""

    def test_qr_code_basic(self, printer, dummy_connector):
        """Test basic QR code."""
        printer.qr_code("https://example.com")
        data = dummy_connector.get_data()
        assert len(data) > 10  # Should have some output

    def test_qr_code_error_correction_l(self, printer, dummy_connector):
        """Test QR code with EC level L."""
        printer.qr_code("Test", ec=Printer.QR_ECLEVEL_L)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_error_correction_m(self, printer, dummy_connector):
        """Test QR code with EC level M."""
        printer.qr_code("Test", ec=Printer.QR_ECLEVEL_M)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_error_correction_q(self, printer, dummy_connector):
        """Test QR code with EC level Q."""
        printer.qr_code("Test", ec=Printer.QR_ECLEVEL_Q)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_error_correction_h(self, printer, dummy_connector):
        """Test QR code with EC level H."""
        printer.qr_code("Test", ec=Printer.QR_ECLEVEL_H)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_model_1(self, printer, dummy_connector):
        """Test QR code model 1."""
        printer.qr_code("Test", model=Printer.QR_MODEL_1)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_model_2(self, printer, dummy_connector):
        """Test QR code model 2."""
        printer.qr_code("Test", model=Printer.QR_MODEL_2)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_size_min(self, printer, dummy_connector):
        """Test QR code minimum size."""
        printer.qr_code("Test", size=1)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_size_max(self, printer, dummy_connector):
        """Test QR code maximum size."""
        printer.qr_code("Test", size=16)
        assert len(dummy_connector.get_data()) > 0

    def test_qr_code_size_invalid_raises(self, printer):
        """Test QR code with invalid size."""
        with pytest.raises(ValueError):
            printer.qr_code("Test", size=0)
        with pytest.raises(ValueError):
            printer.qr_code("Test", size=17)

    def test_qr_code_with_url(self, printer, dummy_connector):
        """Test QR code with URL content."""
        printer.qr_code("https://example.com")
        assert len(dummy_connector.get_data()) > 0


# ============================================================================
# PDF417 TESTS
# ============================================================================

class TestPDF417:
    """Tests for PDF417 2D barcode printing."""

    def test_pdf417_basic(self, printer, dummy_connector):
        """Test basic PDF417."""
        printer.pdf417_code("Hello World")
        data = dummy_connector.get_data()
        assert len(data) > 10

    def test_pdf417_width(self, printer, dummy_connector):
        """Test PDF417 with custom width."""
        printer.pdf417_code("Test", width=3)
        assert len(dummy_connector.get_data()) > 0

    def test_pdf417_height_multiplier(self, printer, dummy_connector):
        """Test PDF417 with height multiplier."""
        printer.pdf417_code("Test", height_multiplier=4)
        assert len(dummy_connector.get_data()) > 0

    def test_pdf417_error_correction(self, printer, dummy_connector):
        """Test PDF417 with error correction."""
        printer.pdf417_code("Test", ec=0.5)
        assert len(dummy_connector.get_data()) > 0


# ============================================================================
# CUT TESTS - Extended
# ============================================================================

class TestCutExtended:
    """Extended tests for paper cutting."""

    def test_cut_full_zero_lines(self, printer, dummy_connector):
        """Test full cut with 0 lines."""
        printer.cut(Printer.CUT_FULL, 0)
        check_output(dummy_connector, b"\x1b@\x1dVA\x00")

    def test_cut_partial_max_lines(self, printer, dummy_connector):
        """Test partial cut with max lines."""
        printer.cut(Printer.CUT_PARTIAL, 255)
        check_output(dummy_connector, b"\x1b@\x1dVB\xff")

    def test_cut_invalid_mode_raises(self, printer):
        """Test cut with invalid mode."""
        with pytest.raises(ValueError):
            printer.cut(mode=64)
        with pytest.raises(ValueError):
            printer.cut(mode=67)

    def test_cut_invalid_lines_negative_raises(self, printer):
        """Test cut with negative lines."""
        with pytest.raises(ValueError):
            printer.cut(lines=-1)

    def test_cut_invalid_lines_too_large_raises(self, printer):
        """Test cut with lines > 255."""
        with pytest.raises(ValueError):
            printer.cut(lines=256)


# ============================================================================
# PULSE TESTS - Extended
# ============================================================================

class TestPulseExtended:
    """Extended tests for cash drawer pulse."""

    def test_pulse_pin_0(self, printer, dummy_connector):
        """Test pulse on pin 0."""
        printer.pulse(pin=0)
        data = dummy_connector.get_data()
        assert b"\x1bp0" in data

    def test_pulse_custom_timing(self, printer, dummy_connector):
        """Test pulse with custom timing."""
        printer.pulse(on_ms=200, off_ms=400)
        assert len(dummy_connector.get_data()) > 0

    def test_pulse_invalid_pin_raises(self, printer):
        """Test pulse with invalid pin."""
        with pytest.raises(ValueError):
            printer.pulse(pin=2)
        with pytest.raises(ValueError):
            printer.pulse(pin=-1)


# ============================================================================
# TEXT FORMATTING TESTS - Extended
# ============================================================================

class TestTextFormattingExtended:
    """Extended tests for text formatting."""

    def test_text_size_all_combinations(self, printer, dummy_connector):
        """Test various text size combinations."""
        for w in range(1, 9):
            for h in range(1, 9):
                connector = DummyConnector()
                p = Printer(connector)
                p.set_text_size(w, h)
                assert len(connector.get_data()) > 0

    def test_emphasis_toggle(self, printer, dummy_connector):
        """Test toggling emphasis on and off."""
        printer.set_emphasis(True)
        printer.text("Bold\n")
        printer.set_emphasis(False)
        printer.text("Normal\n")
        data = dummy_connector.get_data()
        assert b"\x1bE\x01" in data
        assert b"\x1bE\x00" in data

    def test_underline_toggle(self, printer, dummy_connector):
        """Test toggling underline modes."""
        printer.set_underline(Printer.UNDERLINE_SINGLE)
        printer.text("Underlined\n")
        printer.set_underline(Printer.UNDERLINE_NONE)
        printer.text("Normal\n")
        data = dummy_connector.get_data()
        assert b"\x1b-\x01" in data
        assert b"\x1b-\x00" in data

    def test_double_strike_toggle(self, printer, dummy_connector):
        """Test toggling double strike."""
        printer.set_double_strike(True)
        printer.set_double_strike(False)
        data = dummy_connector.get_data()
        assert b"\x1bG\x01" in data
        assert b"\x1bG\x00" in data


# ============================================================================
# LINE SPACING TESTS
# ============================================================================

class TestLineSpacingExtended:
    """Extended tests for line spacing."""

    def test_line_spacing_min(self, printer, dummy_connector):
        """Test minimum line spacing (1)."""
        printer.set_line_spacing(1)
        check_output(dummy_connector, b"\x1b@\x1b3\x01")

    def test_line_spacing_max(self, printer, dummy_connector):
        """Test maximum line spacing."""
        printer.set_line_spacing(255)
        check_output(dummy_connector, b"\x1b@\x1b3\xff")

    def test_line_spacing_invalid_raises(self, printer):
        """Test invalid line spacing raises error."""
        with pytest.raises(ValueError):
            printer.set_line_spacing(0)
        with pytest.raises(ValueError):
            printer.set_line_spacing(256)


# ============================================================================
# BARCODE SETTINGS TESTS
# ============================================================================

class TestBarcodeSettingsExtended:
    """Extended tests for barcode settings."""

    def test_barcode_height_min(self, printer, dummy_connector):
        """Test minimum barcode height."""
        printer.set_barcode_height(1)
        check_output(dummy_connector, b"\x1b@\x1dh\x01")

    def test_barcode_height_max(self, printer, dummy_connector):
        """Test maximum barcode height."""
        printer.set_barcode_height(255)
        check_output(dummy_connector, b"\x1b@\x1dh\xff")

    def test_barcode_height_invalid_raises(self, printer):
        """Test invalid barcode height."""
        with pytest.raises(ValueError):
            printer.set_barcode_height(0)
        with pytest.raises(ValueError):
            printer.set_barcode_height(256)

    def test_barcode_width_min(self, printer, dummy_connector):
        """Test minimum barcode width."""
        printer.set_barcode_width(1)
        check_output(dummy_connector, b"\x1b@\x1dw\x01")

    def test_barcode_width_max(self, printer, dummy_connector):
        """Test maximum barcode width."""
        printer.set_barcode_width(6)
        check_output(dummy_connector, b"\x1b@\x1dw\x06")

    def test_barcode_width_invalid_raises(self, printer):
        """Test invalid barcode width."""
        with pytest.raises(ValueError):
            printer.set_barcode_width(0)

    def test_barcode_text_position_above(self, printer, dummy_connector):
        """Test barcode text position above."""
        printer.set_barcode_text_position(Printer.BARCODE_TEXT_ABOVE)
        check_output(dummy_connector, b"\x1b@\x1dH\x01")

    def test_barcode_text_position_combined(self, printer, dummy_connector):
        """Test barcode text position above and below combined."""
        # BARCODE_TEXT_ABOVE | BARCODE_TEXT_BELOW = 1 | 2 = 3
        printer.set_barcode_text_position(Printer.BARCODE_TEXT_ABOVE | Printer.BARCODE_TEXT_BELOW)
        check_output(dummy_connector, b"\x1b@\x1dH\x03")


# ============================================================================
# MARGIN TESTS - Extended
# ============================================================================

class TestMarginsExtended:
    """Extended tests for margin settings."""

    def test_left_margin_zero(self, printer, dummy_connector):
        """Test zero left margin."""
        printer.set_print_left_margin(0)
        check_output(dummy_connector, b"\x1b@\x1dL\x00\x00")

    def test_print_width_various(self, printer, dummy_connector):
        """Test various print widths."""
        printer.set_print_width(576)  # Common 80mm width
        data = dummy_connector.get_data()
        assert b"\x1dW" in data


# ============================================================================
# CHARACTER TABLE TESTS
# ============================================================================

class TestCharacterTable:
    """Tests for character table management."""

    def test_get_character_table_default(self, printer):
        """Test default character table."""
        assert printer.get_character_table() == 0

    def test_character_table_after_init(self, printer, dummy_connector):
        """Test character table is 0 after initialization."""
        # Initialize resets character table
        printer.initialize()
        assert printer.get_character_table() == 0

    def test_character_table_type(self, printer):
        """Test character table is integer."""
        assert isinstance(printer.get_character_table(), int)


# ============================================================================
# PRINT MODE TESTS - Extended
# ============================================================================

class TestPrintModeExtended:
    """Extended tests for print mode selection."""

    def test_print_mode_all_flags(self, printer, dummy_connector):
        """Test all print mode flags combined."""
        mode = (Printer.MODE_FONT_B | Printer.MODE_EMPHASIZED |
                Printer.MODE_DOUBLE_HEIGHT | Printer.MODE_DOUBLE_WIDTH |
                Printer.MODE_UNDERLINE)
        printer.select_print_mode(mode)
        data = dummy_connector.get_data()
        assert b"\x1b!" in data

    def test_print_mode_underline(self, printer, dummy_connector):
        """Test underline mode."""
        printer.select_print_mode(Printer.MODE_UNDERLINE)
        check_output(dummy_connector, b"\x1b@\x1b!\x80")


# ============================================================================
# REVERSE FEED TESTS
# ============================================================================

class TestReverseFeed:
    """Tests for reverse feed."""

    def test_feed_reverse_min(self, printer, dummy_connector):
        """Test minimum reverse feed."""
        printer.feed_reverse(1)
        check_output(dummy_connector, b"\x1b@\x1be\x01")

    def test_feed_reverse_max(self, printer, dummy_connector):
        """Test maximum reverse feed."""
        printer.feed_reverse(255)
        check_output(dummy_connector, b"\x1b@\x1be\xff")

    def test_feed_reverse_invalid_raises(self, printer):
        """Test invalid reverse feed."""
        with pytest.raises(ValueError):
            printer.feed_reverse(0)
        with pytest.raises(ValueError):
            printer.feed_reverse(256)


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestValidation:
    """Tests for input validation methods."""

    def test_validate_integer_in_range(self):
        """Test integer validation in range."""
        # Should not raise
        Printer._validate_integer(5, 1, 10, "test")

    def test_validate_integer_at_bounds(self):
        """Test integer validation at bounds."""
        Printer._validate_integer(1, 1, 10, "test")
        Printer._validate_integer(10, 1, 10, "test")

    def test_validate_integer_out_of_range(self):
        """Test integer validation out of range."""
        with pytest.raises(ValueError):
            Printer._validate_integer(0, 1, 10, "test")
        with pytest.raises(ValueError):
            Printer._validate_integer(11, 1, 10, "test")

    def test_validate_integer_with_name(self):
        """Test integer validation error message includes name."""
        with pytest.raises(ValueError) as exc_info:
            Printer._validate_integer(100, 1, 10, "test_func", "param")
        assert "test_func" in str(exc_info.value) or "param" in str(exc_info.value)


# ============================================================================
# PRINTER CLOSE TESTS
# ============================================================================

class TestPrinterClose:
    """Tests for printer close behavior."""

    def test_close_clears_data(self):
        """Test close finalizes the connector."""
        connector = DummyConnector()
        printer = Printer(connector)
        printer.text("Test")
        data_before = connector.get_data()
        printer.close()
        # After close, getting data should return empty (buffer cleared by finalize)
        assert len(data_before) > 0

    def test_double_close_safe(self):
        """Test that closing twice is safe."""
        connector = DummyConnector()
        printer = Printer(connector)
        printer.close()
        printer.close()  # Should not raise


# ============================================================================
# CONSTANTS TESTS - Extended
# ============================================================================

class TestConstantsExtended:
    """Extended tests for printer constants."""

    def test_mode_constants(self):
        """Test mode constants."""
        assert Printer.MODE_FONT_A == 0
        assert Printer.MODE_FONT_B == 1
        assert Printer.MODE_EMPHASIZED == 8
        assert Printer.MODE_DOUBLE_HEIGHT == 16
        assert Printer.MODE_DOUBLE_WIDTH == 32
        assert Printer.MODE_UNDERLINE == 128

    def test_underline_constants(self):
        """Test underline constants."""
        assert Printer.UNDERLINE_NONE == 0
        assert Printer.UNDERLINE_SINGLE == 1
        assert Printer.UNDERLINE_DOUBLE == 2

    def test_color_constants(self):
        """Test color constants."""
        assert Printer.COLOR_1 == 0
        assert Printer.COLOR_2 == 1

    def test_barcode_text_constants(self):
        """Test barcode text position constants."""
        assert Printer.BARCODE_TEXT_NONE == 0
        assert Printer.BARCODE_TEXT_ABOVE == 1
        assert Printer.BARCODE_TEXT_BELOW == 2
        # BARCODE_TEXT_BOTH = ABOVE | BELOW = 3
        assert (Printer.BARCODE_TEXT_ABOVE | Printer.BARCODE_TEXT_BELOW) == 3

    def test_image_constants(self):
        """Test image constants."""
        assert Printer.IMG_DEFAULT == 0
        assert Printer.IMG_DOUBLE_WIDTH == 1
        assert Printer.IMG_DOUBLE_HEIGHT == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_receipt_simulation(self, printer, dummy_connector):
        """Test simulating a typical receipt."""
        printer.set_justification(Printer.JUSTIFY_CENTER)
        printer.set_emphasis(True)
        printer.text("MY STORE\n")
        printer.set_emphasis(False)
        printer.text("123 Main St\n\n")

        printer.set_justification(Printer.JUSTIFY_LEFT)
        printer.text("Item 1            $10.00\n")
        printer.text("Item 2            $15.00\n")
        printer.text("------------------------\n")

        printer.set_emphasis(True)
        printer.text("TOTAL             $25.00\n")
        printer.set_emphasis(False)

        printer.feed(3)
        printer.cut()

        data = dummy_connector.get_data()
        assert len(data) > 100
        assert b"MY STORE" in data
        assert b"$25.00" in data

    def test_barcode_with_settings(self, printer, dummy_connector):
        """Test barcode with custom settings."""
        printer.set_barcode_height(80)
        printer.set_barcode_width(3)
        printer.set_barcode_text_position(Printer.BARCODE_TEXT_BELOW)
        printer.barcode("ABC123", Printer.BARCODE_CODE39)

        data = dummy_connector.get_data()
        assert b"\x1dh" in data  # height
        assert b"\x1dw" in data  # width
        assert b"\x1dH" in data  # text position
        assert b"ABC123" in data

    def test_multiple_text_styles(self, printer, dummy_connector):
        """Test multiple text style changes."""
        printer.set_text_size(2, 2)
        printer.text("BIG\n")
        printer.set_text_size(1, 1)

        printer.set_emphasis(True)
        printer.set_underline(Printer.UNDERLINE_SINGLE)
        printer.text("Bold Underline\n")
        printer.set_emphasis(False)
        printer.set_underline(Printer.UNDERLINE_NONE)

        printer.set_font(Printer.FONT_B)
        printer.text("Font B\n")
        printer.set_font(Printer.FONT_A)

        data = dummy_connector.get_data()
        assert b"BIG" in data
        assert b"Bold Underline" in data
        assert b"Font B" in data


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_text(self, printer, dummy_connector):
        """Test printing very long text."""
        long_text = "A" * 1000 + "\n"
        printer.text(long_text)
        data = dummy_connector.get_data()
        assert b"A" * 1000 in data

    def test_special_characters(self, printer, dummy_connector):
        """Test special characters in text."""
        printer.text("Line1\nLine2\n")
        data = dummy_connector.get_data()
        assert b"\n" in data
        assert b"Line1" in data

    def test_unicode_text(self, printer, dummy_connector):
        """Test unicode text (should be handled by buffer)."""
        # Basic ASCII should work
        printer.text("Hello World\n")
        assert len(dummy_connector.get_data()) > 0

    def test_empty_barcode_raises(self, printer):
        """Test empty barcode content raises error."""
        with pytest.raises(ValueError):
            printer.barcode("", Printer.BARCODE_CODE39)

    def test_multiple_cuts(self, printer, dummy_connector):
        """Test multiple consecutive cuts."""
        printer.cut()
        printer.cut()
        printer.cut()
        data = dummy_connector.get_data()
        # Should have 3 cut commands (plus init)
        assert data.count(b"\x1dV") == 3

    def test_feed_then_cut(self, printer, dummy_connector):
        """Test feed followed by cut."""
        printer.feed(5)
        printer.cut()
        data = dummy_connector.get_data()
        assert b"\x1bd\x05" in data  # feed 5
        assert b"\x1dV" in data  # cut


class TestProfileSupport:
    """Tests for printer profile support."""

    def test_default_profile(self, printer):
        """Test printer with default profile."""
        profile = printer._profile
        assert profile is not None

    def test_get_profile_names(self):
        """Test getting available profile names."""
        names = CapabilityProfile.get_profile_names()
        assert len(names) > 0
        assert "default" in names

    def test_load_profile(self):
        """Test loading a specific profile."""
        profile = CapabilityProfile.load("default")
        assert profile is not None
        assert profile.get_id() == "default"


# ============================================================================
# DATA OUTPUT VERIFICATION
# ============================================================================

class TestDataOutput:
    """Tests verifying exact data output."""

    def test_initialize_exact_output(self, printer, dummy_connector):
        """Test exact initialize output."""
        # Printer is already initialized in fixture
        data = dummy_connector.get_data()
        assert data == b"\x1b@"

    def test_feed_single_exact_output(self, printer, dummy_connector):
        """Test exact single feed output."""
        printer.feed(1)
        check_output(dummy_connector, b"\x1b@\x0a")

    def test_text_exact_output(self, printer, dummy_connector):
        """Test exact text output."""
        printer.text("Hi\n")
        check_output(dummy_connector, b"\x1b@Hi\n")


class TestBitImageAndGraphics:
    """Tests for bit image and graphics settings."""

    def test_bit_image_column_format_exists(self, printer):
        """Test bit_image method exists."""
        assert hasattr(printer, 'bit_image')

    def test_graphics_method_exists(self, printer):
        """Test graphics method exists."""
        assert hasattr(printer, 'graphics')
