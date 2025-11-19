from arua.compression.helpers import encode_semantic_pattern, decode_semantic_pattern


def test_sp_roundtrip_pattern() -> None:
    pattern = "user {user_id} logged in from {ip}"
    fields = {"user_id": "u123", "ip": "1.2.3.4"}

    payload = encode_semantic_pattern(pattern, fields, domain_id=11)
    pat_out, fields_out, header, plan = decode_semantic_pattern(payload)

    assert pat_out == pattern
    assert fields_out == fields
    assert plan.codec_label == "Sp"
    assert header.domain_id == 11

