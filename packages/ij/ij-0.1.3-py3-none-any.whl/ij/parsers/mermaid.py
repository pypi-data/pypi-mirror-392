"""Mermaid diagram parser.

Converts Mermaid syntax back to DiagramIR, enabling bidirectional conversion.
"""

import re
from typing import Dict, List, Optional, Tuple
from ..core import DiagramIR, Edge, EdgeType, Node, NodeType


class MermaidParser:
    """Parses Mermaid flowchart syntax to DiagramIR.

    Supports basic flowchart syntax including:
    - Node definitions with various shapes
    - Edge connections with labels
    - Title metadata
    """

    # Pattern for flowchart declaration
    FLOWCHART_PATTERN = re.compile(r"flowchart\s+(TD|LR|BT|RL)")

    # Pattern for title
    TITLE_PATTERN = re.compile(r"title:\s*(.+)")

    # Pattern for node with shape
    NODE_PATTERNS = [
        # Stadium shape: n1([Label])
        (re.compile(r"(\w+)\(\[(.+?)\]\)"), NodeType.START),
        # Rhombus: n1{Label}
        (re.compile(r"(\w+)\{(.+?)\}"), NodeType.DECISION),
        # Cylindrical: n1[(Label)]
        (re.compile(r"(\w+)\[\((.+?)\)\]"), NodeType.DATA),
        # Subroutine: n1[[Label]]
        (re.compile(r"(\w+)\[\[(.+?)\]\]"), NodeType.SUBPROCESS),
        # Rectangle: n1[Label]
        (re.compile(r"(\w+)\[(.+?)\]"), NodeType.PROCESS),
    ]

    # Pattern for edges
    EDGE_PATTERNS = [
        # With label: n1 -->|label| n2
        (
            re.compile(r"(\w+)\s+(-->|<-->|-\.->)\s*\|([^|]+)\|\s*(\w+)"),
            "labeled",
        ),
        # Simple: n1 --> n2
        (re.compile(r"(\w+)\s+(-->|<-->|-\.->)\s+(\w+)"), "simple"),
    ]

    ARROW_TO_EDGE_TYPE = {
        "-->": EdgeType.DIRECT,
        "-.->": EdgeType.CONDITIONAL,
        "<-->": EdgeType.BIDIRECTIONAL,
    }

    def __init__(self):
        """Initialize parser."""
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.metadata: Dict = {}

    def parse(self, mermaid_text: str) -> DiagramIR:
        """Parse Mermaid syntax to DiagramIR.

        Args:
            mermaid_text: Mermaid flowchart syntax

        Returns:
            DiagramIR representation

        Raises:
            ValueError: If the syntax is invalid
        """
        self.nodes = {}
        self.edges = []
        self.metadata = {}

        lines = mermaid_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line or line.startswith("---"):
                continue

            # Check for title
            title_match = self.TITLE_PATTERN.match(line)
            if title_match:
                self.metadata["title"] = title_match.group(1).strip()
                continue

            # Check for flowchart declaration
            flowchart_match = self.FLOWCHART_PATTERN.match(line)
            if flowchart_match:
                self.metadata["direction"] = flowchart_match.group(1)
                continue

            # Try to parse as edge
            if self._parse_edge(line):
                continue

            # Try to parse as node
            self._parse_node(line)

        # Build DiagramIR
        diagram = DiagramIR(metadata=self.metadata)
        for node in self.nodes.values():
            diagram.add_node(node)
        for edge in self.edges:
            diagram.add_edge(edge)

        return diagram

    def _parse_node(self, line: str) -> bool:
        """Parse a node definition.

        Args:
            line: Line containing node definition

        Returns:
            True if successfully parsed, False otherwise
        """
        for pattern, node_type in self.NODE_PATTERNS:
            match = pattern.search(line)
            if match:
                node_id = match.group(1)
                label = match.group(2)

                # Determine if it's START or END based on label
                if node_type == NodeType.START:
                    # Check if label suggests END
                    if any(
                        word in label.lower()
                        for word in ["end", "finish", "complete", "done"]
                    ):
                        node_type = NodeType.END

                if node_id not in self.nodes:
                    self.nodes[node_id] = Node(
                        id=node_id, label=label, node_type=node_type
                    )
                return True

        return False

    def _parse_edge(self, line: str) -> bool:
        """Parse an edge definition.

        Args:
            line: Line containing edge definition

        Returns:
            True if successfully parsed, False otherwise
        """
        # Try labeled edge first
        for pattern, edge_kind in self.EDGE_PATTERNS:
            match = pattern.match(line)
            if match:
                if edge_kind == "labeled":
                    source = match.group(1)
                    arrow = match.group(2)
                    label = match.group(3).strip()
                    target = match.group(4)
                else:  # simple
                    source = match.group(1)
                    arrow = match.group(2)
                    target = match.group(3)
                    label = None

                # Ensure nodes exist
                if source not in self.nodes:
                    self.nodes[source] = Node(
                        id=source, label=source, node_type=NodeType.PROCESS
                    )
                if target not in self.nodes:
                    self.nodes[target] = Node(
                        id=target, label=target, node_type=NodeType.PROCESS
                    )

                edge_type = self.ARROW_TO_EDGE_TYPE.get(arrow, EdgeType.DIRECT)
                self.edges.append(
                    Edge(source=source, target=target, label=label, edge_type=edge_type)
                )
                return True

        return False

    def parse_file(self, filename: str) -> DiagramIR:
        """Parse Mermaid file to DiagramIR.

        Args:
            filename: Path to Mermaid file

        Returns:
            DiagramIR representation
        """
        with open(filename, "r") as f:
            return self.parse(f.read())
