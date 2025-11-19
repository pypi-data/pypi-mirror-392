import pytest


def _has_aura() -> bool:
    try:
        import aura_compression  # type: ignore[import]
    except Exception:
        return False
    return True


pytestmark = pytest.mark.skipif(not _has_aura(), reason="AURA repo not available")


def test_aura_semantic_roundtrip_auto():
    from arua.compression.semantic_aura import (
        aura_semantic_compress,
        aura_semantic_decompress,
    )

    text = "Hello from AURA semantic wrapper!"
    wrapped, meta = aura_semantic_compress(
        text, codec="auto", domain_id=7, template_id=123
    )
    out, meta2, header = aura_semantic_decompress(wrapped)

    assert out == text
    assert header.domain_id == 7
    assert (
        header.template_id == 123 or header.template_id == 0
    )  # template_id may be sanitized
    assert "semantic_codec" in meta
    assert meta2.get("semantic_codec_id") in (1, 2)
