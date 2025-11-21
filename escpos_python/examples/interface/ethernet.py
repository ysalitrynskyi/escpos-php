#!/usr/bin/env python3
"""
Ethernet/network printer connection example.

This example shows how to connect to a network printer.
"""

from escpos import Printer
from escpos.connectors import NetworkConnector


def main():
    """Connect to and print on a network printer."""
    # Network printers typically use port 9100
    # Change the IP address to match your printer
    ip_address = "192.168.1.100"
    port = 9100

    print(f"Connecting to {ip_address}:{port}...")

    try:
        connector = NetworkConnector(ip_address, port, timeout=5.0)
        printer = Printer(connector)

        printer.text("Network printer test\n")
        printer.text(f"Connected to {ip_address}:{port}\n")
        printer.feed(3)
        printer.cut()

        printer.close()
        print("Print job sent successfully!")

    except ConnectionError as e:
        print(f"Failed to connect: {e}")
        print("Make sure the printer is powered on and connected to the network.")


if __name__ == "__main__":
    main()
