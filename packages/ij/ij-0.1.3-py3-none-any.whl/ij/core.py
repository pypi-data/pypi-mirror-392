"""Core data structures for Idea Junction.

This module provides the intermediate representation (IR) for diagrams,
following the recommendation from research to use AST-like structures
for bidirectional conversion between text, diagrams, and code.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(Enum):
    """Types of nodes in a diagram."""

    PROCESS = "process"
    DECISION = "decision"
    START = "start"
    END = "end"
    DATA = "data"
    SUBPROCESS = "subprocess"
    CUSTOM = "custom"


class EdgeType(Enum):
    """Types of edges connecting nodes."""

    DIRECT = "direct"
    CONDITIONAL = "conditional"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class Node:
    """Represents a node in the diagram IR.

    Attributes:
        id: Unique identifier for the node
        label: Display label/text
        node_type: Type of node (process, decision, etc.)
        metadata: Additional properties for extensibility
    """

    id: str
    label: str
    node_type: NodeType = NodeType.PROCESS
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)


@dataclass
class Edge:
    """Represents an edge in the diagram IR.

    Attributes:
        source: Source node ID
        target: Target node ID
        label: Optional edge label
        edge_type: Type of edge
        metadata: Additional properties for extensibility
    """

    source: str
    target: str
    label: Optional[str] = None
    edge_type: EdgeType = EdgeType.DIRECT
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagramIR:
    """Intermediate Representation for diagrams.

    This serves as the central data structure that can be:
    - Generated from natural language
    - Converted to various diagram formats (Mermaid, PlantUML, D2)
    - Manipulated programmatically
    - Parsed back from diagram syntax

    Attributes:
        nodes: List of nodes in the diagram
        edges: List of edges connecting nodes
        metadata: Diagram-level properties (title, description, etc.)
    """

    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        """Add a node to the diagram."""
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the diagram."""
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def validate(self) -> bool:
        """Validate the diagram structure.

        Returns:
            True if the diagram is valid, False otherwise
        """
        # Check for unique node IDs
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            return False

        # Check that edges reference existing nodes
        for edge in self.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                return False

        return True
