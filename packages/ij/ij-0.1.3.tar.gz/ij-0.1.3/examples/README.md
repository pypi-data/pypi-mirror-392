# Idea Junction Examples

This directory contains examples demonstrating various features of Idea Junction.

## Running the Examples

```bash
# Install the package first
pip install -e .

# Run the basic usage examples
python examples/basic_usage.py

# Or run individual functions
python -c "from examples.basic_usage import example1_simple_conversion; example1_simple_conversion()"
```

## Examples Overview

### basic_usage.py

Demonstrates the core functionality:

1. **Simple text-to-diagram conversion** - Quick conversion from text to Mermaid
2. **Manual diagram creation** - Building diagrams programmatically
3. **Graph analysis** - Finding paths and analyzing diagram structure
4. **Different directions** - TD, LR, BT, RL layouts
5. **Natural language** - Converting ideas to diagrams
6. **Saving to file** - Exporting diagrams

## Viewing the Diagrams

The generated Mermaid diagrams can be viewed in several ways:

1. **GitHub/GitLab** - Paste in markdown files (native support)
2. **Mermaid Live Editor** - https://mermaid.live/
3. **VS Code** - Use the Mermaid extension
4. **Command line** - Use `mmdc` (Mermaid CLI)

Example: Viewing in Mermaid Live Editor:
1. Copy the generated Mermaid code
2. Go to https://mermaid.live/
3. Paste the code
4. Export as PNG/SVG if needed
