from __future__ import annotations

# ruff: noqa: FBT002
import asyncio
import json
import os
import secrets
import shutil
import socket
import subprocess
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Literal

import httpx
import questionary
import typer
from git import Actor, Repo
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlalchemy import true
from typer.testing import CliRunner

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

from ontologia_agent import AgentPlan, ArchitectAgent, ProjectState
from ontologia_api.v2.schemas.metamodel import LinkTypePutRequest, ObjectTypePutRequest

from ontologia.ogm.errors import ConnectionNotInitialized
from ontologia.ogm.migration_errors import DangerousMigrationError
from ontologia.ogm.python_definitions import load_python_definitions
from ontologia.ogm.schema import apply_schema as ogm_apply_schema
from ontologia_cli.config import load_config

# CLI Apps
app = typer.Typer(add_completion=False, help="Ontology as Code CLI")
projects_app = typer.Typer(help="Manage local Ontologia projects.")
pipeline_app = typer.Typer(help="Orchestrate Ontologia data pipelines.")
graph_app = typer.Typer(help="Manage Kùzu graph storage.")
migrations_app = typer.Typer(help="Execute schema migration tasks.")
new_app = typer.Typer(help="Create new ontology definitions interactively.")
changeset_app = typer.Typer(help="Manage change sets for what-if scenarios.")
app.add_typer(projects_app, name="projects")
app.add_typer(pipeline_app, name="pipeline")
app.add_typer(graph_app, name="graph")
app.add_typer(migrations_app, name="migrations")
app.add_typer(new_app, name="new")
app.add_typer(changeset_app, name="changeset")

console = Console()

CONFIG_DIR = Path.home() / ".ontologia"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOCAL_STATE_DIR = ".ontologia"
LOCAL_STATE_FILE = "state.json"

_CONFIG = load_config()
DEFAULT_HOST = _CONFIG.api.base_url
DEFAULT_ONTOLOGY = _CONFIG.api.ontology
DEFAULT_DEFINITIONS_DIR = _CONFIG.project.definitions_dir
DEFAULT_SDK_DIR = _CONFIG.sdk.output_dir


@dataclass
class PlanItem:
    kind: str  # objectType | linkType
    api_name: str
    action: str  # create | update | delete
    dangerous: bool = False
    reasons: list[str] = field(default_factory=list)


def _load_yaml_file(path: str) -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml is required. Install with: uvx pip install pyyaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _collect_definitions(root_dir: str) -> tuple[dict[str, dict], dict[str, dict]]:
    obj_dir = os.path.join(root_dir, "object_types")
    link_dir = os.path.join(root_dir, "link_types")
    objs: dict[str, dict] = {}
    links: dict[str, dict] = {}

    if os.path.isdir(obj_dir):
        for fn in os.listdir(obj_dir):
            if fn.endswith((".yml", ".yaml")):
                raw = _load_yaml_file(os.path.join(obj_dir, fn))
                api_name = str(raw.get("apiName") or os.path.splitext(fn)[0])
                objs[api_name] = raw

    if os.path.isdir(link_dir):
        for fn in os.listdir(link_dir):
            if fn.endswith((".yml", ".yaml")):
                raw = _load_yaml_file(os.path.join(link_dir, fn))
                api_name = str(raw.get("apiName") or os.path.splitext(fn)[0])
                links[api_name] = raw

    return objs, links


def _validate_local(objs: dict[str, dict], links: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    for api_name, raw in objs.items():
        body = {k: v for k, v in raw.items() if k != "apiName"}
        try:
            ObjectTypePutRequest(**body)
        except ValidationError as ve:
            errors.append(f"ObjectType '{api_name}' invalid: {ve}")
    for api_name, raw in links.items():
        body = {k: v for k, v in raw.items() if k != "apiName"}
        try:
            LinkTypePutRequest(**body)
        except ValidationError as ve:
            errors.append(f"LinkType '{api_name}' invalid: {ve}")
    return errors


def fetch_server_state(host: str, ontology: str) -> tuple[dict[str, dict], dict[str, dict]]:
    """Fetch object and link types from the server."""
    base = host.rstrip("/") + f"/v2/ontologies/{ontology}"
    with httpx.Client(timeout=30) as client:
        obj_resp = client.get(base + "/objectTypes")
        obj_resp.raise_for_status()
        obj_data = obj_resp.json().get("data", [])

        link_resp = client.get(base + "/linkTypes")
        link_resp.raise_for_status()
        link_data = link_resp.json().get("data", [])

        objs_remote = {obj["apiName"]: obj for obj in obj_data}
        links_remote = {link["apiName"]: link for link in link_data}

        return objs_remote, links_remote


def _fetch_server_state(host: str, ontology: str) -> tuple[dict[str, dict], dict[str, dict]]:
    """Internal wrapper for fetch_server_state."""
    return fetch_server_state(host, ontology)


def _plan(
    objs_local: dict[str, dict],
    links_local: dict[str, dict],
    objs_remote: dict[str, dict],
    links_remote: dict[str, dict],
) -> list[PlanItem]:
    plan: list[PlanItem] = []
    for api_name in objs_local.keys():
        if api_name not in objs_remote:
            plan.append(PlanItem("objectType", api_name, "create"))
        else:
            local = objs_local[api_name]
            remote = objs_remote[api_name]
            if (
                (local.get("displayName") != remote.get("displayName"))
                or (local.get("properties") != remote.get("properties"))
                or (local.get("primaryKey") != remote.get("primaryKey"))
            ):
                reasons: list[str] = []
                if local.get("primaryKey") != remote.get("primaryKey"):
                    reasons.append("primaryKey change")
                remote_props = dict(remote.get("properties") or {})
                local_props = dict(local.get("properties") or {})
                for prop_name in remote_props.keys() - local_props.keys():
                    reasons.append(f"property removed: {prop_name}")
                for prop_name, local_prop in local_props.items():
                    if prop_name not in remote_props:
                        continue
                    remote_prop = remote_props.get(prop_name) or {}
                    if (local_prop or {}).get("dataType") != remote_prop.get("dataType"):
                        reasons.append(
                            f"property type change: {prop_name} ({remote_prop.get('dataType')}→{(local_prop or {}).get('dataType')})"
                        )
                plan.append(
                    PlanItem(
                        "objectType",
                        api_name,
                        "update",
                        dangerous=bool(reasons),
                        reasons=reasons,
                    )
                )
    for api_name in set(objs_remote.keys()) - set(objs_local.keys()):
        plan.append(PlanItem("objectType", api_name, "delete", dangerous=True, reasons=["delete"]))
    for api_name in links_local.keys():
        if api_name not in links_remote:
            plan.append(PlanItem("linkType", api_name, "create"))
        else:
            local = links_local[api_name]
            remote = links_remote[api_name]
            fields = [
                "displayName",
                "cardinality",
                "fromObjectType",
                "toObjectType",
                "inverse",
                "description",
                "properties",
                "backingDatasetApiName",
                "fromPropertyMapping",
                "toPropertyMapping",
                "propertyMappings",
                "incrementalField",
            ]
            if any(local.get(f) != remote.get(f) for f in fields):
                reasons: list[str] = []
                if local.get("fromObjectType") != remote.get("fromObjectType") or local.get(
                    "toObjectType"
                ) != remote.get("toObjectType"):
                    reasons.append("endpoint change")
                plan.append(
                    PlanItem(
                        "linkType",
                        api_name,
                        "update",
                        dangerous=bool(reasons),
                        reasons=reasons,
                    )
                )
    for api_name in set(links_remote.keys()) - set(links_local.keys()):
        plan.append(PlanItem("linkType", api_name, "delete", dangerous=True, reasons=["delete"]))
    return plan


def _apply(
    host: str,
    ontology: str,
    plan: list[PlanItem],
    objs_local: dict[str, dict],
    links_local: dict[str, dict],
    *,
    allow_destructive: bool = False,
) -> None:
    base = host.rstrip("/") + f"/v2/ontologies/{ontology}"
    with httpx.Client(timeout=30) as client:
        for item in plan:
            try:
                if item.dangerous and not allow_destructive:
                    raise RuntimeError(
                        f"Refusing dangerous {item.kind} {item.api_name} without --allow-destructive"
                    )
                if item.action == "delete":
                    if not allow_destructive:
                        raise RuntimeError(
                            f"Refusing to delete {item.kind} {item.api_name} without --allow-destructive"
                        )
                    if item.kind == "objectType":
                        client.delete(base + f"/objectTypes/{item.api_name}").raise_for_status()
                    else:
                        client.delete(base + f"/linkTypes/{item.api_name}").raise_for_status()
                elif item.kind == "objectType":
                    body = {k: v for k, v in objs_local[item.api_name].items() if k != "apiName"}
                    client.put(base + f"/objectTypes/{item.api_name}", json=body).raise_for_status()
                else:
                    body = {k: v for k, v in links_local[item.api_name].items() if k != "apiName"}
                    client.put(base + f"/linkTypes/{item.api_name}", json=body).raise_for_status()
                print(f"[OK] {item.action.upper()} {item.kind} {item.api_name}")
            except httpx.HTTPError as e:
                print(f"[ERR] {item.kind} {item.api_name}: {e}")
                raise


def _display_plan_table(plan: list[PlanItem]) -> None:
    """Display migration plan in a rich table format."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Action", style="bold")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    for p in plan:
        # Determine status color and text
        if p.action == "create":
            status_style = "green"
            status_text = "✓ CREATE"
        elif p.action == "delete":
            status_style = "red"
            status_text = "✗ DELETE"
        elif p.action == "update":
            if p.dangerous:
                status_style = "yellow"
                status_text = "⚠ UPDATE"
            else:
                status_style = "blue"
                status_text = "→ UPDATE"
        else:
            status_style = "white"
            status_text = p.action.upper()

        dangerous_tag = " [DANGEROUS]" if p.dangerous else ""
        extra = f" ({', '.join(p.reasons)})" if p.reasons else ""

        table.add_row(
            p.action.upper(),
            p.kind,
            p.api_name,
            f"[{status_style}]{status_text}[/{status_style}]{dangerous_tag}",
            extra,
        )

    console.print("[bold]Migration plan:[/bold]")
    console.print(table)


def _apply_with_progress(
    host: str,
    ontology: str,
    plan: list[PlanItem],
    objs_local: dict[str, dict],
    links_local: dict[str, dict],
    *,
    allow_destructive: bool = False,
    progress: Progress,
    task: Any,
) -> None:
    base = host.rstrip("/") + f"/v2/ontologies/{ontology}"
    with httpx.Client(timeout=30) as client:
        for item in plan:
            try:
                # Update progress description
                progress.update(
                    task, description=f"{item.action.upper()} {item.kind} {item.api_name}..."
                )

                if item.dangerous and not allow_destructive:
                    raise RuntimeError(
                        f"Refusing dangerous {item.kind} {item.api_name} without --allow-destructive"
                    )
                if item.action == "delete":
                    if not allow_destructive:
                        raise RuntimeError(
                            f"Refusing to delete {item.kind} {item.api_name} without --allow-destructive"
                        )
                    if item.kind == "objectType":
                        client.delete(base + f"/objectTypes/{item.api_name}").raise_for_status()
                    else:
                        client.delete(base + f"/linkTypes/{item.api_name}").raise_for_status()
                elif item.kind == "objectType":
                    body = {k: v for k, v in objs_local[item.api_name].items() if k != "apiName"}
                    client.put(base + f"/objectTypes/{item.api_name}", json=body).raise_for_status()
                else:
                    body = {k: v for k, v in links_local[item.api_name].items() if k != "apiName"}
                    client.put(base + f"/linkTypes/{item.api_name}", json=body).raise_for_status()

                # Show success with rich formatting
                if item.action == "create":
                    console.print(
                        f"[green]✓ Created[/green] {item.kind} [cyan]{item.api_name}[/cyan]"
                    )
                elif item.action == "delete":
                    console.print(f"[red]✗ Deleted[/red] {item.kind} [cyan]{item.api_name}[/cyan]")
                elif item.action == "update":
                    if item.dangerous:
                        console.print(
                            f"[yellow]⚠ Updated (dangerous)[/yellow] {item.kind} [cyan]{item.api_name}[/cyan]"
                        )
                    else:
                        console.print(
                            f"[blue]→ Updated[/blue] {item.kind} [cyan]{item.api_name}[/cyan]"
                        )

                # Update progress
                progress.update(task, advance=1)
            except httpx.HTTPError as e:
                console.print(f"[red]✗ Failed[/red] {item.kind} [cyan]{item.api_name}[/cyan]: {e}")
                raise


def _to_camel(name: str) -> str:
    parts = [p for p in str(name).replace("-", "_").split("_") if p]
    return "".join(s[:1].upper() + s[1:] for s in parts) or "X"


def _ensure_python_plan_safe(plan: list[PlanItem], allow_destructive: bool) -> None:
    deletes = [p for p in plan if p.action == "delete"]
    if deletes:
        listing = ", ".join(f"{item.kind}:{item.api_name}" for item in deletes)
        raise RuntimeError(
            "Python source mode does not support deletions. Include all remote types or switch to --source yaml."
            f" Pending deletes: {listing}"
        )
    if not allow_destructive and any(item.dangerous for item in plan):
        raise RuntimeError(
            "Dangerous changes detected. Re-run with --allow-destructive to continue in python mode."
        )


def _apply_python_plan(
    plan: list[PlanItem], *, allow_destructive: bool
) -> dict[str, tuple[bool, str]]:
    if not plan:
        return {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Applying schema via OGM...", total=1)
        try:
            results = ogm_apply_schema(allow_destructive=allow_destructive)
        except DangerousMigrationError as exc:
            progress.update(task, completed=True)
            raise RuntimeError(str(exc)) from exc
        except ConnectionNotInitialized as exc:
            progress.update(task, completed=True)
            raise RuntimeError(
                "OGM connection is not initialized. Call ontologia.ogm.connect before running apply --source python."
            ) from exc
        progress.update(task, advance=1)
    return results


def _print_python_apply_results(plan: list[PlanItem], results: dict[str, tuple[bool, str]]) -> None:
    if not plan:
        console.print("[green]No changes detected.[/green]")
        return

    seen = set()
    for item in plan:
        success, message = results.get(item.api_name, (True, "Applied"))
        seen.add(item.api_name)
        style = "green" if success else "red"
        symbol = "✓" if success else "✗"
        console.print(f"[{style}]{symbol}[/] {item.kind} [cyan]{item.api_name}[/cyan]: {message}")

    extra = {k: v for k, v in results.items() if k not in seen}
    for api_name, (success, message) in extra.items():
        style = "green" if success else "red"
        symbol = "✓" if success else "✗"
        console.print(f"[{style}]{symbol}[/] [cyan]{api_name}[/cyan]: {message}")


def _py_type_of(data_type: str, *, required: bool) -> str:
    mapping = {
        "string": "str",
        "integer": "int",
        "double": "float",
        "boolean": "bool",
        "date": "datetime.date",
        "timestamp": "datetime.datetime",
    }
    base = mapping.get(str(data_type), "typing.Any")
    return base if required else f"{base} | None"


def _python_literal(value: object) -> str:
    if isinstance(value, dict):
        inner = ", ".join(f'"{k}": {_python_literal(v)}' for k, v in value.items())
        return "{" + inner + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_python_literal(v) for v in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is True:
        return "True"
    if value is False:
        return "False"
    if value is None:
        return "None"
    return repr(value)


def _generate_objects_module(
    out_dir: str, objs_remote: dict[str, dict], links_remote: dict[str, dict]
) -> None:
    os.makedirs(out_dir, exist_ok=True)
    link_classes = sorted([_to_camel(lt_api) + "LinkProperties" for lt_api in links_remote.keys()])
    object_classes = sorted([_to_camel(api_name) for api_name in objs_remote.keys()])

    init_path = os.path.join(out_dir, "__init__.py")
    with open(init_path, "w", encoding="utf-8") as f:
        f.write("# Generated by ontologia-cli generate-sdk\n")
        if link_classes:
            f.write("from .links import " + ", ".join(link_classes) + "\n")
        if object_classes:
            f.write("from .objects import " + ", ".join(object_classes) + "\n")
        names = link_classes + object_classes
        if names:
            f.write("\n__all__ = [" + ", ".join(f'"{n}"' for n in names) + "]\n")

    uses_datetime = False
    for ot in objs_remote.values():
        for prop_def in (ot.get("properties") or {}).values():
            if str(prop_def.get("dataType")) in {"date", "timestamp"}:
                uses_datetime = True
                break
        if uses_datetime:
            break

    import_lines: list[str] = ["from __future__ import annotations", ""]
    if uses_datetime:
        import_lines.append("import datetime")
    import_lines.append("import typing")
    import_lines.append("")
    import_lines.extend(
        [
            "from ontologia_sdk.actions import ObjectActionsNamespace",
            "from ontologia_sdk.client import OntologyClient",
            "from ontologia_sdk.dsl import FieldDescriptor",
            "from ontologia_sdk.link_proxy import LinkDescriptor",
            "from ontologia_sdk.query import QueryBuilder",
            "from ontologia_sdk.types import Page",
        ]
    )
    if link_classes:
        import_lines.append("")
        import_lines.append("from .links import " + ", ".join(link_classes))
    import_lines.append("")
    import_lines += [
        "",
        "class ObjectTypeMeta(type):",
        "    def __getattr__(cls, item: str) -> FieldDescriptor:",
        '        fields = getattr(cls, "__fields__", {})',
        "        if item in fields:",
        "            return FieldDescriptor(cls.object_type_api_name, item, fields[item])",
        "        raise AttributeError(item)",
        "",
        "class BaseObject(metaclass=ObjectTypeMeta):",
        '    object_type_api_name: str = ""',
        '    primary_key: str = ""',
        "    __fields__: dict[str, dict[str, typing.Any]] = {}",
        "",
        "    def __init__(self, client: OntologyClient, rid: str, pkValue: str, properties: dict[str, typing.Any]):",
        "        self._client = client",
        "        self.rid = rid",
        "        self.pk = pkValue",
        "        for k, v in dict(properties or {}).items():",
        "            setattr(self, k, v)",
        '        shared_actions = getattr(client, "actions", None)',
        "        self.actions = ObjectActionsNamespace(",
        "            client=client,",
        "            object_type=self.object_type_api_name,",
        "            pk_getter=lambda: self.pk,",
        "            shared_namespace=shared_actions,",
        "        )",
        "",
        "    @classmethod",
        "    def get(cls, client: OntologyClient, pk: str):",
        "        data = client.get_object(cls.object_type_api_name, pk)",
        "        return cls.from_response(client, data)",
        "",
        "    @classmethod",
        "    def from_response(cls, client: OntologyClient, data: dict[str, typing.Any]):",
        '        props = dict(data.get("properties") or {})',
        '        return cls(client, data.get("rid", ""), str(data.get("pkValue", "")), props)',
        "",
        "    @classmethod",
        "    def search(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        limit: int = 100,",
        "        offset: int = 0,",
        "    ):",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(limit)",
        "        qb.offset(offset)",
        "        return qb.all()",
        "",
        "    @classmethod",
        "    def search_typed(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        limit: int = 100,",
        "        offset: int = 0,",
        "    ) -> Page[typing.Any]:",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(limit)",
        "        qb.offset(offset)",
        "        return qb.all_typed()",
        "",
        "    @classmethod",
        "    def iter_search(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        page_size: int = 100,",
        "        offset: int = 0,",
        "    ):",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(page_size)",
        "        qb.offset(offset)",
        "        return qb.iter_pages(page_size=page_size)",
        "",
        "    @classmethod",
        "    def iter_search_typed(",
        "        cls,",
        "        client: OntologyClient,",
        "        where: list[dict] | None = None,",
        "        order_by: list[dict] | None = None,",
        "        page_size: int = 100,",
        "        offset: int = 0,",
        "    ):",
        "        qb = cls.search_builder(client)",
        "        if where:",
        "            qb.where(where)",
        "        if order_by:",
        "            qb.order_by(order_by)",
        "        qb.limit(page_size)",
        "        qb.offset(offset)",
        "        return qb.iter_pages_typed(page_size=page_size)",
        "",
        "    @classmethod",
        "    def search_builder(cls, client: OntologyClient) -> QueryBuilder:",
        "        return QueryBuilder(client=client, object_type=cls.object_type_api_name, object_cls=cls)",
        "",
        "    @classmethod",
        "    def field(cls, name: str) -> FieldDescriptor:",
        '        fields = getattr(cls, "__fields__", {})',
        "        if name not in fields:",
        "            raise AttributeError(name)",
        "        return FieldDescriptor(cls.object_type_api_name, name, fields[name])",
        "",
        "    def list_actions(self):",
        "        return self._client.list_actions(self.object_type_api_name, self.pk)",
        "",
        "    def execute_action(self, action_api_name: str, parameters: dict[str, typing.Any] | None = None):",
        "        return self._client.execute_action(self.object_type_api_name, self.pk, action_api_name, parameters)",
        "",
    ]

    body_lines: list[str] = []
    ot_to_out_links: dict[str, list[str]] = {}
    for lt_api, lt in links_remote.items():
        src = str(lt.get("fromObjectType") or "")
        if src:
            ot_to_out_links.setdefault(src, []).append(lt_api)
    for api_name in sorted(objs_remote.keys()):
        ot = objs_remote[api_name] or {}
        cls_name = _to_camel(api_name)
        pk = str(ot.get("primaryKey") or "id")
        props: dict = dict(ot.get("properties") or {})
        body_lines.append("")
        body_lines.append(f"class {cls_name}(BaseObject):")
        body_lines.append(f'    object_type_api_name = "{api_name}"')
        body_lines.append(f'    primary_key = "{pk}"')
        if props:
            body_lines.append("    __fields__ = {")
            for prop_name, prop_def in props.items():
                serialized = _python_literal(prop_def)
                body_lines.append(f'        "{prop_name}": {serialized},')
            body_lines.append("    }")
        else:
            body_lines.append("    __fields__: dict[str, dict[str, typing.Any]] = {}")
        type_lines: list[str] = []
        for prop_name, prop_def in props.items():
            dt = _py_type_of(
                str(prop_def.get("dataType")), required=bool(prop_def.get("required", False))
            )
            type_lines.append(f"        {prop_name}: {dt}  # noqa: N815")
        if type_lines:
            body_lines.append("    if typing.TYPE_CHECKING:")
            body_lines.extend(type_lines)
        for lt_api in sorted(ot_to_out_links.get(api_name, [])):
            lt = links_remote.get(lt_api) or {}
            to_object = str(lt.get("toObjectType") or "")
            props_cls_name = _to_camel(lt_api) + "LinkProperties"
            body_lines.append("")
            body_lines.append(
                f'    {lt_api} = LinkDescriptor("{lt_api}", to_object_type="{to_object}", properties_cls={props_cls_name})'
            )
            body_lines.append("")
            body_lines.append(f"    # Links: {lt_api}")
            body_lines.append(
                f"    def traverse_{lt_api}(self, limit: int = 100, offset: int = 0):"
            )
            body_lines.append(
                f'        return self._client.traverse(self.object_type_api_name, self.pk, "{lt_api}", limit=limit, offset=offset)'
            )
            body_lines.append(f"    def get_{lt_api}_link(self, to_pk: str):")
            body_lines.append(f'        return self._client.get_link("{lt_api}", self.pk, to_pk)')
            cls_name = _to_camel(lt_api) + "LinkProperties"
            body_lines.append(f"    def get_{lt_api}_link_typed(self, to_pk: str):")
            body_lines.append(f'        raw = self._client.get_link("{lt_api}", self.pk, to_pk)')
            body_lines.append('        props = dict(raw.get("linkProperties") or {})')
            body_lines.append(f"        return {cls_name}.from_dict(props)")
            body_lines.append(
                f"    def create_{lt_api}(self, to_pk: str, properties: dict[str, typing.Any] | None = None):"
            )
            body_lines.append(
                f'        return self._client.create_link("{lt_api}", self.pk, to_pk, properties)'
            )
            body_lines.append(f"    def delete_{lt_api}(self, to_pk: str) -> None:")
            body_lines.append(
                f'        return self._client.delete_link("{lt_api}", self.pk, to_pk)'
            )
            body_lines.append(f"    def list_{lt_api}(self, to_pk: str | None = None):")
            body_lines.append(
                f'        return self._client.list_links("{lt_api}", from_pk=self.pk, to_pk=to_pk)'
            )
    path = os.path.join(out_dir, "objects.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(import_lines + body_lines) + "\n")


def _generate_links_module(out_dir: str, links_remote: dict[str, dict]) -> None:
    os.makedirs(out_dir, exist_ok=True)
    uses_datetime = any(
        str(prop_def.get("dataType")) in {"date", "timestamp"}
        for lt in links_remote.values()
        for prop_def in (lt.get("properties") or {}).values()
    )

    import_lines: list[str] = ["from __future__ import annotations", ""]
    if uses_datetime:
        import_lines.append("import datetime")
    import_lines.append("import typing")
    import_lines.append("")
    import_lines += [
        "",
        "class BaseLinkProperties:",
        '    link_type_api_name: str = ""',
        "",
        "    def __init__(self, **kwargs: typing.Any):",
        "        for k, v in kwargs.items():",
        "            setattr(self, k, v)",
        "",
        "    @classmethod",
        "    def from_dict(cls, data: dict[str, typing.Any]):",
        "        return cls(**dict(data or {}))",
        "",
    ]
    body_lines: list[str] = []
    for lt_api in sorted(links_remote.keys()):
        lt = links_remote[lt_api] or {}
        props: dict = dict(lt.get("properties") or {})
        cls_name = _to_camel(lt_api) + "LinkProperties"
        body_lines.append("")
        body_lines.append(f"class {cls_name}(BaseLinkProperties):")
        body_lines.append(f'    link_type_api_name = "{lt_api}"')
        for prop_name, prop_def in props.items():
            dt = _py_type_of(
                str(prop_def.get("dataType")), required=bool(prop_def.get("required", False))
            )
            body_lines.append(f"    {prop_name}: {dt} = None  # noqa: N815")
    path = os.path.join(out_dir, "links.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(import_lines + body_lines) + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _register_project(
    name: str,
    project_dir: Path,
    api_url: str,
    mcp_url: str,
    token: str,
    model_name: str,
    profile: str,
) -> None:
    data = _load_json(CONFIG_FILE)
    projects = data.setdefault("projects", {})
    projects[name] = {
        "path": str(project_dir),
        "api_url": api_url,
        "mcp_url": mcp_url,
        "agent_token": token,
        "model_name": model_name,
        "profile": profile,
    }
    data["current_project"] = name
    _save_json(CONFIG_FILE, data)


def _list_registered_projects() -> dict[str, dict[str, Any]]:
    data = _load_json(CONFIG_FILE)
    return data.get("projects", {})


def _find_local_state(start: Path) -> tuple[Path, dict[str, Any]] | None:
    for base in [start] + list(start.parents):
        candidate = base / LOCAL_STATE_DIR / LOCAL_STATE_FILE
        if candidate.exists():
            return base, _load_json(candidate)
    return None


def _write_local_state(project_dir: Path, data: dict[str, Any]) -> None:
    state_dir = project_dir / LOCAL_STATE_DIR
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / LOCAL_STATE_FILE
    _save_json(state_path, data)


def _load_project_state(model_override: str | None = None) -> ProjectState:
    local = _find_local_state(Path.cwd())
    if local:
        root_path, state_data = local
    else:
        config = _load_json(CONFIG_FILE)
        current = config.get("current_project")
        if not current:
            console.print(
                "[red]No Ontologia project context found. Run `ontologia genesis` first.[/red]"
            )
            raise typer.Exit(1)
        project_info = config.get("projects", {}).get(current)
        if not project_info:
            console.print(f"[red]Project '{current}' not found in registry.[/red]")
            raise typer.Exit(1)
        root_path = Path(project_info.get("path", "."))
        state_data = {
            "name": current,
            "api_url": project_info.get("api_url", DEFAULT_HOST),
            "mcp_url": project_info.get("mcp_url"),
            "agent_token": project_info.get("agent_token"),
            "model_name": project_info.get("model_name"),
        }
    if not root_path.exists():
        console.print(f"[red]Project directory '{root_path}' not found.[/red]")
        raise typer.Exit(1)
    name = state_data.get("name") or root_path.name
    api_url = state_data.get("api_url") or DEFAULT_HOST
    mcp_url = state_data.get("mcp_url") or api_url.rstrip("/") + "/mcp"
    token = state_data.get("agent_token") or state_data.get("token")
    if not token:
        console.print(
            "[red]Project state missing agent token. Re-run genesis or update state file.[/red]"
        )
        raise typer.Exit(1)
    model_name = model_override or state_data.get("model_name") or "openai:gpt-4o-mini"
    return ProjectState(
        name=name,
        root_path=root_path,
        api_url=api_url,
        mcp_url=mcp_url,
        agent_token=token,
        model_name=model_name,
    )


def _find_free_port(start: int) -> int:
    port = start
    while port < start + 1000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                port += 1
                continue
            return port
    raise RuntimeError("Unable to find a free port")


def _render_docker_compose(api_port: int, db_port: int, kuzu_port: int, profile: str) -> str:
    return (
        textwrap.dedent(
            f"""
        version: "3.9"
        services:
          api:
            image: ghcr.io/ontologiahq/ontologia-api:latest
            ports:
              - "{api_port}:8000"
            env_file:
              - .env
            depends_on:
              - postgres
              - kuzu
          postgres:
            image: postgres:15
            environment:
              POSTGRES_DB: ontologia
              POSTGRES_USER: ontologia
              POSTGRES_PASSWORD: ontologia
            ports:
              - "{db_port}:5432"
          kuzu:
            image: ghcr.io/kuzudb/kuzu:latest
            ports:
              - "{kuzu_port}:9075"
            volumes:
              - ./data/kuzu:/var/lib/kuzu
        """
        ).strip()
        + "\n"
    )


def _render_env_file(project_name: str, api_port: int, agent_token: str, profile: str) -> str:
    api_url = f"http://localhost:{api_port}"
    return (
        textwrap.dedent(
            f"""
        # Generated by ontologia genesis
        ONTOLOGIA_PROJECT={project_name}
        ONTOLOGIA_GENESIS_PROFILE={profile}
        ONTOLOGIA_API_URL={api_url}
        ONTOLOGIA_MCP_URL={api_url}/mcp
        ONTOLOGIA_AGENT_TOKEN={agent_token}
        POSTGRES_DB=ontologia
        POSTGRES_USER=ontologia
        POSTGRES_PASSWORD=ontologia
        JWT_SECRET_KEY={secrets.token_hex(32)}
        """
        ).strip()
        + "\n"
    )


def _render_gitignore() -> str:
    return (
        textwrap.dedent(
            """
        .env
        .ontologia/
        __pycache__/
        *.pyc
        data/
        dist/
        .DS_Store
        """
        ).strip()
        + "\n"
    )


def _render_readme(project_name: str) -> str:
    return (
        textwrap.dedent(
            f"""
        # {project_name}

        This project was scaffolded by `ontologia genesis`. It contains the local definitions for
        your Ontologia ecosystem. Common commands:

        ```bash
        ontologia validate --dir ontologia
        ontologia diff --dir ontologia --host http://localhost:8000 --ontology default
        ontologia agent
        ```
        """
        ).strip()
        + "\n"
    )


def _write_scaffold(
    project_dir: Path,
    *,
    project_name: str,
    api_port: int,
    db_port: int,
    kuzu_port: int,
    agent_token: str,
    model_name: str,
    profile: str,
) -> dict[str, Any]:
    (project_dir / "ontologia" / "object_types").mkdir(parents=True, exist_ok=True)
    (project_dir / "ontologia" / "link_types").mkdir(parents=True, exist_ok=True)
    (project_dir / "data" / "kuzu").mkdir(parents=True, exist_ok=True)

    compose_path = project_dir / "docker-compose.yml"
    compose_path.write_text(
        _render_docker_compose(api_port, db_port, kuzu_port, profile), encoding="utf-8"
    )
    env_path = project_dir / ".env"
    env_path.write_text(
        _render_env_file(project_name, api_port, agent_token, profile), encoding="utf-8"
    )
    gitignore_path = project_dir / ".gitignore"
    gitignore_path.write_text(_render_gitignore(), encoding="utf-8")
    readme_path = project_dir / "README.md"
    readme_path.write_text(_render_readme(project_name), encoding="utf-8")

    api_url = f"http://localhost:{api_port}"
    state = {
        "name": project_name,
        "api_url": api_url,
        "mcp_url": f"{api_url}/mcp",
        "agent_token": agent_token,
        "model_name": model_name,
        "profile": profile,
        "created_at": time.time(),
    }
    _write_local_state(project_dir, state)
    return state


def _initialize_git_repo(project_dir: Path) -> None:
    repo = Repo.init(project_dir)
    repo.git.add(A=True)
    actor = Actor("Ontologia Genesis", "genesis@ontologia.local")
    try:
        repo.index.commit("chore: initial genesis scaffold", author=actor, committer=actor)
    except Exception as exc:  # pragma: no cover - depends on user git config
        console.print(f"[yellow]Warning: initial commit failed ({exc}).[/yellow]")


def _run_docker_compose_up(project_dir: Path) -> None:
    try:
        docker_bin = shutil.which("docker")
        if docker_bin is None:
            console.print("[yellow]Docker executable not found; skipping service startup.[/yellow]")
            return
        subprocess.run(  # noqa: S603
            [docker_bin, "compose", "up", "-d"], cwd=project_dir, check=True
        )
        console.print("[green]Docker services started.[/green]")
    except FileNotFoundError:
        console.print("[yellow]Docker compose not found; skipping service startup.[/yellow]")
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]Docker compose failed: {exc}[/red]")


def _wait_for_health(api_url: str, timeout: int = 120) -> bool:
    deadline = time.time() + timeout
    health_url = api_url.rstrip("/") + "/health"
    while time.time() < deadline:
        try:
            resp = httpx.get(health_url, timeout=5.0)
            if resp.status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(2)
    return False


def _bootstrap_environment(api_url: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    bootstrap_url = api_url.rstrip("/") + "/v2/genesis/bootstrap"
    try:
        resp = httpx.post(bootstrap_url, json={}, headers=headers, timeout=15)
        if resp.status_code == 404:
            console.print("[yellow]Bootstrap endpoint not found; skipping.[/yellow]")
            return
        resp.raise_for_status()
        console.print("[green]Bootstrap completed successfully.[/green]")
    except Exception as exc:
        console.print(f"[yellow]Bootstrap step failed or was skipped: {exc}[/yellow]")


def _display_plan(plan: AgentPlan) -> None:
    console.print(f"[bold]Summary:[/bold] {plan.summary}")
    console.print(f"[bold]Branch:[/bold] {plan.branch_name}")
    console.print(f"[bold]Commit:[/bold] {plan.commit_message}")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Description")
    for file_change in plan.files:
        description = file_change.description or ""
        table.add_row(file_change.path, description)
    if plan.files:
        console.print(table)
    else:
        console.print("(No files to change)")


_MAX_LOG_CHARS = 4000


def _truncate_log(text: str, limit: int = _MAX_LOG_CHARS) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    truncated = text[:limit]
    return f"{truncated}\n… ({len(text) - limit} additional characters truncated)"


def _display_pipeline_result(result: dict[str, Any]) -> None:
    status = str(result.get("status"))
    return_code = result.get("returncode")
    stdout = _truncate_log(result.get("stdout", ""))
    stderr = _truncate_log(result.get("stderr", ""))

    if status == "ok":
        console.print("[green]✅ Pipeline executed successfully.[/green]")
    else:
        console.print(
            f"[red]❌ Pipeline failed (return code {return_code}). Review the logs below.[/red]"
        )

    if stdout:
        console.print(Panel(stdout, title="stdout", border_style="cyan"))
    if stderr:
        style = "red" if status != "ok" else "yellow"
        console.print(Panel(stderr, title="stderr", border_style=style))


def _build_failure_prompt(original_prompt: str, result: dict[str, Any]) -> str:
    stdout = _truncate_log(result.get("stdout", "")) or "<empty>"
    stderr = _truncate_log(result.get("stderr", "")) or "<empty>"
    returncode = result.get("returncode")
    return (
        f"{original_prompt}\n\n"
        "Previous plan was applied, but the pipeline execution failed. Use the details below to "
        "diagnose and correct the problem. Update only the necessary files.\n"
        f"Return code: {returncode}\n"
        f"STDOUT:\n{stdout}\n\n"
        f"STDERR:\n{stderr}"
    )


def validate_command(definitions_dir: str) -> int:
    objs, links = _collect_definitions(definitions_dir)
    errors = _validate_local(objs, links)
    if errors:
        console.print("[red]Validation errors:[/red]")
        for e in errors:
            console.print(f" - {e}")
        return 1
    console.print("[green]Validation OK[/green]")
    return 0


@app.command("diff")
def diff_command(
    definitions_dir: str = typer.Option(
        DEFAULT_DEFINITIONS_DIR, "--dir", "-d", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
    fail_on_dangerous: Annotated[
        bool, typer.Option("--fail-on-dangerous", help="Fail if dangerous changes detected")
    ] = False,  # noqa: FBT001, FBT003
    impact: Annotated[
        bool, typer.Option("--impact", help="Show impact analysis")
    ] = False,  # noqa: FBT001, FBT003
    deps: Annotated[
        bool, typer.Option("--deps", help="Show dependency analysis")
    ] = False,  # noqa: FBT001, FBT003
) -> int:
    """Show migration plan without applying."""
    objs_local, links_local = _collect_definitions(definitions_dir)
    errors = _validate_local(objs_local, links_local)
    if errors:
        console.print("[red]Validation errors:[/red]")
        for e in errors:
            console.print(f" - {e}")
        return 1
    objs_remote, links_remote = _fetch_server_state(host, ontology)
    plan = _plan(objs_local, links_local, objs_remote, links_remote)
    _display_plan_table(plan)
    if not plan:
        console.print("[green]No changes.[/green]")
        return 0

    if fail_on_dangerous and any(p.dangerous for p in plan):
        console.print("[red]Dangerous changes detected. Aborting.[/red]")
        return 1

    if impact:
        impacted = set()
        for p in plan:
            if p.kind == "objectType":
                impacted.add(p.api_name)
            if p.kind == "linkType":
                t = links_local.get(p.api_name, {}).get("fromObjectType")
                if t:
                    impacted.add(str(t))
                t = links_local.get(p.api_name, {}).get("toObjectType")
                if t:
                    impacted.add(str(t))
        if impacted:
            console.print("Impact (object instance counts):")
            base = host.rstrip("/") + f"/v2/ontologies/{ontology}/analytics/aggregate"
            with httpx.Client(timeout=30) as client:
                for ot in sorted(impacted):
                    try:
                        resp = client.post(
                            base,
                            json={
                                "objectTypeApiName": ot,
                                "metrics": [{"func": "count"}],
                                "groupBy": [],
                                "where": [],
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json() or {}
                        count = data.get("data", [{}])[0].get("count", 0)
                        console.print(f"  {ot}: {count} instances")
                    except httpx.HTTPError:
                        console.print(f"  {ot}: <error fetching count>")

    return 0


@app.command("apply")
def apply_command(
    definitions_dir: str = typer.Option(
        DEFAULT_DEFINITIONS_DIR, "--dir", "-d", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
    allow_destructive: Annotated[
        bool, typer.Option("--allow-destructive", help="Allow destructive changes")
    ] = False,  # noqa: FBT001, FBT003
    source: Literal["python", "yaml"] = typer.Option(
        "python",
        "--source",
        help="Use 'python' for ObjectModel definitions or 'yaml' for legacy files.",
    ),
    python_module: str = typer.Option(
        "ontology_definitions.models",
        "--module",
        "-m",
        help="Python module imported when --source=python.",
    ),
    module_path: Path | None = typer.Option(
        None,
        "--module-path",
        help="Optional path added to sys.path before importing --module.",
    ),
    assume_yes: bool = False,
) -> int:
    """Apply migration plan."""
    if source == "python":
        try:
            definition_set = load_python_definitions(python_module, module_path=module_path)
        except ModuleNotFoundError as exc:
            console.print(f"[red]Failed to import module[/red] {python_module}: {exc}")
            raise typer.Exit(code=1) from exc
        objs_local = definition_set.object_types
        links_local = definition_set.link_types
    else:
        objs_local, links_local = _collect_definitions(definitions_dir)
        errors = _validate_local(objs_local, links_local)
        if errors:
            console.print("[red]Validation errors:[/red]")
            for error in errors:
                console.print(f" - {error}")
            raise typer.Exit(code=1)

    # Show progress during server state fetch
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching server state...", total=None)
        objs_remote, links_remote = _fetch_server_state(host, ontology)
        progress.update(task, description="Planning changes...")
        plan = _plan(objs_local, links_local, objs_remote, links_remote)
        progress.update(task, completed=True)

    # Display the plan using the shared function
    _display_plan_table(plan)

    if not plan:
        console.print("[green]No changes detected.[/green]")
        return 0

    if source == "python":
        try:
            _ensure_python_plan_safe(plan, allow_destructive)
            results = _apply_python_plan(plan, allow_destructive=allow_destructive)
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(code=1) from exc
        _print_python_apply_results(plan, results)
        return 0

    # Show progress during apply
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Applying changes...", total=len(plan))
        _apply_with_progress(
            host,
            ontology,
            plan,
            objs_local,
            links_local,
            allow_destructive=bool(allow_destructive),
            progress=progress,
            task=task,
        )

    config = load_config()
    if config.sdk.auto_generate_on_apply:
        console.print("[cyan]Regenerating SDK from server definitions...[/cyan]")
        out_dir = Path(config.sdk.output_dir)
        code = generate_sdk_command(
            str(definitions_dir),
            host,
            ontology,
            str(out_dir),
            source="remote",
        )
        if code != 0:
            console.print("[red]SDK generation failed.[/red]")
            return code
    return 0


@app.command("export:yaml")
def export_yaml_command(
    output_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--out", "-o", help="Output directory for YAML definitions"
    ),
    module: str = typer.Option(
        "ontology_definitions.models",
        "--module",
        "-m",
        help="Python module containing ObjectModel definitions to export.",
    ),
    module_path: Path | None = typer.Option(
        None,
        "--module-path",
        help="Optional path added to sys.path before importing --module.",
    ),
    overwrite: bool = typer.Option(
        True,
        "--overwrite/--no-overwrite",
        help="Overwrite existing YAML files when exporting.",
    ),
) -> int:
    if yaml is None:
        console.print("[red]pyyaml is required. Install with: uvx pip install pyyaml[/red]")
        raise typer.Exit(code=1)

    try:
        definition_set = load_python_definitions(module, module_path=module_path)
    except ModuleNotFoundError as exc:
        console.print(f"[red]Failed to import module[/red] {module}: {exc}")
        raise typer.Exit(code=1) from exc

    base_dir = Path(output_dir)
    obj_dir = base_dir / "object_types"
    link_dir = base_dir / "link_types"
    obj_dir.mkdir(parents=True, exist_ok=True)
    link_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0

    for api_name, payload in sorted(definition_set.object_types.items()):
        path = obj_dir / f"{api_name}.yaml"
        if path.exists() and not overwrite:
            skipped += 1
            continue
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(payload, fh, sort_keys=False)
        written += 1

    for api_name, payload in sorted(definition_set.link_types.items()):
        path = link_dir / f"{api_name}.yaml"
        if path.exists() and not overwrite:
            skipped += 1
            continue
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(payload, fh, sort_keys=False)
        written += 1

    console.print(
        f"[green]Export complete[/green]: wrote {written} file(s), skipped {skipped} existing file(s)."
    )
    return 0


def generate_sdk_command(
    definitions_dir: str,
    host: str,
    ontology: str,
    out_dir: str,
    *,
    source: Literal["remote", "local"] = "remote",
) -> int:
    if source == "local":
        objs_local, links_local = _collect_definitions(definitions_dir)
        errors = _validate_local(objs_local, links_local)
        if errors:
            console.print("[red]Validation errors:[/red]")
            for e in errors:
                console.print(f" - {e}")
            return 1
        objs_remote, links_remote = objs_local, links_local
    else:
        objs_remote, links_remote = _fetch_server_state(host, ontology)
    _generate_objects_module(out_dir, objs_remote, links_remote)
    _generate_links_module(out_dir, links_remote)
    console.print(f"SDK generated to: {out_dir}")
    return 0


def _save_changeset_state(rid: str, changeset_data: dict[str, Any]) -> None:
    """Save change set information locally."""
    changesets_dir = Path(LOCAL_STATE_DIR) / "changesets"
    changesets_dir.mkdir(parents=True, exist_ok=True)
    state_file = changesets_dir / f"{rid}.json"
    _save_json(state_file, changeset_data)


def _load_changeset_state(rid: str) -> dict[str, Any] | None:
    """Load change set information locally."""
    state_file = Path(LOCAL_STATE_DIR) / "changesets" / f"{rid}.json"
    if state_file.exists():
        return _load_json(state_file)
    return None


@changeset_app.command("create")
def changeset_create_command(
    name: str = typer.Argument(..., help="Change set name"),
    target_type: str = typer.Option(
        None, "--target-type", "-t", help="Target object type for this change set"
    ),
    from_file: str = typer.Option(None, "--from-file", "-f", help="Load changes from JSON file"),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
) -> None:
    """Create a new change set for what-if scenarios."""
    console.print(f"[bold cyan]🔄 Creating change set:[/bold cyan] {name}\n")

    # Prepare changes
    changes = []

    if from_file:
        # Load changes from file
        file_path = Path(from_file)
        if not file_path.exists():
            console.print(f"[red]❌ File not found: {from_file}[/red]")
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                file_data = json.load(f)

            if "changes" in file_data:
                changes = file_data["changes"]
            else:
                # Assume the entire file is the changes array
                changes = file_data if isinstance(file_data, list) else [file_data]

            console.print(f"[green]✅ Loaded {len(changes)} changes from file[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to load file: {e}[/red]")
            return
    else:
        # Interactive change creation (simplified for now)
        console.print("[yellow]Interactive change creation not yet implemented.[/yellow]")
        console.print("Use --from-file to load changes from a JSON file.")
        return

    if not changes:
        console.print("[yellow]No changes to create change set with.[/yellow]")
        return

    # Create change set via API
    payload = {"name": name, "changes": changes}

    if target_type:
        payload["targetObjectTypeApiName"] = target_type

    try:
        with _get_api_client(host, ontology) as client:
            response = client.post("/change-sets", json=payload)
            response.raise_for_status()
            data = response.json()

            rid = data.get("rid")
            if not rid:
                console.print("[red]❌ No RID returned from API[/red]")
                return

            # Save local state
            changeset_data = {
                "rid": rid,
                "name": name,
                "created_at": time.time(),
                "changes": changes,
                "target_type": target_type,
            }
            _save_changeset_state(rid, changeset_data)

            console.print("\n[green]✅ Change set created successfully![/green]")
            console.print(f"🆔 RID: [cyan]{rid}[/cyan]")
            console.print(f"📋 Name: {name}")
            console.print(f"📝 Changes: {len(changes)} defined")
            if target_type:
                console.print(f"🎯 Target: {target_type}")
            console.print(f"\n💡 Use 'ontologia changeset approve {rid}' to apply these changes.")

    except httpx.HTTPStatusError as e:
        console.print(f"[red]❌ API error ({e.response.status_code}): {e.response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to create change set: {e}[/red]")


@changeset_app.command("approve")
def changeset_approve_command(
    rid: str = typer.Argument(..., help="Change set RID"),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,  # noqa: FBT001, FBT003
) -> None:
    """Approve and apply a change set."""
    console.print(f"[bold cyan]⚡ Approving change set:[/bold cyan] {rid}\n")

    # Load local state for context
    local_state = _load_changeset_state(rid)
    if local_state:
        name = local_state.get("name", "Unknown")
        changes_count = len(local_state.get("changes", []))
        console.print(f"📋 Name: {name}")
        console.print(f"📝 Changes: {changes_count} defined")

    # Confirmation
    if not yes:
        confirm = questionary.confirm(
            f"Are you sure you want to approve change set {rid}? This will apply the changes.",
            default=False,
        ).ask()

        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    try:
        with _get_api_client(host, ontology) as client:
            response = client.post(f"/change-sets/{rid}/approve")
            response.raise_for_status()
            data = response.json()

            console.print("\n[green]✅ Change set approved successfully![/green]")
            console.print(f"🆔 RID: [cyan]{rid}[/cyan]")

            # Show approval details
            status = data.get("status", "unknown")
            console.print(f"📊 Status: {status}")

            # Clean up local state
            if local_state:
                state_file = Path(LOCAL_STATE_DIR) / "changesets" / f"{rid}.json"
                if state_file.exists():
                    state_file.unlink()
                    console.print("🧹 Cleaned up local state file")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]❌ Change set not found: {rid}[/red]")
        else:
            console.print(f"[red]❌ API error ({e.response.status_code}): {e.response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to approve change set: {e}[/red]")


@changeset_app.command("list")
def changeset_list_command(
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
) -> None:
    """List all change sets."""
    console.print("[bold cyan]📋 Listing change sets[/bold cyan]\n")

    try:
        with _get_api_client(host, ontology) as client:
            response = client.get("/change-sets")
            response.raise_for_status()
            data = response.json()

            change_sets = data.get("data", [])
            if not change_sets:
                console.print("[dim]No change sets found.[/dim]")
                return

            console.print(f"[green]✅ Found {len(change_sets)} change sets:[/green]\n")

            # Change sets table
            cs_table = Table(show_header=True, header_style="bold magenta")
            cs_table.add_column("RID", style="cyan")
            cs_table.add_column("Name", style="white")
            cs_table.add_column("Status", style="yellow")
            cs_table.add_column("Target Type", style="dim")
            cs_table.add_column("Created", style="dim")

            for cs in change_sets:
                rid = cs.get("rid", "N/A")
                name = cs.get("name", "N/A")
                status = cs.get("status", "unknown")
                target_type = cs.get("targetObjectTypeApiName", "N/A")
                created_at = cs.get("createdAt", "")

                # Format created date
                if created_at:
                    try:
                        from datetime import datetime

                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        created_str = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        created_str = created_at[:10] if len(created_at) > 10 else created_at
                else:
                    created_str = "N/A"

                # Color code status
                status_style = {
                    "pending": "yellow",
                    "approved": "green",
                    "rejected": "red",
                    "applied": "blue",
                }.get(status.lower(), "white")

                cs_table.add_row(
                    rid[:8] + "..." if len(rid) > 8 else rid,
                    name,
                    f"[{status_style}]{status}[/{status_style}]",
                    target_type,
                    created_str,
                )

            console.print(cs_table)

    except httpx.HTTPStatusError as e:
        console.print(f"[red]❌ API error ({e.response.status_code}): {e.response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to list change sets: {e}[/red]")


def _slugify(text: str) -> str:
    """Convert text to a slugified API name."""
    import re

    # Convert to lowercase and replace spaces/special chars with underscores
    slug = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    slug = re.sub(r"\s+", "_", slug.strip())
    # Remove multiple underscores
    slug = re.sub(r"_+", "_", slug)
    # Remove leading/trailing underscores
    slug = slug.strip("_")
    return slug or "unnamed"


def _save_yaml_file(path: str, data: dict) -> None:
    """Save data to a YAML file with proper formatting."""
    if yaml is None:
        raise RuntimeError("pyyaml is required. Install with: uvx pip install pyyaml")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)


@new_app.command("object-type")
def new_object_type_command(
    definitions_dir: str = typer.Option(
        DEFAULT_DEFINITIONS_DIR, "--dir", "-d", help="Definitions directory"
    )
) -> None:
    """Create a new object type interactively."""
    console.print("[bold cyan]🏗️  Creating new Object Type[/bold cyan]")
    console.print("Let's configure your object type step by step.\n")

    # Basic information
    display_name = questionary.text(
        "Display name (human-readable name):",
        validate=lambda x: len(x.strip()) > 0 or "Display name is required",
    ).ask()

    if not display_name:
        console.print("[red]Cancelled.[/red]")
        return

    suggested_api_name = _slugify(display_name)
    api_name = questionary.text(
        "API name (machine-readable identifier):",
        default=suggested_api_name,
        validate=lambda x: len(x.strip()) > 0 or "API name is required",
    ).ask()

    primary_key = questionary.text(
        "Primary key field:",
        default="id",
        validate=lambda x: len(x.strip()) > 0 or "Primary key is required",
    ).ask()

    # Properties collection
    properties = {}
    while questionary.confirm("Add a property?", default=True).ask():
        console.print("\n[bold]Adding property:[/bold]")

        prop_name = questionary.text(
            "Property name:", validate=lambda x: len(x.strip()) > 0 or "Property name is required"
        ).ask()

        if not prop_name:
            continue

        data_type = questionary.select(
            "Data type:", choices=["string", "integer", "double", "boolean", "date", "timestamp"]
        ).ask()

        required = questionary.confirm("Is this property required?", default=False).ask()

        properties[prop_name] = {"dataType": data_type, "required": required}

        console.print(f"✓ Added property '{prop_name}' ({data_type})\n")

    # Build the object type definition
    object_type_def = {"apiName": api_name, "displayName": display_name, "primaryKey": primary_key}

    if properties:
        object_type_def["properties"] = properties

    # Save to file
    object_types_dir = os.path.join(definitions_dir, "object_types")
    file_path = os.path.join(object_types_dir, f"{api_name}.yaml")

    try:
        _save_yaml_file(file_path, object_type_def)
        console.print("\n[green]✅ Object Type created successfully![/green]")
        console.print(f"📁 File saved to: [cyan]{file_path}[/cyan]")
        console.print("\n📋 Summary:")
        console.print(f"   • Display name: {display_name}")
        console.print(f"   • API name: {api_name}")
        console.print(f"   • Primary key: {primary_key}")
        console.print(f"   • Properties: {len(properties)} defined")
    except Exception as e:
        console.print(f"\n[red]❌ Failed to save file: {e}[/red]")


@new_app.command("link-type")
def new_link_type_command(
    definitions_dir: str = typer.Option(
        DEFAULT_DEFINITIONS_DIR, "--dir", "-d", help="Definitions directory"
    )
) -> None:
    """Create a new link type interactively."""
    console.print("[bold cyan]🔗 Creating new Link Type[/bold cyan]")
    console.print("Let's configure your link type step by step.\n")

    # Basic information
    display_name = questionary.text(
        "Display name (human-readable name):",
        validate=lambda x: len(x.strip()) > 0 or "Display name is required",
    ).ask()

    if not display_name:
        console.print("[red]Cancelled.[/red]")
        return

    suggested_api_name = _slugify(display_name)
    api_name = questionary.text(
        "API name (machine-readable identifier):",
        default=suggested_api_name,
        validate=lambda x: len(x.strip()) > 0 or "API name is required",
    ).ask()

    # From and To object types
    from_object_type = questionary.text(
        "From object type (source):",
        validate=lambda x: len(x.strip()) > 0 or "From object type is required",
    ).ask()

    to_object_type = questionary.text(
        "To object type (target):",
        validate=lambda x: len(x.strip()) > 0 or "To object type is required",
    ).ask()

    # Cardinality
    cardinality = questionary.select(
        "Cardinality:", choices=["ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"]
    ).ask()

    # Optional inverse
    has_inverse = questionary.confirm("Add inverse relationship?", default=False).ask()
    inverse = None
    if has_inverse:
        inverse = questionary.text(
            "Inverse link type name:",
            validate=lambda x: len(x.strip()) > 0 or "Inverse name is required",
        ).ask()

    # Properties collection
    properties = {}
    while questionary.confirm("Add a property to the link?", default=False).ask():
        console.print("\n[bold]Adding link property:[/bold]")

        prop_name = questionary.text(
            "Property name:", validate=lambda x: len(x.strip()) > 0 or "Property name is required"
        ).ask()

        if not prop_name:
            continue

        data_type = questionary.select(
            "Data type:", choices=["string", "integer", "double", "boolean", "date", "timestamp"]
        ).ask()

        required = questionary.confirm("Is this property required?", default=False).ask()

        properties[prop_name] = {"dataType": data_type, "required": required}

        console.print(f"✓ Added property '{prop_name}' ({data_type})\n")

    # Build the link type definition
    link_type_def = {
        "apiName": api_name,
        "displayName": display_name,
        "fromObjectType": from_object_type,
        "toObjectType": to_object_type,
        "cardinality": cardinality,
    }

    if inverse:
        link_type_def["inverse"] = inverse

    if properties:
        link_type_def["properties"] = properties

    # Save to file
    link_types_dir = os.path.join(definitions_dir, "link_types")
    file_path = os.path.join(link_types_dir, f"{api_name}.yaml")

    try:
        _save_yaml_file(file_path, link_type_def)
        console.print("\n[green]✅ Link Type created successfully![/green]")
        console.print(f"📁 File saved to: [cyan]{file_path}[/cyan]")
        console.print("\n📋 Summary:")
        console.print(f"   • Display name: {display_name}")
        console.print(f"   • API name: {api_name}")
        console.print(f"   • From: {from_object_type}")
        console.print(f"   • To: {to_object_type}")
        console.print(f"   • Cardinality: {cardinality}")
        console.print(f"   • Properties: {len(properties)} defined")
        if inverse:
            console.print(f"   • Inverse: {inverse}")
    except Exception as e:
        console.print(f"\n[red]❌ Failed to save file: {e}[/red]")


def _get_api_client(host: str, ontology: str) -> httpx.Client:
    """Create an HTTP client for API calls."""
    base_url = host.rstrip("/") + f"/v2/ontologies/{ontology}"
    headers = {"Content-Type": "application/json"}

    # Try to get token from project state if available
    try:
        project_state = _load_project_state()
        if project_state.agent_token:
            headers["Authorization"] = f"Bearer {project_state.agent_token}"
    except Exception:
        # If we can't load project state, continue without auth
        pass

    return httpx.Client(base_url=base_url, headers=headers, timeout=30)


@app.command("query")
def query_command(
    query_string: str = typer.Argument(
        ..., help="Query string (e.g., 'employee where dept eq ENG AND age gt 25')"
    ),
    object_type: str = typer.Option(None, "--object-type", "-t", help="Object type to query"),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of results"),
) -> None:
    """Execute a simple query against object instances.

    Supports operators: eq, gt, lt, gte, lte, contains, ne
    Also supports: =, >, <, >=, <=
    Multiple conditions with AND: 'field1 eq value1 AND field2 gt value2'
    """
    console.print(f"[bold cyan]🔍 Executing query:[/bold cyan] {query_string}\n")

    # Parse simple query format: "object_type where field eq value"
    # This is a simplified parser for common cases
    if not object_type:
        # Try to extract object type from query
        parts = query_string.split()
        if len(parts) >= 4 and parts[1].lower() == "where":
            object_type = parts[0]
            where_clause = " ".join(parts[2:])
        else:
            console.print(
                "[red]❌ Could not determine object type. Use --object-type or format: 'object_type where field eq value'[/red]"
            )
            return
    else:
        # Remove object type from query if present
        if query_string.lower().startswith(object_type.lower() + " where"):
            where_clause = query_string[len(object_type) :].strip()
            if where_clause.lower().startswith("where "):
                where_clause = where_clause[6:].strip()
        else:
            where_clause = query_string

    # Parse where clause (enhanced parser for multiple operators)
    where_conditions = []
    if where_clause:
        # Enhanced parsing for multiple operators: "field eq value", "field gt value", etc.
        import re

        # Support for multiple operators: eq, gt, lt, gte, lte, contains, ne
        operator_pattern = r"(\w+)\s+(eq|gt|lt|gte|lte|contains|ne|=|>|<|>=|<=)\s+(.+)"

        # Split by AND for multiple conditions
        conditions = [cond.strip() for cond in where_clause.split("AND") if cond.strip()]

        for condition in conditions:
            match = re.search(operator_pattern, condition, re.IGNORECASE)

            if match:
                field = match.group(1)
                op_str = match.group(2).lower()
                value = match.group(3).strip("\"'")  # Remove quotes if present

                # Map operator strings to API operators
                op_map = {
                    "eq": "eq",
                    "=": "eq",
                    "gt": "gt",
                    ">": "gt",
                    "lt": "lt",
                    "<": "lt",
                    "gte": "gte",
                    ">=": "gte",
                    "lte": "lte",
                    "<=": "lte",
                    "contains": "contains",
                    "ne": "ne",
                }

                api_op = op_map.get(op_str, "eq")

                # Try to determine value type
                if value.lower() in ("true", "false"):
                    value_bool = value.lower() == "true"
                    where_conditions.append({"field": field, "op": api_op, "value": value_bool})
                elif value.isdigit():
                    where_conditions.append({"field": field, "op": api_op, "value": int(value)})
                elif value.replace(".", "", 1).isdigit():  # Handle float
                    where_conditions.append({"field": field, "op": api_op, "value": float(value)})
                else:
                    where_conditions.append({"field": field, "op": api_op, "value": value})

    try:
        with _get_api_client(host, ontology) as client:
            # Build search request
            search_payload = {"where": where_conditions, "limit": limit}

            response = client.post(f"/objects/{object_type}/search", json=search_payload)
            response.raise_for_status()
            data = response.json()

            objects = data.get("data", [])
            total = data.get("total", len(objects))

            if not objects:
                console.print("[dim]No results found.[/dim]")
                return

            console.print(f"[green]✅ Found {total} results (showing {len(objects)}):[/green]\n")

            # Results table
            if objects:
                # Create table with PK and common properties
                results_table = Table(show_header=True, header_style="bold magenta")
                results_table.add_column("PK", style="cyan")

                # Add up to 5 most common properties
                prop_counts = {}
                for obj in objects:
                    for prop_name in obj.get("properties", {}):
                        prop_counts[prop_name] = prop_counts.get(prop_name, 0) + 1

                common_props = sorted(prop_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                for prop_name, _ in common_props:
                    results_table.add_column(prop_name, style="white")

                # Add rows
                for obj in objects:
                    pk = obj.get("pkValue", "N/A")
                    obj_props = obj.get("properties", {})

                    row = [pk]
                    for prop_name, _ in common_props:
                        value = obj_props.get(prop_name)
                        value_str = str(value) if value is not None else "null"
                        # Truncate long values
                        if len(value_str) > 30:
                            value_str = value_str[:27] + "..."
                        row.append(value_str)

                    results_table.add_row(*row)

                console.print(results_table)

                if total > len(objects):
                    console.print(
                        f"\n[dim]... and {total - len(objects)} more results (use --limit to show more)[/dim]"
                    )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]❌ Object type not found: {object_type}[/red]")
        else:
            console.print(f"[red]❌ API error ({e.response.status_code}): {e.response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Failed to execute query: {e}[/red]")


@app.command("get")
def get_command(
    object_type: str = typer.Argument(..., help="Object type API name"),
    pk: str = typer.Argument(..., help="Primary key value"),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
) -> None:
    """Get a specific object instance by type and primary key."""
    console.print(f"[bold cyan]🔍 Fetching object:[/bold cyan] {object_type} with PK {pk}\n")

    try:
        with _get_api_client(host, ontology) as client:
            response = client.get(f"/objects/{object_type}/{pk}")
            response.raise_for_status()
            data = response.json()

            # Display results in a nice table format
            console.print("[green]✅ Found object:[/green]")

            # Basic info table
            info_table = Table(show_header=True, header_style="bold magenta")
            info_table.add_column("Field", style="cyan")
            info_table.add_column("Value", style="white")

            info_table.add_row("RID", data.get("rid", "N/A"))
            info_table.add_row("PK Value", data.get("pkValue", "N/A"))
            info_table.add_row("Object Type", data.get("objectTypeApiName", "N/A"))

            console.print(info_table)
            console.print("\n[bold]Properties:[/bold]")

            # Properties table
            props = data.get("properties", {})
            if props:
                props_table = Table(show_header=True, header_style="bold magenta")
                props_table.add_column("Property", style="cyan")
                props_table.add_column("Value", style="white")
                props_table.add_column("Type", style="dim")

                for prop_name, prop_value in props.items():
                    value_str = str(prop_value) if prop_value is not None else "null"
                    type_str = type(prop_value).__name__ if prop_value is not None else "null"
                    props_table.add_row(prop_name, value_str, type_str)

                console.print(props_table)
            else:
                console.print("[dim]No properties defined.[/dim]")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]❌ Object not found: {object_type} with PK {pk}[/red]")
        else:
            console.print(f"[red]❌ API error ({e.response.status_code}): {e.response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error fetching object: {e}[/red]")


@app.command("actions")
def actions_command(
    object_type: str = typer.Argument(..., help="Object type API name"),
    pk: str = typer.Argument(..., help="Primary key value"),
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="API host URL"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", "-o", help="Ontology name"),
) -> None:
    """List available actions for a specific object instance."""
    console.print(f"[bold cyan]⚡ Fetching actions for:[/bold cyan] {object_type} with PK {pk}\n")

    try:
        with _get_api_client(host, ontology) as client:
            response = client.get(f"/objects/{object_type}/{pk}/actions")
            response.raise_for_status()
            data = response.json()

            actions = data.get("actions", [])
            if not actions:
                console.print("[dim]No actions available for this object.[/dim]")
                return

            console.print(f"[green]✅ Found {len(actions)} available actions:[/green]\n")

            # Actions table
            actions_table = Table(show_header=True, header_style="bold magenta")
            actions_table.add_column("Action Name", style="cyan")
            actions_table.add_column("Display Name", style="white")
            actions_table.add_column("Description", style="dim")
            actions_table.add_column("Parameters", style="yellow")

            for action in actions:
                action_name = action.get("apiName", "N/A")
                display_name = action.get("displayName", "N/A")
                description = action.get("description", "No description")

                # Format parameters
                params = action.get("parameters", {})
                if params:
                    param_names = ", ".join(params.keys())
                    param_count = len(params)
                    param_str = f"{param_count} ({param_names})"
                else:
                    param_str = "None"

                actions_table.add_row(
                    action_name,
                    display_name,
                    description[:50] + "..." if len(description) > 50 else description,
                    param_str,
                )

            console.print(actions_table)

            # Show detailed parameter info for first action if any
            if actions and len(actions) == 1:
                console.print("\n[bold]Parameters:[/bold]")
                params = actions[0].get("parameters", {})
                if params:
                    param_table = Table(show_header=True, header_style="bold magenta")
                    param_table.add_column("Parameter", style="cyan")
                    param_table.add_column("Type", style="white")
                    param_table.add_column("Required", style="yellow")
                    param_table.add_column("Description", style="dim")

                    for param_name, param_def in params.items():
                        param_type = param_def.get("dataType", "unknown")
                        required = param_def.get("required", False)
                        param_desc = param_def.get("description", "No description")

                        param_table.add_row(
                            param_name,
                            param_type,
                            "Yes" if required else "No",
                            param_desc[:30] + "..." if len(param_desc) > 30 else param_desc,
                        )

                    console.print(param_table)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]❌ Object not found: {object_type} with PK {pk}[/red]")
        else:
            console.print(f"[red]❌ API error ({e.response.status_code}): {e.response.text}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error fetching actions: {e}[/red]")


@app.command("genesis")
def genesis_command(
    name: str = typer.Argument(..., help="Name of the new Ontologia ecosystem"),
    directory: Path = typer.Option(Path.cwd(), "--directory", "-d", help="Target directory"),
    profile: str = typer.Option("light", "--profile", help="Installation profile label"),
    start_services: Annotated[
        bool,
        typer.Option(
            "--start-services",
            help="Start Docker services after scaffolding",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    bootstrap: Annotated[
        bool,
        typer.Option(
            "--bootstrap",
            help="Attempt to bootstrap the ontology once the API is healthy",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    model: str = typer.Option(
        "openai:gpt-4o-mini", "--model", help="Default LLM model for the agent"
    ),
) -> None:
    project_dir = (directory / name).resolve()
    if project_dir.exists():
        console.print(f"[red]Directory '{project_dir}' already exists.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]✨ Creating Ontologia ecosystem '{name}'[/bold]")
    project_dir.mkdir(parents=True, exist_ok=True)

    api_port = _find_free_port(8000)
    db_port = _find_free_port(5432)
    kuzu_port = _find_free_port(9075)
    agent_token = secrets.token_hex(32)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Scaffolding project structure...", total=None)
        state = _write_scaffold(
            project_dir,
            project_name=name,
            api_port=api_port,
            db_port=db_port,
            kuzu_port=kuzu_port,
            agent_token=agent_token,
            model_name=model,
            profile=profile,
        )
        progress.update(task, description="Initializing git repository...")
        _initialize_git_repo(project_dir)
        progress.update(task, description="Registering project context...")
        _register_project(
            name, project_dir, state["api_url"], state["mcp_url"], agent_token, model, profile
        )
        progress.update(task, description="Finalizing...")
        progress.stop_task(task)

    console.print(f"[green]✅ Ecosystem '{name}' created at {project_dir}[/green]")
    console.print(f"   API URL: [cyan]{state['api_url']}[/cyan]")

    if start_services:
        _run_docker_compose_up(project_dir)
        if bootstrap:
            console.print("[cyan]Waiting for API health...[/cyan]")
            if _wait_for_health(state["api_url"]):
                _bootstrap_environment(state["api_url"], agent_token)
            else:
                console.print(
                    "[yellow]API did not become healthy within the timeout window.[/yellow]"
                )
    else:
        console.print(
            "[yellow]Services not started. Run `docker compose up -d` inside the project directory when ready.[/yellow]"
        )

    console.print("\nNext steps:")
    console.print(f"  1. cd {project_dir}")
    console.print("  2. ontologia agent\n")


@app.command("agent")
def agent_command(
    model: str | None = typer.Option(
        None, "--model", help="Override the LLM model for this session"
    ),
    auto_apply: Annotated[
        bool,
        typer.Option(
            "--auto-apply",
            help="Apply plans automatically without confirmation",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    author_name: str | None = typer.Option(None, "--author-name", help="Git author name override"),
    author_email: str | None = typer.Option(
        None, "--author-email", help="Git author email override"
    ),
) -> None:
    try:
        state = _load_project_state(model_override=model)
    except typer.Exit as exc:
        raise exc
    except Exception as exc:  # pragma: no cover - defensive
        console.print(f"[red]Failed to load project state:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[green]Connected to project '{state.name}'[/green]")
    console.print(f"API: [cyan]{state.api_url}[/cyan]")

    try:
        agent = ArchitectAgent(state)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    except Exception as exc:  # pragma: no cover - defensive
        console.print(f"[red]Failed to initialize agent:[/red] {exc}")
        raise typer.Exit(1) from exc

    while True:
        try:
            user_prompt = questionary.text("👤 > ").ask()
        except KeyboardInterrupt:
            console.print("\n[yellow]Session cancelled by user.[/yellow]")
            raise typer.Exit() from None
        if user_prompt is None:
            console.print()
            break
        prompt = user_prompt.strip()
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break

        base_prompt = prompt
        current_prompt = base_prompt

        while True:
            console.print("[cyan]🤖 Agent thinking…[/cyan]")
            try:
                plan = asyncio.run(agent.create_plan(current_prompt))
            except Exception as exc:
                console.print(f"[red]Agent failed to produce a plan:[/red] {exc}")
                break

            _display_plan(plan)
            if plan.is_empty():
                console.print("[green]The agent determined no changes are required.[/green]")
                break

            if auto_apply:
                apply_change = True
            else:
                answer = questionary.confirm("Apply this plan?", default=True).ask()
                apply_change = bool(answer)
            if not apply_change:
                console.print("[yellow]Plan discarded.[/yellow]")
                break

            try:
                written = agent.apply_plan(
                    plan,
                    author_name=author_name,
                    author_email=author_email,
                )
            except Exception as exc:
                console.print(f"[red]Failed to apply plan:[/red] {exc}")
                break

            if written:
                console.print(
                    f"[green]✅ Applied {len(written)} file(s) on branch '{plan.branch_name}'.[/green]"
                )
                for path in written:
                    rel = path.relative_to(state.root_path)
                    console.print(f"  • {rel}")
            else:
                console.print("[yellow]No files were written; nothing to commit.[/yellow]")

            try:
                pipeline_result = asyncio.run(agent.run_pipeline())
            except Exception as exc:
                pipeline_result = {
                    "status": "error",
                    "returncode": None,
                    "stdout": "",
                    "stderr": str(exc),
                }

            _display_pipeline_result(pipeline_result)
            if str(pipeline_result.get("status")) == "ok":
                break

            retry = questionary.confirm(
                "Pipeline failed. Ask the agent to generate a corrective plan?", default=True
            ).ask()
            if not retry:
                console.print("[yellow]Stopping after pipeline failure.[/yellow]")
                break

            current_prompt = _build_failure_prompt(base_prompt, pipeline_result)
            console.print("[cyan]🔁 Retrying with failure context…[/cyan]")
        # inner loop end -> prompt user again
    console.print("[cyan]Session ended.[/cyan]")


@app.command("dev")
def dev_cli(
    no_docker: Annotated[
        bool,
        typer.Option("--no-docker", help="Skip starting Docker services", is_flag=True),
    ] = False,  # noqa: FBT002
    no_reload: Annotated[
        bool,
        typer.Option("--no-reload", help="Disable Uvicorn auto-reload", is_flag=True),
    ] = False,  # noqa: FBT002
) -> None:
    """Start a local Ontologia development workspace."""

    config = load_config()
    console.print("[bold green]🚀 Starting Ontologia workspace[/bold green]")

    if not no_docker:
        console.print("[cyan]Bringing up Docker services...[/cyan]")
        docker_binary = shutil.which("docker")
        if docker_binary is None:
            console.print("[red]Docker executable not found in PATH.[/red]")
            raise typer.Exit(1)
        subprocess.run([docker_binary, "compose", "up", "-d"], check=True)  # noqa: S603

    console.print(f"[cyan]Starting API server at http://{config.api.host}:{config.api.port}[/cyan]")
    uvicorn_args = [
        "uvicorn",
        "api.main:app",
        "--host",
        config.api.host,
        "--port",
        str(config.api.port),
    ]
    if not no_reload:
        uvicorn_args.append("--reload")

    env = os.environ.copy()
    env.setdefault("ONTOLOGIA_CONFIG_ROOT", str(Path.cwd()))

    uvicorn_binary = shutil.which("uvicorn")
    if uvicorn_binary is None:
        console.print("[red]uvicorn executable not found in PATH.[/red]")
        raise typer.Exit(1)
    subprocess.run([uvicorn_binary, *uvicorn_args[1:]], env=env, check=True)  # noqa: S603


@pipeline_app.command("run")
def pipeline_run(
    skip_dbt: Annotated[
        bool,
        typer.Option("--skip-dbt", help="Skip dbt dependency install and build", is_flag=True),
    ] = False,  # noqa: FBT002
    skip_sync: Annotated[
        bool,
        typer.Option("--skip-sync", help="Skip ontology sync stage", is_flag=True),
    ] = False,  # noqa: FBT002
) -> None:
    """Execute the full Ontologia data pipeline (DuckDB prep, dbt, sync)."""

    config = load_config()
    uv_binary = shutil.which("uv")
    if uv_binary is None:
        console.print("[red]uv executable not found in PATH.[/red]")
        raise typer.Exit(1)

    env = os.environ.copy()
    env.setdefault("ONTOLOGIA_CONFIG_ROOT", str(Path.cwd()))
    duckdb_path = os.path.abspath(env.get("DUCKDB_PATH", config.data.duckdb_path))
    env["DUCKDB_PATH"] = duckdb_path

    console.print(f"[cyan]Preparing DuckDB raw tables at {duckdb_path}[/cyan]")
    subprocess.run(  # noqa: S603
        [uv_binary, "run", "python", "scripts/prepare_duckdb_raw.py"],
        env=env,
        check=True,
    )

    if not skip_dbt:
        # Prefer new template location, fallback to legacy example_project for backward-compat
        dbt_sources = [Path("templates/project/dbt_project"), Path("example_project/dbt_project")]
        dbt_dir = next((p for p in dbt_sources if p.exists()), None)
        if not dbt_dir:
            console.print(
                "[red]dbt template not found in templates/project or example_project.[/red]"
            )
            raise typer.Exit(1)
        dbt_env = env.copy()
        dbt_env["DBT_PROFILES_DIR"] = str(dbt_dir.resolve())
        console.print("[cyan]Running dbt deps...[/cyan]")
        subprocess.run(  # noqa: S603
            [uv_binary, "run", "dbt", "deps"],
            env=dbt_env,
            cwd=dbt_dir,
            check=True,
        )
        console.print("[cyan]Running dbt build...[/cyan]")
        subprocess.run(  # noqa: S603
            [uv_binary, "run", "dbt", "build"],
            env=dbt_env,
            cwd=dbt_dir,
            check=True,
        )
    else:
        console.print("[yellow]Skipping dbt stage (--skip-dbt).[/yellow]")

    if not skip_sync:
        console.print("[cyan]Syncing ontology to Kùzu...[/cyan]")
        subprocess.run(  # noqa: S603
            [uv_binary, "run", "python", "scripts/main_sync.py"],
            env=env,
            check=True,
        )
    else:
        console.print("[yellow]Skipping sync stage (--skip-sync).[/yellow]")

    console.print("[bold green]✅ Pipeline completed successfully.[/bold green]")


@migrations_app.command("run")
def migrations_run(
    task_rid: Annotated[str, typer.Argument(help="RID of the migration task")],
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Validate only", is_flag=True),
    ] = False,
    batch_size: Annotated[
        int | None,
        typer.Option("--batch-size", help="Instances processed per batch", min=1),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="API base URL", show_default=False),
    ] = DEFAULT_HOST,
    ontology: Annotated[
        str,
        typer.Option("--ontology", help="Ontology instance name", show_default=False),
    ] = DEFAULT_ONTOLOGY,
) -> None:
    """Execute a specific migration task via the API."""

    url = host.rstrip("/") + f"/v2/ontologies/{ontology}/migrations/tasks/{task_rid}/run"
    payload: dict[str, Any] = {"dryRun": dry_run}
    if batch_size is not None:
        payload["batchSize"] = batch_size
    try:
        resp = httpx.post(url, json=payload, timeout=60)
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network failure handled at runtime
        console.print(f"[red]Request failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    data = resp.json()
    failed = int(data.get("failedCount", 0))
    updated = int(data.get("updatedCount", 0))
    status = str(data.get("taskStatus", ""))

    if failed:
        console.print(
            f"[red]Migration task {task_rid} finished with {failed} failures (status={status}).[/red]"
        )
        errors = data.get("errors") or []
        if errors:
            console.print(f"[red]- {errors[0]}[/red]")
        raise typer.Exit(1)

    verb = "validated" if dry_run else "applied"
    console.print(
        f"[green]Migration task {task_rid} {verb} successfully (updated {updated} instance(s)).[/green]"
    )


@migrations_app.command("run-pending")
def migrations_run_pending(
    *,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Validate without applying", is_flag=True),
    ] = False,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Maximum number of tasks to process", min=1),
    ] = None,
    batch_size: Annotated[
        int | None,
        typer.Option("--batch-size", help="Instances processed per batch", min=1),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", help="API base URL", show_default=False),
    ] = DEFAULT_HOST,
    ontology: Annotated[
        str,
        typer.Option("--ontology", help="Ontology instance name", show_default=False),
    ] = DEFAULT_ONTOLOGY,
) -> None:
    """Execute all pending migration tasks for an ontology."""

    url = host.rstrip("/") + f"/v2/ontologies/{ontology}/migrations/tasks/run-pending"
    payload: dict[str, Any] = {"dryRun": dry_run}
    if limit is not None:
        payload["limit"] = limit
    if batch_size is not None:
        payload["batchSize"] = batch_size

    try:
        resp = httpx.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network failure handled at runtime
        console.print(f"[red]Request failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    data = resp.json() or {}
    results = data.get("results") or []
    if not results:
        console.print("[yellow]No pending migration tasks found.[/yellow]")
        return

    failures = [r for r in results if int(r.get("failedCount", 0))]
    console.print(f"[cyan]Processed {len(results)} migration task(s).[/cyan]")
    if failures:
        first = failures[0]
        console.print(
            f"[red]{len(failures)} task(s) reported failures; first: {first.get('taskRid')}[/red]"
        )
        raise typer.Exit(1)

    verb = "validated" if dry_run else "applied"
    console.print(f"[green]All tasks {verb} successfully.[/green]")


@graph_app.command("reset")
def graph_reset(
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Confirm graph storage cleanup", is_flag=True)
    ] = False,  # noqa: FBT002
) -> None:
    """Delete the current Kùzu graph storage so it can be rebuilt fresh."""

    config = load_config(Path.cwd())
    kuzu_path = Path(config.data.kuzu_path).expanduser()
    if not kuzu_path.is_absolute():
        kuzu_path = (Path.cwd() / kuzu_path).resolve()
    else:
        kuzu_path = kuzu_path.resolve()

    if not kuzu_path.exists():
        console.print(f"[yellow]Graph storage not found at {kuzu_path}; nothing to reset.[/yellow]")
        return

    if kuzu_path == Path("/"):
        console.print(
            "[red]Refusing to remove '/'. Update ontologia.toml to point to a directory first.[/red]"
        )
        raise typer.Exit(1)

    if not yes:
        proceed = typer.confirm(
            f"This will delete all data under '{kuzu_path}'. Continue?",
            default=False,
        )
        if not proceed:
            raise typer.Abort()

    if kuzu_path.is_dir():
        shutil.rmtree(kuzu_path)
    else:
        kuzu_path.unlink()

    console.print(
        "[green]Kùzu graph storage removed. Run 'ontologia pipeline run' to rebuild the unified graph.[/green]"
    )


def test_contract_command(definitions_dir: str, duckdb_path: str | None = None) -> int:
    """Validate that physical DuckDB tables match ontology object definitions."""

    try:
        import duckdb
    except ImportError:  # pragma: no cover - optional dependency
        console.print("[red]DuckDB is not installed. Install with `uv add duckdb`.[/red]")
        return 1

    from ontologia_api.core.database import engine
    from sqlmodel import Session, select

    from ontologia.domain.metamodels.types.object_type import ObjectType

    config = load_config()
    objs_local, _ = _collect_definitions(definitions_dir)
    if not objs_local:
        console.print("[yellow]No object type definitions found; nothing to validate.[/yellow]")
        return 0

    resolved_duckdb = os.path.abspath(
        duckdb_path or os.getenv("DUCKDB_PATH") or config.data.duckdb_path
    )
    if not Path(resolved_duckdb).exists():
        console.print(f"[red]DuckDB database not found at {resolved_duckdb}.[/red]")
        return 1

    def _quote_identifier(identifier: str) -> str:
        parts = [part for part in identifier.split(".") if part]
        return ".".join('"' + part.replace('"', '""') + '"' for part in parts)

    def _duckdb_columns(conn: duckdb.DuckDBPyConnection, table: str) -> dict[str, str]:
        qualified = _quote_identifier(table)
        rows = conn.execute(f"DESCRIBE SELECT * FROM {qualified}").fetchall()  # noqa: S608
        return {row[0]: row[1] for row in rows}

    def _normalize_duckdb_type(raw: str) -> str:
        upper = raw.upper().strip()
        if "(" in upper:
            upper = upper.split("(", 1)[0]
        return upper

    type_compatibility: dict[str, set[str]] = {
        "string": {"VARCHAR", "TEXT", "STRING"},
        "integer": {"INTEGER", "INT", "BIGINT", "SMALLINT", "TINYINT"},
        "double": {"DOUBLE", "FLOAT", "REAL", "DECIMAL", "NUMERIC"},
        "number": {"DOUBLE", "FLOAT", "REAL", "DECIMAL", "NUMERIC"},
        "boolean": {"BOOLEAN", "BOOL"},
        "date": {"DATE"},
        "timestamp": {"TIMESTAMP", "DATETIME"},
    }

    def _is_type_compatible(expected: str | None, actual: str) -> bool:
        if expected is None:
            return True
        normalized_expected = expected.lower()
        if normalized_expected in {"struct", "array"}:
            return True
        normalized_actual = _normalize_duckdb_type(actual)
        compatible = type_compatibility.get(normalized_expected)
        if compatible is None:
            return True
        return normalized_actual in compatible

    results: list[tuple[str, str, str | None, str]] = []
    error_count = 0

    with Session(engine) as session:
        object_types = session.exec(
            select(ObjectType).where(
                ObjectType.service == "ontology",
                ObjectType.instance == config.api.ontology,
                ObjectType.is_latest == true(),
            )
        ).all()

        if not object_types:
            console.print(
                "[yellow]No object types registered in the metamodel; nothing to validate.[/yellow]"
            )
            return 0

        conn = duckdb.connect(database=resolved_duckdb, read_only=True)
        try:
            for ot in object_types:
                schema = objs_local.get(ot.api_name)
                if schema is None:
                    results.append(
                        ("error", ot.api_name, None, "Object type not found in local definitions")
                    )
                    error_count += 1
                    continue

                properties = schema.get("properties") or {}
                data_sources = list(getattr(ot, "data_sources", []) or [])
                if not data_sources:
                    results.append(("warning", ot.api_name, None, "No data sources configured"))
                    continue

                for data_source in data_sources:
                    dataset = getattr(data_source, "dataset", None)
                    if dataset is None and getattr(data_source, "dataset_branch", None) is not None:
                        dataset = data_source.dataset_branch.dataset

                    if dataset is None:
                        results.append(("error", ot.api_name, None, "Data source missing dataset"))
                        error_count += 1
                        continue

                    if dataset.source_type != "duckdb_table":
                        results.append(
                            (
                                "warning",
                                ot.api_name,
                                dataset.source_identifier,
                                f"Unsupported source type '{dataset.source_type}'; skipping",
                            )
                        )
                        continue

                    try:
                        columns = _duckdb_columns(conn, dataset.source_identifier)
                    except duckdb.Error as exc:  # pragma: no cover - depends on DuckDB state
                        results.append(
                            (
                                "error",
                                ot.api_name,
                                dataset.source_identifier,
                                f"Failed to inspect table: {exc}",
                            )
                        )
                        error_count += 1
                        continue

                    inverse_mapping = {
                        str(prop_name): str(column_name)
                        for column_name, prop_name in (data_source.property_mappings or {}).items()
                    }

                    dataset_failed = False
                    for prop_name, prop_def in properties.items():
                        dataset_column = inverse_mapping.get(prop_name, prop_name)
                        if dataset_column not in columns:
                            results.append(
                                (
                                    "error",
                                    ot.api_name,
                                    dataset.source_identifier,
                                    f"Missing column '{dataset_column}' for property '{prop_name}'",
                                )
                            )
                            error_count += 1
                            dataset_failed = True
                            continue

                        expected_type = (
                            prop_def.get("dataType") if isinstance(prop_def, dict) else None
                        )
                        if isinstance(expected_type, str) and not _is_type_compatible(
                            expected_type, columns[dataset_column]
                        ):
                            results.append(
                                (
                                    "error",
                                    ot.api_name,
                                    dataset.source_identifier,
                                    (
                                        f"Type mismatch for '{prop_name}': expected {expected_type}, "
                                        f"found {columns[dataset_column]}"
                                    ),
                                )
                            )
                            error_count += 1
                            dataset_failed = True

                    if not dataset_failed:
                        results.append(
                            (
                                "ok",
                                ot.api_name,
                                dataset.source_identifier,
                                "Schema matches object definition",
                            )
                        )
        finally:
            conn.close()

    if not results:
        console.print("[yellow]No datasets available for validation.[/yellow]")
        return 0

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status")
    table.add_column("ObjectType")
    table.add_column("Dataset/Table")
    table.add_column("Details", overflow="fold")

    style_map = {"ok": "green", "warning": "yellow", "error": "red"}
    for status, ot_name, dataset_id, message in results:
        style = style_map.get(status, "white")
        dataset_label = dataset_id or "-"
        table.add_row(f"[{style}]{status.upper()}[/]", ot_name, dataset_label, message)

    console.print(table)

    if error_count > 0:
        console.print(f"[red]Contract tests failed with {error_count} error(s).[/red]")
        return 1

    console.print("[bold green]✅ Contract tests passed.[/bold green]")
    return 0


@app.command("test-contract")
def test_contract_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    duckdb_path: Path | None = typer.Option(
        None, "--duckdb-path", help="Override DuckDB database path"
    ),
) -> None:
    code = test_contract_command(
        str(definitions_dir), duckdb_path=str(duckdb_path) if duckdb_path else None
    )
    if code != 0:
        raise typer.Exit(code)


@app.command("validate")
def validate_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
) -> None:
    code = validate_command(str(definitions_dir))
    if code != 0:
        raise typer.Exit(code)


@app.command("diff")
def diff_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="API host"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", help="Ontology API name"),
    fail_on_dangerous: Annotated[
        bool,
        typer.Option(
            "--fail-on-dangerous",
            help="Exit non-zero if dangerous operations are present",
            is_flag=True,
        ),
    ] = False,  # noqa: FBT002
    impact: Annotated[
        bool,
        typer.Option(
            "--impact", help="Show instance counts for affected object types", is_flag=True
        ),
    ] = False,  # noqa: FBT002
    deps: Annotated[
        bool,
        typer.Option("--deps", help="Show dependency summary for changed types", is_flag=True),
    ] = False,  # noqa: FBT002
) -> None:
    code = diff_command(
        str(definitions_dir),
        host,
        ontology,
        fail_on_dangerous=fail_on_dangerous,
        impact=impact,
        deps=deps,
    )
    if code != 0:
        raise typer.Exit(code)


@app.command("apply")
def apply_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="API host"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", help="Ontology API name"),
    allow_destructive: Annotated[
        bool,
        typer.Option(
            "--allow-destructive", help="Allow destructive operations (deletes)", is_flag=True
        ),
    ] = False,  # noqa: FBT002
    yes: Annotated[
        bool, typer.Option("--yes", help="Apply without confirmation", is_flag=True)
    ] = False,  # noqa: FBT002
    source: Literal["python", "yaml"] = typer.Option(
        "python",
        "--source",
        help="Use 'python' for ObjectModel definitions or 'yaml' for legacy files.",
    ),
    module: str = typer.Option(
        "ontology_definitions.models",
        "--module",
        "-m",
        help="Python module imported when --source=python.",
    ),
    module_path: Path | None = typer.Option(
        None,
        "--module-path",
        help="Optional path added to sys.path before importing --module.",
    ),
) -> None:
    code = apply_command(
        str(definitions_dir),
        host,
        ontology,
        allow_destructive=allow_destructive,
        assume_yes=yes,
        source=source,
        python_module=module,
        module_path=module_path,
    )
    if code != 0:
        raise typer.Exit(code)


@app.command("generate-sdk")
def generate_sdk_cli(
    definitions_dir: Path = typer.Option(
        Path(DEFAULT_DEFINITIONS_DIR), "--dir", help="Definitions directory"
    ),
    host: str = typer.Option(DEFAULT_HOST, "--host", help="API host"),
    ontology: str = typer.Option(DEFAULT_ONTOLOGY, "--ontology", help="Ontology API name"),
    source: Literal["remote", "local"] = typer.Option(
        "remote", "--source", help="Use 'remote' (API) or 'local' definitions"
    ),
    out: Path = typer.Option(
        Path(DEFAULT_SDK_DIR), "--out", help="Output directory for generated modules"
    ),
) -> None:
    code = generate_sdk_command(str(definitions_dir), host, ontology, str(out), source=source)
    if code != 0:
        raise typer.Exit(code)


@projects_app.command("list")
def projects_list() -> None:
    projects = _list_registered_projects()
    if not projects:
        console.print("[yellow]No registered projects found.[/yellow]")
        return
    data = _load_json(CONFIG_FILE)
    current = data.get("current_project")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project")
    table.add_column("Path")
    table.add_column("API URL")
    for name, info in projects.items():
        label = f"{name} (current)" if name == current else name
        table.add_row(label, info.get("path", "?"), info.get("api_url", "?"))
    console.print(table)


@projects_app.command("switch")
def projects_switch(name: str) -> None:
    data = _load_json(CONFIG_FILE)
    projects = data.get("projects", {})
    if name not in projects:
        console.print(f"[red]Project '{name}' not found in registry.[/red]")
        raise typer.Exit(1)
    data["current_project"] = name
    _save_json(CONFIG_FILE, data)
    console.print(f"[green]Current project set to '{name}'.[/green]")


@app.command("init")
def init_command(
    project_name: str = typer.Argument(None, help="Name of the new project"),
    template: str = typer.Option(None, "--template", "-t", help="Template to use"),
    list_templates: bool = typer.Option(
        False, "--list-templates", "-l", help="List available templates"
    ),
) -> None:
    """Initialize a new Ontologia project from a template."""
    from ontologia_cli.init import init_project, list_available_templates

    if list_templates:
        list_available_templates()
        return

    if not project_name:
        console.print("[red]❌ Project name is required when not using --list-templates[/red]")
        console.print("Usage: ontologia-cli init [OPTIONS] PROJECT_NAME")
        console.print("   or: ontologia-cli init --list-templates")
        raise typer.Exit(1)

    # If no template specified, use interactive selection
    if not template:
        template = _select_template_interactive()

    try:
        init_project(project_name, template)
        console.print(f"[green]✅ Project '{project_name}' created successfully![/green]")
        console.print(f"[blue]📁 Location: ./{project_name}[/blue]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(f"1. cd {project_name}")
        console.print("2. cp .env.example .env")
        console.print("3. docker-compose up -d")
        console.print("4. Visit http://localhost:8000/docs")
    except Exception as e:
        console.print(f"[red]❌ Failed to create project: {e}[/red]")
        raise typer.Exit(1) from e


def _select_template_interactive() -> str:
    """Interactive template selection."""
    templates = {
        "simple-api": {
            "name": "Simple API",
            "description": "Basic CRUD operations with PostgreSQL + FastAPI",
            "use_case": "Perfect for getting started with basic ontology management",
            "setup_time": "5 minutes",
        },
        "data-platform": {
            "name": "Data Platform",
            "description": "Analytics with DuckDB + dbt + Dagster",
            "use_case": "For data teams needing ETL and analytics capabilities",
            "setup_time": "10 minutes",
        },
        "knowledge-graph": {
            "name": "Knowledge Graph",
            "description": "Graph traversals with KùzuDB",
            "use_case": "For applications requiring complex relationship queries",
            "setup_time": "15 minutes",
        },
        "enterprise-workflows": {
            "name": "Enterprise Workflows",
            "description": "Full stack with search, workflows, real-time",
            "use_case": "Complete enterprise setup with all features",
            "setup_time": "20 minutes",
        },
    }

    console.print("\n[bold cyan]🚀 Choose a template for your project:[/bold cyan]\n")

    choices = []
    for key, info in templates.items():
        choice = questionary.Choice(
            title=f"{info['name']} - {info['description']}",
            value=key,
            description=f"{info['use_case']} (⏱️ {info['setup_time']})",
        )
        choices.append(choice)

    template = questionary.select("Select a template:", choices=choices).ask()

    if not template:
        console.print("[yellow]No template selected. Exiting.[/yellow]")
        raise typer.Exit(0)

    return template


@app.command("playground")
def playground_command(
    action: str = typer.Argument(..., help="Action to perform"),
    name: str = typer.Option(None, "--name", "-n", help="Playground name"),
    dataset: str = typer.Option(None, "--dataset", "-d", help="Dataset to load"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout in seconds"),
) -> None:
    """Manage Ontologia playground environments."""
    from ontologia_cli.playground import manage_playground

    try:
        manage_playground(action, name, dataset, timeout)
    except Exception as e:
        console.print(f"[red]❌ Playground command failed: {e}[/red]")
        raise typer.Exit(1) from e


def main(argv: list[str] | None = None) -> int:
    """Entry point used both by tests and console scripts."""

    if argv is None:
        app()
        return 0
    runner = CliRunner()
    result = runner.invoke(app, argv)
    if result.exception:
        raise result.exception
    return result.exit_code


def run() -> None:
    app()


if __name__ == "__main__":
    run()
