"""
Barcode Generator - Generate barcodes as images using python-barcode.

This provides a fallback for printers that don't support native barcode printing.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com>

This software is distributed under the terms of the MIT license.
"""

from typing import Optional, Tuple
from io import BytesIO

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Mapping from ESC/POS barcode types to python-barcode types
BARCODE_TYPE_MAP = {
    65: 'upca',      # BARCODE_UPCA
    66: 'upce',      # BARCODE_UPCE (not directly supported, use upc)
    67: 'ean13',     # BARCODE_JAN13 / EAN-13
    68: 'ean8',      # BARCODE_JAN8 / EAN-8
    69: 'code39',    # BARCODE_CODE39
    70: 'itf',       # BARCODE_ITF
    71: None,        # BARCODE_CODABAR (not in python-barcode)
    72: 'code93',    # BARCODE_CODE93 (may not be available)
    73: 'code128',   # BARCODE_CODE128
}


def generate_barcode_image(
    content: str,
    barcode_type: int,
    width: int = 2,
    height: int = 100,
    include_text: bool = True
) -> Optional['Image.Image']:
    """
    Generate a barcode as a PIL Image.

    Args:
        content: The data to encode.
        barcode_type: ESC/POS barcode type constant (65-73).
        width: Module width multiplier.
        height: Barcode height in pixels.
        include_text: Whether to include human-readable text.

    Returns:
        PIL Image of the barcode, or None if generation fails.
    """
    if not BARCODE_AVAILABLE or not PIL_AVAILABLE:
        return None

    bc_type = BARCODE_TYPE_MAP.get(barcode_type)
    if bc_type is None:
        return None

    try:
        # Get the barcode class
        bc_class = barcode.get_barcode_class(bc_type)

        # Configure writer options
        writer = ImageWriter()

        # Create barcode
        bc = bc_class(content, writer=writer)

        # Generate image to BytesIO
        buffer = BytesIO()
        bc.write(buffer, options={
            'module_width': width * 0.2,
            'module_height': height / 10,
            'write_text': include_text,
            'font_size': 10,
            'text_distance': 5,
        })

        # Load as PIL Image
        buffer.seek(0)
        img = Image.open(buffer)

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        return img

    except Exception:
        return None


def generate_qrcode_image(
    content: str,
    size: int = 3,
    error_correction: int = 0,
    border: int = 4
) -> Optional['Image.Image']:
    """
    Generate a QR code as a PIL Image.

    Args:
        content: The data to encode.
        size: Box size (pixels per module).
        error_correction: Error correction level (0=L, 1=M, 2=Q, 3=H).
        border: Border size in modules.

    Returns:
        PIL Image of the QR code, or None if generation fails.
    """
    if not QRCODE_AVAILABLE or not PIL_AVAILABLE:
        return None

    # Map error correction levels
    ec_map = {
        0: qrcode.constants.ERROR_CORRECT_L,
        1: qrcode.constants.ERROR_CORRECT_M,
        2: qrcode.constants.ERROR_CORRECT_Q,
        3: qrcode.constants.ERROR_CORRECT_H,
    }

    ec = ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_L)

    try:
        qr = qrcode.QRCode(
            version=None,  # Auto-determine
            error_correction=ec,
            box_size=size,
            border=border,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to RGB
        if hasattr(img, 'convert'):
            return img.convert('RGB')
        return img

    except Exception:
        return None


def is_barcode_available() -> bool:
    """Check if python-barcode is available."""
    return BARCODE_AVAILABLE


def is_qrcode_available() -> bool:
    """Check if qrcode library is available."""
    return QRCODE_AVAILABLE


def get_supported_barcode_types() -> list:
    """Get list of supported barcode types."""
    if not BARCODE_AVAILABLE:
        return []

    supported = []
    for escpos_type, bc_type in BARCODE_TYPE_MAP.items():
        if bc_type is not None:
            try:
                barcode.get_barcode_class(bc_type)
                supported.append(escpos_type)
            except Exception:
                pass
    return supported
