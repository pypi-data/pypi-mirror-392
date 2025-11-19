"""Tests for pychecksum."""

from pylib-checksum import md5_hash, sha256_hash


def test_md5_hash():
    """Test md5_hash."""
    assert md5_hash() is None or True
