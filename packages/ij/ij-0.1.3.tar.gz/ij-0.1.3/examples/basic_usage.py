"""Basic usage examples for Idea Junction."""

from ij import (
    DiagramIR,
    Edge,
    EdgeType,
    MermaidRenderer,
    Node,
    NodeType,
    SimpleTextConverter,
    text_to_mermaid,
)


def example1_simple_conversion():
    """Example 1: Simple text-to-diagram conversion."""
    print("=" * 60)
    print("Example 1: Simple text-to-diagram conversion")
    print("=" * 60)

    text = "Start -> Process data -> Make decision -> End"
    mermaid = text_to_mermaid(text)

    print(f"Input: {text}")
    print("\nGenerated Mermaid diagram:")
    print(mermaid)
    print()


def example2_manual_diagram_creation():
    """Example 2: Manually create a diagram using DiagramIR."""
    print("=" * 60)
    print("Example 2: Manual diagram creation")
    print("=" * 60)

    # Create diagram
    diagram = DiagramIR(metadata={"title": "User Registration Flow"})

    # Add nodes
    diagram.add_node(Node(id="start", label="User visits site", node_type=NodeType.START))
    diagram.add_node(
        Node(id="check", label="Has account?", node_type=NodeType.DECISION)
    )
    diagram.add_node(Node(id="login", label="Login", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="register", label="Register", node_type=NodeType.PROCESS))
    diagram.add_node(
        Node(id="save", label="Save to database", node_type=NodeType.DATA)
    )
    diagram.add_node(Node(id="end", label="Welcome page", node_type=NodeType.END))

    # Add edges
    diagram.add_edge(Edge(source="start", target="check"))
    diagram.add_edge(Edge(source="check", target="login", label="Yes"))
    diagram.add_edge(Edge(source="check", target="register", label="No"))
    diagram.add_edge(Edge(source="register", target="save"))
    diagram.add_edge(Edge(source="login", target="end"))
    diagram.add_edge(Edge(source="save", target="end"))

    # Render to Mermaid
    renderer = MermaidRenderer(direction="TD")
    mermaid = renderer.render(diagram)

    print("Generated Mermaid diagram:")
    print(mermaid)
    print()


def example3_graph_analysis():
    """Example 3: Graph analysis using NetworkX integration."""
    print("=" * 60)
    print("Example 3: Graph analysis")
    print("=" * 60)

    from ij.graph_ops import GraphOperations

    # Create a workflow diagram
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="Start"))
    diagram.add_node(Node(id="b", label="Step 1"))
    diagram.add_node(Node(id="c", label="Step 2"))
    diagram.add_node(Node(id="d", label="Step 3"))
    diagram.add_node(Node(id="e", label="End"))

    diagram.add_edge(Edge(source="a", target="b"))
    diagram.add_edge(Edge(source="b", target="c"))
    diagram.add_edge(Edge(source="b", target="d"))
    diagram.add_edge(Edge(source="c", target="e"))
    diagram.add_edge(Edge(source="d", target="e"))

    # Analyze the diagram
    paths = GraphOperations.find_paths(diagram, "a", "e")
    print(f"All paths from Start to End:")
    for i, path in enumerate(paths, 1):
        path_labels = [diagram.get_node(nid).label for nid in path]
        print(f"  Path {i}: {' → '.join(path_labels)}")

    topo_order = GraphOperations.topological_sort(diagram)
    if topo_order:
        print(f"\nTopological order: {' → '.join(topo_order)}")
    print()


def example4_different_directions():
    """Example 4: Different diagram directions."""
    print("=" * 60)
    print("Example 4: Different diagram directions")
    print("=" * 60)

    text = "Input -> Process -> Output"

    for direction in ["TD", "LR", "BT", "RL"]:
        mermaid = text_to_mermaid(text, direction=direction)
        print(f"\nDirection: {direction}")
        print(mermaid)


def example5_from_natural_language():
    """Example 5: Converting natural language ideas to diagrams."""
    print("=" * 60)
    print("Example 5: Natural language to diagrams")
    print("=" * 60)

    ideas = [
        "Start the application",
        "Load configuration file",
        "Check if database is ready",
        "Initialize services",
        "Start web server",
        "End setup",
    ]

    # Join with arrows
    text = " -> ".join(ideas)

    converter = SimpleTextConverter()
    diagram = converter.convert(text, title="Application Startup")

    renderer = MermaidRenderer()
    mermaid = renderer.render(diagram)

    print("Ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"  {i}. {idea}")

    print("\nGenerated diagram:")
    print(mermaid)
    print()


def example6_saving_to_file():
    """Example 6: Save diagram to file."""
    print("=" * 60)
    print("Example 6: Saving to file")
    print("=" * 60)

    text = "Design -> Implement -> Test -> Deploy"
    converter = SimpleTextConverter()
    diagram = converter.convert(text, title="Software Development Cycle")

    renderer = MermaidRenderer()
    output_file = "/tmp/diagram.mmd"
    renderer.render_to_file(diagram, output_file)

    print(f"Diagram saved to: {output_file}")
    print("\nFile contents:")
    with open(output_file) as f:
        print(f.read())


if __name__ == "__main__":
    example1_simple_conversion()
    example2_manual_diagram_creation()
    example3_graph_analysis()
    example4_different_directions()
    example5_from_natural_language()
    example6_saving_to_file()
