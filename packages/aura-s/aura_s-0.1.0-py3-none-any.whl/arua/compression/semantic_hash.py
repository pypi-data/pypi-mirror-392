"""Semantic Hash (Sh) codec.

Sh carries stable content hashes and locality-sensitive signatures without the
full payload. This codec encodes hash algorithm name and digest alongside the
compressed payload, enabling content-addressed storage, deduplication hints,
and similarity-based routing.

The wire format embeds hash metadata (algorithm, digest) as a compact binary
structure alongside the compressed payload. This supports the Su (unique store),
Sm (memory reuse), and routing/similarity filters.

Example:
    data = b"important content"
    compressed = compress(data, algorithm="sha256")
    original, algorithm, digest = decompress(compressed)
    # Can verify: hashlib.sha256(original).digest() == digest
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Tuple

from .core import compress as core_compress
from .core import decompress as core_decompress


@dataclass(frozen=True)
class HashMetadata:
    """Hash metadata for a payload."""

    algorithm: str
    digest: bytes


def encode_hash(data: bytes, algorithm: str = "sha256") -> bytes:
    """Compute and encode a hash for the given data.

    Args:
        data: Bytes to hash.
        algorithm: Name of the hashlib algorithm (default: ``"sha256"``).

    Returns:
        A compact binary payload carrying the algorithm name and digest.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("encode_hash() expects a bytes-like object")
    try:
        h = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"unsupported hash algorithm: {algorithm}") from exc
    h.update(data)
    digest = h.digest()
    alg_bytes = algorithm.encode("ascii")
    if len(alg_bytes) > 255 or len(digest) > 255:
        raise ValueError("algorithm name or digest too long for prototype format")
    out = bytearray()
    out.append(len(alg_bytes))
    out.extend(alg_bytes)
    out.append(len(digest))
    out.extend(digest)
    return bytes(out)


def decode_hash(payload: bytes) -> Tuple[str, bytes]:
    """Decode an encoded hash payload into ``(algorithm, digest)``."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_hash() expects a bytes-like object")
    data = memoryview(payload)
    if len(data) < 2:
        raise ValueError("payload too short for encoded hash")
    alg_len = data[0]
    if len(data) < 1 + alg_len + 1:
        raise ValueError("payload truncated while reading algorithm name")
    alg_start = 1
    alg_end = alg_start + alg_len
    alg_name = bytes(data[alg_start:alg_end]).decode("ascii")
    digest_len = data[alg_end]
    digest_start = alg_end + 1
    digest_end = digest_start + digest_len
    if len(data) != digest_end:
        raise ValueError("payload size does not match encoded digest length")
    digest = bytes(data[digest_start:digest_end])
    return alg_name, digest


def verify_hash(data: bytes, payload: bytes) -> bool:
    """Verify that the encoded hash payload matches the given data."""
    alg, digest = decode_hash(payload)
    try:
        h = hashlib.new(alg)
    except ValueError:
        return False
    h.update(data)
    return h.digest() == digest


def compress(data: bytes, algorithm: str = "sha256") -> bytes:
    """Compress data and embed content hash metadata.

    Args:
        data: The payload to compress.
        algorithm: Hash algorithm to use (default: "sha256").
                   Supported: sha256, sha512, sha1, md5, blake2b, blake2s, etc.

    Returns:
        Compressed payload with embedded hash metadata.

    The wire format is:
        [2-byte hash_blob_length][hash_blob][compressed_data]

    Where hash_blob is the encoded hash (algorithm + digest), and
    compressed_data is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Compute and encode hash
    hash_blob = encode_hash(data, algorithm=algorithm)

    # Enforce hash blob size limit (64KB max for 2-byte length prefix)
    if len(hash_blob) > 0xFFFF:
        raise ValueError("hash metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(data, method="auto")

    # Pack: [2-byte length][hash_blob][compressed_data]
    hash_length = len(hash_blob)
    length_bytes = bytes([(hash_length >> 8) & 0xFF, hash_length & 0xFF])

    return length_bytes + hash_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, str, bytes]:
    """Decompress an Sh payload and extract hash metadata.

    Args:
        payload: The compressed payload with embedded hash.

    Returns:
        A tuple of (decompressed_data, algorithm, digest).

    Raises:
        ValueError: If the payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)

    # Need at least 2 bytes for length prefix
    if len(payload) < 2:
        raise ValueError("Sh payload too short (need at least 2 bytes)")

    # Read 2-byte hash blob length
    hash_length = (payload[0] << 8) | payload[1]

    # Validate we have enough data
    if len(payload) < 2 + hash_length:
        raise ValueError(
            f"Sh payload truncated: expected {2 + hash_length} bytes, got {len(payload)}"
        )

    # Extract hash blob and compressed data
    hash_blob = payload[2 : 2 + hash_length]
    compressed_data = payload[2 + hash_length :]

    # Decode hash
    algorithm, digest = decode_hash(hash_blob)

    # Decompress data
    data = core_decompress(compressed_data)

    return data, algorithm, digest

