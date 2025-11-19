"""Semantic Orchestration (So) codec.

So encodes workflow DAGs and orchestration metadata for multi-step processes.
This allows coordination of complex workflows where each step may have
dependencies and use different tools.

The wire format embeds the orchestration graph as JSON alongside compressed data:
    [2-byte graph_blob_length][graph_blob][compressed_data]

Example:
    step1 = OrchestrationStep(step_id="extract", parents=[], tool="lz77")
    step2 = OrchestrationStep(step_id="compress", parents=["extract"], tool="zstd")
    graph = OrchestrationGraph(steps=[step1, step2])

    compressed = compress(b"workflow data", graph=graph)
    data, decoded_graph = decompress(compressed)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .core import compress as core_compress
from .core import decompress as core_decompress


@dataclass(frozen=True)
class OrchestrationStep:
    """Single step in an orchestration graph."""

    step_id: str
    parents: List[str]
    tool: str


@dataclass(frozen=True)
class OrchestrationGraph:
    """Workflow-level metadata for So payloads."""

    steps: List[OrchestrationStep]


def encode_orchestration(graph: OrchestrationGraph) -> bytes:
    """Encode an orchestration graph into a UTF-8 JSON body."""
    obj = {
        "steps": [
            {"id": s.step_id, "parents": s.parents, "tool": s.tool}
            for s in graph.steps
        ]
    }
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def decode_orchestration(payload: bytes) -> OrchestrationGraph:
    """Decode an orchestration graph from a UTF-8 JSON body."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_orchestration() expects a bytes-like object")
    try:
        obj = json.loads(bytes(payload).decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid So payload JSON") from exc
    if not isinstance(obj, dict) or "steps" not in obj or not isinstance(
        obj["steps"], list
    ):
        raise ValueError("So payload must contain a 'steps' list")
    steps: List[OrchestrationStep] = []
    for entry in obj["steps"]:
        if not isinstance(entry, dict) or "id" not in entry:
            raise ValueError("invalid So step entry")
        parents = entry.get("parents", [])
        tool = entry.get("tool", "")
        if not isinstance(parents, list):
            raise ValueError("So step parents must be a list")
        steps.append(
            OrchestrationStep(
                step_id=str(entry["id"]),
                parents=[str(p) for p in parents],
                tool=str(tool),
            )
        )
    return OrchestrationGraph(steps=steps)


def compress(data: bytes, graph: OrchestrationGraph | None = None) -> bytes:
    """Compress data with optional orchestration graph metadata.

    Args:
        data: The raw data to compress.
        graph: Optional orchestration graph describing workflow steps.

    Returns:
        Compressed payload with embedded graph metadata.

    The wire format is:
        [2-byte graph_blob_length][graph_blob][compressed_data]

    If no graph is provided, an empty graph is used.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    if graph is None:
        graph = OrchestrationGraph(steps=[])

    graph_blob = encode_orchestration(graph)
    if len(graph_blob) > 0xFFFF:
        raise ValueError("orchestration graph metadata too large (max 65535 bytes)")

    compressed_data = core_compress(bytes(data), method="auto")

    graph_length = len(graph_blob)
    length_bytes = bytes([(graph_length >> 8) & 0xFF, graph_length & 0xFF])

    return length_bytes + graph_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, OrchestrationGraph]:
    """Decompress a payload and extract orchestration graph metadata.

    Args:
        payload: The compressed payload with embedded graph.

    Returns:
        A tuple of (decompressed_data, orchestration_graph).

    Raises:
        TypeError: If payload is not bytes-like.
        ValueError: If payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = bytes(payload)
    if len(data) < 2:
        raise ValueError("So payload too short for length header")

    graph_length = (data[0] << 8) | data[1]
    if len(data) < 2 + graph_length:
        raise ValueError("So payload truncated before graph blob")

    graph_blob = data[2 : 2 + graph_length]
    compressed_data = data[2 + graph_length :]

    graph = decode_orchestration(graph_blob)
    decompressed_data = core_decompress(compressed_data)

    return decompressed_data, graph

