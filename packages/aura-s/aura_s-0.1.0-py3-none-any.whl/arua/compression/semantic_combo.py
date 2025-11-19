"""Semantic Context / Combo (Sc)

Sc is a context-aware combo codec: it can try multiple compression
strategies and select the best result for a given payload. In the
current CPU-only implementation, it simply runs flow + grain + core
and picks the smallest result, preferring lower-latency options on
ties.

Future versions can incorporate richer semantic context (Sa/Sb header
atoms and templates, Se/Sy/Sr signals, SemanticPlan) to choose between
Sf/Sg/Sq/Sz and different execution tiers.
"""
from __future__ import annotations

from typing import Optional, Tuple

from .core import compress as core_compress, decompress as core_decompress
from .flow import compress as flow_compress, decompress as flow_decompress
from .grain import compress as grain_compress, decompress as grain_decompress


def compress(
    data: bytes,
    max_seq: Optional[int] = None,
    priority: Optional[str] = None,
) -> bytes:
    """Try different strategies and return the best payload.

    Strategies tried (CPU placeholder):
    - Flow (Sf)   – good for shorter, chat-like text.
    - Grain (Sg)  – good for denser, repetitive text.
    - Core (auto) – generic fallback.

    If ``max_seq`` or ``priority`` are provided from a higher-level
    context plan, they can bias the choice slightly in favour of flow
    (low-latency) vs grain/core without changing the on-wire format.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    raw = bytes(data)

    # Strategy 1: flow compression
    flow_payload = flow_compress(raw)
    # Strategy 2: grain compression
    grain_payload = grain_compress(raw)
    # Strategy 3: core auto
    core_payload = core_compress(raw, method="auto")

    # Compare sizes first.
    candidates = [
        (len(flow_payload), "flow", flow_payload),
        (len(grain_payload), "grain", grain_payload),
        (len(core_payload), "core", core_payload),
    ]
    candidates.sort(key=lambda x: (x[0], x[1]))
    best_len, best_label, best = candidates[0]

    # Simple context-aware tweaks:
    # - For short contexts (small max_seq), prefer flow if close in size.
    # - For high-priority traffic, avoid the heaviest option when sizes are similar.
    if max_seq is not None and max_seq <= 1024:
        for size, label, payload in candidates:
            if label == "flow" and size <= best_len * 1.05:
                best_len, best_label, best = size, label, payload
                break
    if priority == "high":
        # For high-priority contexts, prefer flow over grain/core when sizes
        # are within 10% to slightly favour latency over ratio.
        for size, label, payload in candidates:
            if label == "flow" and size <= best_len * 1.10:
                best_len, best_label, best = size, label, payload
                break

    return best


def decompress(payload: bytes, prefer: str | None = None) -> bytes:
    """Attempt to decompress by trying the flow/grain/core decompressor.

    If `prefer` is specified, try that backend first.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    # Optionally, backends could store a small tag in header to pick fast path.
    # But for CPU-side placeholder, we just try all and return the first that succeeds.

    # Try prefer
    if prefer == "flow":
        try:
            return flow_decompress(payload)
        except (ValueError, TypeError):
            pass
    if prefer == "grain":
        try:
            return grain_decompress(payload)
        except (ValueError, TypeError):
            pass
    if prefer == "core":
        try:
            return core_decompress(payload)
        except (ValueError, TypeError):
            pass

    # Try flow
    try:
        return flow_decompress(payload)
    except (ValueError, TypeError):
        pass
    # Try grain
    try:
        return grain_decompress(payload)
    except (ValueError, TypeError):
        pass
    # Try core
    return core_decompress(payload)
