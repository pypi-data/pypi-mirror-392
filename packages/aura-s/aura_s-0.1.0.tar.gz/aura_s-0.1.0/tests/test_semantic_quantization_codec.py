from arua.compression.semantic_quantization import (
    encode_quantized_floats,
    decode_quantized_floats,
    compress,
    decompress,
)


def test_sq_codec_json_array_roundtrip() -> None:
    vec = [0.0, 0.25, 0.5, 0.75, 1.0]
    json_bytes = b"[0.0,0.25,0.5,0.75,1.0]"

    payload = compress(json_bytes, bits=8)
    out_json = decompress(payload)

    # Decode back to floats and compare with small quantization error tolerance.
    decoded = decode_quantized_floats(payload)
    assert len(decoded) == len(vec)
    for a, b in zip(vec, decoded):
        assert abs(a - b) <= 0.02

    # The JSON form should decode to the same float list.
    import json

    arr_from_json = json.loads(out_json.decode("utf-8"))
    assert len(arr_from_json) == len(vec)
    for a, b in zip(vec, arr_from_json):
        assert abs(a - b) <= 0.02

