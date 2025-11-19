"""Display and UI helper functions for model download command."""

import os
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from ....utils.size import format_size_bytes
from ..models import VariantFile

console = Console()


def show_variant_selection_panel(
    model: str, version: str, variants: list[str], error_msg: str | None = None
) -> None:
    """Display variant selection help to user."""
    title = "Variant Not Found" if error_msg else "Variant Selection Required"
    color = "red" if error_msg else "yellow"

    lines = []
    if error_msg:
        lines.append(f"[{color}]{error_msg}[/{color}]\n")
    else:
        lines.append(
            f"[{color}]Multiple variants available for {model} {version}[/{color}]\n"
        )

    lines.append("Available variants:")
    lines.extend(f"  • {v}" for v in variants)
    lines.append(f"\n{'Run' if error_msg else 'Please specify a variant'}:")
    lines.append(
        f"  [blue]vcp model download --model {model} --version {version} --variant <variant_name>[/blue]"
    )

    console.print(Panel("\n".join(lines), title=title))


def show_verbose_file_details(
    all_files: list[VariantFile], *, total_size_bytes: int, model_dir: Path
) -> None:
    """Display detailed file information in verbose mode."""
    console.print(f"\n[bold blue]Files to download:[/bold blue] {len(all_files)} files")
    console.print(
        f"[bold blue]Total size:[/bold blue] {format_size_bytes(total_size_bytes)}"
    )
    console.print(f"[bold blue]Download directory:[/bold blue] {model_dir}\n")

    for i, file_info in enumerate(all_files, 1):
        filename = os.path.basename(file_info.relative_path)
        console.print(
            f"[bold blue]File {i}:[/bold blue] {filename} ({format_size_bytes(file_info.size_bytes)})"
        )
        console.print(f"[bold blue]  Path:[/bold blue] {file_info.relative_path}")


def show_download_summary(
    *, model_dir: Path, total_files: int, total_size_bytes: int
) -> None:
    """Display download location and summary."""
    file_word = "file" if total_files == 1 else "files"
    size_gb = total_size_bytes / (1024**3)  # Convert bytes to GB
    console.print(
        Panel(
            f"[cyan]Downloading to:[/cyan] [bold]{model_dir}[/bold]\n"
            f"[dim]Total: {total_files} {file_word} ({size_gb:.2f} GB)[/dim]",
            title="📥 Download Info",
            border_style="cyan",
        )
    )


def show_download_results(
    *, successful_count: int, total_count: int, model_dir: Path
) -> None:
    """Display download results with appropriate success/warning/error message."""
    if successful_count == total_count:
        file_word = "file" if total_count == 1 else "files"
        console.print(
            Panel(
                f"[green]✅ All {total_count} {file_word} downloaded successfully to: {model_dir}[/green]",
                title="Success",
            )
        )
    elif successful_count > 0:
        console.print(
            Panel(
                f"[yellow]⚠️ Partial success: {successful_count}/{total_count} files downloaded to: {model_dir}[/yellow]\n"
                f"Some files may have failed. Check the output directory.",
                title="Partial Success",
            )
        )
    else:
        console.print(
            Panel(
                "[red]❌ All downloads failed. No files were downloaded.[/red]",
                title="Download Error",
            )
        )
