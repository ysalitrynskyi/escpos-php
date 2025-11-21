"""
USBPrintConnector - A connector for USB printers using pyusb.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Optional, Union
import warnings

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

from escpos.connectors.print_connector import PrintConnector


class USBConnector(PrintConnector):
    """
    PrintConnector for USB printers using pyusb.
    """

    def __init__(
        self,
        vendor_id: int,
        product_id: int,
        interface: int = 0,
        in_ep: int = 0x82,
        out_ep: int = 0x01,
        timeout: int = 0
    ):
        """
        Construct a new USBConnector.

        Args:
            vendor_id: USB vendor ID.
            product_id: USB product ID.
            interface: USB interface to use (default 0).
            in_ep: Input endpoint address (default 0x82).
            out_ep: Output endpoint address (default 0x01).
            timeout: Timeout in milliseconds (default 0 for unlimited).

        Raises:
            ImportError: If pyusb is not installed.
            IOError: If the device cannot be found or opened.
        """
        if not USB_AVAILABLE:
            raise ImportError("pyusb is required for USB support. Install with: pip install pyusb")

        self._device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if self._device is None:
            raise IOError(f"USB device {vendor_id:04x}:{product_id:04x} not found")

        self._interface = interface
        self._in_ep = in_ep
        self._out_ep = out_ep
        self._timeout = timeout

        # Detach kernel driver if active
        try:
            if self._device.is_kernel_driver_active(interface):
                self._device.detach_kernel_driver(interface)
        except (usb.core.USBError, NotImplementedError):
            pass

        # Set configuration
        try:
            self._device.set_configuration()
        except usb.core.USBError:
            pass

        # Claim interface
        try:
            usb.util.claim_interface(self._device, interface)
        except usb.core.USBError as e:
            raise IOError(f"Cannot claim USB interface: {e}")

    def __del__(self):
        """Warn if connector was not finalized."""
        if hasattr(self, '_device') and self._device is not None:
            warnings.warn(
                "Print connector was not finalized. Did you forget to close the printer?",
                UserWarning
            )

    def finalize(self) -> None:
        """Release USB interface and resources."""
        if self._device is not None:
            try:
                usb.util.release_interface(self._device, self._interface)
            except (usb.core.USBError, ValueError):
                pass
            try:
                usb.util.dispose_resources(self._device)
            except (usb.core.USBError, ValueError):
                pass
            self._device = None

    def read(self, length: int) -> bytes:
        """
        Read data from the USB device.

        Args:
            length: Number of bytes to read.

        Returns:
            Data read from the device.

        Raises:
            IOError: If the connector has been closed.
        """
        if self._device is None:
            raise IOError("PrintConnector has been closed, cannot read input.")
        try:
            data = self._device.read(self._in_ep, length, timeout=self._timeout)
            return bytes(data)
        except usb.core.USBError as e:
            if e.errno == 110:  # Timeout
                return b""
            raise IOError(f"USB read error: {e}")

    def write(self, data: bytes) -> None:
        """
        Write data to the USB device.

        Args:
            data: Data to write.

        Raises:
            IOError: If the connector has been closed.
        """
        if self._device is None:
            raise IOError("PrintConnector has been closed, cannot send output.")
        try:
            self._device.write(self._out_ep, data, timeout=self._timeout)
        except usb.core.USBError as e:
            raise IOError(f"USB write error: {e}")
