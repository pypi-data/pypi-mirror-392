"""Python code analyzer for reverse engineering diagrams.

Analyzes Python code to generate flowcharts, call graphs, and class diagrams
following research recommendations for code-to-diagram generation.
"""

import ast
from typing import Dict, List, Optional, Set

from ..core import DiagramIR, Edge, EdgeType, Node, NodeType


class PythonCodeAnalyzer:
    """Analyze Python code to generate diagrams.

    Supports:
    - Function call graphs
    - Control flow diagrams
    - Class relationship diagrams
    """

    def __init__(self):
        """Initialize analyzer."""
        self.node_counter = 0

    def analyze_function(
        self, code: str, function_name: Optional[str] = None
    ) -> DiagramIR:
        """Analyze a Python function to create a flowchart.

        Args:
            code: Python source code
            function_name: Specific function to analyze (None = first function)

        Returns:
            DiagramIR representation of the function's control flow

        Example:
            >>> code = '''
            ... def process_order(order):
            ...     if order.is_valid():
            ...         save_to_database(order)
            ...         send_confirmation(order)
            ...     else:
            ...         send_error_notification(order)
            ... '''
            >>> analyzer = PythonCodeAnalyzer()
            >>> diagram = analyzer.analyze_function(code)
        """
        tree = ast.parse(code)

        # Find the target function
        func_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if function_name is None or node.name == function_name:
                    func_def = node
                    break

        if func_def is None:
            raise ValueError(
                f"Function {function_name or 'not found'} in provided code"
            )

        diagram = DiagramIR(
            metadata={"title": f"Control Flow: {func_def.name}", "type": "function"}
        )

        # Create start node
        start_node = self._create_node(f"Start {func_def.name}", NodeType.START)
        diagram.add_node(start_node)

        # Analyze function body
        last_node = start_node
        for stmt in func_def.body:
            last_node = self._analyze_statement(stmt, last_node, diagram)

        # Create end node
        end_node = self._create_node(f"End {func_def.name}", NodeType.END)
        diagram.add_node(end_node)
        if last_node:
            diagram.add_edge(Edge(source=last_node.id, target=end_node.id))

        return diagram

    def analyze_class(self, code: str, class_name: Optional[str] = None) -> DiagramIR:
        """Analyze a Python class to create a class diagram.

        Args:
            code: Python source code
            class_name: Specific class to analyze (None = first class)

        Returns:
            DiagramIR representation of the class structure
        """
        tree = ast.parse(code)

        # Find the target class
        class_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if class_name is None or node.name == class_name:
                    class_def = node
                    break

        if class_def is None:
            raise ValueError(f"Class {class_name or 'not found'} in provided code")

        diagram = DiagramIR(
            metadata={"title": f"Class: {class_def.name}", "type": "class"}
        )

        # Class node
        methods = []
        attributes = []

        for item in class_def.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)

        class_label = f"{class_def.name}\\n"
        if attributes:
            class_label += f"Attributes: {', '.join(attributes)}\\n"
        if methods:
            class_label += f"Methods: {', '.join(methods[:5])}"
            if len(methods) > 5:
                class_label += "..."

        class_node = self._create_node(class_label, NodeType.PROCESS)
        diagram.add_node(class_node)

        # Add inheritance relationships
        for base in class_def.bases:
            if isinstance(base, ast.Name):
                base_node = self._create_node(base.id, NodeType.PROCESS)
                diagram.add_node(base_node)
                diagram.add_edge(
                    Edge(
                        source=base_node.id,
                        target=class_node.id,
                        label="inherits",
                    )
                )

        return diagram

    def analyze_module_calls(self, code: str) -> DiagramIR:
        """Analyze function calls in a module to create a call graph.

        Args:
            code: Python source code

        Returns:
            DiagramIR representation of function call relationships
        """
        tree = ast.parse(code)

        diagram = DiagramIR(metadata={"title": "Call Graph", "type": "calls"})

        # Extract all function definitions
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = node

        # Analyze calls in each function
        for func_name, func_def in functions.items():
            caller_node = self._get_or_create_function_node(
                func_name, diagram
            )

            # Find all function calls
            for node in ast.walk(func_def):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        callee_name = node.func.id  # Use .id for ast.Name
                        callee_node = self._get_or_create_function_node(
                            callee_name, diagram
                        )
                        # Add edge if not already present
                        edge_exists = any(
                            e.source == caller_node.id and e.target == callee_node.id
                            for e in diagram.edges
                        )
                        if not edge_exists:
                            diagram.add_edge(
                                Edge(source=caller_node.id, target=callee_node.id)
                            )

        return diagram

    def _analyze_statement(
        self, stmt: ast.stmt, prev_node: Node, diagram: DiagramIR
    ) -> Node:
        """Analyze a single statement and add to diagram.

        Returns the last node created.
        """
        if isinstance(stmt, ast.If):
            return self._analyze_if(stmt, prev_node, diagram)
        elif isinstance(stmt, ast.While):
            return self._analyze_while(stmt, prev_node, diagram)
        elif isinstance(stmt, ast.For):
            return self._analyze_for(stmt, prev_node, diagram)
        elif isinstance(stmt, ast.Return):
            return self._analyze_return(stmt, prev_node, diagram)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            return self._analyze_call(stmt.value, prev_node, diagram)
        else:
            # Generic statement
            node = self._create_node(
                self._stmt_to_string(stmt), NodeType.PROCESS
            )
            diagram.add_node(node)
            diagram.add_edge(Edge(source=prev_node.id, target=node.id))
            return node

    def _analyze_if(self, stmt: ast.If, prev_node: Node, diagram: DiagramIR) -> Node:
        """Analyze an if statement."""
        # Decision node
        condition = self._expr_to_string(stmt.test)
        decision_node = self._create_node(condition, NodeType.DECISION)
        diagram.add_node(decision_node)
        diagram.add_edge(Edge(source=prev_node.id, target=decision_node.id))

        # True branch
        last_true = decision_node
        for body_stmt in stmt.body:
            last_true = self._analyze_statement(body_stmt, last_true, diagram)

        # Update edge to decision to have "Yes" label
        if last_true != decision_node:
            # Find and update the first edge from decision
            for edge in diagram.edges:
                if edge.source == decision_node.id and edge.target == last_true.id:
                    edge.label = "Yes"
                    break

        # False branch
        last_false = decision_node
        if stmt.orelse:
            for else_stmt in stmt.orelse:
                last_false = self._analyze_statement(else_stmt, last_false, diagram)
            # Update edge to have "No" label
            if last_false != decision_node:
                for edge in diagram.edges:
                    if edge.source == decision_node.id and edge.target == last_false.id:
                        edge.label = "No"
                        break

        # For simplicity, return the last node from true branch
        # In a real implementation, you might want to merge branches
        return last_true if last_true != decision_node else last_false

    def _analyze_while(self, stmt: ast.While, prev_node: Node, diagram: DiagramIR) -> Node:
        """Analyze a while loop."""
        condition = self._expr_to_string(stmt.test)
        decision_node = self._create_node(condition, NodeType.DECISION)
        diagram.add_node(decision_node)
        diagram.add_edge(Edge(source=prev_node.id, target=decision_node.id))

        # Loop body
        last_body = decision_node
        for body_stmt in stmt.body:
            last_body = self._analyze_statement(body_stmt, last_body, diagram)

        # Loop back
        diagram.add_edge(
            Edge(
                source=last_body.id,
                target=decision_node.id,
                edge_type=EdgeType.CONDITIONAL,
                label="Continue",
            )
        )

        return decision_node

    def _analyze_for(self, stmt: ast.For, prev_node: Node, diagram: DiagramIR) -> Node:
        """Analyze a for loop."""
        target = self._expr_to_string(stmt.target)
        iter_expr = self._expr_to_string(stmt.iter)
        loop_label = f"For {target} in {iter_expr}"

        loop_node = self._create_node(loop_label, NodeType.DECISION)
        diagram.add_node(loop_node)
        diagram.add_edge(Edge(source=prev_node.id, target=loop_node.id))

        # Loop body
        last_body = loop_node
        for body_stmt in stmt.body:
            last_body = self._analyze_statement(body_stmt, last_body, diagram)

        # Loop back
        diagram.add_edge(
            Edge(
                source=last_body.id,
                target=loop_node.id,
                edge_type=EdgeType.CONDITIONAL,
            )
        )

        return loop_node

    def _analyze_return(self, stmt: ast.Return, prev_node: Node, diagram: DiagramIR) -> Node:
        """Analyze a return statement."""
        if stmt.value:
            label = f"Return {self._expr_to_string(stmt.value)}"
        else:
            label = "Return"

        node = self._create_node(label, NodeType.PROCESS)
        diagram.add_node(node)
        diagram.add_edge(Edge(source=prev_node.id, target=node.id))
        return node

    def _analyze_call(self, call: ast.Call, prev_node: Node, diagram: DiagramIR) -> Node:
        """Analyze a function call."""
        func_name = self._expr_to_string(call.func)
        args = [self._expr_to_string(arg) for arg in call.args]
        label = f"{func_name}({', '.join(args) if args else ''})"

        node = self._create_node(label, NodeType.PROCESS)
        diagram.add_node(node)
        diagram.add_edge(Edge(source=prev_node.id, target=node.id))
        return node

    def _create_node(self, label: str, node_type: NodeType = NodeType.PROCESS) -> Node:
        """Create a node with unique ID."""
        node_id = f"n{self.node_counter}"
        self.node_counter += 1
        return Node(id=node_id, label=label, node_type=node_type)

    def _get_or_create_function_node(self, func_name: str, diagram: DiagramIR) -> Node:
        """Get existing function node or create new one."""
        # Check if node exists
        for node in diagram.nodes:
            if node.label == func_name:
                return node

        # Create new node
        node = self._create_node(func_name, NodeType.SUBPROCESS)
        diagram.add_node(node)
        return node

    def _expr_to_string(self, expr: ast.expr) -> str:
        """Convert AST expression to string."""
        try:
            return ast.unparse(expr)
        except AttributeError:
            # Python < 3.9 fallback
            if isinstance(expr, ast.Name):
                return expr.id
            elif isinstance(expr, ast.Constant):
                return str(expr.value)
            elif isinstance(expr, ast.Attribute):
                return f"{self._expr_to_string(expr.value)}.{expr.attr}"
            elif isinstance(expr, ast.Call):
                func = self._expr_to_string(expr.func)
                return f"{func}(...)"
            else:
                return "<expr>"

    def _stmt_to_string(self, stmt: ast.stmt) -> str:
        """Convert AST statement to string."""
        try:
            return ast.unparse(stmt)[:50]
        except AttributeError:
            return f"{stmt.__class__.__name__}"
