"""
RawbtPrintConnector - A connector for Android RawBT app.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

from typing import Optional, List
import base64
import warnings

from escpos.connectors.print_connector import PrintConnector


class RawbtConnector(PrintConnector):
    """
    Print connector for Android RawBT app output.

    This connector accumulates data and can output it as a data URI
    or base64 string for use with the RawBT Android app.
    """

    def __init__(self):
        """Create new RawBT print connector."""
        self._buffer: Optional[List[bytes]] = []

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_buffer') and self._buffer is not None:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Finalize the connector."""
        self._buffer = None

    def get_data(self) -> bytes:
        """
        Get the accumulated data.

        Returns:
            All data written to this connector as bytes.
        """
        if self._buffer is None:
            return b""
        return b"".join(self._buffer)

    def get_data_uri(self) -> str:
        """
        Get the accumulated data as a data URI for RawBT.

        Returns:
            Data URI string that can be opened with RawBT.
        """
        data = self.get_data()
        encoded = base64.b64encode(data).decode('ascii')
        return f"rawbt:base64,{encoded}"

    def read(self, length: int) -> bytes:
        """
        Read data (returns empty bytes).

        Args:
            length: Number of bytes to read.

        Returns:
            Empty bytes.
        """
        return b""

    def write(self, data: bytes) -> None:
        """
        Write data to the buffer.

        Args:
            data: Data to write.
        """
        if self._buffer is not None:
            self._buffer.append(data)
