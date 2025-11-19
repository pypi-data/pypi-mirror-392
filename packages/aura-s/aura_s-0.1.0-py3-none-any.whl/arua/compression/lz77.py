"""Minimal LZ77-style compressor used for tests.

This module implements a simple LZ77-inspired scheme with the following
binary format:

* The stream is a sequence of tokens.
* Each token starts with a 1-byte header:

  - bit 7 (0x80): 0 for literal, 1 for match
  - bits 0-6    : length (1–127)

* Literal token:

  - header: bit7 = 0, len in low 7 bits
  - next ``len`` bytes: literal data

* Match token:

  - header: bit7 = 1, len in low 7 bits (match length)
  - next 2 bytes: big-endian offset (distance back from current output)

The compressor uses a small sliding window with naive search and favors
correctness and simplicity over compression ratio or speed. Tests only
assert round-trip behaviour (``decompress(compress(x)) == x``).
"""

from __future__ import annotations

from typing import Final

WINDOW_SIZE: Final[int] = 4096
MIN_MATCH: Final[int] = 3
MAX_MATCH: Final[int] = 127  # fits in 7 bits


def _find_longest_match(data: bytes, pos: int) -> tuple[int, int]:
    """Find the longest backward match starting at ``pos``.

    Returns:
        (offset, length) where offset > 0 and length >= MIN_MATCH, or
        (0, 0) if no suitable match is found.
    """
    end = len(data)
    window_start = max(0, pos - WINDOW_SIZE)

    best_len = 0
    best_offset = 0

    # Naive search: compare against all possible start positions in window
    for candidate in range(window_start, pos):
        length = 0
        # Compare forward while bytes match and we stay in bounds/limits
        while (
            pos + length < end
            and data[candidate + length] == data[pos + length]
            and length < MAX_MATCH
        ):
            length += 1
        if length >= MIN_MATCH and length > best_len:
            best_len = length
            best_offset = pos - candidate
            if best_len == MAX_MATCH:
                break

    if best_len >= MIN_MATCH and best_offset > 0:
        return best_offset, best_len
    return 0, 0


def compress(data: bytes) -> bytes:
    """Compress ``data`` using a minimal LZ77-style scheme."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    if not data:
        return b""

    src = bytes(data)
    out = bytearray()
    pos = 0
    end = len(src)

    while pos < end:
        offset, length = _find_longest_match(src, pos)

        if length >= MIN_MATCH:
            # Emit match token: header with high bit + length, then 2-byte offset.
            length = min(length, MAX_MATCH)
            header = 0x80 | (length & 0x7F)
            out.append(header)
            out.extend(offset.to_bytes(2, "big"))
            pos += length
        else:
            # Emit single-byte literal token.
            header = 0x01  # literal run of length 1
            out.append(header)
            out.append(src[pos])
            pos += 1

    return bytes(out)


def decompress(payload: bytes) -> bytes:
    """Decompress data produced by :func:`compress`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    if not payload:
        return b""

    data = bytes(payload)
    out = bytearray()
    pos = 0
    end = len(data)

    while pos < end:
        header = data[pos]
        pos += 1
        is_match = bool(header & 0x80)
        length = header & 0x7F
        if length == 0:
            raise ValueError("invalid token length 0")

        if is_match:
            # Need 2 bytes for offset.
            if pos + 2 > end:
                raise ValueError("truncated match token")
            offset = int.from_bytes(data[pos : pos + 2], "big")
            pos += 2
            if offset == 0 or offset > len(out):
                raise ValueError("invalid match offset")
            start = len(out) - offset
            for _ in range(length):
                out.append(out[start])
                start += 1
        else:
            # Literal run.
            if pos + length > end:
                raise ValueError("truncated literal token")
            out.extend(data[pos : pos + length])
            pos += length

    return bytes(out)
