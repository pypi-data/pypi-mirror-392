from arua.compression.semantic_vector import encode_vector, decode_vector


def test_vector_roundtrip_simple() -> None:
    vec = [0.0, 0.5, -0.5, 1.0, -1.0]
    payload = encode_vector(vec)
    decoded = decode_vector(payload)
    assert len(decoded) == len(vec)
    for a, b in zip(vec, decoded):
        assert abs(a - b) <= 1e-3


def test_vector_empty() -> None:
    vec: list[float] = []
    payload = encode_vector(vec)
    decoded = decode_vector(payload)
    assert decoded == vec

