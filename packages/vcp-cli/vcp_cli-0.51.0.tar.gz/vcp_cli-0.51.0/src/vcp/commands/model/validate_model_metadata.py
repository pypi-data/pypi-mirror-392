import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from ...config.config import Config
from .utils import validate_metadata_files

console = Console()


@click.command()
@click.option(
    "--work-dir",
    help="Path to the model repository work directory (defaults to current directory)",
)
@click.option("--config", "-c", help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed debug information")
def validate_model_metadata_command(
    work_dir: Optional[str] = None,
    config: Optional[str] = None,
    verbose: bool = False,
):
    """Validates model metadata files against requirements in vcp-model-hub.

    By default, looks for files in <work-dir>/model_card_docs/:
    - model_card_metadata.yaml
    - model_card_details.md

    \b
    Examples:
    • vcp model validate-metadata                         # Validate files in current directory
    • vcp model validate-metadata --work-dir ./my-model   # Validate files in specific directory
    • vcp model validate-metadata --verbose               # Show detailed validation info
    """
    # Determine work directory
    if not work_dir:
        work_dir = str(Path.cwd())

    # Load configuration
    config_data = Config.load(config)

    console.print("\n[dim]Validating metadata files...[/dim]")

    try:
        result = validate_metadata_files(work_dir, config_data, verbose)
    except FileNotFoundError as e:
        console.print(
            Panel(
                f"[red]Metadata files not found:[/red]\n{e}\n\n"
                "[yellow]Make sure you're in a model workspace and have run 'vcp model init'.[/yellow]",
                title="[red]Error[/red]",
                border_style="red",
            )
        )
        sys.exit(1)
    # Error during API call
    except Exception as e:
        console.print(
            Panel(
                f"[red]Error during validation:[/red]\n{str(e)}",
                title="[red]Error[/red]",
                border_style="red",
            )
        )
        sys.exit(1)

    # Validation Passed ✓
    if result.success:
        console.print(
            Panel(
                "[green]✓ All metadata validations passed![/green]\n\n"
                "Your metadata files are ready for submission.",
                title="Success",
                border_style="green",
            )
        )
        sys.exit(0)

    # Validation Errors returned from vcp-model-hub
    else:
        console.print(
            Panel(
                result.error_message,
                title="[red]Validation Failed[/red]",
                border_style="red",
            )
        )
        console.print(
            "\n[yellow]Please fix the above errors and run validation again.[/yellow]"
        )
        sys.exit(2)
