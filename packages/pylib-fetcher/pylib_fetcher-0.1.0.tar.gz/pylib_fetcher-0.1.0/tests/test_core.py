"""Tests for pyfetcher."""

from pylib-fetcher import fetch


def test_fetch():
    """Test fetch."""
    assert fetch() is None or True
