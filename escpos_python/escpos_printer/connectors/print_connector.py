"""
PrintConnector abstract base class.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from abc import ABC, abstractmethod
from typing import Union
import warnings


class PrintConnector(ABC):
    """
    Abstract base class for print connectors.

    Print connectors are responsible for transporting print data to the actual printer.
    """

    def __del__(self):
        """
        Destructor - warn if connector was not finalized.
        """
        # Subclasses should check if they have unflushed data
        pass

    @abstractmethod
    def finalize(self) -> None:
        """
        Finish using this print connector.

        Close file, socket, send accumulated output, etc.
        """
        pass

    @abstractmethod
    def read(self, length: int) -> Union[bytes, bool]:
        """
        Read data from the printer.

        Args:
            length: Number of bytes to read.

        Returns:
            Data read from the printer, or False where reading is not possible.
        """
        pass

    @abstractmethod
    def write(self, data: bytes) -> None:
        """
        Write data to the print connector.

        Args:
            data: The data to write (bytes).
        """
        pass
