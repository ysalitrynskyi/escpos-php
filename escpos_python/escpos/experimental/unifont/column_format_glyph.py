"""
ColumnFormatGlyph - Glyph data in column format.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from abc import ABC, abstractmethod
from typing import List


class ColumnFormatGlyph(ABC):
    """
    Abstract class representing a glyph in column format.
    """

    @abstractmethod
    def get_width(self) -> int:
        """
        Get the width of this glyph in pixels.

        Returns:
            Width in pixels.
        """
        pass

    @abstractmethod
    def get_height(self) -> int:
        """
        Get the height of this glyph in pixels.

        Returns:
            Height in pixels.
        """
        pass

    @abstractmethod
    def get_column_format_data(self) -> bytes:
        """
        Get the glyph data in column format.

        Returns:
            Column format data.
        """
        pass


class ColumnFormatGlyphFactory(ABC):
    """
    Abstract factory for creating column format glyphs.
    """

    @abstractmethod
    def get_glyph(self, code_point: int) -> ColumnFormatGlyph:
        """
        Get a glyph for the specified code point.

        Args:
            code_point: Unicode code point.

        Returns:
            A ColumnFormatGlyph instance.
        """
        pass


class SimpleColumnFormatGlyph(ColumnFormatGlyph):
    """
    Simple implementation of ColumnFormatGlyph.
    """

    def __init__(self, width: int, height: int, data: bytes):
        """
        Create a new SimpleColumnFormatGlyph.

        Args:
            width: Width in pixels.
            height: Height in pixels.
            data: Column format data.
        """
        self._width = width
        self._height = height
        self._data = data

    def get_width(self) -> int:
        """Get the width of this glyph in pixels."""
        return self._width

    def get_height(self) -> int:
        """Get the height of this glyph in pixels."""
        return self._height

    def get_column_format_data(self) -> bytes:
        """Get the glyph data in column format."""
        return self._data
