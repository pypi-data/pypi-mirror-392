import pytest
from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_plans import decode_payload_to_plan


def _roundtrip_codec(label: str) -> None:
    data = f"hello semantic {label}".encode("utf-8")
    # Skip if label is not part of the stable v1 codec set; some extended
    # codecs remain experimental and are not exercised here.
    stable = {"Sa", "Sb", "Sc", "Sd", "Se", "Sf", "Sg", "Su", "Sp", "Ss", "Sr"}
    if label not in stable:
        pytest.skip(f"Codec {label} not supported in main package; prototype tests are located in tmp/prototypes")
    payload = semantic_compress(data, codec=label, domain_id=5, template_id=42)
    decoded = semantic_decompress(payload)
    assert decoded == data

    header, plan, core_payload = decode_payload_to_plan(payload)
    assert plan.codec_label == label
    assert header.domain_id == 5
    assert header.template_id == 42
    assert isinstance(core_payload, bytes)


def test_sp_roundtrip_and_plan() -> None:
    _roundtrip_codec("Sp")


def test_ss_roundtrip_and_plan() -> None:
    _roundtrip_codec("Ss")


def test_sr_roundtrip_and_plan() -> None:
    _roundtrip_codec("Sr")
