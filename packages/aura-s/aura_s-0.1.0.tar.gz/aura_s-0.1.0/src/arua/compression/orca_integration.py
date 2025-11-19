"""ORCA integration helpers for semantic compression plans.

This module provides a light mapping from :class:`SemanticPlan` to
engine/profile identifiers that an ORCA deployment can use to select
the appropriate CUDA/TensorRT pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .semantic_plans import SemanticPlan


@dataclass(frozen=True)
class EngineSelection:
    """Represents a selected engine/profile for execution."""

    engine_name: str
    profile_name: str
    max_batch: int


class OrcaEngineSelector:
    """Simple engine selector based on SemanticPlan."""

    def __init__(self) -> None:
        # These mappings are intentionally generic; ORCA can override them.
        self._tier_to_engine: Dict[str, str] = {
            "small": "orca-small",
            "medium": "orca-medium",
            "large": "orca-large",
        }
        self._quant_to_profile: Dict[str, str] = {
            "int8": "int8-default",
            "fp16": "fp16-default",
            "fp32": "fp32-default",
        }

    def select(self, plan: SemanticPlan) -> EngineSelection:
        """Map a SemanticPlan to an EngineSelection."""
        engine_name = self._tier_to_engine.get(plan.model_tier, "orca-medium")
        profile_name = self._quant_to_profile.get(plan.quantization, "fp16-default")

        # Base heuristic: longer max sequence → smaller batch.
        if plan.max_sequence_length <= 512:
            max_batch = 64
        elif plan.max_sequence_length <= 2048:
            max_batch = 32
        else:
            max_batch = 8

        # Entropy-aware adjustment for Se (Semantic Entropy) plans.
        # We only tweak selection when an entropy bucket is present so that
        # existing Sa/Sb/Sf/Sg behaviour remains unchanged.
        if plan.codec_label == "Se" and plan.entropy_bucket is not None:
            bucket = plan.entropy_bucket

            # Low-entropy payloads (bucket 0–1): prefer smaller engines and
            # higher batch sizes for better energy efficiency.
            if bucket <= 1:
                if plan.model_tier == "medium":
                    engine_name = self._tier_to_engine.get("small", engine_name)
                if max_batch < 128:
                    max_batch = min(128, max_batch * 2)

            # High-entropy payloads (bucket 3): favour larger engines and
            # reduce batch size to avoid overloading a single engine instance.
            elif bucket >= 3:
                if plan.model_tier == "medium":
                    engine_name = self._tier_to_engine.get("large", engine_name)
                if max_batch > 1:
                    max_batch = max(1, max_batch // 2)

        return EngineSelection(
            engine_name=engine_name,
            profile_name=profile_name,
            max_batch=max_batch,
        )
