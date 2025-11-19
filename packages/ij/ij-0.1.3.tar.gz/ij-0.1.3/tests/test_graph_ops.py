"""Tests for graph operations."""

import pytest
from ij.core import DiagramIR, Edge, Node, NodeType
from ij.graph_ops import GraphOperations


def test_to_networkx():
    """Test conversion to NetworkX."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_edge(Edge(source="n1", target="n2"))

    G = GraphOperations.to_networkx(diagram)

    assert G.number_of_nodes() == 2
    assert G.number_of_edges() == 1
    assert "n1" in G.nodes
    assert "n2" in G.nodes
    assert G.has_edge("n1", "n2")


def test_from_networkx():
    """Test conversion from NetworkX."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A", node_type=NodeType.START))
    diagram.add_node(Node(id="n2", label="B", node_type=NodeType.END))
    diagram.add_edge(Edge(source="n1", target="n2", label="go"))

    # Convert to NetworkX and back
    G = GraphOperations.to_networkx(diagram)
    diagram2 = GraphOperations.from_networkx(G)

    assert len(diagram2.nodes) == 2
    assert len(diagram2.edges) == 1
    assert diagram2.get_node("n1").label == "A"
    assert diagram2.get_node("n1").node_type == NodeType.START


def test_find_paths():
    """Test path finding."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_node(Node(id="n3", label="C"))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))
    diagram.add_edge(Edge(source="n1", target="n3"))  # Direct path

    paths = GraphOperations.find_paths(diagram, "n1", "n3")

    assert len(paths) == 2  # Two paths: direct and via n2
    assert ["n1", "n3"] in paths
    assert ["n1", "n2", "n3"] in paths


def test_find_cycles():
    """Test cycle detection."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_node(Node(id="n3", label="C"))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))
    diagram.add_edge(Edge(source="n3", target="n1"))  # Creates cycle

    cycles = GraphOperations.find_cycles(diagram)

    assert len(cycles) > 0


def test_topological_sort():
    """Test topological sorting."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_node(Node(id="n3", label="C"))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))

    order = GraphOperations.topological_sort(diagram)

    assert order is not None
    assert order.index("n1") < order.index("n2")
    assert order.index("n2") < order.index("n3")


def test_topological_sort_with_cycle():
    """Test topological sort fails with cycles."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n1"))  # Cycle

    order = GraphOperations.topological_sort(diagram)

    assert order is None  # Should fail due to cycle


def test_simplify_diagram():
    """Test diagram simplification."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_node(Node(id="n3", label="C"))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))
    diagram.add_edge(Edge(source="n1", target="n3"))  # Redundant edge

    simplified = GraphOperations.simplify_diagram(diagram)

    # Should remove the redundant direct edge from n1 to n3
    assert len(simplified.edges) == 2
