## Phase 3 Features - AI/LLM Integration & Code Analysis

Phase 3 adds AI-powered diagram generation and Python code reverse engineering capabilities, completing the research-recommended feature set for modern diagramming systems.

## New Features

### 1. AI/LLM-Powered Diagram Generation

Convert natural language descriptions to diagrams using OpenAI's API. Achieves **10-20x faster** diagram creation as documented in research.

```python
from ij.converters import LLMConverter

converter = LLMConverter(model="gpt-4o-mini", temperature=0.3)

diagram = converter.convert("""
A user logs into the system. If authentication succeeds, they see
the dashboard. Otherwise, they see an error message.
""")
```

**Features:**
- Natural language understanding
- Automatic node type inference
- Clean, well-structured output
- Iterative refinement support
- Uses cheap, effective models (gpt-4o-mini: ~$0.00015 per diagram)

**Installation:**
```bash
pip install ij[ai]  # Installs openai package
export OPENAI_API_KEY=your-key-here
```

### 2. Iterative Diagram Refinement

Refine diagrams conversationally using AI feedback:

```python
from ij.renderers import MermaidRenderer

# Generate initial diagram
diagram = converter.convert("User login process")
mermaid = MermaidRenderer().render(diagram)

# Refine with feedback
refined = converter.refine(
    diagram,
    "Add a password reset option if login fails",
    mermaid
)
```

This enables:
- Conversational diagram improvement
- Adding missing details
- Restructuring flows
- Fixing errors

### 3. Python Code Analysis

Reverse engineer diagrams from Python code using AST parsing.

#### Function Flowcharts

```python
from ij.analyzers import PythonCodeAnalyzer

code = """
def process_order(order):
    if order.is_valid():
        if order.in_stock():
            charge_customer(order)
            ship_order(order)
        else:
            backorder(order)
    else:
        reject_order(order)
"""

analyzer = PythonCodeAnalyzer()
diagram = analyzer.analyze_function(code)
```

Generates a flowchart showing:
- Control flow (if/else, while, for)
- Function calls
- Return statements
- Decision points

#### Call Graphs

```python
code = """
def main():
    config = load_config()
    db = setup_database(config)
    run_app(db)

def load_config():
    return read_file("config.json")
"""

diagram = analyzer.analyze_module_calls(code)
```

Shows function dependencies and call relationships.

#### Class Diagrams

```python
code = """
class UserService(BaseService):
    def __init__(self):
        self.users = []

    def add_user(self, user):
        self.users.append(user)

    def get_user(self, id):
        return find_by_id(self.users, id)
"""

diagram = analyzer.analyze_class(code, class_name="UserService")
```

Shows:
- Class structure
- Methods and attributes
- Inheritance relationships

### 4. Hybrid Workflows

Combine code analysis with AI enhancement:

```python
# Step 1: Analyze existing code
analyzer = PythonCodeAnalyzer()
diagram = analyzer.analyze_function(code)

# Step 2: Enhance with AI
converter = LLMConverter()
enhanced = converter.refine(
    diagram,
    "Add error handling for edge cases",
    MermaidRenderer().render(diagram)
)
```

## AI Model Configuration

### Recommended Models

**gpt-4o-mini** (default):
- Cost: ~$0.00015 per diagram
- Speed: ~1-2 seconds
- Quality: Excellent for flowcharts
- Best for: Most use cases

**gpt-4o**:
- Cost: ~$0.0015 per diagram (10x more)
- Speed: ~2-3 seconds
- Quality: Slightly better for complex diagrams
- Best for: Production-critical diagrams

### Configuration Options

```python
converter = LLMConverter(
    api_key="your-key",      # Or use OPENAI_API_KEY env var
    model="gpt-4o-mini",     # Model choice
    temperature=0.3          # Lower = more deterministic
)
```

**Temperature guide:**
- 0.1-0.3: Consistent, predictable output (recommended)
- 0.4-0.7: More creative variations
- 0.8-1.0: Maximum creativity (less consistent)

## Cost Estimation

Based on typical usage with gpt-4o-mini:

- Simple diagram (3-5 nodes): $0.00010 - $0.00015
- Medium diagram (6-10 nodes): $0.00015 - $0.00020
- Complex diagram (11+ nodes): $0.00020 - $0.00030
- Refinement iteration: $0.00015 - $0.00025

**Monthly estimates:**
- Light use (10 diagrams/day): ~$1-2/month
- Medium use (50 diagrams/day): ~$5-10/month
- Heavy use (200 diagrams/day): ~$20-40/month

## Python Code Analysis Capabilities

### Supported Constructs

✅ **Control Flow:**
- if/elif/else statements
- while loops
- for loops
- Nested conditions

✅ **Functions:**
- Function definitions
- Function calls
- Return statements
- Parameters

✅ **Classes:**
- Class definitions
- Methods
- Attributes
- Inheritance

### Limitations

⚠️ **Not Yet Supported:**
- Try/except blocks (shown as generic statements)
- Async/await
- Decorators (not visualized)
- Complex comprehensions
- Multi-file analysis

## Testing

### Mock Tests (Always Run)

Tests use mocks by default - no API key needed:

```bash
pytest tests/test_llm_converter.py -v -k "not real_api"
pytest tests/test_python_analyzer.py -v
```

**71 total tests** including:
- 12 Python analyzer tests
- 7 LLM converter mock tests
- 2 optional real API tests (require `OPENAI_API_KEY`)

### Real API Tests (Optional)

Optional integration tests with real OpenAI API:

```bash
export OPENAI_API_KEY=your-key-here
pytest tests/test_llm_converter.py -v  # Runs all tests including real API
```

These tests:
- Only run if `OPENAI_API_KEY` is set
- Use gpt-4o-mini (cheap)
- Cost ~$0.0003 per test run
- Validate end-to-end functionality

## Complete Examples

### Example 1: Code → Diagram → Multiple Formats

```python
from ij.analyzers import PythonCodeAnalyzer
from ij.renderers import MermaidRenderer, PlantUMLRenderer, D2Renderer

code = """
def validate(data):
    if not data:
        return False
    if check_format(data):
        save(data)
        return True
    return False
"""

analyzer = PythonCodeAnalyzer()
diagram = analyzer.analyze_function(code)

# Export to multiple formats
mermaid = MermaidRenderer().render(diagram)
plantuml = PlantUMLRenderer().render(diagram)
d2 = D2Renderer().render(diagram)
```

### Example 2: Natural Language → AI → Diagram

```python
from ij.converters import LLMConverter
from ij.renderers import MermaidRenderer

converter = LLMConverter()

diagram = converter.convert("""
Create a diagram for an online shopping checkout process. The user
adds items to cart, proceeds to checkout, enters shipping info,
chooses payment method, and confirms the order. Include error handling.
""", title="E-commerce Checkout")

mermaid = MermaidRenderer().render(diagram)
print(mermaid)
```

### Example 3: Few-Shot Learning

Provide examples to guide AI output:

```python
examples = [
    {
        "description": "Simple login",
        "mermaid": """flowchart TD
            A([Start]) --> B[Enter credentials]
            B --> C{Valid?}
            C -->|Yes| D([Success])
            C -->|No| E([Error])"""
    }
]

diagram = converter.convert_with_examples(
    "User registration process",
    examples=examples
)
```

### Example 4: Hybrid Workflow

```python
# 1. Analyze existing code
analyzer = PythonCodeAnalyzer()
code_diagram = analyzer.analyze_function(existing_code)

# 2. Get initial Mermaid
initial = MermaidRenderer().render(code_diagram)

# 3. Use AI to add missing pieces
converter = LLMConverter()
enhanced = converter.refine(
    code_diagram,
    "Add input validation and error handling steps",
    initial
)

# 4. Export final version
final = MermaidRenderer().render(enhanced)
```

## Running Examples

```bash
# Phase 3 examples (AI examples skip if no API key)
python examples/phase3_features.py

# Individual examples
python -c "from examples.phase3_features import example1_python_code_analysis; example1_python_code_analysis()"
```

## CI/CD Integration

The OpenAI API key is configured in CI for integration testing:

```yaml
# .github/workflows/ci.yml
- name: Run Tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: pytest
```

Tests automatically:
- Run mock tests (always)
- Run real API tests (if key available)
- Skip gracefully (if key missing)

## Best Practices

### AI-Powered Generation

**DO:**
- Use clear, specific descriptions
- Include context about the domain
- Start with simpler diagrams and refine
- Use temperature 0.1-0.3 for consistency
- Cache and reuse diagrams when possible

**DON'T:**
- Use vague or ambiguous language
- Expect perfect output on first try
- Generate diagrams for well-known patterns (use templates instead)
- Use high temperature for production diagrams

### Code Analysis

**DO:**
- Analyze one function/class at a time
- Use meaningful variable names in code
- Document complex logic
- Review generated diagrams for accuracy

**DON'T:**
- Analyze overly complex functions (refactor first)
- Expect diagram to show implementation details
- Rely solely on generated diagrams (human review needed)

## Future Enhancements (Phase 4+)

Planned for future releases:
- [ ] Java code analysis
- [ ] JavaScript/TypeScript analysis
- [ ] Sequence diagram generation from traces
- [ ] PlantUML parser (completing bidirectional support)
- [ ] Local LLM support (Ollama, etc.)
- [ ] Diagram optimization suggestions
- [ ] Multi-language code analysis
- [ ] Visual diff for diagram changes

## Troubleshooting

### ImportError: No module named 'openai'

Install AI dependencies:
```bash
pip install ij[ai]
```

### ValueError: OpenAI API key required

Set your API key:
```bash
export OPENAI_API_KEY=your-key-here
```

Or pass directly:
```python
converter = LLMConverter(api_key="your-key")
```

### API Rate Limits

If you hit rate limits:
- Add delays between requests
- Use caching for repeated diagrams
- Consider batch processing
- Upgrade OpenAI tier if needed

### Quality Issues

If AI output is poor quality:
- Lower temperature (0.1-0.2)
- Provide more specific descriptions
- Use few-shot examples
- Try gpt-4o instead of gpt-4o-mini
- Break complex diagrams into smaller parts

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Phase 1 Features](README.md#features)
- [Phase 2 Features](PHASE2.md)

---

**Phase 3 Status:** ✅ Complete

**Test Coverage:** 71 tests (100% pass rate)

**Key Metrics:**
- AI generation: 10-20x faster than manual
- Code analysis: Instant diagram generation
- Cost: ~$0.00015 per AI-generated diagram
- Quality: Production-ready with human review
