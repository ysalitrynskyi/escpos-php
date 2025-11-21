"""
AuresCustomerDisplay - Specialized printer for Aures customer display.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

from typing import Optional

from escpos.printer import Printer
from escpos.capability_profile import CapabilityProfile
from escpos.connectors.print_connector import PrintConnector


class AuresCustomerDisplay(Printer):
    """
    Extension of Printer class for Aures customer display devices.

    Provides additional functionality specific to customer displays.
    """

    # Text scroll modes
    TEXT_OVERWRITE = 1
    TEXT_VERTICAL_SCROLL = 2
    TEXT_HORIZONTAL_SCROLL = 3

    def __init__(
        self,
        connector: PrintConnector,
        profile: Optional[CapabilityProfile] = None
    ):
        """
        Construct a new AuresCustomerDisplay.

        Args:
            connector: The PrintConnector to send data to.
            profile: Supported features of this printer.
        """
        super().__init__(connector, profile)

    def initialize(self) -> None:
        """
        Initialize the customer display.

        This resets formatting back to the defaults.
        """
        # Standard initialization
        self._connector.write(self.ESC + b"@")
        self._character_table = 0

        # Clear display
        self._connector.write(self.ESC + b"[2J")

    def select_text_scroll_mode(self, mode: int = TEXT_VERTICAL_SCROLL) -> None:
        """
        Select the text scroll mode for the display.

        Args:
            mode: One of TEXT_OVERWRITE, TEXT_VERTICAL_SCROLL, or TEXT_HORIZONTAL_SCROLL.
        """
        self._validate_integer(mode, 1, 3, "select_text_scroll_mode")
        self._connector.write(self.ESC + b"[" + str(mode).encode() + b"s")

    def move_cursor(self, row: int, column: int) -> None:
        """
        Move the cursor to a specific position.

        Args:
            row: Row number (1-based).
            column: Column number (1-based).
        """
        self._validate_integer(row, 1, 255, "move_cursor", "row")
        self._validate_integer(column, 1, 255, "move_cursor", "column")
        self._connector.write(self.ESC + b"[" + f"{row};{column}H".encode())

    def clear_display(self) -> None:
        """
        Clear the entire display.
        """
        self._connector.write(self.ESC + b"[2J")

    def clear_line(self) -> None:
        """
        Clear the current line.
        """
        self._connector.write(self.ESC + b"[2K")

    def set_brightness(self, level: int) -> None:
        """
        Set the display brightness.

        Args:
            level: Brightness level (1-4, where 1 is dimmest).
        """
        self._validate_integer(level, 1, 4, "set_brightness", "level")
        self._connector.write(self.ESC + b"[" + str(level).encode() + b"q")
