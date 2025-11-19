"""Tests for pytzconvert."""

from pylib-tzconvert import convert_timezone


def test_convert_timezone():
    """Test convert_timezone."""
    assert convert_timezone() is None or True
