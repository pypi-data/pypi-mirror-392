"""Tests for diagram parsers."""

import pytest
from ij.parsers import MermaidParser
from ij.core import NodeType, EdgeType


def test_mermaid_parser_simple():
    """Test parsing simple Mermaid diagram."""
    mermaid_text = """
    flowchart TD
        n1([Start])
        n2[Process]
        n3([End])
        n1 --> n2
        n2 --> n3
    """

    parser = MermaidParser()
    diagram = parser.parse(mermaid_text)

    assert len(diagram.nodes) == 3
    assert len(diagram.edges) == 2
    assert diagram.validate()


def test_mermaid_parser_with_title():
    """Test parsing diagram with title."""
    mermaid_text = """
    ---
    title: My Process
    ---
    flowchart TD
        n1[Step 1]
    """

    parser = MermaidParser()
    diagram = parser.parse(mermaid_text)

    assert diagram.metadata["title"] == "My Process"


def test_mermaid_parser_node_shapes():
    """Test parsing different node shapes."""
    mermaid_text = """
    flowchart TD
        n1([Start])
        n2{Decision?}
        n3[(Database)]
        n4[[Subprocess]]
        n5[Process]
    """

    parser = MermaidParser()
    diagram = parser.parse(mermaid_text)

    nodes = {node.id: node for node in diagram.nodes}

    assert nodes["n1"].node_type == NodeType.START
    assert nodes["n2"].node_type == NodeType.DECISION
    assert nodes["n3"].node_type == NodeType.DATA
    assert nodes["n4"].node_type == NodeType.SUBPROCESS
    assert nodes["n5"].node_type == NodeType.PROCESS


def test_mermaid_parser_edges_with_labels():
    """Test parsing edges with labels."""
    mermaid_text = """
    flowchart TD
        n1[A]
        n2[B]
        n1 -->|Yes| n2
    """

    parser = MermaidParser()
    diagram = parser.parse(mermaid_text)

    assert len(diagram.edges) == 1
    edge = diagram.edges[0]
    assert edge.label == "Yes"
    assert edge.source == "n1"
    assert edge.target == "n2"


def test_mermaid_parser_edge_types():
    """Test parsing different edge types."""
    mermaid_text = """
    flowchart TD
        n1[A]
        n2[B]
        n3[C]
        n4[D]
        n1 --> n2
        n2 -.-> n3
        n3 <--> n4
    """

    parser = MermaidParser()
    diagram = parser.parse(mermaid_text)

    edges = diagram.edges
    assert edges[0].edge_type == EdgeType.DIRECT
    assert edges[1].edge_type == EdgeType.CONDITIONAL
    assert edges[2].edge_type == EdgeType.BIDIRECTIONAL


def test_mermaid_parser_direction():
    """Test parsing diagram direction."""
    mermaid_text = """
    flowchart LR
        n1[A] --> n2[B]
    """

    parser = MermaidParser()
    diagram = parser.parse(mermaid_text)

    assert diagram.metadata["direction"] == "LR"


def test_mermaid_parser_roundtrip():
    """Test roundtrip conversion: IR -> Mermaid -> IR."""
    from ij import DiagramIR, Node, Edge, NodeType
    from ij.renderers import MermaidRenderer

    # Create original diagram
    original = DiagramIR()
    original.add_node(Node(id="n1", label="Start", node_type=NodeType.START))
    original.add_node(Node(id="n2", label="Process", node_type=NodeType.PROCESS))
    original.add_node(Node(id="n3", label="End", node_type=NodeType.END))
    original.add_edge(Edge(source="n1", target="n2"))
    original.add_edge(Edge(source="n2", target="n3"))

    # Convert to Mermaid
    renderer = MermaidRenderer()
    mermaid_text = renderer.render(original)

    # Parse back
    parser = MermaidParser()
    parsed = parser.parse(mermaid_text)

    # Verify
    assert len(parsed.nodes) == len(original.nodes)
    assert len(parsed.edges) == len(original.edges)
    assert parsed.validate()
