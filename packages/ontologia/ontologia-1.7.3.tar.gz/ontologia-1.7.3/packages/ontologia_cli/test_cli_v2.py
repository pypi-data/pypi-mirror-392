"""
Tests for the CLI v2 implementation.
"""

import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import typer
import yaml
from typer.testing import CliRunner

from ontologia_cli.cli_v2 import (
    CLIConfig,
    app,
    cli_config,
    format_dict_as_table,
    format_output,
    format_table,
    get_client,
    run_async,
)


class TestCLIConfig:
    """Test CLI configuration management."""

    def test_config_init(self):
        """Test configuration initialization."""
        config = CLIConfig()

        assert config.host is None
        assert config.token is None
        assert config.connection_string is None
        assert config.ontology == "default"
        assert config.timeout == 30.0
        assert config.output_format == "table"
        assert config.verbose is False

    def test_config_attributes(self):
        """Test setting configuration attributes."""
        config = CLIConfig()
        config.host = "http://localhost:8000"
        config.token = "test-token"
        config.ontology = "test-ontology"

        assert config.host == "http://localhost:8000"
        assert config.token == "test-token"
        assert config.ontology == "test-ontology"

    @patch("ontologia_cli.cli_v2.Path.exists")
    @patch("ontologia_cli.cli_v2.yaml.safe_load")
    @patch("ontologia_cli.cli_v2.open")
    def test_config_load(self, mock_open, mock_yaml_load, mock_exists):
        """Test loading configuration from file."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "host": "http://test.com",
            "token": "test-token",
            "ontology": "test-ontology",
        }

        config = CLIConfig()
        config.load()

        assert config.host == "http://test.com"
        assert config.token == "test-token"
        assert config.ontology == "test-ontology"

    @patch("ontologia_cli.cli_v2.Path.mkdir")
    @patch("ontologia_cli.cli_v2.yaml.dump")
    @patch("ontologia_cli.cli_v2.open")
    def test_config_save(self, mock_open, mock_yaml_dump, mock_mkdir):
        """Test saving configuration to file."""
        config = CLIConfig()
        config.host = "http://test.com"
        config.token = "test-token"

        config.save()

        mock_mkdir.assert_called_once_with(exist_ok=True)
        mock_yaml_dump.assert_called_once()


class TestOutputFormatting:
    """Test output formatting functions."""

    def test_format_output_json(self):
        """Test JSON output formatting."""
        data = {"name": "test", "value": 123}
        result = format_output(data, "json")

        parsed = json.loads(result)
        assert parsed == data

    def test_format_output_yaml(self):
        """Test YAML output formatting."""
        data = {"name": "test", "value": 123}
        result = format_output(data, "yaml")

        parsed = yaml.safe_load(result)
        assert parsed == data

    def test_format_output_table_list(self):
        """Test table formatting for lists."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = format_output(data, "table")

        assert "Alice" in result
        assert "Bob" in result
        assert "30" in result
        assert "25" in result

    def test_format_output_table_dict(self):
        """Test table formatting for dictionaries."""
        data = {"name": "test", "value": 123}
        result = format_output(data, "table")

        assert "name" in result
        assert "test" in result
        assert "value" in result
        assert "123" in result

    def test_format_output_default(self):
        """Test default output formatting."""
        data = "simple string"
        result = format_output(data)

        assert result == "simple string"

    def test_format_table_empty(self):
        """Test formatting empty table."""
        result = format_table([])
        assert result == "No data"

    def test_format_table_with_data(self):
        """Test formatting table with data."""
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = format_table(data)

        assert "Alice" in result
        assert "Bob" in result

    def test_format_dict_as_table(self):
        """Test formatting dictionary as table."""
        data = {"name": "test", "value": 123}
        result = format_dict_as_table(data)

        assert "name" in result
        assert "test" in result


class TestClientIntegration:
    """Test client integration."""

    @patch("ontologia_cli.cli_v2.create_remote_client")
    def test_get_client_remote(self, mock_create_remote):
        """Test getting remote client."""
        cli_config.host = "http://localhost:8000"
        cli_config.token = "test-token"

        mock_client = AsyncMock()
        mock_create_remote.return_value = mock_client

        client = get_client()

        assert client is mock_client
        mock_create_remote.assert_called_once_with(
            host="http://localhost:8000", token="test-token", ontology="default", timeout=30.0
        )

    @patch("ontologia_cli.cli_v2.create_local_client")
    def test_get_client_local(self, mock_create_local):
        """Test getting local client."""
        cli_config.connection_string = "sqlite:///test.db"

        mock_client = AsyncMock()
        mock_create_local.return_value = mock_client

        client = get_client()

        assert client is mock_client
        mock_create_local.assert_called_once_with(
            connection_string="sqlite:///test.db", ontology="default"
        )

    def test_get_client_no_config(self):
        """Test getting client with no configuration."""
        # Reset config
        cli_config.host = None
        cli_config.connection_string = None

        with pytest.raises(typer.Exit):
            get_client()


class TestAsyncRunner:
    """Test async function runner."""

    @pytest.mark.asyncio
    async def test_run_async_success(self):
        """Test successful async function execution."""

        async def test_func():
            return "success"

        result = await run_async(test_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_run_async_error(self):
        """Test async function error handling."""

        async def test_func():
            raise ValueError("test error")

        with pytest.raises(typer.Exit):
            await run_async(test_func)


class TestCLICommands:
    """Test CLI commands."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()

        # Reset config for each test
        cli_config.host = None
        cli_config.token = None
        cli_config.connection_string = None
        cli_config.ontology = "default"
        cli_config.timeout = 30.0
        cli_config.output_format = "table"
        cli_config.verbose = False

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Ontologia CLI v2.0.0" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_status_command_success(self, mock_get_client):
        """Test status command with successful connection."""
        mock_client = AsyncMock()
        mock_client.list_object_types = AsyncMock(return_value=[{"api_name": "test"}])
        mock_client.mode = "remote"
        mock_client.ontology = "test-ontology"

        mock_get_client.return_value = mock_client

        # Configure for remote mode
        cli_config.host = "http://localhost:8000"

        result = self.runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Connection Status" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_status_command_failure(self, mock_get_client):
        """Test status command with failed connection."""
        mock_client = AsyncMock()
        mock_client.list_object_types = AsyncMock(side_effect=Exception("Connection failed"))

        mock_get_client.return_value = mock_client

        # Configure for remote mode
        cli_config.host = "http://localhost:8000"

        result = self.runner.invoke(app, ["status"])
        assert result.exit_code == 1

    def test_config_show_command(self):
        """Test config show command."""
        cli_config.host = "http://test.com"
        cli_config.ontology = "test-ontology"

        result = self.runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "http://test.com" in result.stdout
        assert "test-ontology" in result.stdout

    def test_config_set_command(self):
        """Test config set command."""
        with patch("ontologia_cli.cli_v2.cli_config.save") as mock_save:
            result = self.runner.invoke(app, ["config", "set", "host", "http://new-test.com"])
            assert result.exit_code == 0
            assert cli_config.host == "http://new-test.com"
            mock_save.assert_called_once()

    def test_config_set_invalid_key(self):
        """Test config set with invalid key."""
        result = self.runner.invoke(app, ["config", "set", "invalid", "value"])
        assert result.exit_code == 1
        assert "Invalid key" in result.stdout

    def test_config_set_timeout_conversion(self):
        """Test config set with timeout conversion."""
        with patch("ontologia_cli.cli_v2.cli_config.save") as mock_save:
            result = self.runner.invoke(app, ["config", "set", "timeout", "60"])
            assert result.exit_code == 0
            assert cli_config.timeout == 60.0
            mock_save.assert_called_once()

    def test_config_set_verbose_conversion(self):
        """Test config set with verbose conversion."""
        with patch("ontologia_cli.cli_v2.cli_config.save") as mock_save:
            result = self.runner.invoke(app, ["config", "set", "verbose", "true"])
            assert result.exit_code == 0
            assert cli_config.verbose is True
            mock_save.assert_called_once()

    @patch("ontologia_cli.cli_v2.cli_config.save")
    def test_config_remote_command(self, mock_save):
        """Test config remote command."""
        result = self.runner.invoke(
            app,
            [
                "config",
                "remote",
                "--host",
                "http://remote-test.com",
                "--token",
                "test-token",
                "--ontology",
                "remote-ontology",
            ],
        )

        assert result.exit_code == 0
        assert cli_config.host == "http://remote-test.com"
        assert cli_config.token == "test-token"
        assert cli_config.connection_string is None
        assert cli_config.ontology == "remote-ontology"
        mock_save.assert_called_once()

    @patch("ontologia_cli.cli_v2.cli_config.save")
    def test_config_local_command(self, mock_save):
        """Test config local command."""
        result = self.runner.invoke(
            app,
            [
                "config",
                "local",
                "--connection-string",
                "sqlite:///local-test.db",
                "--ontology",
                "local-ontology",
            ],
        )

        assert result.exit_code == 0
        assert cli_config.connection_string == "sqlite:///local-test.db"
        assert cli_config.host is None
        assert cli_config.token is None
        assert cli_config.ontology == "local-ontology"
        mock_save.assert_called_once()


class TestObjectTypeCommands:
    """Test object type commands."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        cli_config.host = "http://localhost:8000"  # Configure for tests

    @patch("ontologia_cli.cli_v2.get_client")
    def test_list_object_types(self, mock_get_client):
        """Test listing object types."""
        mock_client = AsyncMock()
        mock_client.list_object_types = AsyncMock(
            return_value=[
                {"api_name": "person", "display_name": "Person"},
                {"api_name": "company", "display_name": "Company"},
            ]
        )

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["types", "list"])
        assert result.exit_code == 0
        assert "person" in result.stdout
        assert "company" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_get_object_type(self, mock_get_client):
        """Test getting object type."""
        mock_client = AsyncMock()
        mock_client.get_object_type = AsyncMock(
            return_value={
                "api_name": "person",
                "display_name": "Person",
                "properties": [{"name": "name", "type": "string"}],
            }
        )

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["types", "get", "person"])
        assert result.exit_code == 0
        assert "person" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_get_object_type_not_found(self, mock_get_client):
        """Test getting non-existent object type."""
        mock_client = AsyncMock()
        mock_client.get_object_type = AsyncMock(return_value=None)

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["types", "get", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_create_object_type(self, mock_get_client):
        """Test creating object type."""
        mock_client = AsyncMock()
        mock_client.create_object_type = AsyncMock(
            return_value={"api_name": "person", "display_name": "Person"}
        )

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        # Create temporary file with object type definition
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "api_name": "person",
                    "display_name": "Person",
                    "properties": [{"name": "name", "type": "string"}],
                },
                f,
            )
            temp_file = f.name

        try:
            result = self.runner.invoke(app, ["types", "create", temp_file])
            assert result.exit_code == 0
            assert "Object type created successfully" in result.stdout
        finally:
            os.unlink(temp_file)


class TestObjectCommands:
    """Test object commands."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        cli_config.host = "http://localhost:8000"

    @patch("ontologia_cli.cli_v2.get_client")
    def test_list_objects(self, mock_get_client):
        """Test listing objects."""
        mock_client = AsyncMock()
        mock_client.list_objects = AsyncMock(
            return_value=[{"pk": "person-1", "name": "Alice"}, {"pk": "person-2", "name": "Bob"}]
        )

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["objects", "list", "person"])
        assert result.exit_code == 0
        assert "Alice" in result.stdout
        assert "Bob" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_list_objects_with_filters(self, mock_get_client):
        """Test listing objects with filters."""
        mock_client = AsyncMock()
        mock_client.list_objects = AsyncMock(return_value=[])

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(
            app,
            [
                "objects",
                "list",
                "person",
                "--limit",
                "10",
                "--offset",
                "5",
                "--where",
                "name:=:Alice",
            ],
        )
        assert result.exit_code == 0

        # Check that filters were passed correctly
        call_args = mock_client.list_objects.call_args
        assert call_args[0][0] == "person"
        assert call_args[1]["limit"] == 10
        assert call_args[1]["offset"] == 5

    @patch("ontologia_cli.cli_v2.get_client")
    def test_get_object(self, mock_get_client):
        """Test getting object."""
        mock_client = AsyncMock()
        mock_client.get_object = AsyncMock(
            return_value={"pk": "person-1", "name": "Alice", "age": 30}
        )

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["objects", "get", "person", "person-1"])
        assert result.exit_code == 0
        assert "Alice" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    def test_create_object(self, mock_get_client):
        """Test creating object."""
        mock_client = AsyncMock()
        mock_client.create_object = AsyncMock(return_value={"pk": "person-1", "name": "Alice"})

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        # Create temporary file with object data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "Alice", "age": 30}, f)
            temp_file = f.name

        try:
            result = self.runner.invoke(app, ["objects", "create", "person", temp_file])
            assert result.exit_code == 0
            assert "Object created successfully" in result.stdout
        finally:
            os.unlink(temp_file)

    @patch("ontologia_cli.cli_v2.get_client")
    def test_delete_object(self, mock_get_client):
        """Test deleting object."""
        mock_client = AsyncMock()
        mock_client.delete_object = AsyncMock(return_value=True)

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["objects", "delete", "person", "person-1", "--confirm"])
        assert result.exit_code == 0
        assert "Object deleted successfully" in result.stdout


class TestQueryCommands:
    """Test query commands."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        cli_config.host = "http://localhost:8000"

    @patch("ontologia_cli.cli_v2.get_client")
    @patch("ontologia_cli.cli_v2.QueryExecutor")
    def test_query_build(self, mock_executor_class, mock_get_client):
        """Test building and executing query."""
        mock_client = AsyncMock()
        mock_executor = AsyncMock()
        mock_executor.execute = AsyncMock(
            return_value=[{"pk": "person-1", "name": "Alice"}, {"pk": "person-2", "name": "Bob"}]
        )

        mock_executor_class.return_value = mock_executor
        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(
            app,
            [
                "query",
                "build",
                "person",
                "--where",
                "age:>:25",
                "--order",
                "name:asc",
                "--limit",
                "10",
            ],
        )
        assert result.exit_code == 0
        assert "Alice" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    @patch("ontologia_cli.cli_v2.QueryExecutor")
    def test_query_count(self, mock_executor_class, mock_get_client):
        """Test counting query results."""
        mock_client = AsyncMock()
        mock_executor = AsyncMock()
        mock_executor.count = AsyncMock(return_value=42)

        mock_executor_class.return_value = mock_executor
        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["query", "count", "person", "--where", "status:=:active"])
        assert result.exit_code == 0
        assert "Count: 42" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    @patch("ontologia_cli.cli_v2.QueryExecutor")
    def test_query_sql(self, mock_executor_class, mock_get_client):
        """Test query with SQL output."""
        mock_client = AsyncMock()
        mock_executor = AsyncMock()
        mock_executor.execute = AsyncMock(return_value=[])

        mock_executor_class.return_value = mock_executor
        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(
            app, ["query", "build", "person", "--where", "age:>:25", "--sql"]
        )
        assert result.exit_code == 0
        assert "SQL Representation" in result.stdout


class TestModelCommands:
    """Test model commands."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        cli_config.host = "http://localhost:8000"

    @patch("ontologia_cli.cli_v2.get_client")
    @patch("ontologia_cli.cli_v2.ModelFactory")
    def test_model_generate(self, mock_factory_class, mock_get_client):
        """Test generating model."""
        mock_client = AsyncMock()
        mock_client.get_object_type = AsyncMock(
            return_value={"api_name": "person", "properties": [{"name": "name", "type": "string"}]}
        )

        mock_factory = MagicMock()
        mock_model = MagicMock()
        mock_model.__name__ = "PersonModel"
        mock_factory.create_model.return_value = mock_model
        mock_factory_class.return_value = mock_factory

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        result = self.runner.invoke(app, ["models", "generate", "person"])
        assert result.exit_code == 0
        assert "Generated Model" in result.stdout

    @patch("ontologia_cli.cli_v2.get_client")
    @patch("ontologia_cli.cli_v2.ModelFactory")
    def test_model_validate(self, mock_factory_class, mock_get_client):
        """Test validating data."""
        mock_client = AsyncMock()
        mock_client.get_object_type = AsyncMock(
            return_value={"api_name": "person", "properties": [{"name": "name", "type": "string"}]}
        )

        mock_factory = MagicMock()
        mock_factory.validate_data.return_value = (MagicMock(), None)
        mock_factory_class.return_value = mock_factory

        mock_get_client.return_value.__aenter__.return_value = mock_client
        mock_get_client.return_value.__aexit__.return_value = None

        # Create temporary file with data
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "Alice"}, f)
            temp_file = f.name

        try:
            result = self.runner.invoke(app, ["models", "validate", "person", temp_file])
            assert result.exit_code == 0
            assert "Data is valid" in result.stdout
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
