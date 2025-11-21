"""
MultiplePrintConnector - A connector that broadcasts to multiple printers.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import List, Union
import warnings

from escpos.connectors.print_connector import PrintConnector


class MultipleConnector(PrintConnector):
    """
    Print connector that broadcasts output to multiple printers.
    """

    def __init__(self, *connectors: PrintConnector):
        """
        Create new multiple print connector.

        Args:
            *connectors: Variable number of PrintConnector instances to broadcast to.
        """
        self._connectors: List[PrintConnector] = list(connectors)

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_connectors') and self._connectors:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Finalize all connected connectors."""
        for connector in self._connectors:
            connector.finalize()
        self._connectors = []

    def read(self, length: int) -> bool:
        """
        Read is not supported on multiple connector.

        Args:
            length: Number of bytes to read.

        Returns:
            False (reading not supported).
        """
        return False

    def write(self, data: bytes) -> None:
        """
        Write data to all connected printers.

        Args:
            data: Data to write.
        """
        for connector in self._connectors:
            connector.write(data)
