"""Unified task execution module for benchmarking tasks."""

import logging
from typing import Any, Dict, List, Union

import numpy as np
import scipy.sparse as sp
from anndata import AnnData
from czbenchmarks.metrics.types import MetricResult
from czbenchmarks.tasks import TASK_REGISTRY
from czbenchmarks.tasks.types import CellRepresentation

from .resolve_references import resolve_anndata_references

logger = logging.getLogger(__name__)
RANDOM_SEED = 42


def _ensure_dense_matrix(cell_rep: Union[CellRepresentation, np.ndarray]) -> np.ndarray:
    if sp.issparse(cell_rep):
        return cell_rep.toarray()
    return cell_rep


def run_task(
    task_name: str,
    *,
    adata_input: Union[AnnData, List[AnnData]],
    cell_representation_input: Union[
        str, CellRepresentation, List[Union[str, CellRepresentation]]
    ],
    run_baseline: bool = False,
    baseline_params: Dict[str, Any] | None = None,
    task_params: Dict[str, Any] | None = None,
    random_seed: int = RANDOM_SEED,
) -> List[MetricResult]:
    """Unified task runner for single and multi-dataset benchmarks."""

    if random_seed is None:
        random_seed = RANDOM_SEED

    logger.info(f"Running task: {task_name}")

    TaskClass = TASK_REGISTRY.get_task_class(task_name)
    task_instance = TaskClass(random_seed=random_seed)
    is_multi_dataset_task = getattr(task_instance, "requires_multiple_datasets", False)

    if isinstance(adata_input, list):
        anndata_objects = [
            dataset.adata if hasattr(dataset, "adata") else dataset
            for dataset in adata_input
        ]
    else:
        anndata_objects = (
            adata_input.adata if hasattr(adata_input, "adata") else adata_input
        )

    resolved_task_params = resolve_anndata_references(
        task_params or {}, anndata_objects
    )

    if run_baseline:
        assert (
            not is_multi_dataset_task
        ), "Baseline computation not supported for multi-dataset tasks"

        baseline_input_model = TaskClass.baseline_model(**baseline_params or {})
        cell_repr = task_instance.compute_baseline(
            expression_data=anndata_objects.X, baseline_input=baseline_input_model
        )
    else:
        cell_repr = resolve_anndata_references(
            cell_representation_input, anndata_objects
        )

    dense_cell_repr = (
        [_ensure_dense_matrix(rep) for rep in cell_repr]
        if isinstance(cell_repr, list)
        else _ensure_dense_matrix(cell_repr)
    )

    TASK_REGISTRY.validate_task_inputs(task_name, resolved_task_params)
    task_input_model = TaskClass.input_model(**resolved_task_params)

    results = task_instance.run(
        cell_representation=dense_cell_repr,
        task_input=task_input_model,
    )
    logger.debug("Task execution complete")
    return results
