"""Tests for Ss (Semantic Cache) codec."""

import pytest
from arua.compression.semantic_cache import (
    compress,
    decompress,
    CacheMetadata,
    _build_frequency_table,
    _build_dictionary,
    _substitute_patterns,
    _restore_patterns,
)


class TestCacheHelpers:
    """Test cache helper functions."""

    def test_build_frequency_table_finds_patterns(self):
        """Test frequency table building."""
        data = b"hello world hello world hello"
        freq_table = _build_frequency_table(data, min_length=4)

        # "hello" appears 3 times
        assert freq_table[b"hello"] >= 3
        # "world" appears 2 times
        assert freq_table[b"world"] >= 2

    def test_build_dictionary_selects_frequent_patterns(self):
        """Test dictionary building from frequency table."""
        data = b"the quick brown fox jumps over the lazy dog the quick"
        freq_table = _build_frequency_table(data, min_length=4)
        dictionary = _build_dictionary(freq_table, max_entries=10, min_freq=2)

        # "the " appears 3 times, should be in dictionary
        assert b"the " in dictionary or b"the" in dictionary

    def test_substitute_patterns_replaces_with_refs(self):
        """Test pattern substitution."""
        data = b"AAAABBBBAAAABBBB"
        dictionary = {b"AAAA": 0, b"BBBB": 1}

        substituted = _substitute_patterns(data, dictionary)

        # Should be much shorter (4 patterns replaced by 3-byte refs each)
        assert len(substituted) < len(data)
        # Should contain cache markers
        assert 0xFF in substituted

    def test_restore_patterns_reverses_substitution(self):
        """Test pattern restoration."""
        data = b"TESTTEST"
        dictionary = {b"TEST": 0}

        substituted = _substitute_patterns(data, dictionary)
        dict_list = [b"TEST"]
        restored = _restore_patterns(bytes(substituted), dict_list)

        assert restored == data

    def test_cache_marker_escaping(self):
        """Test that 0xFF bytes are properly escaped."""
        data = b"\xFF\xFF\xFF"  # Three cache marker bytes
        dictionary = {}  # No patterns

        substituted = _substitute_patterns(data, dictionary)
        restored = _restore_patterns(bytes(substituted), [])

        assert restored == data


class TestCacheCompression:
    """Test cache compression/decompression."""

    def test_compress_decompress_roundtrip(self):
        """Test basic roundtrip."""
        data = b"hello world hello world hello world"
        compressed = compress(data)
        decompressed, metadata = decompress(compressed)

        assert decompressed == data
        assert isinstance(metadata, CacheMetadata)

    def test_compress_finds_repetitive_patterns(self):
        """Test compression on repetitive data."""
        # Highly repetitive data (good candidate for caching)
        data = b"function call() { return true; } " * 10
        compressed = compress(data)

        # Should achieve significant compression
        assert len(compressed) < len(data) * 0.7

    def test_compress_handles_random_data(self):
        """Test compression on random data (poor candidate)."""
        data = bytes(range(256))  # All unique bytes
        compressed = compress(data)
        decompressed, _ = decompress(compressed)

        assert decompressed == data
        # May not compress well, but should not expand too much
        assert len(compressed) < len(data) * 2

    def test_compress_llm_prompt_style_data(self):
        """Test compression on LLM-style prompts."""
        # Simulated LLM prompt with system message, repeated function names
        data = (
            b"You are a helpful assistant. "
            b"User: Calculate sum(1,2,3) "
            b"Assistant: sum(1,2,3) = 6 "
            b"User: Calculate sum(4,5,6) "
            b"Assistant: sum(4,5,6) = 15 "
            b"You are a helpful assistant. "
        )

        compressed = compress(data)
        decompressed, metadata = decompress(compressed)

        assert decompressed == data
        # Should compress well due to repeated phrases
        assert len(compressed) < len(data) * 0.8
        assert metadata.dict_size > 0

    def test_compress_empty_data(self):
        """Test compression of empty data."""
        data = b""
        compressed = compress(data)
        decompressed, _ = decompress(compressed)

        assert decompressed == data

    def test_compress_tiny_data(self):
        """Test compression of tiny data (<16 bytes)."""
        data = b"tiny"
        compressed = compress(data)
        decompressed, _ = decompress(compressed)

        assert decompressed == data

    def test_compress_preserves_binary_data(self):
        """Test compression preserves all byte values."""
        data = bytes(range(256)) * 3  # All byte values, repeated 3 times
        compressed = compress(data)
        decompressed, _ = decompress(compressed)

        assert decompressed == data

    def test_compress_metadata(self):
        """Test metadata extraction."""
        data = b"test data test data test data"
        compressed = compress(data)
        _, metadata = decompress(compressed)

        assert metadata.original_size == len(data)
        assert metadata.compressed_size == len(compressed)
        assert metadata.dict_size >= 0

    def test_compress_with_custom_params(self):
        """Test compression with custom parameters."""
        data = b"abcdefgh" * 100
        compressed = compress(data, min_pattern_length=8, max_dict_size=16)
        decompressed, metadata = decompress(compressed)

        assert decompressed == data
        assert metadata.dict_size <= 16


class TestCacheEdgeCases:
    """Test edge cases for cache codec."""

    def test_decompress_invalid_payload_too_short(self):
        """Test decompression fails on too-short payload."""
        with pytest.raises(ValueError, match="too short"):
            decompress(b"short")

    def test_decompress_invalid_dict_format(self):
        """Test decompression fails on invalid dictionary."""
        # Valid header but invalid JSON in dict
        payload = b"\x00\x05{bad}xxxx"
        with pytest.raises(Exception):  # JSON decode error
            decompress(payload)

    def test_decompress_invalid_cache_reference(self):
        """Test decompression fails on out-of-bounds cache reference."""
        # Build valid payload with invalid reference
        data = b"test"
        compressed = compress(data)

        # Corrupt the compressed data to have invalid ref
        # Assuming structure: [2B dict_len][dict][4B data_len][data]
        dict_len = (compressed[0] << 8) | compressed[1]
        # Inject invalid cache reference after header
        corrupted = bytearray(compressed)
        data_start = 2 + dict_len + 4
        if data_start + 3 <= len(corrupted):
            corrupted[data_start] = 0xFF  # Cache marker
            corrupted[data_start + 1] = 0xFF  # High ref (65535)
            corrupted[data_start + 2] = 0xFF  # Low ref

        with pytest.raises(ValueError, match="Invalid cache reference"):
            decompress(bytes(corrupted))

    def test_compress_type_validation(self):
        """Test compress validates input type."""
        with pytest.raises(TypeError):
            compress("not bytes")  # type: ignore

        with pytest.raises(TypeError):
            compress(123)  # type: ignore

    def test_decompress_type_validation(self):
        """Test decompress validates input type."""
        with pytest.raises(TypeError):
            decompress("not bytes")  # type: ignore

    def test_compress_no_frequent_patterns(self):
        """Test compression when no patterns meet frequency threshold."""
        # All unique patterns (each occurs once)
        data = b"".join([f"pattern{i:03d}".encode() for i in range(100)])
        compressed = compress(data)
        decompressed, metadata = decompress(compressed)

        assert decompressed == data
        # Should have empty or small dictionary
        assert metadata.dict_size <= 10


class TestCacheLLMUseCases:
    """Test cache codec on realistic LLM use cases."""

    def test_system_prompt_repetition(self):
        """Test compression of repeated system prompts."""
        system_prompt = b"You are a helpful, harmless, and honest AI assistant. "
        conversation = (
            system_prompt
            + b"User: Hello. "
            + b"Assistant: Hi! "
            + system_prompt
            + b"User: How are you? "
            + b"Assistant: I'm well! "
            + system_prompt
        )

        compressed = compress(conversation)
        decompressed, metadata = decompress(compressed)

        assert decompressed == conversation
        # System prompt repetition should compress well
        assert len(compressed) < len(conversation) * 0.7
        assert metadata.dict_size > 0

    def test_function_calling_patterns(self):
        """Test compression of function calling patterns."""
        data = (
            b'{"function": "calculate", "args": [1, 2, 3]} '
            b'{"result": 6} '
            b'{"function": "calculate", "args": [4, 5, 6]} '
            b'{"result": 15} '
            b'{"function": "calculate", "args": [7, 8, 9]} '
        )

        compressed = compress(data)
        decompressed, metadata = decompress(compressed)

        assert decompressed == data
        # Repeated JSON keys and structure should compress well
        assert len(compressed) < len(data) * 0.8

    def test_token_repetition(self):
        """Test compression of repeated tokens (common in LLM output)."""
        # Simulated tokenized output with repeated tokens
        data = b"the " * 50 + b"quick " * 30 + b"brown " * 20 + b"fox " * 10
        compressed = compress(data)
        decompressed, metadata = decompress(compressed)

        assert decompressed == data
        # Should achieve excellent compression on highly repetitive tokens
        assert len(compressed) < len(data) * 0.4

    def test_code_completion_context(self):
        """Test compression of code completion context."""
        code = (
            b"def calculate(x, y):\n"
            b"    return x + y\n\n"
            b"def calculate_sum(numbers):\n"
            b"    return sum(numbers)\n\n"
            b"def calculate_average(numbers):\n"
            b"    return sum(numbers) / len(numbers)\n\n"
            b"def calculate(x, y):\n"  # Repeated function
        )

        compressed = compress(code)
        decompressed, metadata = decompress(compressed)

        assert decompressed == code
        # Repeated function names and patterns should compress
        assert len(compressed) < len(code) * 0.85


class TestCacheIntegration:
    """Test cache codec integration with semantic layer."""

    def test_semantic_compress_with_ss(self):
        """Test Ss codec via semantic_compress."""
        from arua.compression.semantic import semantic_compress, semantic_decompress

        data = b"repeated text " * 20
        payload = semantic_compress(data, codec="Ss", domain_id=0)

        # Should have semantic header
        assert len(payload) >= 4

        # Decompress
        decompressed = semantic_decompress(payload)
        assert decompressed == data

    def test_ss_codec_id(self):
        """Test Ss uses correct codec ID."""
        from arua.compression.semantic import semantic_compress, SemanticHeader, CODEC_ID_SS

        data = b"cache test data " * 10
        payload = semantic_compress(data, codec="Ss")

        header, _ = SemanticHeader.from_bytes(payload)
        assert header.codec_id == CODEC_ID_SS

    def test_ss_roundtrip_large_data(self):
        """Test Ss on larger realistic data."""
        from arua.compression.semantic import semantic_compress, semantic_decompress

        # 100KB of semi-repetitive text (like LLM context window)
        data = (b"function test() { console.log('test'); } " * 1000)[:100000]

        payload = semantic_compress(data, codec="Ss")
        decompressed = semantic_decompress(payload)

        assert decompressed == data
        # Should achieve good compression
        assert len(payload) < len(data) * 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
