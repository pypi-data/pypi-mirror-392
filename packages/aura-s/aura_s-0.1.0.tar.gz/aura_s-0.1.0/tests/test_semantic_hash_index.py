"""Tests for Semantic Hash (Sh) and Semantic Index (Si) codecs."""

from __future__ import annotations

import hashlib

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_hash import (
    HashMetadata,
    compress as hash_compress,
    decompress as hash_decompress,
    encode_hash,
    decode_hash,
    verify_hash,
)
from arua.compression.semantic_index import (
    IndexMetadata,
    compress as index_compress,
    decompress as index_decompress,
    encode_index,
    decode_index,
)


class TestHashEncoding:
    """Test low-level hash encoding/decoding."""

    def test_encode_decode_sha256(self):
        """Test encoding and decoding SHA256 hash."""
        data = b"hello world"
        encoded = encode_hash(data, algorithm="sha256")
        algorithm, digest = decode_hash(encoded)
        assert algorithm == "sha256"
        assert digest == hashlib.sha256(data).digest()

    def test_encode_decode_sha512(self):
        """Test encoding and decoding SHA512 hash."""
        data = b"test data"
        encoded = encode_hash(data, algorithm="sha512")
        algorithm, digest = decode_hash(encoded)
        assert algorithm == "sha512"
        assert digest == hashlib.sha512(data).digest()

    def test_encode_decode_md5(self):
        """Test encoding and decoding MD5 hash."""
        data = b"legacy hash"
        encoded = encode_hash(data, algorithm="md5")
        algorithm, digest = decode_hash(encoded)
        assert algorithm == "md5"
        assert digest == hashlib.md5(data).digest()

    def test_encode_decode_blake2b(self):
        """Test encoding and decoding BLAKE2b hash."""
        data = b"modern hash"
        encoded = encode_hash(data, algorithm="blake2b")
        algorithm, digest = decode_hash(encoded)
        assert algorithm == "blake2b"
        assert digest == hashlib.blake2b(data).digest()

    def test_verify_hash_valid(self):
        """Test verify_hash with valid data."""
        data = b"verify me"
        encoded = encode_hash(data, algorithm="sha256")
        assert verify_hash(data, encoded) is True

    def test_verify_hash_invalid(self):
        """Test verify_hash with invalid data."""
        data = b"original"
        encoded = encode_hash(data, algorithm="sha256")
        assert verify_hash(b"modified", encoded) is False

    def test_encode_invalid_algorithm(self):
        """Test encode_hash with invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match="unsupported hash algorithm"):
            encode_hash(b"data", algorithm="invalid_algo")

    def test_decode_truncated_payload(self):
        """Test decode_hash with truncated payload raises ValueError."""
        with pytest.raises(ValueError, match="payload too short"):
            decode_hash(b"\x05")

    def test_decode_truncated_algorithm(self):
        """Test decode_hash with truncated algorithm name."""
        # Header says 10 bytes for algorithm, but only 3 bytes follow
        payload = b"\x0Asha"
        with pytest.raises(ValueError, match="truncated while reading algorithm"):
            decode_hash(payload)


class TestShCompression:
    """Test Sh codec compression and decompression."""

    def test_compress_decompress_default_algorithm(self):
        """Test compress/decompress with default SHA256."""
        data = b"important content"
        compressed = hash_compress(data)
        decompressed, algorithm, digest = hash_decompress(compressed)
        assert decompressed == data
        assert algorithm == "sha256"
        assert digest == hashlib.sha256(data).digest()

    def test_compress_decompress_custom_algorithm(self):
        """Test compress/decompress with SHA512."""
        data = b"secure data"
        compressed = hash_compress(data, algorithm="sha512")
        decompressed, algorithm, digest = hash_decompress(compressed)
        assert decompressed == data
        assert algorithm == "sha512"
        assert digest == hashlib.sha512(data).digest()

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        compressed = hash_compress(data, algorithm="sha256")
        decompressed, algorithm, digest = hash_decompress(compressed)
        assert decompressed == data
        assert algorithm == "sha256"
        assert len(digest) == 32  # SHA256 produces 32 bytes

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        compressed = hash_compress(data, algorithm="blake2b")
        decompressed, algorithm, digest = hash_decompress(compressed)
        assert decompressed == data
        assert algorithm == "blake2b"

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        compressed = hash_compress(data)
        decompressed, algorithm, digest = hash_decompress(compressed)
        assert decompressed == data
        assert digest == hashlib.sha256(b"").digest()

    def test_compress_invalid_data_type(self):
        """Test compress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            hash_compress("not bytes")  # type: ignore

    def test_decompress_invalid_data_type(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            hash_decompress("not bytes")  # type: ignore

    def test_decompress_truncated_payload(self):
        """Test decompress raises ValueError for truncated payload."""
        with pytest.raises(ValueError, match="too short"):
            hash_decompress(b"\x00")

    def test_hash_integrity_check(self):
        """Test that hash can be used to verify data integrity."""
        data = b"verify this data"
        compressed = hash_compress(data, algorithm="sha256")
        decompressed, algorithm, digest = hash_decompress(compressed)

        # Manually verify the hash
        expected_digest = hashlib.sha256(data).digest()
        assert digest == expected_digest


class TestShSemanticIntegration:
    """Test Sh codec integration with semantic.py."""

    def test_semantic_compress_sh_codec(self):
        """Test semantic_compress with Sh codec."""
        data = b"hash me"
        compressed = semantic_compress(data, codec="Sh")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sh_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="Sh")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_sh_with_domain_template(self):
        """Test Sh codec with domain_id and template_id."""
        data = b"routed hash"
        compressed = semantic_compress(
            data, codec="Sh", domain_id=99, template_id=5555
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data


class TestIndexEncoding:
    """Test low-level index encoding/decoding."""

    def test_encode_decode_index(self):
        """Test encoding and decoding index metadata."""
        index = IndexMetadata(doc_id=12345, section_id=42, shard_id=7, offset=1024)
        encoded = encode_index(index)
        decoded = decode_index(encoded)
        assert decoded.doc_id == 12345
        assert decoded.section_id == 42
        assert decoded.shard_id == 7
        assert decoded.offset == 1024

    def test_encode_decode_zero_values(self):
        """Test encoding and decoding all-zero index."""
        index = IndexMetadata(doc_id=0, section_id=0, shard_id=0, offset=0)
        encoded = encode_index(index)
        decoded = decode_index(encoded)
        assert decoded.doc_id == 0
        assert decoded.section_id == 0
        assert decoded.shard_id == 0
        assert decoded.offset == 0

    def test_encode_decode_max_values(self):
        """Test encoding and decoding maximum values."""
        index = IndexMetadata(
            doc_id=2**64 - 1,  # Max u64
            section_id=2**32 - 1,  # Max u32
            shard_id=2**32 - 1,  # Max u32
            offset=2**64 - 1,  # Max u64
        )
        encoded = encode_index(index)
        decoded = decode_index(encoded)
        assert decoded.doc_id == index.doc_id
        assert decoded.section_id == index.section_id
        assert decoded.shard_id == index.shard_id
        assert decoded.offset == index.offset

    def test_encode_fixed_size(self):
        """Test that encoded index is always 24 bytes."""
        index = IndexMetadata(doc_id=1, section_id=2, shard_id=3, offset=4)
        encoded = encode_index(index)
        assert len(encoded) == 24  # 8 + 4 + 4 + 8 = 24 bytes

    def test_decode_invalid_size(self):
        """Test decode_index raises ValueError for wrong size."""
        with pytest.raises(ValueError, match="invalid index payload size"):
            decode_index(b"short")

    def test_decode_invalid_type(self):
        """Test decode_index raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decode_index("not bytes")  # type: ignore


class TestSiCompression:
    """Test Si codec compression and decompression."""

    def test_compress_decompress_with_index(self):
        """Test compress/decompress with index metadata."""
        data = b"document chunk"
        index = IndexMetadata(doc_id=999, section_id=5, shard_id=2, offset=4096)
        compressed = index_compress(data, index=index)
        decompressed, idx = index_decompress(compressed)
        assert decompressed == data
        assert idx.doc_id == 999
        assert idx.section_id == 5
        assert idx.shard_id == 2
        assert idx.offset == 4096

    def test_compress_decompress_no_index(self):
        """Test compress/decompress with no index (zeros)."""
        data = b"no index metadata"
        compressed = index_compress(data)
        decompressed, idx = index_decompress(compressed)
        assert decompressed == data
        assert idx.doc_id == 0
        assert idx.section_id == 0
        assert idx.shard_id == 0
        assert idx.offset == 0

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"z" * 100000
        index = IndexMetadata(doc_id=10000, section_id=100, shard_id=10, offset=0)
        compressed = index_compress(data, index=index)
        decompressed, idx = index_decompress(compressed)
        assert decompressed == data
        assert idx.doc_id == 10000

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        index = IndexMetadata(doc_id=42, section_id=1, shard_id=0, offset=256)
        compressed = index_compress(data, index=index)
        decompressed, idx = index_decompress(compressed)
        assert decompressed == data
        assert idx.offset == 256

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        index = IndexMetadata(doc_id=0, section_id=0, shard_id=0, offset=0)
        compressed = index_compress(data, index=index)
        decompressed, idx = index_decompress(compressed)
        assert decompressed == data

    def test_compress_invalid_data_type(self):
        """Test compress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            index_compress("not bytes")  # type: ignore

    def test_decompress_invalid_data_type(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            index_decompress("not bytes")  # type: ignore

    def test_decompress_truncated_payload(self):
        """Test decompress raises ValueError for truncated payload."""
        # Less than 24 bytes
        with pytest.raises(ValueError, match="too short"):
            index_decompress(b"short")

    def test_wire_format_structure(self):
        """Test that wire format is [24-byte index][compressed_data]."""
        data = b"test"
        index = IndexMetadata(doc_id=123, section_id=4, shard_id=5, offset=678)
        compressed = index_compress(data, index=index)

        # First 24 bytes are index metadata
        assert len(compressed) >= 24
        index_blob = compressed[:24]
        decoded_idx = decode_index(index_blob)
        assert decoded_idx.doc_id == 123
        assert decoded_idx.section_id == 4
        assert decoded_idx.shard_id == 5
        assert decoded_idx.offset == 678


class TestSiSemanticIntegration:
    """Test Si codec integration with semantic.py."""

    def test_semantic_compress_si_codec(self):
        """Test semantic_compress with Si codec."""
        data = b"indexed content"
        compressed = semantic_compress(data, codec="Si")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_si_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"B" * 2000
        compressed = semantic_compress(data, codec="Si")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_si_with_domain_template(self):
        """Test Si codec with domain_id and template_id."""
        data = b"routed index"
        compressed = semantic_compress(
            data, codec="Si", domain_id=7, template_id=777
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_index(self):
        """Test that semantic_decompress returns only data, not index.

        Note: The semantic layer doesn't expose index metadata in the simple
        API. To access index info, use semantic_index.decompress() directly.
        """
        data = b"message"
        # Compress directly with Si codec including index
        from arua.compression.semantic_index import compress as si_compress

        index = IndexMetadata(doc_id=555, section_id=6, shard_id=7, offset=888)
        si_payload = si_compress(data, index=index)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SI, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SI, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + si_payload

        # Decompress via semantic API (index is discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestHashAndIndexInterplay:
    """Test interactions between Sh and Si codecs."""

    def test_different_codecs_different_payloads(self):
        """Test that Sh and Si produce different compressed payloads."""
        data = b"same data"
        sh_compressed = hash_compress(data)
        si_compressed = index_compress(data)

        # Payloads should be different due to different metadata
        assert sh_compressed != si_compressed

    def test_roundtrip_independence(self):
        """Test that Sh and Si roundtrips are independent."""
        data = b"codec independence"

        # Sh roundtrip
        sh_compressed = hash_compress(data, algorithm="sha256")
        sh_decompressed, algorithm, digest = hash_decompress(sh_compressed)
        assert sh_decompressed == data

        # Si roundtrip
        index = IndexMetadata(doc_id=1, section_id=2, shard_id=3, offset=4)
        si_compressed = index_compress(data, index=index)
        si_decompressed, idx = index_decompress(si_compressed)
        assert si_decompressed == data

        # Both produce same original data
        assert sh_decompressed == si_decompressed == data
