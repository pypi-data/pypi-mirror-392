"""Tests for sequence diagram renderer and interaction analyzer."""

import pytest

from ij import DiagramIR, Edge, EdgeType, InteractionAnalyzer, Node, SequenceDiagramRenderer


def test_sequence_renderer_simple():
    """Test rendering a simple sequence diagram."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="user", label="User"))
    diagram.add_node(Node(id="api", label="API"))
    diagram.add_edge(Edge(source="user", target="api", label="Request"))

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    assert "sequenceDiagram" in result
    assert "participant user as User" in result
    assert "participant api as API" in result
    assert "user->>api: Request" in result


def test_sequence_renderer_with_title():
    """Test rendering sequence diagram with title."""
    diagram = DiagramIR(metadata={"title": "User Login Flow"})
    diagram.add_node(Node(id="user", label="User"))
    diagram.add_node(Node(id="auth", label="Auth Service"))
    diagram.add_edge(Edge(source="user", target="auth", label="Login"))

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    assert "title User Login Flow" in result


def test_sequence_renderer_arrow_types():
    """Test different arrow types in sequence diagrams."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))

    # Direct/synchronous
    diagram.add_edge(
        Edge(source="a", target="b", label="sync", edge_type=EdgeType.DIRECT)
    )

    # Conditional/asynchronous
    diagram.add_edge(
        Edge(source="b", target="a", label="async", edge_type=EdgeType.CONDITIONAL)
    )

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    # Direct should use solid arrow ->>
    assert "a->>b: sync" in result
    # Conditional should use dashed arrow -->>
    assert "b-->>a: async" in result


def test_sequence_renderer_multiple_messages():
    """Test rendering multiple messages between participants."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="client", label="Client"))
    diagram.add_node(Node(id="server", label="Server"))
    diagram.add_node(Node(id="db", label="Database"))

    diagram.add_edge(Edge(source="client", target="server", label="GET /data"))
    diagram.add_edge(Edge(source="server", target="db", label="SELECT *"))
    diagram.add_edge(
        Edge(source="db", target="server", label="Results", edge_type=EdgeType.CONDITIONAL)
    )
    diagram.add_edge(
        Edge(source="server", target="client", label="200 OK", edge_type=EdgeType.CONDITIONAL)
    )

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    assert "client->>server: GET /data" in result
    assert "server->>db: SELECT *" in result
    assert "db-->>server: Results" in result
    assert "server-->>client: 200 OK" in result


def test_sequence_renderer_with_notes():
    """Test rendering sequence diagram with notes."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="user", label="User"))
    diagram.add_node(Node(id="api", label="API"))
    diagram.add_edge(Edge(source="user", target="api", label="Request"))

    renderer = SequenceDiagramRenderer()
    notes = {
        "user": ["This is the end user"],
        "api": ["REST API endpoint"],
    }
    result = renderer.render_with_notes(diagram, notes)

    assert "Note over user: This is the end user" in result
    assert "Note over api: REST API endpoint" in result


def test_sequence_renderer_with_activations():
    """Test rendering sequence diagram with activations."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="client", label="Client"))
    diagram.add_node(Node(id="server", label="Server"))
    diagram.add_edge(Edge(source="client", target="server", label="Request"))

    renderer = SequenceDiagramRenderer()
    activations = [
        ("server", "activate"),
        ("server", "deactivate"),
    ]
    result = renderer.render_with_activations(diagram, activations)

    assert "activate server" in result
    assert "deactivate server" in result


def test_sequence_renderer_no_label():
    """Test rendering messages without labels."""
    diagram = DiagramIR()
    diagram.add_node(Node(id="a", label="A"))
    diagram.add_node(Node(id="b", label="B"))
    diagram.add_edge(Edge(source="a", target="b"))  # No label

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    assert "a->>b:" in result


def test_interaction_analyzer_function_calls():
    """Test analyzing function calls to create sequence diagram."""
    code = """
api.authenticate(user)
db.query(user_id)
cache.store(result)
"""
    analyzer = InteractionAnalyzer()
    diagram = analyzer.analyze_function_calls("client", code)

    # Should have client, api, db, cache as participants
    assert len(diagram.nodes) == 4
    participant_ids = {node.id for node in diagram.nodes}
    assert "client" in participant_ids
    assert "api" in participant_ids
    assert "db" in participant_ids
    assert "cache" in participant_ids

    # Should have 3 messages
    assert len(diagram.edges) == 3
    assert any(
        e.source == "client" and e.target == "api" and "authenticate" in e.label
        for e in diagram.edges
    )
    assert any(
        e.source == "client" and e.target == "db" and "query" in e.label
        for e in diagram.edges
    )
    assert any(
        e.source == "client" and e.target == "cache" and "store" in e.label
        for e in diagram.edges
    )


def test_interaction_analyzer_invalid_code():
    """Test handling invalid Python code."""
    code = "this is not valid python code @#$%"
    analyzer = InteractionAnalyzer()
    diagram = analyzer.analyze_function_calls("client", code)

    # Should return diagram with just the caller
    assert len(diagram.nodes) == 1
    assert diagram.nodes[0].id == "client"
    assert len(diagram.edges) == 0


def test_interaction_analyzer_from_text():
    """Test creating sequence diagram from text description."""
    text = """
    User sends request to API.
    API queries Database.
    Database returns data to API.
    API responds to User.
    """
    analyzer = InteractionAnalyzer()
    diagram = analyzer.from_text_description(text)

    # Should identify User, API, Database as participants
    participant_ids = {node.id for node in diagram.nodes}
    assert "User" in participant_ids
    assert "API" in participant_ids
    assert "Database" in participant_ids

    # Should have multiple interactions
    assert len(diagram.edges) >= 3


def test_interaction_analyzer_text_variations():
    """Test different text patterns for interactions."""
    texts = [
        "Alice calls Bob",
        "Client requests Server",
        "User asks API",
        "Service queries Database",
    ]

    analyzer = InteractionAnalyzer()

    for text in texts:
        diagram = analyzer.from_text_description(text)
        # Each should create at least one interaction
        assert len(diagram.nodes) >= 2
        assert len(diagram.edges) >= 1


def test_interaction_analyzer_empty_text():
    """Test handling empty text input."""
    analyzer = InteractionAnalyzer()
    diagram = analyzer.from_text_description("")

    assert len(diagram.nodes) == 0
    assert len(diagram.edges) == 0


def test_sequence_integration():
    """Test full integration: analyze code -> render sequence diagram."""
    code = """
user.login(credentials)
auth.validate(credentials)
db.check_password(username)
"""
    analyzer = InteractionAnalyzer()
    diagram = analyzer.analyze_function_calls("app", code)

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    # Should produce valid Mermaid sequence diagram
    assert "sequenceDiagram" in result
    assert "participant app" in result
    assert "participant user" in result
    assert "participant auth" in result
    assert "participant db" in result


def test_sequence_text_to_diagram():
    """Test text description to sequence diagram."""
    text = """
    Browser sends HTTP request to WebServer.
    WebServer calls AppServer.
    AppServer queries Database.
    Database returns results to AppServer.
    AppServer responds to WebServer.
    WebServer sends response to Browser.
    """

    analyzer = InteractionAnalyzer()
    diagram = analyzer.from_text_description(text)

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    assert "sequenceDiagram" in result
    assert "Browser" in result
    assert "WebServer" in result
    assert "AppServer" in result
    assert "Database" in result


def test_sequence_complex_scenario():
    """Test complex multi-participant sequence diagram."""
    diagram = DiagramIR(metadata={"title": "E-commerce Checkout"})

    # Add participants
    participants = ["User", "Frontend", "API", "PaymentGateway", "Database"]
    for p in participants:
        diagram.add_node(Node(id=p, label=p))

    # Add interactions
    diagram.add_edge(Edge(source="User", target="Frontend", label="Click Checkout"))
    diagram.add_edge(Edge(source="Frontend", target="API", label="POST /checkout"))
    diagram.add_edge(Edge(source="API", target="Database", label="Validate cart"))
    diagram.add_edge(
        Edge(source="Database", target="API", label="OK", edge_type=EdgeType.CONDITIONAL)
    )
    diagram.add_edge(Edge(source="API", target="PaymentGateway", label="Process payment"))
    diagram.add_edge(
        Edge(
            source="PaymentGateway",
            target="API",
            label="Success",
            edge_type=EdgeType.CONDITIONAL,
        )
    )
    diagram.add_edge(Edge(source="API", target="Database", label="Save order"))
    diagram.add_edge(
        Edge(
            source="API",
            target="Frontend",
            label="200 OK",
            edge_type=EdgeType.CONDITIONAL,
        )
    )
    diagram.add_edge(
        Edge(
            source="Frontend",
            target="User",
            label="Show confirmation",
            edge_type=EdgeType.CONDITIONAL,
        )
    )

    renderer = SequenceDiagramRenderer()
    result = renderer.render(diagram)

    assert "title E-commerce Checkout" in result
    assert len(diagram.edges) == 9
    assert "User->>Frontend" in result
    assert "Frontend->>API" in result
    assert "API->>PaymentGateway" in result
