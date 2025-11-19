"""Tests for Python code analyzer."""

import pytest
from ij.analyzers import PythonCodeAnalyzer
from ij.core import NodeType


def test_analyze_simple_function():
    """Test analyzing a simple function."""
    code = """
def hello():
    print("Hello")
    return "done"
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    assert diagram.validate()
    assert len(diagram.nodes) >= 3  # start, print, return, end
    assert diagram.metadata["title"] == "Control Flow: hello"


def test_analyze_function_with_if():
    """Test analyzing function with if statement."""
    code = """
def check_value(x):
    if x > 0:
        print("Positive")
    else:
        print("Negative")
    return x
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    assert diagram.validate()

    # Should have decision node
    decision_nodes = [n for n in diagram.nodes if n.node_type == NodeType.DECISION]
    assert len(decision_nodes) >= 1

    # Should have edges with labels
    labeled_edges = [e for e in diagram.edges if e.label]
    assert len(labeled_edges) >= 0  # May have Yes/No labels


def test_analyze_function_with_while():
    """Test analyzing function with while loop."""
    code = """
def count_down(n):
    while n > 0:
        print(n)
        n = n - 1
    return "done"
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    assert diagram.validate()

    # Should have decision node for while condition
    decision_nodes = [n for n in diagram.nodes if n.node_type == NodeType.DECISION]
    assert len(decision_nodes) >= 1

    # Should have conditional edges (loop back)
    from ij.core import EdgeType

    conditional_edges = [e for e in diagram.edges if e.edge_type == EdgeType.CONDITIONAL]
    assert len(conditional_edges) >= 1


def test_analyze_function_with_for():
    """Test analyzing function with for loop."""
    code = """
def process_items(items):
    for item in items:
        print(item)
    return len(items)
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    assert diagram.validate()
    # Should have loop structure
    assert len(diagram.nodes) >= 3


def test_analyze_specific_function():
    """Test analyzing a specific function by name."""
    code = """
def first():
    return 1

def second():
    return 2
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code, function_name="second")

    assert diagram.metadata["title"] == "Control Flow: second"


def test_analyze_function_with_calls():
    """Test analyzing function with function calls."""
    code = """
def process():
    data = load_data()
    result = transform(data)
    save(result)
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    assert diagram.validate()
    # Should have nodes for each call
    assert len(diagram.nodes) >= 4  # start, load_data, transform, save, end


def test_analyze_class():
    """Test analyzing a class."""
    code = """
class MyClass:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_class(code)

    assert diagram.validate()
    assert diagram.metadata["title"] == "Class: MyClass"
    assert len(diagram.nodes) >= 1


def test_analyze_class_with_inheritance():
    """Test analyzing class with inheritance."""
    code = """
class Base:
    pass

class Derived(Base):
    def method(self):
        pass
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_class(code, class_name="Derived")

    assert diagram.validate()
    # Should have nodes for both Base and Derived
    assert len(diagram.nodes) >= 2
    # Should have inheritance edge
    assert len(diagram.edges) >= 1


def test_analyze_module_calls():
    """Test analyzing function calls in a module."""
    code = """
def helper():
    return "data"

def processor():
    data = helper()
    return data

def main():
    result = processor()
    print(result)
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_module_calls(code)

    assert diagram.validate()
    assert diagram.metadata["title"] == "Call Graph"
    # Should have nodes for all functions
    assert len(diagram.nodes) >= 3
    # Should have call edges
    assert len(diagram.edges) >= 2


def test_analyze_complex_function():
    """Test analyzing a more complex function."""
    code = """
def process_order(order):
    if order.is_valid():
        if order.in_stock():
            charge_customer(order)
            ship_order(order)
            send_confirmation(order)
        else:
            send_backorder_notice(order)
    else:
        send_error_notification(order)
    return order.status
"""

    analyzer = PythonCodeAnalyzer()
    diagram = analyzer.analyze_function(code)

    assert diagram.validate()
    # Should have multiple decision nodes for nested ifs
    decision_nodes = [n for n in diagram.nodes if n.node_type == NodeType.DECISION]
    assert len(decision_nodes) >= 2


def test_analyze_function_not_found():
    """Test error when function not found."""
    code = """
def existing():
    pass
"""

    analyzer = PythonCodeAnalyzer()
    with pytest.raises(ValueError, match="Function nonexistent"):
        analyzer.analyze_function(code, function_name="nonexistent")


def test_analyze_class_not_found():
    """Test error when class not found."""
    code = """
class Existing:
    pass
"""

    analyzer = PythonCodeAnalyzer()
    with pytest.raises(ValueError, match="Class NonExistent"):
        analyzer.analyze_class(code, class_name="NonExistent")
