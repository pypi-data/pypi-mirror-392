from arua.compression.semantic import (
    SemanticHeader,
    CODEC_ID_SA,
    CODEC_ID_SB,
    CODEC_ID_SF,
    CODEC_ID_SG,
)
from arua.compression.semantic_plans import plan_from_header, decode_payload_to_plan
from arua.compression.semantic import semantic_compress
from arua.templates import TemplateLibrary


def test_plan_from_header_sa_vs_sb():
    h_sa = SemanticHeader(codec_id=CODEC_ID_SA, domain_id=1, template_id=0)
    h_sb = SemanticHeader(codec_id=CODEC_ID_SB, domain_id=1, template_id=0)

    plan_sa = plan_from_header(h_sa)
    plan_sb = plan_from_header(h_sb)

    assert plan_sa.codec_label == "Sa"
    assert plan_sa.model_tier == "small"
    assert plan_sa.quantization == "int8"
    assert plan_sa.max_sequence_length == 512

    assert plan_sb.codec_label == "Sb"
    assert plan_sb.model_tier == "medium"
    assert plan_sb.quantization == "fp16"
    assert plan_sb.max_sequence_length == 2048


def test_plan_from_header_flow_and_grain():
    h_sf = SemanticHeader(codec_id=CODEC_ID_SF, domain_id=2, template_id=0)
    h_sg = SemanticHeader(codec_id=CODEC_ID_SG, domain_id=2, template_id=0)

    plan_sf = plan_from_header(h_sf)
    plan_sg = plan_from_header(h_sg)

    assert plan_sf.model_tier == "large"
    assert plan_sg.model_tier == "large"
    assert plan_sf.max_sequence_length == 4096
    assert plan_sg.max_sequence_length == 4096


def test_plan_template_lookup_flag():
    lib = TemplateLibrary()
    lib.add(domain_id=3, template_id=42, pattern="Hello, {name}!", metadata={})

    h_has_template = SemanticHeader(codec_id=CODEC_ID_SB, domain_id=3, template_id=42)
    h_missing_template = SemanticHeader(
        codec_id=CODEC_ID_SB, domain_id=3, template_id=99
    )

    plan1 = plan_from_header(h_has_template, templates=lib)
    plan2 = plan_from_header(h_missing_template, templates=lib)

    assert plan1.needs_template_lookup is True
    assert plan2.needs_template_lookup is False


def test_decode_payload_to_plan_roundtrip():
    lib = TemplateLibrary()
    lib.add(domain_id=4, template_id=7, pattern="Hi, {x}", metadata={})
    data = b"hello semantic"
    # Use Sb to ensure core compressor is exercised
    payload = semantic_compress(data, codec="Sb", domain_id=4, template_id=7)
    header, plan, core_payload = decode_payload_to_plan(payload, templates=lib)

    assert header.domain_id == 4
    assert header.template_id == 7
    assert plan.codec_label in {"Sb", "Sc", "Sd", "Se", "Sf", "Sg"}
    assert plan.needs_template_lookup is True
    # Ensure we did not accidentally modify the core payload
    assert isinstance(core_payload, bytes)
