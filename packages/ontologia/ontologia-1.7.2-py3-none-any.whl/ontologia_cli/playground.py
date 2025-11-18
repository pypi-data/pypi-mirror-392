"""Playground management functionality for Ontologia CLI."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def get_playground_dir() -> Path:
    """Get the playground directory path."""
    current_dir = Path(__file__).parent
    repo_root = current_dir.parent.parent
    playground_dir = repo_root / "playground"

    if not playground_dir.exists():
        raise RuntimeError(f"Playground directory not found: {playground_dir}")

    return playground_dir


def validate_playground_name(name: str) -> str:
    """Validate playground name."""
    if not name:
        raise ValueError("Playground name cannot be empty")

    # Check for invalid characters
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in invalid_chars:
        if char in name:
            raise ValueError(f"Playground name cannot contain '{char}'")

    # Check if it starts with dot or dash
    if name.startswith((".", "-")):
        raise ValueError("Playground name cannot start with '.' or '-'")

    return name


def create_playground(name: str) -> None:
    """Create a new playground environment."""
    playground_dir = get_playground_dir()
    target_dir = Path.cwd() / name

    if target_dir.exists():
        raise RuntimeError(f"Directory already exists: {target_dir}")

    console.print(f"🚀 Creating playground '{name}'...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Setting up playground...", total=None)

        # Create target directory first
        progress.update(task, description="Creating target directory...")
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy playground files
        progress.update(task, description="Copying playground files...")

        # Copy all files except .git and __pycache__
        for item in playground_dir.iterdir():
            if item.name.startswith(".git") or item.name == "__pycache__":
                continue

            if item.is_file():
                shutil.copy2(item, target_dir / item.name)
            elif item.is_dir():
                target_subdir = target_dir / item.name
                shutil.copytree(
                    item, target_subdir, ignore=shutil.ignore_patterns("__pycache__", ".git")
                )

        progress.update(task, description="Setting up environment...")

        # Create .env file if it doesn't exist
        env_file = target_dir / ".env"
        env_example = target_dir / ".env.example"

        if env_example.exists() and not env_file.exists():
            shutil.copy2(env_example, env_file)

            # Update project name in .env
            content = env_file.read_text(encoding="utf-8")
            content = content.replace("ontologia-playground", name)
            env_file.write_text(content, encoding="utf-8")

        progress.update(task, description="Finalizing setup...")

        # Make scripts executable
        scripts_dir = target_dir / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.sh"):
                os.chmod(script_file, 0o755)

    console.print(f"✅ Playground '{name}' created successfully!")
    console.print(f"📁 Location: {target_dir}")

    # Show next steps
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print(f"1. cd {name}")
    console.print("2. ./scripts/setup.sh")
    console.print("3. docker-compose up -d")
    console.print("4. ./scripts/wait-for-services.sh")
    console.print("5. ./scripts/load-sample-data.sh")


def start_playground() -> None:
    """Start playground services."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    console.print("🚀 Starting playground services...")

    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True, capture_output=True, text=True)
        console.print("✅ Playground services started!")

        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("1. ./scripts/wait-for-services.sh")
        console.print("2. ./scripts/load-sample-data.sh")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to start services: {e}[/red]")
        console.print(f"[red]Output: {e.stderr}[/red]")
        raise


def stop_playground() -> None:
    """Stop playground services."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    console.print("🛑 Stopping playground services...")

    try:
        subprocess.run(["docker-compose", "down"], check=True, capture_output=True, text=True)
        console.print("✅ Playground services stopped!")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to stop services: {e}[/red]")
        console.print(f"[red]Output: {e.stderr}[/red]")
        raise


def restart_playground() -> None:
    """Restart playground services."""
    console.print("🔄 Restarting playground services...")
    stop_playground()
    start_playground()


def show_playground_status() -> None:
    """Show playground status."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    console.print("📊 Playground Status")
    console.print("=" * 40)

    try:
        # Get container status
        result = subprocess.run(
            ["docker-compose", "ps"], check=True, capture_output=True, text=True
        )

        console.print(result.stdout)

        # Check if services are healthy
        console.print("\n🔍 Service Health:")

        services = {
            "API": "http://localhost:8000/health",
            "Jupyter": "http://localhost:8888/api",
            "Temporal": "http://localhost:7233/api/v1/namespaces/default",
            "Dagster": "http://localhost:3000",
            "Kibana": "http://localhost:5601/api/status",
            "Grafana": "http://localhost:3001/api/health",
            "Elasticsearch": "http://localhost:9200/_cluster/health",
        }

        try:
            import requests

            for service, url in services.items():
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        console.print(f"  ✅ {service}")
                    else:
                        console.print(f"  ❌ {service} (HTTP {response.status_code})")
                except Exception:
                    console.print(f"  ❌ {service}")

            # Check Redis separately
            try:
                import redis  # type: ignore

                r = redis.from_url("redis://localhost:6379")
                r.ping()
                console.print("  ✅ Redis")
            except Exception:
                console.print("  ❌ Redis")
        except ImportError as e:
            console.print(f"  ⚠️  Cannot check service health: missing dependencies ({e})")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to get status: {e}[/red]")
        raise


def show_playground_logs() -> None:
    """Show playground logs."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    console.print("📋 Showing playground logs...")
    console.print("Press Ctrl+C to stop watching logs")

    try:
        subprocess.run(["docker-compose", "logs", "-f"], check=True)
    except KeyboardInterrupt:
        console.print("\n👋 Stopped watching logs")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to show logs: {e}[/red]")
        raise


def load_dataset(dataset: str) -> None:
    """Load sample dataset into playground."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    console.print(f"📊 Loading dataset: {dataset}")

    script_path = Path("scripts/load-sample-data.sh")
    if not script_path.exists():
        raise RuntimeError("Load script not found: scripts/load-sample-data.sh")

    try:
        subprocess.run([str(script_path), dataset], check=True, text=True)
        console.print(f"✅ Dataset '{dataset}' loaded successfully!")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to load dataset: {e}[/red]")
        raise


def wait_for_services(timeout: int) -> None:
    """Wait for playground services to be ready."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    script_path = Path("scripts/wait-for-services.sh")
    if not script_path.exists():
        raise RuntimeError("Wait script not found: scripts/wait-for-services.sh")

    console.print(f"⏳ Waiting for services to be ready (timeout: {timeout}s)...")

    try:
        subprocess.run([str(script_path), str(timeout)], check=True, text=True)
        console.print("✅ All services are ready!")

    except subprocess.CalledProcessError:
        console.print("[red]❌ Services failed to start within timeout[/red]")
        raise


def destroy_playground() -> None:
    """Destroy playground environment."""
    if not Path("docker-compose.yml").exists():
        raise RuntimeError("Not in a playground directory (docker-compose.yml not found)")

    console.print("🚨 This will remove all playground data and services!")
    console.print("This action cannot be undone.")

    from rich.prompt import Confirm

    if not Confirm.ask("Are you sure you want to destroy this playground?"):
        console.print("👋 Playground destruction cancelled")
        return

    console.print("💥 Destroying playground...")

    script_path = Path("scripts/cleanup.sh")
    if script_path.exists():
        try:
            subprocess.run([str(script_path), "--all"], check=True, text=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Cleanup script failed: {e}[/red]")

    # Remove the entire directory
    current_dir = Path.cwd()
    parent_dir = current_dir.parent

    try:
        os.chdir(parent_dir)
        shutil.rmtree(current_dir)
        console.print(f"✅ Playground '{current_dir.name}' destroyed!")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove directory: {e}[/red]")
        raise


def show_playground_help() -> None:
    """Show playground help."""
    help_text = """
🚀 Ontologia Playground Management

Usage: ontologia-cli playground <action> [options]

Actions:
  create <name>     Create a new playground environment
  start             Start playground services
  stop              Stop playground services
  restart           Restart playground services
  status            Show playground status
  logs              Show playground logs
  load <dataset>    Load sample dataset
  wait [timeout]    Wait for services to be ready
  destroy           Destroy playground environment

Options:
  --name, -n        Playground name (for create)
  --dataset, -d     Dataset to load (basic, healthcare, financial, ecommerce, all)
  --timeout, -t     Timeout in seconds (default: 300)

Examples:
  ontologia-cli playground create my-playground
  ontologia-cli playground start
  ontologia-cli playground load basic
  ontologia-cli playground status
  ontologia-cli playground destroy

Available Datasets:
  basic      - Basic demo data (people, projects, skills)
  healthcare - Healthcare data (patients, doctors, appointments)
  financial  - Financial data (accounts, transactions, customers)
  ecommerce  - E-commerce data (products, customers, orders)
  all        - Load all datasets

For more information, see the playground README.md
"""

    console.print(Panel(help_text, title="🚀 Playground Help", border_style="blue"))


def manage_playground(
    action: str, name: str | None = None, dataset: str | None = None, timeout: int = 300
) -> None:
    """Main playground management function."""
    try:
        if action == "create":
            if not name:
                console.print("[red]❌ Playground name is required for create action[/red]")
                console.print("Usage: ontologia-cli playground create <name>")
                raise typer.Exit(1)

            name = validate_playground_name(name)
            create_playground(name)

        elif action == "start":
            start_playground()

        elif action == "stop":
            stop_playground()

        elif action == "restart":
            restart_playground()

        elif action == "status":
            show_playground_status()

        elif action == "logs":
            show_playground_logs()

        elif action == "load":
            if not dataset:
                console.print("[red]❌ Dataset is required for load action[/red]")
                console.print("Usage: ontologia-cli playground load <dataset>")
                console.print("Available datasets: basic, healthcare, financial, ecommerce, all")
                raise typer.Exit(1)

            load_dataset(dataset)

        elif action == "wait":
            wait_for_services(timeout)

        elif action == "destroy":
            destroy_playground()

        elif action in ["help", "--help", "-h"]:
            show_playground_help()

        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            show_playground_help()
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]❌ Playground management failed: {e}[/red]")
        raise
