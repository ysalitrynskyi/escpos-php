#!/usr/bin/env python3
"""
Complete receipt example with logo.

This example demonstrates a complete receipt with logo, items, and formatting.
"""

import sys
import os
from datetime import datetime

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from escpos_thermal import Printer, EscposImage
from escpos_thermal.connectors import DummyConnector


def create_logo(width: int = 200, height: int = 80) -> str:
    """Create a simple text-based logo."""
    if not PIL_AVAILABLE:
        raise ImportError("PIL/Pillow is required")

    import tempfile

    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw a simple box logo
    draw.rectangle([10, 10, width - 10, height - 10], outline='black', width=3)
    draw.rectangle([15, 15, width - 15, height - 15], outline='black', width=1)

    # Add some lines for decoration
    draw.line([20, height // 2, width - 20, height // 2], fill='black', width=2)

    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    img.save(path)
    return path


def main():
    """Print a complete receipt."""
    connector = DummyConnector()
    printer = Printer(connector)

    # Print logo
    if PIL_AVAILABLE:
        logo_path = create_logo()
        try:
            printer.set_justification(Printer.JUSTIFY_CENTER)
            img = EscposImage.load(logo_path)
            printer.graphics(img)
            printer.feed(1)
        finally:
            os.unlink(logo_path)

    # Store header
    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.set_text_size(2, 2)
    printer.text("ACME STORE\n")
    printer.set_text_size(1, 1)
    printer.text("123 Main Street\n")
    printer.text("City, State 12345\n")
    printer.text("Tel: (555) 123-4567\n")
    printer.text("\n")

    # Transaction info
    printer.set_justification(Printer.JUSTIFY_LEFT)
    now = datetime.now()
    printer.text(f"Date: {now.strftime('%Y-%m-%d')}\n")
    printer.text(f"Time: {now.strftime('%H:%M:%S')}\n")
    printer.text("Trans#: 00001234\n")
    printer.text("Cashier: John\n")
    printer.text("================================\n")

    # Items
    items = [
        ("Widget A", 2, 9.99),
        ("Gadget B", 1, 24.99),
        ("Gizmo C", 3, 4.99),
        ("Thing D", 1, 15.00),
    ]

    subtotal = 0
    for name, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        printer.text(f"{name[:16]:<16}\n")
        printer.text(f"  {qty} x ${price:>6.2f}   ${line_total:>7.2f}\n")

    printer.text("--------------------------------\n")

    # Totals
    tax_rate = 0.08
    tax = subtotal * tax_rate
    total = subtotal + tax

    printer.text(f"{'Subtotal:':<20}${subtotal:>7.2f}\n")
    printer.text(f"{'Tax (8%):':<20}${tax:>7.2f}\n")
    printer.text("================================\n")

    printer.set_emphasis(True)
    printer.set_text_size(2, 1)
    printer.text(f"{'TOTAL:':<10}${total:>7.2f}\n")
    printer.set_text_size(1, 1)
    printer.set_emphasis(False)

    printer.text("================================\n")

    # Payment info
    payment = 100.00
    change = payment - total
    printer.text(f"{'Cash:':<20}${payment:>7.2f}\n")
    printer.text(f"{'Change:':<20}${change:>7.2f}\n")
    printer.text("\n")

    # Footer
    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.text("Thank you for shopping!\n")
    printer.text("Please come again\n")
    printer.text("\n")

    # Print barcode
    printer.set_barcode_height(40)
    printer.set_barcode_text_position(Printer.BARCODE_TEXT_BELOW)
    printer.barcode("00001234", Printer.BARCODE_CODE39)

    printer.feed(3)
    printer.cut()
    printer.close()

    print("Receipt demo completed!")
    print(f"Output would be {len(connector.get_data())} bytes")


if __name__ == "__main__":
    main()
