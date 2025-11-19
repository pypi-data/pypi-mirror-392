import json
import logging
from typing import Optional

import click
from rich.console import Console
from rich.console import Console as WideConsole

from .api import fetch_benchmark_by_key, fetch_benchmarks_list
from .utils import (
    BENCHMARK_BASE_COLUMNS,
    CLIError,
    format_as_table,
    handle_cli_error,
    validate_benchmark_filters,
)

logger = logging.getLogger(__name__)
console = Console()


@click.command(name="list", context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-b",
    "--benchmark-key",
    help="Retrieve by benchmark key. Mutually-exclusive with filter options.",
)
@click.option(
    "-m",
    "--model-filter",
    help="Filter by model key (substring match with '*' wildcards, e.g. 'scvi*v1').",
)
@click.option(
    "-d",
    "--dataset-filter",
    help="Filter by dataset key (substring match with '*' wildcards, e.g. 'tsv2*liver').",
)
@click.option(
    "-t",
    "--task-filter",
    help="Filter by task key (substring match with '*' wildcards, e.g. 'label*pred').",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option(
    "--fit/--full",
    default=True,
    help="Column display for table format (default: fit). Use --full to show full column content; pair with a pager like 'less -S' for horizontal scrolling. Only applies to --format=table.",
)
# TODO: Consider --debug if this is just showing debug log output (https://czi.atlassian.net/browse/VC-4024)
@click.pass_context
def list_command(
    ctx: click.Context,
    benchmark_key: Optional[str],
    dataset_filter: Optional[str],
    model_filter: Optional[str],
    task_filter: Optional[str],
    format: str,
    fit: bool,
) -> None:
    """
    List available model, dataset and task benchmark combinations. You can filter results by dataset, model, or task using glob patterns.
    """

    try:
        validate_benchmark_filters(model_filter, dataset_filter, task_filter)

        if benchmark_key:
            benchmark_record = fetch_benchmark_by_key(benchmark_key)
            benchmarks = [benchmark_record]
        else:
            benchmarks = fetch_benchmarks_list(
                model_filter=model_filter,
                dataset_filter=dataset_filter,
                task_filter=task_filter,
            )

        if not benchmarks:
            if format == "json":
                console.print("[]", markup=False)
            else:
                console.print("No benchmarks found matching the specified filters.")
            return

        api_rows = []
        for benchmark in benchmarks:
            benchmark_dict = benchmark.model_dump()
            api_rows.append({
                "benchmark_key": benchmark_dict["benchmark_key"],
                "model_key": benchmark_dict["model_key"],
                "model_name": benchmark_dict["model_name_display"],
                "dataset_keys": ", ".join(benchmark_dict["dataset_keys"]),
                "dataset_names": ", ".join(benchmark_dict["dataset_names_display"]),
                "task_key": benchmark_dict["task_key"],
                "task_name": benchmark_dict["task_name_display"],
            })

        if format == "json":
            console.print(json.dumps(api_rows, indent=2))
        else:
            # Use wide console for --full to allow full column values
            # With --fit (default), use normal console with max_width constraints
            if not fit:
                wide_console = WideConsole(width=500)
                wide_console.print(
                    format_as_table(
                        api_rows, table_type=BENCHMARK_BASE_COLUMNS, wrap=fit
                    )
                )
            else:
                console.print(
                    format_as_table(
                        api_rows, table_type=BENCHMARK_BASE_COLUMNS, wrap=fit
                    )
                )

    except CLIError as e:
        handle_cli_error(e)
