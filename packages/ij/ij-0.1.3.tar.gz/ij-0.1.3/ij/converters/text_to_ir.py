"""Text to DiagramIR converters.

This module provides simple rule-based conversion from structured text
to DiagramIR. Future versions can integrate AI/LLM-based conversion.
"""

import re
from typing import List, Tuple
from ..core import DiagramIR, Edge, EdgeType, Node, NodeType


class SimpleTextConverter:
    """Simple rule-based text to diagram converter.

    Parses structured text like:
    - "Start -> Process A -> Decision B"
    - "If condition: Process C, else: Process D"
    """

    def __init__(self):
        """Initialize converter."""
        self.node_counter = 0

    def convert(self, text: str, title: str = None) -> DiagramIR:
        """Convert structured text to DiagramIR.

        Args:
            text: Input text describing a process/flow
            title: Optional diagram title

        Returns:
            DiagramIR representation
        """
        diagram = DiagramIR()
        if title:
            diagram.metadata["title"] = title

        # Parse the text into steps
        steps = self._parse_steps(text)

        # Convert steps to nodes and edges
        previous_node_id = None
        for step_text, step_type in steps:
            node_id = f"n{self.node_counter}"
            self.node_counter += 1

            node = Node(id=node_id, label=step_text, node_type=step_type)
            diagram.add_node(node)

            # Connect to previous node
            if previous_node_id:
                edge = Edge(source=previous_node_id, target=node_id)
                diagram.add_edge(edge)

            previous_node_id = node_id

        return diagram

    def _parse_steps(self, text: str) -> List[Tuple[str, NodeType]]:
        """Parse text into a list of (step_text, node_type) tuples.

        Args:
            text: Input text

        Returns:
            List of tuples (step_text, node_type)
        """
        steps = []

        # Split by common delimiters
        parts = re.split(r"\s*->\s*|\s*→\s*|\n", text)

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            # Determine node type based on keywords
            node_type = self._infer_node_type(part, i, len(parts))
            steps.append((part, node_type))

        return steps

    def _infer_node_type(self, text: str, index: int, total: int) -> NodeType:
        """Infer node type from text content and position.

        Args:
            text: Node text
            index: Position in sequence
            total: Total number of nodes

        Returns:
            Inferred NodeType
        """
        text_lower = text.lower()

        # Check for explicit keywords
        if any(
            word in text_lower for word in ["start", "begin", "initialize", "open"]
        ):
            return NodeType.START
        elif any(word in text_lower for word in ["end", "finish", "complete", "close"]):
            return NodeType.END
        elif any(
            word in text_lower
            for word in ["if", "decide", "check", "verify", "validate", "?"]
        ):
            return NodeType.DECISION
        elif any(word in text_lower for word in ["database", "store", "save"]):
            return NodeType.DATA

        # Use position as hint
        if index == 0:
            return NodeType.START
        elif index == total - 1:
            return NodeType.END

        return NodeType.PROCESS


class StructuredTextConverter:
    """More advanced converter supporting branching and conditions.

    Planned for future implementation to handle:
    - Conditional branches
    - Parallel flows
    - Subprocesses
    - Loops
    """

    pass
