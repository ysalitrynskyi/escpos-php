# escpos-printer

A powerful Python library for ESC/POS thermal receipt printers.

## Features

- **Full ESC/POS Support** - Text, formatting, barcodes, QR codes, images, and more
- **Multiple Connections** - Network (TCP/IP), USB, Serial, File, CUPS, and Windows printing
- **Async Support** - AsyncNetworkConnector for non-blocking I/O
- **Image Dithering** - Floyd-Steinberg, Atkinson, and ordered dithering algorithms
- **Printer Status** - Read paper status, online state, and error conditions
- **Cash Drawer Control** - Open drawers and check open/closed status
- **Context Manager** - Clean resource management with `with` statement
- **Logging** - Built-in debug logging support
- **294 Tests** - Comprehensive test coverage

## Installation

```bash
pip install escpos-printer
```

### Optional Dependencies

```bash
# USB printer support
pip install pyusb

# Serial printer support
pip install pyserial

# QR code generation fallback
pip install qrcode

# Barcode generation fallback
pip install python-barcode
```

## Quick Start

```python
from escpos_printer import Printer
from escpos_printer.connectors import NetworkConnector

# Using context manager (recommended)
with Printer(NetworkConnector("192.168.1.100", 9100)) as printer:
    printer.text("Hello, World!\n")
    printer.barcode("123456789012", Printer.BARCODE_UPCA)
    printer.qr_code("https://example.com")
    printer.cut()
```

## Connection Types

### Network Printer (TCP/IP)

```python
from escpos_printer import Printer
from escpos_printer.connectors import NetworkConnector

with Printer(NetworkConnector("192.168.1.100", 9100)) as printer:
    printer.text("Network printing!\n")
    printer.cut()
```

### Async Network Printer

```python
import asyncio
from escpos_printer.connectors import AsyncNetworkConnector

async def print_async():
    async with AsyncNetworkConnector("192.168.1.100", 9100) as conn:
        await conn.write(b"\x1b@")  # Initialize
        await conn.write(b"Async printing!\n")
        await conn.write(b"\x1dVA\x03")  # Cut

asyncio.run(print_async())
```

### USB Printer

```python
from escpos_printer import Printer
from escpos_printer.connectors import USBConnector

# Find vendor/product ID with: lsusb
with Printer(USBConnector(0x04b8, 0x0202)) as printer:
    printer.text("USB printing!\n")
    printer.cut()
```

### Serial Printer

```python
from escpos_printer import Printer
from escpos_printer.connectors import SerialConnector

with Printer(SerialConnector("/dev/ttyUSB0", 9600)) as printer:
    printer.text("Serial printing!\n")
    printer.cut()
```

## Text Formatting

```python
with Printer(connector) as printer:
    # Text sizes (1-8)
    printer.set_text_size(2, 2)
    printer.text("BIG TEXT\n")
    printer.set_text_size(1, 1)

    # Styles
    printer.set_emphasis(True)
    printer.text("Bold\n")
    printer.set_emphasis(False)

    printer.set_underline(Printer.UNDERLINE_SINGLE)
    printer.text("Underlined\n")
    printer.set_underline(Printer.UNDERLINE_NONE)

    # Alignment
    printer.set_justification(Printer.JUSTIFY_CENTER)
    printer.text("Centered\n")
    printer.set_justification(Printer.JUSTIFY_LEFT)

    # Fonts
    printer.set_font(Printer.FONT_B)
    printer.text("Smaller font\n")
    printer.set_font(Printer.FONT_A)
```

## Barcodes

```python
with Printer(connector) as printer:
    # Configure barcode appearance
    printer.set_barcode_height(80)
    printer.set_barcode_width(3)
    printer.set_barcode_text_position(Printer.BARCODE_TEXT_BELOW)

    # Print various barcode types
    printer.barcode("012345678905", Printer.BARCODE_UPCA)
    printer.barcode("5901234123457", Printer.BARCODE_JAN13)
    printer.barcode("{BHELLO123", Printer.BARCODE_CODE128)
    printer.barcode("ABC123", Printer.BARCODE_CODE39)
```

## QR Codes

```python
with Printer(connector) as printer:
    # Simple QR code
    printer.qr_code("https://example.com")

    # With options
    printer.qr_code(
        "https://example.com",
        ec=Printer.QR_ECLEVEL_H,  # High error correction
        size=8,                    # Module size
        model=Printer.QR_MODEL_2
    )
```

## Image Printing with Dithering

```python
from escpos_printer import Printer, PillowEscposImage, DitherMode
from escpos_printer.connectors import NetworkConnector

with Printer(NetworkConnector("192.168.1.100")) as printer:
    # Simple threshold (default)
    img = PillowEscposImage("logo.png")
    printer.graphics(img)

    # Floyd-Steinberg dithering (best for photos)
    img = PillowEscposImage("photo.jpg", dither=DitherMode.FLOYDSTEINBERG)
    printer.graphics(img)

    # Atkinson dithering (lighter, good for graphics)
    img = PillowEscposImage("graphic.png", dither=DitherMode.ATKINSON)
    printer.graphics(img)

    # Custom threshold
    img = PillowEscposImage("logo.png", threshold=100)
    printer.graphics(img)
```

### Convert Image to Monochrome

```python
from PIL import Image
from escpos_printer import PillowEscposImage, DitherMode

# Convert any image to printer-ready monochrome
pil_image = Image.open("photo.jpg")
mono = PillowEscposImage.to_monochrome(pil_image, dither=DitherMode.FLOYDSTEINBERG)
mono.save("preview.png")  # Preview what will print
```

## Printer Status

```python
with Printer(connector) as printer:
    # Check printer status
    if printer.is_online():
        print("Printer is online")

    if printer.has_paper():
        print("Paper is loaded")
    else:
        print("Paper is low or out!")

    if printer.has_error():
        print("Printer has an error")
```

## Cash Drawer

```python
with Printer(connector) as printer:
    # Open cash drawer
    printer.pulse()  # Pin 0, default timing
    printer.pulse(pin=1, on_ms=200, off_ms=400)  # Pin 1, custom timing

    # Check drawer status (requires compatible hardware)
    if printer.is_drawer_open():
        print("Drawer is open!")
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('escpos')
logger.setLevel(logging.DEBUG)

# Now printer operations will log debug info
with Printer(connector) as printer:
    printer.text("Debug logging enabled\n")
```

## Printer Profiles

```python
from escpos_printer import Printer, CapabilityProfile
from escpos_printer.connectors import NetworkConnector

# List available profiles
profiles = CapabilityProfile.get_profile_names()
print(profiles)

# Use a specific profile
profile = CapabilityProfile.load("TM-T88IV")
with Printer(NetworkConnector("192.168.1.100"), profile) as printer:
    printer.text("Using TM-T88IV profile\n")
```

## API Reference

### Printer Constants

| Category | Constants |
|----------|-----------|
| Barcode Types | `BARCODE_UPCA`, `BARCODE_UPCE`, `BARCODE_JAN13`, `BARCODE_JAN8`, `BARCODE_CODE39`, `BARCODE_ITF`, `BARCODE_CODABAR`, `BARCODE_CODE93`, `BARCODE_CODE128` |
| QR Code | `QR_ECLEVEL_L/M/Q/H`, `QR_MODEL_1/2`, `QR_MICRO` |
| Text | `JUSTIFY_LEFT/CENTER/RIGHT`, `FONT_A/B/C`, `UNDERLINE_NONE/SINGLE/DOUBLE` |
| Cut | `CUT_FULL`, `CUT_PARTIAL` |
| Images | `IMG_DEFAULT`, `IMG_DOUBLE_WIDTH`, `IMG_DOUBLE_HEIGHT` |

### DitherMode Options

| Mode | Description |
|------|-------------|
| `DitherMode.NONE` | Simple threshold (fast, good for logos) |
| `DitherMode.FLOYDSTEINBERG` | Floyd-Steinberg error diffusion (best for photos) |
| `DitherMode.ATKINSON` | Atkinson dithering (lighter, good for graphics) |
| `DitherMode.ORDERED` | Bayer ordered dithering (fast, consistent) |

### Connectors

| Connector | Use Case | Requirements |
|-----------|----------|--------------|
| `NetworkConnector` | TCP/IP printers | None |
| `AsyncNetworkConnector` | Async TCP/IP | None |
| `USBConnector` | USB printers | `pyusb` |
| `SerialConnector` | Serial printers | `pyserial` |
| `FileConnector` | Device files | None |
| `CupsConnector` | CUPS (Linux/macOS) | `pycups` |
| `WindowsConnector` | Windows API | Windows |
| `DummyConnector` | Testing | None |

## Requirements

- Python 3.8+
- Pillow (for image support)

## License

MIT License

## Credits

- **Author:** [Yevhen Salitrynskyi](https://github.com/ysalitrynskyi)
- **Based on:** [escpos-php](https://github.com/mike42/escpos-php) by Michael Billington
