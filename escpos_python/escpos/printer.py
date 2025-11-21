"""
Printer class - Main class for ESC/POS code generation.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

import re
import logging
from math import ceil
from typing import Optional, List, Union, TYPE_CHECKING

from escpos.capability_profile import CapabilityProfile
from escpos.connectors.print_connector import PrintConnector

if TYPE_CHECKING:
    from escpos.buffers.print_buffer import PrintBuffer
    from escpos.escpos_image import EscposImage

# Module-level logger
logger = logging.getLogger(__name__)


class Printer:
    """
    Main class for ESC/POS code generation.
    """

    # ASCII control characters
    NUL = b"\x00"
    LF = b"\x0a"
    ESC = b"\x1b"
    FS = b"\x1c"
    FF = b"\x0c"
    GS = b"\x1d"
    DLE = b"\x10"
    EOT = b"\x04"

    # Barcode types
    BARCODE_UPCA = 65
    BARCODE_UPCE = 66
    BARCODE_JAN13 = 67
    BARCODE_JAN8 = 68
    BARCODE_CODE39 = 69
    BARCODE_ITF = 70
    BARCODE_CODABAR = 71
    BARCODE_CODE93 = 72
    BARCODE_CODE128 = 73

    # Barcode text position
    BARCODE_TEXT_NONE = 0
    BARCODE_TEXT_ABOVE = 1
    BARCODE_TEXT_BELOW = 2

    # Colors
    COLOR_1 = 0  # Usually black
    COLOR_2 = 1  # Usually red or blue

    # Cut modes
    CUT_FULL = 65
    CUT_PARTIAL = 66

    # Fonts
    FONT_A = 0
    FONT_B = 1
    FONT_C = 2

    # Image sizes
    IMG_DEFAULT = 0
    IMG_DOUBLE_WIDTH = 1
    IMG_DOUBLE_HEIGHT = 2

    # Justification
    JUSTIFY_LEFT = 0
    JUSTIFY_CENTER = 1
    JUSTIFY_RIGHT = 2

    # Print modes (flags - combinable)
    MODE_FONT_A = 0
    MODE_FONT_B = 1
    MODE_EMPHASIZED = 8
    MODE_DOUBLE_HEIGHT = 16
    MODE_DOUBLE_WIDTH = 32
    MODE_UNDERLINE = 128

    # PDF417 options
    PDF417_STANDARD = 0
    PDF417_TRUNCATED = 1

    # QR Code error correction levels
    QR_ECLEVEL_L = 0
    QR_ECLEVEL_M = 1
    QR_ECLEVEL_Q = 2
    QR_ECLEVEL_H = 3

    # QR Code models
    QR_MODEL_1 = 1
    QR_MODEL_2 = 2
    QR_MICRO = 3

    # Printer status (experimental)
    STATUS_PRINTER = 1
    STATUS_OFFLINE_CAUSE = 2
    STATUS_ERROR_CAUSE = 3
    STATUS_PAPER_ROLL = 4
    STATUS_INK_A = 7
    STATUS_INK_B = 6
    STATUS_PEELER = 8

    # Underline modes
    UNDERLINE_NONE = 0
    UNDERLINE_SINGLE = 1
    UNDERLINE_DOUBLE = 2

    def __init__(
        self,
        connector: PrintConnector,
        profile: Optional[CapabilityProfile] = None
    ):
        """
        Construct a new print object.

        Args:
            connector: The PrintConnector to send data to.
            profile: Supported features of this printer. If not set, the "default"
                CapabilityProfile will be used, which is suitable for Epson printers.
        """
        from escpos.buffers.escpos_print_buffer import EscposPrintBuffer

        self._connector = connector

        # Set capability profile
        if profile is None:
            profile = CapabilityProfile.load('default')
        self._profile = profile

        # Set buffer
        self._buffer: Optional['PrintBuffer'] = None
        buffer = EscposPrintBuffer()
        self.set_print_buffer(buffer)

        # Character table
        self._character_table = 0

        # Initialize printer
        self.initialize()

    def initialize(self) -> None:
        """
        Initialize printer. This resets formatting back to the defaults.
        """
        self._connector.write(self.ESC + b"@")
        self._character_table = 0

    def close(self) -> None:
        """
        Close the underlying buffer. With some connectors, the job will not
        actually be sent to the printer until this is called.
        """
        logger.debug("Closing printer connection")
        self._connector.finalize()

    # Context manager support

    def __enter__(self) -> 'Printer':
        """Context manager entry - returns the printer instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes the printer."""
        self.close()

    # Printer status methods

    def get_printer_status(self, status_type: int = STATUS_PRINTER) -> Optional[bytes]:
        """
        Request and read printer status using DLE EOT command.

        Args:
            status_type: Type of status to request:
                - STATUS_PRINTER (1): General printer status
                - STATUS_OFFLINE_CAUSE (2): Offline cause status
                - STATUS_ERROR_CAUSE (3): Error cause status
                - STATUS_PAPER_ROLL (4): Paper roll sensor status

        Returns:
            Status byte(s) from printer, or None if read fails.

        Note:
            Not all printers support status reading. The connector must
            support the read() method.
        """
        self._validate_integer(status_type, 1, 8, "get_printer_status")
        logger.debug(f"Requesting printer status type {status_type}")

        # Send DLE EOT n command
        self._connector.write(self.DLE + self.EOT + bytes([status_type]))

        try:
            status = self._connector.read(1)
            logger.debug(f"Received status: {status.hex() if status else 'None'}")
            return status
        except Exception as e:
            logger.warning(f"Failed to read printer status: {e}")
            return None

    def is_online(self) -> Optional[bool]:
        """
        Check if the printer is online.

        Returns:
            True if online, False if offline, None if status cannot be read.
        """
        status = self.get_printer_status(self.STATUS_PRINTER)
        if status is None or len(status) == 0:
            return None
        # Bit 3 (0x08) indicates offline status
        return (status[0] & 0x08) == 0

    def has_paper(self) -> Optional[bool]:
        """
        Check if the printer has paper.

        Returns:
            True if paper present, False if paper out, None if status cannot be read.
        """
        status = self.get_printer_status(self.STATUS_PAPER_ROLL)
        if status is None or len(status) == 0:
            return None
        # Bits 5-6 (0x60) indicate paper status
        # 0x00 = paper present, 0x60 = paper near end or out
        return (status[0] & 0x60) == 0

    def has_error(self) -> Optional[bool]:
        """
        Check if the printer has an error condition.

        Returns:
            True if error present, False if no error, None if status cannot be read.
        """
        status = self.get_printer_status(self.STATUS_ERROR_CAUSE)
        if status is None or len(status) == 0:
            return None
        # Various bits indicate different errors
        # Bit 3 (0x08) = cutter error, Bit 5 (0x20) = unrecoverable error
        # Bit 6 (0x40) = auto-recoverable error
        return (status[0] & 0x68) != 0

    def is_drawer_open(self, pin: int = 0) -> Optional[bool]:
        """
        Check if the cash drawer is open.

        Args:
            pin: Drawer pin to check (0 or 1).

        Returns:
            True if drawer is open, False if closed, None if status cannot be read.

        Note:
            Requires a cash drawer with status feedback connected to the printer.
        """
        status = self.get_printer_status(self.STATUS_PRINTER)
        if status is None or len(status) == 0:
            return None
        # Bit 2 (0x04) indicates drawer status
        return (status[0] & 0x04) != 0

    # Text output methods

    def text(self, text: str) -> None:
        """
        Add text to the buffer.

        Text should either be followed by a line-break, or feed() should be called
        after this to clear the print buffer.

        Args:
            text: Text to print, as UTF-8.
        """
        self._buffer.write_text(str(text))

    def text_raw(self, text: str = "") -> None:
        """
        Add text to the buffer without attempting to interpret character codes.

        Args:
            text: Text to print.
        """
        self._buffer.write_text_raw(str(text))

    def text_chinese(self, text: str = "") -> None:
        """
        Add Chinese text to the buffer.

        This is a specific workaround for Zijang printers -
        The printer will be switched to a two-byte mode and sent GBK-encoded text.

        Args:
            text: Text to print, as UTF-8.
        """
        self._connector.write(self.FS + b"&")
        encoded = text.encode('gbk', errors='replace')
        self._buffer.write_text_raw(encoded.decode('latin-1'))
        self._connector.write(self.FS + b".")

    # Feed and cut methods

    def feed(self, lines: int = 1) -> None:
        """
        Print and feed line / Print and feed n lines.

        Args:
            lines: Number of lines to feed (1-255).
        """
        self._validate_integer(lines, 1, 255, "feed")
        if lines <= 1:
            self._connector.write(self.LF)
        else:
            self._connector.write(self.ESC + b"d" + bytes([lines]))

    def feed_reverse(self, lines: int = 1) -> None:
        """
        Print and reverse feed n lines.

        Args:
            lines: Number of lines to feed (1-255).
        """
        self._validate_integer(lines, 1, 255, "feed_reverse")
        self._connector.write(self.ESC + b"e" + bytes([lines]))

    def feed_form(self) -> None:
        """
        Some printers require a form feed to release the paper.
        """
        self._connector.write(self.FF)

    def release(self) -> None:
        """
        Some slip printers require ESC q sequence to release the paper.
        """
        self._connector.write(self.ESC + bytes([113]))

    def cut(self, mode: int = CUT_FULL, lines: int = 3) -> None:
        """
        Cut the paper.

        Args:
            mode: Cut mode (CUT_FULL or CUT_PARTIAL).
            lines: Number of lines to feed before cutting.

        Raises:
            ValueError: If mode or lines are out of valid range.
        """
        self._validate_integer(mode, self.CUT_FULL, self.CUT_PARTIAL, "cut", "mode")
        self._validate_integer(lines, 0, 255, "cut", "lines")
        self._connector.write(self.GS + b"V" + bytes([mode, lines]))

    def pulse(self, pin: int = 0, on_ms: int = 120, off_ms: int = 240) -> None:
        """
        Generate a pulse, for opening a cash drawer if one is connected.

        Args:
            pin: 0 or 1, for pin 2 or pin 5 kick-out connector respectively.
            on_ms: Pulse ON time, in milliseconds.
            off_ms: Pulse OFF time, in milliseconds.
        """
        self._validate_integer(pin, 0, 1, "pulse")
        self._validate_integer(on_ms, 1, 511, "pulse")
        self._validate_integer(off_ms, 1, 511, "pulse")

        pin_value = pin + 48  # Character '0' or '1'
        on_value = on_ms // 2
        off_value = off_ms // 2
        self._connector.write(self.ESC + b"p" + bytes([pin_value, on_value, off_value]))

    # Formatting methods

    def set_font(self, font: int = FONT_A) -> None:
        """
        Select font. Most printers have two fonts (A and B), some have three (C).

        Args:
            font: The font to use (FONT_A, FONT_B, or FONT_C).
        """
        self._validate_integer(font, 0, 2, "set_font")
        self._connector.write(self.ESC + b"M" + bytes([font]))

    def set_justification(self, justification: int = JUSTIFY_LEFT) -> None:
        """
        Select justification.

        Args:
            justification: One of JUSTIFY_LEFT, JUSTIFY_CENTER, or JUSTIFY_RIGHT.
        """
        self._validate_integer(justification, 0, 2, "set_justification")
        self._connector.write(self.ESC + b"a" + bytes([justification]))

    def set_text_size(self, width_multiplier: int, height_multiplier: int) -> None:
        """
        Set the size of text, as a multiple of the normal size.

        Args:
            width_multiplier: Multiple of the regular width (1-8).
            height_multiplier: Multiple of the regular height (1-8).
        """
        self._validate_integer(width_multiplier, 1, 8, "set_text_size")
        self._validate_integer(height_multiplier, 1, 8, "set_text_size")
        c = (2 << 3) * (width_multiplier - 1) + (height_multiplier - 1)
        self._connector.write(self.GS + b"!" + bytes([c]))

    def set_emphasis(self, on: bool = True) -> None:
        """
        Turn emphasized mode on/off.

        Args:
            on: True for emphasis, False for no emphasis.
        """
        self._connector.write(self.ESC + b"E" + bytes([1 if on else 0]))

    def set_double_strike(self, on: bool = True) -> None:
        """
        Turn double-strike mode on/off.

        Args:
            on: True for double strike, False for no double strike.
        """
        self._connector.write(self.ESC + b"G" + bytes([1 if on else 0]))

    def set_underline(self, underline: int = UNDERLINE_SINGLE) -> None:
        """
        Set underline for printed text.

        Args:
            underline: One of UNDERLINE_NONE, UNDERLINE_SINGLE, or UNDERLINE_DOUBLE.
        """
        self._validate_integer(underline, 0, 2, "set_underline")
        self._connector.write(self.ESC + b"-" + bytes([underline]))

    def set_color(self, color: int = COLOR_1) -> None:
        """
        Select print color on printers that support multiple colors.

        Args:
            color: COLOR_1 (default, usually black) or COLOR_2 (usually red/blue).
        """
        self._validate_integer(color, 0, 1, "set_color")
        self._connector.write(self.ESC + b"r" + bytes([color]))

    def set_reverse_colors(self, on: bool = True) -> None:
        """
        Set black/white reverse mode on or off.

        Args:
            on: True to enable (white on black), False to disable.
        """
        self._connector.write(self.GS + b"B" + bytes([1 if on else 0]))

    def set_upside_down(self, on: bool = True) -> None:
        """
        Print each line upside-down (180 degrees rotated).

        Args:
            on: True to enable, False to disable.
        """
        self._connector.write(self.ESC + b"{" + bytes([1 if on else 0]))

    def select_print_mode(self, mode: int = MODE_FONT_A) -> None:
        """
        Select print mode(s).

        Several MODE_* constants can be OR'd together. Valid modes are:
        MODE_FONT_A, MODE_FONT_B, MODE_EMPHASIZED, MODE_DOUBLE_HEIGHT,
        MODE_DOUBLE_WIDTH, MODE_UNDERLINE.

        Args:
            mode: The mode to use. Default is MODE_FONT_A.
        """
        all_modes = (
            self.MODE_FONT_B |
            self.MODE_EMPHASIZED |
            self.MODE_DOUBLE_HEIGHT |
            self.MODE_DOUBLE_WIDTH |
            self.MODE_UNDERLINE
        )

        if not isinstance(mode, int) or mode < 0 or (mode & all_modes) != mode:
            raise ValueError("Invalid mode")

        self._connector.write(self.ESC + b"!" + bytes([mode]))

    # Character encoding methods

    def select_character_table(self, table: int = 0) -> None:
        """
        Switch character table (code page) manually.

        Args:
            table: The table to select (0-255). Available code tables are model-specific.
        """
        self._validate_integer(table, 0, 255, "select_character_table")

        supported = self._profile.get_code_pages()
        if table not in supported:
            raise ValueError(
                f"There is no code table {table} allowed by this printer's capability profile."
            )

        self._character_table = table

        if self._profile.get_supports_star_commands():
            # STAR printers use a different command
            self._connector.write(self.ESC + self.GS + b"t" + bytes([table]))
        else:
            self._connector.write(self.ESC + b"t" + bytes([table]))

    def select_user_defined_character_set(self, on: bool = True) -> None:
        """
        Select user-defined character set.

        Args:
            on: True to enable user-defined character set, False to use built-in.
        """
        self._connector.write(self.ESC + b"%" + bytes([1 if on else 0]))

    def get_character_table(self) -> int:
        """
        Get the current character table.

        Returns:
            Current character table number.
        """
        return self._character_table

    # Layout control methods

    def set_line_spacing(self, height: Optional[int] = None) -> None:
        """
        Set the height of the line.

        Args:
            height: The height of each line, in dots. If None, reset to default.
        """
        if height is None:
            self._connector.write(self.ESC + b"2")
            return

        self._validate_integer(height, 1, 255, "set_line_spacing")
        self._connector.write(self.ESC + b"3" + bytes([height]))

    def set_print_left_margin(self, margin: int = 0) -> None:
        """
        Set print area left margin.

        Args:
            margin: The left margin in dots (0-65535).
        """
        self._validate_integer(margin, 0, 65535, "set_print_left_margin")
        self._connector.write(self.GS + b"L" + self._int_low_high(margin, 2))

    def set_print_width(self, width: int = 512) -> None:
        """
        Set print area width.

        Args:
            width: The width of the page print area, in dots (1-65535).
        """
        self._validate_integer(width, 1, 65535, "set_print_width")
        self._connector.write(self.GS + b"W" + self._int_low_high(width, 2))

    # Barcode methods

    def barcode(self, content: str, barcode_type: int = BARCODE_CODE39) -> None:
        """
        Print a barcode.

        Args:
            content: The information to encode.
            barcode_type: The barcode standard to output (BARCODE_* constants).
        """
        self._validate_integer(barcode_type, 65, 73, "barcode", "Barcode type")
        content_len = len(content)

        # Validate content based on barcode type
        if barcode_type == self.BARCODE_UPCA:
            self._validate_integer(content_len, 11, 12, "barcode", "UPCA barcode content length")
            self._validate_string_regex(content, "barcode", r"^[0-9]{11,12}$", "UPCA barcode content")
        elif barcode_type == self.BARCODE_UPCE:
            self._validate_integer_multi(content_len, [[6, 8], [11, 12]], "barcode", "UPCE barcode content length")
            self._validate_string_regex(content, "barcode", r"^([0-9]{6,8}|[0-9]{11,12})$", "UPCE barcode content")
        elif barcode_type == self.BARCODE_JAN13:
            self._validate_integer(content_len, 12, 13, "barcode", "JAN13 barcode content length")
            self._validate_string_regex(content, "barcode", r"^[0-9]{12,13}$", "JAN13 barcode content")
        elif barcode_type == self.BARCODE_JAN8:
            self._validate_integer(content_len, 7, 8, "barcode", "JAN8 barcode content length")
            self._validate_string_regex(content, "barcode", r"^[0-9]{7,8}$", "JAN8 barcode content")
        elif barcode_type == self.BARCODE_CODE39:
            self._validate_integer(content_len, 1, 255, "barcode", "CODE39 barcode content length")
            self._validate_string_regex(content, "barcode", r"^([0-9A-Z \$\%\+\-\.\/]+|\*[0-9A-Z \$\%\+\-\.\/]+\*)$", "CODE39 barcode content")
        elif barcode_type == self.BARCODE_ITF:
            self._validate_integer(content_len, 2, 255, "barcode", "ITF barcode content length")
            self._validate_string_regex(content, "barcode", r"^([0-9]{2})+$", "ITF barcode content")
        elif barcode_type == self.BARCODE_CODABAR:
            self._validate_integer(content_len, 1, 255, "barcode", "Codabar barcode content length")
            self._validate_string_regex(content, "barcode", r"^[A-Da-d][0-9\$\+\-\.\/\:]+[A-Da-d]$", "Codabar barcode content")
        elif barcode_type == self.BARCODE_CODE93:
            self._validate_integer(content_len, 1, 255, "barcode", "Code93 barcode content length")
            self._validate_string_regex(content, "barcode", r"^[\x00-\x7F]+$", "Code93 barcode content")
        elif barcode_type == self.BARCODE_CODE128:
            self._validate_integer(content_len, 1, 255, "barcode", "Code128 barcode content length")
            self._validate_string_regex(content, "barcode", r"^\{[A-C][\x00-\x7F]+$", "Code128 barcode content")

        content_bytes = content.encode('latin-1')

        if not self._profile.get_supports_barcode_b():
            # Simpler barcode command for limited printers
            self._validate_integer(barcode_type, 65, 71, "barcode")
            self._connector.write(self.GS + b"k" + bytes([barcode_type - 65]) + content_bytes + self.NUL)
            return

        # More advanced function B
        self._connector.write(self.GS + b"k" + bytes([barcode_type, len(content_bytes)]) + content_bytes)

    def set_barcode_height(self, height: int = 8) -> None:
        """
        Set barcode height.

        Args:
            height: Height in dots (1-255).
        """
        self._validate_integer(height, 1, 255, "set_barcode_height")
        self._connector.write(self.GS + b"h" + bytes([height]))

    def set_barcode_width(self, width: int = 3) -> None:
        """
        Set barcode bar width.

        Args:
            width: Bar width in dots (1-255). Values above 6 may have no effect.
        """
        self._validate_integer(width, 1, 255, "set_barcode_width")
        self._connector.write(self.GS + b"w" + bytes([width]))

    def set_barcode_text_position(self, position: int = BARCODE_TEXT_NONE) -> None:
        """
        Set the position for the Human Readable Interpretation (HRI) of barcode characters.

        Args:
            position: Use BARCODE_TEXT_NONE, BARCODE_TEXT_ABOVE, and/or BARCODE_TEXT_BELOW.
        """
        self._validate_integer(position, 0, 3, "set_barcode_text_position", "Barcode text position")
        self._connector.write(self.GS + b"H" + bytes([position]))

    # 2D Code methods

    def qr_code(
        self,
        content: str,
        ec: int = QR_ECLEVEL_L,
        size: int = 3,
        model: int = QR_MODEL_2
    ) -> None:
        """
        Print the given data as a QR code on the printer.

        Args:
            content: The content of the code.
            ec: Error-correction level (QR_ECLEVEL_L, M, Q, or H).
            size: Pixel size (1-16).
            model: QR code model (QR_MODEL_1, QR_MODEL_2, or QR_MICRO).
        """
        self._validate_integer(ec, 0, 3, "qr_code")
        self._validate_integer(size, 1, 16, "qr_code")
        self._validate_integer(model, 1, 3, "qr_code")

        if content == "":
            return

        if not self._profile.get_supports_qr_code():
            raise RuntimeError("QR codes are not supported on your printer.")

        cn = b'1'  # Code type for QR code

        # Select model
        self._wrapper_send_2d_code_data(b'\x41', cn, bytes([48 + model, 0]))
        # Set dot size
        self._wrapper_send_2d_code_data(b'\x43', cn, bytes([size]))
        # Set error correction level
        self._wrapper_send_2d_code_data(b'\x45', cn, bytes([48 + ec]))
        # Send content & print
        self._wrapper_send_2d_code_data(b'\x50', cn, content.encode('utf-8'), b'0')
        self._wrapper_send_2d_code_data(b'\x51', cn, b'', b'0')

    def pdf417_code(
        self,
        content: str,
        width: int = 3,
        height_multiplier: int = 3,
        data_column_count: int = 0,
        ec: float = 0.10,
        options: int = PDF417_STANDARD
    ) -> None:
        """
        Print a two-dimensional data code using the PDF417 standard.

        Args:
            content: Text or numbers to store in the code.
            width: Width of a module (pixel) in dots (2-8).
            height_multiplier: Multiplier for height of a module (2-8).
            data_column_count: Number of data columns. 0 for auto-calculate.
            ec: Error correction ratio, from 0.01 to 4.00.
            options: PDF417_STANDARD or PDF417_TRUNCATED.
        """
        self._validate_integer(width, 2, 8, "pdf417_code", "width")
        self._validate_integer(height_multiplier, 2, 8, "pdf417_code", "height_multiplier")
        self._validate_integer(data_column_count, 0, 30, "pdf417_code", "data_column_count")
        self._validate_float(ec, 0.01, 4.00, "pdf417_code", "ec")
        self._validate_integer(options, 0, 1, "pdf417_code", "options")

        if content == "":
            return

        if not self._profile.get_supports_pdf417_code():
            raise RuntimeError("PDF417 codes are not supported on your printer.")

        cn = b'0'  # Code type for PDF417

        # Select model
        self._wrapper_send_2d_code_data(b'\x46', cn, bytes([options]))
        # Column count
        self._wrapper_send_2d_code_data(b'\x41', cn, bytes([data_column_count]))
        # Set dot sizes
        self._wrapper_send_2d_code_data(b'\x43', cn, bytes([width]))
        self._wrapper_send_2d_code_data(b'\x44', cn, bytes([height_multiplier]))
        # Set error correction ratio
        ec_int = int(ceil(float(ec) * 10))
        self._wrapper_send_2d_code_data(b'\x45', cn, bytes([ec_int]), b'1')
        # Send content & print
        self._wrapper_send_2d_code_data(b'\x50', cn, content.encode('utf-8'), b'0')
        self._wrapper_send_2d_code_data(b'\x51', cn, b'', b'0')

    # Image methods

    def graphics(self, img: 'EscposImage', size: int = IMG_DEFAULT) -> None:
        """
        Print an image to the printer.

        Args:
            img: The image to print.
            size: Size modifier (IMG_DEFAULT, IMG_DOUBLE_WIDTH, IMG_DOUBLE_HEIGHT, or combination).
        """
        self._validate_integer(size, 0, 3, "graphics")

        raster_data = img.to_raster_format()
        img_header = self._data_header([img.get_width(), img.get_height()], True)
        tone = b'0'
        colors = b'1'
        xm = bytes([2]) if (size & self.IMG_DOUBLE_WIDTH) == self.IMG_DOUBLE_WIDTH else bytes([1])
        ym = bytes([2]) if (size & self.IMG_DOUBLE_HEIGHT) == self.IMG_DOUBLE_HEIGHT else bytes([1])
        header = tone + xm + ym + colors + img_header

        self._wrapper_send_graphics_data(b'0', b'p', header + raster_data)
        self._wrapper_send_graphics_data(b'0', b'2')

    def bit_image(self, img: 'EscposImage', size: int = IMG_DEFAULT) -> None:
        """
        Print an image using the older "bit image" command.

        Args:
            img: The image to print.
            size: Size modifier (IMG_DEFAULT, IMG_DOUBLE_WIDTH, IMG_DOUBLE_HEIGHT, or combination).
        """
        self._validate_integer(size, 0, 3, "bit_image")

        raster_data = img.to_raster_format()
        header = self._data_header([img.get_width_bytes(), img.get_height()], True)
        self._connector.write(self.GS + b"v0" + bytes([size]) + header)
        self._connector.write(raster_data)

    def bit_image_column_format(self, img: 'EscposImage', size: int = IMG_DEFAULT) -> None:
        """
        Print an image using the older "bit image" command in column format.

        Args:
            img: The image to print.
            size: Size modifier (IMG_DEFAULT, IMG_DOUBLE_WIDTH, IMG_DOUBLE_HEIGHT, or combination).
        """
        high_density_vertical = not ((size & self.IMG_DOUBLE_HEIGHT) == self.IMG_DOUBLE_HEIGHT)
        high_density_horizontal = not ((size & self.IMG_DOUBLE_WIDTH) == self.IMG_DOUBLE_WIDTH)

        self.set_line_spacing(16)
        density_code = (1 if high_density_horizontal else 0) + (32 if high_density_vertical else 0)
        col_format_data = img.to_column_format(high_density_vertical)
        header = self._data_header([img.get_width()], True)

        for line in col_format_data:
            self._connector.write(self.ESC + b"*" + bytes([density_code]) + header + line)
            self.feed()

        self.set_line_spacing()

    # Accessors

    def get_print_connector(self) -> PrintConnector:
        """
        Get the print connector.

        Returns:
            The PrintConnector instance.
        """
        return self._connector

    def get_print_buffer(self) -> 'PrintBuffer':
        """
        Get the print buffer.

        Returns:
            The PrintBuffer instance.
        """
        return self._buffer

    def get_printer_capability_profile(self) -> CapabilityProfile:
        """
        Get the printer capability profile.

        Returns:
            The CapabilityProfile instance.
        """
        return self._profile

    def set_print_buffer(self, buffer: 'PrintBuffer') -> None:
        """
        Attach a different print buffer to the printer.

        Args:
            buffer: The buffer to use.

        Raises:
            ValueError: If the buffer is already attached to a different printer.
        """
        if buffer is self._buffer:
            return

        if buffer.get_printer() is not None:
            raise ValueError("This buffer is already attached to a printer.")

        if self._buffer is not None:
            self._buffer.set_printer(None)

        self._buffer = buffer
        self._buffer.set_printer(self)

    # Internal helper methods

    def _wrapper_send_2d_code_data(
        self,
        fn: bytes,
        cn: bytes,
        data: bytes = b'',
        m: bytes = b''
    ) -> None:
        """
        Wrapper for GS ( k, to calculate and send correct data length.

        Args:
            fn: Function to use.
            cn: Output code type.
            data: Data to send.
            m: Modifier/variant for function.
        """
        if len(m) > 1 or len(cn) != 1 or len(fn) != 1:
            raise ValueError("cn and fn must be one character each.")

        header = self._int_low_high(len(data) + len(m) + 2, 2)
        self._connector.write(self.GS + b"(k" + header + cn + fn + m + data)

    def _wrapper_send_graphics_data(
        self,
        m: bytes,
        fn: bytes,
        data: bytes = b''
    ) -> None:
        """
        Wrapper for GS ( L, to calculate and send correct data length.

        Args:
            m: Modifier/variant for function.
            fn: Function number.
            data: Data to send.
        """
        if len(m) != 1 or len(fn) != 1:
            raise ValueError("m and fn must be one character each.")

        header = self._int_low_high(len(data) + 2, 2)
        self._connector.write(self.GS + b"(L" + header + m + fn + data)

    @staticmethod
    def _data_header(inputs: List[int], long: bool = True) -> bytes:
        """
        Convert widths and heights to bytes for graphics commands.

        Args:
            inputs: List of values to convert.
            long: True to use 2 bytes per value, False to use 1 byte.

        Returns:
            Header bytes.
        """
        output = []
        for value in inputs:
            if long:
                output.append(Printer._int_low_high(value, 2))
            else:
                Printer._validate_integer(value, 0, 255, "_data_header")
                output.append(bytes([value]))
        return b"".join(output)

    @staticmethod
    def _int_low_high(value: int, length: int) -> bytes:
        """
        Generate bytes for a number: in lower and higher parts.

        Args:
            value: Input number.
            length: The number of bytes to output (1-4).

        Returns:
            Bytes representation.
        """
        max_input = (1 << (length * 8)) - 1
        Printer._validate_integer(length, 1, 4, "_int_low_high")
        Printer._validate_integer(value, 0, max_input, "_int_low_high")

        output = []
        for _ in range(length):
            output.append(value % 256)
            value = value // 256
        return bytes(output)

    # Validation methods

    @staticmethod
    def _validate_boolean(test: bool, source: str) -> None:
        """Validate that the argument is a boolean."""
        if not isinstance(test, bool):
            raise ValueError(f"Argument to {source} must be a boolean")

    @staticmethod
    def _validate_float(
        test: float,
        min_val: float,
        max_val: float,
        source: str,
        argument: str = "Argument"
    ) -> None:
        """Validate that the argument is a float within the specified range."""
        if not isinstance(test, (int, float)):
            raise ValueError(f"{argument} given to {source} must be a float, but '{test}' was given.")
        if test < min_val or test > max_val:
            raise ValueError(f"{argument} given to {source} must be in range {min_val} to {max_val}, but {test} was given.")

    @staticmethod
    def _validate_integer(
        test: int,
        min_val: int,
        max_val: int,
        source: str,
        argument: str = "Argument"
    ) -> None:
        """Validate that the argument is an integer within the specified range."""
        Printer._validate_integer_multi(test, [[min_val, max_val]], source, argument)

    @staticmethod
    def _validate_integer_multi(
        test: int,
        ranges: List[List[int]],
        source: str,
        argument: str = "Argument"
    ) -> None:
        """Validate that the argument is an integer within one of the specified ranges."""
        if not isinstance(test, int) or isinstance(test, bool):
            raise ValueError(f"{argument} given to {source} must be a number, but '{test}' was given.")

        match = False
        for range_pair in ranges:
            if range_pair[0] <= test <= range_pair[1]:
                match = True
                break

        if not match:
            range_str = "range "
            for i, r in enumerate(ranges):
                range_str += f"{r[0]}-{r[1]}"
                if i == len(ranges) - 1:
                    pass
                elif i == len(ranges) - 2:
                    range_str += " or "
                else:
                    range_str += ", "
            raise ValueError(f"{argument} given to {source} must be in {range_str}, but {test} was given.")

    @staticmethod
    def _validate_string_regex(
        test: str,
        source: str,
        regex: str,
        argument: str = "Argument"
    ) -> None:
        """Validate that the argument matches the given regex."""
        if not re.match(regex, test):
            raise ValueError(f"{argument} given to {source} is invalid. It should match regex '{regex}', but '{test}' was given.")
