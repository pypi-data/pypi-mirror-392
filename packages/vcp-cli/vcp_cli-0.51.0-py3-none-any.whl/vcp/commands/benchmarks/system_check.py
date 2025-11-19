"""System hardware validation CLI command for VCP benchmarks."""

import click
from rich.console import Console

from .system_validator import SystemValidator
from .utils import CLIError, format_as_table, handle_cli_error

console = Console()


@click.command(
    name="system-check", context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Display detailed NVIDIA GPU diagnostic information for troubleshooting.",
)
def system_check_command(verbose: bool) -> None:
    """
    Display system hardware information for running VCP benchmarks.

    Shows current system specifications including RAM, GPUs, CUDA version,
    and Docker availability compared against baseline requirements.
    """
    try:
        validator = SystemValidator()
        system_info = format_as_table(
            validator.get_system_info(),
            table_type=["component", "actual", "expected", "status"],
            table_title="System Information",
        )
        console.print("\n[bold]System Hardware Information[/bold]\n")
        console.print(system_info)

        if verbose:
            validator.print_verbose_info()

    except CLIError:
        raise
    except Exception as e:
        handle_cli_error(CLIError(f"System check failed: {e}"))
