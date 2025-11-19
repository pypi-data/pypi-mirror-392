"""Semantic Derivative (Sd) helper utilities.

This module implements a minimal byte-wise delta codec. It is intended
to demonstrate Sd behaviour without changing the compact semantic header
format.

Body layout (binary):

    [u8 first][n * i8 delta]

Where:
    value[0]   = first
    value[i>0] = (value[i-1] + delta[i-1]) mod 256
"""

from __future__ import annotations

import struct
from typing import Iterable

_FIRST_STRUCT = struct.Struct(">B")  # unsigned 8-bit
_DELTA_STRUCT = struct.Struct(">b")  # signed 8-bit


def encode_derivative(data: bytes) -> bytes:
    """Encode bytes using a simple derivative scheme."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("encode_derivative() expects a bytes-like object")
    raw = bytes(data)
    if not raw:
        return b""
    out = bytearray()
    out.extend(_FIRST_STRUCT.pack(raw[0]))
    prev = raw[0]
    for b in raw[1:]:
        delta = (b - prev + 256) % 256
        # Map 0–255 to signed range -128..127.
        if delta >= 128:
            delta -= 256
        out.extend(_DELTA_STRUCT.pack(delta))
        prev = b
    return bytes(out)


def decode_derivative(payload: bytes) -> bytes:
    """Decode bytes produced by :func:`encode_derivative`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_derivative() expects a bytes-like object")
    if not payload:
        return b""
    data = memoryview(payload)
    if len(data) < _FIRST_STRUCT.size:
        raise ValueError("Sd payload too short for first byte")
    (first,) = _FIRST_STRUCT.unpack_from(data, 0)
    values = bytearray([first])
    offset = _FIRST_STRUCT.size
    while offset < len(data):
        (delta,) = _DELTA_STRUCT.unpack_from(data, offset)
        offset += _DELTA_STRUCT.size
        prev = values[-1]
        val = (prev + delta) % 256
        values.append(val)
    return bytes(values)

