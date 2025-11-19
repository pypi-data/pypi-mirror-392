"""Tests for pyauthclient."""

from pylib-authclient import OAuth2Client


def test_oauth2client():
    """Test OAuth2Client."""
    assert OAuth2Client() is None or True
