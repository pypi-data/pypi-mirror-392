from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_yield import YieldMetadata, encode_yield, decode_yield, compress, decompress


def test_sy_metadata_roundtrip() -> None:
    meta = YieldMetadata(priority="high", max_latency_ms=50, expected_value=1.5)
    blob = encode_yield(meta)
    decoded = decode_yield(blob)
    assert decoded.priority == "high"
    assert decoded.max_latency_ms == 50
    assert decoded.expected_value == 1.5


def test_sy_compress_decompress() -> None:
    data = b"yield-sensitive payload"
    meta = YieldMetadata(priority="low", max_latency_ms=500)
    payload = compress(data, meta=meta)
    out, out_meta = decompress(payload)
    assert out == data
    assert out_meta.priority == "low"
    assert out_meta.max_latency_ms == 500


def test_sy_semantic_roundtrip() -> None:
    data = b"semantic Sy test" * 5
    payload = semantic_compress(data, codec="Sy", domain_id=16)
    out = semantic_decompress(payload)
    assert out == data

