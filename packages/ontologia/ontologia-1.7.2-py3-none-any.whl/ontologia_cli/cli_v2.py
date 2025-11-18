"""
Ontologia CLI v2 - Unified command-line interface using the new SDK.

Provides a modern, intuitive CLI experience with dual-mode support,
rich output formatting, and comprehensive command coverage.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import typer
import typer.colors
import yaml
from ontologia_sdk import OntologyClient, create_local_client, create_remote_client
from ontologia_sdk.model_factory import ModelFactory
from ontologia_sdk.query_builder import QueryExecutor, query
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

# Setup rich console for beautiful output
console = Console()
app = typer.Typer(
    name="ontologia",
    help="Ontologia CLI v2 - Unified interface for ontology operations",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Global configuration
config_file = Path.home() / ".ontologia" / "config.yaml"


class CLIConfig:
    """CLI configuration management."""

    def __init__(self):
        self.host: str | None = None
        self.token: str | None = None
        self.connection_string: str | None = None
        self.ontology: str = "default"
        self.timeout: float = 30.0
        self.output_format: str = "table"  # table, json, yaml
        self.verbose: bool = False

    def load(self):
        """Load configuration from file."""
        if config_file.exists():
            try:
                with open(config_file) as f:
                    data = yaml.safe_load(f)
                    if data:
                        for key, value in data.items():
                            if hasattr(self, key):
                                setattr(self, key, value)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")

    def save(self):
        """Save configuration to file."""
        config_file.parent.mkdir(exist_ok=True)
        data = {
            "host": self.host,
            "token": self.token,
            "connection_string": self.connection_string,
            "ontology": self.ontology,
            "timeout": self.timeout,
            "output_format": self.output_format,
            "verbose": self.verbose,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


# Global config instance
cli_config = CLIConfig()
cli_config.load()


def get_client() -> OntologyClient:
    """Get configured OntologyClient."""
    # Prefer an explicit local connection string over host, to avoid
    # accidentally hitting remote when both are present from prior state.
    if cli_config.connection_string:
        client = create_local_client(
            connection_string=cli_config.connection_string, ontology=cli_config.ontology
        )
    elif cli_config.host:
        client = create_remote_client(
            host=cli_config.host,
            token=cli_config.token,
            ontology=cli_config.ontology,
            timeout=cli_config.timeout,
        )
    else:
        console.print("[red]Error: No configuration found. Use 'ontologia config' to set up.[/red]")
        raise typer.Exit(1)

    return client  # type: ignore[return-value]


def format_output(data: Any, format_type: str | None = None) -> str:
    """Format data for output."""
    fmt = format_type or cli_config.output_format

    if fmt == "json":
        return json.dumps(data, indent=2, default=str)
    elif fmt == "yaml":
        return yaml.dump(data, default_flow_style=False)
    elif fmt == "table":
        if isinstance(data, list) and data:
            return format_table(data)
        elif isinstance(data, dict):
            return format_dict_as_table(data)
        else:
            return str(data)
    else:
        return str(data)


def format_table(data: list[dict[str, Any]]) -> str:
    """Format list of dictionaries as a table."""
    if not data:
        return "No data"

    # Get all keys from all items
    keys = set()
    for item in data:
        keys.update(item.keys())
    keys = sorted(list(keys))

    table = Table(show_header=True, header_style="bold magenta")

    # Add columns
    for key in keys:
        table.add_column(key, style="cyan", no_wrap=False)

    # Add rows
    for item in data:
        row = []
        for key in keys:
            value = item.get(key, "")
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            row.append(str(value))
        table.add_row(*row)

    # Capture table output
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_dict_as_table(data: dict[str, Any]) -> str:
    """Format dictionary as a two-column table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2, default=str)
        table.add_row(key, str(value))

    with console.capture() as capture:
        console.print(table)
    return capture.get()


async def run_async(func):
    """Run async function with proper error handling."""
    try:
        return await func()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if cli_config.verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


# Configuration commands
config_app = typer.Typer(name="config", help="Manage CLI configuration")
app.add_typer(config_app)


@config_app.command("show")
def config_show():
    """Show current configuration."""
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    config_data = {
        "Host": cli_config.host or "Not set",
        "Token": "***" if cli_config.token else "Not set",
        "Connection String": cli_config.connection_string or "Not set",
        "Ontology": cli_config.ontology,
        "Timeout": f"{cli_config.timeout}s",
        "Output Format": cli_config.output_format,
        "Verbose": str(cli_config.verbose),
    }

    for key, value in config_data.items():
        table.add_row(key, value)

    console.print(table)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
):
    """Set a configuration value."""
    valid_keys = [
        "host",
        "token",
        "connection_string",
        "ontology",
        "timeout",
        "output_format",
        "verbose",
    ]

    if key not in valid_keys:
        console.print(f"[red]Invalid key. Valid keys: {', '.join(valid_keys)}[/red]")
        raise typer.Exit(1)

    # Type conversion
    if key == "timeout":
        try:
            value = float(value)  # type: ignore[assignment]
        except ValueError:
            console.print("[red]Timeout must be a number[/red]")
            raise typer.Exit(1)
    elif key == "verbose":
        # Store as a real boolean, not a string
        value = value.lower() in ["true", "1", "yes", "on"]  # type: ignore[assignment]

    setattr(cli_config, key, value)
    cli_config.save()
    console.print(f"[green]✓[/green] Set {key} = {value}")


@config_app.command("remote")
def config_remote(
    host: str = typer.Option(..., help="API host URL"),
    token: str | None = typer.Option(None, help="API token"),
    ontology: str = typer.Option("default", help="Ontology name"),
    timeout: float = typer.Option(30.0, help="Request timeout"),
):
    """Configure for remote mode."""
    cli_config.host = host
    cli_config.token = token
    cli_config.connection_string = None
    cli_config.ontology = ontology
    cli_config.timeout = timeout
    cli_config.save()
    console.print(f"[green]✓[/green] Configured for remote mode: {host}")


@config_app.command("local")
def config_local(
    connection_string: str = typer.Option(..., help="Database connection string"),
    ontology: str = typer.Option("default", help="Ontology name"),
):
    """Configure for local mode."""
    cli_config.connection_string = connection_string
    cli_config.host = None
    cli_config.token = None
    cli_config.ontology = ontology
    cli_config.save()
    console.print("[green]✓[/green] Configured for local mode")


# Object type commands
object_type_app = typer.Typer(name="types", help="Manage object types")
app.add_typer(object_type_app)


@object_type_app.command("list")
def list_object_types(
    format: str | None = typer.Option(None, "--format", "-f", help="Output format")
):
    """List all object types."""

    async def _list():
        client = get_client()
        async with client as c:
            types = await c.list_object_types()
            output = format_output(types, format)
            console.print(output)

    asyncio.run(run_async(_list))


@object_type_app.command("get")
def get_object_type(
    api_name: str = typer.Argument(..., help="Object type API name"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
):
    """Get object type details."""

    async def _get():
        client = get_client()
        async with client as c:
            obj_type = await c.get_object_type(api_name)
            if obj_type:
                output = format_output(obj_type, format)
                console.print(output)
            else:
                console.print(f"[red]Object type '{api_name}' not found[/red]")
                raise typer.Exit(1)

    asyncio.run(run_async(_get))


@object_type_app.command("create")
def create_object_type(
    file: typer.FileText = typer.Argument(..., help="YAML/JSON file with object type definition"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
):
    """Create a new object type from file."""

    async def _create():
        try:
            # Parse file content
            content = file.read()
            if file.name.endswith(".yaml") or file.name.endswith(".yml"):
                data = yaml.safe_load(content)
            else:
                data = json.loads(content)

            client = get_client()
            async with client as c:
                obj_type = await c.create_object_type(data)
                output = format_output(obj_type, format)
                console.print("[green]✓[/green] Object type created successfully:")
                console.print(output)

        except Exception as e:
            console.print(f"[red]Error parsing file: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_async(_create))


# Object commands
object_app = typer.Typer(name="objects", help="Manage object instances")
app.add_typer(object_app)


@object_app.command("list")
def list_objects(
    object_type: str = typer.Argument(..., help="Object type name"),
    limit: int | None = typer.Option(None, "--limit", "-l", help="Limit results"),
    offset: int | None = typer.Option(None, "--offset", "-o", help="Offset results"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
    where: str | None = typer.Option(
        None, "--where", "-w", help="Where clause (field:operator:value)"
    ),
    order: str | None = typer.Option(None, "--order", help="Order by field (field:direction)"),
):
    """List objects of a type."""

    async def _list():
        client = get_client()
        async with client as c:
            # Build filters
            filters = {}
            if limit:
                filters["limit"] = limit
            if offset:
                filters["offset"] = offset

            # Parse where clause
            if where:
                try:
                    field, operator, value = where.split(":", 2)
                    filters[field] = value
                except ValueError:
                    console.print(
                        "[red]Invalid where clause. Use format: field:operator:value[/red]"
                    )
                    raise typer.Exit(1)

            objects = await c.list_objects(object_type, **filters)
            output = format_output(objects, format)
            console.print(output)

    asyncio.run(run_async(_list))


@object_app.command("get")
def get_object(
    object_type: str = typer.Argument(..., help="Object type name"),
    pk: str = typer.Argument(..., help="Object primary key"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
):
    """Get a specific object."""

    async def _get():
        client = get_client()
        async with client as c:
            obj = await c.get_object(object_type, pk)
            if obj:
                output = format_output(obj, format)
                console.print(output)
            else:
                console.print(f"[red]Object '{pk}' not found[/red]")
                raise typer.Exit(1)

    asyncio.run(run_async(_get))


@object_app.command("create")
def create_object(
    object_type: str = typer.Argument(..., help="Object type name"),
    file: typer.FileText = typer.Argument(..., help="YAML/JSON file with object data"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
):
    """Create a new object from file."""

    async def _create():
        try:
            # Parse file content
            content = file.read()
            if file.name.endswith(".yaml") or file.name.endswith(".yml"):
                data = yaml.safe_load(content)
            else:
                data = json.loads(content)

            client = get_client()
            async with client as c:
                obj = await c.create_object(object_type, data)
                output = format_output(obj, format)
                console.print("[green]✓[/green] Object created successfully:")
                console.print(output)

        except Exception as e:
            console.print(f"[red]Error parsing file: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_async(_create))


@object_app.command("update")
def update_object(
    object_type: str = typer.Argument(..., help="Object type name"),
    pk: str = typer.Argument(..., help="Object primary key"),
    file: typer.FileText = typer.Argument(..., help="YAML/JSON file with update data"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
):
    """Update an object from file."""

    async def _update():
        try:
            # Parse file content
            content = file.read()
            if file.name.endswith(".yaml") or file.name.endswith(".yml"):
                data = yaml.safe_load(content)
            else:
                data = json.loads(content)

            client = get_client()
            async with client as c:
                obj = await c.update_object(object_type, pk, data)
                output = format_output(obj, format)
                console.print("[green]✓[/green] Object updated successfully:")
                console.print(output)

        except Exception as e:
            console.print(f"[red]Error parsing file: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_async(_update))


@object_app.command("delete")
def delete_object(
    object_type: str = typer.Argument(..., help="Object type name"),
    pk: str = typer.Argument(..., help="Object primary key"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation"),
):
    """Delete an object."""

    async def _delete():
        if not confirm:
            if not typer.confirm(f"Delete object '{pk}' of type '{object_type}'?"):
                console.print("Cancelled")
                raise typer.Exit()

        client = get_client()
        async with client as c:
            success = await c.delete_object(object_type, pk)
            if success:
                console.print("[green]✓[/green] Object deleted successfully")
            else:
                console.print(f"[red]Failed to delete object '{pk}'[/red]")
                raise typer.Exit(1)

    asyncio.run(run_async(_delete))


# Query commands
query_app = typer.Typer(name="query", help="Execute queries")
app.add_typer(query_app)


@query_app.command("build")
def query_build(
    object_type: str = typer.Argument(..., help="Object type to query"),
    where: list[str] | None = typer.Option(None, "--where", "-w", help="Where conditions"),
    order: list[str] | None = typer.Option(None, "--order", help="Order by fields"),
    limit: int | None = typer.Option(None, "--limit", "-l", help="Limit results"),
    offset: int | None = typer.Option(None, "--offset", "-o", help="Offset results"),
    sql: bool = typer.Option(False, "--sql", help="Show SQL representation"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format"),
):
    """Build and execute a query."""

    async def _query():
        # Build query
        builder = query(object_type)

        # Add where conditions
        if where:
            for condition in where:
                try:
                    field, operator, value = condition.split(":", 2)
                    builder.where(field, operator, value)
                except ValueError:
                    console.print(f"[red]Invalid where clause: {condition}[/red]")
                    raise typer.Exit(1)

        # Add ordering
        if order:
            for order_field in order:
                if ":" in order_field:
                    field, direction = order_field.split(":", 1)
                    builder.order_by(field, direction)
                else:
                    builder.order_by_asc(order_field)

        # Add pagination
        if limit:
            builder.limit(limit)
        if offset:
            builder.offset(offset)

        if sql:
            console.print(Panel(builder.build_sql(), title="SQL Representation"))

        # Execute query
        client = get_client()
        executor = QueryExecutor(client)

        async with client as c:
            results = await executor.execute(builder)
            output = format_output(results, format)
            console.print(output)

    asyncio.run(run_async(_query))


@query_app.command("count")
def query_count(
    object_type: str = typer.Argument(..., help="Object type to query"),
    where: list[str] | None = typer.Option(None, "--where", "-w", help="Where conditions"),
):
    """Count query results."""

    async def _count():
        # Build query
        builder = query(object_type)

        # Add where conditions
        if where:
            for condition in where:
                try:
                    field, operator, value = condition.split(":", 2)
                    builder.where(field, operator, value)
                except ValueError:
                    console.print(f"[red]Invalid where clause: {condition}[/red]")
                    raise typer.Exit(1)

        # Execute query
        client = get_client()
        executor = QueryExecutor(client)

        async with client as c:
            count = await executor.count(builder)
            console.print(f"[green]Count: {count}[/green]")

    asyncio.run(run_async(_count))


# Model commands
model_app = typer.Typer(name="models", help="Manage dynamic models")
app.add_typer(model_app)


@model_app.command("generate")
def model_generate(
    object_type: str = typer.Argument(..., help="Object type name"),
    output: typer.FileTextWrite | None = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate Pydantic model for object type."""

    async def _generate():
        client = get_client()
        async with client as c:
            # Get object type definition
            obj_type = await c.get_object_type(object_type)
            if not obj_type:
                console.print(f"[red]Object type '{object_type}' not found[/red]")
                raise typer.Exit(1)

            # Generate model
            factory = ModelFactory()
            model = factory.create_model(obj_type)

            # Generate model code
            model_code = f"""
# Auto-generated model for {object_type}
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

{model.__name__} = {repr(model)}

# Example usage:
# instance = {model.__name__}(
#     pk="example-id",
#     # ... other fields
# )
"""

            if output:
                output.write(model_code)
                console.print(f"[green]✓[/green] Model generated and saved to {output.name}")
            else:
                console.print(
                    Panel(Syntax(model_code, "python"), title=f"Generated Model: {model.__name__}")
                )

    asyncio.run(run_async(_generate))


@model_app.command("validate")
def model_validate(
    object_type: str = typer.Argument(..., help="Object type name"),
    file: typer.FileText = typer.Argument(..., help="File with data to validate"),
):
    """Validate data against object type model."""

    async def _validate():
        try:
            # Parse file content
            content = file.read()
            if file.name.endswith(".yaml") or file.name.endswith(".yml"):
                data = yaml.safe_load(content)
            else:
                data = json.loads(content)

            client = get_client()
            async with client as c:
                # Get object type definition
                obj_type = await c.get_object_type(object_type)
                if not obj_type:
                    console.print(f"[red]Object type '{object_type}' not found[/red]")
                    raise typer.Exit(1)

                # Validate data
                factory = ModelFactory()
                model, error = factory.validate_data(object_type, data)

                if error:
                    console.print("[red]Validation failed:[/red]")
                    console.print(error)
                    raise typer.Exit(1)
                else:
                    console.print("[green]✓[/green] Data is valid")
                    # Optional pretty print omitted for robustness in mixed environments

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_async(_validate))


# Utility commands
@app.command("status")
def status():
    """Show connection status and information."""

    async def _status():
        try:
            client = get_client()
            async with client as _c:
                # Test connection by listing object types
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Testing connection...", total=None)

                    # Prefer calling on the outer client to work with simple mocks
                    object_types = await client.list_object_types()

                    progress.update(task, description="Connection successful")

                # Create status panel
                status_data = {
                    "Mode": client.mode.upper(),
                    "Ontology": client.ontology,
                    "Object Types": len(object_types),
                    "Connection": "✓ Healthy",
                }

                table = Table(title="Connection Status")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                for key, value in status_data.items():
                    table.add_row(key, str(value))

                console.print(table)

        except Exception as e:
            console.print(f"[red]Connection failed: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_async(_status))


@app.command("version")
def version():
    """Show CLI and SDK version information."""
    console.print(
        Panel.fit(
            "[bold cyan]Ontologia CLI v2.0.0[/bold cyan]\n"
            "[dim]Built with the new unified SDK[/dim]\n"
            "[dim]Featuring dual-mode operation and rich output[/dim]",
            title="Version Information",
        )
    )


def main():
    """Main entry point."""
    # Setup logging
    if cli_config.verbose:
        logging.basicConfig(level=logging.DEBUG)

    app()


if __name__ == "__main__":
    main()
