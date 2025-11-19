"""Semantic Pattern (Sp) codec.

Sp encodes pattern-based structured data with a template string and field values.
This is useful for log messages, formatted strings, and structured events where
the pattern provides a template and fields contain the variable data.

The wire format embeds pattern metadata as JSON alongside compressed data:
    [2-byte pattern_blob_length][pattern_blob][compressed_data]

Body layout (UTF-8 JSON):
    {
        "pattern": "<pattern string>",
        "fields": {"name": "value", ...}
    }

Example:
    pattern = "User {user_id} logged in from {ip_address}"
    fields = {"user_id": "alice", "ip_address": "192.168.1.100"}
    compressed = compress(b"event data", pattern=pattern, fields=fields)
    data, decoded_pattern, decoded_fields = decompress(compressed)
"""

from __future__ import annotations

import json
import struct
from typing import Any, Dict, List, Tuple

from .core import compress as core_compress
from .core import decompress as core_decompress

_SLOT_HEADER_STRUCT = struct.Struct(">IH")  # pattern_id:u32, slot_count:u16

_SLOT_NULL = 0
_SLOT_BOOL = 1
_SLOT_INT = 2
_SLOT_FLOAT = 3
_SLOT_STR = 4
_SLOT_BYTES = 5


def encode_pattern(pattern: str, fields: Dict[str, Any]) -> bytes:
    """Encode a pattern and field mapping into a UTF-8 JSON body."""
    obj = {"pattern": pattern, "fields": fields}
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def decode_pattern(payload: bytes) -> Tuple[str, Dict[str, Any]]:
    """Decode a pattern body back into (pattern, fields)."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_pattern() expects a bytes-like object")
    try:
        obj = json.loads(bytes(payload).decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sp payload JSON") from exc
    if not isinstance(obj, dict) or "pattern" not in obj or "fields" not in obj:
        raise ValueError("Sp payload must contain 'pattern' and 'fields' keys")
    pattern = str(obj["pattern"])
    if not isinstance(obj["fields"], dict):
        raise ValueError("Sp 'fields' must be a JSON object")
    fields: Dict[str, Any] = dict(obj["fields"])
    return pattern, fields


def encode_pattern_slots(pattern_id: int, slots: List[Any]) -> bytes:
    """Encode a pattern id and ordered slot values into a compact binary body.

    This helper is an experimental building block for a binary Sp body.
    It does not change the existing JSON-based encode/decode helpers.
    """
    if pattern_id < 0:
        raise ValueError("pattern_id must be non-negative")
    slot_count = len(slots)
    if slot_count > 0xFFFF:
        raise ValueError("too many slots for Sp body")
    out = bytearray()
    out.extend(_SLOT_HEADER_STRUCT.pack(pattern_id, slot_count))
    for value in slots:
        if value is None:
            out.append(_SLOT_NULL)
        elif isinstance(value, bool):
            out.append(_SLOT_BOOL)
            out.append(1 if value else 0)
        elif isinstance(value, int):
            out.append(_SLOT_INT)
            out.extend(int(value).to_bytes(8, "big", signed=True))
        elif isinstance(value, float):
            out.append(_SLOT_FLOAT)
            out.extend(struct.pack(">d", float(value)))
        elif isinstance(value, str):
            data = value.encode("utf-8")
            out.append(_SLOT_STR)
            out.extend(len(data).to_bytes(4, "big"))
            out.extend(data)
        elif isinstance(value, (bytes, bytearray)):
            data = bytes(value)
            out.append(_SLOT_BYTES)
            out.extend(len(data).to_bytes(4, "big"))
            out.extend(data)
        else:
            raise TypeError(f"unsupported slot type for Sp: {type(value)!r}")
    return bytes(out)


def decode_pattern_slots(payload: bytes) -> Tuple[int, List[Any]]:
    """Decode a binary Sp slots body produced by encode_pattern_slots."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_pattern_slots() expects a bytes-like object")
    data = memoryview(payload)
    if len(data) < _SLOT_HEADER_STRUCT.size:
        raise ValueError("Sp slots payload too short for header")
    pattern_id, slot_count = _SLOT_HEADER_STRUCT.unpack_from(data, 0)
    offset = _SLOT_HEADER_STRUCT.size
    slots: List[Any] = []
    for _ in range(slot_count):
        if offset >= len(data):
            raise ValueError("Sp slots payload truncated before slot tag")
        tag = data[offset]
        offset += 1
        if tag == _SLOT_NULL:
            slots.append(None)
        elif tag == _SLOT_BOOL:
            if offset >= len(data):
                raise ValueError("Sp slots payload truncated in bool slot")
            slots.append(bool(data[offset]))
            offset += 1
        elif tag == _SLOT_INT:
            if offset + 8 > len(data):
                raise ValueError("Sp slots payload truncated in int slot")
            raw = bytes(data[offset : offset + 8])
            offset += 8
            slots.append(int.from_bytes(raw, "big", signed=True))
        elif tag == _SLOT_FLOAT:
            if offset + 8 > len(data):
                raise ValueError("Sp slots payload truncated in float slot")
            (val,) = struct.unpack_from(">d", data, offset)
            offset += 8
            slots.append(float(val))
        elif tag in (_SLOT_STR, _SLOT_BYTES):
            if offset + 4 > len(data):
                raise ValueError("Sp slots payload truncated before length")
            length = int.from_bytes(data[offset : offset + 4], "big")
            offset += 4
            if offset + length > len(data):
                raise ValueError("Sp slots payload length out of range")
            raw = bytes(data[offset : offset + length])
            offset += length
            if tag == _SLOT_STR:
                slots.append(raw.decode("utf-8"))
            else:
                slots.append(raw)
        else:
            raise ValueError(f"unknown Sp slot tag: {tag}")
    return pattern_id, slots


def compress(
    data: bytes, pattern: str = "", fields: Dict[str, Any] | None = None
) -> bytes:
    """Compress data with optional pattern metadata.

    Args:
        data: The payload to compress.
        pattern: Template/pattern string (e.g., log format, template).
        fields: Dictionary of field names to values for the pattern.
                If None, an empty fields dict is encoded.

    Returns:
        Compressed payload with embedded pattern metadata.

    The wire format is:
        [2-byte pattern_blob_length][pattern_blob][compressed_data]

    Where pattern_blob is JSON-encoded pattern and fields metadata,
    and compressed_data is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode pattern metadata
    if fields is None:
        fields = {}
    pattern_blob = encode_pattern(pattern, fields)

    # Enforce pattern blob size limit (64KB max for 2-byte length prefix)
    if len(pattern_blob) > 0xFFFF:
        raise ValueError("pattern metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(bytes(data), method="auto")

    # Pack: [2-byte length][pattern_blob][compressed_data]
    pattern_length = len(pattern_blob)
    length_bytes = bytes([(pattern_length >> 8) & 0xFF, pattern_length & 0xFF])

    return length_bytes + pattern_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, str, Dict[str, Any]]:
    """Decompress an Sp payload and extract pattern metadata.

    Args:
        payload: The compressed payload with embedded pattern metadata.

    Returns:
        A tuple of (decompressed_data, pattern, fields).

    Raises:
        TypeError: If payload is not bytes-like.
        ValueError: If payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = bytes(payload)
    if len(data) < 2:
        raise ValueError("Sp payload too short for length header")

    # Read 2-byte pattern blob length
    pattern_length = (data[0] << 8) | data[1]

    # Validate we have enough data
    if len(data) < 2 + pattern_length:
        raise ValueError("Sp payload truncated before pattern blob")

    # Extract pattern blob and compressed data
    pattern_blob = data[2 : 2 + pattern_length]
    compressed_data = data[2 + pattern_length :]

    # Decode pattern metadata
    pattern, fields = decode_pattern(pattern_blob)

    # Decompress data
    decompressed_data = core_decompress(compressed_data)

    return decompressed_data, pattern, fields
