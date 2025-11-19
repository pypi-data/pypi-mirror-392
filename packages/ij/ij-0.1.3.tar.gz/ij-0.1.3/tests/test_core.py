"""Tests for core data structures."""

import pytest
from ij.core import DiagramIR, Edge, EdgeType, Node, NodeType


def test_node_creation():
    """Test creating nodes."""
    node = Node(id="n1", label="Test Node", node_type=NodeType.PROCESS)
    assert node.id == "n1"
    assert node.label == "Test Node"
    assert node.node_type == NodeType.PROCESS


def test_edge_creation():
    """Test creating edges."""
    edge = Edge(source="n1", target="n2", label="test", edge_type=EdgeType.DIRECT)
    assert edge.source == "n1"
    assert edge.target == "n2"
    assert edge.label == "test"


def test_diagram_ir():
    """Test DiagramIR operations."""
    diagram = DiagramIR()

    # Add nodes
    n1 = Node(id="n1", label="Start", node_type=NodeType.START)
    n2 = Node(id="n2", label="End", node_type=NodeType.END)
    diagram.add_node(n1)
    diagram.add_node(n2)

    # Add edge
    e1 = Edge(source="n1", target="n2")
    diagram.add_edge(e1)

    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1
    assert diagram.get_node("n1") == n1
    assert diagram.validate()


def test_diagram_validation():
    """Test diagram validation."""
    diagram = DiagramIR()

    # Valid diagram
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    diagram.add_node(n1)
    diagram.add_node(n2)
    diagram.add_edge(Edge(source="n1", target="n2"))
    assert diagram.validate()

    # Invalid: duplicate node IDs
    diagram.add_node(Node(id="n1", label="Duplicate"))
    assert not diagram.validate()

    # Invalid: edge references non-existent node
    diagram2 = DiagramIR()
    diagram2.add_node(Node(id="n1", label="A"))
    diagram2.add_edge(Edge(source="n1", target="n999"))
    assert not diagram2.validate()


def test_node_types():
    """Test all node types."""
    for node_type in NodeType:
        node = Node(id="test", label="Test", node_type=node_type)
        assert node.node_type == node_type


def test_edge_types():
    """Test all edge types."""
    for edge_type in EdgeType:
        edge = Edge(source="n1", target="n2", edge_type=edge_type)
        assert edge.edge_type == edge_type


def test_metadata():
    """Test metadata storage."""
    node = Node(
        id="n1", label="Test", metadata={"color": "blue", "custom": "value"}
    )
    assert node.metadata["color"] == "blue"
    assert node.metadata["custom"] == "value"

    edge = Edge(source="n1", target="n2", metadata={"weight": 5})
    assert edge.metadata["weight"] == 5

    diagram = DiagramIR(metadata={"title": "Test Diagram"})
    assert diagram.metadata["title"] == "Test Diagram"
