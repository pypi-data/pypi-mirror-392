from arua.compression.flow import compress as flow_compress, decompress as flow_decompress
from arua.compression.grain import compress as grain_compress, decompress as grain_decompress
from arua.compression.semantic import semantic_compress, semantic_decompress


def test_flow_roundtrip_direct() -> None:
    data = (b"hello chat " * 50) + b"tail"
    comp = flow_compress(data)
    out = flow_decompress(comp)
    assert out == data


def test_grain_roundtrip_direct() -> None:
    data = (b"abc123" * 100) + b"tail"
    comp = grain_compress(data)
    out = grain_decompress(comp)
    assert out == data


def test_sf_semantic_roundtrip() -> None:
    data = (b"hello world " * 80) + b"end"
    payload = semantic_compress(data, codec="Sf", domain_id=2)
    out = semantic_decompress(payload)
    assert out == data


def test_sg_semantic_roundtrip() -> None:
    data = (b"xyz" * 200) + b"end"
    payload = semantic_compress(data, codec="Sg", domain_id=1)
    out = semantic_decompress(payload)
    assert out == data
