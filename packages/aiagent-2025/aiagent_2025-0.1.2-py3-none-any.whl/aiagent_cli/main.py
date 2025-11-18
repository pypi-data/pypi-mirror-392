"""
Main CLI entry point for AI Agent CLI.

Provides commands for codebase understanding and documentation generation.
"""

import click
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import __version__
from .auth import check_auth, setup_auth, get_default_model, get_model_display_name, select_model_interactive
from .scanner import scan_project
from .analyzer import analyze_codebase
from .generator import (
    generate_technical_documentation,
    generate_business_documentation,
)
from .project_brief import create_or_update_brief

console = Console()


def show_interactive_menu() -> None:
    """Display interactive menu and handle user selection."""
    while True:
        console.clear()

        # Get current model for display
        current_model = get_default_model()
        model_display = get_model_display_name(current_model)

        # Create header with model info
        console.print(Panel.fit(
            "[bold cyan]🤖 AI Agent CLI[/bold cyan]\n"
            f"[dim]Version {__version__}[/dim]\n\n"
            "[white]AI-powered codebase analysis and documentation generation[/white]\n"
            f"[green]Current Model:[/green] [yellow]{model_display}[/yellow]\n\n"
            "[dim]Developed by Hossam[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        console.print()

        # Create menu table with emojis
        table = Table(show_header=False, box=None, padding=(0, 3))
        table.add_column("Number", style="bold cyan", width=8, justify="center")
        table.add_column("Option", style="bold white", width=20)
        table.add_column("Description", style="dim")

        table.add_row("1", "⚙️  Configure", "Set up Databricks authentication")
        table.add_row("2", "📋 Project Brief", "Describe your project for better analysis")
        table.add_row("3", "🔍 Understand", "Analyze codebase and build knowledge base")
        table.add_row("4", "📝 Create Docs", "Generate technical documentation")
        table.add_row("5", "💼 Business Docs", "Generate business documentation")
        table.add_row("6", "🎯 Change Model", "Select default AI model")
        table.add_row("", "", "")
        table.add_row("0", "🚪 Exit", "Quit the application")

        console.print(table)
        console.print()

        # Get user choice
        choice = console.input("[bold cyan]Select an option (0-6):[/bold cyan] ").strip()

        try:
            if choice == "0":
                console.print("\n[yellow]Goodbye![/yellow]\n")
                break
            elif choice == "1":
                console.print()
                ctx = click.Context(configure)
                ctx.invoke(configure)
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "2":
                console.print()
                project_path = console.input(
                    "[cyan]Project path (press Enter for current directory):[/cyan] "
                ).strip()
                if not project_path:
                    project_path = str(Path.cwd())

                console.print()
                ctx = click.Context(project_brief)
                ctx.invoke(project_brief, project_path=Path(project_path))
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "3":
                console.print()
                project_path = console.input(
                    "[cyan]Project path (press Enter for current directory):[/cyan] "
                ).strip()
                if not project_path:
                    project_path = str(Path.cwd())

                # Use default model
                selected_model = get_default_model()

                console.print()
                ctx = click.Context(understand)
                ctx.invoke(understand, project_path=Path(project_path), model=selected_model)
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "4":
                console.print()
                project_path = console.input(
                    "[cyan]Project path (press Enter for current directory):[/cyan] "
                ).strip()
                if not project_path:
                    project_path = str(Path.cwd())

                # Use default model
                selected_model = get_default_model()

                console.print()
                ctx = click.Context(create_documentation)
                ctx.invoke(create_documentation, project_path=Path(project_path), model=selected_model)
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "5":
                console.print()
                project_path = console.input(
                    "[cyan]Project path (press Enter for current directory):[/cyan] "
                ).strip()
                if not project_path:
                    project_path = str(Path.cwd())

                # Use default model
                selected_model = get_default_model()

                console.print()
                ctx = click.Context(create_business_documentation)
                ctx.invoke(create_business_documentation, project_path=Path(project_path), model=selected_model)
                console.input("\n[dim]Press Enter to continue...[/dim]")
            elif choice == "6":
                console.print()
                select_model_interactive()
                console.input("\n[dim]Press Enter to continue...[/dim]")
            else:
                console.print("[red]Invalid option. Please select 0-6.[/red]")
                console.input("\n[dim]Press Enter to continue...[/dim]")
        except click.Abort:
            console.input("\n[dim]Press Enter to continue...[/dim]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Returning to menu...[/yellow]")
            console.input("\n[dim]Press Enter to continue...[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.input("\n[dim]Press Enter to continue...[/dim]")


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="aiagent")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    AI Agent CLI - Analyze codebases and generate documentation using Databricks AI.

    Inspired by GitHub spec-kit, this tool helps you understand projects and create
    comprehensive technical and business documentation.

    Run without arguments for interactive menu mode.
    """
    ctx.ensure_object(dict)

    # If no subcommand was provided, show interactive menu
    if ctx.invoked_subcommand is None:
        show_interactive_menu()


@cli.command()
def configure() -> None:
    """
    Configure Databricks authentication (token and workspace URL).

    Run this command to set up or update your Databricks credentials.
    The token is stored securely in your system's keyring.

    Example:
        aiagent configure
    """
    try:
        console.print("\n[bold blue]⚙️  AI Agent - Configuration[/bold blue]\n")
        setup_auth()
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration cancelled by user.[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n")
        raise click.Abort()


@cli.command(name="project-brief")
@click.option(
    "--project-path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Path to the project directory (defaults to current directory)",
)
def project_brief(project_path: Path) -> None:
    """
    Create or update a project brief to improve analysis accuracy.

    Asks 3 quick questions about your project to provide context for AI analysis.
    This helps prevent hallucination and ensures more accurate documentation.

    The brief is optional but highly recommended as it helps the AI understand:
    - What the project is about
    - The problem it solves and business value
    - Who the target users or stakeholders are

    Example:
        aiagent project-brief
        aiagent project-brief --project-path /path/to/project
    """
    try:
        create_or_update_brief(project_path)
    except KeyboardInterrupt:
        console.print("\n[yellow]Project brief cancelled by user.[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n")
        raise click.Abort()


@cli.command()
@click.option(
    "--project-path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Path to the project directory to analyze (defaults to current directory)",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(
        ["databricks-claude-sonnet-4-5", "databricks-gpt-5", "databricks-gemini-2-5-pro"],
        case_sensitive=False,
    ),
    default="databricks-claude-sonnet-4-5",
    help="Databricks AI model to use for analysis",
)
def understand(project_path: Path, model: str) -> None:
    """
    Perform deep analysis of the project and build internal knowledge base.

    This command recursively scans the project, analyzes its structure,
    components, and relationships, then persists the understanding into
    a knowledge file (.aiagent/knowledge.md) for use by other commands.

    Example:
        aiagent understand
        aiagent understand --project-path /path/to/project
        aiagent understand --model databricks-gpt-5
    """
    try:
        console.print("\n[bold blue]🤖 AI Agent - Understanding Your Codebase[/bold blue]\n")

        # Check authentication
        if not check_auth():
            console.print("[yellow]First-time setup detected. Let's configure Databricks authentication.[/yellow]\n")
            setup_auth()

        # Scan project files
        console.print(f"[cyan]📂 Scanning project:[/cyan] {project_path}")
        files = scan_project(project_path)
        console.print(f"[green]✓ Found {len(files)} files to analyze[/green]\n")

        # Analyze codebase
        model_name = get_model_display_name(model)
        console.print(f"[cyan]🔍 Analyzing codebase with {model_name}...[/cyan]")
        knowledge = analyze_codebase(files, project_path, model)

        # Save knowledge file
        aiagent_dir = project_path / ".aiagent"
        aiagent_dir.mkdir(exist_ok=True)
        knowledge_file = aiagent_dir / "knowledge.md"
        knowledge_file.write_text(knowledge)

        console.print(f"\n[bold green]✓ Analysis complete![/bold green]")
        console.print(f"[green]Knowledge saved to:[/green] {knowledge_file}\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n")
        raise click.Abort()


@cli.command(name="create-documentation")
@click.option(
    "--project-path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Path to the project directory (defaults to current directory)",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(
        ["databricks-claude-sonnet-4-5", "databricks-gpt-5", "databricks-gemini-2-5-pro"],
        case_sensitive=False,
    ),
    default="databricks-claude-sonnet-4-5",
    help="Databricks AI model to use for generation",
)
def create_documentation(project_path: Path, model: str) -> None:
    """
    Generate comprehensive technical documentation with architecture diagrams.

    Uses the knowledge base created by the 'understand' command to generate:
    - Detailed technical documentation (technical-documentation.md)
    - Architecture-focused document (architecture.md)
    - Mermaid diagrams for visualizing system design

    Example:
        aiagent create-documentation
        aiagent create-documentation --project-path /path/to/project
    """
    try:
        console.print("\n[bold blue]📝 AI Agent - Generating Technical Documentation[/bold blue]\n")

        # Check authentication
        if not check_auth():
            console.print("[red]✗ Please run 'aiagent understand' first to set up authentication.[/red]\n")
            raise click.Abort()

        # Check for knowledge file
        knowledge_file = project_path / ".aiagent" / "knowledge.md"
        if not knowledge_file.exists():
            console.print("[red]✗ Knowledge file not found. Please run 'aiagent understand' first.[/red]\n")
            raise click.Abort()

        # Load knowledge
        knowledge = knowledge_file.read_text()

        # Generate documentation
        model_name = get_model_display_name(model)
        console.print(f"[cyan]📄 Generating technical documentation with {model_name}...[/cyan]")
        docs = generate_technical_documentation(knowledge, project_path, model)

        # Save documentation files
        aiagent_dir = project_path / ".aiagent"
        tech_doc_file = aiagent_dir / "technical-documentation.md"
        arch_doc_file = aiagent_dir / "architecture.md"

        tech_doc_file.write_text(docs["technical"])
        arch_doc_file.write_text(docs["architecture"])

        console.print(f"\n[bold green]✓ Documentation generated![/bold green]")
        console.print(f"[green]Technical docs:[/green] {tech_doc_file}")
        console.print(f"[green]Architecture:[/green] {arch_doc_file}\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n")
        raise click.Abort()


@cli.command(name="create-business-documentation")
@click.option(
    "--project-path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Path to the project directory (defaults to current directory)",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(
        ["databricks-claude-sonnet-4-5", "databricks-gpt-5", "databricks-gemini-2-5-pro"],
        case_sensitive=False,
    ),
    default="databricks-claude-sonnet-4-5",
    help="Databricks AI model to use for generation",
)
def create_business_documentation(project_path: Path, model: str) -> None:
    """
    Generate business-level documentation with no technical jargon.

    Translates technical concepts into business language suitable for
    stakeholders. The tool will ask up to 5 clarifying questions to map
    unclear technical identifiers to business-friendly terms.

    Example:
        aiagent create-business-documentation
        aiagent create-business-documentation --model databricks-gemini-2-5-pro
    """
    try:
        console.print("\n[bold blue]💼 AI Agent - Generating Business Documentation[/bold blue]\n")

        # Check authentication
        if not check_auth():
            console.print("[red]✗ Please run 'aiagent understand' first to set up authentication.[/red]\n")
            raise click.Abort()

        # Check for knowledge file
        knowledge_file = project_path / ".aiagent" / "knowledge.md"
        if not knowledge_file.exists():
            console.print("[red]✗ Knowledge file not found. Please run 'aiagent understand' first.[/red]\n")
            raise click.Abort()

        # Load knowledge
        knowledge = knowledge_file.read_text()

        # Generate business documentation (includes interactive Q&A)
        model_name = get_model_display_name(model)
        console.print(f"[cyan]💼 Generating business documentation with {model_name}...[/cyan]\n")
        business_doc = generate_business_documentation(knowledge, project_path, model, console)

        # Save documentation
        aiagent_dir = project_path / ".aiagent"
        business_doc_file = aiagent_dir / "business-documentation.md"
        business_doc_file.write_text(business_doc)

        console.print(f"\n[bold green]✓ Business documentation generated![/bold green]")
        console.print(f"[green]Documentation:[/green] {business_doc_file}\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n")
        raise click.Abort()


if __name__ == "__main__":
    cli()
