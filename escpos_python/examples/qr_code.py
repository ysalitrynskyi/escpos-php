#!/usr/bin/env python3
"""
QR code printing example for escpos-printer.

This example demonstrates printing QR codes.
"""

from escpos import Printer
from escpos.connectors import DummyConnector


def main():
    """Run the QR code demo."""
    connector = DummyConnector()
    printer = Printer(connector)

    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.text("QR Code Examples\n")
    printer.text("================\n\n")

    # Basic QR code
    printer.text("Basic QR Code:\n")
    try:
        printer.qr_code("https://example.com")
    except RuntimeError as e:
        printer.text(f"(QR not supported: {e})\n")
    printer.feed(2)

    # QR code with different sizes
    printer.text("Size 5:\n")
    try:
        printer.qr_code("https://example.com", size=5)
    except RuntimeError as e:
        printer.text(f"(QR not supported: {e})\n")
    printer.feed(2)

    printer.text("Size 10:\n")
    try:
        printer.qr_code("https://example.com", size=10)
    except RuntimeError as e:
        printer.text(f"(QR not supported: {e})\n")
    printer.feed(2)

    # QR code with different error correction levels
    printer.text("High Error Correction:\n")
    try:
        printer.qr_code(
            "https://example.com",
            ec=Printer.QR_ECLEVEL_H,
            size=6
        )
    except RuntimeError as e:
        printer.text(f"(QR not supported: {e})\n")
    printer.feed(2)

    # QR code with text content
    printer.text("Text Content:\n")
    try:
        printer.qr_code("Hello, World! This is a test QR code.", size=4)
    except RuntimeError as e:
        printer.text(f"(QR not supported: {e})\n")
    printer.feed(3)

    printer.cut()
    printer.close()

    print("QR code demo completed!")
    print(f"Output would be {len(connector.get_data())} bytes")


if __name__ == "__main__":
    main()
