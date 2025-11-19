"""Tests for diagram renderers."""

import pytest
from ij.core import DiagramIR, Edge, Node, NodeType
from ij.renderers import MermaidRenderer


def test_mermaid_simple_diagram():
    """Test rendering a simple diagram to Mermaid."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="Start", node_type=NodeType.START))
    diagram.add_node(Node(id="n2", label="Process", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="n3", label="End", node_type=NodeType.END))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))

    renderer = MermaidRenderer()
    output = renderer.render(diagram)

    assert "flowchart TD" in output
    assert "n1([Start])" in output
    assert "n2[Process]" in output
    assert "n3([End])" in output
    assert "n1 --> n2" in output
    assert "n2 --> n3" in output


def test_mermaid_with_title():
    """Test rendering with title."""
    diagram = DiagramIR(metadata={"title": "My Process"})
    diagram.add_node(Node(id="n1", label="Step 1"))

    renderer = MermaidRenderer()
    output = renderer.render(diagram)

    assert "title: My Process" in output


def test_mermaid_node_shapes():
    """Test different node shapes."""
    diagram = DiagramIR()

    # Test different node types
    test_cases = [
        (NodeType.PROCESS, "[", "]"),
        (NodeType.DECISION, "{", "}"),
        (NodeType.START, "([", "])"),
        (NodeType.DATA, "[(", ")]"),
    ]

    for i, (node_type, start, end) in enumerate(test_cases):
        node = Node(id=f"n{i}", label=f"Test {i}", node_type=node_type)
        diagram.add_node(node)

    renderer = MermaidRenderer()
    output = renderer.render(diagram)

    for i, (_, start, end) in enumerate(test_cases):
        assert f"n{i}{start}Test {i}{end}" in output


def test_mermaid_edge_with_label():
    """Test rendering edges with labels."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_edge(Edge(source="n1", target="n2", label="Yes"))

    renderer = MermaidRenderer()
    output = renderer.render(diagram)

    assert "n1 -->|Yes| n2" in output


def test_mermaid_direction():
    """Test different diagram directions."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))

    # Test different directions
    for direction in ["TD", "LR", "BT", "RL"]:
        renderer = MermaidRenderer(direction=direction)
        output = renderer.render(diagram)
        assert f"flowchart {direction}" in output


def test_mermaid_invalid_diagram():
    """Test error handling for invalid diagrams."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_edge(Edge(source="n1", target="n999"))  # Invalid edge

    renderer = MermaidRenderer()
    with pytest.raises(ValueError):
        renderer.render(diagram)
