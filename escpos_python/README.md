# escpos-python

A Python 3 library for ESC/POS-compatible thermal and impact receipt printers.

## About

This is a complete Python 3 port of the [escpos-php](https://github.com/mike42/escpos-php) library by Michael Billington.

**Ported by:** [Yevhen Salitrynskyi](https://github.com/ysalitrynskyi)

The library provides a 1:1 feature-complete implementation of the original PHP library, allowing you to control ESC/POS thermal printers from Python applications.

## Features

- **Text printing** with various fonts, sizes, and styles (bold, underline, double-strike)
- **Barcode printing** - UPC-A, UPC-E, EAN-13, EAN-8, CODE39, ITF, CODABAR, CODE93, CODE128
- **QR code printing** with configurable error correction levels
- **PDF417 2D barcode** support
- **Image/graphics printing** via Pillow
- **Cash drawer control** (pulse commands)
- **Paper cutting** (full and partial cut)
- **Character encoding** support (80+ code pages)
- **Multiple connection types** - Network, USB, Serial, File, CUPS

## Requirements

- Python 3.8+
- Pillow (for image processing)

Optional dependencies:
- `pyusb` - for USB printer support
- `pyserial` - for serial port printer support
- `qrcode` - for QR code generation
- `python-barcode` - for barcode generation

## Installation

### From source (development)

```bash
git clone https://github.com/ysalitrynskyi/escpos-php.git
cd escpos-php/escpos_python
pip install -e .
```

### Install with optional dependencies

```bash
# USB support
pip install -e ".[usb]"

# Serial support
pip install -e ".[serial]"

# All optional dependencies
pip install -e ".[all]"
```

### Install dependencies manually

```bash
pip install -r requirements.txt
```

## Quick Start

### Network Printer (TCP/IP)

```python
from escpos import Printer
from escpos.connectors import NetworkConnector

# Connect to printer at IP address, port 9100 (default)
connector = NetworkConnector("192.168.1.100", 9100)
printer = Printer(connector)

# Print a simple receipt
printer.initialize()
printer.set_justification(Printer.JUSTIFY_CENTER)
printer.text("MY STORE\n")
printer.text("123 Main Street\n\n")

printer.set_justification(Printer.JUSTIFY_LEFT)
printer.text("Item 1              $10.00\n")
printer.text("Item 2              $15.00\n")
printer.text("Item 3               $5.00\n")
printer.text("--------------------------------\n")
printer.set_emphasis(True)
printer.text("TOTAL               $30.00\n")
printer.set_emphasis(False)

printer.feed(3)
printer.cut()
printer.close()
```

### USB Printer (via pyusb)

```python
from escpos import Printer
from escpos.connectors import USBConnector

# Find your printer's vendor ID and product ID using `lsusb`
connector = USBConnector(0x04b8, 0x0202)  # Example: Epson TM-T88
printer = Printer(connector)

printer.text("Hello from USB!\n")
printer.cut()
printer.close()
```

### Serial Printer

```python
from escpos import Printer
from escpos.connectors import SerialConnector

connector = SerialConnector("/dev/ttyUSB0", 9600)
printer = Printer(connector)

printer.text("Hello from Serial!\n")
printer.cut()
printer.close()
```

### File/Device Printer (Linux)

```python
from escpos import Printer
from escpos.connectors import FileConnector

# Direct device access (requires permissions)
connector = FileConnector("/dev/usb/lp0")
printer = Printer(connector)

printer.text("Hello from device!\n")
printer.cut()
printer.close()
```

### Testing with DummyConnector

```python
from escpos import Printer
from escpos.connectors import DummyConnector

connector = DummyConnector()
printer = Printer(connector)

printer.text("This is a test\n")
printer.barcode("123456789012", Printer.BARCODE_UPCA)
printer.cut()

# Get the raw bytes that would be sent to printer
output = connector.get_data()
print(f"Output size: {len(output)} bytes")

printer.close()
```

## Printing Barcodes

```python
from escpos import Printer
from escpos.connectors import NetworkConnector

connector = NetworkConnector("192.168.1.100")
printer = Printer(connector)

# UPC-A barcode
printer.barcode("012345678905", Printer.BARCODE_UPCA)

# EAN-13 barcode
printer.barcode("5901234123457", Printer.BARCODE_JAN13)

# CODE128 barcode
printer.barcode("{B" + "HELLO123", Printer.BARCODE_CODE128)

printer.cut()
printer.close()
```

## Printing QR Codes

```python
from escpos import Printer
from escpos.connectors import NetworkConnector

connector = NetworkConnector("192.168.1.100")
printer = Printer(connector)

# Simple QR code
printer.qr_code("https://github.com/ysalitrynskyi")

# QR code with options
printer.qr_code(
    "https://example.com",
    ec=Printer.QR_ECLEVEL_H,  # High error correction
    size=8,                    # Module size
    model=Printer.QR_MODEL_2   # QR Model 2
)

printer.cut()
printer.close()
```

## Printing Images

```python
from escpos import Printer
from escpos.connectors import NetworkConnector
from escpos import EscposImage

connector = NetworkConnector("192.168.1.100")
printer = Printer(connector)

# Load and print an image
img = EscposImage.load("logo.png")
printer.graphics(img)

# Or with size option
printer.graphics(img, Printer.IMG_DOUBLE_WIDTH)

printer.cut()
printer.close()
```

## Text Formatting

```python
from escpos import Printer
from escpos.connectors import NetworkConnector

connector = NetworkConnector("192.168.1.100")
printer = Printer(connector)

# Text sizes (1-8 for width and height)
printer.set_text_size(2, 2)  # Double width and height
printer.text("BIG TEXT\n")
printer.set_text_size(1, 1)  # Normal

# Bold text
printer.set_emphasis(True)
printer.text("Bold text\n")
printer.set_emphasis(False)

# Underline
printer.set_underline(Printer.UNDERLINE_SINGLE)
printer.text("Underlined\n")
printer.set_underline(Printer.UNDERLINE_NONE)

# Justification
printer.set_justification(Printer.JUSTIFY_CENTER)
printer.text("Centered\n")
printer.set_justification(Printer.JUSTIFY_RIGHT)
printer.text("Right aligned\n")
printer.set_justification(Printer.JUSTIFY_LEFT)

# Fonts
printer.set_font(Printer.FONT_B)
printer.text("Font B (smaller)\n")
printer.set_font(Printer.FONT_A)

printer.cut()
printer.close()
```

## Supported Connectors

| Connector | Description | Requirements |
|-----------|-------------|--------------|
| `NetworkConnector` | TCP/IP network printers | None |
| `USBConnector` | USB printers | `pyusb` |
| `SerialConnector` | Serial port printers | `pyserial` |
| `FileConnector` | File or device path | None |
| `CupsConnector` | CUPS printing system (Linux/macOS) | `pycups` |
| `WindowsConnector` | Windows printing API | Windows |
| `DummyConnector` | Testing (captures output) | None |
| `MultipleConnector` | Broadcast to multiple printers | None |

## Printer Capability Profiles

The library includes capability profiles for many printer models:

```python
from escpos import Printer, CapabilityProfile
from escpos.connectors import NetworkConnector

# List available profiles
profiles = CapabilityProfile.get_profile_names()
print(profiles)

# Use a specific profile
profile = CapabilityProfile.load("TM-T88IV")
connector = NetworkConnector("192.168.1.100")
printer = Printer(connector, profile)
```

## API Reference

### Printer Class Constants

**Barcode Types:**
- `BARCODE_UPCA`, `BARCODE_UPCE`, `BARCODE_JAN13`, `BARCODE_JAN8`
- `BARCODE_CODE39`, `BARCODE_ITF`, `BARCODE_CODABAR`
- `BARCODE_CODE93`, `BARCODE_CODE128`

**QR Code:**
- `QR_ECLEVEL_L`, `QR_ECLEVEL_M`, `QR_ECLEVEL_Q`, `QR_ECLEVEL_H`
- `QR_MODEL_1`, `QR_MODEL_2`, `QR_MICRO`

**Text:**
- `JUSTIFY_LEFT`, `JUSTIFY_CENTER`, `JUSTIFY_RIGHT`
- `FONT_A`, `FONT_B`, `FONT_C`
- `UNDERLINE_NONE`, `UNDERLINE_SINGLE`, `UNDERLINE_DOUBLE`

**Cut:**
- `CUT_FULL`, `CUT_PARTIAL`

**Images:**
- `IMG_DEFAULT`, `IMG_DOUBLE_WIDTH`, `IMG_DOUBLE_HEIGHT`, `IMG_DOUBLE_WIDTH | IMG_DOUBLE_HEIGHT`

### Main Methods

| Method | Description |
|--------|-------------|
| `initialize()` | Reset printer to default state |
| `text(str)` | Print text |
| `feed(lines)` | Feed paper |
| `cut(mode, lines)` | Cut paper |
| `barcode(content, type)` | Print barcode |
| `qr_code(content, ec, size, model)` | Print QR code |
| `graphics(image, size)` | Print image |
| `pulse(pin, on_ms, off_ms)` | Open cash drawer |
| `set_font(font)` | Set font |
| `set_justification(justification)` | Set text alignment |
| `set_text_size(width, height)` | Set text size |
| `set_emphasis(on)` | Set bold |
| `set_underline(mode)` | Set underline |
| `close()` | Close connection |

## Troubleshooting

### Permission Denied (Linux USB)

Add udev rules for your printer:

```bash
# /etc/udev/rules.d/99-escpos.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0202", MODE="0666"
```

Then reload rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Finding USB Vendor/Product ID

```bash
lsusb
# Look for your printer, e.g.:
# Bus 001 Device 005: ID 04b8:0202 Seiko Epson Corp. Receipt Printer
```

### Network Printer Not Responding

- Verify printer IP: `ping 192.168.1.100`
- Check port is open: `nc -zv 192.168.1.100 9100`
- Ensure firewall allows port 9100

## Credits

- **Original PHP Library:** [mike42/escpos-php](https://github.com/mike42/escpos-php) by Michael Billington
- **Python Port:** [Yevhen Salitrynskyi](https://github.com/ysalitrynskyi)

## License

MIT License - see the original [escpos-php](https://github.com/mike42/escpos-php) for details.
