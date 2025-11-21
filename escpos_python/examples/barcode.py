#!/usr/bin/env python3
"""
Barcode printing example for escpos-thermal.

This example demonstrates printing various barcode types.
"""

from escpos_thermal import Printer
from escpos_thermal.connectors import DummyConnector


def main():
    """Run the barcode demo."""
    connector = DummyConnector()
    printer = Printer(connector)

    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.text("Barcode Examples\n")
    printer.text("================\n\n")

    # CODE39 barcode
    printer.text("CODE39:\n")
    printer.set_barcode_height(50)
    printer.set_barcode_width(2)
    printer.set_barcode_text_position(Printer.BARCODE_TEXT_BELOW)
    printer.barcode("ABC123", Printer.BARCODE_CODE39)
    printer.feed(2)

    # UPC-A barcode
    printer.text("UPC-A:\n")
    printer.barcode("12345678901", Printer.BARCODE_UPCA)
    printer.feed(2)

    # JAN13 (EAN13) barcode
    printer.text("JAN13 (EAN13):\n")
    printer.barcode("123456789012", Printer.BARCODE_JAN13)
    printer.feed(2)

    # JAN8 (EAN8) barcode
    printer.text("JAN8 (EAN8):\n")
    printer.barcode("1234567", Printer.BARCODE_JAN8)
    printer.feed(2)

    # ITF barcode
    printer.text("ITF:\n")
    printer.barcode("1234567890", Printer.BARCODE_ITF)
    printer.feed(2)

    # Codabar
    printer.text("CODABAR:\n")
    printer.barcode("A12345B", Printer.BARCODE_CODABAR)
    printer.feed(2)

    # No text position
    printer.text("Without HRI text:\n")
    printer.set_barcode_text_position(Printer.BARCODE_TEXT_NONE)
    printer.barcode("ABC123", Printer.BARCODE_CODE39)
    printer.feed(3)

    printer.cut()
    printer.close()

    print("Barcode demo completed!")
    print(f"Output would be {len(connector.get_data())} bytes")


if __name__ == "__main__":
    main()
