#!/usr/bin/env python3
"""
Basic demo of escpos-thermal functionality.

This example demonstrates basic text formatting and printing.
"""

from escpos_thermal import Printer
from escpos_thermal.connectors import DummyConnector, NetworkConnector, FileConnector


def main():
    """Run the demo."""
    # Use DummyConnector for demonstration (captures output instead of printing)
    # For a real printer, use:
    # connector = NetworkConnector("192.168.1.100", 9100)  # Network printer
    # connector = FileConnector("/dev/usb/lp0")  # USB printer on Linux
    connector = DummyConnector()
    printer = Printer(connector)

    # Print a receipt header
    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.set_text_size(2, 2)
    printer.text("RECEIPT\n")
    printer.set_text_size(1, 1)
    printer.text("Store Name\n")
    printer.text("123 Main Street\n")
    printer.text("City, State 12345\n")
    printer.text("\n")

    # Print items
    printer.set_justification(Printer.JUSTIFY_LEFT)
    printer.text("Item 1          $10.00\n")
    printer.text("Item 2          $15.00\n")
    printer.text("Item 3           $5.00\n")
    printer.text("------------------------\n")

    # Print total
    printer.set_emphasis(True)
    printer.text("TOTAL           $30.00\n")
    printer.set_emphasis(False)
    printer.text("\n")

    # Print footer
    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.text("Thank you for shopping!\n")
    printer.text("Please come again\n")
    printer.feed(3)

    # Cut paper (if supported)
    printer.cut()

    # For DummyConnector, we can see what would have been sent (before close)
    output_size = len(connector.get_data())

    # Close the connection
    printer.close()

    print("Demo completed!")
    print(f"Output would be {output_size} bytes")


if __name__ == "__main__":
    main()
