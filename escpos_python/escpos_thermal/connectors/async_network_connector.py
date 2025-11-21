"""
AsyncNetworkConnector - An async connector for TCP/IP network printers.

This file is part of escpos-thermal: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com>

This software is distributed under the terms of the MIT license.
"""

import asyncio
from typing import Optional


class AsyncNetworkConnector:
    """
    Async PrintConnector for network printers using asyncio.

    Usage:
        async with AsyncNetworkConnector("192.168.1.100", 9100) as connector:
            await connector.write(b"Hello\\n")
    """

    DEFAULT_PORT = 9100

    def __init__(
        self,
        ip: str,
        port: int = 9100,
        timeout: Optional[float] = None
    ):
        """
        Construct a new AsyncNetworkConnector.

        Args:
            ip: IP address or hostname to use.
            port: The port number to connect on (default 9100).
            timeout: Connection timeout in seconds.
        """
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None

    async def connect(self) -> None:
        """
        Open the connection to the printer.

        Raises:
            ConnectionError: If the connection cannot be established.
        """
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._ip, self._port),
                timeout=self._timeout
            )
        except asyncio.TimeoutError:
            raise ConnectionError(f"Timeout connecting to {self._ip}:{self._port}")
        except OSError as e:
            raise ConnectionError(f"Cannot connect to {self._ip}:{self._port}: {e}")

    async def __aenter__(self) -> 'AsyncNetworkConnector':
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.finalize()

    async def finalize(self) -> None:
        """Close the connection."""
        if self._writer is not None:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

    async def write(self, data: bytes) -> None:
        """
        Write data to the printer.

        Args:
            data: Data to write.

        Raises:
            IOError: If the connection is closed or on error.
        """
        if self._writer is None:
            raise IOError("Connection is not open. Call connect() first.")

        try:
            self._writer.write(data)
            await self._writer.drain()
        except asyncio.TimeoutError:
            raise IOError("Timeout during write operation")
        except OSError as e:
            raise IOError(f"Error during write: {e}")

    async def read(self, length: int) -> bytes:
        """
        Read data from the printer.

        Args:
            length: Number of bytes to read.

        Returns:
            Data read from the printer.

        Raises:
            IOError: If the connection is closed or on error.
        """
        if self._reader is None:
            raise IOError("Connection is not open. Call connect() first.")

        try:
            if self._timeout:
                return await asyncio.wait_for(
                    self._reader.read(length),
                    timeout=self._timeout
                )
            else:
                return await self._reader.read(length)
        except asyncio.TimeoutError:
            raise IOError("Timeout during read operation")
        except OSError as e:
            raise IOError(f"Error during read: {e}")

    @property
    def is_connected(self) -> bool:
        """Check if the connection is open."""
        return self._writer is not None and not self._writer.is_closing()
