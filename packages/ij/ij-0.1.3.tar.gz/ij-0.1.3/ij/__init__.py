"""Idea Junction - Connect vague ideas and evolve them to fully functional systems.

A bidirectional diagramming system that enables seamless movement between
natural language, visual diagrams, and code.
"""

from .analyzers import PythonCodeAnalyzer
from .core import DiagramIR, Edge, EdgeType, Node, NodeType
from .converters import EnhancedTextConverter, SimpleTextConverter
from .graph_ops import GraphOperations
from .parsers import D2Parser, MermaidParser
from .transforms import DiagramTransforms
from .renderers import (
    D2Renderer,
    GraphvizRenderer,
    InteractionAnalyzer,
    MermaidRenderer,
    PlantUMLRenderer,
    SequenceDiagramRenderer,
)

# LLMConverter is optional (requires openai package)
try:
    from .converters import LLMConverter
    _has_llm = True
except ImportError:
    _has_llm = False

__version__ = "0.1.1"

__all__ = [
    "DiagramIR",
    "Node",
    "Edge",
    "NodeType",
    "EdgeType",
    "SimpleTextConverter",
    "EnhancedTextConverter",
    "MermaidRenderer",
    "PlantUMLRenderer",
    "D2Renderer",
    "GraphvizRenderer",
    "SequenceDiagramRenderer",
    "InteractionAnalyzer",
    "MermaidParser",
    "D2Parser",
    "GraphOperations",
    "PythonCodeAnalyzer",
    "DiagramTransforms",
]

if _has_llm:
    __all__.append("LLMConverter")


def text_to_mermaid(text: str, title: str = None, direction: str = "TD") -> str:
    """Convert text description to Mermaid diagram (convenience function).

    Args:
        text: Text description of the process/flow
        title: Optional diagram title
        direction: Flow direction (TD, LR, etc.)

    Returns:
        Mermaid syntax string

    Example:
        >>> mermaid = text_to_mermaid("Start -> Process data -> End")
        >>> print(mermaid)
        flowchart TD
            n0([Start])
            n1[Process data]
            n2([End])
            n0 --> n1
            n1 --> n2
    """
    converter = SimpleTextConverter()
    diagram = converter.convert(text, title=title)
    renderer = MermaidRenderer(direction=direction)
    return renderer.render(diagram)
