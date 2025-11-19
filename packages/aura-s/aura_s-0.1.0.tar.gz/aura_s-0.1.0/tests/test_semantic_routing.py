from arua.compression.semantic import (
    SemanticHeader,
    CODEC_ID_SE,
    CODEC_ID_SB,
)
from arua.compression.semantic_plans import decode_payload_to_plan
from arua.compression.semantic import semantic_compress
from arua.compression.semantic_routing import SemanticRouter, RoutingProfile


def test_routing_profile_basic_shape() -> None:
    router = SemanticRouter()
    data = b"hello semantic routing"
    payload = semantic_compress(data, codec="Sb", domain_id=1, template_id=0)
    header, plan, _ = decode_payload_to_plan(payload)

    assert isinstance(header, SemanticHeader)

    profile = router.select(plan)
    assert isinstance(profile, RoutingProfile)
    assert profile.tier == plan.model_tier
    assert profile.precision == plan.quantization
    assert profile.max_batch > 0


def test_routing_profile_entropy_low_vs_high() -> None:
    router = SemanticRouter()

    # Low-entropy Se payload (repetitive bytes)
    low_entropy = b"a" * 256
    low_payload = bytes(
        [CODEC_ID_SE, 0, 0, 0]
    ) + low_entropy  # pre-encoded Se header followed by body
    header_low, plan_low, body_low = decode_payload_to_plan(low_payload)
    assert header_low.codec_id == CODEC_ID_SE
    assert body_low == low_entropy
    assert plan_low.entropy_bucket is not None

    profile_low = router.select(plan_low)

    # High-entropy Se payload (many unique bytes)
    high_entropy = bytes(range(256))
    high_payload = bytes([CODEC_ID_SE, 0, 0, 0]) + high_entropy
    header_high, plan_high, body_high = decode_payload_to_plan(high_payload)
    assert header_high.codec_id == CODEC_ID_SE
    assert body_high == high_entropy
    assert plan_high.entropy_bucket is not None

    profile_high = router.select(plan_high)

    # Low-entropy should favour at least as large a batch as high-entropy.
    assert profile_low.max_batch >= profile_high.max_batch

