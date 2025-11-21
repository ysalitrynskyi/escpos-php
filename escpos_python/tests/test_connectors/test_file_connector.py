"""
Tests for the FileConnector class.
"""

import pytest
import tempfile
import os
from escpos_thermal.connectors.file_connector import FileConnector


class TestFileConnector:
    """Tests for FileConnector."""

    def test_create_connector(self):
        """Test creating a FileConnector."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            assert connector is not None
            connector.finalize()
        finally:
            os.unlink(temp_path)

    def test_write_to_file(self):
        """Test writing to a file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.write(b"Hello World")
            connector.finalize()

            with open(temp_path, 'rb') as f:
                content = f.read()
            assert content == b"Hello World"
        finally:
            os.unlink(temp_path)

    def test_multiple_writes(self):
        """Test multiple writes to file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.write(b"Hello ")
            connector.write(b"World")
            connector.finalize()

            with open(temp_path, 'rb') as f:
                content = f.read()
            assert content == b"Hello World"
        finally:
            os.unlink(temp_path)

    def test_write_after_finalize_raises(self):
        """Test that writing after finalize raises an error."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.finalize()
            with pytest.raises(IOError):
                connector.write(b"Test")
        finally:
            os.unlink(temp_path)

    def test_read_after_finalize_raises(self):
        """Test that reading after finalize raises an error."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            connector = FileConnector(temp_path)
            connector.finalize()
            with pytest.raises(IOError):
                connector.read(10)
        finally:
            os.unlink(temp_path)
