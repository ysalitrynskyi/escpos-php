"""
DummyPrintConnector - A connector that writes to nowhere but allows data retrieval.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2024 Yevhen Salitrynskyi <https://github.com/ysalitrynskyi> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Union, List, Optional
import warnings

from escpos.connectors.print_connector import PrintConnector


class DummyConnector(PrintConnector):
    """
    Print connector that writes to nowhere, but allows the user to retrieve the
    buffered data. Used for testing.
    """

    def __init__(self):
        """Create new dummy print connector."""
        self._buffer: Optional[List[bytes]] = []
        self._read_data: bytes = b""

    def __del__(self):
        """Warn if connector was not finalized."""
        if self._buffer is not None:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def clear(self) -> None:
        """Clear the accumulated buffer."""
        self._buffer = []

    def finalize(self) -> None:
        """Finalize the connector."""
        self._buffer = None

    def get_data(self) -> bytes:
        """
        Get the accumulated data that has been sent to this buffer.

        Returns:
            All data written to this connector as bytes.
        """
        if self._buffer is None:
            return b""
        return b"".join(self._buffer)

    def set_read_data(self, data: bytes) -> None:
        """
        Set the data that will be returned on the next read.

        Args:
            data: Data to return on read.
        """
        self._read_data = data

    def read(self, length: int) -> bytes:
        """
        Read data from the dummy buffer.

        Args:
            length: Number of bytes to read.

        Returns:
            The read data (from set_read_data).
        """
        if length >= len(self._read_data):
            return self._read_data
        return self._read_data[:length]

    def write(self, data: bytes) -> None:
        """
        Write data to the buffer.

        Args:
            data: Data to write.
        """
        if self._buffer is not None:
            self._buffer.append(data)
