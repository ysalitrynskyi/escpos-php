"""
FilePrintConnector - A connector for writing to files or device paths.

This file is part of escpos-thermal: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Union, Optional, BinaryIO
import warnings

from escpos_thermal.connectors.print_connector import PrintConnector


class FileConnector(PrintConnector):
    """
    PrintConnector for passing print data to a file or device.
    """

    def __init__(self, filename: str):
        """
        Construct new connector, given a filename.

        Args:
            filename: Path to the file or device to write to.

        Raises:
            IOError: If the file cannot be opened.
        """
        self._fp: Optional[BinaryIO] = open(filename, "wb+")
        if self._fp is None:
            raise IOError("Cannot initialise FileConnector.")

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_fp') and self._fp is not None and not self._fp.closed:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Close file pointer."""
        if self._fp is not None and not self._fp.closed:
            self._fp.close()
        self._fp = None

    def read(self, length: int) -> bytes:
        """
        Read data from the file.

        Args:
            length: Number of bytes to read.

        Returns:
            Data read from the file.

        Raises:
            IOError: If the connector has been closed.
        """
        if self._fp is None or self._fp.closed:
            raise IOError("PrintConnector has been closed, cannot read input.")
        return self._fp.read(length)

    def write(self, data: bytes) -> None:
        """
        Write data to the file.

        Args:
            data: Data to write.

        Raises:
            IOError: If the connector has been closed.
        """
        if self._fp is None or self._fp.closed:
            raise IOError("PrintConnector has been closed, cannot send output.")
        self._fp.write(data)
