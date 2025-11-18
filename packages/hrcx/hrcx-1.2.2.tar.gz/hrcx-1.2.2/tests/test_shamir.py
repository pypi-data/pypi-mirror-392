"""
Tests for Shamir's Secret Sharing implementation.
"""

import pytest
from hrcx.shamir import split, combine


def test_split_and_combine_simple():
    """Test basic split and combine with minimum threshold."""
    secret = b"hello world"
    shares = split(secret, total=3, threshold=2)
    
    assert len(shares) == 3
    assert all(len(share) == len(secret) + 1 for share in shares)  # +1 for x-coordinate
    
    # Any 2 shares should reconstruct the secret
    reconstructed = combine(shares[:2])
    assert reconstructed == secret
    
    reconstructed = combine(shares[1:])
    assert reconstructed == secret
    
    reconstructed = combine([shares[0], shares[2]])
    assert reconstructed == secret


def test_split_and_combine_all_shares():
    """Test reconstruction with all shares."""
    secret = b"test secret"
    shares = split(secret, total=5, threshold=3)
    
    # Using all 5 shares should also work
    reconstructed = combine(shares)
    assert reconstructed == secret


def test_split_single_byte():
    """Test with a single-byte secret."""
    secret = b"X"
    shares = split(secret, total=5, threshold=3)
    
    reconstructed = combine(shares[:3])
    assert reconstructed == secret


def test_split_long_secret():
    """Test with a longer secret."""
    secret = b"This is a much longer secret that spans multiple words and contains various characters!"
    shares = split(secret, total=7, threshold=4)
    
    reconstructed = combine(shares[:4])
    assert reconstructed == secret
    
    # Try with different combinations
    reconstructed = combine(shares[2:6])
    assert reconstructed == secret


def test_invalid_threshold_too_low():
    """Test that threshold < 2 raises error."""
    with pytest.raises(ValueError, match="Threshold must be at least 2"):
        split(b"secret", total=3, threshold=1)


def test_invalid_total_less_than_threshold():
    """Test that total < threshold raises error."""
    with pytest.raises(ValueError, match="Total shares must be >= threshold"):
        split(b"secret", total=2, threshold=3)


def test_invalid_total_too_high():
    """Test that total > 255 raises error."""
    with pytest.raises(ValueError, match="Total shares cannot exceed 255"):
        split(b"secret", total=256, threshold=2)


def test_invalid_empty_secret():
    """Test that empty secret raises error."""
    with pytest.raises(ValueError, match="Secret cannot be empty"):
        split(b"", total=3, threshold=2)


def test_combine_insufficient_shares():
    """Test that < 2 shares raises error."""
    secret = b"test"
    shares = split(secret, total=3, threshold=2)
    
    with pytest.raises(ValueError, match="Need at least 2 shares"):
        combine([shares[0]])


def test_combine_mismatched_lengths():
    """Test that shares with different lengths raise error."""
    share1 = b"\x01ABC"
    share2 = b"\x02ABCD"  # Different length
    
    with pytest.raises(ValueError, match="All shares must have the same length"):
        combine([share1, share2])


def test_combine_duplicate_shares():
    """Test that duplicate shares (same x-coordinate) raise error."""
    secret = b"test"
    shares = split(secret, total=3, threshold=2)
    
    # Use same share twice
    with pytest.raises(ValueError, match="Duplicate shares"):
        combine([shares[0], shares[0]])


def test_shares_are_different():
    """Test that all shares are different from each other."""
    secret = b"secret data"
    shares = split(secret, total=5, threshold=3)
    
    # All shares should be unique
    assert len(set(shares)) == len(shares)
    
    # Each share should be different from the secret
    for share in shares:
        assert share[1:] != secret  # Skip x-coordinate


def test_binary_data():
    """Test with binary data (not just ASCII)."""
    secret = bytes(range(256))  # All possible byte values
    shares = split(secret, total=5, threshold=3)
    
    reconstructed = combine(shares[:3])
    assert reconstructed == secret


def test_maximum_values():
    """Test with maximum allowed parameters."""
    secret = b"test"
    shares = split(secret, total=255, threshold=255)
    
    # Need all 255 shares
    reconstructed = combine(shares)
    assert reconstructed == secret


def test_threshold_exactly_met():
    """Test that threshold-1 shares cannot reconstruct."""
    secret = b"important secret"
    threshold = 4
    shares = split(secret, total=6, threshold=threshold)
    
    # With threshold shares, reconstruction should work
    reconstructed = combine(shares[:threshold])
    assert reconstructed == secret
    
    # Note: With threshold-1 shares, the reconstruction will produce wrong result
    # (but won't raise an error, as this is a mathematical property of Shamir's scheme)
    wrong_result = combine(shares[:threshold-1])
    assert wrong_result != secret  # Should be wrong


def test_x_coordinates_are_sequential():
    """Test that shares have sequential x-coordinates starting from 1."""
    secret = b"test"
    shares = split(secret, total=5, threshold=3)
    
    x_coords = [share[0] for share in shares]
    assert x_coords == [1, 2, 3, 4, 5]
