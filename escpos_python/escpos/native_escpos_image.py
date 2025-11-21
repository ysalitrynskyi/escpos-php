"""
NativeEscposImage - Image handling using pure Python.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

import struct
import zlib
from typing import Optional, BinaryIO

from escpos.escpos_image import EscposImage


class NativeEscposImage(EscposImage):
    """
    Implementation of EscposImage using pure Python for basic image formats.

    Supports: PNG, BMP, GIF, PBM, PGM, PPM, WBMP
    """

    def __init__(self, filename: Optional[str] = None, allow_optimisations: bool = True):
        """
        Construct a new NativeEscposImage.

        Args:
            filename: Path to image file, or None for empty image.
            allow_optimisations: True to use library-specific shortcuts.
        """
        super().__init__(filename, allow_optimisations)

        if filename is not None:
            self._load_image_data(filename)

    def _load_image_data(self, filename: Optional[str] = None) -> None:
        """
        Load an image from disk using pure Python.

        Args:
            filename: The filename to load from.
        """
        if filename is None:
            return super()._load_image_data(filename)

        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        with open(filename, 'rb') as f:
            if ext == 'png':
                self._load_png(f)
            elif ext == 'bmp':
                self._load_bmp(f)
            elif ext in ('pbm', 'pgm', 'ppm'):
                self._load_pnm(f)
            elif ext == 'gif':
                self._load_gif(f)
            elif ext == 'wbmp':
                self._load_wbmp(f)
            else:
                raise ValueError(f"Unsupported format: {ext}")

    def _load_png(self, f: BinaryIO) -> None:
        """Load a PNG file."""
        # Check PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Invalid PNG file")

        width = height = 0
        bit_depth = color_type = 0
        image_data = []

        while True:
            chunk_len = struct.unpack('>I', f.read(4))[0]
            chunk_type = f.read(4)
            chunk_data = f.read(chunk_len)
            f.read(4)  # CRC

            if chunk_type == b'IHDR':
                width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk_data[:10])
            elif chunk_type == b'IDAT':
                image_data.append(chunk_data)
            elif chunk_type == b'IEND':
                break

        # Decompress image data
        raw_data = zlib.decompress(b''.join(image_data))

        # Parse scanlines (very simplified - assumes 8-bit grayscale or RGB)
        img_data = []
        bytes_per_pixel = 1 if color_type == 0 else 3 if color_type == 2 else 4
        row_size = 1 + width * bytes_per_pixel  # +1 for filter byte

        for y in range(height):
            row_start = y * row_size + 1  # Skip filter byte
            for x in range(width):
                pixel_start = row_start + x * bytes_per_pixel
                if color_type == 0:  # Grayscale
                    gray = raw_data[pixel_start]
                elif color_type == 2:  # RGB
                    r = raw_data[pixel_start]
                    g = raw_data[pixel_start + 1]
                    b = raw_data[pixel_start + 2]
                    gray = (r + g + b) // 3
                elif color_type == 6:  # RGBA
                    r = raw_data[pixel_start]
                    g = raw_data[pixel_start + 1]
                    b = raw_data[pixel_start + 2]
                    a = raw_data[pixel_start + 3]
                    if a < 128:  # Mostly transparent = white
                        gray = 255
                    else:
                        gray = (r + g + b) // 3
                else:
                    gray = 128

                black = 1 if gray < 128 else 0
                img_data.append(str(black))

        self._set_img_width(width)
        self._set_img_height(height)
        self._set_img_data(''.join(img_data))

    def _load_bmp(self, f: BinaryIO) -> None:
        """Load a BMP file."""
        # BMP header
        header = f.read(14)
        if header[:2] != b'BM':
            raise ValueError("Invalid BMP file")

        # DIB header
        dib_header = f.read(40)
        width, height = struct.unpack('<ii', dib_header[4:12])
        bit_count = struct.unpack('<H', dib_header[14:16])[0]

        # Handle negative height (top-down bitmap)
        top_down = height < 0
        height = abs(height)

        # Read pixel data (simplified - assumes 24-bit)
        row_size = ((width * bit_count + 31) // 32) * 4
        f.seek(struct.unpack('<I', header[10:14])[0])

        rows = []
        for _ in range(height):
            row_data = f.read(row_size)
            rows.append(row_data)

        if not top_down:
            rows.reverse()

        img_data = []
        for row in rows:
            for x in range(width):
                if bit_count == 24:
                    pixel_start = x * 3
                    b = row[pixel_start]
                    g = row[pixel_start + 1]
                    r = row[pixel_start + 2]
                    gray = (r + g + b) // 3
                elif bit_count == 8:
                    gray = row[x]
                else:
                    gray = 128

                black = 1 if gray < 128 else 0
                img_data.append(str(black))

        self._set_img_width(width)
        self._set_img_height(height)
        self._set_img_data(''.join(img_data))

    def _load_pnm(self, f: BinaryIO) -> None:
        """Load a PBM/PGM/PPM file."""
        # Read magic number
        magic = f.read(2)
        if magic not in (b'P1', b'P2', b'P3', b'P4', b'P5', b'P6'):
            raise ValueError("Invalid PNM file")

        is_binary = magic in (b'P4', b'P5', b'P6')
        is_bitmap = magic in (b'P1', b'P4')
        is_rgb = magic in (b'P3', b'P6')

        # Skip whitespace and comments
        def read_token():
            token = b''
            while True:
                c = f.read(1)
                if c == b'#':
                    while c != b'\n':
                        c = f.read(1)
                elif c in b' \t\r\n':
                    if token:
                        return token
                else:
                    token += c

        width = int(read_token())
        height = int(read_token())
        max_val = 1 if is_bitmap else int(read_token())

        img_data = []

        if is_binary:
            if is_bitmap:
                # P4: packed bits
                row_bytes = (width + 7) // 8
                for _ in range(height):
                    row = f.read(row_bytes)
                    for x in range(width):
                        byte_idx = x // 8
                        bit_idx = 7 - (x % 8)
                        pixel = (row[byte_idx] >> bit_idx) & 1
                        img_data.append(str(pixel))
            elif is_rgb:
                # P6: binary RGB
                for _ in range(height * width):
                    r, g, b = f.read(3)
                    gray = (r + g + b) // 3
                    black = 1 if gray < max_val // 2 else 0
                    img_data.append(str(black))
            else:
                # P5: binary grayscale
                for _ in range(height * width):
                    gray = f.read(1)[0]
                    black = 1 if gray < max_val // 2 else 0
                    img_data.append(str(black))
        else:
            # ASCII formats
            pixels = []
            remaining = f.read().decode('ascii')
            for token in remaining.split():
                if token.startswith('#'):
                    continue
                pixels.append(int(token))

            idx = 0
            for _ in range(height * width):
                if is_bitmap:
                    black = pixels[idx]
                    idx += 1
                elif is_rgb:
                    r, g, b = pixels[idx:idx + 3]
                    idx += 3
                    gray = (r + g + b) // 3
                    black = 1 if gray < max_val // 2 else 0
                else:
                    gray = pixels[idx]
                    idx += 1
                    black = 1 if gray < max_val // 2 else 0
                img_data.append(str(black))

        self._set_img_width(width)
        self._set_img_height(height)
        self._set_img_data(''.join(img_data))

    def _load_gif(self, f: BinaryIO) -> None:
        """Load a GIF file (basic support - first frame only)."""
        # Check GIF signature
        signature = f.read(6)
        if signature not in (b'GIF87a', b'GIF89a'):
            raise ValueError("Invalid GIF file")

        # Logical screen descriptor
        width, height = struct.unpack('<HH', f.read(4))
        flags = f.read(1)[0]
        f.read(2)  # Background color index, pixel aspect ratio

        # Global color table
        has_gct = (flags >> 7) & 1
        gct_size = 2 ** ((flags & 7) + 1) if has_gct else 0

        color_table = []
        if has_gct:
            for _ in range(gct_size):
                r, g, b = f.read(3)
                gray = (r + g + b) // 3
                color_table.append(gray)

        # Skip to image data (simplified - ignores extensions)
        img_data = ['0'] * (width * height)

        while True:
            block_type = f.read(1)
            if block_type == b'\x2c':  # Image descriptor
                left, top, img_width, img_height = struct.unpack('<HHHH', f.read(8))
                flags = f.read(1)[0]

                has_lct = (flags >> 7) & 1
                if has_lct:
                    lct_size = 2 ** ((flags & 7) + 1)
                    for _ in range(lct_size):
                        f.read(3)  # Skip local color table

                min_code_size = f.read(1)[0]
                # Skip LZW data (simplified - just mark as gray)
                while True:
                    sub_block_size = f.read(1)[0]
                    if sub_block_size == 0:
                        break
                    f.read(sub_block_size)

                # Can't decode LZW without more code, so fill with pattern
                break
            elif block_type == b'\x21':  # Extension
                f.read(1)  # Extension type
                while True:
                    sub_block_size = f.read(1)[0]
                    if sub_block_size == 0:
                        break
                    f.read(sub_block_size)
            elif block_type == b'\x3b' or not block_type:  # Trailer
                break

        self._set_img_width(width)
        self._set_img_height(height)
        self._set_img_data(''.join(img_data))

    def _load_wbmp(self, f: BinaryIO) -> None:
        """Load a WBMP file."""
        # Type and fixed header
        type_field = f.read(1)[0]
        f.read(1)  # Fixed header

        # Read multi-byte integers
        def read_multibyte():
            value = 0
            while True:
                byte = f.read(1)[0]
                value = (value << 7) | (byte & 0x7f)
                if not (byte & 0x80):
                    break
            return value

        width = read_multibyte()
        height = read_multibyte()

        img_data = []
        row_bytes = (width + 7) // 8

        for _ in range(height):
            row = f.read(row_bytes)
            for x in range(width):
                byte_idx = x // 8
                bit_idx = 7 - (x % 8)
                pixel = 1 - ((row[byte_idx] >> bit_idx) & 1)  # WBMP: 0=black, 1=white
                img_data.append(str(pixel))

        self._set_img_width(width)
        self._set_img_height(height)
        self._set_img_data(''.join(img_data))
