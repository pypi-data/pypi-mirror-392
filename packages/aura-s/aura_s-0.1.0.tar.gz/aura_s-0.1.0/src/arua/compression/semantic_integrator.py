"""Semantic integrator for routing and decompression.

This module provides a small orchestration layer that ties together:

* header/plan parsing (``decode_payload_to_plan``),
* interplay/routing metadata (``get_interplay``),
* fast-path accelerator decisions (``FastPathEngine``), and
* concrete backend implementations (local CPU by default).

It is intended to be the single entrypoint that callers use when they
want a semantic payload to be:

1. Parsed into header + plan,
2. Routed to an appropriate backend (CPU/GPU/remote), and
3. Decompressed into a usable value.

Backends are pluggable; the default integrator only uses the local
Python implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable, Dict, Optional, Tuple

from ..templates import TemplateLibrary
from .semantic import SemanticHeader, semantic_decompress
from .semantic_fastpath import FastPathEngine, FastPathDecision
from .semantic_interplay import InterplayFlag, get_interplay
from .semantic_plans import SemanticPlan, decode_payload_to_plan


@dataclass
class IntegratorResult:
    """Result of routing and decompressing a semantic payload."""

    value: Any
    header: SemanticHeader
    plan: SemanticPlan
    interplay: InterplayFlag
    backend_name: str
    decision: FastPathDecision
    duration_ms: float


class BaseBackend:
    """Abstract backend interface for semantic payloads."""

    name: str = "base"

    def decompress(self, payload: bytes, plan: SemanticPlan) -> Any:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass(frozen=True)
class BackendConfig:
    """Logical backend configuration for discovery/integration.

    This is a lightweight descriptor that callers can use to describe
    available backends (CPU, GPU, remote) without tying the integrator
    to a specific inference stack.
    """

    name: str        # e.g. "cpu", "gpu0"
    kind: str        # e.g. "cpu", "gpu", "remote"
    device: str | None = None  # e.g. "cuda:0", "rtx-4090", URL, etc.


class GpuBackend(BaseBackend):
    """GPU/accelerator backend stub.

    This backend is intentionally minimal: it currently proxies to the
    local semantic decompressor but keeps a distinct type and name so it
    can be swapped out for a real GPU implementation without changing
    the integrator API.
    """

    name: str = "gpu"

    def decompress(self, payload: bytes, plan: SemanticPlan) -> Any:
        # Stub: in a future version, this would hand off to a GPU/remote
        # accelerator implementation. For now, mirror LocalBackend
        # semantics so that integration and routing logic can be tested.
        return semantic_decompress(payload)


class LocalBackend(BaseBackend):
    """Local CPU backend using the in-process semantic codecs."""

    name: str = "cpu"

    def decompress(self, payload: bytes, plan: SemanticPlan) -> Any:
        # For now, just return the raw bytes produced by semantic_decompress.
        # Higher-level callers can further interpret the body using helpers.
        return semantic_decompress(payload)


@dataclass
class IntegratorConfig:
    """Configuration for the semantic integrator.

    Attributes:
        backends: Mapping from backend name to backend instance. The
            default configuration provides ``"cpu"`` and a stub
            ``"gpu"`` backend so that accelerator routing can be
            exercised even without a real GPU implementation.
        backend_configs: Optional mapping from backend name to
            :class:`BackendConfig` descriptors for discovery/logging.
        default_backend: Name of the backend to use when no specific
            accelerator backend is selected or available.
        on_decision: Optional callback invoked with the final
            :class:`IntegratorResult` so callers can log or aggregate
            routing/latency information.
    """
    backends: Dict[str, BaseBackend] = field(
        default_factory=lambda: {"cpu": LocalBackend(), "gpu": GpuBackend()}
    )
    backend_configs: Dict[str, BackendConfig] = field(
        default_factory=lambda: {
            "cpu": BackendConfig(name="cpu", kind="cpu", device=None),
            "gpu": BackendConfig(name="gpu", kind="gpu", device="cuda:0"),
        }
    )
    default_backend: str = "cpu"
    on_decision: Optional[Callable[["IntegratorResult"], None]] = None


class SemanticIntegrator:
    """High-level orchestrator that routes and decompresses semantic payloads."""

    def __init__(self, config: IntegratorConfig | None = None) -> None:
        self._config = config or IntegratorConfig()
        self._fastpath = FastPathEngine()

    def route_and_decompress(
        self,
        payload: bytes,
        templates: TemplateLibrary | None = None,
        priority: str | None = None,
    ) -> IntegratorResult:
        """Route a semantic payload and decompress it via the chosen backend.

        Args:
            payload: Semantic payload (header + body).
            templates: Optional template library used when building the plan.
            priority: Optional hint such as ``"low"``, ``"normal"`` or
                ``"high"`` to influence accelerator selection.

        Returns:
            IntegratorResult describing the decoded value, header, plan,
            interplay flags, chosen backend and fast-path decision.
        """
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("route_and_decompress() expects a bytes-like object")

        header, plan, _ = decode_payload_to_plan(payload, templates=templates)
        interplay = get_interplay(plan)
        decision = self._fastpath.choose(payload, priority=priority, templates=templates)

        # Decide backend name from accelerator decision; fall back to default.
        backend_name = decision.accelerator.backend or self._config.default_backend
        if not decision.accelerator.offload:
            backend_name = self._config.default_backend

        backend = self._config.backends.get(backend_name)
        if backend is None:
            backend_name = self._config.default_backend
            backend = self._config.backends[backend_name]

        start = perf_counter()
        value = backend.decompress(payload, plan)
        duration_ms = (perf_counter() - start) * 1000.0

        result = IntegratorResult(
            value=value,
            header=header,
            plan=plan,
            interplay=interplay,
            backend_name=backend_name,
            decision=decision,
            duration_ms=duration_ms,
        )

        callback = self._config.on_decision
        if callback is not None:
            callback(result)

        return result
