"""
Extended tests for image handling.
"""

import pytest
import tempfile
import os
from io import BytesIO
from PIL import Image
from escpos.escpos_image import EscposImage
from escpos.pillow_escpos_image import PillowEscposImage


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_temp_image(width, height, color='white', mode='RGB'):
    """Create a temporary image file and return its path."""
    img = Image.new(mode, (width, height), color=color)
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    img.save(path)
    return path


# ============================================================================
# PILLOW IMAGE TESTS
# ============================================================================

class TestPillowEscposImage:
    """Tests for PillowEscposImage class."""

    def test_create_from_file(self):
        """Test creating from image file."""
        path = create_temp_image(100, 50)
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 100
            assert img.get_height() == 50
        finally:
            os.unlink(path)

    def test_create_black_image(self):
        """Test creating from black image."""
        path = create_temp_image(80, 40, color='black')
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 80
            assert img.get_height() == 40
        finally:
            os.unlink(path)

    def test_to_raster_format(self):
        """Test converting to raster format."""
        path = create_temp_image(8, 8)
        try:
            img = PillowEscposImage(path)
            raster = img.to_raster_format()
            assert isinstance(raster, bytes)
            assert len(raster) == 8  # 8 rows * 1 byte each
        finally:
            os.unlink(path)

    def test_to_raster_format_black(self):
        """Test raster format for black image."""
        path = create_temp_image(8, 8, color='black')
        try:
            img = PillowEscposImage(path)
            raster = img.to_raster_format()
            # Black pixels should be 1s (0xFF)
            assert all(b == 0xFF for b in raster)
        finally:
            os.unlink(path)

    def test_to_column_format(self):
        """Test converting to column format."""
        path = create_temp_image(8, 8)
        try:
            img = PillowEscposImage(path)
            columns = img.to_column_format()
            assert isinstance(columns, list)
            assert all(isinstance(col, bytes) for col in columns)
        finally:
            os.unlink(path)

    def test_rgba_image(self):
        """Test RGBA image handling."""
        path = create_temp_image(50, 50, mode='RGBA')
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 50
            raster = img.to_raster_format()
            assert len(raster) > 0
        finally:
            os.unlink(path)

    def test_grayscale_image(self):
        """Test grayscale image."""
        path = create_temp_image(64, 32, mode='L')
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 64
            assert img.get_height() == 32
        finally:
            os.unlink(path)


# ============================================================================
# ESCPOS IMAGE BASE CLASS TESTS
# ============================================================================

class TestEscposImageLoad:
    """Tests for EscposImage.load factory method."""

    def test_load_from_file_path(self):
        """Test loading image from file path."""
        path = create_temp_image(10, 10, color='red')
        try:
            img = EscposImage.load(path)
            assert isinstance(img, PillowEscposImage)
            assert img.get_width() == 10
        finally:
            os.unlink(path)

    def test_load_returns_correct_type(self):
        """Test load returns PillowEscposImage."""
        path = create_temp_image(20, 20)
        try:
            img = EscposImage.load(path)
            assert isinstance(img, PillowEscposImage)
        finally:
            os.unlink(path)


# ============================================================================
# IMAGE DIMENSION TESTS
# ============================================================================

class TestImageDimensions:
    """Tests for image dimension handling."""

    def test_small_image(self):
        """Test very small image."""
        path = create_temp_image(8, 8)
        try:
            img = PillowEscposImage(path)
            assert img.get_height() == 8
        finally:
            os.unlink(path)

    def test_wide_image(self):
        """Test wide image."""
        path = create_temp_image(576, 10)
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 576
            assert img.get_height() == 10
        finally:
            os.unlink(path)

    def test_tall_image(self):
        """Test tall image."""
        path = create_temp_image(10, 200)
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 10
            assert img.get_height() == 200
        finally:
            os.unlink(path)

    def test_square_image(self):
        """Test square image."""
        path = create_temp_image(100, 100)
        try:
            img = PillowEscposImage(path)
            assert img.get_width() == 100
            assert img.get_height() == 100
        finally:
            os.unlink(path)


# ============================================================================
# IMAGE CONTENT TESTS
# ============================================================================

class TestImageContent:
    """Tests for image content processing."""

    def test_white_image_raster(self):
        """Test white image produces all zeros in raster."""
        path = create_temp_image(8, 8, color='white')
        try:
            img = PillowEscposImage(path)
            raster = img.to_raster_format()
            # White pixels should be 0s
            assert all(b == 0x00 for b in raster)
        finally:
            os.unlink(path)

    def test_black_image_raster(self):
        """Test black image produces all ones in raster."""
        path = create_temp_image(8, 8, color='black')
        try:
            img = PillowEscposImage(path)
            raster = img.to_raster_format()
            # Black pixels should be 0xFF
            assert all(b == 0xFF for b in raster)
        finally:
            os.unlink(path)


# ============================================================================
# RASTER OUTPUT TESTS
# ============================================================================

class TestRasterOutput:
    """Tests for raster format output."""

    def test_raster_returns_bytes(self):
        """Test raster format returns bytes."""
        path = create_temp_image(16, 16)
        try:
            img = PillowEscposImage(path)
            raster = img.to_raster_format()
            assert isinstance(raster, bytes)
        finally:
            os.unlink(path)

    def test_raster_length_calculation(self):
        """Test raster length is height * width_bytes."""
        path = create_temp_image(16, 8)  # 2 bytes wide, 8 rows
        try:
            img = PillowEscposImage(path)
            raster = img.to_raster_format()
            # 8 rows * 2 bytes per row = 16 bytes
            assert len(raster) == 16
        finally:
            os.unlink(path)


# ============================================================================
# COLUMN FORMAT TESTS
# ============================================================================

class TestColumnFormat:
    """Tests for column format conversion."""

    def test_column_returns_list(self):
        """Test column format returns list."""
        path = create_temp_image(16, 8)
        try:
            img = PillowEscposImage(path)
            columns = img.to_column_format()
            assert isinstance(columns, list)
        finally:
            os.unlink(path)

    def test_column_contains_bytes(self):
        """Test column list contains bytes objects."""
        path = create_temp_image(16, 8)
        try:
            img = PillowEscposImage(path)
            columns = img.to_column_format()
            assert all(isinstance(col, bytes) for col in columns)
        finally:
            os.unlink(path)
