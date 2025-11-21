#!/usr/bin/env python3
"""
Linux USB printer connection example.

This example shows how to connect to a USB printer on Linux.
"""

import os
from escpos_printer import Printer
from escpos_printer.connectors import FileConnector


def main():
    """Connect to and print on a USB printer on Linux."""
    # USB printers on Linux are typically at /dev/usb/lp0
    # The user needs permission to access this device
    device_path = "/dev/usb/lp0"

    # Alternative paths to try
    alternative_paths = [
        "/dev/usb/lp0",
        "/dev/usb/lp1",
        "/dev/lp0",
        "/dev/lp1",
    ]

    # Find available device
    selected_path = None
    for path in alternative_paths:
        if os.path.exists(path):
            selected_path = path
            break

    if selected_path is None:
        print("No USB printer device found!")
        print("Tried: " + ", ".join(alternative_paths))
        print("\nMake sure:")
        print("1. The printer is connected and powered on")
        print("2. You have permission to access the device")
        print("   (try: sudo chmod 666 /dev/usb/lp0)")
        return

    print(f"Using device: {selected_path}")

    try:
        connector = FileConnector(selected_path)
        printer = Printer(connector)

        printer.text("USB printer test on Linux\n")
        printer.text(f"Device: {selected_path}\n")
        printer.feed(3)
        printer.cut()

        printer.close()
        print("Print job sent successfully!")

    except IOError as e:
        print(f"Failed to open device: {e}")
        print("Make sure you have permission to access the device.")


if __name__ == "__main__":
    main()
