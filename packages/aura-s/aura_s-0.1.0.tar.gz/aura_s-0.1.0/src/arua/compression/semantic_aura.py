"""Semantic header wrapper around ARUA's text compressor.

This module prepends the same 4-byte semantic header used by ARUA's
local semantic compressor (Sa/Sb) in front of payloads produced by
the high-level :mod:`arua.compression` text API.
"""

from __future__ import annotations

from typing import Any

from .. import compression as aura_bridge
from .semantic import (
    CODEC_ID_SA,
    CODEC_ID_SB,
    SA_THRESHOLD,
    SemanticHeader,
)


def aura_semantic_compress(
    text: str,
    codec: str = "auto",
    domain_id: int = 0,
    template_id: int | None = None,
) -> tuple[bytes, dict[str, Any]]:
    """Compress text and prepend a semantic header.

    Args:
        text: UTF-8 text to compress.
        codec: \"auto\", \"Sa\", or \"Sb\" as in the local semantic compressor.
        domain_id: Domain identifier for routing.
        template_id: Optional template id (0-65535).
    """
    data = text.encode("utf-8")
    if codec == "auto":
        codec = "Sa" if len(data) < SA_THRESHOLD else "Sb"

    if codec == "Sa":
        codec_id = CODEC_ID_SA
    elif codec == "Sb":
        codec_id = CODEC_ID_SB
    else:
        raise ValueError(f"unsupported semantic codec for ARUA semantic wrapper: {codec}")

    tid = 0 if template_id is None else int(template_id)
    header = SemanticHeader(codec_id=codec_id, domain_id=domain_id, template_id=tid)

    payload, metadata = aura_bridge.compress_text(text)
    wrapped = header.to_bytes() + payload
    # Adjust compressed_size/ratio in metadata to account for header
    if "original_size" in metadata:
        original_size = metadata["original_size"]
    else:
        original_size = len(data)
    compressed_size = len(wrapped)
    metadata = dict(metadata)
    metadata["compressed_size"] = compressed_size
    metadata["ratio"] = original_size / compressed_size if compressed_size else 1.0
    metadata["semantic_codec"] = codec
    metadata["semantic_domain_id"] = domain_id
    metadata["semantic_template_id"] = tid
    return wrapped, metadata


def aura_semantic_decompress(
    payload: bytes,
) -> tuple[str | bytes, dict[str, Any], SemanticHeader]:
    """Decompress payload produced by :func:`aura_semantic_compress`."""
    header, body = SemanticHeader.from_bytes(bytes(payload))
    text, metadata = aura_bridge.decompress_text(body)
    metadata = dict(metadata)
    metadata["semantic_codec_id"] = header.codec_id
    metadata["semantic_domain_id"] = header.domain_id
    metadata["semantic_template_id"] = header.template_id
    return text, metadata, header
