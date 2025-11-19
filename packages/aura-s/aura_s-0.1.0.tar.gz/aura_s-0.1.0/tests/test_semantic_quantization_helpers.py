from arua.compression.helpers import (
    encode_semantic_quantized_floats,
    decode_semantic_quantized_floats,
)


def test_sq_roundtrip_basic() -> None:
    vec = [0.0, 0.25, 0.5, 0.75, 1.0]
    payload = encode_semantic_quantized_floats(vec, bits=8, domain_id=12)
    decoded, header, plan = decode_semantic_quantized_floats(payload)

    assert plan.codec_label == "Sq"
    assert header.domain_id == 12
    assert len(decoded) == len(vec)
    # Allow some quantization error.
    for a, b in zip(vec, decoded):
        assert abs(a - b) <= 0.02

