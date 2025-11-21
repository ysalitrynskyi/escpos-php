"""
EscposPrintBuffer - Text buffer with character encoding management.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

import os
import gzip
import pickle
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Dict, List, Any

from escpos.buffers.print_buffer import PrintBuffer
from escpos.code_page import CodePage

if TYPE_CHECKING:
    from escpos.printer import Printer


class EscposPrintBuffer(PrintBuffer):
    """
    This class manages newlines and character encoding for the target printer.

    Can be interchanged for an image-based buffer (ImagePrintBuffer) if you can't
    get it operating properly on your machine.
    """

    # True to cache output compressed, False for uncompressed (useful for debugging)
    COMPRESS_CACHE = True

    # Unrecognised characters will be replaced with this
    REPLACEMENT_CHAR = "?"

    def __init__(self):
        """Create an empty print buffer."""
        self._printer: Optional['Printer'] = None
        self._available: Optional[Dict[int, int]] = None
        self._encode: Optional[Dict[int, Dict[int, int]]] = None

    def flush(self) -> None:
        """
        Flush the buffer.

        This indicates that the printer needs the current line to be ended.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")
        # TODO: Not yet fully implemented for this buffer

    def get_printer(self) -> Optional['Printer']:
        """
        Get the printer this buffer is attached to.

        Returns:
            The Printer instance, or None if not attached.
        """
        return self._printer

    def set_printer(self, printer: Optional['Printer']) -> None:
        """
        Set the printer this buffer is attached to.

        Args:
            printer: The Printer instance, or None to detach.
        """
        self._printer = printer
        if printer is not None:
            self._load_available_characters()

    def write_text(self, text: str) -> None:
        """
        Write text to the buffer with automatic character encoding.

        Args:
            text: Text to write, as UTF-8.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")

        # Normalize text - replaces combining characters with composed glyphs
        normalized = unicodedata.normalize('NFC', text)

        # Get current encoding
        encoding = self._printer.get_character_table()
        current_block: List[int] = []

        # Process each code point
        for char in normalized:
            code_point = ord(char)

            # Check if we need to change code pages
            if self._available is None or self._encode is None:
                matching = True
            else:
                # Character matches if it's not in available OR it's in current encoding
                matching = (
                    code_point not in self._available or
                    (encoding in self._encode and code_point in self._encode[encoding])
                )

            if matching:
                current_block.append(code_point)
            else:
                # Write what we have
                self._write_text_using_encoding(current_block, encoding)
                # Find new encoding
                encoding = self._identify_text(code_point)
                current_block = [code_point]

        # Write out remaining bytes
        if current_block:
            self._write_text_using_encoding(current_block, encoding)

    def write_text_raw(self, text: str) -> None:
        """
        Write text to the buffer without character encoding translation.

        Args:
            text: Text to write.
        """
        if self._printer is None:
            raise RuntimeError("Not attached to a printer.")

        if not text:
            return

        # Pass only printable characters
        output = []
        for c in text:
            if c == '\r':
                # Skip Windows line endings
                continue
            elif self._ascii_check(c, extended=True):
                output.append(c)
            else:
                output.append(self.REPLACEMENT_CHAR)

        self._write(''.join(output))

    def _identify_text(self, code_point: int) -> int:
        """
        Return an encoding which we can use for outputting this character.

        Args:
            code_point: Code point to check.

        Returns:
            Code page number, or 0 if not printable on any supported encoding.
        """
        if self._available is None or code_point not in self._available:
            return 0
        return self._available[code_point]

    def _load_available_characters(self) -> None:
        """
        Load character encoding maps for the printer's capability profile.
        """
        profile = self._printer.get_printer_capability_profile()
        supported_code_pages = profile.get_code_pages()
        profile_name = profile.get_id()

        # Cache file path
        cache_dir = Path(__file__).parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        cache_ext = ".ser.z" if self.COMPRESS_CACHE else ".ser"
        cache_file = cache_dir / f"Characters-{profile_name}{cache_ext}"

        cache_key = profile.get_code_page_cache_key()

        # Check for pre-generated file
        if cache_file.exists():
            try:
                cache_data = cache_file.read_bytes()
                if self.COMPRESS_CACHE:
                    cache_data = gzip.decompress(cache_data)
                data_array = pickle.loads(cache_data)

                if (
                    isinstance(data_array, dict) and
                    data_array.get("key") == cache_key and
                    "available" in data_array and
                    "encode" in data_array
                ):
                    self._available = data_array["available"]
                    self._encode = data_array["encode"]
                    return
            except (OSError, pickle.PickleError, gzip.BadGzipFile):
                pass

        # Generate conversion tables
        encode: Dict[int, Dict[int, int]] = {}
        available: Dict[int, int] = {}

        for num, code_page in supported_code_pages.items():
            if not code_page.is_encodable():
                continue

            try:
                char_map = code_page.get_data_array()
            except ValueError:
                continue

            encode_map: Dict[int, int] = {}
            for char_code in range(128, 256):
                code_point = char_map[char_code - 128]
                if code_point == CodePage.MISSING_CHAR_CODE:
                    continue

                encode_map[code_point] = char_code
                if code_point not in available:
                    available[code_point] = num

            encode[num] = encode_map

        # Use generated data
        data_array = {
            "available": available,
            "encode": encode,
            "key": cache_key
        }
        self._available = available
        self._encode = encode

        # Try to cache (but don't fail if we can't)
        try:
            cache_data = pickle.dumps(data_array)
            if self.COMPRESS_CACHE:
                cache_data = gzip.compress(cache_data)
            cache_file.write_bytes(cache_data)
        except OSError:
            pass

    def _write_text_using_encoding(self, code_points: List[int], encoding_no: int) -> None:
        """
        Encode a block of text using the specified map and write to printer.

        Args:
            code_points: Text to print, as list of unicode code points.
            encoding_no: Encoding number to use.
        """
        if not code_points:
            return

        encode_map = self._encode.get(encoding_no, {}) if self._encode else {}

        raw_text = []
        cr = 0x0D  # Carriage return from Windows line endings

        for code_point in code_points:
            if code_point in encode_map:
                # Printable via selected code page
                raw_text.append(chr(encode_map[code_point]))
            elif (32 <= code_point < 127) or code_point == 10:
                # Printable as ASCII
                raw_text.append(chr(code_point))
            elif code_point == cr:
                # Skip Windows line endings
                continue
            else:
                raw_text.append(self.REPLACEMENT_CHAR)

        if self._printer.get_character_table() != encoding_no:
            self._printer.select_character_table(encoding_no)

        self.write_text_raw(''.join(raw_text))

    def _write(self, data: str) -> None:
        """
        Write data to the underlying printer.

        Args:
            data: String data to write.

        Raises:
            ValueError: If the data contains characters outside the latin-1 range.
        """
        try:
            self._printer.get_print_connector().write(data.encode('latin-1'))
        except UnicodeEncodeError as e:
            raise ValueError(f"Cannot encode text for printer (character outside 0-255 range): {e}")

    @staticmethod
    def _ascii_check(char: str, extended: bool = False) -> bool:
        """
        Return true if a character is an ASCII printable character.

        Args:
            char: Character to check.
            extended: True to allow 128-255 values also.

        Returns:
            True if printable, False otherwise.
        """
        if len(char) != 1:
            return False

        num = ord(char)
        if 32 <= num < 127:  # Printable ASCII
            return True
        if num == 10:  # Newline
            return True
        if extended and num > 127:
            return True
        return False
