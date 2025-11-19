"""Convenience helpers for working with semantic compression.

These helpers sit on top of the Sa/Sb semantic codecs and JSON helpers
to provide one-shot encode/decode operations that are ergonomic for
typical application code.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from .sa_json import sa_encode_json, sa_decode_json, sb_encode_json, sb_decode_json
from .semantic import SemanticHeader, semantic_compress, semantic_decompress
from .semantic_index import IndexMetadata, encode_index, decode_index
from .semantic_joint import encode_joint, decode_joint
from .semantic_key import KeyMetadata, encode_keys, decode_keys
from .semantic_pattern import encode_pattern, decode_pattern
from .semantic_quantization import encode_quantized_floats, decode_quantized_floats
from .semantic_plans import SemanticPlan, decode_payload_to_plan
from .semantic_table import TableSchema, TableColumn, encode_table, decode_table
from .semantic_stream import encode_wave, decode_wave
from .semantic_vector import encode_vector, decode_vector
from ..templates import TemplateLibrary, Template

__all__ = [
    "encode_semantic_text",
    "decode_semantic_text",
    "encode_with_template",
    "decode_with_template",
    "parse_semantic_payload",
    "encode_semantic_vector",
    "decode_semantic_vector",
    "encode_semantic_stream",
    "decode_semantic_stream",
    "encode_semantic_index",
    "decode_semantic_index",
    "encode_semantic_table",
    "decode_semantic_table",
    "encode_semantic_joint",
    "decode_semantic_joint",
    "encode_semantic_keys",
    "decode_semantic_keys",
    "encode_semantic_pattern",
    "decode_semantic_pattern",
    "encode_semantic_quantized_floats",
    "decode_semantic_quantized_floats",
    "encode_chat_completion_response",
    "decode_chat_completion_response",
]


def encode_semantic_text(
    data: str | bytes,
    codec: str = "auto",
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode text or bytes with a semantic header.

    Args:
        data: Text (str) or raw bytes to compress.
        codec: Semantic codec label (\"auto\", \"Sa\", \"Sb\", ...).
        domain_id: Domain identifier to embed in the header.
        template_id: Optional template id; None encodes as 0.
    """
    if isinstance(data, str):
        raw = data.encode("utf-8")
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
    else:
        raise TypeError("encode_semantic_text() expects str or bytes-like input")
    return semantic_compress(raw, codec=codec, domain_id=domain_id, template_id=template_id)


def decode_semantic_text(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[str | bytes, SemanticHeader, SemanticPlan]:
    """Decode a semantic payload into text/bytes and a plan.

    Returns:
        (decoded_text_or_bytes, header, plan)
    """
    header, plan, core_payload = decode_payload_to_plan(payload, templates=templates)
    raw = semantic_decompress(payload)
    # raw is already the original bytes; try to decode to str but fall back to bytes.
    if isinstance(raw, bytes):
        try:
            text_or_bytes: str | bytes = raw.decode("utf-8")
        except UnicodeDecodeError:
            text_or_bytes = raw
    else:
        text_or_bytes = raw
    return text_or_bytes, header, plan


def encode_with_template(
    obj: Any,
    domain_id: int,
    template_id: int,
    codec: str = "auto",
) -> bytes:
    """Encode a JSON-serializable object with a semantic template hint."""
    # Use Sa/Sb JSON helpers based on codec label for clarity.
    if codec == "Sa":
        return sa_encode_json(obj, domain_id=domain_id, template_id=template_id)
    if codec == "Sb":
        return sb_encode_json(obj, domain_id=domain_id, template_id=template_id)
    # Fallback: choose helper based on size.
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    encoded = text.encode("utf-8")
    chosen = "Sa" if len(encoded) < 100 else "Sb"
    if chosen == "Sa":
        return sa_encode_json(obj, domain_id=domain_id, template_id=template_id)
    return sb_encode_json(obj, domain_id=domain_id, template_id=template_id)


def decode_with_template(
    payload: bytes,
    templates: TemplateLibrary,
) -> Tuple[Any, Template | None]:
    """Decode a semantic JSON payload and look up its template record."""
    header, plan, core_payload = decode_payload_to_plan(payload, templates=templates)
    # Decide Sa vs Sb by inspecting codec id.
    if header.codec_id == 0x01:  # Sa
        obj = sa_decode_json(payload)
    elif header.codec_id == 0x02:  # Sb
        obj = sb_decode_json(payload)
    else:
        # Fallback: treat as generic semantic-compressed UTF-8 JSON.
        raw = semantic_decompress(payload)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError("payload is not valid UTF-8 JSON") from exc
        obj = json.loads(text)

    template = templates.get(header.domain_id, header.template_id)
    return obj, template


def parse_semantic_payload(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[SemanticHeader, SemanticPlan]:
    """Parse a semantic payload into (header, plan) without touching the body."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    return header, plan


def encode_semantic_vector(
    vec: Iterable[float],
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode a float vector with an Sv semantic header.

    This helper first encodes the vector into a compact Sv binary form
    and then wraps it with :func:`semantic_compress` using the ``Sv``
    codec label so downstream systems can route it as a vector payload.
    """
    body = encode_vector(vec)
    return semantic_compress(body, codec="Sv", domain_id=domain_id, template_id=template_id)


def decode_semantic_vector(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[list[float], SemanticHeader, SemanticPlan]:
    """Decode an Sv semantic payload into a list of floats.

    Returns:
        (vector, header, plan)

    Raises:
        ValueError: if the payload does not use the ``Sv`` codec label.
    """
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sv":
        raise ValueError(f"expected Sv payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sv payload body must be bytes-like")
    vec = decode_vector(raw)
    return vec, header, plan


def encode_semantic_stream(
    samples: Iterable[float],
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode a numeric stream with an Sw semantic header."""
    body = encode_wave(samples)
    return semantic_compress(body, codec="Sw", domain_id=domain_id, template_id=template_id)


def decode_semantic_stream(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[list[float], SemanticHeader, SemanticPlan]:
    """Decode an Sw semantic payload into a list of floats."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sw":
        raise ValueError(f"expected Sw payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sw payload body must be bytes-like")
    samples = decode_wave(raw)
    return samples, header, plan


def encode_semantic_index(
    meta: IndexMetadata,
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode index metadata with an Si semantic header."""
    body = encode_index(meta)
    return semantic_compress(body, codec="Si", domain_id=domain_id, template_id=template_id)


def decode_semantic_index(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[IndexMetadata, SemanticHeader, SemanticPlan]:
    """Decode an Si semantic payload into IndexMetadata."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Si":
        raise ValueError(f"expected Si payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Si payload body must be bytes-like")
    meta = decode_index(raw)
    return meta, header, plan


def encode_semantic_table(
    rows: Iterable[Mapping[str, Any]],
    domain_id: int = 0,
    template_id: int | None = None,
    schema: TableSchema | None = None,
) -> bytes:
    """Encode row dicts as an St semantic payload.

    This is a small wrapper around :func:`semantic_table.encode_table`
    that keeps the St semantics consistent with other helpers.
    """
    # Normalize to a concrete sequence for reuse during schema inference.
    materialized_rows = list(rows)
    return encode_table(
        materialized_rows,
        domain_id=domain_id,
        template_id=template_id,
        schema=schema,
    )


def decode_semantic_table(
    payload: bytes,
) -> Tuple[List[Dict[str, Any]], TableSchema, SemanticHeader, SemanticPlan]:
    """Decode an St semantic payload into rows and schema."""
    rows, schema, header, plan = decode_table(payload)
    return rows, schema, header, plan


def encode_semantic_pattern(
    pattern: str,
    fields: Dict[str, Any],
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode pattern + fields as an Sp semantic payload."""
    body = encode_pattern(pattern, fields)
    return semantic_compress(body, codec="Sp", domain_id=domain_id, template_id=template_id)


def decode_semantic_pattern(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[str, Dict[str, Any], SemanticHeader, SemanticPlan]:
    """Decode an Sp semantic payload into pattern and fields."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sp":
        raise ValueError(f"expected Sp payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sp payload body must be bytes-like")
    pattern, fields = decode_pattern(raw)
    return pattern, fields, header, plan


def encode_semantic_joint(
    payloads: Iterable[bytes],
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode multiple semantic payloads into a single Sj container."""
    body = encode_joint(payloads)
    return semantic_compress(body, codec="Sj", domain_id=domain_id, template_id=template_id)


def decode_semantic_joint(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[list[bytes], SemanticHeader, SemanticPlan]:
    """Decode an Sj semantic payload into a list of payloads."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sj":
        raise ValueError(f"expected Sj payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sj payload body must be bytes-like")
    parts = decode_joint(raw)
    return parts, header, plan


def encode_semantic_keys(
    keys: Dict[str, str],
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode logical keys with an Sk semantic header."""
    meta = KeyMetadata(keys=dict(keys))
    body = encode_keys(meta)
    return semantic_compress(body, codec="Sk", domain_id=domain_id, template_id=template_id)


def decode_semantic_keys(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[KeyMetadata, SemanticHeader, SemanticPlan]:
    """Decode an Sk semantic payload into key metadata."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sk":
        raise ValueError(f"expected Sk payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sk payload body must be bytes-like")
    meta = decode_keys(raw)
    return meta, header, plan


def encode_semantic_pattern(
    pattern: str,
    fields: Dict[str, Any],
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode a pattern + fields mapping as an Sp semantic payload."""
    body = encode_pattern(pattern, fields)
    return semantic_compress(body, codec="Sp", domain_id=domain_id, template_id=template_id)


def decode_semantic_pattern(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[str, Dict[str, Any], SemanticHeader, SemanticPlan]:
    """Decode an Sp semantic payload into (pattern, fields, header, plan)."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sp":
        raise ValueError(f"expected Sp payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sp payload body must be bytes-like")
    pattern, fields = decode_pattern(raw)
    return pattern, fields, header, plan


def encode_semantic_quantized_floats(
    floats: Iterable[float],
    bits: int = 8,
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Encode floats as an Sq semantic payload."""
    body = encode_quantized_floats(floats, bits=bits)
    return semantic_compress(body, codec="Sq", domain_id=domain_id, template_id=template_id)


def decode_semantic_quantized_floats(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> Tuple[list[float], SemanticHeader, SemanticPlan]:
    """Decode an Sq semantic payload into a list of floats."""
    header, plan, _ = decode_payload_to_plan(payload, templates=templates)
    if plan.codec_label != "Sq":
        raise ValueError(f"expected Sq payload, got codec {plan.codec_label!r}")
    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("Sq payload body must be bytes-like")
    floats = decode_quantized_floats(raw)
    return floats, header, plan


def encode_chat_completion_response(
    *,
    id: str,
    model: str,
    content: str,
    role: str = "assistant",
    created: int | None = None,
    finish_reason: str | None = "stop",
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    domain_id: int = 0,
    template_id: int = 0,
) -> bytes:
    """Encode a standard chat completion-style JSON response using Sb.

    This helper builds a minimal OpenAI-style response object:
        {"id": ..., "object": "chat.completion", "created": ..., ...}
    and wraps it in an Sb semantic header via :func:`sb_encode_json`.
    """
    if created is None:
        created = 0
    usage: Dict[str, Any] = {}
    if prompt_tokens is not None:
        usage["prompt_tokens"] = prompt_tokens
    if completion_tokens is not None:
        usage["completion_tokens"] = completion_tokens
    if total_tokens is not None:
        usage["total_tokens"] = total_tokens

    obj: Dict[str, Any] = {
        "id": id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": role, "content": content},
                "finish_reason": finish_reason,
            }
        ],
    }
    if usage:
        obj["usage"] = usage

    return sb_encode_json(obj, domain_id=domain_id, template_id=template_id)


def decode_chat_completion_response(payload: bytes) -> Dict[str, Any]:
    """Decode a chat completion-style Sb semantic payload back into a dict."""
    obj = sb_decode_json(payload)
    if not isinstance(obj, dict):
        raise ValueError("chat completion payload must decode to a JSON object")
    return obj
