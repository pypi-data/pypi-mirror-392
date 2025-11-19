"""
Global Configuration Management for PySpark StoryDoc.

This module provides a centralized configuration system that allows users to set
global defaults for history tracking and report generation, eliminating the need
to specify paths repeatedly in decorators and report generators.

Usage:
    >>> from pyspark_storydoc import setConfig, getConfig
    >>>
    >>> # Set global configuration
    >>> setConfig(
    ...     history_table_path="./lineage_history",
    ...     reports_output_dir="./reports",
    ...     pipeline_name="my_pipeline",
    ...     environment="production"
    ... )
    >>>
    >>> # Now decorators and report generators will use these defaults
    >>> @businessConcept("Process Data")
    >>> def process_data(df):
    ...     return df.filter(col("active") == True)
    >>>
    >>> # Generate report without specifying output_dir
    >>> generate_report()  # Uses "./reports" from config
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class GlobalConfig:
    """
    Singleton class to manage global configuration for PySpark StoryDoc.

    This provides centralized management of:
    - History tracking table paths
    - Report output directories
    - Pipeline metadata (name, environment, version)
    - Storage backend settings
    """

    _instance: Optional['GlobalConfig'] = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalConfig, cls).__new__(cls)
            cls._instance._config = {
                # Project settings
                'project_name': None,

                # History tracking settings
                'history_table_path': None,
                'storage_backend': 'parquet',
                'pipeline_name': None,
                'environment': None,
                'version': None,

                # Report generation settings
                'reports_output_dir': './outputs',

                # Feature flags
                'auto_enable_history_tracking': False,
                'auto_generate_reports': False,
            }
        return cls._instance

    def set(self, **kwargs) -> None:
        """
        Set one or more configuration values.

        Args:
            project_name: Project name for organizing lineage across projects
            history_table_path: Path to the history tracking table (parquet/delta)
            storage_backend: Storage backend for history ('parquet' or 'delta')
            pipeline_name: Default pipeline name for history tracking
            environment: Default environment (e.g., 'dev', 'staging', 'prod')
            version: Default version string for snapshots
            reports_output_dir: Default directory for all generated reports
            auto_enable_history_tracking: Automatically enable history tracking
            auto_generate_reports: Automatically generate reports after operations

        Example:
            >>> config = GlobalConfig()
            >>> config.set(
            ...     project_name="Customer Analytics",
            ...     history_table_path="./my_lineage",
            ...     reports_output_dir="./my_reports",
            ...     pipeline_name="data_pipeline",
            ...     environment="production"
            ... )
        """
        for key, value in kwargs.items():
            if key not in self._config:
                logger.warning(f"Unknown configuration key: {key}")
                continue

            self._config[key] = value
            logger.debug(f"Config set: {key} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key to retrieve
            default: Default value if key not found or value is None

        Returns:
            The configuration value, or default if not set

        Example:
            >>> config = GlobalConfig()
            >>> output_dir = config.get('reports_output_dir', './outputs')
        """
        value = self._config.get(key)
        return value if value is not None else default

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary of all configuration settings
        """
        return self._config.copy()

    def reset(self) -> None:
        """
        Reset all configuration to defaults.

        Example:
            >>> config = GlobalConfig()
            >>> config.reset()
        """
        self._config = {
            'project_name': None,
            'history_table_path': None,
            'storage_backend': 'parquet',
            'pipeline_name': None,
            'environment': None,
            'version': None,
            'reports_output_dir': './outputs',
            'auto_enable_history_tracking': False,
            'auto_generate_reports': False,
        }
        logger.info("Configuration reset to defaults")

    def clear(self, key: str) -> None:
        """
        Clear a specific configuration value (set to None).

        Args:
            key: Configuration key to clear

        Example:
            >>> config = GlobalConfig()
            >>> config.clear('pipeline_name')
        """
        if key in self._config:
            self._config[key] = None
            logger.debug(f"Config cleared: {key}")
        else:
            logger.warning(f"Unknown configuration key: {key}")


# Module-level instance
_global_config = GlobalConfig()


def setConfig(**kwargs) -> None:
    """
    Set global configuration for PySpark StoryDoc.

    This is the main user-facing API for configuring global defaults.
    Once set, these values are used as fallbacks when not explicitly
    specified in decorators, context managers, or report generators.

    Args:
        project_name: Project name for organizing lineage across projects
        history_table_path: Path to the history tracking table
        storage_backend: Storage backend ('parquet' or 'delta')
        pipeline_name: Default pipeline name for history tracking
        environment: Default environment (e.g., 'dev', 'staging', 'prod')
        version: Default version string for snapshots
        reports_output_dir: Default directory for all generated reports
        auto_enable_history_tracking: Automatically enable history tracking
        auto_generate_reports: Automatically generate reports after operations

    Example:
        >>> from pyspark_storydoc import setConfig
        >>>
        >>> # Configure once at the start of your script
        >>> setConfig(
        ...     project_name="Customer Analytics",
        ...     history_table_path="./lineage_history",
        ...     reports_output_dir="./reports",
        ...     pipeline_name="customer_analytics",
        ...     environment="production",
        ...     storage_backend="parquet"
        ... )
        >>>
        >>> # Now all decorators and reports use these defaults
        >>> @businessConcept("Filter Customers")
        >>> def filter_customers(df):
        ...     return df.filter(col("status") == "active")
    """
    _global_config.set(**kwargs)


def getConfig(key: str, default: Any = None) -> Any:
    """
    Get a global configuration value.

    Args:
        key: Configuration key to retrieve
        default: Default value if key not found or not set

    Returns:
        The configuration value, or default if not set

    Example:
        >>> from pyspark_storydoc import getConfig
        >>>
        >>> output_dir = getConfig('reports_output_dir', './default_outputs')
        >>> history_path = getConfig('history_table_path')
    """
    return _global_config.get(key, default)


def getAllConfig() -> Dict[str, Any]:
    """
    Get all global configuration values.

    Returns:
        Dictionary of all configuration settings

    Example:
        >>> from pyspark_storydoc import getAllConfig
        >>>
        >>> config = getAllConfig()
        >>> print(f"History path: {config['history_table_path']}")
        >>> print(f"Reports dir: {config['reports_output_dir']}")
    """
    return _global_config.get_all()


def resetConfig() -> None:
    """
    Reset all global configuration to defaults.

    Example:
        >>> from pyspark_storydoc import resetConfig
        >>>
        >>> resetConfig()  # Clear all settings
    """
    _global_config.reset()


def clearConfig(key: str) -> None:
    """
    Clear a specific configuration value.

    Args:
        key: Configuration key to clear

    Example:
        >>> from pyspark_storydoc import clearConfig
        >>>
        >>> clearConfig('pipeline_name')  # Clear just this setting
    """
    _global_config.clear(key)


__all__ = [
    'setConfig',
    'getConfig',
    'getAllConfig',
    'resetConfig',
    'clearConfig',
    'GlobalConfig',
]
