"""
Context manager for enabling history tracking.

This module provides a convenient context manager interface for
automatic lineage history capture.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, Optional

from pyspark.sql import SparkSession

from ..config import getConfig
from .snapshot_manager import SnapshotManager
from .storage_factory import create_storage

logger = logging.getLogger(__name__)


@contextmanager
def enable_history_tracking(
    table_path: Optional[str] = None,
    environment: Optional[str] = None,
    pipeline_name: Optional[str] = None,
    version: Optional[str] = None,
    project_name: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    spark: Optional[SparkSession] = None,
    enable_compression: bool = True,
    retention_days: int = 90,
    storage_backend: Optional[str] = None,
):
    """
    Context manager to enable lineage history tracking.

    This context manager automatically captures lineage history on exit,
    storing snapshots in persistent storage (Delta Lake or Parquet).
    It's designed to be non-invasive and backward compatible with existing code.

    Parameters default to global configuration values set via setConfig().
    Explicit parameters override global configuration.

    Args:
        table_path: Path to storage tables (e.g., "./lineage_history").
            If None, uses global config 'history_table_path'.
        environment: Environment tag (dev/staging/prod/testing).
            If None, uses global config 'environment' (default: "development").
        pipeline_name: Name of the pipeline.
            If None, uses global config 'pipeline_name' (default: auto-generated).
        version: Code version (Git SHA, tag, etc.).
            If None, uses global config 'version'.
        project_name: Project name for organizing lineage across projects.
            If None, uses global config 'project_name'.
        metadata: Additional metadata to attach to snapshot
        spark: SparkSession (default: active session)
        enable_compression: Enable compression (Zstandard for Delta, Snappy for Parquet)
        retention_days: Number of days to retain history
        storage_backend: Storage backend to use.
            If None, uses global config 'storage_backend' (default: "auto").
            - "auto": Use Delta Lake if available, fallback to Parquet
            - "delta": Force Delta Lake (raises error if not available)
            - "parquet": Force Parquet (useful for testing or compatibility)

    Yields:
        None (context manager)

    Example:
        >>> from pyspark_storydoc import setConfig, businessConcept
        >>> from pyspark_storydoc.history import enable_history_tracking
        >>>
        >>> # Option 1: Set global config once
        >>> setConfig(
        ...     project_name="Customer Analytics",
        ...     history_table_path="./lineage_history",
        ...     pipeline_name="customer_analysis",
        ...     environment="production"
        ... )
        >>>
        >>> # Now you can use enable_history_tracking without parameters
        >>> with enable_history_tracking():
        ...     @businessConcept("Filter Active Customers")
        ...     def filter_active(df):
        ...         return df.filter(col("status") == "active")
        ...     result = filter_active(customers_df)
        >>>
        >>> # Option 2: Override global config for specific contexts
        >>> with enable_history_tracking(environment="staging"):
        ...     # Uses global table_path but overrides environment
        ...     result = filter_active(customers_df)

    Raises:
        ValueError: If table_path is not provided and not set in global config
        Exception: If snapshot capture or storage fails
    """
    # Get values from global config as fallback
    table_path = table_path or getConfig('history_table_path')
    environment = environment or getConfig('environment', 'development')
    pipeline_name = pipeline_name or getConfig('pipeline_name')
    version = version or getConfig('version')
    project_name = project_name or getConfig('project_name')
    storage_backend = storage_backend or getConfig('storage_backend', 'auto')

    # Validate table_path
    if not table_path:
        raise ValueError(
            "table_path must be provided either as parameter or via "
            "setConfig(history_table_path='...')"
        )
    # Get SparkSession
    if spark is None:
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark is None:
                raise RuntimeError("No active SparkSession found")
        except Exception as e:
            logger.error(f"Failed to get SparkSession: {str(e)}")
            raise

    logger.info(
        f"Enabling history tracking for pipeline '{pipeline_name or 'auto'}' "
        f"in environment '{environment}'"
    )

    # Initialize storage (auto-detect or force specific backend)
    storage = create_storage(
        spark=spark,
        base_path=table_path,
        storage_backend=storage_backend,
        enable_compression=enable_compression,
        retention_days=retention_days,
    )

    # Create tables if they don't exist
    try:
        storage.initialize_tables()
    except Exception as e:
        logger.error(f"Failed to initialize storage tables: {str(e)}")
        raise

    # Add project_name to metadata if provided
    if metadata is None:
        metadata = {}
    if project_name:
        metadata['project_name'] = project_name

    # Initialize snapshot manager
    snapshot_manager = SnapshotManager(
        spark=spark,
        pipeline_name=pipeline_name,
        environment=environment,
        version=version,
        metadata=metadata,
    )

    try:
        # Yield control to user code
        yield

    finally:
        # Capture and save snapshot on exit
        try:
            logger.info("Capturing lineage snapshot...")
            snapshot = snapshot_manager.capture_snapshot()

            logger.info("Writing snapshot to storage...")
            snapshot_id = storage.write_snapshot(
                snapshot_data=snapshot["snapshot_data"],
                operations_data=snapshot["operations_data"],
                governance_data=snapshot["governance_data"],
                metrics_data=snapshot["metrics_data"],
            )

            logger.info(
                f"Successfully captured and saved snapshot {snapshot_id} "
                f"for pipeline '{snapshot_manager.pipeline_name}'"
            )

        except Exception as e:
            logger.error(
                f"Failed to capture or save snapshot: {str(e)}",
                exc_info=True
            )
            # Don't raise - we want the user's code to complete even if
            # history tracking fails
            logger.warning(
                "History tracking failed, but user code completed successfully"
            )
