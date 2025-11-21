"""
ImagePrintBuffer - Image-based text rendering buffer.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2024 Yevhen Salitrynskyi <https://github.com/ysalitrynskyi> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import TYPE_CHECKING, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from escpos.buffers.print_buffer import PrintBuffer

if TYPE_CHECKING:
    from escpos.printer import Printer


class ImagePrintBuffer(PrintBuffer):
    """
    Print buffer that renders text to images using Pillow.

    This is useful when you need complete control over font rendering,
    or when the printer doesn't support certain character sets.
    """

    def __init__(
        self,
        font_path: Optional[str] = None,
        font_size: int = 12,
        line_width: int = 384
    ):
        """
        Create an image print buffer.

        Args:
            font_path: Path to TTF font file, or None for default.
            font_size: Font size in pixels.
            line_width: Width of the print area in pixels.
        """
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow is required for ImagePrintBuffer. "
                "Install with: pip install pillow"
            )

        self._printer: Optional['Printer'] = None
        self._font_path = font_path
        self._font_size = font_size
        self._line_width = line_width

        # Load font
        if font_path:
            self._font = ImageFont.truetype(font_path, font_size)
        else:
            try:
                # Try to use a monospace font
                self._font = ImageFont.load_default()
            except Exception:
                self._font = None

        # Buffer for current line
        self._current_line = ""

    def flush(self) -> None:
        """
        Flush the buffer, rendering any pending text as an image.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")

        if self._current_line:
            self._render_and_print(self._current_line)
            self._current_line = ""

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
        Write text to the buffer with automatic character encoding.

        Args:
            text: Text to write, as UTF-8.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")

        for char in text:
            if char == '\n':
                self.flush()
                self._printer.feed()
            else:
                self._current_line += char

    def write_text_raw(self, text: str) -> None:
        """
        Write text to the buffer (same as write_text for image buffer).

        Args:
            text: Text to write.
        """
        self.write_text(text)

    def _render_and_print(self, text: str) -> None:
        """
        Render text as an image and print it.

        Args:
            text: Text to render.
        """
        if not text.strip():
            return

        # Create image for text
        # First, calculate text size
        if self._font:
            # Get text bounding box
            dummy_img = Image.new('1', (1, 1), color=1)
            draw = ImageDraw.Draw(dummy_img)
            bbox = draw.textbbox((0, 0), text, font=self._font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # Estimate size
            text_width = len(text) * 8
            text_height = self._font_size

        # Create actual image
        img_width = min(self._line_width, text_width + 4)
        img_height = text_height + 4

        img = Image.new('1', (img_width, img_height), color=1)  # White background
        draw = ImageDraw.Draw(img)
        draw.text((2, 2), text, font=self._font, fill=0)  # Black text

        # Print the image
        from escpos.pillow_escpos_image import PillowEscposImage
        escpos_img = PillowEscposImage.from_pil_image(img)
        self._printer.graphics(escpos_img)
