"""D2 diagram renderer.

Converts DiagramIR to D2 (Terrastruct) syntax, a modern diagram-as-code
language with excellent aesthetics and bidirectional editing support.
"""

from typing import Dict
from ..core import DiagramIR, EdgeType, NodeType


class D2Renderer:
    """Renders DiagramIR to D2 syntax.

    D2 is a modern diagram language with clean syntax, multiple layout engines,
    and PowerPoint export capabilities.
    """

    # Map node types to D2 shapes
    NODE_SHAPES: Dict[NodeType, str] = {
        NodeType.START: "oval",
        NodeType.END: "oval",
        NodeType.PROCESS: "rectangle",
        NodeType.DECISION: "diamond",
        NodeType.DATA: "cylinder",
        NodeType.SUBPROCESS: "rectangle",
        NodeType.CUSTOM: "rectangle",
    }

    def __init__(self, layout: str = "dagre"):
        """Initialize renderer.

        Args:
            layout: Layout engine (dagre, elk, tala)
        """
        self.layout = layout

    def render(self, diagram: DiagramIR) -> str:
        """Render a DiagramIR to D2 syntax.

        Args:
            diagram: The diagram to render

        Returns:
            D2 syntax as a string
        """
        if not diagram.validate():
            raise ValueError("Invalid diagram structure")

        lines = []

        # Add title as a comment and direction
        if "title" in diagram.metadata:
            lines.append(f"# {diagram.metadata['title']}")
            lines.append("")

        # Set direction based on metadata
        direction = diagram.metadata.get("direction", "down")
        d2_direction = self._convert_direction(direction)
        if d2_direction:
            lines.append(f"direction: {d2_direction}")
            lines.append("")

        # Render nodes
        for node in diagram.nodes:
            node_def = self._render_node(node)
            lines.append(node_def)

        if diagram.nodes:
            lines.append("")

        # Render edges
        for edge in diagram.edges:
            edge_def = self._render_edge(edge)
            lines.append(edge_def)

        return "\n".join(lines)

    def _convert_direction(self, mermaid_direction: str) -> str:
        """Convert Mermaid direction to D2 direction."""
        direction_map = {
            "TD": "down",
            "BT": "up",
            "LR": "right",
            "RL": "left",
        }
        return direction_map.get(mermaid_direction, "down")

    def _render_node(self, node) -> str:
        """Render a single node to D2 syntax."""
        # Sanitize label for D2
        label = node.label.replace('"', '\\"')

        # Get shape
        shape = self.NODE_SHAPES.get(node.node_type, "rectangle")

        # Style start/end nodes differently
        if node.node_type in [NodeType.START, NodeType.END]:
            style = " {style.fill: '#90EE90'; style.stroke: '#228B22'}"
        elif node.node_type == NodeType.DECISION:
            style = " {style.fill: '#FFE4B5'; style.stroke: '#FF8C00'}"
        elif node.node_type == NodeType.DATA:
            style = " {style.fill: '#B0E0E6'; style.stroke: '#4682B4'}"
        else:
            style = ""

        return f'{node.id}: "{label}" {{\n  shape: {shape}{style}\n}}'

    def _render_edge(self, edge) -> str:
        """Render a single edge to D2 syntax."""
        # Determine arrow style
        if edge.edge_type == EdgeType.BIDIRECTIONAL:
            arrow = "<->"
        elif edge.edge_type == EdgeType.CONDITIONAL:
            arrow = "->  {style.stroke-dash: 3}"
        else:
            arrow = "->"

        if edge.label:
            # Edge with label
            label = edge.label.replace('"', '\\"')
            return f'{edge.source} {arrow} {edge.target}: "{label}"'
        else:
            # Simple edge
            if edge.edge_type == EdgeType.CONDITIONAL:
                return f"{edge.source} -> {edge.target} {{style.stroke-dash: 3}}"
            else:
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
