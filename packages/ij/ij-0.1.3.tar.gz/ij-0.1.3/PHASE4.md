# Phase 4: Advanced Diagramming Features

Phase 4 completes the bidirectional diagramming system with advanced features for diagram manipulation, multi-format support, and sequence diagram generation.

## New Features

### 1. Bidirectional D2 Support

Complete bidirectional conversion for D2 (Terrastruct) diagrams.

**D2 Parser (`ij.parsers.D2Parser`)**:
- Parse D2 syntax to DiagramIR
- Support for all node shapes (oval, rectangle, diamond, cylinder)
- Edge types (direct, conditional, bidirectional)
- Direction metadata
- Automatic START/END node inference

**Example**:
```python
from ij import D2Parser, D2Renderer

# Parse D2 to IR
d2_code = """
start: "Begin" {
  shape: oval
}
process: "Process Data" {
  shape: rectangle
}
start -> process
"""

parser = D2Parser()
diagram = parser.parse(d2_code)

# Render back to D2
renderer = D2Renderer()
d2_output = renderer.render(diagram)
```

### 2. Sequence Diagram Generation

Generate Mermaid sequence diagrams for showing interactions and message flows.

**SequenceDiagramRenderer**:
- Render DiagramIR as Mermaid sequence diagrams
- Support for sync (solid arrows) and async (dashed arrows) messages
- Notes and activations support

**InteractionAnalyzer**:
- Analyze Python code to extract interaction patterns
- Parse natural language descriptions
- Automatic participant detection

**Examples**:

**From DiagramIR**:
```python
from ij import DiagramIR, Node, Edge, SequenceDiagramRenderer

diagram = DiagramIR()
diagram.add_node(Node(id="user", label="User"))
diagram.add_node(Node(id="api", label="API"))
diagram.add_edge(Edge(source="user", target="api", label="Request"))

renderer = SequenceDiagramRenderer()
print(renderer.render(diagram))
```

**From Code**:
```python
from ij import InteractionAnalyzer, SequenceDiagramRenderer

code = """
api.authenticate(user)
db.query(user_id)
cache.store(result)
"""

analyzer = InteractionAnalyzer()
diagram = analyzer.analyze_function_calls("app", code)

renderer = SequenceDiagramRenderer()
print(renderer.render(diagram))
```

**From Natural Language**:
```python
text = """
User sends request to API.
API queries Database.
Database returns data to API.
"""

analyzer = InteractionAnalyzer()
diagram = analyzer.from_text_description(text)
```

### 3. Diagram Transformations

Powerful utilities for manipulating and optimizing diagrams.

**DiagramTransforms Class**:

**Simplification**:
```python
from ij import DiagramTransforms

# Remove isolated nodes and duplicate edges
simplified = DiagramTransforms.simplify(diagram, remove_isolated=True)
```

**Filtering**:
```python
# Keep only PROCESS nodes
filtered = DiagramTransforms.filter_by_node_type(
    diagram, [NodeType.PROCESS], keep=True
)

# Custom filtering with predicates
error_nodes = DiagramTransforms.apply_node_filter(
    diagram, lambda n: "error" in n.label.lower()
)
```

**Subgraph Extraction**:
```python
# Extract subgraph starting from a node
subgraph = DiagramTransforms.extract_subgraph(
    diagram, root_node_id="start", max_depth=3
)
```

**Merging Diagrams**:
```python
# Merge multiple diagrams
merged = DiagramTransforms.merge_diagrams(
    [diagram1, diagram2], title="Combined Flow"
)
```

**Cycle Detection**:
```python
# Find all cycles in the diagram
cycles = DiagramTransforms.find_cycles(diagram)
if cycles:
    print(f"Found {len(cycles)} cycle(s)")
```

**Statistics**:
```python
# Get comprehensive diagram statistics
stats = DiagramTransforms.get_statistics(diagram)
print(f"Nodes: {stats['node_count']}")
print(f"Edges: {stats['edge_count']}")
print(f"Has cycles: {stats['has_cycles']}")
print(f"Node types: {stats['node_types']}")
```

**Other Transformations**:
- `reverse_edges()` - Reverse all edge directions
- `merge_sequential_nodes()` - Combine linear sequences

### 4. Multi-Format Workflows

Seamlessly convert between all supported formats.

**Supported Formats**:
- **Mermaid**: GitHub/GitLab native, excellent browser support
- **PlantUML**: Enterprise standard, extensive features
- **D2**: Modern, beautiful diagrams with scripting
- **Graphviz/DOT**: Classic graph visualization, 30+ year foundation

**Example Workflow**:
```python
from ij import (
    MermaidParser,
    D2Renderer,
    PlantUMLRenderer,
    GraphvizRenderer
)

# Start with Mermaid
mermaid_code = "flowchart TD\n  A --> B"
diagram = MermaidParser().parse(mermaid_code)

# Convert to any format
d2_output = D2Renderer().render(diagram)
plantuml_output = PlantUMLRenderer().render(diagram)
dot_output = GraphvizRenderer().render(diagram)
```

## API Reference

### D2Parser

```python
class D2Parser:
    def parse(self, d2_text: str) -> DiagramIR:
        """Parse D2 syntax to DiagramIR."""

    def parse_file(self, filename: str) -> DiagramIR:
        """Parse D2 file to DiagramIR."""
```

### SequenceDiagramRenderer

```python
class SequenceDiagramRenderer:
    def render(self, diagram: DiagramIR) -> str:
        """Render DiagramIR as Mermaid sequence diagram."""

    def render_with_notes(
        self, diagram: DiagramIR, notes: Dict[str, List[str]]
    ) -> str:
        """Render with participant notes."""

    def render_with_activations(
        self, diagram: DiagramIR, activations: List[tuple]
    ) -> str:
        """Render with participant activations."""
```

### InteractionAnalyzer

```python
class InteractionAnalyzer:
    def analyze_function_calls(self, caller: str, code: str) -> DiagramIR:
        """Analyze code to create sequence diagram."""

    def from_text_description(self, text: str) -> DiagramIR:
        """Create sequence diagram from text description."""
```

### DiagramTransforms

```python
class DiagramTransforms:
    @staticmethod
    def simplify(diagram: DiagramIR, remove_isolated: bool = True) -> DiagramIR:
        """Simplify diagram by removing redundant elements."""

    @staticmethod
    def filter_by_node_type(
        diagram: DiagramIR,
        node_types: List[NodeType],
        keep: bool = True
    ) -> DiagramIR:
        """Filter diagram by node types."""

    @staticmethod
    def extract_subgraph(
        diagram: DiagramIR,
        root_node_id: str,
        max_depth: Optional[int] = None
    ) -> DiagramIR:
        """Extract subgraph from root node."""

    @staticmethod
    def merge_diagrams(
        diagrams: List[DiagramIR],
        title: Optional[str] = None
    ) -> DiagramIR:
        """Merge multiple diagrams."""

    @staticmethod
    def find_cycles(diagram: DiagramIR) -> List[List[str]]:
        """Find all cycles in the diagram."""

    @staticmethod
    def get_statistics(diagram: DiagramIR) -> dict:
        """Get comprehensive diagram statistics."""

    @staticmethod
    def apply_node_filter(
        diagram: DiagramIR,
        predicate: Callable[[Node], bool]
    ) -> DiagramIR:
        """Filter nodes using custom predicate."""

    @staticmethod
    def reverse_edges(diagram: DiagramIR) -> DiagramIR:
        """Reverse all edge directions."""

    @staticmethod
    def merge_sequential_nodes(
        diagram: DiagramIR,
        separator: str = " → "
    ) -> DiagramIR:
        """Merge sequential nodes into single nodes."""
```

## Examples

See `examples/phase4_features.py` for comprehensive examples including:

1. **Bidirectional D2 Conversion** - Parse and render D2 diagrams
2. **Sequence Diagrams** - Generate interaction diagrams
3. **Code to Sequence** - Analyze Python code for interactions
4. **Text to Sequence** - Parse natural language descriptions
5. **Diagram Transformations** - Simplify and optimize diagrams
6. **Filtering & Extraction** - Extract relevant subgraphs
7. **Merging Diagrams** - Combine multiple flows
8. **Cycle Detection** - Find circular dependencies
9. **Multi-Format Workflows** - Convert between formats
10. **Custom Filtering** - Advanced filtering with predicates

## Testing

Phase 4 includes 51 new tests:
- **16 tests** for D2 parser
- **15 tests** for sequence diagrams
- **20 tests** for diagram transformations

Run tests:
```bash
pytest tests/test_d2_parser.py -v
pytest tests/test_sequence.py -v
pytest tests/test_transforms.py -v
```

Total test count: **124 tests** (122 passing, 2 optional AI tests)

## Use Cases

### 1. Documentation Generation
- Parse existing D2/Mermaid diagrams
- Transform and optimize
- Export to multiple formats for different audiences

### 2. Code Documentation
- Analyze Python code for interactions
- Generate sequence diagrams automatically
- Visualize system architecture

### 3. Diagram Optimization
- Simplify complex diagrams
- Remove redundant elements
- Extract relevant portions

### 4. System Analysis
- Detect circular dependencies
- Calculate complexity metrics
- Filter by component type

### 5. Multi-Team Collaboration
- Convert between team-preferred formats
- Merge partial diagrams from different teams
- Maintain consistency across formats

## Performance

All transformations operate on DiagramIR in-memory:
- **Parsing**: O(n) where n is input size
- **Simplification**: O(n + m) where m is edges
- **Filtering**: O(n)
- **Subgraph extraction**: O(n + m) with BFS
- **Cycle detection**: O(n + m) with DFS
- **Statistics**: O(n + m)

## Limitations

1. **D2 Parser**: Supports basic D2 syntax; advanced styling not fully supported
2. **Sequence Diagrams**: No support for alt/opt/loop blocks yet
3. **Merge Sequential**: Basic implementation, may not handle all edge cases
4. **Text Parsing**: Simple regex-based, may miss complex sentence structures

## Future Enhancements

Potential Phase 5 features:
- Interactive diagram editing
- Real-time collaboration
- Advanced layout algorithms
- Diagram diff and merge
- Version control integration
- Web-based editor
- Diagram animation
- Export to image formats (PNG, SVG)

## Migration from Phase 3

Phase 4 is fully backward compatible with Phase 3. No breaking changes.

New imports:
```python
from ij import (
    # New in Phase 4
    D2Parser,
    SequenceDiagramRenderer,
    InteractionAnalyzer,
    DiagramTransforms,

    # Existing from previous phases
    DiagramIR,
    MermaidParser,
    MermaidRenderer,
    # ... etc
)
```

## Contributing

To add new transformations:

1. Add method to `DiagramTransforms` class in `ij/transforms.py`
2. Add tests in `tests/test_transforms.py`
3. Add example in `examples/phase4_features.py`
4. Update this documentation

To add new diagram types:

1. Create parser in `ij/parsers/`
2. Create renderer in `ij/renderers/`
3. Add tests
4. Update examples

## License

MIT License - see LICENSE file for details
