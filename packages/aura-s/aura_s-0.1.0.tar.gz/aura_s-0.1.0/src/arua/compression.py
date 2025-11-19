"""High-level text compression API for ARUA.

This module provides a small, documented interface for compressing and
decompressing UTF-8 text on top of the internal ARUA core compressor.

It intentionally does not depend on the external AURA repository so that
the PyPI package can be installed and used without extra system setup.
"""

from __future__ import annotations

from typing import Any

from .compression.core import compress as core_compress_fallback
from .compression.core import decompress as core_decompress_fallback


def compress_text(text: str) -> tuple[bytes, dict[str, Any]]:
    """Compress a UTF-8 text string using the ARUA core compressor.

    Returns:
        A tuple ``(compressed_bytes, metadata)`` where:
            * ``compressed_bytes`` is the full wire payload (method byte +
              compressed body) produced by :mod:`arua.compression.core`.
            * ``metadata`` is a minimal dict describing the compression
              ratio and method used.
    """
    data = text.encode("utf-8")
    payload = core_compress_fallback(data, method="auto")
    metadata = {
        "original_size": len(data),
        "compressed_size": len(payload),
        "ratio": len(data) / len(payload) if len(payload) else 1.0,
        "method": "core_auto",
    }
    return payload, metadata


def decompress_text(data: bytes) -> tuple[str | bytes, dict[str, Any]]:
    """Decompress a payload previously produced by :func:`compress_text`.

    Returns:
        A tuple ``(plaintext, metadata)``.

        The plaintext will be:
            * ``str`` for UTF-8 text inputs, or
            * ``bytes`` for binary inputs, depending on how AURA encoded it.
    """
    out = core_decompress_fallback(data)
    try:
        text_out: str | bytes = out.decode("utf-8")
    except UnicodeDecodeError:
        text_out = out
    metadata = {"method": "core_auto"}
    return text_out, metadata
