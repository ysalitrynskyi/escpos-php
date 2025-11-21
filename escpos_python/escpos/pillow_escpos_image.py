"""
PillowEscposImage - Image handling using Pillow (PIL fork).

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2024 Yevhen Salitrynskyi <https://github.com/ysalitrynskyi> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Optional, Literal
from enum import Enum

try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from escpos.escpos_image import EscposImage


class DitherMode(Enum):
    """Dithering modes for image conversion."""
    NONE = "none"  # Simple threshold (default)
    FLOYDSTEINBERG = "floydsteinberg"  # Floyd-Steinberg error diffusion
    ATKINSON = "atkinson"  # Atkinson dithering (lighter)
    ORDERED = "ordered"  # Ordered/Bayer dithering


class PillowEscposImage(EscposImage):
    """
    Implementation of EscposImage using the Pillow library.

    Supports various dithering algorithms for better image quality on
    thermal printers.
    """

    def __init__(
        self,
        filename: Optional[str] = None,
        allow_optimisations: bool = True,
        dither: DitherMode = DitherMode.NONE,
        threshold: int = 128
    ):
        """
        Construct a new PillowEscposImage.

        Args:
            filename: Path to image file, or None for empty image.
            allow_optimisations: True to use library-specific shortcuts.
            dither: Dithering algorithm to use (NONE, FLOYDSTEINBERG, ATKINSON, ORDERED).
            threshold: Threshold for simple threshold mode (0-255, default 128).
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image support. Install with: pip install pillow")

        self._dither = dither
        self._threshold = threshold

        super().__init__(filename, allow_optimisations)

        if filename is not None:
            self._load_image_data(filename)

    def _load_image_data(self, filename: Optional[str] = None) -> None:
        """
        Load an image from disk using Pillow.

        Args:
            filename: The filename to load from.
        """
        if filename is None:
            return super()._load_image_data(filename)

        # Open image
        im = Image.open(filename)
        self._process_pil_image(im)

    def _process_pil_image(self, im: 'Image.Image') -> None:
        """
        Process a PIL Image with alpha handling and dithering.

        Args:
            im: PIL Image object to process.
        """
        # Convert RGBA to RGB with white background
        if im.mode == 'RGBA':
            background = Image.new('RGB', im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])
            im = background
        elif im.mode != 'RGB':
            im = im.convert('RGB')

        self._read_image_from_pil(im)

    def _read_image_from_pil(self, im: 'Image.Image') -> None:
        """
        Load actual image pixels from PIL Image object.

        Args:
            im: PIL Image object to use.
        """
        img_width, img_height = im.size

        # Convert to grayscale first
        gray = im.convert('L')

        # Apply dithering based on selected mode
        if self._dither == DitherMode.FLOYDSTEINBERG:
            binary = self._dither_floydsteinberg(gray)
        elif self._dither == DitherMode.ATKINSON:
            binary = self._dither_atkinson(gray)
        elif self._dither == DitherMode.ORDERED:
            binary = self._dither_ordered(gray)
        else:
            # Simple threshold (default)
            binary = self._threshold_convert(gray)

        # Extract binary data
        img_data = []
        pixels = binary.load()

        for y in range(img_height):
            for x in range(img_width):
                # In mode '1', 0=black, 255=white
                # We need 1=black, 0=white for ESC/POS
                black = 1 if pixels[x, y] == 0 else 0
                img_data.append(str(black))

        self._set_img_width(img_width)
        self._set_img_height(img_height)
        self._set_img_data(''.join(img_data))

    def _threshold_convert(self, gray: 'Image.Image') -> 'Image.Image':
        """
        Convert grayscale to binary using simple threshold.

        Args:
            gray: Grayscale PIL Image.

        Returns:
            Binary (mode '1') PIL Image.
        """
        return gray.point(lambda x: 255 if x >= self._threshold else 0, mode='1')

    def _dither_floydsteinberg(self, gray: 'Image.Image') -> 'Image.Image':
        """
        Apply Floyd-Steinberg dithering.

        Args:
            gray: Grayscale PIL Image.

        Returns:
            Binary (mode '1') PIL Image with dithering applied.
        """
        # PIL's convert to '1' with dither uses Floyd-Steinberg by default
        return gray.convert('1', dither=Image.Dither.FLOYDSTEINBERG)

    def _dither_atkinson(self, gray: 'Image.Image') -> 'Image.Image':
        """
        Apply Atkinson dithering (produces lighter output than Floyd-Steinberg).

        Args:
            gray: Grayscale PIL Image.

        Returns:
            Binary (mode '1') PIL Image with dithering applied.
        """
        width, height = gray.size
        pixels = list(gray.getdata())
        output = [0] * len(pixels)

        for y in range(height):
            for x in range(width):
                idx = y * width + x
                old_pixel = pixels[idx]
                new_pixel = 255 if old_pixel >= 128 else 0
                output[idx] = new_pixel
                error = (old_pixel - new_pixel) // 8

                # Atkinson distributes error to 6 neighbors (1/8 each, total 6/8)
                # This creates a lighter result than Floyd-Steinberg
                neighbors = [
                    (x + 1, y),      # right
                    (x + 2, y),      # right+1
                    (x - 1, y + 1),  # bottom-left
                    (x, y + 1),      # bottom
                    (x + 1, y + 1),  # bottom-right
                    (x, y + 2),      # bottom+1
                ]

                for nx, ny in neighbors:
                    if 0 <= nx < width and 0 <= ny < height:
                        nidx = ny * width + nx
                        if nidx < len(pixels):
                            pixels[nidx] = max(0, min(255, pixels[nidx] + error))

        result = Image.new('1', (width, height))
        result.putdata([0 if p < 128 else 255 for p in output])
        return result

    def _dither_ordered(self, gray: 'Image.Image') -> 'Image.Image':
        """
        Apply ordered (Bayer) dithering.

        Args:
            gray: Grayscale PIL Image.

        Returns:
            Binary (mode '1') PIL Image with dithering applied.
        """
        # 4x4 Bayer matrix
        bayer = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]

        width, height = gray.size
        pixels = gray.load()
        result = Image.new('1', (width, height))
        result_pixels = result.load()

        for y in range(height):
            for x in range(width):
                # Normalize pixel value to 0-16 range and compare with Bayer threshold
                threshold = (bayer[y % 4][x % 4] + 1) * 16
                result_pixels[x, y] = 255 if pixels[x, y] >= threshold else 0

        return result

    @staticmethod
    def from_pil_image(
        im: 'Image.Image',
        allow_optimisations: bool = True,
        dither: DitherMode = DitherMode.NONE,
        threshold: int = 128
    ) -> 'PillowEscposImage':
        """
        Create an EscposImage directly from a PIL Image object.

        Args:
            im: PIL Image object.
            allow_optimisations: True to use library-specific shortcuts.
            dither: Dithering algorithm to use.
            threshold: Threshold for simple threshold mode.

        Returns:
            A PillowEscposImage instance.
        """
        instance = PillowEscposImage(None, allow_optimisations, dither, threshold)
        instance._process_pil_image(im)
        return instance

    @staticmethod
    def to_monochrome(
        im: 'Image.Image',
        dither: DitherMode = DitherMode.NONE,
        threshold: int = 128
    ) -> 'Image.Image':
        """
        Convert any image to monochrome (black and white).

        This is a utility method for converting images before printing.

        Args:
            im: PIL Image object (any mode).
            dither: Dithering algorithm to use.
            threshold: Threshold for simple threshold mode.

        Returns:
            Binary (mode '1') PIL Image.
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required")

        # Handle RGBA
        if im.mode == 'RGBA':
            background = Image.new('RGB', im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])
            im = background
        elif im.mode != 'RGB':
            im = im.convert('RGB')

        gray = im.convert('L')

        temp_instance = PillowEscposImage.__new__(PillowEscposImage)
        temp_instance._dither = dither
        temp_instance._threshold = threshold

        if dither == DitherMode.FLOYDSTEINBERG:
            return temp_instance._dither_floydsteinberg(gray)
        elif dither == DitherMode.ATKINSON:
            return temp_instance._dither_atkinson(gray)
        elif dither == DitherMode.ORDERED:
            return temp_instance._dither_ordered(gray)
        else:
            return temp_instance._threshold_convert(gray)


# Aliases for backward compatibility
GdEscposImage = PillowEscposImage
ImagickEscposImage = PillowEscposImage
