"""Tests for Semantic Pattern (Sp) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_pattern import (
    compress,
    decompress,
    encode_pattern,
    decode_pattern,
)


class TestPatternEncoding:
    """Test low-level pattern encoding/decoding."""

    def test_encode_decode_simple_pattern(self):
        """Test encoding and decoding a simple pattern."""
        pattern = "User {user_id} logged in"
        fields = {"user_id": "alice"}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern
        assert decoded_fields == fields

    def test_encode_decode_multiple_fields(self):
        """Test encoding and decoding pattern with multiple fields."""
        pattern = "{level}: {message} at {timestamp}"
        fields = {"level": "ERROR", "message": "Connection failed", "timestamp": "2024-01-15T10:30:00Z"}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern
        assert decoded_fields == fields

    def test_encode_decode_empty_pattern(self):
        """Test encoding and decoding empty pattern."""
        pattern = ""
        fields = {}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == ""
        assert decoded_fields == {}

    def test_encode_decode_nested_values(self):
        """Test encoding pattern with nested field values."""
        pattern = "Event: {event}"
        fields = {"event": {"type": "click", "target": "button"}, "count": 5}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern
        assert decoded_fields["event"] == {"type": "click", "target": "button"}
        assert decoded_fields["count"] == 5

    def test_encode_decode_unicode_pattern(self):
        """Test encoding pattern with unicode characters."""
        pattern = "Événement: {événement} à {heure}"
        fields = {"événement": "connexion", "heure": "10h30"}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern
        assert decoded_fields == fields

    def test_decode_invalid_json(self):
        """Test decode_pattern raises ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="invalid Sp payload JSON"):
            decode_pattern(b"not json")

    def test_decode_missing_pattern_key(self):
        """Test decode_pattern raises ValueError for missing pattern key."""
        with pytest.raises(ValueError, match="must contain 'pattern' and 'fields' keys"):
            decode_pattern(b'{"fields": {}}')

    def test_decode_missing_fields_key(self):
        """Test decode_pattern raises ValueError for missing fields key."""
        with pytest.raises(ValueError, match="must contain 'pattern' and 'fields' keys"):
            decode_pattern(b'{"pattern": "test"}')

    def test_decode_fields_not_dict(self):
        """Test decode_pattern raises ValueError when fields is not a dict."""
        with pytest.raises(ValueError, match="'fields' must be a JSON object"):
            decode_pattern(b'{"pattern": "test", "fields": "not a dict"}')

    def test_decode_non_bytes_raises(self):
        """Test decode_pattern raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decode_pattern("not bytes")  # type: ignore

    def test_json_format(self):
        """Test that encoded JSON has expected structure."""
        pattern = "Log: {msg}"
        fields = {"msg": "test"}
        encoded = encode_pattern(pattern, fields)
        text = encoded.decode("utf-8")
        assert '"pattern":"Log: {msg}"' in text
        assert '"fields":{"msg":"test"}' in text


class TestSpCompression:
    """Test Sp codec compression and decompression."""

    def test_compress_decompress_simple_pattern(self):
        """Test compress/decompress with simple pattern."""
        data = b"log data"
        pattern = "User {user} action {action}"
        fields = {"user": "bob", "action": "login"}
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_pattern == pattern
        assert decoded_fields == fields

    def test_compress_decompress_no_pattern(self):
        """Test compress/decompress with no pattern (empty pattern)."""
        data = b"plain data"
        compressed = compress(data)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_pattern == ""
        assert decoded_fields == {}

    def test_compress_decompress_complex_fields(self):
        """Test compress/decompress with complex field values."""
        data = b"event payload"
        pattern = "Event {type} from {source}"
        fields = {
            "type": "error",
            "source": {"service": "api", "host": "server-1"},
            "metadata": {"severity": "high", "count": 42}
        }
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_pattern == pattern
        assert decoded_fields == fields

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        pattern = "Large data chunk {id}"
        fields = {"id": "chunk-001"}
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_pattern == pattern

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        pattern = "Binary message"
        fields = {"format": "raw"}
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_fields["format"] == "raw"

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        pattern = "Empty event"
        fields = {}
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_pattern == pattern

    def test_compress_invalid_data_type(self):
        """Test compress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            compress("not bytes")  # type: ignore

    def test_decompress_invalid_data_type(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decompress("not bytes")  # type: ignore

    def test_decompress_truncated_header(self):
        """Test decompress raises ValueError for truncated length header."""
        with pytest.raises(ValueError, match="too short for length header"):
            decompress(b"\x00")

    def test_decompress_truncated_pattern_blob(self):
        """Test decompress raises ValueError for truncated pattern blob."""
        # Header says 100 bytes, but only 5 bytes follow
        payload = b"\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated before pattern blob"):
            decompress(payload)

    def test_compress_pattern_too_large(self):
        """Test compress raises ValueError for pattern metadata too large."""
        # Create enormous pattern to exceed 65535 bytes
        # JSON overhead: {"pattern":"...","fields":{...}}
        # Need to ensure the JSON exceeds 65535 bytes
        pattern = "x" * 50000  # 50KB pattern
        fields = {"field_" + str(i): "value_" + str(i) * 100 for i in range(200)}
        with pytest.raises(ValueError, match="pattern metadata too large"):
            compress(b"data", pattern=pattern, fields=fields)

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        data = b"test"
        pattern = "Test {field}"
        fields = {"field": "value"}
        compressed = compress(data, pattern=pattern, fields=fields)

        # First 2 bytes are length
        pattern_length = (compressed[0] << 8) | compressed[1]
        assert pattern_length > 0

        # Next pattern_length bytes are the pattern blob
        pattern_blob = compressed[2 : 2 + pattern_length]
        decoded_pattern, decoded_fields = decode_pattern(pattern_blob)
        assert decoded_pattern == pattern
        assert decoded_fields == fields


class TestSpSemanticIntegration:
    """Test Sp codec integration with semantic.py."""

    def test_semantic_compress_sp_codec(self):
        """Test semantic_compress with Sp codec."""
        data = b"structured event"
        compressed = semantic_compress(data, codec="Sp")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sp_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="Sp")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sp_with_domain_template(self):
        """Test Sp codec with domain_id and template_id."""
        data = b"routed pattern"
        compressed = semantic_compress(
            data, codec="Sp", domain_id=5, template_id=1234
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_pattern(self):
        """Test that semantic_decompress returns only data, not pattern.

        Note: The semantic layer doesn't expose pattern metadata in the simple
        API. To access pattern info, use semantic_pattern.decompress() directly.
        """
        data = b"event message"
        # Compress directly with Sp codec including pattern
        from arua.compression.semantic_pattern import compress as sp_compress

        pattern = "Event: {event_type}"
        fields = {"event_type": "login"}
        sp_payload = sp_compress(data, pattern=pattern, fields=fields)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SP, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SP, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + sp_payload

        # Decompress via semantic API (pattern is discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestSpEdgeCases:
    """Test edge cases for Sp codec."""

    def test_pattern_with_no_placeholders(self):
        """Test pattern string with no placeholders."""
        pattern = "Static log message"
        fields = {}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern
        assert decoded_fields == {}

    def test_many_fields(self):
        """Test pattern with many fields."""
        pattern = "Multi-field event"
        fields = {f"field_{i}": f"value_{i}" for i in range(100)}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern
        assert len(decoded_fields) == 100

    def test_special_characters_in_pattern(self):
        """Test pattern with special characters."""
        pattern = 'Pattern with "quotes" and {brackets} and [arrays]'
        fields = {"brackets": "value"}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_pattern == pattern

    def test_numeric_and_boolean_field_values(self):
        """Test fields with numeric and boolean values."""
        pattern = "Metrics: {count} errors, enabled: {enabled}"
        fields = {"count": 42, "enabled": True, "ratio": 3.14}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_fields["count"] == 42
        assert decoded_fields["enabled"] is True
        assert decoded_fields["ratio"] == 3.14

    def test_null_field_value(self):
        """Test field with null value."""
        pattern = "Event {data}"
        fields = {"data": None}
        encoded = encode_pattern(pattern, fields)
        decoded_pattern, decoded_fields = decode_pattern(encoded)
        assert decoded_fields["data"] is None

    def test_roundtrip_log_format_pattern(self):
        """Test realistic log format pattern."""
        data = b"log entry content"
        pattern = "[{timestamp}] {level}: {message} (source: {source})"
        fields = {
            "timestamp": "2024-01-15T10:30:00.000Z",
            "level": "ERROR",
            "message": "Database connection timeout",
            "source": "db-connector.py:142"
        }
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_pattern == pattern
        assert decoded_fields == fields

    def test_roundtrip_structured_logging(self):
        """Test structured logging use case."""
        data = b"application event"
        pattern = "Application event"
        fields = {
            "event_type": "user_action",
            "user": {"id": "user-123", "role": "admin"},
            "action": "delete_resource",
            "resource": {"type": "document", "id": "doc-456"},
            "timestamp_ms": 1705315800000
        }
        compressed = compress(data, pattern=pattern, fields=fields)
        decompressed, decoded_pattern, decoded_fields = decompress(compressed)
        assert decompressed == data
        assert decoded_fields["user"]["id"] == "user-123"
        assert decoded_fields["resource"]["type"] == "document"
