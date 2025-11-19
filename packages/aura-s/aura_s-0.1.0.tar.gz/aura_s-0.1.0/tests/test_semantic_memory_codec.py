from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_unique import reset_unique_store


def test_sm_semantic_roundtrip() -> None:
    reset_unique_store()
    data = (b"block-A" * 100) + (b"block-B" * 100)
    payload = semantic_compress(data, codec="Sm", domain_id=15)
    out = semantic_decompress(payload)
    assert out == data

