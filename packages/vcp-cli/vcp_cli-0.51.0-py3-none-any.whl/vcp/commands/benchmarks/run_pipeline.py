from __future__ import annotations

import logging
import shutil
from pathlib import Path

from czbenchmarks.datasets import Dataset
from czbenchmarks.metrics.types import MetricResult

from vcp.commands.benchmarks.specs import (
    DatasetSpec,
    UserDatasetSpec,
)

from .run_task import run_task
from .specs import BenchmarkRunSpec
from .utils import (
    CLIError,
    DockerRunner,
    get_cell_representation_cache_dir,
    handle_cli_error,
    load_from_cache,
    save_to_cache,
)

logger = logging.getLogger(__name__)


def load_czbenchmarks_dataset(dataset_key: str) -> Dataset:
    """Load a dataset using czbenchmarks and provide user feedback."""
    try:
        logger.info(f"Loading dataset '{dataset_key}'...")

        from czbenchmarks.datasets.utils import (  # noqa: PLC0415
            load_dataset as czb_load_dataset,  # noqa: PLC0415
        )

        dataset = czb_load_dataset(dataset_key)
        logger.info(
            f"  -> Dataset loaded: {dataset.adata.n_obs} cells, {dataset.adata.n_vars} genes"
        )
        return dataset
    except KeyError:
        handle_cli_error(CLIError(f"Dataset key '{dataset_key}' is not valid."))


def load_datasets(spec: BenchmarkRunSpec) -> list[Dataset]:
    """Load multiple datasets based on the BenchmarkRunSpec."""
    datasets = []

    for dataset_spec in spec.datasets:
        if dataset_spec.key:
            datasets.append(load_czbenchmarks_dataset(dataset_spec.key))
        elif dataset_spec.user_dataset:
            try:
                dataset = dataset_spec.user_dataset.load()
                datasets.append(dataset)
            except KeyError as e:
                missing_key = str(e).strip("'")
                handle_cli_error(
                    CLIError(
                        f"Missing required key '{missing_key}' in user dataset specification. "
                        f"Required keys: dataset_class, organism, path"
                    )
                )

    if not datasets:
        handle_cli_error(
            CLIError("Either --dataset-key or --user-dataset must be specified.")
        )

    return datasets


class CellRepresentationPipeline:
    """Pipeline for running benchmarks using precomputed cell representations."""

    def run(self, spec: BenchmarkRunSpec) -> list[MetricResult]:
        """Execute the benchmarking pipeline using precomputed cell representations."""

        logger.info(f"Starting benchmark: {spec.task_key}")

        datasets = load_datasets(spec)

        if not spec.cell_representations and not spec.run_baseline:
            handle_cli_error(CLIError("No cell representation specified."))

        embeddings = []
        for cr_path in spec.cell_representations:
            if isinstance(cr_path, str) and cr_path.startswith("@"):
                embeddings.append(cr_path)
            else:
                from numpy import load  # noqa: PLC0415

                embeddings.append(load(Path(cr_path)))

        if len(embeddings) == 0 and spec.run_baseline:
            cell_repr_input = None
        elif len(embeddings) == 1:
            cell_repr_input = embeddings[0]
        else:
            cell_repr_input = embeddings

        if len(datasets) == 1:
            task_params = spec.task_inputs or {}

            results = run_task(
                spec.task_key,
                adata_input=datasets[0],
                cell_representation_input=cell_repr_input,
                run_baseline=spec.run_baseline,
                baseline_params=spec.baseline_args,
                task_params=task_params,
                random_seed=spec.random_seed,
            )
        else:
            task_params = spec.task_inputs or {}

            results = run_task(
                spec.task_key,
                adata_input=datasets,
                cell_representation_input=cell_repr_input,
                run_baseline=spec.run_baseline,
                baseline_params=spec.baseline_args,
                task_params=task_params,
                random_seed=spec.random_seed,
            )

        return results


class FullBenchmarkPipeline:
    """Pipeline for running a full benchmark, including model inference and evaluation."""

    def run(self, spec: BenchmarkRunSpec) -> list[MetricResult]:
        """Execute the full benchmarking pipeline from scratch."""

        logger.info(f"Running benchmark: {spec}")

        datasets = load_datasets(spec)

        all_embeddings = []

        for dataset_spec in spec.datasets:
            embeddings = None
            if not spec.no_cache:
                try:
                    embeddings = load_from_cache(
                        spec.model_details.uid,
                        [dataset_spec.uid],
                        None,
                        "embeddings",
                    )
                    logger.info(
                        f"Reusing cached embeddings for dataset {dataset_spec}."
                    )
                except FileNotFoundError:
                    pass

            if embeddings is None:
                assert (
                    isinstance(dataset_spec.user_dataset.path, Path)
                    if dataset_spec.user_dataset
                    else True
                )
                self._run_model_pipeline(spec, dataset_spec)
                assert (
                    isinstance(dataset_spec.user_dataset.path, Path)
                    if dataset_spec.user_dataset
                    else True
                )

                embeddings_cache_path = (
                    get_cell_representation_cache_dir(
                        spec.model_details.uid, [dataset_spec.uid]
                    )
                    / "task_input"
                    / "embeddings.npy"
                )
                if embeddings_cache_path.exists():
                    from numpy import load  # noqa: PLC0415

                    embeddings = load(embeddings_cache_path)
                    if not spec.no_cache:
                        save_to_cache(
                            spec.model_details.uid,
                            [dataset_spec.uid],
                            None,
                            embeddings,
                            "embeddings",
                        )
                else:
                    raise CLIError(
                        f"Embeddings file not found at {embeddings_cache_path}. Pipeline may have failed."
                    )

            all_embeddings.append(embeddings)

        if len(datasets) == 1:
            task_params = spec.task_inputs or {}

            results = run_task(
                spec.task_key,
                adata_input=datasets[0],
                cell_representation_input=all_embeddings[0],
                run_baseline=spec.run_baseline,
                baseline_params=spec.baseline_args,
                task_params=task_params,
                random_seed=spec.random_seed,
            )
        else:
            task_params = spec.task_inputs or {}

            results = run_task(
                spec.task_key,
                adata_input=datasets,
                cell_representation_input=all_embeddings,
                run_baseline=spec.run_baseline,
                baseline_params=spec.baseline_args,
                task_params=task_params,
                random_seed=spec.random_seed,
            )

        return results

    def _run_model_pipeline(
        self, spec: BenchmarkRunSpec, dataset_spec: DatasetSpec
    ) -> None:
        """
        Run the model pipeline to generate cell embeddings for the given dataset.

        Executes the preprocessing, inference, and postprocessing steps using Docker containers
        as specified in the model registry. Ensures that the final embeddings file is created.

        Args:
            spec (BenchmarkRunSpec): The benchmark specification.
            dataset (Dataset): The dataset to process.

        Raises:
            CLIError: If any pipeline step fails or required files are missing.
        """

        run_cache_dir = get_cell_representation_cache_dir(
            spec.model_details.uid, [dataset_spec.uid]
        )
        final_embeddings_path = run_cache_dir / "task_input" / "embeddings.npy"

        self._run_preprocess(
            spec.model_details.adapter_image, run_cache_dir, dataset_spec
        )
        self._run_inference(spec.model_details.model_image, run_cache_dir)
        self._run_postprocess(spec.model_details.adapter_image, run_cache_dir)

        if not final_embeddings_path.exists():
            raise CLIError(
                f"Postprocessing failed: Expected embeddings file {final_embeddings_path} was not created. "
                f"Check adapter configuration and Docker logs."
            )

    def _run_preprocess_docker_with_user_dataset(
        self,
        adapter_image: str,
        model_input_dir: Path,
        user_dataset_spec: UserDatasetSpec,
    ):
        """Execute Docker preprocessing step with user dataset."""
        DockerRunner(use_gpu=self.spec.use_gpu).run(
            image=adapter_image,
            mounts=[(str(model_input_dir), "/model_input", "rw")],
            cmd_args=[
                "preprocess",
                "--dataset-spec",
                user_dataset_spec.model_dump_json(),
            ],
            description="Preprocessing",
        )

    def _run_preprocess_docker_with_dataset_key(
        self, adapter_image: str, model_input_dir: Path, dataset_key: str
    ):
        """Execute Docker preprocessing step with dataset key."""
        DockerRunner(use_gpu=self.spec.use_gpu).run(
            image=adapter_image,
            mounts=[(str(model_input_dir), "/model_input", "rw")],
            cmd_args=["preprocess", "--dataset-name", dataset_key],
            description="Preprocessing",
        )

    # TODO: We should move to only support UserDatasetSpec and deprecate dataset_key. The UserDatasetSpec should become just DatasetSpec.
    # This will simplify handling of user datasets vs czbenchmarks datasets.
    # This will also involve changing model adapters to only accept DatasetSpecs. The fetching of a remote dataset would be handled by the CLI,
    # allowing for dataset caching to be managed entirely by the CLI (the adapter Docker image is currently downloading a czb dataset witout caching it).
    # Will require a fix to DatasetSpec to allow extra attributes.
    def _run_preprocess(
        self, adapter_image: str, run_cache_dir: Path, dataset: DatasetSpec
    ):
        """Run the preprocessing step of the model pipeline. Must specify either dataset_key or user_dataset."""
        logger.info("1. Running Preprocessing Step...")

        model_input_dir = run_cache_dir / "model_input"
        model_input_dir.mkdir(exist_ok=True)

        if dataset.user_dataset is not None:
            dataset_file_path = dataset.user_dataset.path.expanduser().resolve()
            shutil.copy(dataset_file_path, model_input_dir)

            user_dataset = dataset.user_dataset.model_copy()
            user_dataset.path = f"/model_input/{dataset_file_path.name}"

            logger.info(f"Preprocessing with user dataset: {dataset_file_path.name}")
            logger.debug(
                f"Executing Docker command: adapter_image={adapter_image}, "
                f"mounts=[{str(model_input_dir)}, '/model_input', 'rw'], "
                f"cmd_args=['preprocess', '--dataset-spec', {user_dataset.model_dump_json()}], "
                "description='Preprocessing'"
            )
            try:
                self._run_preprocess_docker_with_user_dataset(
                    adapter_image, model_input_dir, user_dataset
                )
            except Exception as e:
                handle_cli_error(
                    CLIError(
                        f"Docker execution failed during preprocessing with user dataset: {e}"
                    )
                )
        else:  # czb dataset
            logger.info(f"Running preprocessing with dataset: {dataset.key}")
            logger.debug(
                f"Executing Docker command: adapter_image={adapter_image}, "
                f"mounts=[{str(model_input_dir)}, '/model_input', 'rw'], "
                f"cmd_args=['preprocess', '--dataset-name', {dataset.key}], "
                f"description='Preprocessing'"
            )
            try:
                self._run_preprocess_docker_with_dataset_key(
                    adapter_image, model_input_dir, dataset.key
                )
            except Exception as e:
                handle_cli_error(
                    CLIError(
                        f"Docker execution failed during preprocessing with dataset '{dataset.key}': {e}"
                    )
                )

    def _run_inference_docker(
        self, adapter_image: str, model_input_dir: Path, model_output_dir: Path
    ):
        """Execute Docker inference step."""
        self.docker.run(
            image=adapter_image,
            mounts=[
                (str(model_input_dir), "/model_input", "ro"),
                (str(model_output_dir), "/model_output", "rw"),
            ],
            cmd_args=[],
            description="Inference",
        )

    def _run_inference(self, model_image: str, run_cache_dir: Path):
        """Run the model inference step of the pipeline."""
        logger.info("2. Running Model Inference Step...")

        model_input_dir = run_cache_dir / "model_input"
        model_output_dir = run_cache_dir / "model_output"
        model_output_dir.mkdir(exist_ok=True)

        input_json_path = model_input_dir / "input.json"
        if not input_json_path.exists():
            raise CLIError(
                f"input.json not found in {model_input_dir}. Preprocessing may have failed."
            )

        self._run_inference_docker(model_image, model_input_dir, model_output_dir)

        output_json_path = model_output_dir / "output.json"
        if not output_json_path.exists():
            raise CLIError(
                f"Model inference failed: Expected output file {output_json_path} was not created. "
                f"Check model configuration and Docker logs."
            )

    def _run_postprocess_docker(
        self, adapter_image: str, model_output_dir: Path, task_input_dir: Path
    ):
        """Execute Docker postprocessing step."""
        self.docker.run(
            image=adapter_image,
            mounts=[
                (str(model_output_dir), "/model_output", "ro"),
                (str(task_input_dir), "/task_input", "rw"),
            ],
            cmd_args=["postprocess"],
            description="Postprocessing",
        )

    def _run_postprocess(self, adapter_image: str, run_cache_dir: Path):
        """Run the postprocessing step of the model pipeline."""
        logger.info("3. Running Postprocessing Step...")

        model_output_dir = run_cache_dir / "model_output"
        task_input_dir = run_cache_dir / "task_input"
        task_input_dir.mkdir(exist_ok=True)

        output_json_path = model_output_dir / "output.json"
        if not output_json_path.exists():
            raise CLIError(
                f"output.json not found in {model_output_dir}. Model inference may have failed."
            )

        self._run_postprocess_docker(adapter_image, model_output_dir, task_input_dir)
