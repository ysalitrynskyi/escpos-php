"""
WindowsPrintConnector - A connector for Windows printers.

This file is part of escpos-thermal: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

import sys
from typing import Optional, Union, List
import warnings

# Windows-specific imports
if sys.platform == 'win32':
    try:
        import win32print
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

from escpos_thermal.connectors.print_connector import PrintConnector


class WindowsConnector(PrintConnector):
    """
    PrintConnector for Windows printers using win32print.

    Supports:
    - Local ports (LPT1, COM1, etc.)
    - Shared printers (\\\\hostname\\printer)
    - SMB printers (smb://hostname/printer)
    """

    def __init__(self, destination: str):
        """
        Construct a new WindowsConnector.

        Args:
            destination: Printer name or path. Can be:
                - A local port (e.g., 'LPT1', 'COM1')
                - A shared printer (e.g., '\\\\hostname\\printer')
                - An SMB path (e.g., 'smb://hostname/printer')

        Raises:
            ImportError: If win32print is not installed or not on Windows.
            IOError: If the printer cannot be opened.
        """
        if not WIN32_AVAILABLE:
            raise ImportError(
                "win32print is required for Windows printing. "
                "Install with: pip install pywin32"
            )

        self._buffer: List[bytes] = []
        self._destination = self._parse_destination(destination)
        self._handle = None

        # For local ports, open directly
        if self._is_local_port(self._destination):
            try:
                self._fp = open(self._destination, 'wb')
                self._use_file = True
            except IOError as e:
                raise IOError(f"Cannot open port {self._destination}: {e}")
        else:
            self._use_file = False
            # Will use win32print for network/shared printers

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_buffer') and self._buffer is not None:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def _parse_destination(self, dest: str) -> str:
        """
        Parse and normalize the destination string.

        Args:
            dest: Original destination string.

        Returns:
            Normalized destination string.
        """
        # Handle SMB URLs
        if dest.lower().startswith('smb://'):
            # Convert smb://hostname/printer to \\hostname\printer
            path = dest[6:]  # Remove 'smb://'
            return '\\\\' + path.replace('/', '\\')
        return dest

    def _is_local_port(self, dest: str) -> bool:
        """
        Check if destination is a local port.

        Args:
            dest: Destination string.

        Returns:
            True if local port, False otherwise.
        """
        local_ports = ['LPT', 'COM', 'USB', 'PRN']
        upper = dest.upper()
        return any(upper.startswith(port) for port in local_ports)

    def finalize(self) -> None:
        """Send accumulated data to printer and clean up."""
        if self._buffer is not None and len(self._buffer) > 0:
            data = b"".join(self._buffer)

            if self._use_file:
                self._fp.write(data)
                self._fp.close()
            else:
                # Use win32print for network printers
                try:
                    handle = win32print.OpenPrinter(self._destination)
                    try:
                        job = win32print.StartDocPrinter(handle, 1, ("ESC/POS Print Job", None, "RAW"))
                        try:
                            win32print.StartPagePrinter(handle)
                            win32print.WritePrinter(handle, data)
                            win32print.EndPagePrinter(handle)
                        finally:
                            win32print.EndDocPrinter(handle)
                    finally:
                        win32print.ClosePrinter(handle)
                except Exception as e:
                    raise IOError(f"Failed to print: {e}")

        self._buffer = None

    def read(self, length: int) -> bool:
        """
        Read is not supported on Windows connector.

        Args:
            length: Number of bytes to read.

        Returns:
            False (reading not supported).
        """
        return False

    def write(self, data: bytes) -> None:
        """
        Buffer data for later printing.

        Args:
            data: Data to write.
        """
        if self._buffer is not None:
            self._buffer.append(data)
