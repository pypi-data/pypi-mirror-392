from arua.compression.semantic import SemanticHeader, CODEC_ID_SF
from arua.compression.semantic_plans import plan_from_header
from arua.compression.semantic_accelerator import (
    SemanticAcceleratorSelector,
    AcceleratorSelection,
)


def test_accelerator_selector_gpu_for_flow() -> None:
    header = SemanticHeader(codec_id=CODEC_ID_SF, domain_id=0, template_id=0)
    plan = plan_from_header(header)
    selector = SemanticAcceleratorSelector()
    sel = selector.select(plan, priority="high")

    assert isinstance(sel, AcceleratorSelection)
    assert sel.backend in {"cpu", "gpu", "dpu"}
    # For Sf with high priority we expect GPU offload in the prototype.
    assert sel.backend == "gpu"
    assert sel.offload is True

