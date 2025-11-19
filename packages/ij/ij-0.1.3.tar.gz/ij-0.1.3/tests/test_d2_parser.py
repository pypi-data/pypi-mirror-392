"""Tests for D2 parser."""

import pytest

from ij import D2Parser
from ij.core import DiagramIR, EdgeType, NodeType


def test_d2_parser_simple_nodes():
    """Test parsing simple D2 nodes."""
    d2_code = """
n1: "Start" {
  shape: oval
}
n2: "Process" {
  shape: rectangle
}
n3: "End" {
  shape: oval
}
n1 -> n2
n2 -> n3
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 3
    assert len(diagram.edges) == 2

    # Check node types
    assert diagram.nodes[0].label == "Start"
    assert diagram.nodes[0].node_type == NodeType.START

    assert diagram.nodes[1].label == "Process"
    assert diagram.nodes[1].node_type == NodeType.PROCESS

    assert diagram.nodes[2].label == "End"
    assert diagram.nodes[2].node_type == NodeType.END


def test_d2_parser_decision_nodes():
    """Test parsing decision/diamond nodes."""
    d2_code = """
n1: "Check status" {
  shape: diamond
}
n2: "Success" {
  shape: rectangle
}
n3: "Failure" {
  shape: rectangle
}
n1 -> n2: "Yes"
n1 -> n3: "No"
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 3
    assert diagram.nodes[0].node_type == NodeType.DECISION
    assert diagram.nodes[0].label == "Check status"

    # Check edge labels
    assert diagram.edges[0].label == "Yes"
    assert diagram.edges[1].label == "No"


def test_d2_parser_data_nodes():
    """Test parsing data/cylinder nodes."""
    d2_code = """
n1: "Database" {
  shape: cylinder
}
n2: "Save data" {
  shape: rectangle
}
n2 -> n1
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 2
    assert diagram.nodes[0].node_type == NodeType.DATA
    assert diagram.nodes[0].label == "Database"


def test_d2_parser_direction():
    """Test parsing direction metadata."""
    d2_code = """
direction: right
n1: "A"
n2: "B"
n1 -> n2
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert diagram.metadata.get("direction") == "LR"


def test_d2_parser_all_directions():
    """Test parsing all direction options."""
    directions = {
        "down": "TD",
        "up": "BT",
        "right": "LR",
        "left": "RL",
    }

    for d2_dir, expected in directions.items():
        d2_code = f"direction: {d2_dir}\nn1: \"A\"\nn2: \"B\"\nn1 -> n2"
        parser = D2Parser()
        diagram = parser.parse(d2_code)
        assert diagram.metadata.get("direction") == expected


def test_d2_parser_simple_nodes_without_block():
    """Test parsing simple nodes without property blocks."""
    d2_code = """
n1: "First step"
n2: "Second step"
n1 -> n2
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 2
    assert diagram.nodes[0].label == "First step"
    assert diagram.nodes[0].node_type == NodeType.PROCESS
    assert diagram.nodes[1].label == "Second step"


def test_d2_parser_edges_with_labels():
    """Test parsing edges with labels."""
    d2_code = """
n1: "A"
n2: "B"
n3: "C"
n1 -> n2: "step 1"
n2 -> n3: "step 2"
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.edges) == 2
    assert diagram.edges[0].label == "step 1"
    assert diagram.edges[1].label == "step 2"


def test_d2_parser_conditional_edges():
    """Test parsing conditional/dashed edges."""
    d2_code = """
n1: "A"
n2: "B"
n1 -> n2 {style.stroke-dash: 3}
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.edges) == 1
    assert diagram.edges[0].edge_type == EdgeType.CONDITIONAL


def test_d2_parser_bidirectional_edges():
    """Test parsing bidirectional edges."""
    d2_code = """
n1: "A"
n2: "B"
n1 <-> n2
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.edges) == 1
    assert diagram.edges[0].edge_type == EdgeType.BIDIRECTIONAL


def test_d2_parser_auto_create_nodes():
    """Test that nodes are auto-created if referenced in edges."""
    d2_code = """
n1 -> n2
n2 -> n3
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 3
    # Auto-created nodes should have their ID as label
    assert diagram.nodes[0].label == "n1"
    assert diagram.nodes[1].label == "n2"
    assert diagram.nodes[2].label == "n3"


def test_d2_parser_start_end_inference():
    """Test inference of START/END nodes based on edges."""
    d2_code = """
n1: "First" {
  shape: oval
}
n2: "Middle" {
  shape: rectangle
}
n3: "Last" {
  shape: oval
}
n1 -> n2
n2 -> n3
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    # n1 has no incoming edges -> START
    # n3 has no outgoing edges -> END
    assert diagram.nodes[0].node_type == NodeType.START
    assert diagram.nodes[2].node_type == NodeType.END


def test_d2_parser_empty_input():
    """Test parsing empty D2 input."""
    parser = D2Parser()
    diagram = parser.parse("")

    assert len(diagram.nodes) == 0
    assert len(diagram.edges) == 0


def test_d2_parser_comments():
    """Test parsing D2 with comments."""
    d2_code = """
# This is a comment
n1: "Start"
# Another comment
n2: "End"
n1 -> n2
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1


def test_d2_parser_complex_flowchart():
    """Test parsing a complex D2 flowchart."""
    d2_code = """
direction: down

start: "Begin Process" {
  shape: oval
}

check: "Validate Input" {
  shape: diamond
}

process: "Process Data" {
  shape: rectangle
}

save: "Save to DB" {
  shape: cylinder
}

end: "Complete" {
  shape: oval
}

start -> check
check -> process: "Valid"
check -> end: "Invalid"
process -> save
save -> end
"""
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    assert len(diagram.nodes) == 5
    assert len(diagram.edges) == 5
    assert diagram.metadata.get("direction") == "TD"

    # Check specific node types
    node_map = {node.label: node for node in diagram.nodes}
    assert node_map["Begin Process"].node_type == NodeType.START
    assert node_map["Validate Input"].node_type == NodeType.DECISION
    assert node_map["Process Data"].node_type == NodeType.PROCESS
    assert node_map["Save to DB"].node_type == NodeType.DATA
    assert node_map["Complete"].node_type == NodeType.END


def test_d2_parser_roundtrip_with_renderer():
    """Test roundtrip: Mermaid -> IR -> D2 -> IR."""
    from ij import D2Renderer, MermaidParser

    mermaid_code = """
flowchart TD
    start([Start])
    process[Process Data]
    decision{Check Status}
    end_node([End])

    start --> process
    process --> decision
    decision -->|Success| end_node
    decision -->|Failure| process
"""

    # Parse Mermaid
    mermaid_parser = MermaidParser()
    diagram1 = mermaid_parser.parse(mermaid_code)

    # Render to D2
    d2_renderer = D2Renderer()
    d2_code = d2_renderer.render(diagram1)

    # Parse D2 back
    d2_parser = D2Parser()
    diagram2 = d2_parser.parse(d2_code)

    # Should have same structure
    assert len(diagram1.nodes) == len(diagram2.nodes)
    assert len(diagram1.edges) == len(diagram2.edges)


def test_d2_parser_file():
    """Test parsing D2 from file."""
    import tempfile

    d2_code = """
n1: "Start" {
  shape: oval
}
n2: "End" {
  shape: oval
}
n1 -> n2
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".d2", delete=False) as f:
        f.write(d2_code)
        f.flush()

        parser = D2Parser()
        diagram = parser.parse_file(f.name)

        assert len(diagram.nodes) == 2
        assert len(diagram.edges) == 1
