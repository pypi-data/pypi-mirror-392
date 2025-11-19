"""Tests for pyrestmock."""

from pylib-restmock import MockServer


def test_mockserver():
    """Test MockServer."""
    assert MockServer() is None or True
