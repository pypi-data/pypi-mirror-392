"""
Tests for the encryption module.

Tests AES-256-GCM encryption and decryption functionality.
"""

import pytest
from cryptography.exceptions import InvalidTag

from hrcx.crypto import AES_KEY_SIZE, GCM_NONCE_SIZE, decrypt, encrypt, generate_key


class TestKeyGeneration:
    """Tests for generate_key function."""

    def test_generates_correct_size(self):
        """Key should be 32 bytes for AES-256."""
        key = generate_key()
        assert len(key) == AES_KEY_SIZE
        assert len(key) == 32

    def test_generates_different_keys(self):
        """Each call should generate a different key."""
        key1 = generate_key()
        key2 = generate_key()
        assert key1 != key2

    def test_generates_bytes(self):
        """Key should be bytes type."""
        key = generate_key()
        assert isinstance(key, bytes)


class TestEncryption:
    """Tests for encrypt function."""

    def test_encrypts_successfully(self):
        """Basic encryption should work."""
        key = generate_key()
        plaintext = b"Hello, World!"
        nonce, ciphertext = encrypt(plaintext, key)

        assert len(nonce) == GCM_NONCE_SIZE
        assert len(ciphertext) > len(plaintext)  # ciphertext includes auth tag
        assert ciphertext != plaintext

    def test_different_nonces(self):
        """Each encryption should use a different nonce."""
        key = generate_key()
        plaintext = b"test"
        nonce1, ciphertext1 = encrypt(plaintext, key)
        nonce2, ciphertext2 = encrypt(plaintext, key)

        assert nonce1 != nonce2
        assert ciphertext1 != ciphertext2

    def test_empty_plaintext(self):
        """Should be able to encrypt empty data."""
        key = generate_key()
        nonce, ciphertext = encrypt(b"", key)
        assert len(nonce) == GCM_NONCE_SIZE
        assert len(ciphertext) > 0  # auth tag still present

    def test_large_plaintext(self):
        """Should handle large data."""
        key = generate_key()
        plaintext = b"x" * 1_000_000  # 1MB
        nonce, ciphertext = encrypt(plaintext, key)
        assert len(nonce) == GCM_NONCE_SIZE
        assert len(ciphertext) > len(plaintext)

    def test_binary_data(self):
        """Should handle arbitrary binary data."""
        key = generate_key()
        plaintext = bytes(range(256))
        nonce, ciphertext = encrypt(plaintext, key)
        assert len(nonce) == GCM_NONCE_SIZE
        assert ciphertext != plaintext

    def test_rejects_wrong_key_size(self):
        """Should reject keys that aren't 32 bytes."""
        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            encrypt(b"test", b"short_key")

        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            encrypt(b"test", b"x" * 16)  # 16 bytes (AES-128 size)


class TestDecryption:
    """Tests for decrypt function."""

    def test_decrypts_successfully(self):
        """Basic decryption should work."""
        key = generate_key()
        plaintext = b"Hello, World!"
        nonce, ciphertext = encrypt(plaintext, key)

        decrypted = decrypt(ciphertext, key, nonce)
        assert decrypted == plaintext

    def test_empty_plaintext_roundtrip(self):
        """Empty data should roundtrip correctly."""
        key = generate_key()
        plaintext = b""
        nonce, ciphertext = encrypt(plaintext, key)

        decrypted = decrypt(ciphertext, key, nonce)
        assert decrypted == plaintext

    def test_large_plaintext_roundtrip(self):
        """Large data should roundtrip correctly."""
        key = generate_key()
        plaintext = b"x" * 1_000_000  # 1MB
        nonce, ciphertext = encrypt(plaintext, key)

        decrypted = decrypt(ciphertext, key, nonce)
        assert decrypted == plaintext

    def test_binary_data_roundtrip(self):
        """Binary data should roundtrip correctly."""
        key = generate_key()
        plaintext = bytes(range(256))
        nonce, ciphertext = encrypt(plaintext, key)

        decrypted = decrypt(ciphertext, key, nonce)
        assert decrypted == plaintext

    def test_rejects_wrong_key(self):
        """Decryption with wrong key should fail."""
        key1 = generate_key()
        key2 = generate_key()
        plaintext = b"secret"
        nonce, ciphertext = encrypt(plaintext, key1)

        with pytest.raises(InvalidTag):
            decrypt(ciphertext, key2, nonce)

    def test_rejects_wrong_nonce(self):
        """Decryption with wrong nonce should fail."""
        key = generate_key()
        plaintext = b"secret"
        nonce, ciphertext = encrypt(plaintext, key)
        wrong_nonce = generate_key()[:GCM_NONCE_SIZE]

        with pytest.raises(InvalidTag):
            decrypt(ciphertext, key, wrong_nonce)

    def test_rejects_tampered_ciphertext(self):
        """Decryption of tampered ciphertext should fail."""
        key = generate_key()
        plaintext = b"secret"
        nonce, ciphertext = encrypt(plaintext, key)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[0] ^= 0xFF  # flip bits
        tampered = bytes(tampered)

        with pytest.raises(InvalidTag):
            decrypt(tampered, key, nonce)

    def test_rejects_wrong_key_size(self):
        """Should reject keys that aren't 32 bytes."""
        key = generate_key()
        plaintext = b"test"
        nonce, ciphertext = encrypt(plaintext, key)

        with pytest.raises(ValueError, match="Key must be 32 bytes"):
            decrypt(ciphertext, b"short_key", nonce)

    def test_rejects_wrong_nonce_size(self):
        """Should reject nonces that aren't 12 bytes."""
        key = generate_key()
        plaintext = b"test"
        nonce, ciphertext = encrypt(plaintext, key)

        with pytest.raises(ValueError, match="Nonce must be 12 bytes"):
            decrypt(ciphertext, key, b"short")

        with pytest.raises(ValueError, match="Nonce must be 12 bytes"):
            decrypt(ciphertext, key, b"x" * 16)
