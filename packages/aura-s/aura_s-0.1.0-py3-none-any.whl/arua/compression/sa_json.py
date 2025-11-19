"""JSON helpers for the Sa (Semantic Atom) codec.

These utilities are intended for tiny JSON payloads that fit comfortably
within the Sa size band. They convert between Python objects, JSON text,
and the binary representation produced by :func:`semantic_compress`.
"""
from __future__ import annotations

import json
from typing import Any

from .semantic import (
    CODEC_ID_SA,
    CODEC_ID_SB,
    SemanticHeader,
    semantic_compress,
    semantic_decompress,
)


def sa_encode_json(
    obj: Any,
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode a small JSON-serializable object using Sa semantics.

    The object is serialized to compact JSON, encoded as UTF-8, and
    wrapped with an Sa semantic header via :func:`semantic_compress`.
    """
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    data = text.encode("utf-8")
    return semantic_compress(data, codec="Sa", domain_id=domain_id, template_id=template_id)


def sa_decode_json(payload: bytes) -> Any:
    """Decode a payload produced by :func:`sa_encode_json`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("sa_decode_json() expects a bytes-like object")

    header, _ = SemanticHeader.from_bytes(bytes(payload))
    if header.codec_id != CODEC_ID_SA:
        raise ValueError(f"expected Sa codec, got codec_id={header.codec_id}")

    data = semantic_decompress(payload)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError("payload is not valid UTF-8 JSON") from exc
    return json.loads(text)


def sb_encode_json(
    obj: Any,
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode a JSON-serializable object using Sb semantics.

    This is identical to :func:`sa_encode_json` except that it uses the
    Sb codec label, which is intended for slightly larger messages
    (e.g. 100 bytes – 1 KiB).
    """
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    data = text.encode("utf-8")
    return semantic_compress(data, codec="Sb", domain_id=domain_id, template_id=template_id)


def sb_decode_json(payload: bytes) -> Any:
    """Decode a payload produced by :func:`sb_encode_json`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("sb_decode_json() expects a bytes-like object")

    header, _ = SemanticHeader.from_bytes(bytes(payload))
    if header.codec_id != CODEC_ID_SB:
        raise ValueError(f"expected Sb codec, got codec_id={header.codec_id}")

    data = semantic_decompress(payload)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError("payload is not valid UTF-8 JSON") from exc
    return json.loads(text)
