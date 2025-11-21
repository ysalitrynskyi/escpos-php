# escpos-python

Python library for ESC/POS-compatible thermal and impact receipt printers.

This is a Python port of the [escpos-php](https://github.com/mike42/escpos-php) library.

## Installation

```bash
pip install escpos-python
```

For additional features:

```bash
# USB support
pip install escpos-python[usb]

# Serial support
pip install escpos-python[serial]

# All optional dependencies
pip install escpos-python[all]
```

## Quick Start

```python
from escpos import Printer
from escpos.connectors import NetworkConnector

# Connect to a network printer
connector = NetworkConnector("192.168.1.100", 9100)
printer = Printer(connector)

# Print a receipt
printer.set_justification(Printer.JUSTIFY_CENTER)
printer.text("My Store\n")
printer.set_justification(Printer.JUSTIFY_LEFT)
printer.text("Item 1          $10.00\n")
printer.text("Item 2          $15.00\n")
printer.text("------------------------\n")
printer.text("Total           $25.00\n")
printer.feed(3)
printer.cut()
printer.close()
```

## Supported Connectors

- **FileConnector** - Print to a file or device path
- **NetworkConnector** - TCP/IP network printers (default port 9100)
- **USBConnector** - USB printers via pyusb
- **SerialConnector** - Serial printers via pyserial
- **CupsConnector** - CUPS printing system
- **DummyConnector** - For testing (captures output)

## Features

- Text printing with various fonts and styles
- Barcode printing (UPC-A, UPC-E, JAN13, JAN8, CODE39, ITF, CODABAR, CODE93, CODE128)
- QR code printing
- PDF417 code printing
- Image/graphics printing
- Cash drawer control
- Paper cutting
- Character encoding support (80+ code pages)

## License

MIT License - see LICENSE.md for details.
