"""Semantic Vector (Sv) codec.

Sv encodes vector/embedding metadata alongside compressed data. This codec
is designed for semantic vectors and dense embeddings, storing vector metadata
(dimension, model info) separately from the quantized vector data.

The wire format embeds vector metadata as JSON alongside compressed vector data:
    [2-byte metadata_blob_length][metadata_blob][compressed_vector_data]

Example:
    vec_data = b"\\x00\\x00\\x00\\x03..."  # encoded vector
    metadata = {"dimension": 384, "model": "all-MiniLM-L6-v2", "dtype": "float32"}
    compressed = compress(vec_data, metadata=metadata)
    data, decoded_metadata = decompress(compressed)
"""

from __future__ import annotations

import json
import struct
import zlib
from typing import Any, Dict, Iterable, List

from .core import compress as core_compress
from .core import decompress as core_decompress

_LENGTH_STRUCT = struct.Struct(">I")  # unsigned 32-bit big-endian
_COMPONENT_STRUCT = struct.Struct(">h")  # signed 16-bit big-endian
_MAX_I16 = 32767
_MIN_I16 = -32768


def _quantize_component(value: float) -> int:
    """Quantize a float in roughly [-1, 1] into a signed 16-bit integer."""
    if value > 1.0:
        value = 1.0
    elif value < -1.0:
        value = -1.0
    scaled = int(round(value * _MAX_I16))
    if scaled > _MAX_I16:
        scaled = _MAX_I16
    if scaled < _MIN_I16:
        scaled = _MIN_I16
    return scaled


def encode_vector(vec: Iterable[float]) -> bytes:
    """Encode a semantic vector into a compact binary representation.

    Args:
        vec: Iterable of floats, typically in the range [-1.0, 1.0].

    Returns:
        Bytes payload with a 4-byte length prefix followed by signed
        16-bit quantized components.
    """
    components: List[float] = list(vec)
    length = len(components)
    out = bytearray()
    out.extend(_LENGTH_STRUCT.pack(length))
    for value in components:
        q = _quantize_component(float(value))
        out.extend(_COMPONENT_STRUCT.pack(q))
    return bytes(out)


def decode_vector(payload: bytes) -> list[float]:
    """Decode a semantic vector from the binary representation.

    Args:
        payload: Bytes produced by :func:`encode_vector`.

    Returns:
        List of floats reconstructed from the quantized representation.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_vector() expects a bytes-like object")
    data = memoryview(payload)
    if len(data) < _LENGTH_STRUCT.size:
        raise ValueError("payload too short for vector length")
    (length,) = _LENGTH_STRUCT.unpack_from(data, 0)
    expected_size = _LENGTH_STRUCT.size + length * _COMPONENT_STRUCT.size
    if len(data) != expected_size:
        raise ValueError("payload size does not match encoded length")
    offset = _LENGTH_STRUCT.size
    result: list[float] = []
    for _ in range(length):
        (q,) = _COMPONENT_STRUCT.unpack_from(data, offset)
        offset += _COMPONENT_STRUCT.size
        # Dequantize back into approximately [-1, 1]
        result.append(q / _MAX_I16)
    return result


def compress_from_floats(floats: Iterable[float]) -> bytes:
    """Quantize and compress a vector for transport/storage."""
    raw = encode_vector(floats)
    return zlib.compress(raw, level=6)


def decompress_to_floats(payload: bytes) -> list[float]:
    """Decompress and decode a vector previously produced by compress_from_floats."""
    raw = zlib.decompress(payload)
    return decode_vector(raw)


def compress_from_json_array(json_bytes: bytes) -> bytes:
    """Parse a JSON array of floats and compress it using compress_from_floats."""
    arr = json.loads(json_bytes.decode("utf-8"))
    return compress_from_floats(arr)


def serialize_compressed_vector(payload: bytes) -> bytes:
    """Identity helper kept for compatibility with prototype tests."""
    return payload


def parse_compressed_vector(payload: bytes) -> list[float]:
    """Inverse of serialize_compressed_vector + compress_from_floats."""
    return decompress_to_floats(payload)


def compress(data: bytes, metadata: Dict[str, Any] | None = None) -> bytes:
    """Compress vector data with optional metadata.

    Args:
        data: The vector payload to compress (typically encoded vector).
        metadata: Optional dictionary of vector metadata (dimension, model, dtype, etc.).
                  If None, an empty metadata dict is encoded.

    Returns:
        Compressed payload with embedded vector metadata.

    The wire format is:
        [2-byte metadata_blob_length][metadata_blob][compressed_data]

    Where metadata_blob is JSON-encoded vector metadata, and compressed_data
    is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode vector metadata
    if metadata is None:
        metadata = {}
    metadata_blob = json.dumps(metadata, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    # Enforce metadata blob size limit (64KB max for 2-byte length prefix)
    if len(metadata_blob) > 0xFFFF:
        raise ValueError("vector metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(bytes(data), method="auto")

    # Pack: [2-byte length][metadata_blob][compressed_data]
    metadata_length = len(metadata_blob)
    length_bytes = bytes([(metadata_length >> 8) & 0xFF, metadata_length & 0xFF])

    return length_bytes + metadata_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, Dict[str, Any]]:
    """Decompress an Sv payload and extract vector metadata.

    Args:
        payload: The compressed payload with embedded vector metadata.

    Returns:
        A tuple of (decompressed_data, metadata).

    Raises:
        TypeError: If payload is not bytes-like.
        ValueError: If payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = bytes(payload)
    if len(data) < 2:
        raise ValueError("Sv payload too short for length header")

    # Read 2-byte metadata blob length
    metadata_length = (data[0] << 8) | data[1]

    # Validate we have enough data
    if len(data) < 2 + metadata_length:
        raise ValueError("Sv payload truncated before metadata blob")

    # Extract metadata blob and compressed data
    metadata_blob = data[2 : 2 + metadata_length]
    compressed_data = data[2 + metadata_length :]

    # Decode vector metadata
    try:
        metadata = json.loads(metadata_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sv payload JSON") from exc

    if not isinstance(metadata, dict):
        raise ValueError("Sv payload must contain a JSON object")

    # Decompress data
    decompressed_data = core_decompress(compressed_data)

    return decompressed_data, metadata
