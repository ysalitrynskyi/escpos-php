"""
Print buffers for escpos-python.

Buffers manage text output and character encoding for the printer.
"""

from escpos.buffers.print_buffer import PrintBuffer
from escpos.buffers.escpos_print_buffer import EscposPrintBuffer

__all__ = [
    "PrintBuffer",
    "EscposPrintBuffer",
]

# Optional buffer (requires Pillow with font support)
try:
    from escpos.buffers.image_print_buffer import ImagePrintBuffer
    __all__.append("ImagePrintBuffer")
except ImportError:
    pass
