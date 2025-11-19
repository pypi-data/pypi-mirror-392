"""Tests for Semantic Joint (Sj) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_joint import (
    compress,
    decompress,
    encode_joint,
    decode_joint,
)


class TestJointEncoding:
    """Test low-level joint encoding/decoding."""

    def test_encode_decode_single_payload(self):
        """Test encoding and decoding a single payload."""
        payloads = [b"single payload"]
        encoded = encode_joint(payloads)
        decoded = decode_joint(encoded)
        assert decoded == payloads

    def test_encode_decode_multiple_payloads(self):
        """Test encoding and decoding multiple payloads."""
        payloads = [b"first", b"second", b"third"]
        encoded = encode_joint(payloads)
        decoded = decode_joint(encoded)
        assert decoded == payloads

    def test_encode_decode_empty_payloads(self):
        """Test encoding and decoding with empty payloads."""
        payloads = [b"", b"data", b""]
        encoded = encode_joint(payloads)
        decoded = decode_joint(encoded)
        assert decoded == payloads

    def test_encode_decode_large_payloads(self):
        """Test encoding and decoding large payloads."""
        payloads = [b"x" * 10000, b"y" * 5000, b"z" * 20000]
        encoded = encode_joint(payloads)
        decoded = decode_joint(encoded)
        assert decoded == payloads

    def test_encode_decode_binary_payloads(self):
        """Test encoding and decoding binary payloads."""
        payloads = [bytes(range(256)), bytes(range(128)), bytes(range(64, 192))]
        encoded = encode_joint(payloads)
        decoded = decode_joint(encoded)
        assert decoded == payloads

    def test_decode_truncated_count(self):
        """Test decode_joint raises ValueError for truncated count."""
        with pytest.raises(ValueError, match="too short for count header"):
            decode_joint(b"\x00\x00")

    def test_decode_truncated_length(self):
        """Test decode_joint raises ValueError for truncated length."""
        # Count=1, but length header is incomplete
        payload = b"\x00\x00\x00\x01\x00"
        with pytest.raises(ValueError, match="truncated before length"):
            decode_joint(payload)

    def test_decode_truncated_payload(self):
        """Test decode_joint raises ValueError for truncated payload."""
        # Count=1, length=100, but only 5 bytes follow
        payload = b"\x00\x00\x00\x01\x00\x00\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated before payload bytes"):
            decode_joint(payload)

    def test_decode_extra_data(self):
        """Test decode_joint raises ValueError for extra data."""
        # Valid joint body with extra bytes at the end
        payloads = [b"data"]
        encoded = encode_joint(payloads)
        with pytest.raises(ValueError, match="extra data at end"):
            decode_joint(encoded + b"extra")

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        payloads = [b"abc", b"de"]
        encoded = encode_joint(payloads)

        # Should start with count (2) as u32 big-endian
        assert encoded[:4] == b"\x00\x00\x00\x02"

        # First payload: length=3, data="abc"
        assert encoded[4:8] == b"\x00\x00\x00\x03"
        assert encoded[8:11] == b"abc"

        # Second payload: length=2, data="de"
        assert encoded[11:15] == b"\x00\x00\x00\x02"
        assert encoded[15:17] == b"de"


class TestSjCompression:
    """Test Sj codec compression and decompression."""

    def test_compress_decompress_single_payload(self):
        """Test compress/decompress with a single payload."""
        payloads = [b"single item"]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads

    def test_compress_decompress_multiple_payloads(self):
        """Test compress/decompress with multiple payloads."""
        payloads = [b"part 1", b"part 2", b"part 3", b"part 4"]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads

    def test_compress_decompress_mixed_sizes(self):
        """Test compress/decompress with payloads of different sizes."""
        payloads = [b"tiny", b"x" * 1000, b"", b"medium" * 50, b"z"]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payloads."""
        payloads = [bytes(range(100)), bytes(range(50, 150)), bytes(range(200, 256))]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads

    def test_compress_decompress_semantic_payloads(self):
        """Test compress/decompress with actual semantic payloads."""
        # Create some semantic payloads
        from arua.compression.semantic import semantic_compress

        payload1 = semantic_compress(b"text data", codec="Sa")
        payload2 = semantic_compress(b"binary data", codec="Sb")
        payload3 = semantic_compress(b"flow data", codec="Sf")

        # Bundle them with Sj
        payloads = [payload1, payload2, payload3]
        compressed = compress(payloads)
        decompressed = decompress(compressed)

        assert len(decompressed) == 3
        assert decompressed[0] == payload1
        assert decompressed[1] == payload2
        assert decompressed[2] == payload3

    def test_compress_empty_list_raises(self):
        """Test compress raises ValueError for empty list."""
        with pytest.raises(ValueError, match="requires at least one payload"):
            compress([])

    def test_compress_non_bytes_raises(self):
        """Test compress raises TypeError for non-bytes payloads."""
        with pytest.raises(TypeError, match="must be bytes-like objects"):
            compress([b"valid", "not bytes"])  # type: ignore

    def test_decompress_invalid_type_raises(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decompress("not bytes")  # type: ignore

    def test_compress_iterable_payloads(self):
        """Test compress works with iterable (not just list)."""
        payloads = (b"gen" + bytes([i]) for i in range(5))
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert len(decompressed) == 5

    def test_roundtrip_many_payloads(self):
        """Test roundtrip with many payloads."""
        payloads = [f"payload {i}".encode() for i in range(100)]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads

    def test_roundtrip_large_joint_container(self):
        """Test roundtrip with large joint container."""
        # Each payload is 1KB, 50 payloads = ~50KB joint
        payloads = [bytes([i % 256]) * 1024 for i in range(50)]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert len(decompressed) == 50
        assert all(len(p) == 1024 for p in decompressed)


class TestSjSemanticIntegration:
    """Test Sj codec integration with semantic.py."""

    def test_semantic_compress_sj_with_pre_encoded_joint(self):
        """Test semantic_compress with Sj using pre-encoded joint body."""
        # Manually encode a joint body
        payloads = [b"a", b"b", b"c"]
        joint_body = encode_joint(payloads)

        # Compress it with Sj semantic wrapper
        compressed = semantic_compress(joint_body, codec="Sj")

        # Decompress
        decompressed = semantic_decompress(compressed)

        # Should get back the joint-encoded body
        assert decompressed == joint_body

        # Decode the joint body to get original payloads
        final_payloads = decode_joint(decompressed)
        assert final_payloads == payloads

    def test_semantic_compress_sj_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        payloads = [b"payload A", b"payload B"]
        joint_body = encode_joint(payloads)

        compressed = semantic_compress(joint_body, codec="Sj")
        decompressed = semantic_decompress(compressed)

        assert decode_joint(decompressed) == payloads

    def test_semantic_compress_sj_with_domain_template(self):
        """Test Sj codec with domain_id and template_id."""
        payloads = [b"multi", b"modal", b"message"]
        joint_body = encode_joint(payloads)

        compressed = semantic_compress(
            joint_body, codec="Sj", domain_id=10, template_id=999
        )
        decompressed = semantic_decompress(compressed)

        assert decode_joint(decompressed) == payloads


class TestSjHelperIntegration:
    """Test Sj integration with helper functions."""

    def test_encode_semantic_joint_helper(self):
        """Test the helper function encode_semantic_joint if it exists."""
        # Check if helper exists
        try:
            from arua.compression.helpers import (
                encode_semantic_joint,
                decode_semantic_joint,
            )

            payloads = [b"p1", b"p2", b"p3"]
            encoded = encode_semantic_joint(payloads)
            decoded_payloads, header, plan = decode_semantic_joint(encoded)

            assert decoded_payloads == payloads
            assert header.codec_id == 0x0B  # CODEC_ID_SJ
        except ImportError:
            # Helper not yet implemented, skip
            pytest.skip("encode_semantic_joint helper not yet implemented")


class TestSjEdgeCases:
    """Test edge cases for Sj codec."""

    def test_single_empty_payload(self):
        """Test joint with single empty payload."""
        payloads = [b""]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == [b""]

    def test_all_empty_payloads(self):
        """Test joint with all empty payloads."""
        payloads = [b"", b"", b""]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == [b"", b"", b""]

    def test_payloads_with_null_bytes(self):
        """Test payloads containing null bytes."""
        payloads = [b"\x00\x00\x00", b"test\x00data", b"\x00"]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads

    def test_single_large_payload(self):
        """Test joint with single large payload."""
        payloads = [b"x" * 1000000]  # 1MB payload
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert decompressed == payloads
        assert len(decompressed[0]) == 1000000

    def test_many_small_payloads(self):
        """Test joint with many tiny payloads."""
        payloads = [bytes([i % 256]) for i in range(1000)]
        compressed = compress(payloads)
        decompressed = decompress(compressed)
        assert len(decompressed) == 1000
        assert decompressed == payloads
