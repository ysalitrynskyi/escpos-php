"""
PillowEscposImage - Image handling using Pillow (PIL fork).

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

from typing import Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from escpos.escpos_image import EscposImage


class PillowEscposImage(EscposImage):
    """
    Implementation of EscposImage using the Pillow library.

    This replaces both GdEscposImage and ImagickEscposImage from the PHP version.
    """

    def __init__(self, filename: Optional[str] = None, allow_optimisations: bool = True):
        """
        Construct a new PillowEscposImage.

        Args:
            filename: Path to image file, or None for empty image.
            allow_optimisations: True to use library-specific shortcuts.
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow is required for image support. Install with: pip install pillow")

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

        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if im.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])  # Use alpha channel as mask
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

        # Convert to grayscale
        gray = im.convert('L')

        # Create binary image data (1 for black, 0 for white)
        # We need to invert because ESC/POS expects 1=black, 0=white
        # but PIL's threshold works as 1=white, 0=black in mode '1'
        img_data = []
        pixels = gray.load()

        for y in range(img_height):
            for x in range(img_width):
                # Get grayscale value (0-255)
                gray_val = pixels[x, y]
                # Convert to 1 (black) or 0 (white) using threshold of 128
                black = 1 if gray_val < 128 else 0
                img_data.append(str(black))

        self._set_img_width(img_width)
        self._set_img_height(img_height)
        self._set_img_data(''.join(img_data))

    @staticmethod
    def from_pil_image(im: 'Image.Image', allow_optimisations: bool = True) -> 'PillowEscposImage':
        """
        Create an EscposImage directly from a PIL Image object.

        Args:
            im: PIL Image object.
            allow_optimisations: True to use library-specific shortcuts.

        Returns:
            A PillowEscposImage instance.
        """
        instance = PillowEscposImage(None, allow_optimisations)

        # Convert if necessary
        if im.mode == 'RGBA':
            background = Image.new('RGB', im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[3])
            im = background
        elif im.mode != 'RGB':
            im = im.convert('RGB')

        instance._read_image_from_pil(im)
        return instance


# Alias for backward compatibility with PHP naming
GdEscposImage = PillowEscposImage
ImagickEscposImage = PillowEscposImage
