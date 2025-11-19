"""Model Hub API client.

This module provides API functions for interacting with the VCP Model Hub.
"""

from collections import defaultdict
from typing import Literal, Optional
from urllib.parse import urljoin

import requests

from vcp.config.config import Config
from vcp.utils.errors import AuthenticationError, InvalidInputError
from vcp.utils.token import TokenManager

from .models import (
    ModelResponse,
    ModelsListResponse,
    ModelVersionResponse,
    VariantData,
    VariantFilesResponse,
    VariantsListResponse,
)


def _call_model_api(
    url: str,
    params: Optional[dict] = None,
    method: Literal["GET", "POST"] = "GET",
    json: Optional[dict] = None,
    timeout: float = 30,
    raise_if_not_logged_in: bool = True,
) -> dict:
    """
    Make API call to Model Hub.

    Args:
        url: Full URL to call
        params: Optional query parameters
        method: HTTP method (GET or POST)
        json: Optional JSON body for POST requests
        timeout: Request timeout in seconds
        raise_if_not_logged_in: If True, raises error when not logged in.
                                If False, proceeds without auth (uses auth headers if available).

    Returns:
        Parsed JSON response

    Raises:
        AuthenticationError: If not authenticated and raise_if_not_logged_in=True
        HTTPError: If HTTP error occurs (handled by CLI decorator)
        RequestException: If network error occurs (handled by CLI decorator)
    """
    token_manager = TokenManager()
    auth_headers = token_manager.get_auth_headers()

    if not auth_headers and raise_if_not_logged_in:
        raise AuthenticationError()

    response = requests.request(
        method, url, params=params, json=json, headers=auth_headers, timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def fetch_models_list(config: Config) -> ModelsListResponse:
    """
    Fetch list of available public models from Model Hub.

    Transforms /api/sub/variants response into grouped model/version structure.
    Works with or without authentication. Server filters to public models only.

    Args:
        config: Configuration object with base_url

    Returns:
        ModelsListResponse with models grouped by name and version
    """
    url = urljoin(config.models.base_url, "api/sub/variants")
    data = _call_model_api(url, raise_if_not_logged_in=False)

    variants_response = VariantsListResponse.model_validate(data)

    # Group variants by (model_name, model_version)
    grouped: dict[tuple[str, str], list[VariantData]] = defaultdict(list)
    for variant in variants_response.variants:
        key = (variant.model_name, variant.model_version)
        grouped[key].append(variant)

    # Build models with sorted variants
    models_dict: dict[str, list[ModelVersionResponse]] = defaultdict(list)
    for (model_name, model_version), variants in grouped.items():
        sorted_variants = sorted(variants, key=lambda v: v.name)

        models_dict[model_name].append(
            ModelVersionResponse(version=model_version, variants=sorted_variants)
        )

    models = [
        ModelResponse(name=name, versions=versions)
        for name, versions in sorted(models_dict.items())
    ]

    return ModelsListResponse(models=models)


def fetch_variants_for_model(
    config: Config,
    *,
    model: str,
    version: str,
) -> list[VariantData]:
    """
    Fetch available variants for a specific model/version from Model Hub API.

    Args:
        config: Configuration object with base_url
        model: Model name (e.g., "scVI")
        version: Model version (e.g., "2024-07-01")

    Returns:
        List of VariantData objects

    Raises:
        HTTPError: If API call fails (handled by decorator)
    """
    url = urljoin(config.models.base_url, "api/sub/variants")
    data = _call_model_api(
        url,
        params={"model_name": model, "model_version": version},
        raise_if_not_logged_in=False,
    )
    response = VariantsListResponse.model_validate(data)
    return response.variants


def fetch_files_for_variant(
    config: Config,
    *,
    variant_id: str,
) -> VariantFilesResponse:
    """
    Fetch downloadable files for a specific variant.

    Args:
        config: Configuration object with base_url
        variant_id: UUID string of the variant

    Returns:
        VariantFilesResponse with variant metadata and files

    Raises:
        HTTPError: If API call fails (handled by decorator)
    """
    url = urljoin(config.models.base_url, f"api/sub/variants/{variant_id}/files")
    data = _call_model_api(url, raise_if_not_logged_in=False)
    return VariantFilesResponse.model_validate(data)


def select_variant(
    variants: list[VariantData], requested_variant: str | None
) -> VariantData | None:
    """
    Select variant from a list for a specific model version.

    Args:
        variants: List of available variants for a specific model/version
        requested_variant: User-requested variant name or None for auto-selection

    Returns:
        VariantData if found or auto-selected
        None if multiple variants available and no requested_variant (user must choose)

    Raises:
        InvalidInputError: If requested_variant not found in variants list
    """
    # User requested specific variant - must find it or raise error
    if requested_variant:
        variant = next((v for v in variants if v.name == requested_variant), None)
        if variant is None:
            variant_names = [v.name for v in variants]
            raise InvalidInputError(
                input_type="variant",
                details=f"Variant '{requested_variant}' not found. Available variants: {', '.join(variant_names)}",
                operation="model download",
            )
        return variant

    # Auto-select if only one variant available
    if len(variants) == 1:
        return variants[0]

    # Multiple variants, user must choose (return None)
    return None
