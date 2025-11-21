"""
Print buffers for escpos-thermal.

Buffers manage text output and character encoding for the printer.
"""

from escpos_thermal.buffers.print_buffer import PrintBuffer
from escpos_thermal.buffers.escpos_print_buffer import EscposPrintBuffer

__all__ = [
    "PrintBuffer",
    "EscposPrintBuffer",
]

# Optional buffer (requires Pillow with font support)
try:
    from escpos_thermal.buffers.image_print_buffer import ImagePrintBuffer
    __all__.append("ImagePrintBuffer")
except ImportError:
    pass
