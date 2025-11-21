"""
CodePage class for character encoding support.

This file is part of escpos-printer: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>
Copyright (c) 2025 Yevhen Salitrynskyi <ysalitrynskyi@gmail.com> - Python port

This software is distributed under the terms of the MIT license.
"""

from typing import Dict, List, Optional, Any
import codecs


class CodePage:
    """
    Class to handle data about a particular CodePage, as loaded from the receipt print
    database.

    Also computes map between UTF-8 and this encoding if necessary.
    """

    # Value to use when no character is set. This is a space in ASCII.
    MISSING_CHAR_CODE = 0x20

    def __init__(self, id: str, code_page_data: Dict[str, Any]):
        """
        Create a new CodePage.

        Args:
            id: Unique internal identifier for the CodePage.
            code_page_data: Associative dict of CodePage data. May contain
                'name', 'data', 'iconv', 'python_encode', and 'notes' fields.
        """
        self._id = id
        self._name = code_page_data.get('name', id)
        self._iconv = code_page_data.get('iconv')
        self._python_encode = code_page_data.get('python_encode')
        self._notes = code_page_data.get('notes')

        # Process data field if present
        data = code_page_data.get('data')
        if data is not None:
            self._data = self._encoding_array_from_data(data)
        else:
            self._data = None

    def get_id(self) -> str:
        """
        Get the unique identifier of the code page.

        Returns:
            Unique identifier string.
        """
        return self._id

    def get_name(self) -> str:
        """
        Get the name of the code page.

        Returns:
            Name of the code page.
        """
        return self._name

    def get_iconv(self) -> Optional[str]:
        """
        Get the iconv encoding name.

        Returns:
            Iconv encoding name, or None if not set.
        """
        return self._iconv

    def get_notes(self) -> Optional[str]:
        """
        Get notes about this code page.

        The notes may explain quirks about a code-page, such as a source if it's
        non-standard or un-encodeable.

        Returns:
            Notes on the code page, or None if not set.
        """
        return self._notes

    def is_encodable(self) -> bool:
        """
        Check if we can encode with this code page.

        Many printers contain vendor-specific code pages, which are named but have
        not been identified or typed out. For our purposes, this is an "un-encodeable"
        code page.

        Returns:
            True if we can encode with this code page, False otherwise.
        """
        return self._iconv is not None or self._python_encode is not None or self._data is not None

    def get_data_array(self) -> List[int]:
        """
        Get a 128-entry array of unicode code-points from this code page.

        Returns:
            128-entry list of code points for characters 128-255.

        Raises:
            ValueError: If the data is not known or computable.
        """
        if self._data is not None:
            return self._data

        # Try to compute using Python's encoding
        encoding_name = self._python_encode or self._iconv
        if encoding_name is not None:
            self._data = self._generate_encoding_array(encoding_name)
            return self._data

        raise ValueError(f"Cannot encode code page {self._id}")

    def _generate_encoding_array(self, encoding_name: str) -> List[int]:
        """
        Generate a 128-entry array of unicode code-points.

        Args:
            encoding_name: Name of the encoding to use.

        Returns:
            128-entry list of code points for characters 128-255.
        """
        # Normalize encoding name for Python
        encoding = self._normalize_encoding_name(encoding_name)

        result = [self.MISSING_CHAR_CODE] * 128

        for char_code in range(128, 256):
            try:
                # Try to decode this byte
                byte = bytes([char_code])
                decoded = byte.decode(encoding, errors='strict')

                # Check if it decodes to a single character
                if len(decoded) == 1:
                    # Check if it round-trips correctly
                    reencoded = decoded.encode(encoding, errors='strict')
                    if reencoded == byte:
                        result[char_code - 128] = ord(decoded)
            except (UnicodeDecodeError, UnicodeEncodeError, LookupError):
                pass

        return result

    def _normalize_encoding_name(self, name: str) -> str:
        """
        Normalize encoding name for Python's codecs.

        Args:
            name: Original encoding name.

        Returns:
            Normalized encoding name.
        """
        # Map common iconv names to Python codec names
        mappings = {
            'CP437': 'cp437',
            'CP850': 'cp850',
            'CP858': 'cp858',
            'CP860': 'cp860',
            'CP863': 'cp863',
            'CP865': 'cp865',
            'CP1250': 'cp1250',
            'CP1251': 'cp1251',
            'CP1252': 'cp1252',
            'CP1253': 'cp1253',
            'CP1254': 'cp1254',
            'CP1255': 'cp1255',
            'CP1256': 'cp1256',
            'CP1257': 'cp1257',
            'CP1258': 'cp1258',
            'ISO-8859-1': 'iso-8859-1',
            'ISO-8859-2': 'iso-8859-2',
            'ISO-8859-7': 'iso-8859-7',
            'ISO-8859-15': 'iso-8859-15',
            'KOI8-R': 'koi8-r',
            'KOI8-U': 'koi8-u',
            'Shift_JIS': 'shift_jis',
            'GB18030': 'gb18030',
            'GBK': 'gbk',
            'BIG5': 'big5',
            'TIS-620': 'tis-620',
            'WINDOWS-874': 'cp874',
        }

        # Check direct mapping
        if name.upper() in mappings:
            return mappings[name.upper()]

        # Try as-is
        try:
            codecs.lookup(name)
            return name
        except LookupError:
            pass

        # Try lowercase
        try:
            codecs.lookup(name.lower())
            return name.lower()
        except LookupError:
            pass

        # Try with common transformations
        normalized = name.replace('-', '_').replace(' ', '_').lower()
        try:
            codecs.lookup(normalized)
            return normalized
        except LookupError:
            pass

        # Give up and return original (will fail at encode time)
        return name

    def _encoding_array_from_data(self, data: List[str]) -> List[int]:
        """
        Parse encoding data from JSON format.

        Args:
            data: List of strings containing unicode characters.

        Returns:
            128-entry list of code points.
        """
        # Join all lines
        text = ''.join(data)

        result = [self.MISSING_CHAR_CODE] * 128
        idx = 0

        for char in text:
            if idx >= 128:
                break
            result[idx] = ord(char)
            idx += 1

        return result
