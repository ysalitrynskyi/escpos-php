"""
Pytest configuration and fixtures for escpos-thermal tests.
"""

import pytest
import sys
from pathlib import Path

# Add the escpos package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from escpos_thermal.printer import Printer
from escpos_thermal.connectors.dummy_connector import DummyConnector
from escpos_thermal.capability_profile import CapabilityProfile


def friendly_binary(data: bytes) -> str:
    """
    Convert binary data to a readable hex/string representation.

    Args:
        data: Binary data to convert.

    Returns:
        Human-readable string representation.
    """
    output = []
    for byte in data:
        if 32 <= byte < 127:
            output.append(chr(byte))
        else:
            output.append(f"\\x{byte:02x}")
    return ''.join(output)


@pytest.fixture
def dummy_connector():
    """Create a DummyConnector for testing."""
    return DummyConnector()


@pytest.fixture
def printer(dummy_connector):
    """Create a Printer with DummyConnector for testing."""
    return Printer(dummy_connector)


@pytest.fixture
def default_profile():
    """Load the default capability profile."""
    return CapabilityProfile.load('default')


def check_output(connector: DummyConnector, expected: bytes) -> None:
    """
    Assert that the connector output matches expected bytes.

    Args:
        connector: The DummyConnector to check.
        expected: Expected output bytes.
    """
    actual = connector.get_data()
    if actual != expected:
        print(f"\nExpected: {friendly_binary(expected)}")
        print(f"Actual:   {friendly_binary(actual)}")
    assert actual == expected
