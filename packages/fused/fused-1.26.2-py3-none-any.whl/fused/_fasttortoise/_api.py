"""API client helpers for dataset queries."""

import json
from typing import Any, Dict, List, Optional


def get_row_groups_for_dataset(
    dataset_path: str,
    geographical_regions: List[Dict[str, str]],
    h3_resolution: Optional[int] = None,
    base_url: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query dataset to find files and row groups for given H3 spatial ranges.

    Args:
        dataset_path: S3 path to dataset (e.g., "s3://bucket/dataset/"). Can include
                     subdirectories to filter results (e.g., "s3://bucket/dataset/year=2024/").
        geographical_regions: List of H3 ranges like [{"min": "8928...", "max": "8928..."}]
        h3_resolution: Optional H3 resolution level to filter results. If not provided,
                      returns row groups from all resolutions.
        base_url: Base URL for API (e.g., "https://www.fused.io/server/v1"). If None, uses current environment.

    Returns:
        List of dicts with 'path' and 'row_group_index' keys

    Example:
        regions = [{"min": "8928308280fffff", "max": "89283082a1bffff"}]
        items = get_row_groups_for_dataset(
            "s3://my-bucket/my-dataset/",
            regions,
            h3_resolution=7  # Optional: filter to resolution 7 only
        )
        # Returns: [
        #   {"path": "s3://my-bucket/my-dataset/file1.parquet", "row_group_index": 0},
        #   {"path": "s3://my-bucket/my-dataset/file1.parquet", "row_group_index": 3},
        #   {"path": "s3://my-bucket/my-dataset/file2.parquet", "row_group_index": 1},
        # ]

        # Filter by subdirectory
        items = get_row_groups_for_dataset(
            "s3://my-bucket/my-dataset/year=2024/",
            regions
        )
    """
    # Use current environment's base URL if not specified
    if base_url is None:
        from fused._options import options as OPTIONS

        base_url = OPTIONS.base_url

    # Build query parameters
    params: Dict[str, Any] = {
        "dataset_path": dataset_path,
        "geographical_regions": json.dumps(geographical_regions),
    }

    if h3_resolution is not None:
        params["h3_resolution"] = h3_resolution

    # Make API request with retries
    from fused._request import session_with_retries

    url = f"{base_url}/datasets/items"
    with session_with_retries() as session:
        response = session.get(url, params=params)
        response.raise_for_status()

    # Parse response
    data = response.json()
    items = data.get("items", [])

    # Flatten into list of {path, row_group_index} dicts
    result = []
    for item in items:
        relative_path = item.get("relative_path", "")
        row_groups = item.get("row_groups", [])

        # Construct full path
        full_path = dataset_path.rstrip("/") + "/" + relative_path.lstrip("/")

        # Add each row group
        for rg_index in row_groups:
            result.append({"path": full_path, "row_group_index": rg_index})

    return result
