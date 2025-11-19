import hashlib
import json
import logging
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, get_args, get_origin

import click
import numpy as np
from rich.console import Console
from rich.table import Table

from vcp.config.config import Config

logger = logging.getLogger(__name__)
console = Console()


# TODO: will be replaced when implementing https://czi.atlassian.net/browse/VC-3963
CACHE_PATH = Path.home() / ".vcp" / "cache"

# Column order for benchmark table outputs
# Used by both 'benchmarks list' and 'benchmarks get' commands to ensure consistency
BENCHMARK_BASE_COLUMNS = [
    "benchmark_key",
    "model_key",
    "model_name",
    "dataset_keys",
    "dataset_names",
    "task_key",
    "task_name",
]


def _build_cache_dir_path(
    model_uid: str,
    dataset_uids: List[str],
    task: Optional[str] = None,
    task_run_id: Optional[str] = None,
) -> Path:
    datasets_cache_key = "_".join(sorted(dataset_uids))
    if task:
        cache_dir = (
            CACHE_PATH
            / model_uid
            / datasets_cache_key
            / "task_outputs"
            / task
            / str(task_run_id)
        )
    else:
        cache_dir = CACHE_PATH / model_uid / datasets_cache_key
    return cache_dir


# TODO: Move all cache-related methods to a new cache.py module
def save_to_cache(
    model_key: str,
    dataset_uids: List[str],
    task: Optional[str],
    data: Any,
    data_type: str = "auto",
    task_run_id: Optional[str] = None,
):
    """
    Save data to the local cache directory for a given model, dataset, and task.

    This function serializes and stores data (such as embeddings, results, or datasets)
    in the appropriate subdirectory under ~/.vcp/cache/<model>/<dataset>/task_outputs/<task>/.
    The file type and name are determined by the data_type argument or inferred from the data.
    Creates cache directories automatically if they don't exist.

    Args:
        model (str): The model identifier/key.
        datasets (List[Dataset]): The datasets.
        task (Optional[str]): The task identifier/key. If None, data is stored at the
            model/dataset level without task_outputs subdirectory.
        data (Any): The data to cache. Can be a numpy array, dict, or AnnData object.
        data_type (str, optional): Type of data to store. Options are:
            - "embeddings": Save as .npy file
            - "results": Save as .json file
            - "dataset": Save as .h5ad file
            - "auto": Automatically infer type from data. Defaults to "auto".

    Returns:
        None

    Raises:
        CLIError: If the data type is unsupported for caching or if data cannot be serialized.
    """

    cache_dir = _build_cache_dir_path(model_key, dataset_uids, task, task_run_id)

    cache_dir.mkdir(parents=True, exist_ok=True)

    if data_type == "embeddings" or (
        data_type == "auto" and isinstance(data, np.ndarray)
    ):
        file_path = cache_dir / "embeddings.npy"
        np.save(file_path, data)
    elif data_type == "results" or (data_type == "auto" and isinstance(data, dict)):
        file_path = cache_dir / "results.json"
        file_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    # TODO: remove this case; never used
    elif data_type == "dataset" or (
        data_type == "auto" and hasattr(data, "write_h5ad")
    ):
        file_path = cache_dir / "dataset.h5ad"
        data.write_h5ad(file_path)
    else:
        raise CLIError(f"Unsupported data type for caching: {type(data)}")


# TODO: Should return None on cache miss instead of raising FileNotFoundError; cache misses are normal behavior
def load_from_cache(
    model: str,
    dataset_uids: List[str],
    task: Optional[str],
    data_type: str,
    task_run_id: Optional[str] = None,
) -> Any:
    """
    Load cached data for a given model, dataset, and task from the local cache directory.

    Retrieves and deserializes data (such as embeddings, results, or datasets) from
    ~/.vcp/cache/<model>/<dataset>/task_outputs/<task>/ or ~/.vcp/cache/<model>/<dataset>/
    based on whether a task is specified and the data_type requested.

    Args:
        model (str): The model identifier/key.
        dataset_keys (List[str]): The dataset identifiers/keys.
        task (Optional[str]): The task identifier/key. If None, loads from the
            model/dataset level directory.
        data_type (str): Type of data to load. Must be one of:
            - "embeddings": Load .npy file as numpy array
            - "results": Load .json file as dictionary
            - "dataset": Load .h5ad file as AnnData object

    Returns:
        Any: The loaded data - numpy array for embeddings, dict for results,
             or AnnData object for datasets.

    Raises:
        FileNotFoundError: If the requested cache file does not exist.
        CLIError: If the data_type is not supported.
    """

    cache_dir = _build_cache_dir_path(model, dataset_uids, task, task_run_id)

    if data_type == "embeddings":
        file_path = cache_dir / "embeddings.npy"

        if not file_path.exists():
            raise FileNotFoundError(f"Embeddings not found: {file_path}")

        return np.load(file_path)
    elif data_type == "results":
        file_path = cache_dir / "results.json"
        logger.debug(f"Trying to load cached results from {file_path}")
        if not file_path.exists():
            raise FileNotFoundError(f"Results not found: {file_path}")
        return json.loads(file_path.read_text(encoding="utf-8"))
    elif data_type == "dataset":
        # TODO: remove this case; never used
        file_path = cache_dir / "dataset.h5ad"

        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found: {file_path}")
        from anndata import read_h5ad  # noqa: PLC0415

        return read_h5ad(file_path)
    else:
        raise CLIError(f"Unsupported data type: {data_type}")


def get_cell_representation_cache_dir(model: str, dataset_uids: List[str]) -> Path:
    """
    Get (and create if necessary) the cache directory for a given model and dataset, where cell representations are stored.

    Constructs the path ~/.vcp/cache/<model>/<dataset_keys>/ and ensures it exists.

    Args:
        model (str): The model key.
        dataset_keys (List[str]): The dataset keys.

    Returns:
        Path: The Path object for the cache directory.
    """
    cache_dir = _build_cache_dir_path(model, dataset_uids)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def generate_benchmark_key(
    model_key: str, dataset_keys: List[str], task_key: str
) -> str:
    """
    Generate a short hash-based benchmark key from model, dataset, and task information.

    Creates a deterministic 16-character hexadecimal hash from the descriptive
    benchmark key format: {model_key}-[{dataset_keys_joined}]-{task_key}

    Args:
        model_key (str): The model identifier.
        dataset_keys (List[str]): List of dataset identifiers.
        task_key (str): The task identifier.

    Returns:
        str: 16-character hexadecimal hash representing the benchmark.

    Examples:
        >>> generate_benchmark_key("AIDO-cell_3m", ["tsv2_blood"], "clustering")
        'ee79e260a24cdc63'
        >>> generate_benchmark_key("SCVI-multi_species", ["mouse_brain", "mouse_liver"], "clustering")
        'a3ba18c4b6a3ec1f'
    """
    descriptive_key = f"{model_key}-{sorted(dataset_keys)!r}-{task_key}"
    return hashlib.sha256(descriptive_key.encode("utf-8")).hexdigest()[:16]


def format_as_table(
    rows: List[Dict],
    table_type: str = "auto",
    depth: int = 2,
    table_title: Optional[str] = "Benchmarks",
    wrap: bool = True,
) -> Table:
    """
    Format a list of dictionaries as a Rich table for console display.

    Infers columns from the data, supports nested dicts up to a specified depth,
    and allows explicit column ordering. Handles missing values and formats
    floats, dicts, and lists for display.

    Args:
        rows (List[Dict]): List of records to display as table rows.
        table_type (str or List[str], optional): Controls column ordering:
            - "auto": Automatically sort columns alphabetically
            - List[str]: Explicit column order; unlisted columns appear after listed ones
            Defaults to "auto".
        depth (int, optional): Maximum depth for flattening nested dictionaries.
            Nested keys become "parent.child" column names. Defaults to 2.
        wrap (bool, optional): If True, descriptive columns wrap within max_width=24.
            If False, all columns display full values without width constraints.
            Defaults to True.

    Returns:
        Table: A Rich Table object ready for console display with proper formatting.
    """

    if not rows:
        return Table()

    def extract_columns(row: Dict, parent: str = "", level: int = 1) -> List[str]:
        cols = []
        for k, v in row.items():
            col_name = f"{parent}.{k}" if parent else k
            if isinstance(v, dict) and level < depth:
                cols.extend(extract_columns(v, col_name, level + 1))
            else:
                cols.append(col_name)
        return cols

    columns_set = set()
    for row in rows:
        columns_set.update(extract_columns(row))
    all_columns = sorted(columns_set)

    if isinstance(table_type, list):
        columns = table_type + [col for col in all_columns if col not in table_type]
    else:
        columns = sorted(all_columns)

    # Use expand=False to prevent table from being squeezed to fit terminal width
    tbl = Table(
        show_header=True, header_style="bold magenta", title=table_title, expand=False
    )

    # Key/ID columns should never wrap or truncate (for easy copying)
    no_wrap_columns = {
        "benchmark_key",
        "model_key",
        "dataset_keys",
        "task_key",
        "metric",
    }

    for col in columns:
        header_text = str(col).replace("_", " ").title()
        min_width = max(12, len(header_text))

        if wrap:
            # With wrapping: Key columns show full value, descriptive columns wrap within max_width
            if col in no_wrap_columns:
                tbl.add_column(
                    header_text, overflow="visible", no_wrap=True, min_width=min_width
                )
            else:
                tbl.add_column(
                    header_text,
                    overflow="fold",
                    no_wrap=False,
                    min_width=min_width,
                    max_width=24,
                )
        else:
            # Without wrapping: All columns show full values without width constraints
            tbl.add_column(
                header_text, overflow="visible", no_wrap=True, min_width=min_width
            )

    def get_value(row: Dict, col: str):
        keys = col.split(".")
        val = row
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return ""
        if isinstance(val, float):
            return f"{val:.4f}"
        elif isinstance(val, dict):
            return json.dumps(val)
        elif isinstance(val, list):
            return ", ".join(map(str, val))
        else:
            return str(val)

    for r in rows:
        row_values = [get_value(r, col) for col in columns]
        tbl.add_row(*row_values)
    return tbl


class CLIError(click.ClickException):
    """
    Custom exception class for CLI-related errors.

    Inherits from click.ClickException to provide proper error handling
    and formatting within the Click command-line interface framework.

    Args:
        message (str): The error message to display to the user.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DockerRunner:
    """
    Utility class for running Docker containers with GPU support and custom configurations.

    Provides a simplified interface for executing commands in Docker containers,
    with support for GPU acceleration, volume mounts, and environment variables.

    Attributes:
        Mount: Type alias for mount specification (host_path, container_path, mode).

    Args:
        use_gpu (bool, optional): Whether to enable GPU support with --gpus all. Defaults to True.
        custom_args (Optional[List[str]], optional): Additional Docker arguments. Defaults to None.
    """

    Mount = Tuple[str, str, str]

    def __init__(self, use_gpu: bool = True, custom_args: Optional[List[str]] = None):
        self.use_gpu = use_gpu
        self.custom_args = custom_args or []

    def run(
        self,
        image: str,
        mounts: List[Mount],
        cmd_args: List[str],
        description: str,
        env_vars: Optional[Dict[str, str]] = None,
    ):
        """
        Execute a command in a Docker container with specified configuration.

        Args:
            image (str): Docker image name/tag to run.
            mounts (List[Mount]): List of volume mounts as (host_path, container_path, mode) tuples.
            cmd_args (List[str]): Command and arguments to execute in the container.
            description (str): Human-readable description for logging purposes.
            env_vars (Optional[Dict[str, str]], optional): Environment variables to set. Defaults to None.

        Returns:
            None

        Raises:
            CLIError: If Docker is not found or if the container execution fails.
        """

        cmd = ["docker", "run", "--rm"]
        if self.use_gpu:
            cmd += ["--gpus", "all"]
        cmd.extend(self.custom_args)
        if env_vars:
            for k, v in env_vars.items():
                cmd += ["-e", f"{k}={v}"]
        for host, container, mode in mounts:
            cmd += ["-v", f"{host}:{container}:{mode}"]
        cmd += [image] + cmd_args
        logger.info(f"{description} command: {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, check=True, shell=False
            )
            logger.debug(f"{description} stdout:\n{proc.stdout}")
        except FileNotFoundError as e:
            raise CLIError(
                "Docker not found. Please ensure Docker is installed and accessible in PATH."
            ) from e
        except subprocess.CalledProcessError as e:
            stderr_msg = e.stderr.strip() if e.stderr else "No error output"
            raise CLIError(
                f"{description} failed (exit code {e.returncode}). Docker error: {stderr_msg}"
            ) from e


def mutually_exclusive(*other_names: str):
    """
    Create a Click callback to enforce mutual exclusivity between CLI options.

    Ensures that only one of the mutually exclusive options is provided by the user.
    Raises a Click.BadParameter error if more than one is specified.

    Args:
        *other_names (str): Names of other mutually exclusive options.

    Returns:
        Callable: A Click callback function for use in option definitions.
    """

    def callback(ctx: click.Context, param: click.Parameter, value: Any):
        current_has_value = False
        if isinstance(value, tuple):
            current_has_value = len(value) > 0
        elif isinstance(value, bool):
            # For boolean flags, only consider True as "has value"
            current_has_value = value is True
        else:
            current_has_value = value is not None

        if current_has_value:
            for other in other_names:
                other_value = ctx.params.get(other)
                other_has_value = False

                if isinstance(other_value, tuple):
                    other_has_value = len(other_value) > 0
                elif isinstance(other_value, bool):
                    # For boolean flags, only consider True as "has value"
                    other_has_value = other_value is True
                else:
                    other_has_value = other_value is not None

                if other_has_value:
                    param_name_kebab = param.name.replace("_", "-")
                    other_name_kebab = other.replace("_", "-")
                    raise click.BadParameter(
                        f"--{param_name_kebab} and --{other_name_kebab} are mutually exclusive."
                    )
        return value

    return callback


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Load and cache the application configuration.

    Uses LRU cache to ensure the configuration is loaded only once per session.
    Handles configuration loading errors gracefully by calling handle_cli_error.

    Returns:
        Config: The loaded configuration object, or None if loading fails.

    Raises:
        CLIError: Via handle_cli_error if configuration cannot be loaded.
    """

    try:
        return Config.load()
    except Exception as e:
        handle_cli_error(CLIError(f"Configuration error: {e}"))
        return None


def validate_benchmark_filters(
    model_filter: Optional[str] = None,
    dataset_filter: Optional[str] = None,
    task_filter: Optional[str] = None,
) -> None:
    """
    Validate benchmark filter parameters for length and content safety.

    Ensures filter strings are within acceptable length limits and don't contain
    potentially dangerous characters that could be used for injection attacks.

    Args:
        model_filter (Optional[str], optional): Model name filter. Defaults to None.
        dataset_filter (Optional[str], optional): Dataset name filter. Defaults to None.
        task_filter (Optional[str], optional): Task name filter. Defaults to None.

    Returns:
        None

    Raises:
        CLIError: If any filter exceeds 100 characters or contains invalid characters (<, >, ", ').
    """

    filters = {
        "model_filter": model_filter,
        "dataset_filter": dataset_filter,
        "task_filter": task_filter,
    }

    for name, value in filters.items():
        if value and len(value) > 100:
            handle_cli_error(CLIError(f"{name} too long (max 100 characters)"))
        if value and any(char in value for char in ["<", ">", '"', "'"]):
            handle_cli_error(CLIError(f"{name} contains invalid characters"))


def handle_cli_error(error: CLIError) -> None:
    """Print CLI error to console and exit without raising, to avoid double logging."""
    console.print(f"[red]Error:[/red] {error}")
    sys.exit(1)


def get_first_sentence(text: str) -> str:
    """Extract the first sentence from a docstring.

    Args:
        text: The full text to extract from.

    Returns:
        The first sentence, ending with a period.
    """
    # Remove all newlines and collapse multiple spaces
    single_line = " ".join(text.split())

    # Find the first sentence (ends with period, question mark, or exclamation)
    for i, char in enumerate(single_line):
        if char in ".!?" and (
            i == len(single_line) - 1 or single_line[i + 1].isspace()
        ):
            return single_line[: i + 1]

    # If no sentence ending found, return the text (shouldn't happen with well-formed docstrings)
    return single_line


def display_benchmark_results_table(
    enriched_results: Dict[str, Any], console: Console, wrap: bool = True
) -> None:
    """Display benchmark run results as a formatted table.

    Args:
        enriched_results: Enriched results dict (JSON types only, no Pydantic models). See _build_enriched_results() for structure.
        console: Rich console for output
        wrap: If True, wrap descriptive columns. If False, show full values. Defaults to True.
    """

    run_spec = enriched_results["run_specification"]
    result_metrics = enriched_results["result_metrics"]
    runtime_metrics = enriched_results.get("runtime_metrics", {})

    # Determine model key for display
    model_details = run_spec.get("model_details", {})
    if model_details and model_details.get("key"):
        model_key = model_details["key"]
    elif run_spec.get("run_baseline"):
        model_key = "baseline"
    elif run_spec.get("cell_representations"):
        model_key = "user-cell-representation"
    else:
        raise CLIError("Invalid run specification: missing model details")

    # Determine dataset keys for display
    dataset_keys = []
    for d in run_spec.get("datasets", []):
        if d.get("key"):
            dataset_keys.append(d["key"])
        elif d.get("user_dataset"):
            path = d["user_dataset"].get("path", "")
            dataset_keys.append(f"user:{Path(path).name}" if path else "user-dataset")
        else:
            dataset_keys.append("unknown")

    # Print summary information
    console.print(f"\n[bold]Model:[/bold] {model_key}")
    console.print(f"[bold]Datasets:[/bold] {', '.join(dataset_keys)}")
    console.print(f"[bold]Task:[/bold] {run_spec.get('task_key', 'unknown')}")
    if runtime_metrics:
        elapsed = runtime_metrics.get("elapsed_time_secs", 0)
        memory = runtime_metrics.get("max_memory_mib", 0)
        console.print(f"[bold]Runtime:[/bold] {elapsed:.2f} secs, {memory:.2f} MiB")
    console.print()

    # Build rows for table
    if not result_metrics:
        console.print("[yellow]No metrics to display[/yellow]")
        return

    rows = []
    for metric in result_metrics:
        row = {
            "metric_type": metric.get("metric_type", "unknown"),
            "value": metric.get("value", 0),
        }
        rows.append(row)

    # Display table
    ordered_columns = ["metric_type", "value"]
    table = format_as_table(
        rows, table_type=ordered_columns, table_title="Benchmark Results", wrap=wrap
    )
    console.print(table)


def type_to_click_info(param_type: Any) -> Tuple[click.ParamType, bool]:
    """Infers click parameter type from a Python type annotation."""
    origin = get_origin(param_type)

    if origin is Union:
        args = get_args(param_type)
        blank_args = [arg for arg in args if arg is not type(None)]
        if blank_args:
            return type_to_click_info(blank_args[0])

    if str(param_type).startswith("typing.Literal"):
        return click.Choice([str(a) for a in get_args(param_type)]), False
    if origin in (list, List, tuple, Tuple):
        return click.STRING, True
    if param_type is bool:
        return click.BOOL, False
    if param_type is int:
        return click.INT, False
    if param_type is float:
        return click.FLOAT, False
    return click.STRING, False  # Default to STRING for flexibility
