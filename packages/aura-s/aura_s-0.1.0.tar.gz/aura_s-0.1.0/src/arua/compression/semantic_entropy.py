"""Semantic Entropy (Se)

Se classifies payloads into entropy buckets and applies a compression
strategy accordingly. The primary purpose is to encode entropy metadata
and choose a matching core method (e.g., aggressive compression for
low-entropy data and fast compression for high-entropy data).

This file is a CPU fallback that computes the entropy estimate and then
invokes core compression with a suitable method for each case.
"""
from __future__ import annotations

import math
import zlib

from .core import compress as core_compress, decompress as core_decompress


def _shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    length = len(data)
    ent = 0.0
    for val in freq.values():
        p = val / length
        ent -= p * math.log2(p)
    return ent


def _bucket_from_entropy(entropy: float) -> int:
    """Return a coarse bucket from 0..3 based on entropy.

    0: very low entropy
    1: low
    2: medium
    3: high
    """
    if entropy < 2.0:
        return 0
    if entropy < 3.0:
        return 1
    if entropy < 4.0:
        return 2
    return 3


def compress(data: bytes) -> bytes:
    """Entropy-aware compress: choose the core method based on entropy.

    For now, use these rules:
    - bucket 0..1 => core auto (favor ratio)
    - bucket 2   => core auto (balanced)
    - bucket 3   => core uncompressed (avoid expanding CPU work)

    Note: A real Se implementation would include entropy metadata in a
    side-channel header; for now, only pick the backend method.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    ent = _shannon_entropy(data)
    bucket = _bucket_from_entropy(ent)

    if bucket >= 3:
        # High entropy; returning uncompressed or rle-like strategy
        method = "uncompressed"
    else:
        method = "auto"

    return core_compress(data, method=method)


def decompress(payload: bytes) -> bytes:
    return core_decompress(payload)
