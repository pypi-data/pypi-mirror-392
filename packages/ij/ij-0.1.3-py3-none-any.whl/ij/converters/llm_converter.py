"""AI/LLM-based text to diagram converter.

Uses OpenAI API for intelligent natural language understanding and
diagram generation. Follows research recommendations for AI-powered
diagram generation (10-20x faster initial drafts).
"""

import json
import os
from typing import Dict, List, Optional

try:
    import openai
except ImportError:
    openai = None

from ..core import DiagramIR, Edge, EdgeType, Node, NodeType
from ..parsers import MermaidParser


class LLMConverter:
    """AI-powered text to diagram converter using LLMs.

    Uses OpenAI API with carefully crafted prompts to generate diagrams
    from natural language descriptions. Supports iterative refinement.
    """

    SYSTEM_PROMPT = """You are an expert at converting natural language descriptions into Mermaid flowchart diagrams.

When given a description, create a clear, well-structured Mermaid flowchart that accurately represents the process or system described.

Guidelines:
1. Use appropriate node types:
   - ([...]) for start/end nodes
   - [...] for process steps
   - {...} for decisions
   - [(...)] for data/storage
2. Use meaningful node IDs (e.g., 'start', 'check_user', 'save_data')
3. Add clear labels to decision edges (e.g., |Yes|, |No|)
4. Keep the diagram focused and avoid unnecessary complexity
5. Use flowchart TD (top-down) or LR (left-right) as appropriate

Output ONLY the Mermaid code, no explanations or markdown code blocks."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
    ):
        """Initialize LLM converter.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (gpt-4o-mini is cheap and effective)
            temperature: Sampling temperature (lower = more deterministic)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        if openai is None:
            raise ImportError(
                "OpenAI library required for LLM conversion. "
                "Install with: pip install openai"
            )

        self.client = openai.OpenAI(api_key=self.api_key)

    def convert(
        self, text: str, title: Optional[str] = None, direction: str = "TD"
    ) -> DiagramIR:
        """Convert natural language to DiagramIR using LLM.

        Args:
            text: Natural language description
            title: Optional diagram title
            direction: Diagram direction (TD, LR, etc.)

        Returns:
            DiagramIR representation

        Example:
            >>> converter = LLMConverter()
            >>> diagram = converter.convert(
            ...     "A user logs into the system. If authentication succeeds, "
            ...     "they see the dashboard. Otherwise, they see an error message."
            ... )
        """
        # Build user prompt
        user_prompt = f"Create a Mermaid flowchart for:\n\n{text}"
        if title:
            user_prompt += f"\n\nTitle: {title}"
        if direction != "TD":
            user_prompt += f"\n\nUse direction: {direction}"

        # Call OpenAI API
        mermaid_code = self._generate_mermaid(user_prompt)

        # Parse the generated Mermaid to DiagramIR
        parser = MermaidParser()
        diagram = parser.parse(mermaid_code)

        # Add title if provided
        if title and "title" not in diagram.metadata:
            diagram.metadata["title"] = title

        return diagram

    def refine(
        self, diagram: DiagramIR, feedback: str, current_mermaid: str
    ) -> DiagramIR:
        """Refine an existing diagram based on feedback.

        Args:
            diagram: Current diagram
            feedback: User feedback/instructions
            current_mermaid: Current Mermaid representation

        Returns:
            Refined DiagramIR

        Example:
            >>> diagram = converter.convert("User login process")
            >>> from ij.renderers import MermaidRenderer
            >>> mermaid = MermaidRenderer().render(diagram)
            >>> refined = converter.refine(
            ...     diagram,
            ...     "Add a step for password reset if login fails",
            ...     mermaid
            ... )
        """
        user_prompt = f"""Current diagram:
```mermaid
{current_mermaid}
```

Please modify it based on this feedback:
{feedback}

Output the updated Mermaid code."""

        # Generate refined version
        mermaid_code = self._generate_mermaid(user_prompt)

        # Parse back to DiagramIR
        parser = MermaidParser()
        refined_diagram = parser.parse(mermaid_code)

        # Preserve metadata
        refined_diagram.metadata.update(diagram.metadata)

        return refined_diagram

    def _generate_mermaid(self, user_prompt: str) -> str:
        """Call OpenAI API to generate Mermaid code.

        Args:
            user_prompt: User's prompt

        Returns:
            Generated Mermaid code
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=1000,
        )

        mermaid_code = response.choices[0].message.content.strip()

        # Clean up if wrapped in code blocks
        if mermaid_code.startswith("```"):
            lines = mermaid_code.split("\n")
            # Remove first line (```mermaid or ```) and last line (```)
            mermaid_code = "\n".join(lines[1:-1])

        return mermaid_code

    def convert_with_examples(
        self, text: str, examples: List[Dict[str, str]], title: Optional[str] = None
    ) -> DiagramIR:
        """Convert with few-shot examples for better quality.

        Args:
            text: Natural language description
            examples: List of {"description": "...", "mermaid": "..."} examples
            title: Optional diagram title

        Returns:
            DiagramIR representation
        """
        # Build few-shot prompt
        examples_text = "\n\n".join(
            [
                f"Example {i+1}:\nDescription: {ex['description']}\n\nMermaid:\n{ex['mermaid']}"
                for i, ex in enumerate(examples)
            ]
        )

        user_prompt = f"""{examples_text}

Now create a diagram for:
{text}"""

        if title:
            user_prompt += f"\n\nTitle: {title}"

        mermaid_code = self._generate_mermaid(user_prompt)
        parser = MermaidParser()
        diagram = parser.parse(mermaid_code)

        if title:
            diagram.metadata["title"] = title

        return diagram
