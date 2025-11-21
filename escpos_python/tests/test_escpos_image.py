"""
Tests for the EscposImage classes.
"""

import pytest
import tempfile
import os

# Try to import PIL for image tests
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from escpos.escpos_image import EscposImage


class TestEscposImageStatic:
    """Tests for static EscposImage methods."""

    def test_is_pillow_loaded(self):
        """Test checking if Pillow is loaded."""
        result = EscposImage.is_pillow_loaded()
        assert result == PIL_AVAILABLE


@pytest.mark.skipif(not PIL_AVAILABLE, reason="Pillow not installed")
class TestEscposImageWithPillow:
    """Tests for EscposImage with Pillow available."""

    def test_load_png_image(self):
        """Test loading a PNG image."""
        # Create a simple test image
        img = Image.new('RGB', (8, 8), color='white')
        img.putpixel((0, 0), (0, 0, 0))  # Black pixel

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            img.save(temp_path)

        try:
            escpos_img = EscposImage.load(temp_path)
            assert escpos_img.get_width() == 8
            assert escpos_img.get_height() == 8
        finally:
            os.unlink(temp_path)

    def test_to_raster_format(self):
        """Test converting to raster format."""
        # Create a simple 8x8 black and white image
        img = Image.new('RGB', (8, 8), color='white')
        for x in range(8):
            img.putpixel((x, 0), (0, 0, 0))  # First row black

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            img.save(temp_path)

        try:
            escpos_img = EscposImage.load(temp_path)
            raster = escpos_img.to_raster_format()
            assert isinstance(raster, bytes)
            assert len(raster) > 0
        finally:
            os.unlink(temp_path)

    def test_get_width_bytes(self):
        """Test getting width in bytes."""
        img = Image.new('RGB', (20, 10), color='white')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            img.save(temp_path)

        try:
            escpos_img = EscposImage.load(temp_path)
            # Width of 20 pixels = 3 bytes (20/8 rounded up)
            assert escpos_img.get_width_bytes() == 3
        finally:
            os.unlink(temp_path)

    def test_get_height_bytes(self):
        """Test getting height in bytes."""
        img = Image.new('RGB', (10, 20), color='white')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            img.save(temp_path)

        try:
            escpos_img = EscposImage.load(temp_path)
            # Height of 20 pixels = 3 bytes (20/8 rounded up)
            assert escpos_img.get_height_bytes() == 3
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file_raises(self):
        """Test that loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            EscposImage.load('/nonexistent/path/image.png')


@pytest.mark.skipif(not PIL_AVAILABLE, reason="Pillow not installed")
class TestPillowEscposImage:
    """Tests for PillowEscposImage specifically."""

    def test_from_pil_image(self):
        """Test creating from PIL Image directly."""
        from escpos.pillow_escpos_image import PillowEscposImage

        img = Image.new('RGB', (16, 16), color='white')
        escpos_img = PillowEscposImage.from_pil_image(img)

        assert escpos_img.get_width() == 16
        assert escpos_img.get_height() == 16

    def test_rgba_image(self):
        """Test handling RGBA images."""
        from escpos.pillow_escpos_image import PillowEscposImage

        img = Image.new('RGBA', (8, 8), color=(255, 255, 255, 128))
        escpos_img = PillowEscposImage.from_pil_image(img)

        assert escpos_img.get_width() == 8
        assert escpos_img.get_height() == 8


class TestColumnFormat:
    """Tests for column format conversion."""

    @pytest.mark.skipif(not PIL_AVAILABLE, reason="Pillow not installed")
    def test_to_column_format(self):
        """Test converting to column format."""
        img = Image.new('RGB', (8, 16), color='white')

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            img.save(temp_path)

        try:
            escpos_img = EscposImage.load(temp_path)
            columns = escpos_img.to_column_format(double_density=False)
            assert isinstance(columns, list)
        finally:
            os.unlink(temp_path)
