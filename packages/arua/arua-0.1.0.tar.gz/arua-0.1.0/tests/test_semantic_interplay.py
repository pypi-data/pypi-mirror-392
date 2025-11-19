from arua.compression.semantic import SemanticHeader, CODEC_ID_SA, CODEC_ID_SF, CODEC_ID_SG
from arua.compression.semantic_plans import plan_from_header
from arua.compression.semantic_interplay import get_interplay, InterplayFlag


def test_interplay_flags_for_core_textual() -> None:
    h_sa = SemanticHeader(codec_id=CODEC_ID_SA, domain_id=0, template_id=0)
    plan_sa = plan_from_header(h_sa)
    flags_sa = get_interplay(plan_sa)

    assert flags_sa & InterplayFlag.IS_TEXTUAL
    assert flags_sa & InterplayFlag.USES_RESOLVER


def test_interplay_flags_for_flow_and_grain() -> None:
    h_sf = SemanticHeader(codec_id=CODEC_ID_SF, domain_id=0, template_id=0)
    h_sg = SemanticHeader(codec_id=CODEC_ID_SG, domain_id=0, template_id=0)

    plan_sf = plan_from_header(h_sf)
    plan_sg = plan_from_header(h_sg)

    flags_sf = get_interplay(plan_sf)
    flags_sg = get_interplay(plan_sg)

    assert flags_sf & InterplayFlag.IS_TEXTUAL
    assert flags_sf & InterplayFlag.USES_ACCEL

    assert flags_sg & InterplayFlag.IS_TEXTUAL
    assert flags_sg & InterplayFlag.USES_ACCEL

