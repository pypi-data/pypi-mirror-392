"""Phase 4 feature examples: Advanced Diagramming Features.

Demonstrates:
- Bidirectional D2 conversion
- Sequence diagram generation
- Diagram transformations and optimization
- Multi-format workflows
"""


def example1_d2_bidirectional():
    """Example 1: Bidirectional D2 conversion."""
    print("=" * 60)
    print("Example 1: Bidirectional D2 Conversion")
    print("=" * 60)

    from ij import D2Parser, D2Renderer, MermaidRenderer

    # Start with D2 code
    d2_code = """
direction: right

start: "Begin" {
  shape: oval
}

validate: "Validate Input" {
  shape: diamond
}

process: "Process Data" {
  shape: rectangle
}

db: "Save to Database" {
  shape: cylinder
}

end: "Complete" {
  shape: oval
}

start -> validate
validate -> process: "Valid"
validate -> end: "Invalid"
process -> db
db -> end
"""

    print("Original D2 Code:")
    print(d2_code)

    # Parse D2 to DiagramIR
    parser = D2Parser()
    diagram = parser.parse(d2_code)

    print(f"\nParsed DiagramIR: {len(diagram.nodes)} nodes, {len(diagram.edges)} edges")

    # Render to Mermaid
    mermaid_renderer = MermaidRenderer()
    mermaid_code = mermaid_renderer.render(diagram)

    print("\nConverted to Mermaid:")
    print(mermaid_code)

    # Render back to D2
    d2_renderer = D2Renderer()
    d2_roundtrip = d2_renderer.render(diagram)

    print("\nRoundtrip back to D2:")
    print(d2_roundtrip)
    print()


def example2_sequence_diagrams():
    """Example 2: Sequence diagram generation."""
    print("=" * 60)
    print("Example 2: Sequence Diagram Generation")
    print("=" * 60)

    from ij import DiagramIR, Edge, EdgeType, Node, SequenceDiagramRenderer

    # Create a sequence diagram for an API call
    diagram = DiagramIR(metadata={"title": "User Authentication Flow"})

    # Add participants
    diagram.add_node(Node(id="user", label="User"))
    diagram.add_node(Node(id="frontend", label="Frontend"))
    diagram.add_node(Node(id="api", label="API"))
    diagram.add_node(Node(id="db", label="Database"))

    # Add interactions
    diagram.add_edge(Edge(source="user", target="frontend", label="Enter credentials"))
    diagram.add_edge(Edge(source="frontend", target="api", label="POST /login"))
    diagram.add_edge(Edge(source="api", target="db", label="Check credentials"))
    diagram.add_edge(
        Edge(source="db", target="api", label="User found", edge_type=EdgeType.CONDITIONAL)
    )
    diagram.add_edge(
        Edge(source="api", target="frontend", label="200 OK + token", edge_type=EdgeType.CONDITIONAL)
    )
    diagram.add_edge(
        Edge(source="frontend", target="user", label="Welcome!", edge_type=EdgeType.CONDITIONAL)
    )

    # Render as Mermaid sequence diagram
    renderer = SequenceDiagramRenderer()
    mermaid = renderer.render(diagram)

    print("Generated Sequence Diagram (Mermaid):")
    print(mermaid)
    print()


def example3_interaction_from_code():
    """Example 3: Generate sequence diagram from code."""
    print("=" * 60)
    print("Example 3: Code to Sequence Diagram")
    print("=" * 60)

    from ij import InteractionAnalyzer, SequenceDiagramRenderer

    # Python code with method calls
    code = """
user.authenticate(credentials)
session.create(user_id)
cache.store(session_token)
logger.log("User logged in", user_id)
"""

    print("Python Code:")
    print(code)

    # Analyze to create sequence diagram
    analyzer = InteractionAnalyzer()
    diagram = analyzer.analyze_function_calls("app", code)

    # Render
    renderer = SequenceDiagramRenderer()
    mermaid = renderer.render(diagram)

    print("\nGenerated Sequence Diagram:")
    print(mermaid)
    print()


def example4_interaction_from_text():
    """Example 4: Generate sequence diagram from natural language."""
    print("=" * 60)
    print("Example 4: Text to Sequence Diagram")
    print("=" * 60)

    from ij import InteractionAnalyzer, SequenceDiagramRenderer

    text = """
    Customer sends order to WebShop.
    WebShop queries Inventory.
    Inventory returns availability to WebShop.
    WebShop requests PaymentGateway.
    PaymentGateway responds to WebShop.
    WebShop confirms to Customer.
    """

    print("Natural Language Description:")
    print(text)

    # Parse text to sequence diagram
    analyzer = InteractionAnalyzer()
    diagram = analyzer.from_text_description(text)

    # Render
    renderer = SequenceDiagramRenderer()
    mermaid = renderer.render(diagram)

    print("\nGenerated Sequence Diagram:")
    print(mermaid)
    print()


def example5_diagram_transformations():
    """Example 5: Diagram transformation and optimization."""
    print("=" * 60)
    print("Example 5: Diagram Transformations")
    print("=" * 60)

    from ij import DiagramIR, DiagramTransforms, Edge, Node, NodeType

    # Create a diagram with some issues
    diagram = DiagramIR(metadata={"title": "Original Diagram"})
    diagram.add_node(Node(id="start", label="Start", node_type=NodeType.START))
    diagram.add_node(Node(id="step1", label="Step 1"))
    diagram.add_node(Node(id="step2", label="Step 2"))
    diagram.add_node(Node(id="isolated", label="Isolated Node"))
    diagram.add_node(Node(id="end", label="End", node_type=NodeType.END))

    diagram.add_edge(Edge(source="start", target="step1"))
    diagram.add_edge(Edge(source="step1", target="step2"))
    diagram.add_edge(Edge(source="step2", target="end"))
    diagram.add_edge(Edge(source="start", target="step1"))  # Duplicate

    print(f"Original: {len(diagram.nodes)} nodes, {len(diagram.edges)} edges")

    # Simplify: remove isolated nodes and duplicate edges
    simplified = DiagramTransforms.simplify(diagram)
    print(f"After simplify: {len(simplified.nodes)} nodes, {len(simplified.edges)} edges")

    # Get statistics
    stats = DiagramTransforms.get_statistics(simplified)
    print(f"\nDiagram Statistics:")
    print(f"  - Node count: {stats['node_count']}")
    print(f"  - Edge count: {stats['edge_count']}")
    print(f"  - Isolated nodes: {stats['isolated_nodes']}")
    print(f"  - Has cycles: {stats['has_cycles']}")
    print(f"  - Node types: {stats['node_types']}")
    print()


def example6_filter_and_extract():
    """Example 6: Filtering and extracting subgraphs."""
    print("=" * 60)
    print("Example 6: Filter and Extract Subgraphs")
    print("=" * 60)

    from ij import DiagramIR, DiagramTransforms, Edge, Node, NodeType

    # Create a larger diagram
    diagram = DiagramIR()
    diagram.add_node(Node(id="start", label="Start", node_type=NodeType.START))
    diagram.add_node(Node(id="process1", label="Process 1", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="decision", label="Decision", node_type=NodeType.DECISION))
    diagram.add_node(Node(id="process2", label="Process 2", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="data", label="Database", node_type=NodeType.DATA))
    diagram.add_node(Node(id="end", label="End", node_type=NodeType.END))

    diagram.add_edge(Edge(source="start", target="process1"))
    diagram.add_edge(Edge(source="process1", target="decision"))
    diagram.add_edge(Edge(source="decision", target="process2"))
    diagram.add_edge(Edge(source="process2", target="data"))
    diagram.add_edge(Edge(source="data", target="end"))

    print(f"Original diagram: {len(diagram.nodes)} nodes")

    # Filter: keep only PROCESS nodes
    process_only = DiagramTransforms.filter_by_node_type(
        diagram, [NodeType.PROCESS], keep=True
    )
    print(f"After filtering to PROCESS nodes: {len(process_only.nodes)} nodes")

    # Extract subgraph from decision node with depth 2
    subgraph = DiagramTransforms.extract_subgraph(diagram, "decision", max_depth=2)
    print(f"Subgraph from 'decision' (depth 2): {len(subgraph.nodes)} nodes")
    print()


def example7_merge_diagrams():
    """Example 7: Merging multiple diagrams."""
    print("=" * 60)
    print("Example 7: Merge Multiple Diagrams")
    print("=" * 60)

    from ij import DiagramIR, DiagramTransforms, Edge, Node

    # Create diagram 1: User flow
    user_flow = DiagramIR(metadata={"title": "User Flow"})
    user_flow.add_node(Node(id="login", label="Login"))
    user_flow.add_node(Node(id="dashboard", label="Dashboard"))
    user_flow.add_edge(Edge(source="login", target="dashboard"))

    # Create diagram 2: Admin flow
    admin_flow = DiagramIR(metadata={"title": "Admin Flow"})
    admin_flow.add_node(Node(id="admin_login", label="Admin Login"))
    admin_flow.add_node(Node(id="admin_panel", label="Admin Panel"))
    admin_flow.add_edge(Edge(source="admin_login", target="admin_panel"))

    # Merge both diagrams
    merged = DiagramTransforms.merge_diagrams(
        [user_flow, admin_flow], title="Complete Application Flow"
    )

    print(f"User flow: {len(user_flow.nodes)} nodes")
    print(f"Admin flow: {len(admin_flow.nodes)} nodes")
    print(f"Merged: {len(merged.nodes)} nodes, {len(merged.edges)} edges")
    print(f"Merged title: {merged.metadata.get('title')}")
    print()


def example8_find_cycles():
    """Example 8: Detecting cycles in diagrams."""
    print("=" * 60)
    print("Example 8: Cycle Detection")
    print("=" * 60)

    from ij import DiagramIR, DiagramTransforms, Edge, Node

    # Create a diagram with a cycle
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_node(Node(id="c", label="C"))

    diagram.add_edge(Edge(source="a", target="b"))
    diagram.add_edge(Edge(source="b", target="c"))
    diagram.add_edge(Edge(source="c", target="a"))  # Creates cycle

    # Detect cycles
    cycles = DiagramTransforms.find_cycles(diagram)

    print(f"Found {len(cycles)} cycle(s)")
    for i, cycle in enumerate(cycles, 1):
        print(f"  Cycle {i}: {' -> '.join(cycle)}")
    print()


def example9_multi_format_workflow():
    """Example 9: Multi-format conversion workflow."""
    print("=" * 60)
    print("Example 9: Multi-Format Conversion Workflow")
    print("=" * 60)

    from ij import (
        D2Renderer,
        DiagramIR,
        Edge,
        GraphvizRenderer,
        MermaidRenderer,
        Node,
        PlantUMLRenderer,
    )

    # Create a simple diagram
    diagram = DiagramIR(metadata={"title": "Multi-Format Demo"})
    diagram.add_node(Node(id="start", label="Start"))
    diagram.add_node(Node(id="process", label="Process"))
    diagram.add_node(Node(id="end", label="End"))

    diagram.add_edge(Edge(source="start", target="process"))
    diagram.add_edge(Edge(source="process", target="end"))

    print("Converting diagram to multiple formats:\n")

    # Render to Mermaid
    mermaid = MermaidRenderer().render(diagram)
    print("1. Mermaid (GitHub/GitLab):")
    print(mermaid[:150] + "...\n")

    # Render to PlantUML
    plantuml = PlantUMLRenderer().render(diagram)
    print("2. PlantUML (Enterprise docs):")
    print(plantuml[:150] + "...\n")

    # Render to D2
    d2 = D2Renderer().render(diagram)
    print("3. D2 (Modern/Beautiful):")
    print(d2[:150] + "...\n")

    # Render to Graphviz
    graphviz = GraphvizRenderer().render(diagram)
    print("4. Graphviz/DOT (Classic):")
    print(graphviz[:150] + "...\n")

    print("✅ Same diagram, four different formats!")
    print()


def example10_custom_filtering():
    """Example 10: Custom filtering with predicates."""
    print("=" * 60)
    print("Example 10: Custom Node Filtering")
    print("=" * 60)

    from ij import DiagramIR, DiagramTransforms, Edge, Node

    # Create diagram
    diagram = DiagramIR()
    diagram.add_node(Node(id="n1", label="Handle error"))
    diagram.add_node(Node(id="n2", label="Process data"))
    diagram.add_node(Node(id="n3", label="Log error"))
    diagram.add_node(Node(id="n4", label="Save result"))

    diagram.add_edge(Edge(source="n1", target="n3"))
    diagram.add_edge(Edge(source="n2", target="n4"))

    print(f"Original: {len(diagram.nodes)} nodes")

    # Filter: keep only error-related nodes
    error_nodes = DiagramTransforms.apply_node_filter(
        diagram, lambda n: "error" in n.label.lower()
    )

    print(f"Error-related nodes only: {len(error_nodes.nodes)} nodes")
    for node in error_nodes.nodes:
        print(f"  - {node.label}")
    print()


if __name__ == "__main__":
    # D2 and format conversion examples
    example1_d2_bidirectional()
    example9_multi_format_workflow()

    # Sequence diagram examples
    example2_sequence_diagrams()
    example3_interaction_from_code()
    example4_interaction_from_text()

    # Transformation examples
    example5_diagram_transformations()
    example6_filter_and_extract()
    example7_merge_diagrams()
    example8_find_cycles()
    example10_custom_filtering()

    print("=" * 60)
    print("Phase 4 Examples Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✅ Bidirectional D2 conversion (parse & render)")
    print("✅ Sequence diagram generation")
    print("✅ Interaction analysis from code and text")
    print("✅ Diagram transformations (simplify, filter, extract)")
    print("✅ Multi-diagram merging")
    print("✅ Cycle detection")
    print("✅ Custom filtering with predicates")
    print("✅ Multi-format export (Mermaid, PlantUML, D2, Graphviz)")
    print("\nPhase 4 brings advanced diagram manipulation and multi-format support!")
