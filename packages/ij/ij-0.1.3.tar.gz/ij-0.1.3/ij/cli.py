"""Command-line interface for Idea Junction."""

import argparse
import sys
from pathlib import Path

from . import SimpleTextConverter, MermaidRenderer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Idea Junction - Convert ideas to diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert text to Mermaid diagram
  ij "Start -> Process data -> Make decision -> End"

  # Save to file
  ij "Start -> Process -> End" -o diagram.mmd

  # Read from file
  ij -f input.txt -o output.mmd

  # Specify direction
  ij "Step 1 -> Step 2 -> Step 3" -d LR
        """,
    )

    parser.add_argument(
        "text", nargs="?", help="Text description of the process/flow (or use -f)"
    )
    parser.add_argument("-f", "--file", help="Read text from file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "-d",
        "--direction",
        default="TD",
        choices=["TD", "LR", "BT", "RL"],
        help="Diagram direction (TD=top-down, LR=left-right, etc.)",
    )
    parser.add_argument("-t", "--title", help="Diagram title")

    args = parser.parse_args()

    # Get input text
    if args.file:
        try:
            text = Path(args.file).read_text()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    # Convert text to diagram
    try:
        converter = SimpleTextConverter()
        diagram = converter.convert(text, title=args.title)

        renderer = MermaidRenderer(direction=args.direction)
        mermaid_output = renderer.render(diagram)

        # Output
        if args.output:
            Path(args.output).write_text(mermaid_output)
            print(f"Diagram saved to {args.output}")
        else:
            print(mermaid_output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
