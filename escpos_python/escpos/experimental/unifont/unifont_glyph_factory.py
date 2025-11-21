"""
UnifontGlyphFactory - Factory for creating Unifont glyphs.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Optional

from escpos.experimental.unifont.column_format_glyph import (
    ColumnFormatGlyph,
    ColumnFormatGlyphFactory,
    SimpleColumnFormatGlyph,
)
from escpos.experimental.unifont.font_map import FontMap


class UnifontGlyphFactory(ColumnFormatGlyphFactory):
    """
    Factory for creating glyphs from Unifont font data.
    """

    # Standard Unifont dimensions
    GLYPH_HEIGHT = 16
    NARROW_WIDTH = 8
    WIDE_WIDTH = 16

    def __init__(self, font_map: FontMap):
        """
        Create a new UnifontGlyphFactory.

        Args:
            font_map: FontMap containing Unifont data.
        """
        self._font_map = font_map
        self._fallback_glyph: Optional[ColumnFormatGlyph] = None

    def get_glyph(self, code_point: int) -> ColumnFormatGlyph:
        """
        Get a glyph for the specified code point.

        Args:
            code_point: Unicode code point.

        Returns:
            A ColumnFormatGlyph instance.
        """
        glyph_data = self._font_map.get_glyph_data(code_point)

        if glyph_data is None:
            return self._get_fallback_glyph()

        # Determine glyph width based on data length
        # Unifont: 16 bytes = 8px wide, 32 bytes = 16px wide
        if len(glyph_data) == 16:
            width = self.NARROW_WIDTH
        elif len(glyph_data) == 32:
            width = self.WIDE_WIDTH
        else:
            return self._get_fallback_glyph()

        # Convert raster format to column format
        column_data = self._convert_to_column_format(glyph_data, width)

        return SimpleColumnFormatGlyph(width, self.GLYPH_HEIGHT, column_data)

    def _convert_to_column_format(self, raster_data: bytes, width: int) -> bytes:
        """
        Convert Unifont raster data to column format.

        Unifont stores data in row-major order (one row at a time).
        Column format stores data in column-major order (one column at a time).

        Args:
            raster_data: Unifont glyph data.
            width: Width of the glyph in pixels.

        Returns:
            Column format data.
        """
        bytes_per_row = width // 8
        height = self.GLYPH_HEIGHT

        # Output is height/8 bytes per column, times width columns
        # For 16px height with 3-byte columns (24 dots), we need 2 bytes per column
        column_bytes = (height + 7) // 8
        output = bytearray(width * column_bytes)

        for x in range(width):
            column_value = 0
            for y in range(height):
                # Get the pixel from raster format
                row_start = y * bytes_per_row
                byte_offset = x // 8
                bit_offset = 7 - (x % 8)

                if row_start + byte_offset < len(raster_data):
                    pixel = (raster_data[row_start + byte_offset] >> bit_offset) & 1
                else:
                    pixel = 0

                if pixel:
                    column_value |= (1 << (height - 1 - y))

            # Write column value to output
            for b in range(column_bytes):
                shift = (column_bytes - 1 - b) * 8
                output[x * column_bytes + b] = (column_value >> shift) & 0xFF

        return bytes(output)

    def _get_fallback_glyph(self) -> ColumnFormatGlyph:
        """
        Get a fallback glyph for missing characters.

        Returns:
            A ColumnFormatGlyph representing a missing character.
        """
        if self._fallback_glyph is None:
            # Create a simple box glyph as fallback
            width = self.NARROW_WIDTH
            column_bytes = (self.GLYPH_HEIGHT + 7) // 8
            data = bytearray(width * column_bytes)

            # Draw a box outline
            for x in range(width):
                for b in range(column_bytes):
                    if x == 0 or x == width - 1:
                        data[x * column_bytes + b] = 0xFF  # Vertical lines
                    elif b == 0:
                        data[x * column_bytes + b] = 0x80  # Top line
                    elif b == column_bytes - 1:
                        data[x * column_bytes + b] = 0x01  # Bottom line

            self._fallback_glyph = SimpleColumnFormatGlyph(
                width, self.GLYPH_HEIGHT, bytes(data)
            )

        return self._fallback_glyph

    def set_fallback_glyph(self, glyph: ColumnFormatGlyph) -> None:
        """
        Set the fallback glyph for missing characters.

        Args:
            glyph: The fallback glyph to use.
        """
        self._fallback_glyph = glyph
