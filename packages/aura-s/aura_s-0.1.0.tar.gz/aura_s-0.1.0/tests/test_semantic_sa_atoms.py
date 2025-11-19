from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_sa import register_atoms_for_domain, get_atom


def test_sa_custom_domain_atom_roundtrip() -> None:
    domain_id = 42
    value = b"cache-hot"
    register_atoms_for_domain(domain_id, {0: value})

    payload = semantic_compress(value, codec="Sa", domain_id=domain_id)
    header_atom, body = payload[:4], payload[4:]
    assert body == b""

    decoded = semantic_decompress(payload)
    assert decoded == value

    assert get_atom(domain_id, 0) == value

