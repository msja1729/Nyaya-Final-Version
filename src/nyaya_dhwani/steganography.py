"""Chitragupta's Secret: Steganographic data portability.

This module implements LSB (Least Significant Bit) steganography to:
- Embed encrypted chat history into carrier images
- Extract and decrypt chat history from steganographic images
- Fulfill DPDP Act's "Right to Data Portability" in a secure way

The user downloads what appears to be a normal PNG image, but it contains
their encrypted legal consultation history.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import os
import struct
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Magic header to identify Chitragupta-encoded images
MAGIC_HEADER = b"CHITRAGUPTA_V1"


def _get_fernet():
    """Lazily import cryptography.fernet."""
    try:
        from cryptography.fernet import Fernet
        return Fernet
    except ImportError as e:
        raise ImportError(
            "Install cryptography: pip install cryptography"
        ) from e


def _get_pil():
    """Lazily import PIL."""
    try:
        from PIL import Image
        return Image
    except ImportError as e:
        raise ImportError(
            "Install Pillow: pip install Pillow"
        ) from e


def generate_session_key(session_id: str, secret: str | None = None) -> bytes:
    """Generate a Fernet key from session ID and optional secret.

    Args:
        session_id: Unique session identifier
        secret: Optional additional secret (env var or user-provided)

    Returns:
        32-byte Fernet-compatible key (base64 encoded)
    """
    secret = secret or os.environ.get("CHITRAGUPTA_SECRET", "nyaya-sahayak-2024")
    combined = f"{session_id}:{secret}"
    # SHA256 to get 32 bytes, then base64 encode for Fernet
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)


def encrypt_data(data: dict[str, Any], key: bytes) -> bytes:
    """Encrypt JSON-serializable data using Fernet.

    Args:
        data: Dictionary to encrypt (chat history, metadata)
        key: Fernet-compatible key (from generate_session_key)

    Returns:
        Encrypted bytes
    """
    Fernet = _get_fernet()
    json_bytes = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    compressed = zlib.compress(json_bytes, level=9)
    f = Fernet(key)
    return f.encrypt(compressed)


def decrypt_data(encrypted: bytes, key: bytes) -> dict[str, Any]:
    """Decrypt data encrypted with encrypt_data.

    Args:
        encrypted: Encrypted bytes
        key: Fernet key used for encryption

    Returns:
        Original dictionary
    """
    Fernet = _get_fernet()
    f = Fernet(key)
    compressed = f.decrypt(encrypted)
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes.decode("utf-8"))


def _text_to_bits(data: bytes) -> list[int]:
    """Convert bytes to list of bits."""
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _bits_to_bytes(bits: list[int]) -> bytes:
    """Convert list of bits back to bytes."""
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bits):
                byte = (byte << 1) | bits[i + j]
            else:
                byte = byte << 1
        bytes_list.append(byte)
    return bytes(bytes_list)


def embed_in_image(
    carrier_image: bytes | str | Path,
    data: dict[str, Any],
    session_id: str,
    output_format: str = "PNG",
) -> bytes:
    """Embed encrypted data into a carrier image using LSB steganography.

    Args:
        carrier_image: Path to image file or raw image bytes
        data: Dictionary to embed (chat history, etc.)
        session_id: Session ID for key generation
        output_format: Output image format (PNG recommended)

    Returns:
        Image bytes with embedded data
    """
    Image = _get_pil()

    # Load carrier image
    if isinstance(carrier_image, (str, Path)):
        img = Image.open(carrier_image)
    else:
        img = Image.open(io.BytesIO(carrier_image))

    # Convert to RGB if necessary
    if img.mode != "RGB":
        img = img.convert("RGB")

    pixels = np.array(img, dtype=np.uint8)
    height, width, channels = pixels.shape
    max_bytes = (height * width * channels) // 8

    # Encrypt the data
    key = generate_session_key(session_id)
    encrypted = encrypt_data(data, key)

    # Build payload: MAGIC + length (4 bytes) + encrypted data
    payload = MAGIC_HEADER + struct.pack(">I", len(encrypted)) + encrypted

    if len(payload) > max_bytes - 100:  # Leave some margin
        raise ValueError(
            f"Data too large for carrier image. "
            f"Need {len(payload)} bytes, image can hold {max_bytes} bytes. "
            f"Use a larger image or reduce chat history."
        )

    # Convert payload to bits
    bits = _text_to_bits(payload)

    # Embed bits into LSB of pixel values
    flat_pixels = pixels.flatten()
    for i, bit in enumerate(bits):
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | bit

    # Reshape and create output image
    stego_pixels = flat_pixels.reshape(height, width, channels)
    stego_img = Image.fromarray(stego_pixels.astype(np.uint8), mode="RGB")

    # Save to bytes
    output = io.BytesIO()
    stego_img.save(output, format=output_format)
    output.seek(0)

    logger.info("Chitragupta: Embedded %d bytes into image", len(payload))
    return output.read()


def extract_from_image(
    stego_image: bytes | str | Path,
    session_id: str,
) -> dict[str, Any]:
    """Extract and decrypt data from a steganographic image.

    Args:
        stego_image: Path to image file or raw image bytes
        session_id: Session ID for key generation (must match embedding)

    Returns:
        Decrypted dictionary (chat history, etc.)
    """
    Image = _get_pil()

    # Load stego image
    if isinstance(stego_image, (str, Path)):
        img = Image.open(stego_image)
    else:
        img = Image.open(io.BytesIO(stego_image))

    if img.mode != "RGB":
        img = img.convert("RGB")

    pixels = np.array(img, dtype=np.uint8)
    flat_pixels = pixels.flatten()

    # Extract LSBs
    bits = [p & 1 for p in flat_pixels]

    # Convert first part to bytes to find magic header
    header_bits = bits[:len(MAGIC_HEADER) * 8]
    header_bytes = _bits_to_bytes(header_bits)

    if header_bytes != MAGIC_HEADER:
        raise ValueError(
            "This image doesn't contain Chitragupta data. "
            "Make sure you're using an image exported from Nyaya-Sahayak."
        )

    # Extract length (4 bytes after header)
    length_start = len(MAGIC_HEADER) * 8
    length_bits = bits[length_start:length_start + 32]
    length_bytes = _bits_to_bytes(length_bits)
    data_length = struct.unpack(">I", length_bytes)[0]

    # Extract encrypted data
    data_start = length_start + 32
    data_bits = bits[data_start:data_start + data_length * 8]
    encrypted = _bits_to_bytes(data_bits)

    # Decrypt
    key = generate_session_key(session_id)
    return decrypt_data(encrypted, key)


def create_portable_export(
    chat_history: list[list[str]],
    session_id: str,
    carrier_image: bytes | str | Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> bytes:
    """Create a portable data export with chat history embedded in an image.

    Args:
        chat_history: List of [user_message, assistant_response] pairs
        session_id: Session identifier
        carrier_image: Custom carrier image, or None for default
        metadata: Additional metadata to include

    Returns:
        PNG image bytes with embedded encrypted chat history
    """
    # Build export data
    export_data = {
        "version": "1.0",
        "exported_at": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "chat_history": chat_history,
        "metadata": metadata or {},
        "compliance": {
            "act": "Digital Personal Data Protection Act 2023",
            "right": "Right to Data Portability (Section 13)",
            "note": "This export fulfills your right to receive your personal data in a portable format.",
        },
    }

    # Use default carrier if none provided
    if carrier_image is None:
        carrier_image = _generate_default_carrier()

    return embed_in_image(carrier_image, export_data, session_id)


def _generate_default_carrier() -> bytes:
    """Generate a default carrier image (scales of justice theme)."""
    Image = _get_pil()

    # Create a gradient background with legal theme colors
    width, height = 800, 600
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Create a gradient (deep blue to gold)
    for y in range(height):
        for x in range(width):
            # Gradient from dark blue to lighter
            r = int(13 + (x / width) * 30)
            g = int(27 + (x / width) * 50)
            b = int(62 + (y / height) * 60)
            # Add some noise for better steganography
            noise = np.random.randint(-5, 6)
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            pixels[x, y] = (r, g, b)

    # Convert to bytes
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output.read()


def import_from_image(
    image_path: str | Path | bytes,
    session_id: str,
) -> tuple[list[list[str]], dict[str, Any]]:
    """Import chat history from a Chitragupta-encoded image.

    Args:
        image_path: Path to the image file or image bytes
        session_id: Session ID used when exporting

    Returns:
        (chat_history, metadata) tuple
    """
    data = extract_from_image(image_path, session_id)

    chat_history = data.get("chat_history", [])
    metadata = {
        "exported_at": data.get("exported_at"),
        "original_session": data.get("session_id"),
        "version": data.get("version"),
        "compliance": data.get("compliance"),
        **data.get("metadata", {}),
    }

    return chat_history, metadata
