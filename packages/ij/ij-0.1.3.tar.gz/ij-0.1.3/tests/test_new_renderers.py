"""Tests for PlantUML, D2, and Graphviz renderers."""

import pytest
from ij.core import DiagramIR, Edge, Node, NodeType
from ij.renderers import PlantUMLRenderer, D2Renderer, GraphvizRenderer


def create_sample_diagram():
    """Create a sample diagram for testing."""
    diagram = DiagramIR(metadata={"title": "Test Process"})
    diagram.add_node(Node(id="n1", label="Start", node_type=NodeType.START))
    diagram.add_node(Node(id="n2", label="Process", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="n3", label="End", node_type=NodeType.END))
    diagram.add_edge(Edge(source="n1", target="n2"))
    diagram.add_edge(Edge(source="n2", target="n3"))
    return diagram


def test_plantuml_simple_diagram():
    """Test PlantUML rendering."""
    diagram = create_sample_diagram()
    renderer = PlantUMLRenderer()
    output = renderer.render(diagram)

    assert "@startuml" in output
    assert "@enduml" in output
    assert "title Test Process" in output
    assert "start" in output
    assert "stop" in output
    assert ":Process;" in output


def test_plantuml_without_skinparam():
    """Test PlantUML without styling."""
    diagram = create_sample_diagram()
    renderer = PlantUMLRenderer(use_skinparam=False)
    output = renderer.render(diagram)

    assert "skinparam" not in output
    assert "@startuml" in output


def test_d2_simple_diagram():
    """Test D2 rendering."""
    diagram = create_sample_diagram()
    renderer = D2Renderer()
    output = renderer.render(diagram)

    assert "# Test Process" in output
    assert 'n1: "Start"' in output
    assert 'shape: oval' in output
    assert 'n2: "Process"' in output
    assert 'n3: "End"' in output
    assert "n1 -> n2" in output
    assert "n2 -> n3" in output


def test_d2_with_decision():
    """Test D2 rendering with decision nodes."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="Check", node_type=NodeType.DECISION))
    diagram.add_node(Node(id="n2", label="Yes path"))
    diagram.add_edge(Edge(source="n1", target="n2", label="Yes"))

    renderer = D2Renderer()
    output = renderer.render(diagram)

    assert "shape: diamond" in output
    assert 'n1 -> n2: "Yes"' in output


def test_d2_direction():
    """Test D2 direction conversion."""
    diagram = DiagramIR(metadata={"direction": "LR"})
    diagram.add_node(Node(id="n1", label="A"))

    renderer = D2Renderer()
    output = renderer.render(diagram)

    assert "direction: right" in output


def test_graphviz_simple_diagram():
    """Test Graphviz rendering."""
    diagram = create_sample_diagram()
    renderer = GraphvizRenderer()
    output = renderer.render(diagram)

    assert "digraph G {" in output
    assert "}" in output
    assert 'label="Test Process"' in output
    assert 'n1 [label="Start"' in output
    assert 'n2 [label="Process"' in output
    assert 'n3 [label="End"' in output
    assert "n1 -> n2" in output
    assert "n2 -> n3" in output


def test_graphviz_node_shapes():
    """Test Graphviz node shapes."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="Start", node_type=NodeType.START))
    diagram.add_node(Node(id="n2", label="Decide", node_type=NodeType.DECISION))
    diagram.add_node(Node(id="n3", label="Data", node_type=NodeType.DATA))

    renderer = GraphvizRenderer()
    output = renderer.render(diagram)

    assert "shape=oval" in output  # START
    assert "shape=diamond" in output  # DECISION
    assert "shape=cylinder" in output  # DATA


def test_graphviz_edge_types():
    """Test Graphviz edge types."""
    from ij.core import EdgeType

    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_node(Node(id="n3", label="C"))

    diagram.add_edge(Edge(source="n1", target="n2", edge_type=EdgeType.CONDITIONAL))
    diagram.add_edge(
        Edge(source="n2", target="n3", edge_type=EdgeType.BIDIRECTIONAL)
    )

    renderer = GraphvizRenderer()
    output = renderer.render(diagram)

    assert "style=dashed" in output  # CONDITIONAL
    assert "dir=both" in output  # BIDIRECTIONAL


def test_graphviz_with_labels():
    """Test Graphviz with edge labels."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="A"))
    diagram.add_node(Node(id="n2", label="B"))
    diagram.add_edge(Edge(source="n1", target="n2", label="Yes"))

    renderer = GraphvizRenderer()
    output = renderer.render(diagram)

    assert 'label="Yes"' in output


def test_graphviz_layout():
    """Test Graphviz layout engine selection."""
    diagram = create_sample_diagram()

    for layout in ["dot", "neato", "fdp", "circo"]:
        renderer = GraphvizRenderer(layout=layout)
        output = renderer.render(diagram)
        assert f'layout="{layout}"' in output


def test_all_renderers_produce_output():
    """Test that all renderers produce non-empty output."""
    diagram = create_sample_diagram()

    renderers = [
        PlantUMLRenderer(),
        D2Renderer(),
        GraphvizRenderer(),
    ]

    for renderer in renderers:
        output = renderer.render(diagram)
        assert len(output) > 0
        assert isinstance(output, str)
