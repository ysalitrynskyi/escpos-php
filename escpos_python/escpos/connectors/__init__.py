"""
Print connectors for escpos-python.

Connectors are responsible for transporting print data to the actual printer.
"""

from escpos.connectors.print_connector import PrintConnector
from escpos.connectors.dummy_connector import DummyConnector
from escpos.connectors.file_connector import FileConnector
from escpos.connectors.network_connector import NetworkConnector
from escpos.connectors.multiple_connector import MultipleConnector
from escpos.connectors.uri_connector import UriConnector

__all__ = [
    "PrintConnector",
    "DummyConnector",
    "FileConnector",
    "NetworkConnector",
    "MultipleConnector",
    "UriConnector",
]

# Optional connectors (require additional dependencies)
try:
    from escpos.connectors.usb_connector import USBConnector
    __all__.append("USBConnector")
except ImportError:
    pass

try:
    from escpos.connectors.serial_connector import SerialConnector
    __all__.append("SerialConnector")
except ImportError:
    pass

try:
    from escpos.connectors.cups_connector import CupsConnector
    __all__.append("CupsConnector")
except ImportError:
    pass

try:
    from escpos.connectors.windows_connector import WindowsConnector
    __all__.append("WindowsConnector")
except ImportError:
    pass
