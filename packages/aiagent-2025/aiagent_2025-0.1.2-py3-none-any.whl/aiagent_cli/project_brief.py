"""
Project brief gathering and management.

Collects high-level project context to improve AI analysis accuracy
and prevent hallucination by providing explicit project intent.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from rich.console import Console
from rich.panel import Panel
import click

console = Console()

# Maximum number of questions to ask
MAX_QUESTIONS = 3

# Project brief questions based on best practices
BRIEF_QUESTIONS = [
    {
        "key": "project_overview",
        "question": "What is this project about?",
        "prompt": "Provide a high-level overview of what this project does",
        "example": "e.g., 'A web application for tracking customer orders and inventory'",
    },
    {
        "key": "purpose_and_value",
        "question": "What problem does it solve or what business value does it provide?",
        "prompt": "Describe the purpose, problem being solved, or business value",
        "example": "e.g., 'Reduces manual order processing time by 80% and prevents inventory errors'",
    },
    {
        "key": "target_users",
        "question": "Who are the target users or stakeholders?",
        "prompt": "Describe who will use or benefit from this project",
        "example": "e.g., 'Warehouse staff, inventory managers, and customer service teams'",
    },
]


def get_brief_file(project_path: Path) -> Path:
    """
    Get the path to the project brief file.

    Args:
        project_path: Root directory of the project

    Returns:
        Path to project-brief.json
    """
    return project_path / ".aiagent" / "project-brief.json"


def load_project_brief(project_path: Path) -> Optional[Dict[str, str]]:
    """
    Load existing project brief if it exists.

    Args:
        project_path: Root directory of the project

    Returns:
        Dictionary with brief data, or None if not found
    """
    brief_file = get_brief_file(project_path)
    if not brief_file.exists():
        return None

    try:
        return json.loads(brief_file.read_text())
    except Exception:
        return None


def save_project_brief(project_path: Path, brief: Dict[str, str]) -> None:
    """
    Save project brief to file.

    Args:
        project_path: Root directory of the project
        brief: Dictionary with brief data
    """
    brief_file = get_brief_file(project_path)
    brief_file.parent.mkdir(parents=True, exist_ok=True)
    brief_file.write_text(json.dumps(brief, indent=2))


def format_brief_for_ai(brief: Optional[Dict[str, str]]) -> str:
    """
    Format project brief for inclusion in AI prompts.

    Args:
        brief: Project brief dictionary

    Returns:
        Formatted string for AI context, or empty string if no brief
    """
    if not brief:
        return ""

    context = "\n## Project Brief (User-Provided Context)\n\n"
    context += "**IMPORTANT**: This is what the user says the project is SUPPOSED to do.\n"
    context += "Use this to understand project intent and prevent hallucination.\n\n"

    if "project_overview" in brief and brief["project_overview"]:
        context += f"**Project Overview**: {brief['project_overview']}\n\n"

    if "purpose_and_value" in brief and brief["purpose_and_value"]:
        context += f"**Purpose & Value**: {brief['purpose_and_value']}\n\n"

    if "target_users" in brief and brief["target_users"]:
        context += f"**Target Users**: {brief['target_users']}\n\n"

    context += "**Analysis Guidance**: Validate that the actual code implementation aligns with this stated purpose. "
    context += "If you find discrepancies, note them. Do not assume features not present in the code.\n\n"

    return context


def gather_project_brief(project_path: Path) -> Dict[str, str]:
    """
    Interactively gather project brief from user.

    Args:
        project_path: Root directory of the project

    Returns:
        Dictionary with brief responses
    """
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📋 Project Brief[/bold cyan]\n\n"
        "[white]Help the AI understand your project better by answering 3 quick questions.\n"
        "This context improves analysis accuracy and prevents hallucination.[/white]\n\n"
        "[dim]You can skip any question by pressing Enter[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()

    brief = {}

    for i, question_data in enumerate(BRIEF_QUESTIONS, 1):
        console.print(f"[cyan]━━━ Question {i}/{MAX_QUESTIONS} ━━━[/cyan]")
        console.print(f"[bold white]{question_data['question']}[/bold white]")
        console.print(f"[dim]{question_data['example']}[/dim]\n")

        answer = click.prompt(
            question_data["prompt"],
            default="",
            show_default=False,
        ).strip()

        if answer:
            brief[question_data["key"]] = answer
            console.print(f"[green]✓ Recorded[/green]\n")
        else:
            console.print("[yellow]⊘ Skipped[/yellow]\n")

    # Summary
    answered = sum(1 for v in brief.values() if v)
    if answered > 0:
        console.print(f"[green]✓ Project brief completed with {answered} answer{'s' if answered != 1 else ''}[/green]")
    else:
        console.print("[yellow]⚠️  No information provided - analysis will proceed without project context[/yellow]")

    return brief


def create_or_update_brief(project_path: Path) -> None:
    """
    Create or update project brief for a project.

    Args:
        project_path: Root directory of the project
    """
    console.print("\n[bold blue]📋 AI Agent - Project Brief[/bold blue]\n")

    # Check if brief already exists
    existing_brief = load_project_brief(project_path)
    if existing_brief:
        console.print("[yellow]A project brief already exists for this project.[/yellow]")
        console.print()

        # Show existing brief
        console.print("[cyan]Current Brief:[/cyan]")
        for key, value in existing_brief.items():
            if value:
                # Convert snake_case to Title Case
                label = key.replace("_", " ").title()
                console.print(f"  [bold]{label}:[/bold] {value}")
        console.print()

        # Ask if user wants to update
        update = click.confirm("Do you want to update it?", default=False)
        if not update:
            console.print("[yellow]Keeping existing project brief.[/yellow]\n")
            return

    # Gather brief
    brief = gather_project_brief(project_path)

    # Save if any answers provided
    if brief:
        save_project_brief(project_path, brief)
        brief_file = get_brief_file(project_path)
        console.print(f"\n[green]Project brief saved to:[/green] {brief_file}")
        console.print("\n[cyan]💡 Tip:[/cyan] This context will be used by 'understand' and documentation commands to improve accuracy.\n")
    else:
        console.print("\n[yellow]No project brief saved. You can create one later by running this command again.[/yellow]\n")
