"""Graph operations using NetworkX.

Provides graph manipulation, analysis, and transformation capabilities
following the research recommendation to use NetworkX as the foundation
for graph-based operations.
"""

import networkx as nx
from typing import Dict, List, Optional, Set
from .core import DiagramIR, Edge, Node


class GraphOperations:
    """Graph manipulation and analysis using NetworkX."""

    @staticmethod
    def to_networkx(diagram: DiagramIR) -> nx.DiGraph:
        """Convert DiagramIR to NetworkX directed graph.

        Args:
            diagram: DiagramIR to convert

        Returns:
            NetworkX DiGraph
        """
        G = nx.DiGraph()

        # Add nodes with attributes
        for node in diagram.nodes:
            G.add_node(
                node.id,
                label=node.label,
                node_type=node.node_type.value,
                **node.metadata,
            )

        # Add edges with attributes
        for edge in diagram.edges:
            G.add_edge(
                edge.source,
                edge.target,
                label=edge.label,
                edge_type=edge.edge_type.value,
                **edge.metadata,
            )

        return G

    @staticmethod
    def from_networkx(G: nx.DiGraph) -> DiagramIR:
        """Convert NetworkX graph to DiagramIR.

        Args:
            G: NetworkX directed graph

        Returns:
            DiagramIR representation
        """
        from .core import NodeType, EdgeType

        diagram = DiagramIR()

        # Convert nodes
        for node_id, attrs in G.nodes(data=True):
            node_type = NodeType(attrs.get("node_type", "process"))
            label = attrs.get("label", str(node_id))

            # Filter out known attributes
            metadata = {
                k: v for k, v in attrs.items() if k not in ["label", "node_type"]
            }

            node = Node(id=node_id, label=label, node_type=node_type, metadata=metadata)
            diagram.add_node(node)

        # Convert edges
        for source, target, attrs in G.edges(data=True):
            edge_type = EdgeType(attrs.get("edge_type", "direct"))
            label = attrs.get("label")

            # Filter out known attributes
            metadata = {
                k: v for k, v in attrs.items() if k not in ["label", "edge_type"]
            }

            edge = Edge(
                source=source,
                target=target,
                label=label,
                edge_type=edge_type,
                metadata=metadata,
            )
            diagram.add_edge(edge)

        return diagram

    @staticmethod
    def find_paths(diagram: DiagramIR, source: str, target: str) -> List[List[str]]:
        """Find all paths between two nodes.

        Args:
            diagram: DiagramIR to analyze
            source: Source node ID
            target: Target node ID

        Returns:
            List of paths (each path is a list of node IDs)
        """
        G = GraphOperations.to_networkx(diagram)
        try:
            paths = list(nx.all_simple_paths(G, source, target))
            return paths
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    @staticmethod
    def find_cycles(diagram: DiagramIR) -> List[List[str]]:
        """Find all cycles in the diagram.

        Args:
            diagram: DiagramIR to analyze

        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        G = GraphOperations.to_networkx(diagram)
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    @staticmethod
    def topological_sort(diagram: DiagramIR) -> Optional[List[str]]:
        """Get topological ordering of nodes (for DAGs).

        Args:
            diagram: DiagramIR to sort

        Returns:
            List of node IDs in topological order, or None if graph has cycles
        """
        G = GraphOperations.to_networkx(diagram)
        try:
            return list(nx.topological_sort(G))
        except (nx.NetworkXError, nx.NetworkXUnfeasible):
            # Graph has cycles or other issues
            return None

    @staticmethod
    def find_critical_nodes(diagram: DiagramIR) -> Set[str]:
        """Find nodes whose removal would disconnect the graph.

        Args:
            diagram: DiagramIR to analyze

        Returns:
            Set of critical node IDs
        """
        G = GraphOperations.to_networkx(diagram)
        return set(nx.articulation_points(G.to_undirected()))

    @staticmethod
    def simplify_diagram(diagram: DiagramIR, remove_redundant: bool = True) -> DiagramIR:
        """Simplify diagram by removing redundant edges and nodes.

        Args:
            diagram: DiagramIR to simplify
            remove_redundant: If True, remove transitive edges

        Returns:
            Simplified DiagramIR
        """
        G = GraphOperations.to_networkx(diagram)

        if remove_redundant:
            # Compute transitive reduction to remove redundant edges
            G_reduced = nx.transitive_reduction(G)
            # Copy node and edge attributes
            for node in G.nodes():
                for attr, value in G.nodes[node].items():
                    G_reduced.nodes[node][attr] = value
            for u, v in G_reduced.edges():
                if G.has_edge(u, v):
                    for attr, value in G.edges[u, v].items():
                        G_reduced.edges[u, v][attr] = value
            G = G_reduced

        return GraphOperations.from_networkx(G)
