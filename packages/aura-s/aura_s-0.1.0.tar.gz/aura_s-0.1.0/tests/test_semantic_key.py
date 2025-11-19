"""Tests for Semantic Key (Sk) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_key import (
    KeyMetadata,
    compress,
    decompress,
    encode_keys,
    decode_keys,
)


class TestKeyMetadataEncoding:
    """Test low-level key encoding/decoding."""

    def test_encode_decode_empty_keys(self):
        """Test encoding and decoding empty key set."""
        meta = KeyMetadata(keys={})
        encoded = encode_keys(meta)
        decoded = decode_keys(encoded)
        assert decoded.keys == {}

    def test_encode_decode_single_key(self):
        """Test encoding and decoding a single key."""
        meta = KeyMetadata(keys={"user_id": "alice"})
        encoded = encode_keys(meta)
        decoded = decode_keys(encoded)
        assert decoded.keys == {"user_id": "alice"}

    def test_encode_decode_multiple_keys(self):
        """Test encoding and decoding multiple keys."""
        keys = {
            "user_id": "alice",
            "session": "xyz123",
            "tenant": "acme",
            "region": "us-west-2",
        }
        meta = KeyMetadata(keys=keys)
        encoded = encode_keys(meta)
        decoded = decode_keys(encoded)
        assert decoded.keys == keys

    def test_encode_decode_unicode_keys(self):
        """Test encoding and decoding keys with unicode values."""
        keys = {"user": "アリス", "tenant": "café", "emoji": "🔑"}
        meta = KeyMetadata(keys=keys)
        encoded = encode_keys(meta)
        decoded = decode_keys(encoded)
        assert decoded.keys == keys

    def test_decode_invalid_json(self):
        """Test decoding invalid JSON raises ValueError."""
        invalid_json = b"not valid json"
        with pytest.raises(ValueError, match="invalid Sk payload JSON"):
            decode_keys(invalid_json)

    def test_decode_missing_keys_field(self):
        """Test decoding JSON without 'keys' field raises ValueError."""
        invalid = b'{"other": "field"}'
        with pytest.raises(ValueError, match="must contain a 'keys' dict"):
            decode_keys(invalid)

    def test_decode_non_dict_keys(self):
        """Test decoding non-dict 'keys' field raises ValueError."""
        invalid = b'{"keys": "not a dict"}'
        with pytest.raises(ValueError, match="must contain a 'keys' dict"):
            decode_keys(invalid)


class TestSkCompression:
    """Test Sk codec compression and decompression."""

    def test_compress_decompress_no_keys(self):
        """Test compress/decompress with no keys (empty metadata)."""
        data = b"Hello, world!"
        compressed = compress(data)
        decompressed, metadata = decompress(compressed)
        assert decompressed == data
        assert metadata.keys == {}

    def test_compress_decompress_with_keys(self):
        """Test compress/decompress with key metadata."""
        data = b"Important message"
        keys = {"user_id": "alice", "session": "abc123"}
        compressed = compress(data, keys=keys)
        decompressed, metadata = decompress(compressed)
        assert decompressed == data
        assert metadata.keys == keys

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 10000
        keys = {"tenant": "bigcorp", "region": "eu-central-1"}
        compressed = compress(data, keys=keys)
        decompressed, metadata = decompress(compressed)
        assert decompressed == data
        assert metadata.keys == keys

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        keys = {"type": "binary", "encoding": "raw"}
        compressed = compress(data, keys=keys)
        decompressed, metadata = decompress(compressed)
        assert decompressed == data
        assert metadata.keys == keys

    def test_compress_with_many_keys(self):
        """Test compress with many key-value pairs."""
        data = b"payload"
        keys = {f"key_{i}": f"value_{i}" for i in range(20)}
        compressed = compress(data, keys=keys)
        decompressed, metadata = decompress(compressed)
        assert decompressed == data
        assert metadata.keys == keys

    def test_compress_invalid_data_type(self):
        """Test compress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            compress("not bytes")  # type: ignore

    def test_decompress_invalid_data_type(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decompress("not bytes")  # type: ignore

    def test_decompress_truncated_payload(self):
        """Test decompress raises ValueError for truncated payload."""
        # Payload with only 1 byte (need at least 2)
        with pytest.raises(ValueError, match="too short"):
            decompress(b"\x00")

    def test_decompress_header_data_mismatch(self):
        """Test decompress raises ValueError when header claims more data than exists."""
        # Header claims 100 bytes of key data, but only 5 bytes follow
        payload = b"\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated"):
            decompress(payload)

    def test_compress_keys_too_large(self):
        """Test compress raises ValueError when key metadata exceeds 64KB."""
        data = b"data"
        # Create keys that will exceed 65535 bytes when JSON-encoded
        huge_keys = {f"key_{i}": "x" * 1000 for i in range(100)}
        with pytest.raises(ValueError, match="key metadata too large"):
            compress(data, keys=huge_keys)

    def test_roundtrip_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        keys = {"empty": "payload"}
        compressed = compress(data, keys=keys)
        decompressed, metadata = decompress(compressed)
        assert decompressed == data
        assert metadata.keys == keys


class TestSkSemanticIntegration:
    """Test Sk codec integration with semantic.py."""

    def test_semantic_compress_sk_codec(self):
        """Test semantic_compress with Sk codec."""
        data = b"Test message"
        compressed = semantic_compress(data, codec="Sk")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sk_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 500
        compressed = semantic_compress(data, codec="Sk")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sk_with_domain_template(self):
        """Test Sk codec with domain_id and template_id."""
        data = b"Routed message"
        compressed = semantic_compress(
            data, codec="Sk", domain_id=42, template_id=1337
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_keys(self):
        """Test that semantic_decompress returns only data, not keys.

        Note: The semantic layer doesn't expose key metadata in the simple
        API. To access keys, use semantic_key.decompress() directly.
        """
        data = b"message"
        # Compress directly with Sk codec including keys
        from arua.compression.semantic_key import compress as sk_compress

        sk_payload = sk_compress(data, keys={"user": "bob"})

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SK, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SK, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + sk_payload

        # Decompress via semantic API (keys are discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestSkWireFormat:
    """Test wire format details."""

    def test_wire_format_structure(self):
        """Test that wire format is [2-byte length][keys][compressed_data]."""
        data = b"test"
        keys = {"x": "y"}
        compressed = compress(data, keys=keys)

        # First 2 bytes are length
        key_length = (compressed[0] << 8) | compressed[1]
        assert key_length > 0
        assert key_length < len(compressed) - 2

        # Can extract and decode key blob
        key_blob = compressed[2 : 2 + key_length]
        metadata = decode_keys(key_blob)
        assert metadata.keys == keys

    def test_zero_length_keys(self):
        """Test wire format with zero-length key blob."""
        data = b"data"
        compressed = compress(data, keys=None)

        # First 2 bytes should indicate small (but non-zero) key blob
        # because we encode empty dict as JSON
        key_length = (compressed[0] << 8) | compressed[1]
        assert key_length > 0  # '{"keys":{}}' is ~11 bytes

    def test_key_value_coercion_to_string(self):
        """Test that non-string keys/values are coerced to strings."""
        data = b"payload"
        # Pass in integers as keys/values
        keys_in = {123: 456, "user": 789}  # type: ignore
        compressed = compress(data, keys=keys_in)
        decompressed, metadata = decompress(compressed)

        # Should be coerced to strings
        assert metadata.keys == {"123": "456", "user": "789"}
        assert decompressed == data
