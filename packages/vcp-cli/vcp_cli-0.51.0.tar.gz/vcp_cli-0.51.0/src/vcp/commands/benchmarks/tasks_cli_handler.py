import json
import logging
from typing import Any, List

import click

from vcp.commands.benchmarks.api import fetch_model_details
from vcp.commands.benchmarks.specs import (
    BenchmarkModelDetails,
    BenchmarkRunSpec,
    DatasetSpec,
    UserDatasetSpec,
)

from .utils import CLIError, handle_cli_error, type_to_click_info

logger = logging.getLogger(__name__)


ANNDATA_REFERENCE_TASK_PARAMS = {
    "labels": "@obs:cell_type",
    "input_labels": "@obs:cell_type",
    "batch_labels": "@obs:batch",
    "batch_column": "@obs:batch",
    "sample_ids": None,
    "obs": "@obs",
    "var": "@var",
    "use_rep": "X",
    "obs_index": "@obs_index",
    "var_index": "@var_index",
}


def _get_param_help_message(
    param_name: str,
    p_info,
    is_multiple: bool = False,
) -> str:
    """Get a user-friendly help message for a task parameter."""
    help_text = p_info.help_text

    if not help_text:
        help_text = p_info.stringified_type

    if (
        help_text
        and p_info.default is not None
        and not isinstance(p_info.type, type)
        or (isinstance(p_info.type, type) and p_info.type is not bool)
    ):
        literal_choices = None

        if (
            hasattr(p_info.type, "__origin__")
            and p_info.type.__origin__.__name__ == "Literal"
        ):
            literal_choices = ", ".join(repr(v) for v in p_info.type.__args__)
        elif hasattr(p_info.type, "Literal"):
            literal_choices = p_info.type.Literal

        choices_str = f" [Options : {literal_choices}]" if literal_choices else ""
        result = f"{help_text} [Default: {p_info.default}] [Required: {p_info.required}]{choices_str}"
    else:
        result = f"{help_text}" if help_text else f"{p_info.stringified_type}"

    # Append note about multiple values for parameters that may be repeated
    if is_multiple:
        result += " Can be specified multiple times."

    # Append note about AnnData reference syntax for parameters that support it
    if param_name in ANNDATA_REFERENCE_TASK_PARAMS:
        example = ANNDATA_REFERENCE_TASK_PARAMS[param_name]
        result += f" Supports AnnData reference syntax (e.g. '{example}')."

    return result


def _get_smart_default(param_name: str, original_default: Any) -> Any:
    """Applies smart defaults that align with downstream normalization in specs.py."""
    smart_defaults = ANNDATA_REFERENCE_TASK_PARAMS

    if (
        original_default is None
        and param_name in smart_defaults
        and smart_defaults[param_name] is not None
    ):
        return smart_defaults[param_name]

    return original_default


def add_task_specific_options(task_key: str) -> List[click.Option]:
    """Generates CLI options for a given task's parameters with enhanced UX features."""
    from czbenchmarks.tasks.task import TASK_REGISTRY  # noqa: PLC0415

    info = TASK_REGISTRY.get_task_info(task_key)
    options: List[click.Option] = []
    TaskClass = TASK_REGISTRY.get_task_class(task_key)

    for name, p_info in info.task_params.items():
        param_type, is_multiple = type_to_click_info(p_info.type)

        help_text = _get_param_help_message(name, p_info, is_multiple=is_multiple)

        smart_default = _get_smart_default(name, p_info.default)
        cli_arg_name = f"--{name.replace('_', '-')}"

        if param_type is click.BOOL:
            options.append(
                click.Option(
                    [cli_arg_name],
                    is_flag=True,
                    default=bool(smart_default if smart_default is not None else False),
                    help=help_text,
                )
            )
        else:
            options.append(
                click.Option(
                    [cli_arg_name],
                    type=param_type,
                    multiple=is_multiple,
                    default=smart_default if not is_multiple else None,
                    help=help_text,
                )
            )

    baseline_model = getattr(TaskClass, "baseline_model", None)
    if baseline_model and baseline_model.__name__ != "NoBaselineInput":
        for name, p_info in info.baseline_params.items():
            cli_arg_name = f"--baseline-{name.replace('_', '-')}"
            param_type, is_multiple = type_to_click_info(p_info.type)

            help_text = _get_param_help_message(name, p_info, is_multiple=is_multiple)

            if param_type is click.BOOL:
                options.append(
                    click.Option(
                        [cli_arg_name],
                        is_flag=True,
                        default=None,
                        help=help_text,
                    )
                )
            else:
                options.append(
                    click.Option(
                        [cli_arg_name],
                        type=param_type,
                        multiple=is_multiple,
                        default=None,
                        help=help_text,
                    )
                )
    return options


def _normalize_anndata_column_ref_arg(name: str, value: Any) -> Any:
    """Normalize common label-like parameters to AnnData references."""
    # TODO: This list of cz-benchmarks task input param names is brittle and should at least make use of ANNDATA_REFERENCE_TASK_PARAMS, or some other central source of param metadata.
    label_like = {"labels", "input_labels", "batch_labels", "sample_ids"}

    if name not in label_like or not value:
        return value

    if isinstance(value, str):
        if not value.startswith("@"):
            return f"@obs:{value}"
        return value

    if isinstance(value, (list, tuple)):
        normalized = []
        for v in value:
            if isinstance(v, str) and not v.startswith("@"):
                normalized.append(f"@obs:{v}")
            else:
                normalized.append(v)
        return normalized

    return value


def parse_cli_args(args: dict) -> BenchmarkRunSpec:
    """Create a BenchmarkRunSpec from CLI arguments."""
    from czbenchmarks.tasks.task import TASK_REGISTRY  # noqa: PLC0415

    model_key = args.get("model_key")
    model_image = args.get("model_image")
    model_adapter_image = args.get("model_adapter_image")
    cell_reps = list(args.get("cell_representation", ()) or [])
    czb_dataset_keys = list(args.get("dataset_key", ()) or [])
    user_dataset_spec_jsons = list(args.get("user_dataset", ()) or [])
    task_key = args.get("task_key")

    if args.get("benchmark_key"):
        from .api import fetch_benchmark_by_key  # noqa: PLC0415

        benchmark_record = fetch_benchmark_by_key(args["benchmark_key"])
        model_key = model_key or benchmark_record.model_key
        czb_dataset_keys = czb_dataset_keys or (
            benchmark_record.dataset_keys if benchmark_record.dataset_keys else None
        )
        task_key = task_key or benchmark_record.task_key
        if not czb_dataset_keys:
            handle_cli_error(
                CLIError(
                    f"No dataset found for benchmark key '{args['benchmark_key']}'"
                )
            )

    if not task_key:
        handle_cli_error(
            CLIError("Task key is required. Use --help to see available tasks.")
        )

    try:
        task_info = TASK_REGISTRY.get_task_info(task_key)
    except ValueError as e:
        handle_cli_error(CLIError(f"Invalid task: {e}"))

    spec_data: dict[str, Any] = {
        "model_details": BenchmarkModelDetails(
            key=model_key,
            model_image=model_image,
            adapter_image=model_adapter_image,
        ),
        "datasets": [],
        "cell_representations": cell_reps,
        "task_key": task_key,
        "run_baseline": args.get("run_baseline", False),
    }

    for czb_dataset_key in czb_dataset_keys:
        spec_data["datasets"].append(DatasetSpec(key=czb_dataset_key))
    try:
        for user_dataset_spec_json in user_dataset_spec_jsons:
            spec_data["datasets"].append(
                DatasetSpec(
                    user_dataset=UserDatasetSpec(**json.loads(user_dataset_spec_json))
                )
            )
    except Exception as e:
        handle_cli_error(
            CLIError(f"Invalid user dataset {user_dataset_spec_json}: {e}")
        )

    task_kwargs = {}
    for param_name, param_info in task_info.task_params.items():
        if param_name in args and args[param_name] is not None:
            val = args[param_name]
        else:
            val = None

        if param_info.required and val is None:
            val = _get_smart_default(param_name, param_info.default)

            if val is None:
                handle_cli_error(
                    CLIError(
                        f"Missing required parameter for task '{task_key}': {param_name}"
                    )
                )

        if val is None:
            continue

        if isinstance(val, tuple):
            val = list(val)

        task_kwargs[param_name] = _normalize_anndata_column_ref_arg(param_name, val)

    spec_data["task_inputs"] = task_kwargs

    baseline_kwargs = {}
    for param_name, param_info in task_info.baseline_params.items():
        baseline_key = f"baseline_{param_name}"

        if baseline_key in args and args[baseline_key] is not None:
            val = args[baseline_key]
        else:
            val = None

        if param_info.required and val is None:
            handle_cli_error(
                CLIError(
                    f"Missing required parameter for baseline of task '{task_key}': {param_name}"
                )
            )

        if val is None:
            continue

        if isinstance(val, tuple):
            val = list(val)

        baseline_kwargs[param_name] = val

    if task_info.requires_multiple_datasets:
        BenchmarkRunSpec._validate_multi_dataset_requirements(
            model_key or model_image,
            len(spec_data["datasets"]),
            len(spec_data["cell_representations"]),
            args.get("compute_baseline", False),
        )
        BenchmarkRunSpec._align_cross_species_parameters(task_kwargs)

    if baseline_kwargs:
        spec_data["baseline_args"] = baseline_kwargs
        spec_data["run_baseline"] = True
    elif args.get("compute_baseline", False):
        spec_data["run_baseline"] = True

    if args.get("random_seed") is not None:
        spec_data["random_seed"] = args["random_seed"]

    spec_data["no_cache"] = args.get("no_cache", False)
    spec_data["use_gpu"] = args.get("use_gpu", True)

    spec = BenchmarkRunSpec(**spec_data)

    logger.debug(f"Parsed BenchmarkRunSpec from CLI args: {spec.model_dump()}")

    if spec.model_details.key:
        fetched_model_details = fetch_model_details(model_key)
        logger.debug(f"Fetched model details from registry: {fetched_model_details}")
        # use fetched model details images, but override with images explicitly provided as options
        spec.model_details = BenchmarkModelDetails(
            **(
                fetched_model_details.model_dump()
                | spec.model_details.model_dump(exclude_none=True, exclude_unset=True)
            )
        )

    logger.debug(f"Constructed BenchmarkRunSpec: {spec.model_dump()}")

    has_model_or_representation = (
        (spec.model_details.model_image and spec.model_details.adapter_image)
        or spec.cell_representations
        or spec.run_baseline
    ) is not None
    has_dataset = len(spec.datasets) > 0

    if not (has_model_or_representation and has_dataset and spec.task_key):
        handle_cli_error(
            CLIError(
                "Missing required arguments: model/cell_representation (or --compute-baseline), dataset/user-dataset. Use --help for details."
            )
        )

    logger.info(
        f"Selected benchmark run - "
        f"Model: {spec.model_details.uid}, "
        f"Datasets: {spec.datasets}, "
        f"Task: {spec.task_key}"
    )

    return spec
