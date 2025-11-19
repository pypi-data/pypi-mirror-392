"""Pydantic models for Model Hub API responses."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ModelVersionResponse(BaseModel):
    """
    Model version information.

    Attributes:
        version: Version identifier (e.g., '1.0.0', 'v2')
        variants: List of VariantData objects for this version
    """

    version: str
    variants: list["VariantData"]


class ModelResponse(BaseModel):
    """
    Model information from Model Hub.

    Attributes:
        name: Model name
        versions: List of available versions for this model
    """

    name: str
    versions: list[ModelVersionResponse]


class ModelsListResponse(BaseModel):
    """
    Response from GET /api/models/list.

    Attributes:
        models: List of available models with their versions
    """

    models: list[ModelResponse]


class VariantData(BaseModel):
    """
    Variant information from Model Hub /api/sub/variants endpoint.

    Attributes:
        id: Variant UUID
        submission_id: Associated submission ID
        name: Variant name (e.g., "homo_sapiens")
        model_name: Model identifier slug (e.g., "scvi")
        model_version: Version identifier slug (e.g., "1.0.0")
        mlflow_model_name: Internal MLflow catalog name
        mlflow_model_version: Internal MLflow version number
    """

    id: UUID
    submission_id: str
    name: str
    model_name: str
    model_version: str
    mlflow_model_name: str | None
    mlflow_model_version: int | None


class VariantsListResponse(BaseModel):
    """
    Response from GET /api/sub/variants.

    Attributes:
        variants: List of public model variants
    """

    variants: list[VariantData]


class VariantFile(BaseModel):
    """
    File information from /api/sub/variants/{id}/files endpoint.

    Attributes:
        relative_path: Path relative to model directory
        signed_download_url: Presigned download URL for file
        size_bytes: File size in bytes
        last_modified: ISO datetime string
    """

    relative_path: str
    signed_download_url: str
    size_bytes: int
    last_modified: str


class VariantFilesResponse(BaseModel):
    """
    Response from GET /api/sub/variants/{id}/files.

    Attributes:
        variant: Variant metadata
        files: List of downloadable files
    """

    variant: VariantData
    files: list[VariantFile]


class SubmissionData(BaseModel):
    """
    Submission information from Model Hub API.

    Attributes:
        submission_id: Unique identifier for the submission
        model_name: Name of the model
        model_version: Version of the model
        repo_url: GitHub repository URL for the submission
        status: Current status of the submission
    """

    submission_id: str
    model_name: str
    model_version: str
    repo_url: str
    status: Literal[
        "initialized",
        "submitted",
        "submitted_changes_requested",
        "ready_for_processing",
        "processing_failed",
        "processed",
        "metadata_changes_requested",
        "accepted",
        "denied",
    ]


class SubmissionResponse(BaseModel):
    """
    Response from POST /api/sub.

    Attributes:
        submission: Submission data including repo URL and submission ID
    """

    submission: SubmissionData
