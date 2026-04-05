"""Tests for Chitragupta steganography module."""

import pytest


class TestSteganography:
    """Test steganographic data portability."""

    def test_import(self):
        """Module imports without error (dependencies permitting)."""
        try:
            from nyaya_dhwani.steganography import (
                generate_session_key,
                encrypt_data,
                decrypt_data,
                embed_in_image,
                extract_from_image,
                create_portable_export,
            )
            assert generate_session_key is not None
        except ImportError as e:
            pytest.skip(f"Optional dependencies not installed: {e}")

    def test_generate_session_key(self):
        """Session key generation should be deterministic."""
        try:
            from nyaya_dhwani.steganography import generate_session_key
        except ImportError:
            pytest.skip("cryptography not installed")

        key1 = generate_session_key("session123", "secret")
        key2 = generate_session_key("session123", "secret")
        key3 = generate_session_key("session456", "secret")

        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different session = different key
        assert len(key1) == 44  # Base64-encoded 32 bytes

    def test_encrypt_decrypt_roundtrip(self):
        """Encryption and decryption should preserve data."""
        try:
            from nyaya_dhwani.steganography import (
                generate_session_key,
                encrypt_data,
                decrypt_data,
            )
        except ImportError:
            pytest.skip("cryptography not installed")

        key = generate_session_key("test-session")
        original = {
            "chat_history": [["Hello", "Hi there"]],
            "metadata": {"version": "1.0"},
        }

        encrypted = encrypt_data(original, key)
        assert encrypted != str(original).encode()  # Actually encrypted

        decrypted = decrypt_data(encrypted, key)
        assert decrypted == original

    def test_encrypt_with_wrong_key_fails(self):
        """Decryption with wrong key should fail."""
        try:
            from nyaya_dhwani.steganography import (
                generate_session_key,
                encrypt_data,
                decrypt_data,
            )
            from cryptography.fernet import InvalidToken
        except ImportError:
            pytest.skip("cryptography not installed")

        key1 = generate_session_key("session1")
        key2 = generate_session_key("session2")

        encrypted = encrypt_data({"test": "data"}, key1)

        with pytest.raises(InvalidToken):
            decrypt_data(encrypted, key2)

    def test_magic_header(self):
        """Magic header constant should be defined."""
        try:
            from nyaya_dhwani.steganography import MAGIC_HEADER
        except ImportError:
            pytest.skip("steganography module not available")

        assert MAGIC_HEADER == b"CHITRAGUPTA_V1"

    def test_bits_conversion(self):
        """Bit conversion should be reversible."""
        try:
            from nyaya_dhwani.steganography import _text_to_bits, _bits_to_bytes
        except ImportError:
            pytest.skip("steganography module not available")

        original = b"Hello, World!"
        bits = _text_to_bits(original)
        recovered = _bits_to_bytes(bits)

        assert recovered == original

    def test_default_carrier_generation(self):
        """Default carrier image generation."""
        try:
            from nyaya_dhwani.steganography import _generate_default_carrier
        except ImportError:
            pytest.skip("Pillow not installed")

        carrier = _generate_default_carrier()

        assert isinstance(carrier, bytes)
        assert len(carrier) > 1000  # Should be a real image
        # Check PNG magic bytes
        assert carrier[:8] == b'\x89PNG\r\n\x1a\n'


class TestSteganographyIntegration:
    """Integration tests for full embed/extract cycle."""

    def test_embed_extract_cycle(self):
        """Full steganography cycle should work."""
        try:
            from nyaya_dhwani.steganography import (
                create_portable_export,
                extract_from_image,
            )
        except ImportError:
            pytest.skip("steganography dependencies not installed")

        session_id = "test-session-123"
        chat_history = [
            ["What is DPDP Act?", "The DPDP Act 2023 is..."],
            ["My rights?", "You have the right to..."],
        ]

        # Create export
        image_bytes = create_portable_export(
            chat_history=chat_history,
            session_id=session_id,
            metadata={"test": True},
        )

        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 1000

        # Extract
        extracted = extract_from_image(image_bytes, session_id)

        assert extracted["chat_history"] == chat_history
        assert extracted["session_id"] == session_id
        assert "compliance" in extracted
        assert "DPDP" in str(extracted["compliance"])

    def test_extract_wrong_session_fails(self):
        """Extraction with wrong session should fail."""
        try:
            from nyaya_dhwani.steganography import (
                create_portable_export,
                extract_from_image,
            )
            from cryptography.fernet import InvalidToken
        except ImportError:
            pytest.skip("steganography dependencies not installed")

        image_bytes = create_portable_export(
            chat_history=[["Q", "A"]],
            session_id="correct-session",
        )

        with pytest.raises(InvalidToken):
            extract_from_image(image_bytes, "wrong-session")

    def test_non_chitragupta_image_fails(self):
        """Non-Chitragupta images should fail gracefully."""
        try:
            from nyaya_dhwani.steganography import (
                extract_from_image,
                _generate_default_carrier,
            )
        except ImportError:
            pytest.skip("steganography dependencies not installed")

        # Generate a plain carrier without embedded data
        plain_image = _generate_default_carrier()

        with pytest.raises(ValueError) as excinfo:
            extract_from_image(plain_image, "any-session")

        assert "Chitragupta" in str(excinfo.value)
