from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_sb import register_templates_for_domain, get_template


def test_sb_header_only_with_registered_template() -> None:
    domain_id = 50
    template_id = 7
    value = b"llm_request_schema_v1"

    register_templates_for_domain(domain_id, {template_id: value})

    payload = semantic_compress(value, codec="Sb", domain_id=domain_id, template_id=template_id)
    header = payload[:4]
    body = payload[4:]
    # Header-only Sb when template is known.
    assert body == b""

    decoded = semantic_decompress(payload)
    assert decoded == value

    assert get_template(domain_id, template_id) == value

