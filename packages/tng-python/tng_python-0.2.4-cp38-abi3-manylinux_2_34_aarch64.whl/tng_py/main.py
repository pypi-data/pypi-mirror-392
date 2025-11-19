"""
TNG Python CLI - Main Entry Point
"""

import typer
from pathlib import Path
from rich.console import Console

from .cli import init_config
from .interactive import main as interactive_main
from .ui.generate_tests_ui import GenerateTestsUI

# Add console for rich output
console = Console()

app = typer.Typer(
    name="tng",
    help="Automated Python Tests in Minutes - Static analysis engine with AST-based code intelligence",
    add_completion=True,
)


@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force overwrite existing config"
    ),
    config_path=typer.Option(None, help="Path to save config file"),
):
    """
    Initialize TNG configuration for your project.

    This will analyze your codebase and generate a tng_config.py file
    with framework, testing, and dependency configurations.
    """
    init_config(force=force, config_path=config_path)


@app.command()
@app.command("i")
def interactive():
    """
    Launch interactive TNG session.

    Opens a web-based interface for generating tests interactively.
    """
    interactive_main()


@app.command()
@app.command("g")
def generate(
    file: str = typer.Option(
        ..., "--file", "-f", help="Path to Python file to analyze"
    ),
    method: str = typer.Option(
        ..., "--method", "-m", help="Name of the method to generate tests for"
    ),
):
    """
    Generate unit tests for a specific Python method.
    """
    # Validate file exists
    if not Path(file).exists():
        typer.echo(f"❌ Error: File '{file}' does not exist", err=True)
        raise typer.Exit(1)

    # Validate file is Python
    if not file.endswith(".py"):
        typer.echo(
            f"❌ Error: File '{file}' is not a Python file (.py extension required)",
            err=True,
        )
        raise typer.Exit(1)

    typer.echo(f"🔍 Analyzing method '{method}' in '{file}'...")

    try:
        # Create UI instance for test generation
        ui = GenerateTestsUI(cli_mode=True)

        # Prepare method info - assume standalone function for simplicity
        selected_method = {
            "name": method,
            "class": None,
            "display": method,
            "type": "function",
        }

        # Generate tests using the same logic as the interactive UI
        with console.status(
            "[bold green]Analyzing and generating tests...[/bold green]"
        ) as _:
            result = ui._generate_tests_for_method(file, selected_method)

        if result and result.get("file_info"):
            file_info = result["file_info"]
            typer.echo("✅ Tests generated successfully!")
            typer.echo(f"📁 Test file: {file_info.get('file_path', 'Unknown')}")
        else:
            typer.echo("❌ Failed to generate tests", err=True)
            raise typer.Exit(1)

    except KeyboardInterrupt:
        typer.echo("\n🛑 Operation cancelled by user", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        raise typer.Exit(1) from e


@app.command()
def version():
    """Show TNG version information."""
    try:
        from . import __version__

        typer.echo(f"TNG Python v{__version__}")
    except ImportError as e:
        typer.echo("TNG Python (version unknown)")
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
