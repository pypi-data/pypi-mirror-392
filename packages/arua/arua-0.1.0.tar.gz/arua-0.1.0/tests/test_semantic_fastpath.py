from arua.compression.semantic import semantic_compress
from arua.compression.semantic_fastpath import FastPathEngine, FastPathDecision
from arua.compression.semantic_interplay import InterplayFlag


def test_fastpath_basic_sb_cpu() -> None:
    engine = FastPathEngine()
    payload = semantic_compress(b"hello sb", codec="Sb", domain_id=1, template_id=0)
    decision = engine.choose(payload, priority="low")

    assert isinstance(decision, FastPathDecision)
    assert decision.header.domain_id == 1
    assert decision.plan.codec_label == "Sb"
    # Sb is textual; interplay should reflect that.
    assert decision.interplay & InterplayFlag.IS_TEXTUAL
    # Low-priority Sb is allowed to stay on CPU.
    assert decision.accelerator.backend == "cpu"


def test_fastpath_flow_high_priority_prefers_gpu() -> None:
    engine = FastPathEngine()
    payload = semantic_compress(b"hello flow", codec="Sf", domain_id=0, template_id=0)
    decision = engine.choose(payload, priority="high")

    assert decision.plan.codec_label == "Sf"
    # Sf is accelerator-friendly in interplay; with high priority we
    # expect GPU offload in this prototype.
    assert decision.accelerator.backend == "gpu"
    assert decision.accelerator.offload is True

