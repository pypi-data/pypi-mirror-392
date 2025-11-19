"""Tests for text converters."""

import pytest
from ij.converters import SimpleTextConverter
from ij.core import NodeType


def test_simple_text_converter():
    """Test basic text to diagram conversion."""
    converter = SimpleTextConverter()
    diagram = converter.convert("Start -> Process -> End")

    assert len(diagram.nodes) == 3
    assert len(diagram.edges) == 2
    assert diagram.validate()


def test_converter_with_title():
    """Test conversion with title."""
    converter = SimpleTextConverter()
    diagram = converter.convert("Step 1 -> Step 2", title="My Process")

    assert diagram.metadata["title"] == "My Process"


def test_converter_node_type_inference():
    """Test that node types are inferred correctly."""
    converter = SimpleTextConverter()
    diagram = converter.convert("Start -> Decide if ready -> Process data -> End")

    # Check inferred types
    nodes = {node.label: node.node_type for node in diagram.nodes}
    assert nodes["Start"] == NodeType.START
    assert nodes["Decide if ready"] == NodeType.DECISION
    assert nodes["Process data"] == NodeType.PROCESS
    assert nodes["End"] == NodeType.END


def test_converter_with_newlines():
    """Test conversion with newline-separated steps."""
    text = """Start
Process data
Make decision
End"""
    converter = SimpleTextConverter()
    diagram = converter.convert(text)

    assert len(diagram.nodes) == 4
    assert len(diagram.edges) == 3


def test_converter_with_arrows():
    """Test different arrow styles."""
    converter = SimpleTextConverter()

    # Test -> arrows
    diagram1 = converter.convert("A -> B -> C")
    assert len(diagram1.nodes) == 3

    # Test → unicode arrows
    diagram2 = converter.convert("A → B → C")
    assert len(diagram2.nodes) == 3


def test_converter_keywords():
    """Test keyword-based node type inference."""
    test_cases = [
        ("Start process", NodeType.START),
        ("Finish task", NodeType.END),
        ("Check if valid", NodeType.DECISION),
        ("Store in database", NodeType.DATA),
    ]

    converter = SimpleTextConverter()
    for text, expected_type in test_cases:
        diagram = converter.convert(text)
        assert diagram.nodes[0].node_type == expected_type
