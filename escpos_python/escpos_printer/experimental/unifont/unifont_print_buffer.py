"""
UnifontPrintBuffer - Print buffer using Unifont glyphs.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import TYPE_CHECKING, Optional, List

from escpos_printer.buffers.print_buffer import PrintBuffer
from escpos_printer.experimental.unifont.column_format_glyph import ColumnFormatGlyphFactory
from escpos_printer.experimental.unifont.unifont_glyph_factory import UnifontGlyphFactory
from escpos_printer.experimental.unifont.font_map import FontMap

if TYPE_CHECKING:
    from escpos_printer.printer import Printer


class UnifontPrintBuffer(PrintBuffer):
    """
    Print buffer that renders text using Unifont glyphs.

    This buffer renders text as graphics using Unifont bitmap font data,
    allowing printing of characters not supported by the printer's built-in fonts.
    """

    def __init__(self, glyph_factory: ColumnFormatGlyphFactory):
        """
        Create a new UnifontPrintBuffer.

        Args:
            glyph_factory: Factory for creating glyph data.
        """
        self._printer: Optional['Printer'] = None
        self._glyph_factory = glyph_factory
        self._current_line: List[int] = []  # Code points

    def flush(self) -> None:
        """
        Flush the buffer, rendering any pending text.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")

        if self._current_line:
            self._render_and_print()
            self._current_line = []

    def get_printer(self) -> Optional['Printer']:
        """
        Get the printer this buffer is attached to.

        Returns:
            The Printer instance, or None if not attached.
        """
        return self._printer

    def set_printer(self, printer: Optional['Printer']) -> None:
        """
        Set the printer this buffer is attached to.

        Args:
            printer: The Printer instance, or None to detach.
        """
        self._printer = printer

    def write_text(self, text: str) -> None:
        """
        Write text to the buffer.

        Args:
            text: Text to write, as UTF-8.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")

        for char in text:
            if char == '\n':
                self.flush()
                self._printer.feed()
            elif char == '\r':
                # Skip carriage returns
                continue
            else:
                self._current_line.append(ord(char))

    def write_text_raw(self, text: str) -> None:
        """
        Write text to the buffer (same as write_text for Unifont buffer).

        Args:
            text: Text to write.
        """
        self.write_text(text)

    def _render_and_print(self) -> None:
        """
        Render the current line as graphics and print it.
        """
        if not self._current_line:
            return

        # Collect all glyphs
        glyphs = [self._glyph_factory.get_glyph(cp) for cp in self._current_line]

        # Calculate total width and max height
        total_width = sum(g.get_width() for g in glyphs)
        max_height = max(g.get_height() for g in glyphs) if glyphs else 0

        if total_width == 0 or max_height == 0:
            return

        # Build column format data
        # Each line is printed separately in column format
        line_height = 24  # Standard line height for column format (3 bytes)
        bytes_per_column = 3

        column_data = bytearray(total_width * bytes_per_column)

        x_offset = 0
        for glyph in glyphs:
            glyph_data = glyph.get_column_format_data()
            glyph_width = glyph.get_width()
            glyph_bytes_per_col = len(glyph_data) // glyph_width if glyph_width > 0 else 0

            for x in range(glyph_width):
                for b in range(min(bytes_per_column, glyph_bytes_per_col)):
                    src_idx = x * glyph_bytes_per_col + b
                    dst_idx = (x_offset + x) * bytes_per_column + b
                    if src_idx < len(glyph_data) and dst_idx < len(column_data):
                        column_data[dst_idx] = glyph_data[src_idx]

            x_offset += glyph_width

        # Print using column format command
        self._print_column_format(bytes(column_data), total_width)

    def _print_column_format(self, data: bytes, width: int) -> None:
        """
        Print data in column format.

        Args:
            data: Column format data.
            width: Width in pixels.
        """
        from escpos_printer.printer import Printer

        # Set line spacing for column format
        self._printer.set_line_spacing(24)

        # Send column format command
        # ESC * m nL nH data
        # m = 33 for 24-dot double density
        m = 33
        n_l = width & 0xFF
        n_h = (width >> 8) & 0xFF

        self._printer.get_print_connector().write(
            Printer.ESC + b"*" + bytes([m, n_l, n_h]) + data
        )
        self._printer.feed()

        # Reset line spacing
        self._printer.set_line_spacing()

    @staticmethod
    def create_from_hex_file(filename: str) -> 'UnifontPrintBuffer':
        """
        Create a UnifontPrintBuffer from a Unifont .hex file.

        Args:
            filename: Path to .hex file.

        Returns:
            A UnifontPrintBuffer instance.
        """
        font_map = FontMap.load_hex_file(filename)
        glyph_factory = UnifontGlyphFactory(font_map)
        return UnifontPrintBuffer(glyph_factory)
