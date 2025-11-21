"""
Print buffers for escpos-printer.

Buffers manage text output and character encoding for the printer.
"""

from escpos_printer.buffers.print_buffer import PrintBuffer
from escpos_printer.buffers.escpos_print_buffer import EscposPrintBuffer

__all__ = [
    "PrintBuffer",
    "EscposPrintBuffer",
]

# Optional buffer (requires Pillow with font support)
try:
    from escpos_printer.buffers.image_print_buffer import ImagePrintBuffer
    __all__.append("ImagePrintBuffer")
except ImportError:
    pass
