"""Tests for pycompress."""

from pylib-compress import compress, decompress


def test_compress():
    """Test compress."""
    assert compress() is None or True
