"""
Documentation generation using Databricks AI.

Generates technical and business documentation from codebase knowledge.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
import click

from .databricks import DatabricksClient
from .project_brief import load_project_brief, format_brief_for_ai

console = Console()

# Anti-hallucination grounding instructions
GROUNDING_INSTRUCTIONS = """
CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:
- ONLY mention technologies, frameworks, and tools that are explicitly present in the provided code or documentation
- DO NOT assume orchestration tools (Apache Airflow, Databricks Workflows, schedulers, etc.) unless they explicitly appear in imports, code, or configuration files
- DO NOT invent implementation details, deployment strategies, or infrastructure components not visible in the source code
- If a technical aspect is not evident from the provided information, state "Not visible in the provided codebase" rather than making assumptions
- Stick strictly to what can be directly observed and inferred from the actual code structure, imports, and dependencies
- When describing architecture, only include components that are actually implemented in the code
"""

# Document completion footer
COMPLETION_FOOTER = """
---

**Document completed by AI Agent CLI developed by Hossam. Thank you for using it!**
"""


def is_response_complete(response: str) -> bool:
    """
    Check if AI response appears to be complete (not truncated).

    Args:
        response: AI-generated text

    Returns:
        True if response appears complete, False if likely truncated
    """
    if not response or len(response) < 100:
        return False

    # Check for incomplete markdown/code blocks
    if response.count("```") % 2 != 0:
        return False  # Odd number of code fences = incomplete

    # Check for incomplete Mermaid diagrams
    if "```mermaid" in response and response.count("```mermaid") > response.count("```\n", response.rindex("```mermaid")):
        return False

    # Check if ends mid-sentence (no punctuation in last 50 chars)
    last_chunk = response[-50:].strip()
    if last_chunk and not any(last_chunk.endswith(p) for p in ['.', '!', '?', '```', '---', ')']):
        # Could be truncated mid-sentence
        return False

    return True


def generate_technical_documentation(
    knowledge: str,
    project_path: Path,
    model: str,
) -> Dict[str, str]:
    """
    Generate technical documentation with Mermaid diagrams.

    Args:
        knowledge: Content from the knowledge.md file
        project_path: Root directory of the project
        model: Databricks model to use

    Returns:
        Dictionary with 'technical' and 'architecture' documentation
    """
    client = DatabricksClient(model=model)

    # Load project brief if available
    project_brief = load_project_brief(project_path)
    brief_context = format_brief_for_ai(project_brief)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Generate main technical documentation
        task = progress.add_task("Generating technical documentation...", total=None)

        tech_system_prompt = f"""You are an expert technical writer specializing in software documentation. Create comprehensive, well-structured technical documentation that is clear, accurate, and useful for engineers.

Include:
- Clear explanations of architecture and design
- Mermaid diagrams to visualize structure and flows
- Code examples where relevant
- Technical details about implementation

Use Mermaid diagram syntax for visualizations (architecture, sequence, component, flowchart, etc.).

{GROUNDING_INSTRUCTIONS}"""

        tech_user_message = f"""Based on this codebase knowledge, create comprehensive technical documentation for engineers.
{brief_context}
# Codebase Knowledge
{knowledge}

Generate a detailed technical documentation that includes:

1. **System Overview**: High-level description of what the system does
2. **Architecture Diagram**: Use Mermaid to show the overall architecture
3. **Components**: Detailed description of each major component
4. **Data Flow**: How data moves through the system (with Mermaid sequence/flow diagrams)
5. **APIs and Interfaces**: Key APIs, endpoints, or interfaces
6. **Technology Stack**: Detailed breakdown of technologies used
7. **Development Setup**: How to set up the development environment
8. **Testing Strategy**: How the system is tested

Use Mermaid diagrams extensively. Format as professional Markdown documentation."""

        technical_doc, tech_continuations = client.chat_with_continuation(
            system_prompt=tech_system_prompt,
            user_message=tech_user_message,
            temperature=0.4,
            max_continuations=5,
        )

        if tech_continuations > 0:
            console.print(f"[dim]Technical doc generated with {tech_continuations} continuation(s)[/dim]")

        # Generate architecture-focused document
        progress.update(task, description="Generating architecture documentation...")

        arch_system_prompt = f"""You are a software architect creating architecture documentation. Focus on high-level design, component interactions, and architectural decisions.

Emphasize:
- Architectural patterns and principles
- Component responsibilities and boundaries
- Integration points and dependencies
- Design rationale and trade-offs

Use Mermaid diagrams to visualize architecture.

{GROUNDING_INSTRUCTIONS}"""

        arch_user_message = f"""Based on this codebase knowledge, create an architecture document focusing on system design.
{brief_context}
# Codebase Knowledge
{knowledge}

Create an architecture document covering:

1. **Architecture Overview**: High-level architectural approach and patterns
2. **Architecture Diagram**: Comprehensive Mermaid diagram showing all major components
3. **Component Architecture**: Each component's responsibilities and design
4. **Component Interactions**: How components communicate (with Mermaid diagrams)
5. **Data Architecture**: How data is structured and flows
6. **Dependencies**: External dependencies and why they were chosen
7. **Design Decisions**: Key architectural decisions and their rationale
8. **Scalability and Performance**: How the architecture supports scale
9. **Security Considerations**: Security aspects of the architecture

Use multiple Mermaid diagrams. Make it suitable for architects and senior engineers."""

        architecture_doc, arch_continuations = client.chat_with_continuation(
            system_prompt=arch_system_prompt,
            user_message=arch_user_message,
            temperature=0.4,
            max_continuations=5,
        )

        if arch_continuations > 0:
            console.print(f"[dim]Architecture doc generated with {arch_continuations} continuation(s)[/dim]")

    # Add metadata headers and completion footer
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    technical_final = f"""# Technical Documentation: {project_path.name}

**Generated:** {timestamp}
**Created by:** AI Agent CLI developed by Hossam

---

{technical_doc}
{COMPLETION_FOOTER}
"""

    architecture_final = f"""# Architecture Documentation: {project_path.name}

**Generated:** {timestamp}
**Created by:** AI Agent CLI developed by Hossam

---

{architecture_doc}
{COMPLETION_FOOTER}
"""

    return {
        "technical": technical_final,
        "architecture": architecture_final,
    }


MAX_CLARIFICATION_QUESTIONS = 7


def extract_unclear_terms_intelligently(knowledge: str, client: DatabricksClient) -> List[Dict[str, str]]:
    """
    Intelligently identify technical terms that truly need business clarification.

    Uses multi-step reasoning to:
    1. Identify all technical terms
    2. Determine which can be inferred from context
    3. Prioritize questions by business importance
    4. Return only essential questions (max 7)

    Args:
        knowledge: Codebase knowledge content
        client: Databricks client

    Returns:
        List of dicts with 'term' and 'reason' for asking, ordered by priority (max 7)
    """
    system_prompt = """You are an expert business analyst who creates stakeholder-friendly documentation.

Your task is to intelligently identify which technical terms TRULY need clarification from a human.

CRITICAL THINKING PROCESS:
1. Identify technical terms, abbreviations, and jargon
2. For EACH term, determine: Can I understand its business meaning from the context?
   - If YES: Skip it, don't ask about it
   - If NO: This needs a question
3. Rank questions by business importance (impact on understanding)
4. Return ONLY the most essential questions (maximum 7)

IMPORTANT RULES:
- Only ask about terms that are IMPOSSIBLE to understand from context
- Skip common technical terms (API, database, server, etc.) - business people know these
- Skip terms explained elsewhere in the documentation
- Prioritize terms that appear frequently or are central to understanding the system
- If everything is clear from context, return an empty array

RETURN FORMAT: JSON array of objects with 'term' and 'reasoning':
[
  {"term": "xyz_svc", "reasoning": "Cryptic abbreviation, appears in critical flows, purpose unclear"},
  {"term": "t340_proc", "reasoning": "Referenced 15 times, business impact unknown"}
]

Return EMPTY ARRAY [] if no clarifications needed."""

    user_message = f"""Analyze this codebase and use smart reasoning to determine what questions (if any) are TRULY necessary.

Think step by step:
1. What technical terms exist?
2. Which ones can I understand from context?
3. Which ones MUST I ask about?
4. What are the top 7 most important?

# Codebase Knowledge
{knowledge[:4000]}

Return ONLY a JSON array (max 7 items, or empty if none needed)."""

    try:
        # Use 1500 tokens for quick term extraction
        response = client.chat(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=1500,
            temperature=0.4,
        )

        # Extract JSON array from response
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            terms_data = json.loads(match.group(0))
            # Ensure max 7 questions
            return terms_data[:MAX_CLARIFICATION_QUESTIONS]
    except Exception as e:
        # Fallback: If parsing fails, return empty
        print(f"Warning: Failed to extract terms: {e}")
        pass

    return []


def ask_clarification_questions(
    unclear_terms_data: List[Dict[str, str]],
    console: Console,
) -> Dict[str, str]:
    """
    Intelligently ask user for clarifications on terms that truly need it.

    Args:
        unclear_terms_data: List of dicts with 'term' and 'reasoning' keys
        console: Rich console for output

    Returns:
        Dictionary mapping technical terms to business-friendly names
    """
    if not unclear_terms_data:
        console.print("\n[green]✓ Great news! All technical terms in your codebase are clear from context.[/green]")
        console.print("[green]No clarifications needed for business documentation.[/green]\n")
        return {}

    count = len(unclear_terms_data)
    console.print(f"\n[yellow]📋 Smart Analysis Complete:[/yellow]")
    console.print(f"Found [bold]{count}[/bold] term{'s' if count != 1 else ''} that need{'s' if count == 1 else ''} clarification for business-friendly documentation.\n")

    mappings = {}

    for i, term_data in enumerate(unclear_terms_data, 1):
        term = term_data.get('term', '')
        reasoning = term_data.get('reasoning', 'Unclear business meaning')

        console.print(f"[cyan]━━━ Question {i}/{count} ━━━[/cyan]")
        console.print(f"[bold white]Term:[/bold white] '{term}'")
        console.print(f"[dim]Why asking:[/dim] {reasoning}\n")

        answer = click.prompt(
            "Business-friendly name (or press Enter to skip)",
            default="",
            show_default=False,
        ).strip()

        if answer:
            mappings[term] = answer
            console.print(f"[green]✓ Recorded:[/green] [bold]{term}[/bold] → [bold]{answer}[/bold]\n")
        else:
            console.print("[yellow]⊘ Skipped[/yellow]\n")

    if mappings:
        console.print(f"[green]✓ Collected {len(mappings)} business term mapping{'s' if len(mappings) != 1 else ''}[/green]\n")

    return mappings


def generate_business_documentation(
    knowledge: str,
    project_path: Path,
    model: str,
    console: Console,
) -> str:
    """
    Generate business-level documentation with no technical jargon.

    Args:
        knowledge: Content from the knowledge.md file
        project_path: Root directory of the project
        model: Databricks model to use
        console: Rich console for interactive questions

    Returns:
        Business documentation as Markdown string
    """
    client = DatabricksClient(model=model)

    # Load project brief if available
    project_brief = load_project_brief(project_path)
    brief_context = format_brief_for_ai(project_brief)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Intelligently extract terms that truly need clarification
        task = progress.add_task("🧠 Smart analysis: identifying terms that need clarification...", total=None)

        unclear_terms_data = extract_unclear_terms_intelligently(knowledge, client)

    # Ask intelligent, prioritized clarification questions
    mappings = ask_clarification_questions(unclear_terms_data, console)

    # Save mappings
    if mappings:
        mappings_file = project_path / ".aiagent" / "business-mappings.json"
        mappings_file.write_text(json.dumps(mappings, indent=2))
        console.print(f"[green]Saved term mappings to {mappings_file}[/green]\n")

    # Generate business documentation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Generating business documentation...", total=None)

        system_prompt = f"""You are an expert business analyst who translates technical systems into business language. Create documentation for business stakeholders that:

- Uses ONLY business terminology (NO technical jargon)
- Focuses on business capabilities, processes, and value
- Explains WHAT the system does and WHY, not HOW
- Uses clear, simple language
- Avoids: code references, implementation details, technical architecture

Your audience is business stakeholders, not engineers.

{GROUNDING_INSTRUCTIONS}"""

        mappings_context = ""
        if mappings:
            mappings_context = "\n\n## Business Term Mappings\n"
            mappings_context += "Use these business-friendly names instead of technical terms:\n"
            for tech, business in mappings.items():
                mappings_context += f"- '{tech}' should be called '{business}'\n"

        user_message = f"""Based on this codebase knowledge, create comprehensive business documentation.
{brief_context}
# Codebase Knowledge
{knowledge}
{mappings_context}

Create business documentation covering:

1. **Business Overview**: What business problem does this system solve?
2. **Business Capabilities**: What can the system do (in business terms)?
3. **Business Processes**: Key business processes supported
4. **Data & Entities**: Important business entities and information
5. **Business Workflows**: How business users interact with the system
6. **Business Value**: Benefits and value delivered
7. **Business Rules**: Key business rules and logic

IMPORTANT:
- Use ONLY business language
- NO technical implementation details
- NO code or technical architecture
- Focus on business value and capabilities
- Use the business term mappings provided

Format as professional business documentation."""

        business_doc, bus_continuations = client.chat_with_continuation(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.5,
            max_continuations=5,
        )

        if bus_continuations > 0:
            console.print(f"[dim]Business doc generated with {bus_continuations} continuation(s)[/dim]")

    # Add metadata header and completion footer
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    final_doc = f"""# Business Documentation: {project_path.name}

**Generated:** {timestamp}
**Created by:** AI Agent CLI developed by Hossam

---

{business_doc}
{COMPLETION_FOOTER}
"""

    return final_doc
