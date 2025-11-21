"""
EscposImage class - Image handling for ESC/POS printers.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

from abc import ABC
from typing import Optional, List, Tuple
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class EscposImage(ABC):
    """
    This class deals with images in raster formats, and converts them into formats
    which are suitable for use on thermal receipt printers.

    Input formats:
    - PNG, JPG, GIF, BMP, and other formats supported by Pillow

    Output formats:
    - ESC/POS raster format
    - ESC/POS column format
    """

    def __init__(self, filename: Optional[str] = None, allow_optimisations: bool = True):
        """
        Construct a new EscposImage.

        Args:
            filename: Path to image filename, or None to create an empty image.
            allow_optimisations: True (default) to use library-specific tricks
                to speed up rendering.
        """
        self._filename = filename
        self._allow_optimisations = allow_optimisations

        # Image dimensions
        self._img_width = 0
        self._img_height = 0

        # Image data in rows: 1 for black, 0 for white
        self._img_data: Optional[str] = None

        # Cached format data
        self._img_raster_data: Optional[bytes] = None
        self._img_column_data: dict = {}

    def get_width(self) -> int:
        """Get width of the image in pixels."""
        return self._img_width

    def get_height(self) -> int:
        """Get height of the image in pixels."""
        return self._img_height

    def get_width_bytes(self) -> int:
        """Get number of bytes to represent a row of this image."""
        return (self._img_width + 7) // 8

    def get_height_bytes(self) -> int:
        """Get number of bytes to represent a column of this image."""
        return (self._img_height + 7) // 8

    def to_raster_format(self) -> bytes:
        """
        Output the image in raster (row) format.

        This can result in padding on the right of the image, if its width
        is not divisible by 8.

        Returns:
            The image in raster format.
        """
        if self._img_raster_data is not None:
            return self._img_raster_data

        if self._allow_optimisations:
            self._img_raster_data = self._get_raster_format_from_file(self._filename)

        if self._img_raster_data is None:
            if self._img_data is None:
                self._load_image_data(self._filename)
            self._img_raster_data = self._get_raster_format()

        return self._img_raster_data

    def to_column_format(self, double_density: bool = False) -> List[bytes]:
        """
        Output the image in column format.

        Args:
            double_density: True for double density (24px) lines, False for single (8px).

        Returns:
            List of bytes, one item per line of output.
        """
        density_idx = 1 if double_density else 0

        if density_idx in self._img_column_data:
            return self._img_column_data[density_idx]

        self._img_column_data[density_idx] = None

        if self._allow_optimisations:
            data = self._get_column_format_from_file(self._filename, double_density)
            self._img_column_data[density_idx] = data

        if self._img_column_data[density_idx] is None:
            if self._img_data is None:
                self._load_image_data(self._filename)
            self._img_column_data[density_idx] = self._get_column_format(double_density)

        return self._img_column_data[density_idx]

    def _load_image_data(self, filename: Optional[str] = None) -> None:
        """
        Load an image from disk.

        This default implementation always gives a zero-sized image.
        Subclasses should override this method.

        Args:
            filename: Filename to load from.
        """
        self._img_width = 0
        self._img_height = 0
        self._img_data = ""

    def _set_img_data(self, data: str) -> None:
        """Set image data."""
        self._img_data = data

    def _set_img_width(self, width: int) -> None:
        """Set image width."""
        self._img_width = width

    def _set_img_height(self, height: int) -> None:
        """Set image height."""
        self._img_height = height

    def _get_raster_format_from_file(self, filename: Optional[str] = None) -> Optional[bytes]:
        """
        Get raster format data directly from file.

        Override in subclasses for optimized implementations.

        Args:
            filename: Filename to load from.

        Returns:
            Raster format data, or None if no optimized renderer available.
        """
        return None

    def _get_column_format_from_file(
        self,
        filename: Optional[str] = None,
        high_density_vertical: bool = True
    ) -> Optional[List[bytes]]:
        """
        Get column format data directly from file.

        Override in subclasses for optimized implementations.

        Args:
            filename: Filename to load from.
            high_density_vertical: True for high density output (24px lines).

        Returns:
            Column format data as list, or None if not available.
        """
        return None

    def _get_raster_format(self) -> bytes:
        """
        Get raster format from loaded image pixels.

        Returns:
            Raster format data.
        """
        width_pixels = self.get_width()
        height_pixels = self.get_height()
        width_bytes = self.get_width_bytes()

        data = bytearray(width_bytes * height_pixels)

        if len(data) == 0:
            return bytes(data)

        x, y, bit, byte_idx, byte_val = 0, 0, 0, 0, 0

        while True:
            pixel = int(self._img_data[y * width_pixels + x]) if (y * width_pixels + x) < len(self._img_data) else 0
            byte_val |= pixel << (7 - bit)
            x += 1
            bit += 1

            if x >= width_pixels:
                x = 0
                y += 1
                bit = 8
                if y >= height_pixels:
                    data[byte_idx] = byte_val
                    break

            if bit >= 8:
                data[byte_idx] = byte_val
                byte_val = 0
                bit = 0
                byte_idx += 1

        if len(data) != self.get_width_bytes() * self.get_height():
            raise RuntimeError("Bug in _get_raster_format, wrong number of bytes.")

        return bytes(data)

    def _get_column_format(self, high_density: bool) -> List[bytes]:
        """
        Get column format from loaded image pixels.

        Args:
            high_density: True for high density output (24px lines).

        Returns:
            List of column format data, one item per row.
        """
        output = []
        i = 0
        while True:
            line = self._get_column_format_line(i, high_density)
            if line is None:
                break
            output.append(line)
            i += 1
        return output

    def _get_column_format_line(self, line_no: int, high_density: bool) -> Optional[bytes]:
        """
        Output image in column format for a single line.

        Args:
            line_no: Line number to retrieve.
            high_density: True for high density output (24px lines).

        Returns:
            Column format data, or None if no more data.
        """
        width_pixels = self.get_width()
        height_pixels = self.get_height()
        line_height = 3 if high_density else 1

        data = bytearray(width_pixels * line_height)
        y_start = line_height * 8 * line_no

        if y_start >= height_pixels:
            return None

        if len(data) == 0:
            return bytes(data)

        x, y, bit, byte_idx, byte_val = 0, 0, 0, 0, 0

        while True:
            y_real = y + y_start
            if y_real < height_pixels:
                pixel = int(self._img_data[y_real * width_pixels + x]) if (y_real * width_pixels + x) < len(self._img_data) else 0
                byte_val |= pixel << (7 - bit)

            y += 1
            bit += 1

            if y >= line_height * 8:
                y = 0
                x += 1
                bit = 8
                if x >= width_pixels:
                    data[byte_idx] = byte_val
                    break

            if bit >= 8:
                data[byte_idx] = byte_val
                byte_val = 0
                bit = 0
                byte_idx += 1

        if len(data) != width_pixels * line_height:
            raise RuntimeError("Bug in _get_column_format_line, wrong number of bytes.")

        return bytes(data)

    @staticmethod
    def is_pillow_loaded() -> bool:
        """Check if Pillow is loaded."""
        return PIL_AVAILABLE

    @staticmethod
    def load(
        filename: str,
        allow_optimisations: bool = True,
        preferred: Optional[List[str]] = None
    ) -> 'EscposImage':
        """
        Load an image from file, auto-selecting an EscposImage implementation.

        Args:
            filename: File to load from.
            allow_optimisations: True to allow fastest rendering shortcuts.
            preferred: Order to try to load libraries in.

        Returns:
            An EscposImage instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If no suitable library could be found.
        """
        if preferred is None:
            preferred = ['pillow', 'native']

        # Check file exists
        path = Path(filename)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File '{filename}' does not exist, or is not readable.")

        ext = path.suffix.lower().lstrip('.')

        for implementation in preferred:
            if implementation == 'pillow':
                if not PIL_AVAILABLE:
                    continue
                from escpos.pillow_escpos_image import PillowEscposImage
                return PillowEscposImage(filename, allow_optimisations)
            elif implementation == 'native':
                # Native supports limited formats
                if ext not in ['bmp', 'gif', 'pbm', 'png', 'ppm', 'pgm', 'wbmp']:
                    continue
                from escpos.native_escpos_image import NativeEscposImage
                return NativeEscposImage(filename, allow_optimisations)
            else:
                raise ValueError(f"'{implementation}' is not a known EscposImage implementation")

        raise ValueError(f"No suitable EscposImage implementation found for '{filename}'.")
