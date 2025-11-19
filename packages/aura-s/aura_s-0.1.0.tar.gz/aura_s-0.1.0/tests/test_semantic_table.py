"""Tests for Semantic Table (St) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_table import (
    TableColumn,
    TableSchema,
    compress,
    decompress,
    encode_table,
    decode_table,
    infer_schema,
)


class TestTableSchema:
    """Test TableSchema and TableColumn dataclasses."""

    def test_table_column_creation(self):
        """Test creating TableColumn instances."""
        col = TableColumn(name="id", type="int")
        assert col.name == "id"
        assert col.type == "int"

    def test_table_schema_creation(self):
        """Test creating TableSchema instances."""
        columns = (
            TableColumn(name="id", type="int"),
            TableColumn(name="name", type="string"),
        )
        schema = TableSchema(columns=columns)
        assert len(schema.columns) == 2
        assert schema.columns[0].name == "id"

    def test_infer_schema_from_rows(self):
        """Test schema inference from row data."""
        rows = [
            {"id": 1, "name": "Alice", "score": 95.5},
            {"id": 2, "name": "Bob", "score": 87.0},
        ]
        schema = infer_schema(rows)
        assert len(schema.columns) == 3
        # Check inferred types
        col_types = {col.name: col.type for col in schema.columns}
        assert col_types["id"] == "int"
        assert col_types["name"] == "string"
        assert col_types["score"] == "float"

    def test_infer_schema_empty_rows(self):
        """Test schema inference from empty rows."""
        schema = infer_schema([])
        assert len(schema.columns) == 0


class TestTableEncoding:
    """Test low-level table encoding/decoding."""

    def test_encode_decode_simple_table(self):
        """Test encoding and decoding a simple table."""
        rows = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        encoded = encode_table(rows)
        decoded_rows, schema, header, plan = decode_table(encoded)
        assert len(decoded_rows) == 2
        assert decoded_rows[0]["id"] == 1
        assert decoded_rows[0]["name"] == "Alice"
        assert decoded_rows[1]["id"] == 2
        assert decoded_rows[1]["name"] == "Bob"
        assert len(schema.columns) == 2

    def test_encode_decode_with_explicit_schema(self):
        """Test encoding with explicit schema."""
        rows = [
            {"id": 1, "value": 10.5},
            {"id": 2, "value": 20.3},
        ]
        schema = TableSchema(
            columns=(
                TableColumn(name="id", type="int"),
                TableColumn(name="value", type="float"),
            )
        )
        encoded = encode_table(rows, schema=schema)
        decoded_rows, decoded_schema, _, _ = decode_table(encoded)
        assert len(decoded_rows) == 2
        assert decoded_schema.columns[0].type == "int"
        assert decoded_schema.columns[1].type == "float"

    def test_encode_decode_empty_table(self):
        """Test encoding empty table."""
        rows = []
        encoded = encode_table(rows)
        decoded_rows, schema, _, _ = decode_table(encoded)
        assert len(decoded_rows) == 0
        assert len(schema.columns) == 0

    def test_encode_decode_complex_values(self):
        """Test encoding table with complex values."""
        rows = [
            {"id": 1, "data": {"nested": "value"}, "count": 42},
            {"id": 2, "data": {"nested": "other"}, "count": 99},
        ]
        encoded = encode_table(rows)
        decoded_rows, schema, _, _ = decode_table(encoded)
        assert decoded_rows[0]["data"]["nested"] == "value"
        assert decoded_rows[1]["count"] == 99

    def test_decode_invalid_codec(self):
        """Test decode_table raises ValueError for wrong codec."""
        # Create a payload with wrong codec label
        from arua.compression.semantic import semantic_compress

        data = b"not a table"
        payload = semantic_compress(data, codec="Sb")  # Wrong codec

        # Extract body (skip 4-byte header)
        body = payload[4:]

        with pytest.raises(ValueError, match="expected St payload"):
            decode_table(body)


class TestStCompression:
    """Test St codec compression and decompression."""

    def test_compress_decompress_simple_schema(self):
        """Test compress/decompress with simple table schema."""
        data = b"table data"
        schema = TableSchema(
            columns=(
                TableColumn(name="id", type="int"),
                TableColumn(name="name", type="string"),
            )
        )
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert decompressed == data
        assert len(decoded_schema.columns) == 2
        assert decoded_schema.columns[0].name == "id"
        assert decoded_schema.columns[1].type == "string"

    def test_compress_decompress_no_schema(self):
        """Test compress/decompress with no schema (empty schema)."""
        data = b"plain data"
        compressed = compress(data)
        decompressed, decoded_schema = decompress(compressed)
        assert decompressed == data
        assert len(decoded_schema.columns) == 0

    def test_compress_decompress_complex_schema(self):
        """Test compress/decompress with complex table schema."""
        data = b"complex table"
        schema = TableSchema(
            columns=(
                TableColumn(name="user_id", type="int"),
                TableColumn(name="username", type="string"),
                TableColumn(name="score", type="float"),
                TableColumn(name="active", type="bool"),
                TableColumn(name="metadata", type="mixed"),
            )
        )
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert decompressed == data
        assert len(decoded_schema.columns) == 5
        assert decoded_schema.columns[2].name == "score"
        assert decoded_schema.columns[2].type == "float"

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        schema = TableSchema(columns=(TableColumn(name="data", type="string"),))
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert decompressed == data
        assert len(decoded_schema.columns) == 1

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        schema = TableSchema(columns=(TableColumn(name="bytes", type="string"),))
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert decompressed == data

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        schema = TableSchema(columns=(TableColumn(name="empty", type="null"),))
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert decompressed == data
        assert decoded_schema.columns[0].type == "null"

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

    def test_decompress_truncated_schema_blob(self):
        """Test decompress raises ValueError for truncated schema blob."""
        # Header says 100 bytes, but only 5 bytes follow
        payload = b"\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated before schema blob"):
            decompress(payload)

    def test_compress_schema_too_large(self):
        """Test compress raises ValueError for table schema too large."""
        # Create enormous schema to exceed 65535 bytes
        columns = [
            TableColumn(name="x" * 1000 + str(i), type="string") for i in range(100)
        ]
        schema = TableSchema(columns=tuple(columns))
        with pytest.raises(ValueError, match="table schema too large"):
            compress(b"data", schema=schema)

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        data = b"test"
        schema = TableSchema(columns=(TableColumn(name="col1", type="int"),))
        compressed = compress(data, schema=schema)

        # First 2 bytes are length
        schema_length = (compressed[0] << 8) | compressed[1]
        assert schema_length > 0

        # Next schema_length bytes are the schema blob
        schema_blob = compressed[2 : 2 + schema_length]
        import json
        schema_dict = json.loads(schema_blob.decode("utf-8"))
        assert "columns" in schema_dict
        assert schema_dict["columns"][0]["name"] == "col1"


class TestStSemanticIntegration:
    """Test St codec integration with semantic.py."""

    def test_semantic_compress_st_codec(self):
        """Test semantic_compress with St codec."""
        data = b"table message"
        compressed = semantic_compress(data, codec="St")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_st_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="St")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_st_with_domain_template(self):
        """Test St codec with domain_id and template_id."""
        data = b"routed table"
        compressed = semantic_compress(
            data, codec="St", domain_id=20, template_id=5000
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_schema(self):
        """Test that semantic_decompress returns only data, not schema.

        Note: The semantic layer doesn't expose table schema in the simple
        API. To access schema, use semantic_table.decompress() directly.
        """
        data = b"table message"
        # Compress directly with St codec including schema
        from arua.compression.semantic_table import compress as st_compress

        schema = TableSchema(
            columns=(
                TableColumn(name="id", type="int"),
                TableColumn(name="value", type="float"),
            )
        )
        st_payload = st_compress(data, schema=schema)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_ST, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_ST, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + st_payload

        # Decompress via semantic API (schema is discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestStEdgeCases:
    """Test edge cases for St codec."""

    def test_schema_with_all_types(self):
        """Test schema with all supported column types."""
        schema = TableSchema(
            columns=(
                TableColumn(name="col_int", type="int"),
                TableColumn(name="col_float", type="float"),
                TableColumn(name="col_string", type="string"),
                TableColumn(name="col_bool", type="bool"),
                TableColumn(name="col_null", type="null"),
                TableColumn(name="col_mixed", type="mixed"),
            )
        )
        data = b"all types"
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert len(decoded_schema.columns) == 6
        col_types = {col.name: col.type for col in decoded_schema.columns}
        assert col_types["col_int"] == "int"
        assert col_types["col_bool"] == "bool"
        assert col_types["col_mixed"] == "mixed"

    def test_schema_with_unicode_column_names(self):
        """Test schema with unicode column names."""
        schema = TableSchema(
            columns=(
                TableColumn(name="identifiant", type="int"),
                TableColumn(name="données", type="string"),
            )
        )
        data = b"unicode columns"
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert decoded_schema.columns[0].name == "identifiant"
        assert decoded_schema.columns[1].name == "données"

    def test_many_columns(self):
        """Test schema with many columns."""
        columns = [TableColumn(name=f"col_{i}", type="int") for i in range(100)]
        schema = TableSchema(columns=tuple(columns))
        data = b"many columns"
        compressed = compress(data, schema=schema)
        decompressed, decoded_schema = decompress(compressed)
        assert len(decoded_schema.columns) == 100

    def test_realistic_user_table(self):
        """Test realistic user table scenario."""
        rows = [
            {"user_id": 1, "username": "alice", "email": "alice@example.com", "active": True, "score": 95.5},
            {"user_id": 2, "username": "bob", "email": "bob@example.com", "active": False, "score": 87.0},
            {"user_id": 3, "username": "charlie", "email": "charlie@example.com", "active": True, "score": 92.3},
        ]
        encoded = encode_table(rows)
        decoded_rows, schema, _, _ = decode_table(encoded)

        assert len(decoded_rows) == 3
        assert decoded_rows[0]["username"] == "alice"
        assert decoded_rows[1]["active"] is False
        assert decoded_rows[2]["score"] == 92.3

        col_names = [col.name for col in schema.columns]
        assert "user_id" in col_names
        assert "email" in col_names

    def test_realistic_log_table(self):
        """Test realistic log event table."""
        rows = [
            {
                "timestamp": 1705315800000,
                "level": "ERROR",
                "message": "Connection timeout",
                "source": "api-gateway",
                "trace_id": "trace-123"
            },
            {
                "timestamp": 1705315801000,
                "level": "INFO",
                "message": "Request processed",
                "source": "data-service",
                "trace_id": "trace-124"
            },
        ]
        encoded = encode_table(rows)
        decoded_rows, schema, _, _ = decode_table(encoded)

        assert len(decoded_rows) == 2
        assert decoded_rows[0]["level"] == "ERROR"
        assert decoded_rows[1]["message"] == "Request processed"
