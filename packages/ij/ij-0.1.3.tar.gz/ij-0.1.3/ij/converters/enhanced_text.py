"""Enhanced text to DiagramIR converter with better NLP.

Provides more sophisticated text parsing with support for:
- Conditional branches
- Parallel flows
- Loop detection
- Better natural language understanding
"""

import re
from typing import Dict, List, Optional, Tuple
from ..core import DiagramIR, Edge, EdgeType, Node, NodeType


class EnhancedTextConverter:
    """Enhanced text-to-diagram converter with NLP capabilities.

    Supports:
    - Conditional branches (if/else)
    - Parallel flows (parallel keyword)
    - Loops (while, repeat)
    - Better keyword detection
    - Multiple sentence formats
    """

    def __init__(self):
        """Initialize converter."""
        self.node_counter = 0
        self.nodes_created = {}

    def convert(self, text: str, title: Optional[str] = None) -> DiagramIR:
        """Convert enhanced text to DiagramIR.

        Args:
            text: Input text describing a process/flow
            title: Optional diagram title

        Returns:
            DiagramIR representation

        Examples:
            >>> converter = EnhancedTextConverter()
            >>> # Conditional
            >>> diagram = converter.convert("Start -> Check user. If authenticated: Show dashboard, else: Show login")
            >>> # Parallel
            >>> diagram = converter.convert("Start -> [parallel: Process A, Process B] -> End")
        """
        diagram = DiagramIR()
        if title:
            diagram.metadata["title"] = title

        self.node_counter = 0
        self.nodes_created = {}

        # Detect and handle different patterns
        if self._contains_conditional(text):
            self._parse_conditional(text, diagram)
        elif self._contains_parallel(text):
            self._parse_parallel(text, diagram)
        elif self._contains_loop(text):
            self._parse_loop(text, diagram)
        else:
            # Use simple parsing
            self._parse_simple(text, diagram)

        return diagram

    def _contains_conditional(self, text: str) -> bool:
        """Check if text contains conditional logic."""
        return bool(
            re.search(
                r"\b(if|when|unless|whether)\b.*\b(then|else|otherwise)\b",
                text,
                re.IGNORECASE,
            )
        )

    def _contains_parallel(self, text: str) -> bool:
        """Check if text contains parallel flows."""
        return bool(re.search(r"\[parallel:", text, re.IGNORECASE))

    def _contains_loop(self, text: str) -> bool:
        """Check if text contains loops."""
        return bool(re.search(r"\b(while|repeat|loop|until)\b", text, re.IGNORECASE))

    def _parse_conditional(self, text: str, diagram: DiagramIR) -> None:
        """Parse text with conditional branches."""
        # Pattern: "... If condition: action1, else: action2 ..."
        pattern = r"(.+?)\s+[Ii]f\s+(.+?):\s*([^,]+),?\s*else:\s*(.+?)(?:\s*->|\s*\.|$)"
        match = re.search(pattern, text)

        if match:
            before = match.group(1).strip()
            condition = match.group(2).strip()
            true_action = match.group(3).strip()
            false_action = match.group(4).strip()

            # Parse before steps
            if before and before.lower() not in ["start", "begin"]:
                for step in re.split(r"\s*->\s*", before):
                    step = step.strip()
                    if step:
                        node = self._create_node(step)
                        diagram.add_node(node)

            # Create decision node
            decision_node = self._create_node(condition, NodeType.DECISION)
            diagram.add_node(decision_node)

            # Create branches
            true_node = self._create_node(true_action)
            false_node = self._create_node(false_action)
            diagram.add_node(true_node)
            diagram.add_node(false_node)

            # Connect decision to branches
            diagram.add_edge(
                Edge(source=decision_node.id, target=true_node.id, label="Yes")
            )
            diagram.add_edge(
                Edge(source=decision_node.id, target=false_node.id, label="No")
            )

            # Connect previous nodes
            if len(diagram.nodes) > 3:
                prev_node = diagram.nodes[-4]  # Node before decision
                diagram.add_edge(Edge(source=prev_node.id, target=decision_node.id))

    def _parse_parallel(self, text: str, diagram: DiagramIR) -> None:
        """Parse text with parallel flows."""
        # Pattern: "[parallel: A, B, C]"
        pattern = r"\[parallel:\s*([^\]]+)\]"
        match = re.search(pattern, text)

        if match:
            # Get steps before and after parallel
            before = text[: match.start()].strip()
            after = text[match.end() :].strip()
            parallel_steps = [s.strip() for s in match.group(1).split(",")]

            # Parse before
            prev_node = None
            for step in re.split(r"\s*->\s*", before):
                step = step.strip()
                if step:
                    node = self._create_node(step)
                    diagram.add_node(node)
                    if prev_node:
                        diagram.add_edge(Edge(source=prev_node.id, target=node.id))
                    prev_node = node

            # Create parallel nodes
            parallel_nodes = []
            for step in parallel_steps:
                node = self._create_node(step)
                diagram.add_node(node)
                parallel_nodes.append(node)

                # Connect from previous
                if prev_node:
                    diagram.add_edge(Edge(source=prev_node.id, target=node.id))

            # Parse after
            if after:
                after = after.lstrip("->").strip()
                for step in re.split(r"\s*->\s*", after):
                    step = step.strip()
                    if step:
                        node = self._create_node(step)
                        diagram.add_node(node)

                        # Connect all parallel nodes to this
                        for pnode in parallel_nodes:
                            diagram.add_edge(Edge(source=pnode.id, target=node.id))

                        prev_node = node

    def _parse_loop(self, text: str, diagram: DiagramIR) -> None:
        """Parse text with loops."""
        # Pattern: "... while condition: action ..."
        pattern = r"(.+?)\s+(while|repeat|loop)\s+(.+?):\s*(.+?)(?:\s*->|\s*\.|$)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            before = match.group(1).strip()
            loop_type = match.group(2).lower()
            condition = match.group(3).strip()
            action = match.group(4).strip()

            # Parse before steps
            prev_node = None
            if before and before.lower() not in ["start", "begin"]:
                for step in re.split(r"\s*->\s*", before):
                    step = step.strip()
                    if step:
                        node = self._create_node(step)
                        diagram.add_node(node)
                        if prev_node:
                            diagram.add_edge(Edge(source=prev_node.id, target=node.id))
                        prev_node = node

            # Create loop decision
            decision_node = self._create_node(condition, NodeType.DECISION)
            diagram.add_node(decision_node)

            if prev_node:
                diagram.add_edge(Edge(source=prev_node.id, target=decision_node.id))

            # Create loop action
            action_node = self._create_node(action)
            diagram.add_node(action_node)

            # Create loop edges
            diagram.add_edge(
                Edge(source=decision_node.id, target=action_node.id, label="Continue")
            )
            diagram.add_edge(
                Edge(
                    source=action_node.id,
                    target=decision_node.id,
                    edge_type=EdgeType.CONDITIONAL,
                )
            )

    def _parse_simple(self, text: str, diagram: DiagramIR) -> None:
        """Parse simple linear flow."""
        # Split by arrows or line breaks
        steps = []
        parts = re.split(r"\s*->\s*|\s*→\s*|\n|\.(?:\s|$)", text)

        for part in parts:
            part = part.strip()
            if part:
                steps.append(part)

        # Create nodes and edges
        prev_node = None
        for i, step in enumerate(steps):
            node = self._create_node(step, self._infer_type(step, i, len(steps)))
            diagram.add_node(node)

            if prev_node:
                diagram.add_edge(Edge(source=prev_node.id, target=node.id))

            prev_node = node

    def _create_node(
        self, label: str, node_type: Optional[NodeType] = None
    ) -> Node:
        """Create a node with unique ID."""
        # Check if we've already created this node
        if label in self.nodes_created:
            return self.nodes_created[label]

        node_id = f"n{self.node_counter}"
        self.node_counter += 1

        if node_type is None:
            node_type = self._infer_type(label, 0, 1)

        node = Node(id=node_id, label=label, node_type=node_type)
        self.nodes_created[label] = node
        return node

    def _infer_type(self, text: str, index: int, total: int) -> NodeType:
        """Infer node type from text content."""
        text_lower = text.lower()

        # Check for explicit keywords (order matters)
        if any(
            word in text_lower
            for word in ["start", "begin", "initialize", "open", "launch"]
        ):
            return NodeType.START
        elif any(
            word in text_lower
            for word in ["end", "finish", "complete", "close", "done"]
        ):
            return NodeType.END
        elif any(
            word in text_lower
            for word in [
                "if",
                "decide",
                "check",
                "verify",
                "validate",
                "whether",
                "when",
                "?",
            ]
        ):
            return NodeType.DECISION
        elif any(
            word in text_lower for word in ["database", "store", "save", "persist"]
        ):
            return NodeType.DATA
        elif any(
            word in text_lower for word in ["subprocess", "subroutine", "call"]
        ):
            return NodeType.SUBPROCESS

        # Use position as hint
        if index == 0 and total > 1:
            return NodeType.START
        elif index == total - 1 and total > 1:
            return NodeType.END

        return NodeType.PROCESS
