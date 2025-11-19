"""Mermaid diagram renderer.

Converts DiagramIR to Mermaid syntax, following the research recommendation
to use Mermaid for its GitHub integration and simplicity.
"""

from typing import Dict
from ..core import DiagramIR, EdgeType, NodeType


class MermaidRenderer:
    """Renders DiagramIR to Mermaid syntax.

    Supports flowchart diagrams with various node shapes and edge types.
    """

    # Map node types to Mermaid shapes
    NODE_SHAPES: Dict[NodeType, tuple] = {
        NodeType.PROCESS: ("[", "]"),  # Rectangle
        NodeType.DECISION: ("{", "}"),  # Rhombus
        NodeType.START: ("([", "])"),  # Stadium
        NodeType.END: ("([", "])"),  # Stadium
        NodeType.DATA: ("[(", ")]"),  # Cylindrical
        NodeType.SUBPROCESS: ("[[", "]]"),  # Subroutine
        NodeType.CUSTOM: ("[", "]"),  # Default rectangle
    }

    # Map edge types to Mermaid arrows
    EDGE_ARROWS: Dict[EdgeType, str] = {
        EdgeType.DIRECT: "-->",
        EdgeType.CONDITIONAL: "-.->",
        EdgeType.BIDIRECTIONAL: "<-->",
    }

    def __init__(self, direction: str = "TD"):
        """Initialize renderer.

        Args:
            direction: Flow direction (TD=top-down, LR=left-right, etc.)
        """
        self.direction = direction

    def render(self, diagram: DiagramIR) -> str:
        """Render a DiagramIR to Mermaid syntax.

        Args:
            diagram: The diagram to render

        Returns:
            Mermaid syntax as a string
        """
        if not diagram.validate():
            raise ValueError("Invalid diagram structure")

        lines = [f"flowchart {self.direction}"]

        # Add title if present
        if "title" in diagram.metadata:
            lines.insert(0, f"---\ntitle: {diagram.metadata['title']}\n---")

        # Render nodes
        for node in diagram.nodes:
            node_def = self._render_node(node)
            lines.append(f"    {node_def}")

        # Render edges
        for edge in diagram.edges:
            edge_def = self._render_edge(edge)
            lines.append(f"    {edge_def}")

        return "\n".join(lines)

    def _render_node(self, node) -> str:
        """Render a single node to Mermaid syntax."""
        shape_start, shape_end = self.NODE_SHAPES[node.node_type]
        # Sanitize label for Mermaid
        label = node.label.replace('"', "'")
        return f"{node.id}{shape_start}{label}{shape_end}"

    def _render_edge(self, edge) -> str:
        """Render a single edge to Mermaid syntax."""
        arrow = self.EDGE_ARROWS[edge.edge_type]

        if edge.label:
            # Edge with label
            label = edge.label.replace('"', "'")
            return f"{edge.source} {arrow}|{label}| {edge.target}"
        else:
            # Simple edge
            return f"{edge.source} {arrow} {edge.target}"

    def render_to_file(self, diagram: DiagramIR, filename: str) -> None:
        """Render diagram and save to file.

        Args:
            diagram: The diagram to render
            filename: Path to output file
        """
        content = self.render(diagram)
        with open(filename, "w") as f:
            f.write(content)
