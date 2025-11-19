from arua.compression.sa_json import sa_encode_json, sa_decode_json, sb_encode_json, sb_decode_json
from arua.compression.semantic import CODEC_ID_SA, CODEC_ID_SB, SemanticHeader


def test_sa_json_roundtrip_simple() -> None:
    obj = {"type": "atom", "value": 42}
    payload = sa_encode_json(obj, domain_id=3, template_id=7)

    header, _ = SemanticHeader.from_bytes(payload)
    assert header.codec_id == CODEC_ID_SA
    assert header.domain_id == 3
    assert header.template_id == 7

    out = sa_decode_json(payload)
    assert out == obj


def test_sa_json_non_ascii_roundtrip() -> None:
    obj = {"msg": "héllø 🌍"}
    payload = sa_encode_json(obj, domain_id=1)
    out = sa_decode_json(payload)
    assert out == obj


def test_sb_json_roundtrip_simple() -> None:
    obj = {"type": "binary", "payload": "x" * 200}
    payload = sb_encode_json(obj, domain_id=5, template_id=9)

    header, _ = SemanticHeader.from_bytes(payload)
    assert header.codec_id == CODEC_ID_SB
    assert header.domain_id == 5
    assert header.template_id == 9

    out = sb_decode_json(payload)
    assert out == obj
