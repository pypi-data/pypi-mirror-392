"""
Tests for global configuration functionality.
"""

import pytest

from pyspark_storydoc import clearConfig, getAllConfig, getConfig, resetConfig, setConfig
from pyspark_storydoc.config import GlobalConfig


class TestGlobalConfig:
    """Test suite for global configuration management."""

    def setup_method(self):
        """Reset config before each test."""
        resetConfig()

    def teardown_method(self):
        """Clean up after each test."""
        resetConfig()

    def test_set_and_get_config(self):
        """Test setting and retrieving configuration values."""
        setConfig(
            project_name="Test Project",
            history_table_path="./test_lineage",
            pipeline_name="test_pipeline",
            environment="testing"
        )

        assert getConfig('project_name') == "Test Project"
        assert getConfig('history_table_path') == "./test_lineage"
        assert getConfig('pipeline_name') == "test_pipeline"
        assert getConfig('environment') == "testing"

    def test_get_config_with_default(self):
        """Test getConfig returns default when value not set."""
        result = getConfig('history_table_path', './default_path')
        assert result == './default_path'

    def test_get_all_config(self):
        """Test retrieving all configuration values."""
        setConfig(
            project_name="My Project",
            history_table_path="./lineage",
            reports_output_dir="./reports"
        )

        config = getAllConfig()
        assert config['project_name'] == "My Project"
        assert config['history_table_path'] == "./lineage"
        assert config['reports_output_dir'] == "./reports"
        assert 'pipeline_name' in config

    def test_reset_config(self):
        """Test resetting configuration to defaults."""
        setConfig(
            project_name="Test Project",
            history_table_path="./test",
            pipeline_name="test"
        )

        resetConfig()

        assert getConfig('project_name') is None
        assert getConfig('history_table_path') is None
        assert getConfig('pipeline_name') is None
        assert getConfig('storage_backend') == 'parquet'  # Default value

    def test_clear_specific_config(self):
        """Test clearing a specific configuration value."""
        setConfig(
            history_table_path="./test",
            pipeline_name="test_pipeline"
        )

        clearConfig('history_table_path')

        assert getConfig('history_table_path') is None
        assert getConfig('pipeline_name') == "test_pipeline"

    def test_singleton_behavior(self):
        """Test that GlobalConfig is a singleton."""
        config1 = GlobalConfig()
        config2 = GlobalConfig()

        assert config1 is config2

        config1.set(history_table_path="./test")
        assert config2.get('history_table_path') == "./test"

    def test_unknown_config_key(self):
        """Test setting unknown configuration key logs warning."""
        # Should not raise, but will log warning
        setConfig(unknown_key="value")

        # Unknown keys are not stored
        assert getConfig('unknown_key') is None

    def test_config_override_none_values(self):
        """Test that None values don't override defaults."""
        setConfig(storage_backend='delta')
        assert getConfig('storage_backend') == 'delta'

        setConfig(storage_backend=None)
        # Should still return None because it was explicitly set to None
        assert getConfig('storage_backend') is None

        # With default parameter
        assert getConfig('storage_backend', 'parquet') == 'parquet'
