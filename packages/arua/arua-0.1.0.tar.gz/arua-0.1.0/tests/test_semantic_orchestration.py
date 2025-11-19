"""Tests for Semantic Orchestration (So) codec."""

from __future__ import annotations

import pytest

from arua.compression.semantic import semantic_compress, semantic_decompress
from arua.compression.semantic_orchestration import (
    OrchestrationGraph,
    OrchestrationStep,
    compress,
    decompress,
    encode_orchestration,
    decode_orchestration,
)


class TestOrchestrationEncoding:
    """Test low-level orchestration graph encoding/decoding."""

    def test_encode_decode_single_step(self):
        """Test encoding and decoding a single step."""
        step = OrchestrationStep(step_id="step1", parents=[], tool="lz77")
        graph = OrchestrationGraph(steps=[step])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert len(decoded.steps) == 1
        assert decoded.steps[0].step_id == "step1"
        assert decoded.steps[0].parents == []
        assert decoded.steps[0].tool == "lz77"

    def test_encode_decode_multiple_steps(self):
        """Test encoding and decoding multiple steps with dependencies."""
        step1 = OrchestrationStep(step_id="extract", parents=[], tool="lz77")
        step2 = OrchestrationStep(step_id="compress", parents=["extract"], tool="zstd")
        step3 = OrchestrationStep(
            step_id="finalize", parents=["compress"], tool="checksum"
        )
        graph = OrchestrationGraph(steps=[step1, step2, step3])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert len(decoded.steps) == 3
        assert decoded.steps[1].parents == ["extract"]
        assert decoded.steps[2].parents == ["compress"]

    def test_encode_decode_complex_dag(self):
        """Test encoding and decoding a complex DAG with multiple parents."""
        step1 = OrchestrationStep(step_id="input1", parents=[], tool="read")
        step2 = OrchestrationStep(step_id="input2", parents=[], tool="read")
        step3 = OrchestrationStep(
            step_id="merge", parents=["input1", "input2"], tool="concat"
        )
        step4 = OrchestrationStep(step_id="process", parents=["merge"], tool="compress")
        graph = OrchestrationGraph(steps=[step1, step2, step3, step4])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert len(decoded.steps) == 4
        assert decoded.steps[2].parents == ["input1", "input2"]

    def test_encode_decode_empty_graph(self):
        """Test encoding and decoding an empty graph."""
        graph = OrchestrationGraph(steps=[])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert len(decoded.steps) == 0

    def test_decode_invalid_json(self):
        """Test decode_orchestration raises ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="invalid So payload JSON"):
            decode_orchestration(b"not json")

    def test_decode_missing_steps(self):
        """Test decode_orchestration raises ValueError for missing steps."""
        with pytest.raises(ValueError, match="must contain a 'steps' list"):
            decode_orchestration(b'{"foo": "bar"}')

    def test_decode_invalid_step_structure(self):
        """Test decode_orchestration raises ValueError for invalid step."""
        with pytest.raises(ValueError, match="invalid So step entry"):
            decode_orchestration(b'{"steps": [{"missing_id": true}]}')

    def test_decode_invalid_parents_type(self):
        """Test decode_orchestration raises ValueError for non-list parents."""
        with pytest.raises(ValueError, match="parents must be a list"):
            decode_orchestration(b'{"steps": [{"id": "step1", "parents": "not_a_list"}]}')

    def test_decode_non_bytes_raises(self):
        """Test decode_orchestration raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decode_orchestration("not bytes")  # type: ignore

    def test_json_format(self):
        """Test that encoded JSON has expected structure."""
        step = OrchestrationStep(step_id="test", parents=["p1", "p2"], tool="foo")
        graph = OrchestrationGraph(steps=[step])
        encoded = encode_orchestration(graph)
        text = encoded.decode("utf-8")
        assert '"id":"test"' in text
        assert '"parents":["p1","p2"]' in text
        assert '"tool":"foo"' in text


class TestSoCompression:
    """Test So codec compression and decompression."""

    def test_compress_decompress_single_step(self):
        """Test compress/decompress with a single-step graph."""
        data = b"workflow data"
        step = OrchestrationStep(step_id="process", parents=[], tool="compress")
        graph = OrchestrationGraph(steps=[step])
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data
        assert len(decoded_graph.steps) == 1
        assert decoded_graph.steps[0].step_id == "process"

    def test_compress_decompress_multi_step_dag(self):
        """Test compress/decompress with multi-step DAG."""
        data = b"complex workflow"
        step1 = OrchestrationStep(step_id="read", parents=[], tool="io")
        step2 = OrchestrationStep(step_id="parse", parents=["read"], tool="parser")
        step3 = OrchestrationStep(step_id="compress", parents=["parse"], tool="lz77")
        graph = OrchestrationGraph(steps=[step1, step2, step3])
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data
        assert len(decoded_graph.steps) == 3

    def test_compress_decompress_no_graph(self):
        """Test compress/decompress with no graph (empty graph)."""
        data = b"no orchestration"
        compressed = compress(data)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data
        assert len(decoded_graph.steps) == 0

    def test_compress_decompress_large_payload(self):
        """Test compress/decompress with larger payload."""
        data = b"x" * 50000
        step = OrchestrationStep(step_id="big", parents=[], tool="lz77")
        graph = OrchestrationGraph(steps=[step])
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data
        assert len(decoded_graph.steps) == 1

    def test_compress_decompress_binary_data(self):
        """Test compress/decompress with binary payload."""
        data = bytes(range(256))
        step = OrchestrationStep(step_id="binary", parents=[], tool="raw")
        graph = OrchestrationGraph(steps=[step])
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data

    def test_compress_decompress_empty_payload(self):
        """Test compress/decompress with empty payload."""
        data = b""
        step = OrchestrationStep(step_id="empty", parents=[], tool="noop")
        graph = OrchestrationGraph(steps=[step])
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data
        assert decoded_graph.steps[0].step_id == "empty"

    def test_compress_invalid_data_type(self):
        """Test compress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            compress("not bytes")  # type: ignore

    def test_decompress_invalid_data_type(self):
        """Test decompress raises TypeError for non-bytes input."""
        with pytest.raises(TypeError, match="expects a bytes-like object"):
            decompress("not bytes")  # type: ignore

    def test_decompress_truncated_header(self):
        """Test decompress raises ValueError for truncated length header."""
        with pytest.raises(ValueError, match="too short for length header"):
            decompress(b"\x00")

    def test_decompress_truncated_graph_blob(self):
        """Test decompress raises ValueError for truncated graph blob."""
        # Header says 100 bytes, but only 5 bytes follow
        payload = b"\x00\x64" + b"short"
        with pytest.raises(ValueError, match="truncated before graph blob"):
            decompress(payload)

    def test_compress_graph_too_large(self):
        """Test compress raises ValueError for graph metadata too large."""
        # Create a graph with enormous step IDs to exceed 65535 bytes
        steps = [
            OrchestrationStep(step_id="x" * 10000, parents=[], tool="foo")
            for _ in range(10)
        ]
        graph = OrchestrationGraph(steps=steps)
        with pytest.raises(ValueError, match="orchestration graph metadata too large"):
            compress(b"data", graph=graph)

    def test_wire_format_structure(self):
        """Test the wire format structure."""
        data = b"test"
        step = OrchestrationStep(step_id="s1", parents=[], tool="t1")
        graph = OrchestrationGraph(steps=[step])
        compressed = compress(data, graph=graph)

        # First 2 bytes are length
        graph_length = (compressed[0] << 8) | compressed[1]
        assert graph_length > 0

        # Next graph_length bytes are the graph blob
        graph_blob = compressed[2 : 2 + graph_length]
        decoded_graph = decode_orchestration(graph_blob)
        assert len(decoded_graph.steps) == 1
        assert decoded_graph.steps[0].step_id == "s1"


class TestSoSemanticIntegration:
    """Test So codec integration with semantic.py."""

    def test_semantic_compress_so_codec(self):
        """Test semantic_compress with So codec."""
        data = b"orchestrated workflow"
        compressed = semantic_compress(data, codec="So")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_so_roundtrip(self):
        """Test full roundtrip through semantic layer."""
        data = b"A" * 1000
        compressed = semantic_compress(data, codec="So")
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_compress_so_with_domain_template(self):
        """Test So codec with domain_id and template_id."""
        data = b"routed orchestration"
        compressed = semantic_compress(
            data, codec="So", domain_id=42, template_id=9999
        )
        decompressed = semantic_decompress(compressed)
        assert decompressed == data

    def test_semantic_decompress_discards_graph(self):
        """Test that semantic_decompress returns only data, not graph.

        Note: The semantic layer doesn't expose graph metadata in the simple
        API. To access graph info, use semantic_orchestration.decompress() directly.
        """
        data = b"workflow message"
        # Compress directly with So codec including graph
        from arua.compression.semantic_orchestration import compress as so_compress

        step1 = OrchestrationStep(step_id="s1", parents=[], tool="t1")
        step2 = OrchestrationStep(step_id="s2", parents=["s1"], tool="t2")
        graph = OrchestrationGraph(steps=[step1, step2])
        so_payload = so_compress(data, graph=graph)

        # Wrap in semantic header
        from arua.compression.semantic import CODEC_ID_SO, SemanticHeader

        header = SemanticHeader(codec_id=CODEC_ID_SO, domain_id=0, template_id=0)
        semantic_payload = header.to_bytes() + so_payload

        # Decompress via semantic API (graph is discarded)
        decompressed = semantic_decompress(semantic_payload)
        assert decompressed == data


class TestSoEdgeCases:
    """Test edge cases for So codec."""

    def test_step_with_empty_tool(self):
        """Test step with empty tool string."""
        step = OrchestrationStep(step_id="step1", parents=[], tool="")
        graph = OrchestrationGraph(steps=[step])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert decoded.steps[0].tool == ""

    def test_step_with_many_parents(self):
        """Test step with many parent dependencies."""
        parents = [f"parent_{i}" for i in range(100)]
        step = OrchestrationStep(step_id="child", parents=parents, tool="merge")
        graph = OrchestrationGraph(steps=[step])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert len(decoded.steps[0].parents) == 100

    def test_many_steps(self):
        """Test graph with many steps."""
        steps = [
            OrchestrationStep(step_id=f"step_{i}", parents=[], tool=f"tool_{i}")
            for i in range(100)
        ]
        graph = OrchestrationGraph(steps=steps)
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert len(decoded.steps) == 100

    def test_unicode_in_step_ids(self):
        """Test steps with unicode characters in IDs and tools."""
        step = OrchestrationStep(step_id="étape_1", parents=[], tool="outil_français")
        graph = OrchestrationGraph(steps=[step])
        encoded = encode_orchestration(graph)
        decoded = decode_orchestration(encoded)
        assert decoded.steps[0].step_id == "étape_1"
        assert decoded.steps[0].tool == "outil_français"

    def test_complex_diamond_dag(self):
        """Test diamond-shaped DAG (common merge pattern)."""
        step1 = OrchestrationStep(step_id="start", parents=[], tool="init")
        step2 = OrchestrationStep(step_id="branch_a", parents=["start"], tool="process_a")
        step3 = OrchestrationStep(step_id="branch_b", parents=["start"], tool="process_b")
        step4 = OrchestrationStep(
            step_id="merge", parents=["branch_a", "branch_b"], tool="combine"
        )
        graph = OrchestrationGraph(steps=[step1, step2, step3, step4])

        data = b"diamond pattern"
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)

        assert decompressed == data
        assert len(decoded_graph.steps) == 4
        assert decoded_graph.steps[3].step_id == "merge"
        assert set(decoded_graph.steps[3].parents) == {"branch_a", "branch_b"}

    def test_roundtrip_with_special_characters(self):
        """Test roundtrip with special characters in step metadata."""
        step = OrchestrationStep(
            step_id='step"with"quotes', parents=['parent:with:colons'], tool="tool,with,commas"
        )
        graph = OrchestrationGraph(steps=[step])
        data = b"special chars test"
        compressed = compress(data, graph=graph)
        decompressed, decoded_graph = decompress(compressed)
        assert decompressed == data
        assert decoded_graph.steps[0].step_id == 'step"with"quotes'
