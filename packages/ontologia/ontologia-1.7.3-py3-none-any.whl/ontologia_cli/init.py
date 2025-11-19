"""Project initialization functionality for Ontologia CLI."""

from __future__ import annotations

import secrets
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Template definitions
TEMPLATES = {
    "simple-api": {
        "name": "Simple API",
        "description": "Basic CRUD operations with PostgreSQL + FastAPI",
        "directory": "simple-api",
        "features": ["REST API", "PostgreSQL", "JWT Auth", "Basic CRUD"],
        "setup_time": "5 minutes",
        "docker_compose": "docker-compose.yml",
        "env_example": ".env.example",
    },
    "data-platform": {
        "name": "Data Platform",
        "description": "Analytics with DuckDB + dbt + Dagster",
        "directory": "data-platform",
        "features": ["Analytics", "DuckDB", "dbt", "Dagster", "ETL"],
        "setup_time": "10 minutes",
        "docker_compose": "docker-compose.analytics.yml",
        "env_example": ".env.example",
    },
    "knowledge-graph": {
        "name": "Knowledge Graph",
        "description": "Graph traversals with KùzuDB",
        "directory": "knowledge-graph",
        "features": ["Graph Database", "KùzuDB", "Traversals", "Relationships"],
        "setup_time": "15 minutes",
        "docker_compose": "docker-compose.graph.yml",
        "env_example": ".env.example",
    },
    "enterprise-workflows": {
        "name": "Enterprise Workflows",
        "description": "Full stack with search, workflows, real-time",
        "directory": "enterprise-workflows",
        "features": ["Search", "Workflows", "Real-time", "Full Stack"],
        "setup_time": "20 minutes",
        "docker_compose": "docker-compose.full.yml",
        "env_example": ".env.example",
    },
}


def get_templates_dir() -> Path:
    """Get the templates directory path."""
    # Try to find templates relative to this file
    current_dir = Path(__file__).parent
    # Go up from packages/ontologia_cli to repo root
    # Current: /Users/kevinsaltarelli/Documents/GitHub/ontologia/packages/ontologia_cli
    # Target:   /Users/kevinsaltarelli/Documents/GitHub/ontologia/templates
    repo_root = current_dir.parent.parent
    templates_dir = repo_root / "templates"

    if not templates_dir.exists():
        raise RuntimeError(f"Templates directory not found: {templates_dir}")

    return templates_dir


def list_available_templates() -> None:
    """List all available templates with details."""
    console.print("\n[bold cyan]🚀 Available Ontologia Templates[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Template", style="bold", width=20)
    table.add_column("Description", width=30)
    table.add_column("Features", width=25)
    table.add_column("Setup Time", width=12)

    for _template_key, template_info in TEMPLATES.items():
        features_str = ", ".join(template_info["features"])
        table.add_row(
            template_info["name"],
            template_info["description"],
            features_str,
            f"⏱️ {template_info['setup_time']}",
        )

    console.print(table)

    console.print("\n[bold]Usage Examples:[/bold]")
    console.print("  ontologia init --template simple-api my-project")
    console.print("  ontologia init --template data-platform my-analytics")
    console.print("  ontologia init my-project  # Interactive selection")

    console.print("\n[bold]Template Details:[/bold]")
    for template_key, template_info in TEMPLATES.items():
        console.print(f"\n[blue]{template_info['name']}[/blue] ({template_key})")
        console.print(f"  {template_info['description']}")
        console.print(f"  Features: {', '.join(template_info['features'])}")
        console.print(f"  Setup time: {template_info['setup_time']}")


def validate_template(template: str) -> str:
    """Validate template name and return normalized key."""
    if template in TEMPLATES:
        return template

    # Try case-insensitive match
    for key in TEMPLATES:
        if key.lower() == template.lower():
            return key

    # Try name match
    for key, info in TEMPLATES.items():
        if info["name"].lower() == template.lower():
            return key

    raise ValueError(f"Unknown template: {template}. Available: {', '.join(TEMPLATES.keys())}")


def validate_project_name(name: str) -> str:
    """Validate project name."""
    if not name:
        raise ValueError("Project name cannot be empty")

    # Check for invalid characters
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    for char in invalid_chars:
        if char in name:
            raise ValueError(f"Project name cannot contain '{char}'")

    # Check if it starts with dot or dash
    if name.startswith((".", "-")):
        raise ValueError("Project name cannot start with '.' or '-'")

    return name


def copy_template_files(template_dir: Path, target_dir: Path, project_name: str) -> None:
    """Copy template files to target directory."""
    if not template_dir.exists():
        raise RuntimeError(f"Template directory not found: {template_dir}")

    # Copy all files from template
    for item in template_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, target_dir / item.name)
        elif item.is_dir() and item.name != "__pycache__":
            target_subdir = target_dir / item.name
            shutil.copytree(item, target_subdir, ignore=shutil.ignore_patterns("__pycache__"))


def customize_project_files(target_dir: Path, project_name: str, template_key: str) -> None:
    """Customize project files with project-specific values."""
    template_info = TEMPLATES[template_key]

    # Customize pyproject.toml
    pyproject_path = target_dir / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        content = content.replace("my-ontology-api", project_name)
        content = content.replace("Your Name", "Developer")
        content = content.replace("your.email@example.com", f"developer@{project_name}.com")
        pyproject_path.write_text(content, encoding="utf-8")

    # Customize .env.example
    env_path = target_dir / ".env.example"
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        content = content.replace("my-ontology-api", project_name)
        env_path.write_text(content, encoding="utf-8")

    # Customize docker-compose.yml
    compose_path = target_dir / template_info["docker_compose"]
    if compose_path.exists():
        content = compose_path.read_text(encoding="utf-8")
        content = content.replace("my-ontology-api", project_name)
        compose_path.write_text(content, encoding="utf-8")


def generate_secrets(target_dir: Path) -> None:
    """Generate secure secrets for the project."""
    env_path = target_dir / ".env.example"
    if not env_path.exists():
        return

    content = env_path.read_text(encoding="utf-8")

    # Generate secure secrets
    secret_key = secrets.token_urlsafe(32)
    jwt_secret_key = secrets.token_urlsafe(32)

    content = content.replace("dev-secret-key-change-in-production", secret_key)
    content = content.replace("jwt-secret-key-change-in-production", jwt_secret_key)

    env_path.write_text(content, encoding="utf-8")


def create_git_repo(target_dir: Path) -> None:
    """Initialize git repository."""
    try:
        import git

        repo = git.Repo.init(target_dir)

        # Create .gitignore
        gitignore_path = target_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
.env
.ontologia/
data/
logs/
*.duckdb
*.kuzu

# Docker
.dockerignore
"""
            gitignore_path.write_text(gitignore_content.strip(), encoding="utf-8")

        # Initial commit
        repo.index.add([str(p) for p in target_dir.iterdir() if p.name != ".git"])
        repo.index.commit("Initial commit from Ontologia template")

    except ImportError:
        console.print("[yellow]⚠️ Git not available. Skipping repository initialization.[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠️ Failed to initialize git repository: {e}[/yellow]")


def print_success_message(project_name: str, template_key: str) -> None:
    """Print success message with next steps."""
    template_info = TEMPLATES[template_key]

    console.print(f"\n[green bold]🎉 Project '{project_name}' created successfully![/green bold]")

    # Project info panel
    panel_content = f"""
[bold]Template:[/bold] {template_info['name']}
[bold]Features:[/bold] {', '.join(template_info['features'])}
[bold]Setup Time:[/bold] {template_info['setup_time']}
[bold]Location:[/bold] ./{project_name}/
"""
    console.print(Panel(panel_content.strip(), title="Project Info", border_style="green"))

    # Next steps
    console.print("\n[bold cyan]🚀 Next Steps:[/bold cyan]")
    console.print(f"1. [blue]cd {project_name}[/blue]")
    console.print("2. [blue]cp .env.example .env[/blue]  # Configure your environment")
    console.print("3. [blue]docker-compose up -d[/blue]  # Start services")
    console.print("4. [blue]Visit http://localhost:8000/docs[/blue]  # API documentation")

    # Additional steps based on template
    if template_key == "data-platform":
        console.print("\n[bold]📊 Analytics Setup:[/bold]")
        console.print("5. [blue]docker-compose -f docker-compose.analytics.yml up -d[/blue]")
        console.print("6. [blue]Visit http://localhost:3000[/blue]  # Dagster UI")
    elif template_key == "knowledge-graph":
        console.print("\n[bold]🕸️ Graph Setup:[/bold]")
        console.print("5. Set [blue]STORAGE_MODE=sql_kuzu[/blue] in .env")
        console.print("6. Restart services to enable graph features")
    elif template_key == "enterprise-workflows":
        console.print("\n[bold]🏢 Enterprise Setup:[/bold]")
        console.print("5. [blue]docker-compose -f docker-compose.full.yml up -d[/blue]")
        console.print("6. Configure additional services as needed")

    console.print("\n[bold]💡 Learn More:[/bold]")
    console.print("• [blue]ontologia --help[/blue]  # CLI commands")
    console.print("• [blue]README.md[/blue]  # Template-specific guide")
    console.print("• [blue]examples/[/blue]  # Usage examples")
    console.print("• [blue]https://github.com/kevinqz/ontologia[/blue]  # Documentation")


def init_project(project_name: str, template: str) -> None:
    """Initialize a new Ontologia project from a template."""
    try:
        # Validate inputs
        project_name = validate_project_name(project_name)
        template_key = validate_template(template)

        # Get paths
        templates_dir = get_templates_dir()
        template_dir = templates_dir / template_key
        target_dir = Path.cwd() / project_name

        # Check if target directory already exists
        if target_dir.exists():
            raise FileExistsError(f"Directory '{project_name}' already exists")

        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        console.print(
            f"[blue]📁 Creating project '{project_name}' from '{template_key}' template...[/blue]"
        )

        # Copy template files
        copy_template_files(template_dir, target_dir, project_name)

        # Customize files
        customize_project_files(target_dir, project_name, template_key)

        # Generate secrets
        generate_secrets(target_dir)

        # Initialize git repository
        create_git_repo(target_dir)

        # Print success message
        print_success_message(project_name, template_key)

    except Exception as e:
        # Cleanup on failure
        target_dir = Path.cwd() / project_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        raise e
