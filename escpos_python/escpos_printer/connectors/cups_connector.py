"""
CupsPrintConnector - A connector for CUPS printing system.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Optional, Union, List
import tempfile
import os
import warnings

try:
    import cups
    CUPS_AVAILABLE = True
except ImportError:
    CUPS_AVAILABLE = False

from escpos_printer.connectors.print_connector import PrintConnector


class CupsConnector(PrintConnector):
    """
    PrintConnector for CUPS printing system.
    """

    def __init__(self, printer_name: str):
        """
        Construct a new CupsConnector.

        Args:
            printer_name: The name of the CUPS printer.

        Raises:
            ImportError: If pycups is not installed.
            IOError: If the printer cannot be found.
        """
        if not CUPS_AVAILABLE:
            raise ImportError("pycups is required for CUPS support. Install with: pip install pycups")

        self._conn = cups.Connection()
        printers = self._conn.getPrinters()

        if printer_name not in printers:
            raise IOError(f"CUPS printer '{printer_name}' not found. Available: {list(printers.keys())}")

        self._printer_name = printer_name
        self._buffer: List[bytes] = []

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_buffer') and self._buffer is not None:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Send accumulated data to CUPS and clean up."""
        if self._buffer is not None and len(self._buffer) > 0:
            # Create temporary file with print data
            fd, temp_path = tempfile.mkstemp(suffix='.bin')
            try:
                with os.fdopen(fd, 'wb') as f:
                    f.write(b"".join(self._buffer))

                # Submit print job
                self._conn.printFile(
                    self._printer_name,
                    temp_path,
                    "ESC/POS Print Job",
                    {"raw": "true"}
                )
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        self._buffer = None

    def read(self, length: int) -> bool:
        """
        Read is not supported on CUPS connector.

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
