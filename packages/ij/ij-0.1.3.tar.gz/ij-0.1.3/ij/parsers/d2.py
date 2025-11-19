"""D2 diagram parser.

Parses D2 (Terrastruct) syntax to DiagramIR, completing bidirectional
support for the modern D2 format.
"""

import re
from typing import Dict, List, Optional, Tuple

from ..core import DiagramIR, Edge, EdgeType, Node, NodeType


class D2Parser:
    """Parse D2 syntax to DiagramIR.

    Supports basic D2 syntax including:
    - Node definitions with shapes and labels
    - Edge connections with labels
    - Direction metadata
    """

    # Shape to NodeType mapping
    SHAPE_TO_TYPE = {
        "oval": NodeType.START,  # Could be START or END, we'll infer
        "rectangle": NodeType.PROCESS,
        "diamond": NodeType.DECISION,
        "cylinder": NodeType.DATA,
    }

    def __init__(self):
        """Initialize parser."""
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.metadata: Dict = {}

    def parse(self, d2_text: str) -> DiagramIR:
        """Parse D2 syntax to DiagramIR.

        Args:
            d2_text: D2 diagram source

        Returns:
            DiagramIR representation

        Example:
            >>> parser = D2Parser()
            >>> d2_code = '''
            ... n1: "Start" {
            ...   shape: oval
            ... }
            ... n2: "Process" {
            ...   shape: rectangle
            ... }
            ... n1 -> n2
            ... '''
            >>> diagram = parser.parse(d2_code)
        """
        self.nodes = {}
        self.edges = []
        self.metadata = {}

        lines = d2_text.strip().split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                # Check for title comment
                if line.startswith("#") and not self.metadata.get("title"):
                    title = line[1:].strip()
                    if title and not title.startswith(" "):
                        self.metadata["title"] = title
                i += 1
                continue

            # Check for direction
            if line.startswith("direction:"):
                direction = line.split(":", 1)[1].strip()
                self.metadata["direction"] = self._convert_direction(direction)
                i += 1
                continue

            # Check for node definition with block
            node_match = re.match(r'(\w+):\s*"([^"]+)"\s*\{', line)
            if node_match:
                node_id = node_match.group(1)
                label = node_match.group(2)
                i += 1

                # Parse node properties
                shape = "rectangle"  # default
                while i < len(lines):
                    prop_line = lines[i].strip()
                    if prop_line == "}":
                        i += 1
                        break
                    if prop_line.startswith("shape:"):
                        shape = prop_line.split(":", 1)[1].strip()
                    i += 1

                node_type = self.SHAPE_TO_TYPE.get(shape, NodeType.PROCESS)
                self.nodes[node_id] = Node(
                    id=node_id, label=label, node_type=node_type
                )
                continue

            # Check for simple node
            simple_node = re.match(r'(\w+):\s*"([^"]+)"', line)
            if simple_node:
                node_id = simple_node.group(1)
                label = simple_node.group(2)
                if node_id not in self.nodes:
                    self.nodes[node_id] = Node(
                        id=node_id, label=label, node_type=NodeType.PROCESS
                    )
                i += 1
                continue

            # Check for edge
            edge_match = self._parse_edge_line(line)
            if edge_match:
                source, target, label, edge_type = edge_match
                # Ensure nodes exist
                if source not in self.nodes:
                    self.nodes[source] = Node(
                        id=source, label=source, node_type=NodeType.PROCESS
                    )
                if target not in self.nodes:
                    self.nodes[target] = Node(
                        id=target, label=target, node_type=NodeType.PROCESS
                    )

                self.edges.append(
                    Edge(source=source, target=target, label=label, edge_type=edge_type)
                )
                i += 1
                continue

            i += 1

        # Infer START/END for oval nodes
        self._infer_start_end()

        # Build diagram
        diagram = DiagramIR(metadata=self.metadata)
        for node in self.nodes.values():
            diagram.add_node(node)
        for edge in self.edges:
            diagram.add_edge(edge)

        return diagram

    def _parse_edge_line(self, line: str) -> Optional[Tuple[str, str, Optional[str], EdgeType]]:
        """Parse an edge line.

        Returns: (source, target, label, edge_type) or None
        """
        # Edge with label: n1 -> n2: "label"
        match = re.match(r'(\w+)\s*->\s*(\w+):\s*"([^"]+)"', line)
        if match:
            return (
                match.group(1),
                match.group(2),
                match.group(3),
                EdgeType.DIRECT,
            )

        # Edge with dashed style: n1 -> n2 {style.stroke-dash: 3}
        match = re.match(
            r'(\w+)\s*->\s*(\w+)\s*\{[^}]*stroke-dash[^}]*\}', line
        )
        if match:
            return (
                match.group(1),
                match.group(2),
                None,
                EdgeType.CONDITIONAL,
            )

        # Simple edge: n1 -> n2
        match = re.match(r'(\w+)\s*->\s*(\w+)', line)
        if match:
            return (
                match.group(1),
                match.group(2),
                None,
                EdgeType.DIRECT,
            )

        # Bidirectional: n1 <-> n2
        match = re.match(r'(\w+)\s*<->\s*(\w+)', line)
        if match:
            return (
                match.group(1),
                match.group(2),
                None,
                EdgeType.BIDIRECTIONAL,
            )

        return None

    def _convert_direction(self, d2_direction: str) -> str:
        """Convert D2 direction to Mermaid direction."""
        direction_map = {
            "down": "TD",
            "up": "BT",
            "right": "LR",
            "left": "RL",
        }
        return direction_map.get(d2_direction, "TD")

    def _infer_start_end(self):
        """Infer which oval nodes are START vs END based on edges."""
        # Nodes with no incoming edges are likely START
        # Nodes with no outgoing edges are likely END
        incoming = set()
        outgoing = set()

        for edge in self.edges:
            outgoing.add(edge.source)
            incoming.add(edge.target)

        for node_id, node in self.nodes.items():
            if node.node_type == NodeType.START:  # oval nodes
                if node_id in outgoing and node_id not in incoming:
                    node.node_type = NodeType.START
                elif node_id in incoming and node_id not in outgoing:
                    node.node_type = NodeType.END
                elif node_id not in outgoing and node_id not in incoming:
                    # Isolated oval, default to START
                    node.node_type = NodeType.START

    def parse_file(self, filename: str) -> DiagramIR:
        """Parse D2 file to DiagramIR.

        Args:
            filename: Path to D2 file

        Returns:
            DiagramIR representation
        """
        with open(filename, "r") as f:
            return self.parse(f.read())
