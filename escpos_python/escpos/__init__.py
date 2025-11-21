"""
escpos-python: Python library for ESC/POS-compatible thermal and impact receipt printers.

This is a Python port of the escpos-php library.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

from escpos.printer import Printer
from escpos.capability_profile import CapabilityProfile
from escpos.code_page import CodePage
from escpos.escpos_image import EscposImage

__version__ = "1.0.0"
__author__ = "Michael Billington"
__email__ = "michael.billington@gmail.com"

__all__ = [
    "Printer",
    "CapabilityProfile",
    "CodePage",
    "EscposImage",
]
