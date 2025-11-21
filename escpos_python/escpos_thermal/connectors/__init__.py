"""
Print connectors for escpos-thermal.

Connectors are responsible for transporting print data to the actual printer.
"""

from escpos_thermal.connectors.print_connector import PrintConnector
from escpos_thermal.connectors.dummy_connector import DummyConnector
from escpos_thermal.connectors.file_connector import FileConnector
from escpos_thermal.connectors.network_connector import NetworkConnector
from escpos_thermal.connectors.multiple_connector import MultipleConnector
from escpos_thermal.connectors.uri_connector import UriConnector
from escpos_thermal.connectors.async_network_connector import AsyncNetworkConnector

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
    from escpos_thermal.connectors.usb_connector import USBConnector
    __all__.append("USBConnector")
except ImportError:
    pass

try:
    from escpos_thermal.connectors.serial_connector import SerialConnector
    __all__.append("SerialConnector")
except ImportError:
    pass

try:
    from escpos_thermal.connectors.cups_connector import CupsConnector
    __all__.append("CupsConnector")
except ImportError:
    pass

try:
    from escpos_thermal.connectors.windows_connector import WindowsConnector
    __all__.append("WindowsConnector")
except ImportError:
    pass
