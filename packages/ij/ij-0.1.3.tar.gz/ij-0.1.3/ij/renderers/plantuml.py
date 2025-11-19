"""PlantUML diagram renderer.

Converts DiagramIR to PlantUML syntax, supporting activity diagrams
which are ideal for process flows.
"""

from typing import Dict
from ..core import DiagramIR, EdgeType, NodeType


class PlantUMLRenderer:
    """Renders DiagramIR to PlantUML activity diagram syntax.

    PlantUML is the enterprise standard for comprehensive UML diagrams
    with support for 25+ diagram types.
    """

    # Map node types to PlantUML syntax
    NODE_SYNTAX: Dict[NodeType, str] = {
        NodeType.START: "start",
        NodeType.END: "stop",
        NodeType.PROCESS: ":",
        NodeType.DECISION: "if",
        NodeType.DATA: ":",  # Use note for data
        NodeType.SUBPROCESS: ":",
        NodeType.CUSTOM: ":",
    }

    def __init__(self, use_skinparam: bool = True):
        """Initialize renderer.

        Args:
            use_skinparam: Whether to include modern styling
        """
        self.use_skinparam = use_skinparam

    def render(self, diagram: DiagramIR) -> str:
        """Render a DiagramIR to PlantUML syntax.

        Args:
            diagram: The diagram to render

        Returns:
            PlantUML syntax as a string
        """
        if not diagram.validate():
            raise ValueError("Invalid diagram structure")

        lines = ["@startuml"]

        # Add title if present
        if "title" in diagram.metadata:
            lines.append(f"title {diagram.metadata['title']}")
            lines.append("")

        # Add modern styling
        if self.use_skinparam:
            lines.extend(
                [
                    "skinparam ActivityFontSize 14",
                    "skinparam ActivityBorderColor #2C3E50",
                    "skinparam ActivityBackgroundColor #ECF0F1",
                    "",
                ]
            )

        # Build a graph structure to understand flow
        node_map = {node.id: node for node in diagram.nodes}
        edges_from = {}
        for edge in diagram.edges:
            if edge.source not in edges_from:
                edges_from[edge.source] = []
            edges_from[edge.source].append(edge)

        # Track rendered nodes to avoid duplicates
        rendered = set()

        # Render in topological order if possible
        from ..graph_ops import GraphOperations

        order = GraphOperations.topological_sort(diagram)
        if not order:
            # If there are cycles, just use node order
            order = [node.id for node in diagram.nodes]

        for node_id in order:
            if node_id in rendered:
                continue

            node = node_map[node_id]
            node_syntax = self._render_node(node)
            if node_syntax:
                lines.append(node_syntax)
                rendered.add(node_id)

            # Render edges from this node
            if node_id in edges_from:
                for edge in edges_from[node_id]:
                    edge_syntax = self._render_edge(edge, node_map)
                    if edge_syntax:
                        lines.append(edge_syntax)

        lines.append("@enduml")
        return "\n".join(lines)

    def _render_node(self, node) -> str:
        """Render a single node to PlantUML syntax."""
        if node.node_type == NodeType.START:
            return "start"
        elif node.node_type == NodeType.END:
            return "stop"
        elif node.node_type == NodeType.DECISION:
            # Decision nodes are rendered with edges
            return None
        elif node.node_type == NodeType.DATA:
            # Render as activity with note
            sanitized_label = node.label.replace(":", "\\:")
            return f":{sanitized_label};\nnote right: Data storage"
        else:
            # Regular activity
            sanitized_label = node.label.replace(":", "\\:")
            return f":{sanitized_label};"

    def _render_edge(self, edge, node_map) -> str:
        """Render an edge (primarily for decisions)."""
        source_node = node_map.get(edge.source)
        target_node = node_map.get(edge.target)

        if source_node and source_node.node_type == NodeType.DECISION:
            # This is a decision branch
            label = edge.label if edge.label else ""
            target_label = (
                target_node.label.replace(":", "\\:") if target_node else edge.target
            )

            if label:
                return f"if ({source_node.label}) then ({label})\n  :{target_label};\nendif"
            else:
                return None

        return None

    def render_to_file(self, diagram: DiagramIR, filename: str) -> None:
        """Render diagram and save to file.

        Args:
            diagram: The diagram to render
            filename: Path to output file
        """
        content = self.render(diagram)
        with open(filename, "w") as f:
            f.write(content)
