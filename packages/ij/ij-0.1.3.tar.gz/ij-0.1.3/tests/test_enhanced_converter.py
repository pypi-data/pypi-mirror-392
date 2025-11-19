"""Tests for enhanced text converter."""

import pytest
from ij.converters import EnhancedTextConverter
from ij.core import NodeType


def test_enhanced_simple_flow():
    """Test basic flow conversion."""
    converter = EnhancedTextConverter()
    diagram = converter.convert("Start -> Process -> End")

    assert len(diagram.nodes) == 3
    assert diagram.validate()


def test_enhanced_conditional():
    """Test conditional branch parsing."""
    converter = EnhancedTextConverter()
    text = "Start -> Check user. If authenticated: Show dashboard, else: Show login"
    diagram = converter.convert(text)

    # Should have: Start, Check user (decision), Show dashboard, Show login
    assert len(diagram.nodes) >= 3
    assert diagram.validate()

    # Find decision node
    decision_nodes = [n for n in diagram.nodes if n.node_type == NodeType.DECISION]
    assert len(decision_nodes) > 0

    # Check for Yes/No edges
    edge_labels = [e.label for e in diagram.edges if e.label]
    assert "Yes" in edge_labels or "No" in edge_labels


def test_enhanced_parallel():
    """Test parallel flow parsing."""
    converter = EnhancedTextConverter()
    text = "Start -> [parallel: Process A, Process B, Process C] -> End"
    diagram = converter.convert(text)

    assert len(diagram.nodes) >= 5  # Start + 3 parallel + End
    assert diagram.validate()


def test_enhanced_loop():
    """Test loop parsing."""
    converter = EnhancedTextConverter()
    text = "Start while data available: Process item"
    diagram = converter.convert(text)

    # Should have decision and loop-back edge
    assert diagram.validate()

    # Find conditional edges (loop back)
    from ij.core import EdgeType

    conditional_edges = [e for e in diagram.edges if e.edge_type == EdgeType.CONDITIONAL]
    assert len(conditional_edges) > 0


def test_enhanced_keywords():
    """Test keyword-based type inference."""
    converter = EnhancedTextConverter()

    test_cases = [
        ("Launch application", NodeType.START),
        ("Complete task", NodeType.END),
        ("Verify credentials", NodeType.DECISION),
        ("Persist to database", NodeType.DATA),
        ("Call subprocess", NodeType.SUBPROCESS),
    ]

    for text, expected_type in test_cases:
        diagram = converter.convert(text)
        assert diagram.nodes[0].node_type == expected_type


def test_enhanced_with_title():
    """Test conversion with title."""
    converter = EnhancedTextConverter()
    diagram = converter.convert("Step 1 -> Step 2", title="My Flow")

    assert diagram.metadata["title"] == "My Flow"


def test_enhanced_sentence_parsing():
    """Test parsing sentence-style descriptions."""
    converter = EnhancedTextConverter()
    text = "Begin process. Load data. Validate input. Save results. End process"
    diagram = converter.convert(text)

    assert len(diagram.nodes) >= 5
    assert diagram.validate()


def test_enhanced_mixed_separators():
    """Test handling mixed separators."""
    converter = EnhancedTextConverter()
    text = "Start -> Step 1. Step 2 → Step 3 -> End"
    diagram = converter.convert(text)

    assert len(diagram.nodes) >= 3
    assert diagram.validate()
