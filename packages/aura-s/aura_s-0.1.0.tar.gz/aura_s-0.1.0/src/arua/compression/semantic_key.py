"""Semantic Key (Sk) codec.

Sk carries logical keys for entities (user/session/resource IDs, tenancy keys)
separately from content-derived hashes or index positions. This codec focuses
on identity and tenancy rather than compression.

The wire format encodes key metadata as a compact JSON object, then compresses
it using the core compressor. Keys can be used for routing, access control,
caching, and multi-tenancy.

Example:
    data = b"some payload"
    keys = {"user_id": "alice", "session": "xyz123", "tenant": "acme"}
    compressed = compress(data, keys)
    original, metadata = decompress(compressed)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

from .core import compress as core_compress
from .core import decompress as core_decompress


@dataclass(frozen=True)
class KeyMetadata:
    """Logical key metadata for a payload."""

    keys: Dict[str, str]


def encode_keys(meta: KeyMetadata) -> bytes:
    """Encode key metadata into a UTF-8 JSON body."""
    obj = {"keys": meta.keys}
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def decode_keys(payload: bytes) -> KeyMetadata:
    """Decode key metadata from a UTF-8 JSON body."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_keys() expects a bytes-like object")
    try:
        obj = json.loads(bytes(payload).decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sk payload JSON") from exc
    if not isinstance(obj, dict) or "keys" not in obj or not isinstance(
        obj["keys"], dict
    ):
        raise ValueError("Sk payload must contain a 'keys' dict")
    keys: Dict[str, str] = {str(k): str(v) for k, v in obj["keys"].items()}
    return KeyMetadata(keys=keys)


def compress(data: bytes, keys: Dict[str, str] | None = None) -> bytes:
    """Compress data with optional key metadata.

    Args:
        data: The payload to compress.
        keys: Optional dictionary of logical keys (user_id, session, tenant, etc.).
              If None, an empty key set is encoded.

    Returns:
        Compressed payload with embedded key metadata.

    The wire format is:
        [2-byte key_blob_length][key_blob][compressed_data]

    Where key_blob is JSON-encoded keys, and compressed_data is the core
    compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode keys metadata
    if keys is None:
        keys = {}
    meta = KeyMetadata(keys={str(k): str(v) for k, v in keys.items()})
    key_blob = encode_keys(meta)

    # Enforce key blob size limit (64KB max for 2-byte length prefix)
    if len(key_blob) > 0xFFFF:
        raise ValueError("key metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(data, method="auto")

    # Pack: [2-byte length][key_blob][compressed_data]
    key_length = len(key_blob)
    length_bytes = bytes([(key_length >> 8) & 0xFF, key_length & 0xFF])

    return length_bytes + key_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, KeyMetadata]:
    """Decompress an Sk payload and extract key metadata.

    Args:
        payload: The compressed payload with embedded keys.

    Returns:
        A tuple of (decompressed_data, key_metadata).

    Raises:
        ValueError: If the payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)

    # Need at least 2 bytes for length prefix
    if len(payload) < 2:
        raise ValueError("Sk payload too short (need at least 2 bytes)")

    # Read 2-byte key blob length
    key_length = (payload[0] << 8) | payload[1]

    # Validate we have enough data
    if len(payload) < 2 + key_length:
        raise ValueError(
            f"Sk payload truncated: expected {2 + key_length} bytes, got {len(payload)}"
        )

    # Extract key blob and compressed data
    key_blob = payload[2 : 2 + key_length]
    compressed_data = payload[2 + key_length :]

    # Decode keys
    metadata = decode_keys(key_blob)

    # Decompress data
    data = core_decompress(compressed_data)

    return data, metadata

