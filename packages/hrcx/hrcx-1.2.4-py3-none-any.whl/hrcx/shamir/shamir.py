"""
Shamir's Secret Sharing Scheme implementation.

This module implements Shamir's Secret Sharing algorithm, which allows splitting a secret
into N shares where any K shares can reconstruct the secret, but K-1 shares reveal nothing.

The implementation uses polynomial interpolation over Galois Field GF(256).

License: MPL-2 (adapted from Hashicorp Vault)
Original: https://github.com/hashicorp/vault/blob/master/shamir/shamir.go
"""

import secrets
from typing import List

from hrcx.shamir.tables import LOG_TABLE, EXP_TABLE

# Constants
SHARE_OVERHEAD = 1  # Each share has a 1-byte overhead for the x-coordinate


def _add(a: int, b: int) -> int:
    """
    Add two numbers in GF(256).
    
    In GF(256), addition is XOR.
    
    Args:
        a: First operand (0-255)
        b: Second operand (0-255)
    
    Returns:
        Sum in GF(256) (0-255)
    """
    return a ^ b


def _mult(a: int, b: int) -> int:
    """
    Multiply two numbers in GF(256).
    
    Uses logarithm tables for efficient multiplication.
    
    Args:
        a: First operand (0-255)
        b: Second operand (0-255)
    
    Returns:
        Product in GF(256) (0-255)
    """
    if a == 0 or b == 0:
        return 0
    
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    return EXP_TABLE[(log_a + log_b) % 255]


def _div(a: int, b: int) -> int:
    """
    Divide two numbers in GF(256).
    
    Uses logarithm tables for efficient division.
    
    Args:
        a: Dividend (0-255)
        b: Divisor (0-255, must not be 0)
    
    Returns:
        Quotient in GF(256) (0-255)
    
    Raises:
        ZeroDivisionError: If b is 0
    """
    if b == 0:
        raise ZeroDivisionError("Division by zero in GF(256)")
    
    if a == 0:
        return 0
    
    log_a = LOG_TABLE[a]
    log_b = LOG_TABLE[b]
    diff = (log_a - log_b) % 255
    return EXP_TABLE[diff]


class _Polynomial:
    """
    Represents a polynomial over GF(256).
    
    The polynomial is represented as: f(x) = c[0] + c[1]*x + c[2]*x^2 + ... + c[n]*x^n
    where c[0] is the intercept (the secret value).
    """
    
    def __init__(self, intercept: int, degree: int):
        """
        Create a random polynomial with the given intercept and degree.
        
        Args:
            intercept: The y-intercept (the secret value, 0-255)
            degree: The degree of the polynomial (threshold - 1)
        """
        self.coefficients = bytearray(degree + 1)
        self.coefficients[0] = intercept
        
        # Generate random coefficients for terms x^1 through x^degree
        if degree > 0:
            self.coefficients[1:] = secrets.token_bytes(degree)
    
    def evaluate(self, x: int) -> int:
        """
        Evaluate the polynomial at point x using Horner's method.
        
        Args:
            x: The x-coordinate (0-255)
        
        Returns:
            The y-coordinate f(x) (0-255)
        """
        if x == 0:
            return self.coefficients[0]
        
        # Horner's method: f(x) = c[0] + x(c[1] + x(c[2] + x(...)))
        result = self.coefficients[-1]
        for i in range(len(self.coefficients) - 2, -1, -1):
            result = _add(_mult(result, x), self.coefficients[i])
        
        return result


def _interpolate(x_coords: List[int], y_coords: List[int], x: int) -> int:
    """
    Perform Lagrange interpolation to find f(x) given sample points.
    
    Uses Lagrange interpolation formula over GF(256).
    
    Args:
        x_coords: List of x-coordinates of sample points
        y_coords: List of y-coordinates of sample points
        x: The x-coordinate to interpolate at
    
    Returns:
        The interpolated y-coordinate f(x)
    """
    limit = len(x_coords)
    result = 0
    
    for i in range(limit):
        basis = 1
        for j in range(limit):
            if i == j:
                continue
            
            num = _add(x, x_coords[j])
            denom = _add(x_coords[i], x_coords[j])
            term = _div(num, denom)
            basis = _mult(basis, term)
        
        group = _mult(y_coords[i], basis)
        result = _add(result, group)
    
    return result


def split(secret: bytes, total: int, threshold: int) -> List[bytes]:
    """
    Split a secret into shares using Shamir's Secret Sharing.
    
    Creates N shares where any K shares can reconstruct the secret.
    Each byte of the secret is split independently.
    
    Args:
        secret: The secret data to split
        total: Total number of shares to create (must be >= threshold, max 255)
        threshold: Minimum number of shares needed to reconstruct (must be >= 2, max 255)
    
    Returns:
        List of shares, each prefixed with its x-coordinate
    
    Raises:
        ValueError: If parameters are invalid
    
    Example:
        >>> secret = b"my secret key"
        >>> shares = split(secret, total=5, threshold=3)
        >>> # Any 3 of the 5 shares can reconstruct the secret
        >>> reconstructed = combine(shares[:3])
        >>> assert reconstructed == secret
    """
    # Validate parameters
    if threshold < 2:
        raise ValueError("Threshold must be at least 2")
    if total < threshold:
        raise ValueError("Total shares must be >= threshold")
    if total > 255:
        raise ValueError("Total shares cannot exceed 255")
    if threshold > 255:
        raise ValueError("Threshold cannot exceed 255")
    if len(secret) == 0:
        raise ValueError("Secret cannot be empty")
    
    # Initialize shares
    shares = [bytearray() for _ in range(total)]
    
    # Assign x-coordinates to each share (1 through N)
    for i in range(total):
        shares[i].append(i + 1)
    
    # For each byte in the secret, create a polynomial and evaluate at each x-coordinate
    for secret_byte in secret:
        # Create polynomial with this byte as intercept
        poly = _Polynomial(secret_byte, threshold - 1)
        
        # Evaluate polynomial at each x-coordinate and append to corresponding share
        for i in range(total):
            x = i + 1
            y = poly.evaluate(x)
            shares[i].append(y)
    
    return [bytes(share) for share in shares]


def combine(shares: List[bytes]) -> bytes:
    """
    Reconstruct the secret from shares.
    
    Takes K or more shares and reconstructs the original secret using
    Lagrange interpolation over GF(256).
    
    Args:
        shares: List of shares (at least threshold shares required)
    
    Returns:
        The reconstructed secret
    
    Raises:
        ValueError: If shares are invalid or insufficient
    
    Example:
        >>> shares = [share1, share2, share3]  # Any threshold number of shares
        >>> secret = combine(shares)
    """
    if len(shares) < 2:
        raise ValueError("Need at least 2 shares to reconstruct")
    
    # Verify all shares have the same length
    share_len = len(shares[0])
    if share_len < 2:
        raise ValueError("Invalid share: too short")
    
    for share in shares[1:]:
        if len(share) != share_len:
            raise ValueError("All shares must have the same length")
    
    # Extract x-coordinates and verify they're unique
    x_coords = [share[0] for share in shares]
    if len(set(x_coords)) != len(x_coords):
        raise ValueError("Duplicate shares detected (same x-coordinate)")
    
    # Reconstruct each byte of the secret
    secret_len = share_len - 1  # Subtract 1 for the x-coordinate
    secret = bytearray(secret_len)
    
    for byte_idx in range(secret_len):
        # Get y-coordinates for this byte from all shares
        y_coords = [share[byte_idx + 1] for share in shares]
        
        # Interpolate to find the secret byte (f(0))
        secret[byte_idx] = _interpolate(x_coords, y_coords, 0)
    
    return bytes(secret)
