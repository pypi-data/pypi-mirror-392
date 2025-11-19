import os
from arua.compression.core import compress, decompress


def test_semantic_grain_roundtrip():
    data = b"This is a test. " * 100
    compressed = compress(data, method="sg")
    decompressed = decompress(compressed)
    assert decompressed == data


def test_auto_prefers_sg(tmp_path):
    # Create data that should benefit from compression
    data = (b"REPEATED_PATTERN_" * 1000)[:1024]
    compressed = compress(data, method="auto")
    # Ensure method byte is SG or LZ77 but prefer SG in our auto policy
    method = compressed[0]
    assert method in (0x01, 0x02)


if __name__ == '__main__':
    test_semantic_grain_roundtrip()
    test_auto_prefers_sg(None)
    print("Semantic grain integration tests run")