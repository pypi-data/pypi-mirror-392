"""Phase 3 feature examples: AI/LLM Integration and Code Analysis.

NOTE: LLM examples require OPENAI_API_KEY environment variable and the openai package:
    pip install ij[ai]
    export OPENAI_API_KEY=your-key-here
"""

import os


def example1_python_code_analysis():
    """Example 1: Analyze Python function to create flowchart."""
    print("=" * 60)
    print("Example 1: Python Code Analysis - Function Flowchart")
    print("=" * 60)

    from ij.analyzers import PythonCodeAnalyzer
    from ij.renderers import MermaidRenderer

    code = """
def process_order(order):
    if order.is_valid():
        if order.in_stock():
            charge_customer(order)
            ship_order(order)
            send_confirmation(order)
        else:
            send_backorder_notice(order)
    else:
        send_error_notification(order)
    return order.status
"""

    print("Python Code:")
    print(code)

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    renderer = MermaidRenderer()
    mermaid = renderer.render(diagram)

    print("\nGenerated Flowchart (Mermaid):")
    print(mermaid)
    print()


def example2_call_graph():
    """Example 2: Generate call graph from Python module."""
    print("=" * 60)
    print("Example 2: Python Module Call Graph")
    print("=" * 60)

    from ij.analyzers import PythonCodeAnalyzer
    from ij.renderers import D2Renderer

    code = """
def load_config():
    return read_file("config.json")

def initialize():
    config = load_config()
    setup_database(config)
    setup_logging(config)

def main():
    initialize()
    run_app()
"""

    print("Python Code:")
    print(code)

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_module_calls(code)

    # Render as D2 for nice visualization
    renderer = D2Renderer()
    d2 = renderer.render(diagram)

    print("\nGenerated Call Graph (D2):")
    print(d2)
    print()


def example3_class_diagram():
    """Example 3: Generate class diagram from Python class."""
    print("=" * 60)
    print("Example 3: Python Class Diagram")
    print("=" * 60)

    from ij.analyzers import PythonCodeAnalyzer
    from ij.renderers import MermaidRenderer

    code = """
class BaseHandler:
    def handle(self):
        pass

class AuthHandler(BaseHandler):
    def __init__(self):
        self.auth_service = None

    def handle(self):
        return self.authenticate()

    def authenticate(self):
        pass
"""

    print("Python Code:")
    print(code)

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_class(code, class_name="AuthHandler")

    renderer = MermaidRenderer()
    mermaid = renderer.render(diagram)

    print("\nGenerated Class Diagram (Mermaid):")
    print(mermaid)
    print()


def example4_llm_conversion():
    """Example 4: AI-powered natural language to diagram (requires OpenAI API key)."""
    print("=" * 60)
    print("Example 4: AI/LLM-Powered Diagram Generation")
    print("=" * 60)

    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Skipping - OPENAI_API_KEY not set")
        print(
            "To run this example, set your OpenAI API key:\n"
            "  export OPENAI_API_KEY=your-key-here\n"
        )
        return

    try:
        from ij.converters import LLMConverter
        from ij.renderers import MermaidRenderer
    except ImportError:
        print("⚠️  Skipping - OpenAI package not installed")
        print("Install with: pip install ij[ai]\n")
        return

    description = """
    A user visits an e-commerce website. They browse products and add items to
    their cart. When ready to checkout, the system checks if they're logged in.
    If not, they must login or create an account. After authentication, they
    proceed to payment. If payment succeeds, the order is confirmed and items
    are shipped. If payment fails, an error is shown.
    """

    print(f"Natural Language Description:{description}")

    print("\nGenerating diagram with AI (using gpt-4o-mini)...")

    try:
        converter = LLMConverter(model="gpt-4o-mini", temperature=0.3)
        diagram = converter.convert(description, title="E-commerce Checkout")

        renderer = MermaidRenderer()
        mermaid = renderer.render(diagram)

        print("\nAI-Generated Diagram (Mermaid):")
        print(mermaid)

        print("\n✅ Success! The AI understood the process and created a diagram.")
        print(
            f"   Generated {len(diagram.nodes)} nodes and {len(diagram.edges)} edges."
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print()


def example5_llm_refinement():
    """Example 5: Iterative diagram refinement with AI."""
    print("=" * 60)
    print("Example 5: AI-Powered Diagram Refinement")
    print("=" * 60)

    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Skipping - OPENAI_API_KEY not set\n")
        return

    try:
        from ij.converters import LLMConverter
        from ij.renderers import MermaidRenderer
    except ImportError:
        print("⚠️  Skipping - OpenAI package not installed\n")
        return

    print("Initial description: User login process")

    try:
        converter = LLMConverter(model="gpt-4o-mini", temperature=0.3)
        diagram = converter.convert("User login process")

        renderer = MermaidRenderer()
        initial_mermaid = renderer.render(diagram)

        print("\nInitial Diagram:")
        print(initial_mermaid)

        print("\nRefining with feedback: 'Add password reset option'...")

        refined = converter.refine(
            diagram,
            "Add a password reset option if login fails",
            initial_mermaid,
        )

        refined_mermaid = renderer.render(refined)

        print("\nRefined Diagram:")
        print(refined_mermaid)

        print("\n✅ Diagram updated based on feedback!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print()


def example6_code_to_multiple_formats():
    """Example 6: Analyze code and export to multiple diagram formats."""
    print("=" * 60)
    print("Example 6: Code Analysis → Multiple Formats")
    print("=" * 60)

    from ij.analyzers import PythonCodeAnalyzer
    from ij.renderers import MermaidRenderer, PlantUMLRenderer, D2Renderer

    code = """
def validate_user(username, password):
    if not username:
        return False
    if not password:
        return False
    if check_credentials(username, password):
        log_success(username)
        return True
    else:
        log_failure(username)
        return False
"""

    print("Python Code:")
    print(code)

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    print("\nGenerated diagrams in multiple formats:\n")

    # Mermaid
    mermaid = MermaidRenderer().render(diagram)
    print("1. Mermaid (for GitHub/GitLab):")
    print(mermaid[:200] + "...\n")

    # PlantUML
    plantuml = PlantUMLRenderer().render(diagram)
    print("2. PlantUML (for enterprise):")
    print(plantuml[:200] + "...\n")

    # D2
    d2 = D2Renderer().render(diagram)
    print("3. D2 (modern/beautiful):")
    print(d2[:200] + "...\n")

    print(
        "✅ Same diagram, three formats! Use whichever fits your workflow best."
    )
    print()


def example7_combined_workflow():
    """Example 7: Combined workflow - Code analysis + AI enhancement."""
    print("=" * 60)
    print("Example 7: Hybrid Workflow (Code + AI)")
    print("=" * 60)

    from ij.analyzers import PythonCodeAnalyzer
    from ij.renderers import MermaidRenderer

    # Step 1: Analyze existing code
    code = """
def checkout():
    cart = get_cart()
    total = calculate_total(cart)
    process_payment(total)
"""

    print("Step 1: Analyze existing code")
    print(code)

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    renderer = MermaidRenderer()
    mermaid = renderer.render(diagram)

    print("\nGenerated diagram:")
    print(mermaid)

    # Step 2: Use AI to enhance if available
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from ij.converters import LLMConverter

            print(
                "\nStep 2: Enhance with AI - adding error handling..."
            )

            converter = LLMConverter(model="gpt-4o-mini")
            enhanced = converter.refine(
                diagram,
                "Add error handling for payment failures and empty cart scenarios",
                mermaid,
            )

            enhanced_mermaid = renderer.render(enhanced)
            print("\nAI-Enhanced Diagram:")
            print(enhanced_mermaid)
        except ImportError:
            print("\nStep 2: Install openai package to enable AI enhancement")
    else:
        print("\nStep 2: Set OPENAI_API_KEY to enable AI enhancement")

    print()


if __name__ == "__main__":
    # Code analysis examples (always work)
    example1_python_code_analysis()
    example2_call_graph()
    example3_class_diagram()
    example6_code_to_multiple_formats()
    example7_combined_workflow()

    # AI examples (require API key)
    example4_llm_conversion()
    example5_llm_refinement()

    print("=" * 60)
    print("Phase 3 Examples Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✅ Python code → flowchart diagrams")
    print("✅ Call graph generation")
    print("✅ Class diagram generation")
    print("✅ AI-powered natural language → diagram")
    print("✅ Iterative refinement with AI")
    print("✅ Multi-format export")
    print("✅ Hybrid code + AI workflows")
    print("\nFor AI features, install: pip install ij[ai]")
    print("And set: export OPENAI_API_KEY=your-key-here")
