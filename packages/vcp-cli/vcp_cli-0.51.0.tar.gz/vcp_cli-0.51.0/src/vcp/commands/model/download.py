"""Model download command."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from ...config.config import Config
from ...utils.errors import InvalidInputError, with_error_handling
from .api import fetch_files_for_variant, fetch_variants_for_model, select_variant
from .helpers.display_helpers import (
    show_download_results,
    show_download_summary,
    show_variant_selection_panel,
    show_verbose_file_details,
)
from .helpers.download_helpers import (
    download_multiple_files,
    prepare_download_directory,
)

console = Console()


@click.command()
@click.option("--model", required=True, help="Name of the model to download")
@click.option("--version", required=True, help="Version of the model to download")
@click.option(
    "--output",
    default=".",
    help="Directory to save the downloaded model (default: current directory)",
)
@click.option("--config", "-c", help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed debug information")
@click.option("--variant", help="Variant name (e.g., homo_sapiens, mus_musculus)")
@click.option(
    "--max-workers",
    default=4,
    help="Maximum number of concurrent downloads (default: 4)",
)
@with_error_handling(resource_type="model", operation="model download")
def download_command(
    model: str,
    version: str,
    output: str,
    config: Optional[str] = None,
    verbose: bool = False,
    variant: Optional[str] = None,
    max_workers: int = 4,
):
    """Download a specific version of a model from the model hub."""
    output_path = Path(output).expanduser().resolve()
    config_obj = Config.load(config)

    # Step 1: Fetch available variants
    variants = fetch_variants_for_model(config_obj, model=model, version=version)

    if not variants:
        raise InvalidInputError(
            input_type="model/version",
            details=f"No variants found for model '{model}' version '{version}'",
            operation="model download",
        )

    # Step 2: Select variant
    selected_variant = select_variant(variants, variant)

    # If selection returned None, multiple variants exist and user must choose
    if selected_variant is None:
        variant_names = [v.name for v in variants]
        show_variant_selection_panel(model, version, variant_names, error_msg=None)
        return

    # Step 3: Fetch files for selected variant
    response = fetch_files_for_variant(config_obj, variant_id=str(selected_variant.id))

    # Show auto-selection message if variant was auto-selected
    if not variant:
        console.print(
            f"[green]✓[/green] Auto-selected variant: [bold]{response.variant.name}[/bold]"
        )

    # Calculate totals
    total_files = len(response.files)
    total_size = sum(f.size_bytes for f in response.files)

    # Prepare download directory
    model_dir = prepare_download_directory(
        output_path, model=model, version=version, variant_name=response.variant.name
    )

    # Show download summary
    show_download_summary(
        model_dir=model_dir, total_files=total_files, total_size_bytes=total_size
    )

    # Show detailed file info in verbose mode
    if verbose:
        console.print("[bold blue]API Response:[/bold blue] Success")
        show_verbose_file_details(
            response.files, total_size_bytes=total_size, model_dir=model_dir
        )

    # Perform download (silent - no progress bars)
    results = download_multiple_files(
        all_files=response.files,
        output_dir=model_dir,
        max_workers=max_workers,
    )

    # Show results
    successful_count = sum(1 for exc in results.values() if exc is None)
    show_download_results(
        successful_count=successful_count, total_count=total_files, model_dir=model_dir
    )
