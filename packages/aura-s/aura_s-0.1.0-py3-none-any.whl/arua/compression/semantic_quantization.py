"""Semantic Quantization (Sq) helper utilities.

This module provides a concrete **binary** body format for quantized
numeric vectors. It is intended as a helper for Sq-labelled payloads,
without changing the core semantic header or routing logic.

Binary body layout (big-endian):

    [bits:u8][min:f32][max:f32][length:u32][qbytes...]

Where:
    - ``bits`` is the quantization precision (typically 8).
    - ``min`` / ``max`` are the original float range.
    - ``length`` is the number of quantized values.
    - ``qbytes`` are the raw quantized bytes (one per value for 8-bit).

JSON helpers (`compress` / `decompress`) remain for ergonomics and tests:
they accept/produce JSON float arrays but use the binary body format
under the hood.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
import struct
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class QuantizationMetadata:
    """Metadata describing a simple linear quantization."""

    bits: int
    min_val: float
    max_val: float


_HEADER_STRUCT = struct.Struct(">BffI")  # bits:u8, min:f32, max:f32, length:u32


def _quantize_floats(
    floats: Iterable[float],
    bits: int = 8,
) -> Tuple[bytes, QuantizationMetadata]:
    values: List[float] = [float(v) for v in floats]
    if not values:
        meta = QuantizationMetadata(bits=bits, min_val=0.0, max_val=0.0)
        return b"", meta

    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        # All values equal; encode zeros.
        meta = QuantizationMetadata(bits=bits, min_val=min_val, max_val=max_val)
        return bytes(len(values)), meta

    levels = (1 << bits) - 1
    scale = levels / (max_val - min_val)
    out = bytearray()
    for v in values:
        q = int(round((v - min_val) * scale))
        if q < 0:
            q = 0
        if q > levels:
            q = levels
        out.append(q)
    meta = QuantizationMetadata(bits=bits, min_val=min_val, max_val=max_val)
    return bytes(out), meta


def _dequantize_floats(
    payload: bytes,
    meta: QuantizationMetadata,
) -> List[float]:
    if not payload:
        return []
    if meta.max_val == meta.min_val:
        return [meta.min_val for _ in payload]
    levels = (1 << meta.bits) - 1
    scale = (meta.max_val - meta.min_val) / levels
    return [meta.min_val + b * scale for b in payload]


def encode_quantized_floats(
    floats: Iterable[float],
    bits: int = 8,
) -> bytes:
    """Encode floats into a compact Sq binary body.

    The returned bytes follow the binary layout documented in the module
    docstring: a fixed header describing the quantization followed by
    raw quantized bytes.
    """
    qbytes, meta = _quantize_floats(floats, bits=bits)
    header = _HEADER_STRUCT.pack(meta.bits, float(meta.min_val), float(meta.max_val), len(qbytes))
    return header + qbytes


def decode_quantized_floats(payload: bytes) -> List[float]:
    """Decode floats from a binary Sq body produced by encode_quantized_floats."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_quantized_floats() expects a bytes-like object")
    data = memoryview(payload)
    if len(data) < _HEADER_STRUCT.size:
        raise ValueError("Sq payload too short for header")
    bits, min_val, max_val, length = _HEADER_STRUCT.unpack_from(data, 0)
    if length < 0:
        raise ValueError("Sq payload has negative length")
    expected_size = _HEADER_STRUCT.size + length
    if len(data) != expected_size:
        raise ValueError("Sq payload size does not match encoded length")
    qbytes = data[_HEADER_STRUCT.size : expected_size]
    meta = QuantizationMetadata(bits=int(bits), min_val=float(min_val), max_val=float(max_val))
    return _dequantize_floats(qbytes.tobytes(), meta)


def compress(data: bytes, bits: int = 8) -> bytes:
    """Sq codec: compress a JSON float array via quantization.

    This convenience codec expects ``data`` to be a UTF-8 JSON-encoded
    array of floats, e.g. ``[0.0, 0.5, -0.5]``. It returns a compact
    binary Sq body as produced by :func:`encode_quantized_floats`.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")
    try:
        arr = json.loads(bytes(data).decode("utf-8"))
    except Exception as exc:
        raise ValueError("Sq compress() expects a JSON array of floats") from exc
    if not isinstance(arr, list):
        raise ValueError("Sq compress() expects a JSON array of floats")
    return encode_quantized_floats(arr, bits=bits)


def decompress(payload: bytes) -> bytes:
    """Sq codec: decompress to a JSON float array (UTF-8 bytes)."""
    floats = decode_quantized_floats(payload)
    text = json.dumps(floats, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")
