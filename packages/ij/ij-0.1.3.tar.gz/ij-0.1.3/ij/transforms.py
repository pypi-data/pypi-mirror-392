"""Diagram transformation and optimization utilities.

Provides operations for manipulating, simplifying, and optimizing diagrams.
"""

from typing import Callable, List, Optional, Set

from .core import DiagramIR, Edge, EdgeType, Node, NodeType


class DiagramTransforms:
    """Transform and optimize diagram structures."""

    @staticmethod
    def simplify(diagram: DiagramIR, remove_isolated: bool = True) -> DiagramIR:
        """Simplify diagram by removing redundant nodes and edges.

        Args:
            diagram: DiagramIR to simplify
            remove_isolated: Remove nodes with no connections

        Returns:
            Simplified DiagramIR

        Example:
            >>> from ij import DiagramIR, Node, Edge
            >>> diagram = DiagramIR()
            >>> diagram.add_node(Node(id="a", label="A"))
            >>> diagram.add_node(Node(id="isolated", label="Isolated"))
            >>> diagram.add_edge(Edge(source="a", target="b"))
            >>> simplified = DiagramTransforms.simplify(diagram)
            >>> len(simplified.nodes)  # isolated node removed
            2
        """
        new_diagram = DiagramIR(metadata=diagram.metadata.copy())

        # Find connected nodes
        connected_nodes = set()
        for edge in diagram.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)

        # Add nodes
        for node in diagram.nodes:
            if remove_isolated:
                # Only add if connected or is START/END
                if node.id in connected_nodes or node.node_type in [
                    NodeType.START,
                    NodeType.END,
                ]:
                    new_diagram.add_node(node)
            else:
                new_diagram.add_node(node)

        # Remove duplicate edges
        added_edges = set()
        for edge in diagram.edges:
            edge_sig = (edge.source, edge.target, edge.label, edge.edge_type)
            if edge_sig not in added_edges:
                new_diagram.add_edge(edge)
                added_edges.add(edge_sig)

        return new_diagram

    @staticmethod
    def merge_sequential_nodes(diagram: DiagramIR, separator: str = " → ") -> DiagramIR:
        """Merge sequential nodes into single nodes.

        Combines nodes that form a linear sequence with no branching.

        Args:
            diagram: DiagramIR to transform
            separator: String to join labels

        Returns:
            DiagramIR with merged nodes
        """
        from collections import defaultdict

        # Build adjacency lists
        outgoing = defaultdict(list)
        incoming = defaultdict(list)

        for edge in diagram.edges:
            outgoing[edge.source].append(edge.target)
            incoming[edge.target].append(edge.source)

        # Find mergeable chains: nodes with exactly 1 incoming and 1 outgoing edge
        merged = set()
        new_diagram = DiagramIR(metadata=diagram.metadata.copy())

        node_map = {node.id: node for node in diagram.nodes}

        for node in diagram.nodes:
            if node.id in merged:
                continue

            # Start a chain if this node has 1 outgoing edge
            if len(outgoing.get(node.id, [])) == 1:
                chain = [node.id]
                current = outgoing[node.id][0]

                # Extend chain while next node has 1 in and 1 out
                while (
                    current in node_map
                    and len(incoming.get(current, [])) == 1
                    and len(outgoing.get(current, [])) == 1
                    and current not in merged
                ):
                    chain.append(current)
                    merged.add(current)
                    current = outgoing[current][0]

                # If we have a chain of at least 2 nodes, merge them
                if len(chain) >= 2:
                    # Create merged node
                    labels = [node_map[nid].label for nid in chain]
                    merged_label = separator.join(labels)
                    merged_node = Node(
                        id=chain[0],
                        label=merged_label,
                        node_type=node_map[chain[0]].node_type,
                    )
                    new_diagram.add_node(merged_node)

                    # Mark all in chain as merged
                    for nid in chain:
                        merged.add(nid)

                    # Add edge to next node after chain
                    if current in node_map:
                        new_diagram.add_edge(Edge(source=chain[0], target=current))
                else:
                    # Single node, add as-is
                    if node.id not in merged:
                        new_diagram.add_node(node)
            else:
                # Node not part of chain, add as-is
                if node.id not in merged:
                    new_diagram.add_node(node)

        # Add edges that don't involve merged nodes
        for edge in diagram.edges:
            if edge.source not in merged and edge.target not in merged:
                new_diagram.add_edge(edge)

        return new_diagram

    @staticmethod
    def filter_by_node_type(
        diagram: DiagramIR, node_types: List[NodeType], keep: bool = True
    ) -> DiagramIR:
        """Filter diagram by node types.

        Args:
            diagram: DiagramIR to filter
            node_types: List of NodeTypes to filter
            keep: If True, keep only these types; if False, remove these types

        Returns:
            Filtered DiagramIR

        Example:
            >>> # Keep only PROCESS nodes
            >>> filtered = DiagramTransforms.filter_by_node_type(
            ...     diagram, [NodeType.PROCESS], keep=True
            ... )
        """
        new_diagram = DiagramIR(metadata=diagram.metadata.copy())

        # Filter nodes
        kept_node_ids = set()
        for node in diagram.nodes:
            should_keep = (node.node_type in node_types) == keep
            if should_keep:
                new_diagram.add_node(node)
                kept_node_ids.add(node.id)

        # Add edges between kept nodes
        for edge in diagram.edges:
            if edge.source in kept_node_ids and edge.target in kept_node_ids:
                new_diagram.add_edge(edge)

        return new_diagram

    @staticmethod
    def extract_subgraph(
        diagram: DiagramIR, root_node_id: str, max_depth: Optional[int] = None
    ) -> DiagramIR:
        """Extract subgraph starting from a root node.

        Args:
            diagram: Source DiagramIR
            root_node_id: ID of root node
            max_depth: Maximum depth to traverse (None = unlimited)

        Returns:
            DiagramIR containing subgraph

        Example:
            >>> # Extract subgraph from node 'start' with depth 2
            >>> subgraph = DiagramTransforms.extract_subgraph(diagram, "start", max_depth=2)
        """
        from collections import deque

        # Find root node
        root_node = None
        for node in diagram.nodes:
            if node.id == root_node_id:
                root_node = node
                break

        if root_node is None:
            raise ValueError(f"Root node '{root_node_id}' not found")

        new_diagram = DiagramIR(metadata=diagram.metadata.copy())

        # BFS to find reachable nodes
        visited = set()
        queue = deque([(root_node_id, 0)])
        visited.add(root_node_id)

        # Build edge map
        edge_map = {}
        for edge in diagram.edges:
            if edge.source not in edge_map:
                edge_map[edge.source] = []
            edge_map[edge.source].append(edge)

        # Traverse
        while queue:
            node_id, depth = queue.popleft()

            # Add node
            for node in diagram.nodes:
                if node.id == node_id:
                    new_diagram.add_node(node)
                    break

            # Check depth limit
            if max_depth is not None and depth >= max_depth:
                continue

            # Add outgoing edges and visit neighbors
            if node_id in edge_map:
                for edge in edge_map[node_id]:
                    new_diagram.add_edge(edge)
                    if edge.target not in visited:
                        visited.add(edge.target)
                        queue.append((edge.target, depth + 1))

        return new_diagram

    @staticmethod
    def merge_diagrams(diagrams: List[DiagramIR], title: Optional[str] = None) -> DiagramIR:
        """Merge multiple diagrams into one.

        Args:
            diagrams: List of DiagramIR to merge
            title: Optional title for merged diagram

        Returns:
            Merged DiagramIR

        Example:
            >>> diagram1 = DiagramIR()
            >>> diagram2 = DiagramIR()
            >>> merged = DiagramTransforms.merge_diagrams([diagram1, diagram2])
        """
        metadata = {"merged": True}
        if title:
            metadata["title"] = title

        merged = DiagramIR(metadata=metadata)

        # Track node IDs to avoid duplicates
        added_node_ids = set()

        for diagram in diagrams:
            # Add nodes
            for node in diagram.nodes:
                if node.id not in added_node_ids:
                    merged.add_node(node)
                    added_node_ids.add(node.id)

            # Add edges
            for edge in diagram.edges:
                merged.add_edge(edge)

        return merged

    @staticmethod
    def reverse_edges(diagram: DiagramIR) -> DiagramIR:
        """Reverse all edge directions in the diagram.

        Args:
            diagram: DiagramIR to reverse

        Returns:
            DiagramIR with reversed edges

        Example:
            >>> reversed_diagram = DiagramTransforms.reverse_edges(diagram)
        """
        new_diagram = DiagramIR(metadata=diagram.metadata.copy())

        # Add all nodes
        for node in diagram.nodes:
            new_diagram.add_node(node)

        # Reverse edges
        for edge in diagram.edges:
            reversed_edge = Edge(
                source=edge.target,
                target=edge.source,
                label=edge.label,
                edge_type=edge.edge_type,
            )
            new_diagram.add_edge(reversed_edge)

        return new_diagram

    @staticmethod
    def apply_node_filter(
        diagram: DiagramIR, predicate: Callable[[Node], bool]
    ) -> DiagramIR:
        """Filter nodes using a custom predicate function.

        Args:
            diagram: DiagramIR to filter
            predicate: Function that returns True for nodes to keep

        Returns:
            Filtered DiagramIR

        Example:
            >>> # Keep only nodes with labels containing "error"
            >>> filtered = DiagramTransforms.apply_node_filter(
            ...     diagram, lambda n: "error" in n.label.lower()
            ... )
        """
        new_diagram = DiagramIR(metadata=diagram.metadata.copy())

        # Filter nodes
        kept_node_ids = set()
        for node in diagram.nodes:
            if predicate(node):
                new_diagram.add_node(node)
                kept_node_ids.add(node.id)

        # Add edges between kept nodes
        for edge in diagram.edges:
            if edge.source in kept_node_ids and edge.target in kept_node_ids:
                new_diagram.add_edge(edge)

        return new_diagram

    @staticmethod
    def find_cycles(diagram: DiagramIR) -> List[List[str]]:
        """Find all cycles in the diagram.

        Args:
            diagram: DiagramIR to analyze

        Returns:
            List of cycles, where each cycle is a list of node IDs

        Example:
            >>> cycles = DiagramTransforms.find_cycles(diagram)
            >>> if cycles:
            ...     print(f"Found {len(cycles)} cycles")
        """
        from collections import defaultdict

        # Build adjacency list
        graph = defaultdict(list)
        for edge in diagram.edges:
            graph[edge.source].append(edge.target)

        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    cycles.append(cycle.copy())

            path.pop()
            rec_stack.remove(node)

        # Check all nodes
        for node in diagram.nodes:
            if node.id not in visited:
                dfs(node.id)

        return cycles

    @staticmethod
    def get_statistics(diagram: DiagramIR) -> dict:
        """Get statistics about the diagram.

        Args:
            diagram: DiagramIR to analyze

        Returns:
            Dictionary containing diagram statistics

        Example:
            >>> stats = DiagramTransforms.get_statistics(diagram)
            >>> print(f"Nodes: {stats['node_count']}, Edges: {stats['edge_count']}")
        """
        from collections import Counter

        node_type_counts = Counter(node.node_type for node in diagram.nodes)
        edge_type_counts = Counter(edge.edge_type for edge in diagram.edges)

        # Find nodes by degree
        incoming_degree = Counter()
        outgoing_degree = Counter()

        for edge in diagram.edges:
            outgoing_degree[edge.source] += 1
            incoming_degree[edge.target] += 1

        return {
            "node_count": len(diagram.nodes),
            "edge_count": len(diagram.edges),
            "node_types": dict(node_type_counts),
            "edge_types": dict(edge_type_counts),
            "max_incoming_degree": max(incoming_degree.values()) if incoming_degree else 0,
            "max_outgoing_degree": max(outgoing_degree.values()) if outgoing_degree else 0,
            "isolated_nodes": len(
                [
                    n
                    for n in diagram.nodes
                    if incoming_degree[n.id] == 0 and outgoing_degree[n.id] == 0
                ]
            ),
            "has_cycles": len(DiagramTransforms.find_cycles(diagram)) > 0,
        }
