import hashlib
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from czbenchmarks.datasets.types import Organism
from pydantic import BaseModel, field_validator

from .utils import CLIError, handle_cli_error

if TYPE_CHECKING:
    from czbenchmarks.datasets import Dataset

logger = logging.getLogger(__name__)


class BenchmarkModelDetails(BaseModel):
    """
    Benchmark model configuration and capabilities.

    Detailed information about a model's the Docker images required to run
    benchmarks with this model and its supported datasets and tasks.

    Attributes:
        key: Unique identifier for this model
        model_image: Docker image containing the actual model
        adapter_image: Docker image for the model adapter/wrapper
        supported_datasets: List of dataset keys this model can work with
        supported_tasks: List of task types this model can perform
    """

    model_config = {"protected_namespaces": ()}

    key: Optional[str] = None
    model_image: Optional[str] = None
    adapter_image: Optional[str] = None
    supported_datasets: list[str] = []
    supported_tasks: list[str] = []

    def is_valid(self) -> bool:
        """
        Check if this model configuration is valid.

        A valid model configuration must have both a model image and an adapter image specified.
        Note that the model key is optional and may have been used to look up this configuration.

        Returns:
            True if both model_image and adapter_image are set; False otherwise.
        """
        return bool(self.model_image and self.adapter_image)

    @property
    def uid(self) -> str:
        """
        Get a unique identifier for this model configuration, using the key, model_image, and adapter_image.

        Returns:
            The model key if available; otherwise, the model Docker image.
            If neither is set, returns "unknown-model".
        """

        # TODO: Use the Docker image ID, rather than a hash of the image name
        def _short_hash(s):
            if not s:
                return "none"
            return hashlib.sha256(s.encode()).hexdigest()[:8]

        key_part = self.key if self.key else "user-model"
        model_hash = _short_hash(self.model_image)
        adapter_hash = _short_hash(self.adapter_image)
        return f"{key_part}-{model_hash}-{adapter_hash}"


def _to_organism_enum(s: str) -> Organism:
    """Convert a string to an Organism enum, case-insensitive."""
    user_organism = s.strip().lower()
    for organism in Organism:
        if user_organism == organism._name_.lower():
            return organism
        if user_organism == organism.value[0].lower():
            return organism
        if organism.value[1] and user_organism == organism.value[1].lower():
            return organism

    valid_names = ", ".join([org._name_ for org in Organism])
    raise ValueError(
        f"Cannot convert '{s}' to Organism enum. Valid values are: {valid_names}"
    )


def _align_labels_to_organisms(
    labels: List[str], organisms: List[str], default_label: str = "cell_type"
) -> Tuple[List[str], List[Organism]]:
    """Align and process labels and organisms for cross-species tasks."""
    num_organisms = len(organisms)
    labels = list(labels) if labels else []

    if len(labels) < num_organisms:
        labels += [default_label] * (num_organisms - len(labels))
    if len(labels) > num_organisms:
        labels = labels[:num_organisms]

    processed_labels = []
    for idx, label in enumerate(labels):
        if isinstance(label, str) and label.startswith("@"):
            parts = label[1:].split(":", 1)
            if parts[0].isdigit():
                processed_labels.append(label)
            else:
                ref = f"@{idx}:{label[1:]}"
                processed_labels.append(ref)
        else:
            ref = f"@{idx}:obs:{label}"
            processed_labels.append(ref)

    organisms_list = []
    for organism_str in organisms:
        org_name = organism_str.split(":", 1)[0]
        org_enum = _to_organism_enum(org_name)
        organisms_list.append(org_enum)

    return processed_labels, organisms_list


def _file_hash(path: Path) -> str:
    """Generate a robust, unique key for a file using its path, size, and modification time."""
    resolved_path = path.resolve()
    stat_info = resolved_path.stat()
    payload = f"{resolved_path}|{stat_info.st_size}|{int(stat_info.st_mtime)}".encode()
    return hashlib.sha256(payload).hexdigest()[:12]


# FIXME: Should allow for extra attributes in UserDatasetSpec
class UserDatasetSpec(BaseModel):
    """Pydantic model for user-provided dataset configuration."""

    dataset_class: str
    organism: str
    path: Path

    @field_validator("path", mode="before")
    @classmethod
    def validate_path_exists_and_expand(cls, v):
        p = Path(v).expanduser()
        if not p.exists():
            handle_cli_error(CLIError(f"User dataset file not found: {p}"))
        return p

    def load(self) -> "Dataset":
        """Load the user dataset with organism conversion."""
        logger.info(f"Loading user dataset from '{self.path}'...")
        organism = self.organism

        if isinstance(organism, str):
            if organism.startswith("Organism."):
                organism = organism.split(".", 1)[1]
            try:
                organism = _to_organism_enum(organism)
            except ValueError as e:
                raise ValueError(f"Invalid organism: {organism}") from e

        from czbenchmarks.datasets.utils import (  # noqa: PLC0415
            load_custom_dataset,
        )

        dataset_name = f"user_dataset_{Path(self.path).stem}"

        logger.debug(
            f"Loading user dataset: dataset_name={dataset_name}, dataset_class={self.dataset_class}, organism={organism}, path={self.path}"
        )
        dataset = load_custom_dataset(
            dataset_name=dataset_name,
            custom_dataset_kwargs={
                "_target_": self.dataset_class,
                "organism": organism,
                "path": str(self.path),
            },
        )
        logger.info(
            f"  -> User dataset loaded: {dataset.adata.n_obs} cells, {dataset.adata.n_vars} genes"
        )
        return dataset

    model_config = {"extra": "forbid", "protected_namespaces": ()}


class DatasetSpec(BaseModel):
    """Pydantic model for datasets that are either czbenchmark-registered datasets or user-provided."""

    key: Optional[str] = None
    user_dataset: Optional[UserDatasetSpec] = None

    @property
    def uid(self) -> str:
        """Get a unique identifier for this dataset specification."""
        if self.key is not None:
            return self.key
        elif self.user_dataset is not None:
            return _file_hash(self.user_dataset.path)
        else:
            handle_cli_error(
                CLIError(
                    "DatasetSpec must have either 'key' or 'user_dataset' defined."
                )
            )
            return "invalid-dataset"


class BenchmarkRunSpec(BaseModel):
    """
    Complete specification for running a benchmark evaluation.

    Defines all parameters needed to execute a benchmark including model
    selection, dataset configuration, task specification, and baseline
    options. Supports both VCP models and precomputed cell representations,
    as well as both czbenchmarks datasets and user-provided datasets.
    """

    model_details: Optional[BenchmarkModelDetails] = None
    datasets: List[DatasetSpec] = []
    task_key: str
    cell_representations: List[str] = []
    run_baseline: bool = False
    baseline_args: Optional[Dict[str, Any]] = None
    task_inputs: Optional[Dict[str, Any]] = None
    random_seed: Optional[int] = None
    no_cache: bool = False
    use_gpu: bool = True

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "protected_namespaces": (),
    }

    @staticmethod
    def _validate_multi_dataset_requirements(
        model_key_or_image: Optional[str],
        num_datasets: int,
        num_cell_representations: int,
        compute_baseline: bool,
    ) -> None:
        """Validate requirements for multi-dataset tasks.

        Multi-dataset tasks require:
        1. Baseline-only mode, OR
        2. 2+ explicit cell representations, OR
        3. Model with 2+ datasets (model generates cell representations)

        Additionally validates that cell representation counts match dataset counts when applicable.
        """
        is_baseline_only = compute_baseline and num_cell_representations == 0

        has_model_key = model_key_or_image is not None
        has_sufficient_cell_reps = num_cell_representations >= 2
        has_model_with_datasets = has_model_key and num_datasets >= 2

        if not (
            is_baseline_only or has_sufficient_cell_reps or has_model_with_datasets
        ):
            handle_cli_error(
                CLIError(
                    "Multi-dataset tasks require either: (1) at least two cell representations "
                    "(--cell-representation), OR (2) a model (--model-key) with at least two datasets."
                )
            )

        # Validate cell representation counts match dataset counts when using explicit representations
        if num_cell_representations > 0 and num_datasets != num_cell_representations:
            handle_cli_error(
                CLIError(
                    "The number of datasets must match the number of cell representations."
                )
            )

    @staticmethod
    def _align_cross_species_parameters(task_kwargs: Dict[str, Any]) -> None:
        """Align organism and label parameters for cross-species tasks.

        Modifies task_kwargs in place to:
        - Convert organism strings to Organism enums
        - Align labels to match the number of organisms
        - Add dataset indices to label references (e.g., @obs:cell_type -> @0:obs:cell_type)
        """
        org_key = None
        for possible_key in ["organism_list", "organisms"]:
            if possible_key in task_kwargs:
                org_key = possible_key
                break

        if not org_key:
            return

        organisms = task_kwargs[org_key]
        if not isinstance(organisms, list):
            organisms = [organisms]

        label_key = None
        for key in ["labels", "input_labels"]:
            if key in task_kwargs:
                label_key = key
                break

        labels = task_kwargs.get(label_key, []) if label_key else []
        if not isinstance(labels, list):
            labels = [labels]

        try:
            aligned_labels, organism_enums = _align_labels_to_organisms(
                labels, organisms
            )
            if label_key:
                task_kwargs[label_key] = aligned_labels
            task_kwargs[org_key] = organism_enums

            if "sample_ids" in task_kwargs:
                sample_ids = task_kwargs["sample_ids"]
                if not isinstance(sample_ids, list):
                    sample_ids = [sample_ids]
                aligned_sample_ids, _ = _align_labels_to_organisms(
                    sample_ids, organisms, default_label="cell_type"
                )
                task_kwargs["sample_ids"] = aligned_sample_ids
        except ValueError as e:
            handle_cli_error(CLIError(f"Organism resolution failed: {e}"))

    # TODO: convert to a model_post_init() on the pydantic model
    def _handle_benchmark_key(self, benchmark_key: str) -> None:
        """
        Resolve benchmark key into individual model, dataset, and task components.

        Fetches the benchmark record from the API and populates the model_key,
        czb_dataset_key, and task_key fields based on the benchmark configuration.

        Args:
            benchmark_key (str): The benchmark key to resolve.

        Raises:
            CLIError: If benchmark key is invalid or resolution fails.
        """

        try:
            from .api import fetch_benchmark_by_key  # noqa: PLC0415

            benchmark_record = fetch_benchmark_by_key(benchmark_key)
            self.model_details.key = (
                self.model_details.key or benchmark_record.model_key
            )
            self.czb_dataset_keys = self.czb_dataset_keys or (
                benchmark_record.dataset_keys if benchmark_record.dataset_keys else None
            )
            self.task_key = self.task_key or benchmark_record.task_key

            if not self.czb_dataset_key:
                handle_cli_error(
                    CLIError(f"No dataset found for benchmark key '{benchmark_key}'")
                )

        except Exception as e:
            handle_cli_error(
                CLIError(f"Failed to resolve benchmark key '{benchmark_key}': {e}")
            )

    def _parse_dynamic_params(self, value: Any) -> Any:
        """Parse dynamic CLI parameter values for task/baseline params."""
        if isinstance(value, str) and value.startswith("@"):
            return value
        if isinstance(value, str):
            try:
                loaded = json.loads(value)
                return loaded
            except Exception:
                return value
        return value

    def _normalize_cli_param_values(
        self, raw: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Normalize CLI parameter values for task/baseline params."""
        if not raw:
            return {}
        out: Dict[str, Any] = {}
        for k, v in raw.items():
            if isinstance(v, tuple):
                continue
            else:
                parsed = self._parse_dynamic_params(v)
                out[k] = parsed
        return out

    @property
    def dataset_uids(self) -> List[str]:
        """Get the dataset unique identifiers for this benchmark run."""
        return [d.uid for d in self.datasets]
