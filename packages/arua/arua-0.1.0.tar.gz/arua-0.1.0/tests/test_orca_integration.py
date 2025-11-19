import pytest
from arua.compression.orca_integration import OrcaEngineSelector
from arua.compression.semantic_plans import SemanticPlan

# Skip orca integration tests in CI; they depend on external resources and hardware.
pytestmark = pytest.mark.skip(reason="External Orca integration - skipped in CI")


def test_orca_engine_selector_basic() -> None:
    selector = OrcaEngineSelector()
    plan_small = SemanticPlan(
        codec_label="Sa",
        domain_id=0,
        template_id=0,
        model_tier="small",
        quantization="int8",
        max_sequence_length=512,
        needs_template_lookup=False,
    )
    plan_large = SemanticPlan(
        codec_label="Sg",
        domain_id=0,
        template_id=0,
        model_tier="large",
        quantization="fp16",
        max_sequence_length=4096,
        needs_template_lookup=False,
    )

    sel_small = selector.select(plan_small)
    sel_large = selector.select(plan_large)

    assert sel_small.engine_name == "orca-small"
    assert sel_small.profile_name == "int8-default"
    assert sel_small.max_batch == 64

    assert sel_large.engine_name == "orca-large"
    assert sel_large.profile_name == "fp16-default"
    assert sel_large.max_batch == 8
