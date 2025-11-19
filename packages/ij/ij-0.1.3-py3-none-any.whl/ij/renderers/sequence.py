"""Sequence diagram renderer for Mermaid format.

Renders DiagramIR as Mermaid sequence diagrams for showing interactions
and message flows between participants over time.
"""

import ast
import re
from typing import Dict, List, Set

from ..core import DiagramIR, Edge, EdgeType, Node


class SequenceDiagramRenderer:
    """Render DiagramIR as Mermaid sequence diagram.

    Maps DiagramIR concepts to sequence diagrams:
    - Nodes -> Participants
    - Edges -> Messages between participants
    - Edge labels -> Message content
    - EdgeType.DIRECT -> Solid arrows (synchronous)
    - EdgeType.CONDITIONAL -> Dashed arrows (asynchronous/return)
    - EdgeType.BIDIRECTIONAL -> Bidirectional arrows
    """

    def __init__(self):
        """Initialize renderer."""
        pass

    def render(self, diagram: DiagramIR) -> str:
        """Render DiagramIR as Mermaid sequence diagram.

        Args:
            diagram: DiagramIR to render

        Returns:
            Mermaid sequence diagram syntax

        Example:
            >>> from ij import DiagramIR, Node, Edge
            >>> diagram = DiagramIR()
            >>> diagram.add_node(Node(id="user", label="User"))
            >>> diagram.add_node(Node(id="api", label="API"))
            >>> diagram.add_edge(Edge(source="user", target="api", label="Request"))
            >>> renderer = SequenceDiagramRenderer()
            >>> print(renderer.render(diagram))
            sequenceDiagram
                participant user as User
                participant api as API
                user->>api: Request
        """
        if not diagram.validate():
            raise ValueError("Invalid diagram structure")

        lines = ["sequenceDiagram"]

        # Add title if present
        if "title" in diagram.metadata:
            lines.append(f"    title {diagram.metadata['title']}")

        # Collect all participants (nodes)
        participants = self._collect_participants(diagram)

        # Declare participants
        for node in diagram.nodes:
            if node.id in participants:
                # Use label if different from id, otherwise just id
                if node.label and node.label != node.id:
                    lines.append(f"    participant {node.id} as {node.label}")
                else:
                    lines.append(f"    participant {node.id}")

        # Add messages (edges)
        for edge in diagram.edges:
            arrow = self._get_arrow_type(edge.edge_type)
            message = edge.label if edge.label else ""
            lines.append(f"    {edge.source}{arrow}{edge.target}: {message}")

        return "\n".join(lines)

    def _collect_participants(self, diagram: DiagramIR) -> Set[str]:
        """Collect all participant IDs from nodes and edges.

        Args:
            diagram: DiagramIR to analyze

        Returns:
            Set of participant IDs
        """
        participants = set()

        # Add all nodes
        for node in diagram.nodes:
            participants.add(node.id)

        # Add any participants referenced in edges that aren't in nodes
        for edge in diagram.edges:
            participants.add(edge.source)
            participants.add(edge.target)

        return participants

    def _get_arrow_type(self, edge_type: EdgeType) -> str:
        """Get Mermaid arrow type for edge type.

        Args:
            edge_type: EdgeType to convert

        Returns:
            Mermaid arrow syntax
        """
        arrow_map = {
            EdgeType.DIRECT: "->>",  # Solid arrow (synchronous)
            EdgeType.CONDITIONAL: "-->>",  # Dashed arrow (asynchronous/return)
            EdgeType.BIDIRECTIONAL: "<<->>",  # Bidirectional
        }
        return arrow_map.get(edge_type, "->>")

    def render_with_notes(
        self, diagram: DiagramIR, notes: Dict[str, List[str]]
    ) -> str:
        """Render sequence diagram with notes.

        Args:
            diagram: DiagramIR to render
            notes: Dict mapping participant IDs to list of notes

        Returns:
            Mermaid sequence diagram with notes

        Example:
            >>> notes = {"user": ["Note about user"], "api": ["API note"]}
            >>> renderer.render_with_notes(diagram, notes)
        """
        lines = self.render(diagram).split("\n")

        # Insert notes after participant declarations
        insert_index = len([l for l in lines if l.strip().startswith("participant")])
        if "title" in diagram.metadata:
            insert_index += 1  # Account for title line
        insert_index += 1  # Account for sequenceDiagram line

        note_lines = []
        for participant_id, participant_notes in notes.items():
            for note in participant_notes:
                note_lines.append(f"    Note over {participant_id}: {note}")

        # Insert notes
        lines = lines[:insert_index] + note_lines + lines[insert_index:]

        return "\n".join(lines)

    def render_with_activations(
        self, diagram: DiagramIR, activations: List[tuple]
    ) -> str:
        """Render sequence diagram with participant activations.

        Args:
            diagram: DiagramIR to render
            activations: List of (participant_id, "activate"/"deactivate") tuples

        Returns:
            Mermaid sequence diagram with activations

        Example:
            >>> activations = [("api", "activate"), ("api", "deactivate")]
            >>> renderer.render_with_activations(diagram, activations)
        """
        base = self.render(diagram)
        lines = base.split("\n")

        # Add activations at the end
        for participant_id, action in activations:
            if action == "activate":
                lines.append(f"    activate {participant_id}")
            elif action == "deactivate":
                lines.append(f"    deactivate {participant_id}")

        return "\n".join(lines)


class InteractionAnalyzer:
    """Analyze code or text to identify interaction patterns for sequence diagrams."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def analyze_function_calls(
        self, caller: str, code: str
    ) -> DiagramIR:
        """Analyze function calls to create a sequence diagram.

        Args:
            caller: The calling function/component name
            code: Python code to analyze

        Returns:
            DiagramIR representing the call sequence

        Example:
            >>> analyzer = InteractionAnalyzer()
            >>> code = '''
            ... api.authenticate(user)
            ... db.query(user_id)
            ... cache.store(result)
            ... '''
            >>> diagram = analyzer.analyze_function_calls("client", code)
        """
        from ..core import Edge, Node

        diagram = DiagramIR(metadata={"type": "sequence"})

        # Add caller as first participant
        diagram.add_node(Node(id=caller, label=caller))

        # Parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If it's not valid Python, return empty diagram
            return diagram

        # Find all function calls of the form object.method()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # This is a method call like obj.method()
                    obj_name = self._get_object_name(node.func.value)
                    method_name = node.func.attr

                    # Add participant if not exists
                    if not any(n.id == obj_name for n in diagram.nodes):
                        diagram.add_node(Node(id=obj_name, label=obj_name))

                    # Add message
                    message = f"{method_name}()"
                    diagram.add_edge(
                        Edge(source=caller, target=obj_name, label=message)
                    )

        return diagram

    def _get_object_name(self, node: ast.expr) -> str:
        """Extract object name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_object_name(node.value) + "." + node.attr
        else:
            return "unknown"

    def from_text_description(self, text: str) -> DiagramIR:
        """Create sequence diagram from text description.

        Args:
            text: Natural language description of interactions

        Returns:
            DiagramIR representing the interaction sequence

        Example:
            >>> analyzer = InteractionAnalyzer()
            >>> text = "User sends request to API. API queries Database. Database returns data to API. API responds to User."
            >>> diagram = analyzer.from_text_description(text)
        """
        from ..core import Edge, Node

        diagram = DiagramIR(metadata={"type": "sequence"})

        # Simple pattern matching for "A sends/queries/calls/requests B"
        # Pattern: "Subject verb Object" or "Subject verb message to Object"
        patterns = [
            r"(\w+)\s+(?:sends?|queries?|calls?|requests?|asks?)\s+(?:to\s+)?(\w+)(?:\s*:\s*(.+?)(?:\.|$))?",
            r"(\w+)\s+(?:responds?|returns?|replies?)\s+(?:to\s+)?(\w+)(?:\s*:\s*(.+?)(?:\.|$))?",
        ]

        sentences = text.split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            for pattern in patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    message = match.group(3) if len(match.groups()) > 2 and match.group(3) else ""

                    # Add participants if not exists
                    if not any(n.id == source for n in diagram.nodes):
                        diagram.add_node(Node(id=source, label=source))
                    if not any(n.id == target for n in diagram.nodes):
                        diagram.add_node(Node(id=target, label=target))

                    # Add message
                    diagram.add_edge(
                        Edge(source=source, target=target, label=message.strip())
                    )
                    break

        return diagram
