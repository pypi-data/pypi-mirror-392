"""Semantic Context (Sc) helpers.

This module builds full-context Sc payloads by bundling multiple
Sa/Sb/S*-labelled segments together with explicit context metadata.

Wire format (Sc body):

    [2B meta_len][meta_blob][joint_payload]

Where:
    * meta_blob is a UTF-8 JSON object describing the context
      (max_seq, priority, truncated flag, roles, etc.).
    * joint_payload is an Sj-style joint container of semantic
      payloads produced by :func:`encode_semantic_text`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .helpers import (
    decode_semantic_text,
    encode_semantic_text,
)
from .semantic import CODEC_ID_SC, SemanticHeader
from .semantic_joint import decode_joint, encode_joint
from .semantic_plans import SemanticPlan


@dataclass(frozen=True)
class ContextSegment:
    """Single segment in an Sc context."""

    role: str
    data: bytes
    codec: str = "auto"
    domain_id: int = 0
    template_id: Optional[int] = None


@dataclass(frozen=True)
class ContextMetadata:
    """Metadata describing an Sc context."""

    max_seq: Optional[int]
    priority: str
    truncated: bool
    num_segments: int
    roles: List[str]
    entropy_bucket: Optional[int] = None
    route_hint: str | None = None


def compress_context(
    segments: Iterable[ContextSegment],
    *,
    domain_id: int = 0,
    max_seq: Optional[int] = None,
    priority: str = "normal",
) -> bytes:
    """Build a full-context Sc payload from segments.

    This helper:
      * optionally truncates context based on ``max_seq`` (approximate bytes),
      * encodes each segment via :func:`encode_semantic_text` (Sa/Sb-aware),
      * bundles them in an Sj joint container, and
      * prefixes explicit context metadata in a JSON blob.
    """
    seg_list = list(segments)
    if not seg_list:
        header = SemanticHeader(codec_id=CODEC_ID_SC, domain_id=domain_id, template_id=0)
        # Empty context with minimal metadata.
        meta = {
            "version": 1,
            "max_seq": max_seq,
            "priority": priority,
            "truncated": False,
            "num_segments": 0,
            "roles": [],
        }
        meta_blob = json.dumps(meta, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if len(meta_blob) > 0xFFFF:
            raise ValueError("Sc context metadata too large (max 65535 bytes)")
        length_bytes = bytes([(len(meta_blob) >> 8) & 0xFF, len(meta_blob) & 0xFF])
        return header.to_bytes() + length_bytes + meta_blob

    # Approximate truncation based on byte length of raw data.
    truncated = False
    if max_seq is not None:
        budget = max_seq
        kept: List[ContextSegment] = []
        for seg in seg_list:
            seg_len = len(seg.data)
            if seg_len <= budget:
                kept.append(seg)
                budget -= seg_len
            else:
                truncated = True
                break
        seg_list = kept

    # Encode segments with semantic headers (Sa/Sb-aware).
    payloads: List[bytes] = []
    roles: List[str] = []
    for seg in seg_list:
        payloads.append(
            encode_semantic_text(
                seg.data,
                codec=seg.codec,
                domain_id=seg.domain_id,
                template_id=seg.template_id,
            )
        )
        roles.append(seg.role)

    joint_payload = encode_joint(payloads)

    # Estimate a coarse entropy bucket across the concatenated segment data
    # to mirror Se behaviour for routing/analysis.
    concat = b"".join(seg.data for seg in seg_list)
    entropy_bucket: Optional[int]
    if not concat:
        entropy_bucket = 0
    else:
        sample = concat[:256]
        unique = len(set(sample))
        ratio = unique / len(sample)
        if ratio < 0.25:
            entropy_bucket = 0
        elif ratio < 0.5:
            entropy_bucket = 1
        elif ratio < 0.75:
            entropy_bucket = 2
        else:
            entropy_bucket = 3

    # Simple route hint inspired by Sr/fastpath: if any segment codec is
    # explicitly numeric/vector/accelerator-friendly, suggest GPU, else CPU.
    gpu_friendly = {"Sq", "Sv", "Sx", "Sz"}
    route_hint = "gpu" if any(seg.codec in gpu_friendly for seg in seg_list) else "cpu"

    meta = {
        "version": 1,
        "max_seq": max_seq,
        "priority": priority,
        "truncated": truncated,
        "num_segments": len(payloads),
        "roles": roles,
        "entropy_bucket": entropy_bucket,
        "route_hint": route_hint,
    }
    meta_blob = json.dumps(meta, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if len(meta_blob) > 0xFFFF:
        raise ValueError("Sc context metadata too large (max 65535 bytes)")
    length_bytes = bytes([(len(meta_blob) >> 8) & 0xFF, len(meta_blob) & 0xFF])

    header = SemanticHeader(codec_id=CODEC_ID_SC, domain_id=domain_id, template_id=0)
    return header.to_bytes() + length_bytes + meta_blob + joint_payload


def decompress_context(
    payload: bytes,
) -> Tuple[List[Tuple[str, bytes, SemanticHeader, SemanticPlan]], ContextMetadata, SemanticHeader]:
    """Decode a full-context Sc payload built by :func:`compress_context`.

    Returns:
        (segments, context_meta, sc_header)

        segments: list of (role, data, header, plan)
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress_context() expects a bytes-like object")
    header, body = SemanticHeader.from_bytes(bytes(payload))
    if header.codec_id != CODEC_ID_SC:
        raise ValueError("decompress_context() expects an Sc payload")

    if len(body) < 2:
        raise ValueError("Sc context payload too short for metadata length")
    meta_len = (body[0] << 8) | body[1]
    if len(body) < 2 + meta_len:
        raise ValueError("Sc context payload truncated before metadata blob")
    meta_blob = body[2 : 2 + meta_len]
    joint_payload = body[2 + meta_len :]

    try:
        meta_obj: Dict[str, Any] = json.loads(meta_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sc context metadata JSON") from exc

    max_seq = meta_obj.get("max_seq")
    priority = str(meta_obj.get("priority", "normal"))
    truncated = bool(meta_obj.get("truncated", False))
    roles = meta_obj.get("roles") or []
    num_segments = int(meta_obj.get("num_segments", len(roles)))

    if not isinstance(roles, list):
        raise ValueError("Sc context metadata 'roles' must be a list")

    entropy_bucket = meta_obj.get("entropy_bucket")
    route_hint = meta_obj.get("route_hint")

    context_meta = ContextMetadata(
        max_seq=max_seq,
        priority=priority,
        truncated=truncated,
        num_segments=num_segments,
        roles=[str(r) for r in roles],
        entropy_bucket=entropy_bucket,
        route_hint=route_hint,
    )

    # Decode joint payload into semantic payloads.
    segment_payloads = decode_joint(joint_payload)
    segments: List[Tuple[str, bytes, SemanticHeader, SemanticPlan]] = []

    for idx, seg_payload in enumerate(segment_payloads):
        role = context_meta.roles[idx] if idx < len(context_meta.roles) else "unknown"
        text_or_bytes, seg_header, seg_plan = decode_semantic_text(seg_payload)
        if isinstance(text_or_bytes, str):
            seg_bytes = text_or_bytes.encode("utf-8")
        else:
            seg_bytes = text_or_bytes
        segments.append((role, seg_bytes, seg_header, seg_plan))

    return segments, context_meta, header
