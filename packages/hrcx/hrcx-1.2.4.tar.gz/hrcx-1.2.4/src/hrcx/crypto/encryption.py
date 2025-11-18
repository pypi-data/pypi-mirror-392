"""
Encryption and decryption utilities using AES-256-GCM.

This module provides functions for encrypting and decrypting data using AES-256 in GCM mode,
which provides both confidentiality and authenticity.
"""

import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Tuple

# AES-256 requires 32-byte (256-bit) keys
AES_KEY_SIZE = 32  # bytes

# GCM nonce size (96 bits / 12 bytes is standard and most efficient)
GCM_NONCE_SIZE = 12  # bytes


def generate_key() -> bytes:
    """
    Generate a random 256-bit encryption key.
    
    Uses cryptographically secure random number generation.
    
    Returns:
        32-byte random key suitable for AES-256
    
    Example:
        >>> key = generate_key()
        >>> len(key)
        32
    """
    return secrets.token_bytes(AES_KEY_SIZE)


def encrypt(plaintext: bytes, key: bytes) -> Tuple[bytes, bytes]:
    """
    Encrypt data using AES-256-GCM.
    
    GCM mode provides authenticated encryption, meaning it protects both the
    confidentiality and authenticity of the data.
    
    Args:
        plaintext: The data to encrypt
        key: 32-byte AES-256 key
    
    Returns:
        Tuple of (nonce, ciphertext) where:
        - nonce: 12-byte nonce used for encryption (must be stored)
        - ciphertext: Encrypted data with authentication tag appended
    
    Raises:
        ValueError: If key size is incorrect
    
    Example:
        >>> key = generate_key()
        >>> nonce, ciphertext = encrypt(b"secret message", key)
        >>> decrypted = decrypt(ciphertext, key, nonce)
        >>> assert decrypted == b"secret message"
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Key must be {AES_KEY_SIZE} bytes, got {len(key)}")
    
    # Generate a random nonce
    nonce = secrets.token_bytes(GCM_NONCE_SIZE)
    
    # Create cipher and encrypt
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    
    return nonce, ciphertext


def decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    """
    Decrypt data using AES-256-GCM.
    
    Verifies the authentication tag and decrypts the ciphertext.
    
    Args:
        ciphertext: Encrypted data with authentication tag
        key: 32-byte AES-256 key (same key used for encryption)
        nonce: 12-byte nonce used during encryption
    
    Returns:
        Decrypted plaintext
    
    Raises:
        ValueError: If key size or nonce size is incorrect
        cryptography.exceptions.InvalidTag: If authentication fails
    
    Example:
        >>> key = generate_key()
        >>> nonce, ciphertext = encrypt(b"secret", key)
        >>> plaintext = decrypt(ciphertext, key, nonce)
        >>> assert plaintext == b"secret"
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Key must be {AES_KEY_SIZE} bytes, got {len(key)}")
    
    if len(nonce) != GCM_NONCE_SIZE:
        raise ValueError(f"Nonce must be {GCM_NONCE_SIZE} bytes, got {len(nonce)}")
    
    # Create cipher and decrypt
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    
    return plaintext
