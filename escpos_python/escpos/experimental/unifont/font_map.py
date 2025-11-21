"""
FontMap - Font mapping for Unifont support.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2024 Yevhen Salitrynskyi <https://github.com/ysalitrynskyi> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Dict, Optional
from pathlib import Path


class FontMap:
    """
    Manages font data for glyph rendering.
    """

    def __init__(self, font_data: Optional[Dict[int, bytes]] = None):
        """
        Create a new FontMap.

        Args:
            font_data: Dictionary mapping code points to glyph data.
        """
        self._font_data: Dict[int, bytes] = font_data or {}

    def get_glyph_data(self, code_point: int) -> Optional[bytes]:
        """
        Get glyph data for a code point.

        Args:
            code_point: Unicode code point.

        Returns:
            Glyph data, or None if not found.
        """
        return self._font_data.get(code_point)

    def has_glyph(self, code_point: int) -> bool:
        """
        Check if a glyph exists for the code point.

        Args:
            code_point: Unicode code point.

        Returns:
            True if glyph exists, False otherwise.
        """
        return code_point in self._font_data

    @staticmethod
    def load_hex_file(filename: str) -> 'FontMap':
        """
        Load a Unifont .hex file.

        The .hex format is: CODE_POINT:HEX_DATA
        Where CODE_POINT is 4 hex digits and HEX_DATA is the glyph bitmap.

        Args:
            filename: Path to .hex file.

        Returns:
            A FontMap instance.
        """
        font_data: Dict[int, bytes] = {}

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue

                code_point_str, hex_data = line.split(':', 1)
                try:
                    code_point = int(code_point_str, 16)
                    glyph_data = bytes.fromhex(hex_data)
                    font_data[code_point] = glyph_data
                except ValueError:
                    continue

        return FontMap(font_data)
