"""
escpos-thermal: Python library for ESC/POS-compatible thermal and impact receipt printers.

A full-featured library for controlling ESC/POS thermal printers from Python.
Supports text, barcodes, QR codes, images, cash drawers, and more.

This software is distributed under the terms of the MIT license.
"""

from escpos_thermal.printer import Printer
from escpos_thermal.capability_profile import CapabilityProfile
from escpos_thermal.code_page import CodePage
from escpos_thermal.escpos_image import EscposImage
from escpos_thermal.pillow_escpos_image import PillowEscposImage, DitherMode

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
