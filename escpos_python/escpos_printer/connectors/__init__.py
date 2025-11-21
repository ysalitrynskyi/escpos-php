"""
Print connectors for escpos-printer.

Connectors are responsible for transporting print data to the actual printer.
"""

from escpos_printer.connectors.print_connector import PrintConnector
from escpos_printer.connectors.dummy_connector import DummyConnector
from escpos_printer.connectors.file_connector import FileConnector
from escpos_printer.connectors.network_connector import NetworkConnector
from escpos_printer.connectors.multiple_connector import MultipleConnector
from escpos_printer.connectors.uri_connector import UriConnector
from escpos_printer.connectors.async_network_connector import AsyncNetworkConnector

__all__ = [
    "PrintConnector",
    "DummyConnector",
    "FileConnector",
    "NetworkConnector",
    "AsyncNetworkConnector",
    "MultipleConnector",
    "UriConnector",
]

# Optional connectors (require additional dependencies)
try:
    from escpos_printer.connectors.usb_connector import USBConnector
    __all__.append("USBConnector")
except ImportError:
    pass

try:
    from escpos_printer.connectors.serial_connector import SerialConnector
    __all__.append("SerialConnector")
except ImportError:
    pass

try:
    from escpos_printer.connectors.cups_connector import CupsConnector
    __all__.append("CupsConnector")
except ImportError:
    pass

try:
    from escpos_printer.connectors.windows_connector import WindowsConnector
    __all__.append("WindowsConnector")
except ImportError:
    pass
