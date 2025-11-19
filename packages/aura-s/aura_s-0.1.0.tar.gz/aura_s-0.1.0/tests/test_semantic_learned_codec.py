from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_learned import (
    LearnedMetadata,
    encode_learned,
    decode_learned,
    compress,
    decompress,
)


def test_sl_metadata_roundtrip() -> None:
    meta = LearnedMetadata(
        model_name="autoencoder-small",
        version="1.0",
        latent_dim=128,
        has_residual=True,
        extra={"domain": "logs"},
    )
    blob = encode_learned(meta)
    decoded = decode_learned(blob)
    assert decoded.model_name == "autoencoder-small"
    assert decoded.version == "1.0"
    assert decoded.latent_dim == 128
    assert decoded.has_residual is True
    assert decoded.extra == {"domain": "logs"}


def test_sl_compress_decompress() -> None:
    data = b"learned codec payload"
    meta = LearnedMetadata(model_name="ae-medium", version="2.0", latent_dim=256)
    payload = compress(data, meta=meta)
    out, out_meta = decompress(payload)
    assert out == data
    assert out_meta.model_name == "ae-medium"
    assert out_meta.version == "2.0"
    assert out_meta.latent_dim == 256


def test_sl_semantic_roundtrip() -> None:
    data = b"semantic Sl test" * 5
    payload = semantic_compress(data, codec="Sl", domain_id=17)
    out = semantic_decompress(payload)
    assert out == data

