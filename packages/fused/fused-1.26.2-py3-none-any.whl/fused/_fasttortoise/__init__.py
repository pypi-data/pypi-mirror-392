"""Fast Tortoise - Efficient parquet row group reconstruction from metadata."""

from typing import Optional

from fused._options import options as OPTIONS

# Keep the API helper in fused-py since it's just an API client
from ._api import get_row_groups_for_dataset


def _get_metadata_url(base_url: Optional[str] = None) -> str:
    """
    Get the metadata URL, using current environment's base URL if not specified.

    Args:
        base_url: Optional base URL override

    Returns:
        Full metadata endpoint URL
    """
    if base_url is None:
        base_url = OPTIONS.base_url

    return f"{base_url}/file-metadata"


def read_parquet_row_group(
    parquet_path: str,
    row_group_index: int,
    base_url: Optional[str] = None,
    columns=None,
):
    """
    Reconstruct and read a single row group from a parquet file.

    Args:
        parquet_path: S3 or HTTP path to parquet file
        row_group_index: Index of row group to read (0-based)
        base_url: Base URL for API (e.g., "https://www.fused.io/server/v1"). If None, uses current environment.
        columns: Optional list of column names to read

    Returns:
        PyArrow Table containing the row group data

    This function imports the implementation from job2 at runtime,
    similar to how raster_to_h3 works.

    Example:
        table = read_parquet_row_group(path, 0)
        df = table.to_pandas()
    """
    metadata_url = _get_metadata_url(base_url)

    try:
        from job2.fasttortoise import read_parquet_row_group as _read_parquet_row_group

        return _read_parquet_row_group(
            parquet_path=parquet_path,
            row_group_index=row_group_index,
            metadata_url=metadata_url,
            columns=columns,
        )
    except ImportError as e:
        raise RuntimeError(
            "The fasttortoise reconstruction functionality requires the job2 module. "
            "This is typically only available in the Fused execution environment."
        ) from e


async def async_read_parquet_row_group(
    parquet_path: str,
    row_group_index: int,
    base_url: Optional[str] = None,
    columns=None,
):
    """
    Reconstruct and read a single row group from a parquet file (async version).

    Args:
        parquet_path: S3 or HTTP path to parquet file
        row_group_index: Index of row group to read (0-based)
        base_url: Base URL for API (e.g., "https://www.fused.io/server/v1"). If None, uses current environment.
        columns: Optional list of column names to read

    Returns:
        PyArrow Table containing the row group data

    This function imports the implementation from job2 at runtime,
    similar to how raster_to_h3 works.

    Example:
        table = await async_read_parquet_row_group(path, 0)
        df = table.to_pandas()
    """
    metadata_url = _get_metadata_url(base_url)

    try:
        from job2.fasttortoise import (
            async_read_parquet_row_group as _async_read_parquet_row_group,
        )

        return await _async_read_parquet_row_group(
            parquet_path=parquet_path,
            row_group_index=row_group_index,
            metadata_url=metadata_url,
            columns=columns,
        )
    except ImportError as e:
        raise RuntimeError(
            "The fasttortoise reconstruction functionality requires the job2 module. "
            "This is typically only available in the Fused execution environment."
        ) from e


__all__ = [
    "async_read_parquet_row_group",
    "read_parquet_row_group",
    "get_row_groups_for_dataset",
]
