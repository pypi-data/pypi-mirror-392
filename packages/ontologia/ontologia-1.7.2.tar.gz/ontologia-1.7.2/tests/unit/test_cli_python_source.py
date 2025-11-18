import importlib
from pathlib import Path

from typer.testing import CliRunner

cli_module = importlib.import_module("packages.ontologia_cli.main")
from packages.ontologia_cli.main import app


def test_export_yaml_command(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "export:yaml",
            "--module",
            "ontology_definitions.models",
            "--out",
            str(tmp_path),
        ],
        catch_exceptions=False,
    )

    assert (
        result.exit_code == 0
    ), f"exit={result.exit_code} stdout={result.stdout} stderr={result.stderr}"
    assert (Path(tmp_path) / "object_types" / "employee.yaml").exists()
    assert (Path(tmp_path) / "link_types" / "works_for.yaml").exists()


def test_apply_command_python_source(monkeypatch):
    monkeypatch.setattr(cli_module, "_fetch_server_state", lambda host, ontology: ({}, {}))
    monkeypatch.setattr(cli_module, "_display_plan_table", lambda plan: None)
    monkeypatch.setattr(
        cli_module,
        "_plan",
        lambda *args, **kwargs: [
            cli_module.PlanItem("objectType", "employee", "create"),
            cli_module.PlanItem("linkType", "works_for", "create"),
        ],
    )

    applied = {}

    def fake_apply_schema(*, allow_destructive: bool = False):
        applied["allow_destructive"] = allow_destructive
        return {
            "employee": (True, "ObjectType created"),
            "works_for": (True, "LinkType created"),
        }

    monkeypatch.setattr(cli_module, "ogm_apply_schema", fake_apply_schema)

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "apply",
            "--source",
            "python",
            "--module",
            "ontology_definitions.models",
        ],
        catch_exceptions=False,
    )

    assert (
        result.exit_code == 0
    ), f"exit={result.exit_code} stdout={result.stdout} stderr={result.stderr}"
    assert applied.get("allow_destructive") is False
    assert "works_for" in result.stdout
