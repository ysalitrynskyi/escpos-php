#!/usr/bin/env python3
"""
USB printer connection example using pyusb.

This example shows how to connect to a USB printer using pyusb.
"""

from escpos import Printer

try:
    from escpos.connectors import USBConnector
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False


def main():
    """Connect to and print on a USB printer using pyusb."""
    if not USB_AVAILABLE:
        print("pyusb is not installed!")
        print("Install with: pip install pyusb")
        return

    # USB Vendor ID and Product ID
    # You can find these using 'lsusb' on Linux or device manager on Windows
    # Common examples:
    # Epson TM-T88V: 0x04b8, 0x0202
    # Epson TM-T20II: 0x04b8, 0x0e15
    vendor_id = 0x04b8
    product_id = 0x0202

    print(f"Looking for USB device {vendor_id:04x}:{product_id:04x}...")

    try:
        connector = USBConnector(
            vendor_id=vendor_id,
            product_id=product_id
        )
        printer = Printer(connector)

        printer.text("USB printer test (pyusb)\n")
        printer.text(f"VID: 0x{vendor_id:04x}\n")
        printer.text(f"PID: 0x{product_id:04x}\n")
        printer.feed(3)
        printer.cut()

        printer.close()
        print("Print job sent successfully!")

    except IOError as e:
        print(f"Failed to connect: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the printer is connected and powered on")
        print("2. Check the Vendor ID and Product ID are correct")
        print("3. On Linux, you may need to set up udev rules or run as root")
        print("4. On Windows, you may need to install a libusb driver")


if __name__ == "__main__":
    main()
