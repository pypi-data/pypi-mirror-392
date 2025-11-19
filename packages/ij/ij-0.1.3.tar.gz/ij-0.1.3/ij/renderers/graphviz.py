"""Graphviz/DOT diagram renderer.

Converts DiagramIR to DOT (Graphviz) syntax, the foundational graph
visualization language.
"""

from typing import Dict
from ..core import DiagramIR, EdgeType, NodeType


class GraphvizRenderer:
    """Renders DiagramIR to Graphviz DOT syntax.

    Graphviz is the 30-year-old foundation that underpins PlantUML,
    Structurizr, and many other tools.
    """

    # Map node types to Graphviz shapes
    NODE_SHAPES: Dict[NodeType, str] = {
        NodeType.START: "oval",
        NodeType.END: "oval",
        NodeType.PROCESS: "box",
        NodeType.DECISION: "diamond",
        NodeType.DATA: "cylinder",
        NodeType.SUBPROCESS: "box3d",
        NodeType.CUSTOM: "box",
    }

    def __init__(self, layout: str = "dot", graph_type: str = "digraph"):
        """Initialize renderer.

        Args:
            layout: Layout algorithm (dot, neato, fdp, sfdp, twopi, circo)
            graph_type: Graph type (digraph for directed, graph for undirected)
        """
        self.layout = layout
        self.graph_type = graph_type

    def render(self, diagram: DiagramIR) -> str:
        """Render a DiagramIR to DOT syntax.

        Args:
            diagram: The diagram to render

        Returns:
            DOT syntax as a string
        """
        if not diagram.validate():
            raise ValueError("Invalid diagram structure")

        lines = [f"{self.graph_type} G {{"]

        # Add graph attributes
        lines.append(f'  layout="{self.layout}";')
        lines.append('  rankdir="TB";')  # Top to bottom by default
        lines.append('  node [fontname="Arial", fontsize=12];')
        lines.append('  edge [fontname="Arial", fontsize=10];')

        # Add title as label if present
        if "title" in diagram.metadata:
            title = diagram.metadata["title"].replace('"', '\\"')
            lines.append(f'  label="{title}";')
            lines.append('  labelloc="t";')

        # Adjust rankdir based on direction
        if "direction" in diagram.metadata:
            rankdir = self._convert_direction(diagram.metadata["direction"])
            lines.append(f'  rankdir="{rankdir}";')

        lines.append("")

        # Render nodes
        for node in diagram.nodes:
            node_def = self._render_node(node)
            lines.append(f"  {node_def}")

        if diagram.nodes:
            lines.append("")

        # Render edges
        edge_op = "->" if self.graph_type == "digraph" else "--"
        for edge in diagram.edges:
            edge_def = self._render_edge(edge, edge_op)
            lines.append(f"  {edge_def}")

        lines.append("}")
        return "\n".join(lines)

    def _convert_direction(self, mermaid_direction: str) -> str:
        """Convert Mermaid direction to Graphviz rankdir."""
        direction_map = {
            "TD": "TB",  # Top to bottom
            "BT": "BT",  # Bottom to top
            "LR": "LR",  # Left to right
            "RL": "RL",  # Right to left
        }
        return direction_map.get(mermaid_direction, "TB")

    def _render_node(self, node) -> str:
        """Render a single node to DOT syntax."""
        # Sanitize label for DOT
        label = node.label.replace('"', '\\"')

        # Get shape and style
        shape = self.NODE_SHAPES.get(node.node_type, "box")

        # Style based on node type
        if node.node_type == NodeType.START:
            style = 'style=filled, fillcolor=lightgreen'
        elif node.node_type == NodeType.END:
            style = 'style=filled, fillcolor=lightcoral'
        elif node.node_type == NodeType.DECISION:
            style = 'style=filled, fillcolor=lightyellow'
        elif node.node_type == NodeType.DATA:
            style = 'style=filled, fillcolor=lightblue'
        else:
            style = 'style=filled, fillcolor=lightgray'

        return f'{node.id} [label="{label}", shape={shape}, {style}];'

    def _render_edge(self, edge, edge_op: str) -> str:
        """Render a single edge to DOT syntax."""
        # Determine edge style
        if edge.edge_type == EdgeType.BIDIRECTIONAL:
            edge_attrs = 'dir=both'
        elif edge.edge_type == EdgeType.CONDITIONAL:
            edge_attrs = 'style=dashed'
        else:
            edge_attrs = ''

        if edge.label:
            # Edge with label
            label = edge.label.replace('"', '\\"')
            if edge_attrs:
                return f'{edge.source} {edge_op} {edge.target} [label="{label}", {edge_attrs}];'
            else:
                return f'{edge.source} {edge_op} {edge.target} [label="{label}"];'
        else:
            # Simple edge
            if edge_attrs:
                return f'{edge.source} {edge_op} {edge.target} [{edge_attrs}];'
            else:
                return f'{edge.source} {edge_op} {edge.target};'

    def render_to_file(self, diagram: DiagramIR, filename: str) -> None:
        """Render diagram and save to file.

        Args:
            diagram: The diagram to render
            filename: Path to output file
        """
        content = self.render(diagram)
        with open(filename, "w") as f:
            f.write(content)

    def render_to_image(
        self, diagram: DiagramIR, filename: str, format: str = "png"
    ) -> None:
        """Render diagram directly to image using graphviz library.

        Args:
            diagram: The diagram to render
            filename: Path to output file (without extension)
            format: Output format (png, svg, pdf, etc.)
        """
        try:
            import graphviz

            dot_source = self.render(diagram)
            graph = graphviz.Source(dot_source, format=format)
            graph.render(filename, cleanup=True)
        except ImportError:
            raise ImportError(
                "graphviz library required for image rendering. "
                "Install with: pip install graphviz"
            )
