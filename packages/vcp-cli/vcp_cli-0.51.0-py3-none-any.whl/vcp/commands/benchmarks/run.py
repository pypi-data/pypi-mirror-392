from __future__ import annotations

import importlib
import json
import logging
import resource
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

import click
from czbenchmarks.metrics.types import MetricResult
from czbenchmarks.tasks.task import TASK_REGISTRY
from rich.console import Console

from vcp import __version__ as vcp_version

from .run_pipeline import CellRepresentationPipeline, FullBenchmarkPipeline
from .specs import (
    BenchmarkRunSpec,
)
from .tasks_cli_handler import add_task_specific_options, parse_cli_args
from .utils import (
    CLIError,
    display_benchmark_results_table,
    get_first_sentence,
    handle_cli_error,
    load_from_cache,
    mutually_exclusive,
    save_to_cache,
)

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# Console for user-facing messages (stderr)
console = Console(stderr=True)


def _build_enriched_results(
    spec: BenchmarkRunSpec,
    metrics: List[MetricResult],
    runtime_metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Build enriched results with metadata. The returned dict can be safely serialized to JSON (i.e. no complex Python types or Pydantic models).

    Args:
        spec: The benchmark run specification
        metrics: Raw metrics from the task execution
        runtime_metrics: Runtime performance metrics

    Returns:
        Dictionary with enriched results including metadata that can be safely serialized to JSON.
    """
    czb_version = importlib.metadata.version("cz-benchmarks")

    # Serialize metrics and spec to JSON-serializable dicts
    # mode="json" converts enums to strings automatically
    json_serializable_metrics = [metric.model_dump(mode="json") for metric in metrics]
    # Serialize the BenchmarkRunSpec to dict that can be safely serialized to JSON
    # TODO: Once benchmarking models are integrated with the Models API, the `model_details` should include additional metadata for the model (version and variant info, e.g.)
    json_serializable_spec = spec.model_dump(mode="json")

    # Build the enriched results
    enriched_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vcp_cli_version": vcp_version,
        "czbenchmarks_version": czb_version,
        "run_specification": json_serializable_spec,
        "runtime_metrics": runtime_metrics,
        "result_metrics": json_serializable_metrics,
    }

    return enriched_results


def _execute_benchmark(
    spec: BenchmarkRunSpec, output_format: Literal["table", "json"], fit: bool = True
) -> None:
    """Core logic to initialize and run a benchmark pipeline from merged CLI arguments."""

    try:
        # Start timing
        start_time = time.time()
        # Determine cache key for results
        if spec.model_details.is_valid():
            cache_model_key = spec.model_details.uid
        elif spec.cell_representations:
            cache_model_key = "user-cell-repr"
        elif spec.run_baseline:
            cache_model_key = "baseline"
        else:
            cache_model_key = None

        # Try to load cached enriched results if caching is enabled
        enriched_results = None
        if not spec.no_cache and cache_model_key:
            try:
                enriched_results = load_from_cache(
                    cache_model_key,
                    spec.dataset_uids,
                    spec.task_key,
                    "results",
                    task_run_id=str(spec.random_seed)
                    if spec.random_seed is not None
                    else None,
                )
                logger.info("Reusing cached task results.")
            except FileNotFoundError:
                pass

        # If no cached results, run the pipeline
        if enriched_results is None:
            if spec.model_details.is_valid():
                _issue_model_compatibility_warnings(spec)
                pipeline = FullBenchmarkPipeline()
            else:
                pipeline = CellRepresentationPipeline()

            metrics = pipeline.run(spec)

            # Calculate runtime metrics
            elapsed_time = time.time() - start_time
            # ru_maxrss units differ by platform:
            # - macOS: bytes
            # - Linux: kilobytes
            max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                max_memory_mib = max_rss / (1024 * 1024)  # Bytes to MiB
            else:
                max_memory_mib = max_rss / 1024  # Kilobytes to MiB

            runtime_metrics = {
                "elapsed_time_secs": round(elapsed_time, 2),
                "max_memory_mib": round(max_memory_mib, 2),
            }

            # Build enriched results with metadata
            enriched_results = _build_enriched_results(spec, metrics, runtime_metrics)

            if cache_model_key:
                save_to_cache(
                    cache_model_key,
                    spec.dataset_uids,
                    spec.task_key,
                    enriched_results,
                    "results",
                    task_run_id=str(spec.random_seed)
                    if spec.random_seed is not None
                    else None,
                )

        # Print success message to stderr
        console.print("\n[green]Benchmark completed successfully![/green]")

        # Output results in requested format
        if output_format == "json":
            # Print JSON results to stdout (no formatting, pure JSON)
            print(json.dumps(enriched_results, indent=2, default=str))
        else:
            # Print table format using shared function
            display_benchmark_results_table(enriched_results, console, wrap=fit)

    except (click.UsageError, CLIError) as e:
        handle_cli_error(e)


def _add_common_task_options() -> List[click.Option]:
    """Returns the common options that should be added to all task subcommands."""
    return [
        click.Option(
            ["-m", "--model-key"],
            callback=mutually_exclusive(
                "benchmark_key", "cell_representation", "compute_baseline"
            ),
            # TODO: Update to use `vcp models list` when benchmark-able models are registered and list-able
            help="Model key (e.g. `SCVI-v1-homo_sapiens`; run `vcp benchmarks list` for available model keys).",
        ),
        click.Option(
            ["--model-image"],
            help="For development/testing purposes. Allows a custom model image to be specified that is not available in the model registry. Overrides the model image from the registry, if --model-key or --benchmark-key is provided.",
            hidden=True,
        ),
        click.Option(
            ["--model-adapter-image"],
            help="For development/testing purposes. Allows a custom model adapter image to be specified that is not available in the model registry. Overrides the model adapter image from the registry, if --model-key or --benchmark-key is provided.",
            hidden=True,
        ),
        click.Option(
            ["-d", "--dataset-key"],
            multiple=True,
            callback=mutually_exclusive("benchmark_key"),
            help="Dataset key from czbenchmarks datasets (e.g., `tsv2_blood`; run `czbenchmarks list datasets` for available dataset keys). Can be used multiple times.",
        ),
        click.Option(
            ["-u", "--user-dataset"],
            multiple=True,
            callback=mutually_exclusive("benchmark_key"),
            help='Path to a user-provided .h5ad file. Provide as a JSON string with keys: \'dataset_class\', \'organism\', and \'path\'. Example: \'{"dataset_class": "czbenchmarks.datasets.SingleCellLabeledDataset", "organism": "HUMAN", "path": "~/mydata.h5ad"}\'. Can be used multiple times.',
        ),
        click.Option(
            ["-c", "--cell-representation"],
            multiple=True,
            type=str,
            callback=mutually_exclusive(
                "benchmark_key", "model_key", "compute_baseline"
            ),
            help="Path to precomputed cell embeddings (.npy file) or AnnData reference (e.g., '@X', '@obsm:X_pca'). Can be used multiple times.",
        ),
        click.Option(
            ["-B", "--compute-baseline"],
            is_flag=True,
            default=False,
            callback=mutually_exclusive("model_key", "cell_representation"),
            help="Compute baseline for comparison. Cannot be used with --model-key or --cell-representation.",
        ),
        click.Option(
            ["-r", "--random-seed"],
            type=int,
            help="Set a random seed for reproducibility.",
        ),
        click.Option(
            ["-n", "--no-cache"],
            is_flag=True,
            help="Disable caching. Forces all steps to run from scratch.",
        ),
        click.Option(
            ["-f", "--format"],
            type=click.Choice(["table", "json"]),
            default="table",
            help="Output format (default: table).",
        ),
        click.Option(
            ["--fit/--full"],
            default=True,
            help="Column display for table format (default: fit). Use --full to show full column content; pair with a pager like 'less -S' for horizontal scrolling. Only applies to --format=table.",
        ),
        click.Option(
            ["--use-gpu/--no-use-gpu"],
            default=True,
            help="Enable GPU support for model inference (default: enabled).",
        ),
    ]


@click.group(
    name="run",
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    help="""Run a benchmark task on a cell representation, which can be provided in one of the following ways:
1) generate a cell representation by performing model inference on a specified dataset, using a specified model, or
2) specify use a previously-computed cell representation (skips performing model inference), or
3) have the task generate a baseline cell representation that is computed from a specified dataset.

Use `vcp benchmarks run <task> --help` to see all available options for that task.
""",
)
@click.option(
    "-b",
    "--benchmark-key",
    help="Run a benchmark using the model, dataset, and task of a VCP-published benchmark (run `vcp benchmarks list` for available benchmark keys).",
)
@click.pass_context
def run_command(ctx, benchmark_key):
    """The main 'run' command group for benchmark tasks."""
    ctx.ensure_object(dict)

    # If benchmark_key is provided and no subcommand is invoked, run the benchmark directly
    if benchmark_key:
        assert ctx.invoked_subcommand is None
        run_spec = parse_cli_args({"benchmark_key": benchmark_key})
        _execute_benchmark(
            run_spec,
            output_format=ctx.params.get("format", "table"),
            fit=ctx.params.get("fit", True),
        )


def _add_task_subcommand(task_key: str) -> click.Command:
    """Factory that generates a click.Command for a given task."""
    info = TASK_REGISTRY.get_task_info(task_key)

    @click.pass_context
    def _task_callback(ctx: click.Context, **all_kwargs):
        """Executed when a user runs `vcp benchmarks run <task>`."""
        all_args = {"task_key": task_key}
        all_args.update(all_kwargs)
        run_spec = parse_cli_args(all_args)
        _execute_benchmark(
            run_spec,
            output_format=ctx.params.get("format", "table"),
            fit=ctx.params.get("fit", True),
        )

    task_command = click.Command(
        name=task_key,
        callback=_task_callback,
        short_help=get_first_sentence(info.description),
        help=f"""{info.description}

Specify one of --model-key, --cell-representation, or --compute-baseline to generate or provide the benchmarked cell representation to the task.

Specify one of --dataset-key or --user-dataset to specify the associated dataset file(s) that contain ground truth data needed by the task for evaluation.
These dataset options may be specified multiple times for multi-dataset tasks.

If --model-key is specified, dataset(s) will provide the input data to the model.
If --compute-baseline is specified, dataset(s) will be used to compute a baseline cell representation.
If --cell-representation is specified, a dataset is only used if task-specific option arguments reference ground truth data within the dataset.
""",
        context_settings={
            "help_option_names": ["-h", "--help"],
            "ignore_unknown_options": True,
        },
        add_help_option=True,
    )

    for option in _add_common_task_options():
        task_command.params.append(option)

    for option in add_task_specific_options(task_key):
        task_command.params.append(option)

    return task_command


for task_name in TASK_REGISTRY.list_tasks():
    run_command.add_command(_add_task_subcommand(task_name))


def _issue_model_compatibility_warnings(spec: BenchmarkRunSpec) -> bool:
    """
    Validate that a benchmark run specification is compatible with the model configuration.

    Args:
        spec: The benchmark run specification to validate

    Returns:
        True if the specification is valid

    Raises:
        CLIError: If validation fails for any reason
    """

    has_unsupported_dataset_keys = [
        dataset_spec.key is None
        or dataset_spec.key in spec.model_details.supported_datasets
        for dataset_spec in spec.datasets
    ]
    if has_unsupported_dataset_keys:
        console.print(
            f"[yellow]Warning: Model is being used with an unsupported dataset and may fail. "
            f"Supported datasets: {spec.model_details.supported_datasets!r}[/yellow]"
        )

    if spec.task_key not in spec.model_details.supported_tasks:
        console.print(
            f"[yellow]Warning: Model output is being for an unsupported task {spec.task_key!r}; the task may fail to work with the model output."
            f"Supported tasks: {spec.model_details.supported_tasks!r}[/yellow]"
        )

    return True
