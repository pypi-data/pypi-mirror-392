"""Download utilities for model files."""

import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from rich.console import Console

from ....utils.size import format_size_bytes
from ..models import VariantFile

console = Console()

# Larger chunk size for better throughput on modern systems
CHUNK_SIZE = 64 * 1024  # 64KB


def prepare_download_directory(
    output_path: Path, *, model: str, version: str, variant_name: str
) -> Path:
    """Create and return the download directory path.

    Returns:
        Full path to the model download directory
    """
    dir_name = f"{model}-{version}-{variant_name}"
    model_dir = output_path / dir_name
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


def _is_valid_size(
    *, actual_size_bytes: int, expected_size_bytes: int, filename: str
) -> bool:
    """Check if file size is valid, accounting for .gz auto-decompression.

    Args:
        actual_size_bytes: Actual file size in bytes
        expected_size_bytes: Expected file size in bytes
        filename: Name of the file

    Returns:
        True if size is valid
    """
    # Exact match
    if actual_size_bytes == expected_size_bytes:
        return True

    # Accept .gz files that are larger (likely auto-decompressed by S3/CDN)
    if filename.endswith(".gz") and actual_size_bytes > expected_size_bytes:
        return True

    return False


def _should_skip_file(file_path: Path, expected_size_bytes: int) -> bool:
    """Check if file should be skipped (already exists with correct size).

    Args:
        file_path: Path to the output file
        expected_size_bytes: Expected file size in bytes

    Returns:
        True if file exists and has correct size (or is auto-decompressed .gz)
    """
    if not file_path.exists():
        return False

    actual_size_bytes = file_path.stat().st_size
    filename = file_path.name

    return _is_valid_size(
        actual_size_bytes=actual_size_bytes,
        expected_size_bytes=expected_size_bytes,
        filename=filename,
    )


def _calculate_dynamic_timeout_seconds(file_size_bytes: int) -> int:
    """Calculate timeout dynamically based on file size.

    Uses a conservative approach with assumed download speed and safety factor
    to avoid premature timeouts while not waiting indefinitely.

    Formula: timeout = (file_size_mb / assumed_speed_mbps) * safety_factor

    Args:
        file_size_bytes: Size of the file in bytes

    Returns:
        Timeout in seconds, bounded by min and max constraints

    Examples:
        - 1 KB file → 60 seconds (minimum)
        - 100 MB file → 360 seconds (6 minutes)
        - 1 GB file → 1,024 seconds (~17 minutes)
        - 5.7 GB file → 3,600 seconds (60 minutes, capped at max)
    """
    MIN_TIMEOUT = 60  # 1 minute minimum for any file
    MAX_TIMEOUT = 3600  # 60 minutes maximum
    ASSUMED_SPEED_MBPS = 5.0  # Conservative assumption: 5 MB/s
    SAFETY_FACTOR = 3  # 3x safety margin for network variability

    # Calculate base time needed at assumed speed
    file_size_mb = file_size_bytes / (1024 * 1024)
    base_seconds = file_size_mb / ASSUMED_SPEED_MBPS

    # Apply safety factor and enforce bounds
    timeout = int(base_seconds * SAFETY_FACTOR)
    return max(MIN_TIMEOUT, min(timeout, MAX_TIMEOUT))


def download_single_file(
    download_url: str,
    output_dir: Path,
    expected_size_bytes: int,
    filename: Optional[str] = None,
) -> None:
    """Download a single file from URL with dynamic timeout based on file size.

    The timeout is dynamically calculated based on file size to ensure large files
    have sufficient time to download.

    Args:
        download_url: URL to download from
        output_dir: Directory to save file
        expected_size_bytes: Expected file size in bytes
        filename: Optional filename (extracted from URL if not provided)

    Raises:
        requests.exceptions.Timeout: If download times out
        requests.exceptions.RequestException: If download fails
        IOError: If file write fails
        ValueError: If file size validation fails
    """
    # Determine filename
    if not filename:
        parsed_url = urlparse(download_url)
        filename = Path(parsed_url.path).name

    output_file = output_dir / filename

    # Skip if file already exists with correct size
    if _should_skip_file(output_file, expected_size_bytes):
        return

    # Create directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Calculate dynamic read timeout based on file size
    # Connection timeout is fixed, read timeout varies with file size
    read_timeout = _calculate_dynamic_timeout_seconds(expected_size_bytes)
    connect_timeout = 30  # 30 seconds to establish connection
    timeout = (connect_timeout, read_timeout)

    # Download file with context manager to ensure connection is closed
    try:
        with requests.get(download_url, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            # Write to file while connection is open
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
    except requests.exceptions.Timeout:
        # Check if file was actually completed despite timeout
        if _should_skip_file(output_file, expected_size_bytes):
            return  # File is complete!

        # File is incomplete or missing - real timeout failure
        console.print(f"[red]✗ Download timeout for {filename}[/red]")
        if output_file.exists():
            output_file.unlink()  # Clean up partial file
        raise
    except requests.exceptions.RequestException as e:
        # Check if file was completed despite request exception
        if _should_skip_file(output_file, expected_size_bytes):
            return  # File is complete!

        # File is incomplete or missing - real failure
        console.print(f"[red]✗ Download failed for {filename}: {str(e)}[/red]")
        console.print(traceback.format_exc())
        if output_file.exists():
            output_file.unlink()  # Clean up partial file
        raise
    except IOError as e:
        # Handle file write errors
        console.print(f"[red]✗ Failed to write {filename}: {str(e)}[/red]")
        console.print(traceback.format_exc())
        if output_file.exists():
            output_file.unlink()  # Clean up partial file
        raise

    # Validate size
    if _should_skip_file(output_file, expected_size_bytes):
        return

    # Size mismatch - get actual size for error message
    actual_size_bytes = output_file.stat().st_size
    error_msg = (
        f"Size mismatch for {filename}: "
        f"expected {format_size_bytes(expected_size_bytes)}, "
        f"got {format_size_bytes(actual_size_bytes)}"
    )
    console.print(f"[yellow]⚠ {error_msg}[/yellow]")
    if output_file.exists():
        output_file.unlink()  # Clean up invalid file
    raise ValueError(error_msg)


def download_multiple_files(
    all_files: List[VariantFile],
    output_dir: Path,
    max_workers: int = 4,
) -> Dict[Path, Exception | None]:
    """Download multiple files in parallel.

    Args:
        all_files: List of VariantFile objects to download
        output_dir: Base output directory
        max_workers: Maximum number of concurrent downloads

    Returns:
        Dictionary mapping relative_path (as Path) to exception (or None if successful)
    """
    results: Dict[Path, Exception | None] = {}

    def _download_file(file_info: VariantFile) -> tuple[Path, Exception | None]:
        """Download a single file and return the result."""
        relative_path = Path(file_info.relative_path)

        if not file_info.signed_download_url:
            return relative_path, ValueError("Missing download URL")

        # Determine output location
        file_path = output_dir / file_info.relative_path
        file_dir = file_path.parent

        try:
            download_single_file(
                download_url=file_info.signed_download_url,
                output_dir=file_dir,
                expected_size_bytes=file_info.size_bytes,
                filename=file_path.name,
            )
            return relative_path, None  # Success
        except Exception as e:
            return relative_path, e  # Return the exception

    # Download in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_download_file, f): f for f in all_files}
        for future in as_completed(futures):
            relative_path, exception = future.result()
            results[relative_path] = exception

    return results
