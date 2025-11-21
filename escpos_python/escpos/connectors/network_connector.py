"""
NetworkPrintConnector - A connector for TCP/IP network printers.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

import socket
from typing import Optional, Union
import warnings

from escpos.connectors.print_connector import PrintConnector


class NetworkConnector(PrintConnector):
    """
    PrintConnector for directly opening a network socket to a printer.
    """

    DEFAULT_PORT = 9100

    def __init__(self, ip: str, port: int = 9100, timeout: Optional[float] = None):
        """
        Construct a new NetworkPrintConnector.

        Args:
            ip: IP address or hostname to use.
            port: The port number to connect on (default 9100).
            timeout: The connection timeout in seconds. None for default.

        Raises:
            ConnectionError: If the socket cannot be opened.
        """
        self._socket: Optional[socket.socket] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if timeout is not None:
            self._socket.settimeout(timeout)

        try:
            self._socket.connect((ip, port))
        except socket.error as e:
            self._socket = None
            raise ConnectionError(f"Cannot initialise NetworkConnector: {e}")

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_socket') and self._socket is not None:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Close the socket."""
        if self._socket is not None:
            try:
                self._socket.close()
            except socket.error:
                pass
            self._socket = None

    def read(self, length: int) -> bytes:
        """
        Read data from the socket.

        Args:
            length: Number of bytes to read.

        Returns:
            Data read from the socket.

        Raises:
            IOError: If the connector has been closed or on timeout/error.
        """
        if self._socket is None:
            raise IOError("PrintConnector has been closed, cannot read input.")
        try:
            return self._socket.recv(length)
        except socket.timeout:
            raise IOError("Socket timeout during read operation")
        except socket.error as e:
            raise IOError(f"Socket error during read: {e}")

    def write(self, data: bytes) -> None:
        """
        Write data to the socket.

        Args:
            data: Data to write.

        Raises:
            IOError: If the connector has been closed or on timeout/error.
        """
        if self._socket is None:
            raise IOError("PrintConnector has been closed, cannot send output.")
        try:
            self._socket.sendall(data)
        except socket.timeout:
            raise IOError("Socket timeout during write operation")
        except socket.error as e:
            raise IOError(f"Socket error during write: {e}")
