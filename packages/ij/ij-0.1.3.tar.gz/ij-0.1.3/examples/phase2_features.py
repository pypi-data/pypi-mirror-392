"""Phase 2 feature examples: Bidirectional conversion and multiple formats."""

from ij import DiagramIR, Node, Edge, NodeType
from ij.renderers import MermaidRenderer, PlantUMLRenderer, D2Renderer, GraphvizRenderer
from ij.parsers import MermaidParser
from ij.converters import EnhancedTextConverter


def example1_bidirectional_conversion():
    """Example 1: Bidirectional conversion - Mermaid to IR and back."""
    print("=" * 60)
    print("Example 1: Bidirectional Conversion")
    print("=" * 60)

    # Original Mermaid diagram
    original_mermaid = """
flowchart TD
    n1([Start])
    n2[Process Data]
    n3{Valid?}
    n4[Save]
    n5([End])
    n1 --> n2
    n2 --> n3
    n3 -->|Yes| n4
    n3 -->|No| n5
    n4 --> n5
"""

    print("Original Mermaid:")
    print(original_mermaid)

    # Parse to IR
    parser = MermaidParser()
    diagram = parser.parse(original_mermaid)

    print(f"\nParsed to DiagramIR:")
    print(f"  Nodes: {len(diagram.nodes)}")
    print(f"  Edges: {len(diagram.edges)}")

    # Render back to Mermaid
    renderer = MermaidRenderer()
    regenerated = renderer.render(diagram)

    print(f"\nRegenerated Mermaid:")
    print(regenerated)
    print()


def example2_multi_format_rendering():
    """Example 2: Render the same diagram in multiple formats."""
    print("=" * 60)
    print("Example 2: Multi-Format Rendering")
    print("=" * 60)

    # Create diagram
    diagram = DiagramIR(metadata={"title": "User Login Flow"})
    diagram.add_node(Node(id="start", label="User visits site", node_type=NodeType.START))
    diagram.add_node(Node(id="check", label="Has account?", node_type=NodeType.DECISION))
    diagram.add_node(Node(id="login", label="Login", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="register", label="Register", node_type=NodeType.PROCESS))
    diagram.add_node(Node(id="end", label="Dashboard", node_type=NodeType.END))

    diagram.add_edge(Edge(source="start", target="check"))
    diagram.add_edge(Edge(source="check", target="login", label="Yes"))
    diagram.add_edge(Edge(source="check", target="register", label="No"))
    diagram.add_edge(Edge(source="login", target="end"))
    diagram.add_edge(Edge(source="register", target="end"))

    # Render in all formats
    formats = {
        "Mermaid": MermaidRenderer(),
        "PlantUML": PlantUMLRenderer(),
        "D2": D2Renderer(),
        "Graphviz": GraphvizRenderer(),
    }

    for format_name, renderer in formats.items():
        output = renderer.render(diagram)
        print(f"\n{format_name} Output:")
        print("-" * 40)
        print(output[:300] + "..." if len(output) > 300 else output)

    print()


def example3_enhanced_text_conversion():
    """Example 3: Enhanced text converter with conditionals."""
    print("=" * 60)
    print("Example 3: Enhanced Text Conversion")
    print("=" * 60)

    converter = EnhancedTextConverter()

    # Conditional example
    text1 = "Start -> Check inventory. If available: Process order, else: Notify customer"
    print(f"Input: {text1}")

    diagram1 = converter.convert(text1, title="Order Processing")
    renderer = MermaidRenderer()
    print(f"\nMermaid Output:")
    print(renderer.render(diagram1))

    # Parallel example
    text2 = "Start -> [parallel: Send email, Update database, Log event] -> End"
    print(f"\nInput: {text2}")

    diagram2 = converter.convert(text2, title="Parallel Tasks")
    print(f"\nMermaid Output:")
    print(renderer.render(diagram2))
    print()


def example4_format_conversion():
    """Example 4: Convert between different diagram formats."""
    print("=" * 60)
    print("Example 4: Format Conversion")
    print("=" * 60)

    # Start with Mermaid
    mermaid_input = """
flowchart LR
    A[Input] --> B[Transform]
    B --> C[Validate]
    C --> D[Output]
"""

    print("Original Mermaid:")
    print(mermaid_input)

    # Parse
    parser = MermaidParser()
    diagram = parser.parse(mermaid_input)

    # Convert to D2
    d2_renderer = D2Renderer()
    d2_output = d2_renderer.render(diagram)

    print("\nConverted to D2:")
    print(d2_output)

    # Convert to PlantUML
    plantuml_renderer = PlantUMLRenderer()
    plantuml_output = plantuml_renderer.render(diagram)

    print("\nConverted to PlantUML:")
    print(plantuml_output)
    print()


def example5_save_multiple_formats():
    """Example 5: Save diagram in multiple formats."""
    print("=" * 60)
    print("Example 5: Save in Multiple Formats")
    print("=" * 60)

    # Create diagram
    from ij.converters import SimpleTextConverter

    converter = SimpleTextConverter()
    diagram = converter.convert(
        "Start -> Validate -> Process -> Store -> End",
        title="Data Pipeline"
    )

    # Save in multiple formats
    files = {
        "/tmp/diagram.mmd": MermaidRenderer(),
        "/tmp/diagram.puml": PlantUMLRenderer(),
        "/tmp/diagram.d2": D2Renderer(),
        "/tmp/diagram.dot": GraphvizRenderer(),
    }

    for filename, renderer in files.items():
        renderer.render_to_file(diagram, filename)
        print(f"Saved: {filename}")

    print("\nAll formats saved to /tmp/")
    print()


def example6_complex_workflow():
    """Example 6: Complex workflow with enhanced converter."""
    print("=" * 60)
    print("Example 6: Complex Workflow")
    print("=" * 60)

    converter = EnhancedTextConverter()

    # Complex workflow with loop
    text = """
    Start application.
    Load configuration.
    Initialize services.
    while requests pending: Process request.
    Shutdown gracefully.
    End application
    """

    print(f"Input:")
    print(text)

    diagram = converter.convert(text, title="Application Lifecycle")

    # Render in Mermaid
    mermaid_renderer = MermaidRenderer()
    mermaid_output = mermaid_renderer.render(diagram)

    print(f"\nMermaid Output:")
    print(mermaid_output)

    # Also render in D2 for comparison
    d2_renderer = D2Renderer()
    d2_output = d2_renderer.render(diagram)

    print(f"\nD2 Output:")
    print(d2_output)
    print()


if __name__ == "__main__":
    example1_bidirectional_conversion()
    example2_multi_format_rendering()
    example3_enhanced_text_conversion()
    example4_format_conversion()
    example5_save_multiple_formats()
    example6_complex_workflow()
