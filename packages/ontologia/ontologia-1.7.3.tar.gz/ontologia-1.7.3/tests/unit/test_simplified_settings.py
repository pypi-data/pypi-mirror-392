"""
Tests for simplified settings with feature flags.

These tests verify that Ontologia can run in minimal mode with just SQL
and gracefully handle missing optional dependencies.
"""

import os
from unittest.mock import patch

import pytest

# Import originals for testing
# Import test settings
# from tests.fixtures._test_settings import (
#     TestAppSimplifiedSettings as TestSimplifiedSettings,
# )
# from tests.fixtures._test_settings import (
#     get_test_simplified_settings,
# )
# Import the actual implementation for testing
from ontologia.application.simplified_settings import (
    SimplifiedSettings,
    _detect_dagster,
    _detect_duckdb,
    _detect_elasticsearch,
    _detect_kuzu,
    _detect_temporal,
    get_simplified_settings,
)


class TestDependencyDetection:
    """Test runtime dependency detection."""

    def test_detect_duckdb_available(self):
        """Test DuckDB detection when available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = True
            assert _detect_duckdb() is True

    def test_detect_duckdb_unavailable(self):
        """Test DuckDB detection when not available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None
            assert _detect_duckdb() is False

    def test_detect_kuzu_available(self):
        """Test KùzuDB detection when available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = True  # type: ignore[assignment]
            assert _detect_kuzu() is True

    def test_detect_elasticsearch_available(self):
        """Test Elasticsearch detection when available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = True  # type: ignore[assignment]
            assert _detect_elasticsearch() is True

    def test_detect_temporal_available(self):
        """Test Temporal detection when available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = True  # type: ignore[assignment]
            assert _detect_temporal() is True

    def test_detect_dagster_available(self):
        """Test Dagster detection when available."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = True  # type: ignore[assignment]
            assert _detect_dagster() is True


class TestSimplifiedSettings:
    """Test simplified settings configuration."""

    def test_core_mode_defaults(self):
        """Test core mode defaults with minimal dependencies."""
        # Use simplified settings with minimal dependencies
        settings = SimplifiedSettings(
            storage_mode="sql_only",
            database_url="sqlite:///:memory:",
            enable_search=False,
            enable_workflows=False,
            enable_realtime=False,
            enable_orchestration=False,
        )

        # Check core mode settings
        assert settings.storage_mode == "sql_only"  # type: ignore[attr-defined]
        assert settings.database_url == "sqlite:///:memory:"  # type: ignore[attr-defined]

        # Check feature flags are disabled
        assert settings.enable_search is False  # type: ignore[attr-defined]
        assert settings.enable_workflows is False  # type: ignore[attr-defined]
        assert settings.enable_realtime is False  # type: ignore[attr-defined]
        assert settings.enable_orchestration is False  # type: ignore[attr-defined]

        # Check mode detection
        assert settings.is_core_mode() is True  # type: ignore[attr-defined]
        assert settings.is_analytics_mode() is False  # type: ignore[attr-defined]
        assert settings.is_enterprise_mode() is False  # type: ignore[attr-defined]

    def test_analytics_mode_detection(self):
        """Test analytics mode when DuckDB is available."""
        with (
            patch("ontologia.application.simplified_settings._detect_duckdb", return_value=True),
            patch("ontologia.application.simplified_settings._detect_kuzu", return_value=False),
            patch(
                "ontologia.application.simplified_settings._detect_elasticsearch",
                return_value=False,
            ),
            patch("ontologia.application.simplified_settings._detect_temporal", return_value=False),
            patch("ontologia.application.simplified_settings._detect_dagster", return_value=False),
        ):
            settings = SimplifiedSettings()

            # Default behavior with duckdb available
            assert settings.storage_mode == "sql_duckdb"  # type: ignore[attr-defined]
            # These should be False by default unless explicitly enabled
            assert settings.enable_search is False  # type: ignore[attr-defined]
            assert settings.enable_workflows is False  # type: ignore[attr-defined]
            assert settings.enable_orchestration is False  # type: ignore[attr-defined]
            assert settings.is_core_mode() is False  # type: ignore[attr-defined]
            assert settings.is_analytics_mode() is True  # type: ignore[attr-defined]
            assert settings.is_enterprise_mode() is False  # type: ignore[attr-defined]

    def test_graph_mode_detection(self):
        """Test graph mode when KùzuDB is available."""
        with (
            patch("ontologia.application.simplified_settings._detect_duckdb", return_value=False),
            patch("ontologia.application.simplified_settings._detect_kuzu", return_value=True),
            patch(
                "ontologia.application.simplified_settings._detect_elasticsearch",
                return_value=False,
            ),
            patch("ontologia.application.simplified_settings._detect_temporal", return_value=False),
            patch("ontologia.application.simplified_settings._detect_dagster", return_value=False),
        ):
            settings = SimplifiedSettings()

            assert settings.storage_mode == "sql_kuzu"  # type: ignore[attr-defined]
            assert settings.is_core_mode() is False  # type: ignore[attr-defined]
            assert settings.is_analytics_mode() is True  # type: ignore[attr-defined]

    def test_enterprise_mode_detection(self):
        """Test enterprise mode when all dependencies are available."""
        with (
            patch("ontologia.application.simplified_settings._detect_duckdb", return_value=True),
            patch("ontologia.application.simplified_settings._detect_kuzu", return_value=True),
            patch(
                "ontologia.application.simplified_settings._detect_elasticsearch", return_value=True
            ),
            patch("ontologia.application.simplified_settings._detect_temporal", return_value=True),
            patch("ontologia.application.simplified_settings._detect_dagster", return_value=True),
        ):
            # Explicitly set storage_mode to sql_kuzu for enterprise mode
            settings = SimplifiedSettings(
                storage_mode="sql_kuzu",
                enable_search=True,
                enable_workflows=True,
                enable_orchestration=True,
                enable_realtime=True,
            )

            assert settings.storage_mode == "sql_kuzu"  # type: ignore[attr-defined]
            assert settings.enable_search is True  # type: ignore[attr-defined]
            assert settings.enable_workflows is True  # type: ignore[attr-defined]
            assert settings.enable_orchestration is True  # type: ignore[attr-defined]
            assert settings.enable_realtime is True  # type: ignore[attr-defined]
            assert settings.is_core_mode() is False  # type: ignore[attr-defined]
            # In enterprise mode with DuckDB available, analytics mode should be True
            assert settings.is_analytics_mode() is True  # type: ignore[attr-defined]
            assert settings.is_enterprise_mode() is True  # type: ignore[attr-defined]

    def test_environment_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "STORAGE_MODE": "sql_only",
                "ENABLE_SEARCH": "true",
                "ENABLE_WORKFLOWS": "false",
                "DEV_MODE": "true",
            },
        ):
            settings = SimplifiedSettings()

            assert settings.storage_mode == "sql_only"  # type: ignore[attr-defined]
            assert settings.enable_search is True  # type: ignore[attr-defined]
            assert settings.enable_workflows is False  # type: ignore[attr-defined]
            assert settings.dev_mode is True  # type: ignore[attr-defined]

    def test_get_enabled_features(self):
        """Test feature listing for display."""
        settings = SimplifiedSettings(
            storage_mode="sql_duckdb",
            enable_search=True,
            enable_workflows=False,
            enable_realtime=False,
            enable_orchestration=True,
            dev_mode=True,
        )

        features = settings.get_enabled_features()  # type: ignore[attr-defined]
        expected = ["core", "storage_sql_duckdb", "search", "orchestration", "dev"]

        assert all(f in features for f in expected)  # type: ignore[index]

    def test_settings_caching(self):
        """Test that settings are cached properly."""
        settings1 = get_simplified_settings()
        settings2 = get_simplified_settings()

        assert settings1 is settings2


class TestModeValidation:
    """Test mode validation and constraints."""

    def test_invalid_storage_mode(self):
        """Test validation of storage mode values."""
        with pytest.raises(ValueError):
            SimplifiedSettings(storage_mode="invalid_mode")  # type: ignore[arg-type]

    def test_mutually_exclusive_storage(self):
        """Test that storage modes are mutually exclusive."""
        # This is more of an integration test - the settings should
        # only allow one storage mode at a time
        settings = SimplifiedSettings(storage_mode="sql_only")
        assert settings.storage_mode == "sql_only"  # type: ignore[attr-defined]

        settings = SimplifiedSettings(storage_mode="sql_duckdb")
        assert settings.storage_mode == "sql_duckdb"  # type: ignore[attr-defined]

        settings = SimplifiedSettings(storage_mode="sql_kuzu")
        assert settings.storage_mode == "sql_kuzu"  # type: ignore[attr-defined]


class TestLegacyCompatibility:
    """Test compatibility with existing settings system."""

    def test_legacy_attributes_exist(self):
        """Test that legacy attributes are still available."""
        settings = SimplifiedSettings()

        # These should exist for backward compatibility
        assert hasattr(settings, "use_temporal_actions")
        assert hasattr(settings, "use_graph_reads")
        assert hasattr(settings, "enable_search_indexing")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "jwt_secret_key")

    def test_legacy_settings_wrapper(self):
        """Test that the legacy get_settings() wrapper works."""
        from ontologia.application.simplified_settings import get_settings

        settings = get_settings()
        assert isinstance(settings, SimplifiedSettings)


class TestDevModeFeatures:
    """Test development mode specific features."""

    def test_dev_mode_enables_debug_features(self):
        """Test that dev mode enables development-friendly settings."""
        settings = SimplifiedSettings(dev_mode=True)

        assert settings.dev_mode is True  # type: ignore[attr-defined]
        assert "dev" in settings.get_enabled_features()  # type: ignore[attr-defined,index]

    def test_dev_mode_from_environment(self):
        """Test dev mode detection from environment."""
        with patch.dict(os.environ, {"ONTOLOGIA_DEV_MODE": "1"}):
            settings = SimplifiedSettings()
            assert settings.dev_mode is True  # type: ignore[attr-defined]

        with patch.dict(os.environ, {"ONTOLOGIA_DEV_MODE": "true"}):
            settings = SimplifiedSettings()
            assert settings.dev_mode is True  # type: ignore[attr-defined]

        with patch.dict(os.environ, {"ONTOLOGIA_DEV_MODE": "false"}):
            settings = SimplifiedSettings()
            assert settings.dev_mode is False  # type: ignore[attr-defined]
