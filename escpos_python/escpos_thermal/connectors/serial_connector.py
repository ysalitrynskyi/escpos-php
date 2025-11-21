"""
SerialPrintConnector - A connector for serial printers using pyserial.

This file is part of escpos-thermal: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Optional, Union
import warnings

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

from escpos_thermal.connectors.print_connector import PrintConnector


class SerialConnector(PrintConnector):
    """
    PrintConnector for serial printers using pyserial.
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = 'N',
        stopbits: int = 1,
        timeout: Optional[float] = None,
        xonxoff: bool = False,
        rtscts: bool = False,
        dsrdtr: bool = True
    ):
        """
        Construct a new SerialConnector.

        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM1').
            baudrate: Baud rate (default 9600).
            bytesize: Number of data bits (default 8).
            parity: Parity checking ('N', 'E', 'O', 'M', 'S').
            stopbits: Number of stop bits (1, 1.5, 2).
            timeout: Read timeout in seconds (None for blocking).
            xonxoff: Enable software flow control.
            rtscts: Enable hardware (RTS/CTS) flow control.
            dsrdtr: Enable hardware (DSR/DTR) flow control.

        Raises:
            ImportError: If pyserial is not installed.
            IOError: If the port cannot be opened.
        """
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial is required for serial support. Install with: pip install pyserial")

        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
                xonxoff=xonxoff,
                rtscts=rtscts,
                dsrdtr=dsrdtr
            )
        except serial.SerialException as e:
            raise IOError(f"Cannot initialise SerialConnector: {e}")

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_serial') and self._serial is not None and self._serial.is_open:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Close the serial port."""
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def read(self, length: int) -> bytes:
        """
        Read data from the serial port.

        Args:
            length: Number of bytes to read.

        Returns:
            Data read from the port.

        Raises:
            IOError: If the connector has been closed.
        """
        if self._serial is None or not self._serial.is_open:
            raise IOError("PrintConnector has been closed, cannot read input.")
        return self._serial.read(length)

    def write(self, data: bytes) -> None:
        """
        Write data to the serial port.

        Args:
            data: Data to write.

        Raises:
            IOError: If the connector has been closed.
        """
        if self._serial is None or not self._serial.is_open:
            raise IOError("PrintConnector has been closed, cannot send output.")
        self._serial.write(data)
