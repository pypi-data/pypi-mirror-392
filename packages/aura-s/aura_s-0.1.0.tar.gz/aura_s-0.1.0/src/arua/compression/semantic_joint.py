"""Semantic Joint (Sj) codec.

Sj bundles multiple related semantic payloads (e.g. text + vectors, prompt +
context slices) into a single joint unit. This enables multi-modal or multi-part
messages to be compressed and routed together as a cohesive bundle.

The wire format embeds multiple payloads as a compact container alongside
optional compression. This sits above Sa/Sb/Sv/Sw and others as a multi-segment
wrapper, working with Sr to keep a whole joint bundle routed and scheduled
consistently.

Body layout (v1, big-endian):
    [u32 count][count * (u32 length + payload_bytes)]

Each payload is an opaque bytes blob (typically a full semantic payload).

Example:
    # Bundle multiple semantic payloads together
    payload1 = b"first part"
    payload2 = b"second part"
    payload3 = b"third part"
    compressed = compress([payload1, payload2, payload3])
    payloads = decompress(compressed)
    # payloads == [b"first part", b"second part", b"third part"]
"""

from __future__ import annotations

import struct
from typing import Iterable, List

from .core import compress as core_compress
from .core import decompress as core_decompress

_COUNT_STRUCT = struct.Struct(">I")
_LEN_STRUCT = struct.Struct(">I")


def encode_joint(payloads: Iterable[bytes]) -> bytes:
    """Encode multiple payloads into a joint container body."""
    payload_list: List[bytes] = [bytes(p) for p in payloads]
    out = bytearray()
    out.extend(_COUNT_STRUCT.pack(len(payload_list)))
    for p in payload_list:
        out.extend(_LEN_STRUCT.pack(len(p)))
        out.extend(p)
    return bytes(out)


def decode_joint(body: bytes) -> list[bytes]:
    """Decode a joint container body produced by :func:`encode_joint`."""
    data = memoryview(body)
    if len(data) < _COUNT_STRUCT.size:
        raise ValueError("Sj body too short for count header")
    (count,) = _COUNT_STRUCT.unpack_from(data, 0)
    offset = _COUNT_STRUCT.size
    parts: list[bytes] = []
    for _ in range(count):
        if offset + _LEN_STRUCT.size > len(data):
            raise ValueError("Sj body truncated before length")
        (length,) = _LEN_STRUCT.unpack_from(data, offset)
        offset += _LEN_STRUCT.size
        if offset + length > len(data):
            raise ValueError("Sj body truncated before payload bytes")
        parts.append(bytes(data[offset : offset + length]))
        offset += length
    if offset != len(data):
        raise ValueError("extra data at end of Sj body")
    return parts


def compress(payloads: Iterable[bytes]) -> bytes:
    """Compress multiple payloads into a joint container.

    Args:
        payloads: An iterable of byte payloads (typically semantic payloads)
                  to bundle together.

    Returns:
        Compressed joint container with all payloads bundled.

    The wire format is:
        [compressed joint body]

    Where the joint body contains:
        [4-byte count][count * (4-byte length + payload)]

    The entire joint structure is then compressed using the core compressor.
    """
    if not isinstance(payloads, (list, tuple)):
        payloads = list(payloads)

    if not payloads:
        raise ValueError("compress() requires at least one payload")

    for p in payloads:
        if not isinstance(p, (bytes, bytearray)):
            raise TypeError("All payloads must be bytes-like objects")

    # Encode the joint structure
    joint_body = encode_joint(payloads)

    # Compress the entire joint body
    return core_compress(joint_body, method="auto")


def decompress(payload: bytes) -> list[bytes]:
    """Decompress a joint container and extract all bundled payloads.

    Args:
        payload: The compressed joint container.

    Returns:
        A list of the original payloads.

    Raises:
        ValueError: If the payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    # Decompress the joint body
    joint_body = core_decompress(bytes(payload))

    # Decode the joint structure
    return decode_joint(joint_body)

