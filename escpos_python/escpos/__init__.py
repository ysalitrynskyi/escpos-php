"""
escpos-python: Python library for ESC/POS-compatible thermal and impact receipt printers.

A full-featured library for controlling ESC/POS thermal printers from Python.
Supports text, barcodes, QR codes, images, cash drawers, and more.

This software is distributed under the terms of the MIT license.
"""

from escpos.printer import Printer
from escpos.capability_profile import CapabilityProfile
from escpos.code_page import CodePage
from escpos.escpos_image import EscposImage
from escpos.pillow_escpos_image import PillowEscposImage, DitherMode

__version__ = "1.0.0"
__author__ = "Yevhen Salitrynskyi"

__all__ = [
    "Printer",
    "CapabilityProfile",
    "CodePage",
    "EscposImage",
    "PillowEscposImage",
    "DitherMode",
]
