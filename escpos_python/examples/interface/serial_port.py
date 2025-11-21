#!/usr/bin/env python3
"""
Serial port printer connection example.

This example shows how to connect to a serial port printer.
"""

from escpos_thermal import Printer

try:
    from escpos_thermal.connectors import SerialConnector
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


def main():
    """Connect to and print on a serial printer."""
    if not SERIAL_AVAILABLE:
        print("pyserial is not installed!")
        print("Install with: pip install pyserial")
        return

    # Serial printer settings - adjust these for your printer
    port = "/dev/ttyUSB0"  # Linux
    # port = "COM1"  # Windows
    baudrate = 9600
    bytesize = 8
    parity = 'N'
    stopbits = 1

    print(f"Connecting to {port} at {baudrate} baud...")

    try:
        connector = SerialConnector(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits
        )
        printer = Printer(connector)

        printer.text("Serial printer test\n")
        printer.text(f"Port: {port}\n")
        printer.text(f"Baud: {baudrate}\n")
        printer.feed(3)
        printer.cut()

        printer.close()
        print("Print job sent successfully!")

    except IOError as e:
        print(f"Failed to connect: {e}")
        print("Make sure the printer is connected and the port settings are correct.")


if __name__ == "__main__":
    main()
