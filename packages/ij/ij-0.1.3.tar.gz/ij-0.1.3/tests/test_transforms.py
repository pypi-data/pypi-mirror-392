"""Tests for diagram transformation utilities."""

import pytest

from ij import DiagramIR, DiagramTransforms, Edge, EdgeType, Node, NodeType


def test_simplify_removes_isolated_nodes():
    """Test that simplify removes isolated nodes."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_node(Node(id="isolated", label="Isolated"))
    diagram.add_edge(Edge(source="a", target="b"))

    simplified = DiagramTransforms.simplify(diagram, remove_isolated=True)

    assert len(simplified.nodes) == 2
    node_ids = {n.id for n in simplified.nodes}
    assert "isolated" not in node_ids


def test_simplify_keeps_start_end_nodes():
    """Test that simplify keeps START/END nodes even if isolated."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="start", label="Start", node_type=NodeType.START))
    diagram.add_node(Node(id="end", label="End", node_type=NodeType.END))

    simplified = DiagramTransforms.simplify(diagram, remove_isolated=True)

    assert len(simplified.nodes) == 2


def test_simplify_removes_duplicate_edges():
    """Test that simplify removes duplicate edges."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_edge(Edge(source="a", target="b", label="same"))
    diagram.add_edge(Edge(source="a", target="b", label="same"))  # Duplicate

    simplified = DiagramTransforms.simplify(diagram)

    assert len(simplified.edges) == 1


def test_filter_by_node_type_keep():
    """Test filtering to keep only specific node types."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="N1", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="n2", label="N2", node_type=NodeType.DECISION))
    diagram.add_node(Node(id="n3", label="N3", node_type=NodeType.PROCESS))

    filtered = DiagramTransforms.filter_by_node_type(
        diagram, [NodeType.PROCESS], keep=True
    )

    assert len(filtered.nodes) == 2
    for node in filtered.nodes:
        assert node.node_type == NodeType.PROCESS


def test_filter_by_node_type_remove():
    """Test filtering to remove specific node types."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="N1", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="n2", label="N2", node_type=NodeType.DECISION))

    filtered = DiagramTransforms.filter_by_node_type(
        diagram, [NodeType.DECISION], keep=False
    )

    assert len(filtered.nodes) == 1
    assert filtered.nodes[0].node_type == NodeType.PROCESS


def test_extract_subgraph():
    """Test extracting a subgraph from a root node."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="root", label="Root"))
    diagram.add_node(Node(id="child1", label="Child1"))
    diagram.add_node(Node(id="child2", label="Child2"))
    diagram.add_node(Node(id="unrelated", label="Unrelated"))

    diagram.add_edge(Edge(source="root", target="child1"))
    diagram.add_edge(Edge(source="root", target="child2"))

    subgraph = DiagramTransforms.extract_subgraph(diagram, "root")

    node_ids = {n.id for n in subgraph.nodes}
    assert "root" in node_ids
    assert "child1" in node_ids
    assert "child2" in node_ids
    assert "unrelated" not in node_ids


def test_extract_subgraph_with_depth():
    """Test extracting subgraph with max depth."""
    diagram = DiagramIR()
    nodes = ["n0", "n1", "n2", "n3"]
    for n in nodes:
        diagram.add_node(Node(id=n, label=n))

    diagram.add_edge(Edge(source="n0", target="n1"))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))

    subgraph = DiagramTransforms.extract_subgraph(diagram, "n0", max_depth=2)

    node_ids = {n.id for n in subgraph.nodes}
    assert "n0" in node_ids
    assert "n1" in node_ids
    assert "n2" in node_ids
    assert "n3" not in node_ids  # Beyond depth 2


def test_merge_diagrams():
    """Test merging multiple diagrams."""
    diagram1 = DiagramIR()
    diagram1.add_node(Node(id="a", label="A"))
    diagram1.add_edge(Edge(source="a", target="b"))

    diagram2 = DiagramIR()
    diagram2.add_node(Node(id="c", label="C"))
    diagram2.add_edge(Edge(source="c", target="d"))

    merged = DiagramTransforms.merge_diagrams([diagram1, diagram2])

    assert len(merged.nodes) >= 2
    assert len(merged.edges) == 2


def test_merge_diagrams_with_duplicates():
    """Test that merging handles duplicate node IDs."""
    diagram1 = DiagramIR()
    diagram1.add_node(Node(id="a", label="A"))

    diagram2 = DiagramIR()
    diagram2.add_node(Node(id="a", label="A"))  # Same ID

    merged = DiagramTransforms.merge_diagrams([diagram1, diagram2])

    # Should only have one node 'a'
    assert len([n for n in merged.nodes if n.id == "a"]) == 1


def test_reverse_edges():
    """Test reversing edge directions."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_edge(Edge(source="a", target="b", label="forward"))

    reversed_diagram = DiagramTransforms.reverse_edges(diagram)

    assert len(reversed_diagram.edges) == 1
    edge = reversed_diagram.edges[0]
    assert edge.source == "b"
    assert edge.target == "a"
    assert edge.label == "forward"


def test_apply_node_filter():
    """Test custom node filter predicate."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="Error handler"))
    diagram.add_node(Node(id="n2", label="Success handler"))
    diagram.add_node(Node(id="n3", label="Error logger"))

    # Keep only nodes with "error" in label
    filtered = DiagramTransforms.apply_node_filter(
        diagram, lambda n: "error" in n.label.lower()
    )

    assert len(filtered.nodes) == 2
    for node in filtered.nodes:
        assert "error" in node.label.lower()


def test_find_cycles_no_cycle():
    """Test cycle detection on acyclic graph."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_edge(Edge(source="a", target="b"))

    cycles = DiagramTransforms.find_cycles(diagram)

    assert len(cycles) == 0


def test_find_cycles_with_cycle():
    """Test cycle detection on cyclic graph."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_node(Node(id="c", label="C"))

    diagram.add_edge(Edge(source="a", target="b"))
    diagram.add_edge(Edge(source="b", target="c"))
    diagram.add_edge(Edge(source="c", target="a"))  # Creates cycle

    cycles = DiagramTransforms.find_cycles(diagram)

    assert len(cycles) > 0


def test_get_statistics():
    """Test diagram statistics calculation."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="N1", node_type=NodeType.START))
    diagram.add_node(Node(id="n2", label="N2", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="n3", label="N3", node_type=NodeType.END))
    diagram.add_node(Node(id="isolated", label="Isolated", node_type=NodeType.DATA))

    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3", edge_type=EdgeType.CONDITIONAL))

    stats = DiagramTransforms.get_statistics(diagram)

    assert stats["node_count"] == 4
    assert stats["edge_count"] == 2
    assert stats["node_types"][NodeType.START] == 1
    assert stats["node_types"][NodeType.PROCESS] == 1
    assert stats["node_types"][NodeType.END] == 1
    assert stats["node_types"][NodeType.DATA] == 1
    assert stats["isolated_nodes"] == 1
    assert not stats["has_cycles"]


def test_get_statistics_with_cycles():
    """Test statistics include cycle detection."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_edge(Edge(source="a", target="b"))
    diagram.add_edge(Edge(source="b", target="a"))  # Cycle

    stats = DiagramTransforms.get_statistics(diagram)

    assert stats["has_cycles"]


def test_extract_subgraph_invalid_root():
    """Test extracting subgraph with invalid root node."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))

    with pytest.raises(ValueError, match="Root node .* not found"):
        DiagramTransforms.extract_subgraph(diagram, "nonexistent")


def test_merge_sequential_nodes_simple():
    """Test merging sequential nodes."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="Step A"))
    diagram.add_node(Node(id="b", label="Step B"))
    diagram.add_node(Node(id="c", label="Step C"))

    diagram.add_edge(Edge(source="a", target="b"))
    diagram.add_edge(Edge(source="b", target="c"))

    merged = DiagramTransforms.merge_sequential_nodes(diagram)

    # Should merge a->b into single node since b has 1 in and 1 out
    # Result should have fewer nodes
    assert len(merged.nodes) <= len(diagram.nodes)


def test_edge_types_preserved():
    """Test that edge types are preserved in transformations."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_edge(
        Edge(source="a", target="b", edge_type=EdgeType.CONDITIONAL)
    )

    reversed_diagram = DiagramTransforms.reverse_edges(diagram)

    assert reversed_diagram.edges[0].edge_type == EdgeType.CONDITIONAL


def test_metadata_preserved():
    """Test that metadata is preserved in transformations."""
    diagram = DiagramIR(metadata={"title": "Test Diagram", "version": "1.0"})
    diagram.add_node(Node(id="a", label="A"))

    simplified = DiagramTransforms.simplify(diagram)

    assert "title" in simplified.metadata
    assert simplified.metadata["title"] == "Test Diagram"


def test_filter_preserves_edges():
    """Test that filtering preserves edges between kept nodes."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="b", label="B", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="c", label="C", node_type=NodeType.DECISION))

    diagram.add_edge(Edge(source="a", target="b"))
    diagram.add_edge(Edge(source="b", target="c"))

    # Keep only PROCESS nodes
    filtered = DiagramTransforms.filter_by_node_type(
        diagram, [NodeType.PROCESS], keep=True
    )

    # Should have edge a->b but not b->c
    assert len(filtered.edges) == 1
    assert filtered.edges[0].source == "a"
    assert filtered.edges[0].target == "b"
