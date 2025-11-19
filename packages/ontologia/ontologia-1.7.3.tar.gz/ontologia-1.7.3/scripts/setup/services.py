"""
🔧 Service management for Ontologia setup.

Handles dependency checking, Docker orchestration, service health checks,
and other service-related operations.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scripts.utils import optional_import

from .modes import ModeConfig

# Optional imports
duckdb = optional_import("duckdb", install_group="analytics")
polars = optional_import("polars", install_group="analytics")
kuzu = optional_import("kuzu", install_group="full")
elasticsearch = optional_import("elasticsearch", install_group="full")
temporalio = optional_import("temporalio", install_group="full")


class DependencyChecker:
    """Checks for required and optional dependencies."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def check_python(self) -> bool:
        """Check if Python 3.11+ is available."""
        version = sys.version_info
        return version.major >= 3 and version.minor >= 11

    def check_docker(self) -> bool:
        """Check if Docker and Docker Compose are available."""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True, timeout=10)
            subprocess.run(
                ["docker", "compose", "version"], check=True, capture_output=True, timeout=10
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_optional_dependencies(self, dependencies: list[str]) -> dict[str, bool]:
        """Check availability of optional dependencies."""
        results: dict[str, bool] = {}

        for dep in dependencies:
            try:
                if dep == "duckdb":
                    duckdb()
                elif dep == "polars":
                    polars()
                elif dep == "kuzu":
                    kuzu()
                elif dep == "elasticsearch":
                    elasticsearch()
                elif dep == "temporalio":
                    temporalio()
                else:
                    # Try direct import
                    __import__(dep)
                results[dep] = True
            except Exception:
                results[dep] = False

        return results

    def check_mode_dependencies(self, mode_config: ModeConfig) -> dict[str, bool]:
        """Check all dependencies for a specific mode."""
        results: dict[str, bool] = {}

        # Check required dependencies
        if "python" in mode_config.required_dependencies:
            results["python"] = self.check_python()

        if "docker" in mode_config.required_dependencies:
            results["docker"] = self.check_docker()

        # Check optional dependencies
        optional_results = self.check_optional_dependencies(
            mode_config.required_dependencies + mode_config.optional_dependencies
        )
        results.update(optional_results)

        return results

    def report_missing_dependencies(
        self, dependencies: dict[str, bool], mode_config: ModeConfig
    ) -> list[str]:
        """Report missing dependencies and return installation instructions."""
        missing = [dep for dep, available in dependencies.items() if not available]
        instructions: list[str] = []

        if not missing:
            return instructions

        self.console.print(f"❌ Missing dependencies: {', '.join(missing)}")

        for dep in missing:
            if dep == "docker":
                self.console.print("Please install Docker and Docker Compose")
                instructions.append("Install Docker from https://docker.com")
            elif dep == "python":
                self.console.print("Please install Python 3.11+")
                instructions.append("Install Python 3.11+ from https://python.org")
            elif dep in ["duckdb", "polars"]:
                self.console.print("Install with: uv sync --group analytics")
                instructions.append("uv sync --group analytics")
            elif dep in ["kuzu", "elasticsearch", "temporalio"]:
                self.console.print("Install with: uv sync --group full")
                instructions.append("uv sync --group full")

        return instructions


class ServiceManager:
    """Manages Docker services and health checks."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def run_docker_compose(self, compose_files: list[str], action: str = "up") -> bool:
        """Run Docker Compose with specified files and action."""
        cmd = ["docker", "compose"] + [f"-f{f}" for f in compose_files]

        if action == "up":
            cmd.extend(["up", "-d"])
        elif action == "down":
            cmd.extend(["down", "-v"])
        else:
            cmd.append(action)

        try:
            self.console.print(f"🐳 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)
            return True
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Docker command failed: {e}")
            if e.stderr:
                self.console.print(f"Stderr: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            self.console.print("❌ Docker command timed out")
            return False

    def wait_for_services(self, timeout: int = 300, check_interval: int = 5) -> bool:
        """Wait for services to be healthy."""
        self.console.print("⏳ Waiting for services to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check API health
                result = subprocess.run(
                    ["curl", "-f", "http://localhost:8000/health"],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    self.console.print("✅ Services are ready!")
                    return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass

            time.sleep(check_interval)
            self.console.print(".", end="")

        self.console.print("\\n❌ Timeout waiting for services")
        return False

    def run_migrations(self) -> bool:
        """Run database migrations using Alembic."""
        self.console.print("🗄️ Running database migrations...")
        try:
            subprocess.run(
                ["uv", "run", "alembic", "upgrade", "head"],
                check=True,
                capture_output=True,
                timeout=120,
            )
            self.console.print("✅ Migrations completed")
            return True
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ Migration failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.console.print("❌ Migration timed out")
            return False

    def generate_sdk(self) -> bool:
        """Generate initial SDK."""
        self.console.print("🔧 Generating SDK...")
        try:
            subprocess.run(
                ["uv", "run", "ontologia-cli", "generate-sdk", "--source", "local"],
                check=True,
                capture_output=True,
                timeout=60,
            )
            self.console.print("✅ SDK generated")
            return True
        except subprocess.CalledProcessError as e:
            self.console.print(f"❌ SDK generation failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.console.print("❌ SDK generation timed out")
            return False

    def setup_mode(self, mode_config: ModeConfig, project_dir: Path) -> bool:
        """Complete setup process for a specific mode."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Check dependencies
            task = progress.add_task("Checking dependencies...", total=None)
            checker = DependencyChecker(self.console)
            dependencies = checker.check_mode_dependencies(mode_config)

            missing = [dep for dep, available in dependencies.items() if not available]
            if missing:
                instructions = checker.report_missing_dependencies(dependencies, mode_config)
                return False

            progress.update(task, description="Starting services...")
            if not self.run_docker_compose(mode_config.docker_compose_files, "up"):
                return False

            progress.update(task, description="Waiting for services...")
            if not self.wait_for_services():
                return False

            progress.update(task, description="Running migrations...")
            if not self.run_migrations():
                return False

            progress.update(task, description="Generating SDK...")
            self.generate_sdk()  # Don't fail if SDK generation fails

        return True
