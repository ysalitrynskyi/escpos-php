#!/usr/bin/env python3
"""
Graphics printing example for escpos-printer.

This example demonstrates printing images.
"""

import sys
import os

# Try to import PIL for creating test images
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from escpos import Printer, EscposImage
from escpos.connectors import DummyConnector


def create_test_image(width: int = 200, height: int = 50) -> str:
    """
    Create a simple test image and return its path.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        Path to the temporary image file.
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL/Pillow is required for this example")

    import tempfile

    # Create a simple gradient image
    img = Image.new('RGB', (width, height), color='white')

    # Draw some pattern
    for x in range(width):
        for y in range(height):
            if (x + y) % 20 < 10:
                img.putpixel((x, y), (0, 0, 0))

    # Save to temporary file
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    img.save(path)
    return path


def main():
    """Run the graphics demo."""
    if not PIL_AVAILABLE:
        print("This example requires PIL/Pillow to be installed.")
        print("Install with: pip install pillow")
        sys.exit(1)

    connector = DummyConnector()
    printer = Printer(connector)

    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.text("Graphics Examples\n")
    printer.text("=================\n\n")

    # Create a test image
    temp_image_path = create_test_image()

    try:
        # Load and print the image
        printer.text("Test Pattern:\n")
        img = EscposImage.load(temp_image_path)
        printer.graphics(img)
        printer.feed(2)

        # Print at double width
        printer.text("Double Width:\n")
        printer.graphics(img, Printer.IMG_DOUBLE_WIDTH)
        printer.feed(2)

        # Print at double height
        printer.text("Double Height:\n")
        printer.graphics(img, Printer.IMG_DOUBLE_HEIGHT)
        printer.feed(2)

        # Print at double size (both)
        printer.text("Double Size:\n")
        printer.graphics(img, Printer.IMG_DOUBLE_WIDTH | Printer.IMG_DOUBLE_HEIGHT)
        printer.feed(3)

    finally:
        # Clean up temporary file
        os.unlink(temp_image_path)

    printer.cut()
    printer.close()

    print("Graphics demo completed!")
    print(f"Output would be {len(connector.get_data())} bytes")


if __name__ == "__main__":
    main()
