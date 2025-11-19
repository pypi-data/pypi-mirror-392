from arua.compression.semantic_derivative import encode_derivative, decode_derivative
from arua.compression.semantic import semantic_compress, semantic_decompress


def test_sd_raw_roundtrip() -> None:
    data = bytes(range(0, 256))
    payload = encode_derivative(data)
    out = decode_derivative(payload)
    assert out == data


def test_sd_semantic_roundtrip() -> None:
    data = b"semantic derivative test" * 10
    payload = semantic_compress(data, codec="Sd", domain_id=13)
    out = semantic_decompress(payload)
    assert out == data

