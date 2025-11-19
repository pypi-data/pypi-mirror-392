"""Fast-path orchestration for semantic payloads.

This module provides a single entrypoint that takes a semantic payload
and returns a consolidated decision describing:

* the parsed :class:`SemanticHeader`,
* the derived :class:`SemanticPlan`,
* a neutral :class:`RoutingProfile` (tier/device/batch),
* a simple accelerator decision, and
* a compact interplay bitmask.

It is intentionally thin and built on top of existing components
(:mod:`semantic_plans`, :mod:`semantic_routing`, and
:mod:`semantic_interplay`) so that the on-wire header remains small.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..templates import TemplateLibrary
from .semantic import SemanticHeader
from .semantic_interplay import InterplayFlag, get_interplay
from .semantic_plans import SemanticPlan, decode_payload_to_plan
from .semantic_routing import RoutingProfile, SemanticRouter


@dataclass(frozen=True)
class AcceleratorDecision:
    """Simple accelerator selection for a semantic payload.

    Attributes:
        backend: Logical backend name (e.g. ``"cpu"`` or ``"gpu"``).
        profile: Textual profile name combining tier/precision, which
            callers can map to concrete engines.
        offload: Whether the payload should be offloaded from CPU at all.
    """

    backend: str
    profile: str
    offload: bool


@dataclass(frozen=True)
class FastPathDecision:
    """Aggregated fast-path decision for a semantic payload."""

    header: SemanticHeader
    plan: SemanticPlan
    routing: RoutingProfile
    accelerator: AcceleratorDecision
    interplay: InterplayFlag


class FastPathEngine:
    """High-level fast-path orchestrator for semantic payloads."""

    def __init__(self) -> None:
        self._router = SemanticRouter()

    def _choose_accelerator(
        self,
        plan: SemanticPlan,
        interplay: InterplayFlag,
        priority: Optional[str],
    ) -> AcceleratorDecision:
        """Derive a simple accelerator decision from plan and interplay."""
        # Base backend choice from codec characteristics:
        # - numeric / accelerator-friendly codecs → GPU by default
        # - everything else → CPU unless promoted by priority hints.
        backend = "cpu"
        if interplay & InterplayFlag.IS_NUMERIC:
            backend = "gpu"
        elif (interplay & InterplayFlag.IS_TEXTUAL) and (interplay & InterplayFlag.USES_ACCEL):
            backend = "gpu"

        offload = backend != "cpu"

        # Priority-based adjustments.
        if priority == "low":
            # Low-priority traffic stays on CPU unless clearly numeric/vector.
            if not (interplay & InterplayFlag.IS_NUMERIC):
                backend = "cpu"
                offload = False
        elif priority == "high":
            # High-priority textual codecs that are accelerator-friendly
            # can be promoted to GPU.
            if (interplay & InterplayFlag.IS_TEXTUAL) and (interplay & InterplayFlag.USES_ACCEL):
                backend = "gpu"
                offload = True

        if backend == "gpu":
            profile = f"gpu-{plan.model_tier}-{plan.quantization}"
        else:
            profile = f"cpu-{plan.model_tier}"

        return AcceleratorDecision(backend=backend, profile=profile, offload=offload)

    def choose(
        self,
        payload: bytes,
        priority: Optional[str] = None,
        templates: Optional[TemplateLibrary] = None,
    ) -> FastPathDecision:
        """Compute a fast-path decision for a semantic payload.

        Args:
            payload: Bytes produced by ``semantic_compress`` or an
                equivalent semantic encoder.
            priority: Optional hint such as ``"low"``, ``"normal"`` or
                ``"high"`` to influence accelerator selection.
            templates: Optional :class:`TemplateLibrary` used when
                building the :class:`SemanticPlan`.
        """
        header, plan, _ = decode_payload_to_plan(payload, templates=templates)
        routing = self._router.select(plan)
        interplay = get_interplay(plan)
        accelerator = self._choose_accelerator(plan, interplay, priority)
        return FastPathDecision(
            header=header,
            plan=plan,
            routing=routing,
            accelerator=accelerator,
            interplay=interplay,
        )
