"""
📦 Dependency management utilities for Ontologia scripts.

Provides helpers for managing optional dependencies with graceful
fallbacks and clear error messages.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from rich.console import Console

T = TypeVar("T")


class DependencyError(Exception):
    """Raised when an optional dependency is required but not available."""

    def __init__(self, package_name: str, install_group: str | None = None) -> None:
        if install_group:
            message = (
                f"{package_name} is not installed. "
                f"Install with: uv sync --group {install_group}"
            )
        else:
            message = (
                f"{package_name} is not installed. " f"Install with: pip install {package_name}"
            )
        super().__init__(message)
        self.package_name = package_name
        self.install_group = install_group


def optional_import(
    module_name: str,
    package_name: str | None = None,
    install_group: str | None = None,
    fallback: Any = None,
) -> Callable[[], Any]:
    """
    Create a lazy import function for an optional dependency.

    Args:
        module_name: Name of the module to import
        package_name: Package name for error messages (defaults to module_name)
        install_group: Install group for uv-based installation
        fallback: Fallback value if import fails and no exception should be raised

    Returns:
        Function that imports the module when called

    Example:
        duckdb = optional_import("duckdb", install_group="analytics")
        # Later:
        conn = duckdb().connect(":memory:")
    """
    if package_name is None:
        package_name = module_name

    cache: Any = None

    def _import() -> Any:
        nonlocal cache
        if cache is not None:
            return cache

        try:
            cache = __import__(module_name)
            return cache
        except ImportError as e:
            if fallback is not None:
                return fallback
            raise DependencyError(package_name, install_group) from e

    return _import


def require_optional_dependency(
    module_name: str,
    package_name: str | None = None,
    install_group: str | None = None,
) -> Any:
    """
    Import an optional dependency, raising a clear error if not available.

    Args:
        module_name: Name of the module to import
        package_name: Package name for error messages
        install_group: Install group for uv-based installation

    Returns:
        Imported module

    Raises:
        DependencyError: If the dependency is not available
    """
    import_func = optional_import(module_name, package_name, install_group)
    return import_func()


def check_dependencies(
    dependencies: list[dict[str, Any]],
    console: Console | None = None,
) -> dict[str, bool]:
    """
    Check availability of multiple optional dependencies.

    Args:
        dependencies: List of dependency specifications with keys:
            - name: Module name to import
            - package: Package name for error messages (optional)
            - group: Install group (optional)
            - required: Whether this dependency is required (default: False)
        console: Console instance for output

    Returns:
        Dictionary mapping dependency names to availability status
    """
    if console is None:
        console = Console()

    results: dict[str, bool] = {}

    for dep in dependencies:
        name = dep["name"]
        package = dep.get("package", name)
        group = dep.get("group")
        required = dep.get("required", False)

        try:
            __import__(name)
            results[name] = True
        except ImportError:
            results[name] = False
            if required:
                console.print(f"❌ Required dependency '{package}' is not installed")
                if group:
                    console.print(f"   Install with: uv sync --group {group}")
                else:
                    console.print(f"   Install with: pip install {package}")
            else:
                console.print(f"⚠️  Optional dependency '{package}' is not available")

    return results


def lazy_import(module_path: str) -> Any:
    """
    Lazy import a module or object from a module.

    Args:
        module_path: Module path or module.object path

    Returns:
        Lazy proxy that imports when accessed

    Example:
        pandas = lazy_import("pandas")
        df = pandas.DataFrame()  # Imports pandas on first use
    """

    class LazyProxy:
        def __init__(self, module_path: str) -> None:
            self.module_path = module_path
            self._module = None
            self._object_name = None

            if "." in module_path:
                self._module_name, self._object_name = module_path.rsplit(".", 1)
            else:
                self._module_name = module_path

        def _load(self) -> Any:
            if self._module is None:
                module = __import__(self._module_name)

                if self._object_name:
                    # Navigate to the specific object
                    for part in self._module_name.split(".")[1:]:
                        module = getattr(module, part)
                    self._module = getattr(module, self._object_name)
                else:
                    self._module = module

            return self._module

        def __getattr__(self, name: str) -> Any:
            obj = self._load()
            return getattr(obj, name)

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            obj = self._load()
            return obj(*args, **kwargs)

        def __repr__(self) -> str:
            return f"<LazyProxy: {self.module_path}>"

    return LazyProxy(module_path)
