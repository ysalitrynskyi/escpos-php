"""
UriPrintConnector - A factory for creating connectors from URI strings.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from urllib.parse import urlparse, parse_qs
from typing import Optional

from escpos_printer.connectors.print_connector import PrintConnector
from escpos_printer.connectors.file_connector import FileConnector
from escpos_printer.connectors.network_connector import NetworkConnector


class UriConnector:
    """
    Factory class for creating PrintConnector instances from URI strings.

    Supported URI schemes:
    - file:///path/to/device
    - tcp://hostname:port
    - usb://vendor_id:product_id
    - serial:///dev/ttyUSB0?baudrate=9600
    - smb://hostname/printer
    - cups://printer_name
    """

    @staticmethod
    def get(uri: str) -> PrintConnector:
        """
        Create a PrintConnector from a URI string.

        Args:
            uri: URI string specifying the connection type and parameters.

        Returns:
            A PrintConnector instance.

        Raises:
            ValueError: If the URI scheme is not supported.
            IOError: If the connection cannot be established.
        """
        parsed = urlparse(uri)
        scheme = parsed.scheme.lower()

        if scheme == 'file':
            # file:///path/to/device
            path = parsed.path
            if not path:
                raise ValueError("File URI must include a path")
            return FileConnector(path)

        elif scheme == 'tcp':
            # tcp://hostname:port
            hostname = parsed.hostname
            port = parsed.port or NetworkConnector.DEFAULT_PORT
            if not hostname:
                raise ValueError("TCP URI must include a hostname")
            return NetworkConnector(hostname, port)

        elif scheme == 'usb':
            # usb://vendor_id:product_id?interface=0&in_ep=0x82&out_ep=0x01
            try:
                from escpos_printer.connectors.usb_connector import USBConnector
            except ImportError:
                raise ImportError("pyusb is required for USB support")

            # Parse vendor:product from hostname
            parts = parsed.netloc.split(':')
            if len(parts) != 2:
                raise ValueError("USB URI must be in format usb://vendor_id:product_id")

            vendor_id = int(parts[0], 16) if parts[0].startswith('0x') else int(parts[0])
            product_id = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])

            # Parse optional parameters
            params = parse_qs(parsed.query)
            interface = int(params.get('interface', [0])[0])
            in_ep = int(params.get('in_ep', ['0x82'])[0], 16) if 'in_ep' in params else 0x82
            out_ep = int(params.get('out_ep', ['0x01'])[0], 16) if 'out_ep' in params else 0x01

            return USBConnector(vendor_id, product_id, interface, in_ep, out_ep)

        elif scheme == 'serial':
            # serial:///dev/ttyUSB0?baudrate=9600
            try:
                from escpos_printer.connectors.serial_connector import SerialConnector
            except ImportError:
                raise ImportError("pyserial is required for serial support")

            port = parsed.path
            if not port:
                raise ValueError("Serial URI must include a port path")

            params = parse_qs(parsed.query)
            baudrate = int(params.get('baudrate', [9600])[0])
            bytesize = int(params.get('bytesize', [8])[0])
            parity = params.get('parity', ['N'])[0]
            stopbits = int(params.get('stopbits', [1])[0])

            return SerialConnector(port, baudrate, bytesize, parity, stopbits)

        elif scheme == 'smb':
            # smb://hostname/printer
            try:
                from escpos_printer.connectors.windows_connector import WindowsConnector
            except ImportError:
                raise ImportError("Windows connector not available")

            return WindowsConnector(uri)

        elif scheme == 'cups':
            # cups://printer_name
            try:
                from escpos_printer.connectors.cups_connector import CupsConnector
            except ImportError:
                raise ImportError("pycups is required for CUPS support")

            printer_name = parsed.netloc or parsed.path.lstrip('/')
            if not printer_name:
                raise ValueError("CUPS URI must include a printer name")
            return CupsConnector(printer_name)

        else:
            raise ValueError(f"Unsupported URI scheme: {scheme}")
