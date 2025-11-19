import click
from requests.exceptions import HTTPError
from rich.console import Console

from vcp.datasets.api import preview_data_api
from vcp.utils.errors import (
    VCPError,
    check_authentication_status,
    validate_dataset_id,
    with_error_handling,
)
from vcp.utils.token import TokenManager

console = Console()
TOKEN_MANAGER = TokenManager()


@click.command("preview")
@click.argument("dataset_id")
@click.option(
    "--open",
    "open_browser",
    is_flag=True,
    default=False,
    help="Automatically open the preview URL in your browser",
)
@with_error_handling(resource_type="dataset", operation="data preview")
def preview_command(dataset_id: str, open_browser: bool = False):
    """
    Generate a Neuroglancer preview URL for a dataset with zarr files.

    DATASET_ID: The ID of the dataset to preview

    Note: Preview is only available for microscopy datasets that contain zarr files.
    Use 'vcp data describe DATASET_ID' to check available file formats.
    """
    # Validate dataset ID
    validate_dataset_id(dataset_id, "data preview")

    tokens = TOKEN_MANAGER.load_tokens()
    check_authentication_status(tokens, "data preview")

    # Call the preview API endpoint with specific error handling
    try:
        response = preview_data_api(tokens.id_token, dataset_id)
    except HTTPError as e:
        if e.response.status_code == 422:
            # Dataset exists but can't be previewed
            error_message = f"Preview not available for dataset '{dataset_id}'"

            # Try to get additional details from the response
            try:
                error_detail = e.response.json().get("detail", "")
                if error_detail:
                    error_message = f"{error_detail} (dataset: '{dataset_id}')"
            except Exception:
                pass

            raise VCPError(
                error_message,
                suggestion=(
                    "The preview feature only works for microscopy datasets with zarr files. "
                    f"Use 'vcp data describe {dataset_id}' to see available file formats."
                ),
                operation="data preview",
            ) from e
        else:
            # Other HTTP errors (including 404) - let decorator handle them
            raise

    # Display the preview information
    console.print("[bold green]Dataset Preview Generated[/bold green]")
    console.print(f"Dataset: [bold]{response.dataset_label}[/bold]")
    console.print(f"Dataset ID: {response.dataset_id}")
    console.print(f"Zarr files found: {len(response.zarr_files)}")

    if len(response.zarr_files) > 1:
        console.print(
            f"[yellow]Note: Picking a random zarr file for preview purposes from {len(response.zarr_files)} available[/yellow]"
        )

    console.print("\n[bold blue]Neuroglancer Preview URL:[/bold blue]")
    console.print(f"[link]{response.neuroglancer_url}[/link]")

    if open_browser:
        import webbrowser  # noqa: PLC0415

        console.print("\n[green]Opening preview in your default browser...[/green]")
        webbrowser.open(response.neuroglancer_url)
    else:
        console.print("\n[dim]Tip: Use --open to automatically open in browser[/dim]")
