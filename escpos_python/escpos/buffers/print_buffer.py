"""
PrintBuffer abstract base class.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from escpos.printer import Printer


class PrintBuffer(ABC):
    """
    Abstract base class for print buffers.

    Print buffers manage text output and character encoding for the printer.
    """

    @abstractmethod
    def flush(self) -> None:
        """
        Flush the buffer, indicating that the current line should be ended.
        """
        pass

    @abstractmethod
    def get_printer(self) -> Optional['Printer']:
        """
        Get the printer this buffer is attached to.

        Returns:
            The Printer instance, or None if not attached.
        """
        pass

    @abstractmethod
    def set_printer(self, printer: Optional['Printer']) -> None:
        """
        Set the printer this buffer is attached to.

        Args:
            printer: The Printer instance, or None to detach.
        """
        pass

    @abstractmethod
    def write_text(self, text: str) -> None:
        """
        Write text to the buffer with automatic character encoding.

        Args:
            text: Text to write, as UTF-8.
        """
        pass

    @abstractmethod
    def write_text_raw(self, text: str) -> None:
        """
        Write text to the buffer without character encoding translation.

        Args:
            text: Text to write.
        """
        pass
