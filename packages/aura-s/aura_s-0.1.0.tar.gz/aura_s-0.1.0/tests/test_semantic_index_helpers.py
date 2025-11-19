from arua.compression.semantic_index import IndexMetadata, encode_index, decode_index


def test_index_roundtrip() -> None:
    meta = IndexMetadata(doc_id=123, section_id=4, shard_id=2, offset=4096)
    payload = encode_index(meta)
    decoded = decode_index(payload)
    assert decoded == meta


def test_index_invalid_size() -> None:
    try:
        decode_index(b"\x00")
    except ValueError:
        pass
    else:
        assert False, "expected ValueError for invalid size"

