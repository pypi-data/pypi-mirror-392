from __future__ import annotations

import csv
import sqlite3
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

__all__ = ["DataAnalysisService"]


class DataAnalysisService:
    """Lightweight data profiling utilities used by API tests and MCP tools."""

    def __init__(
        self,
        instances_service: Any | None = None,
        metamodel_service: Any | None = None,
        *,
        http_client_factory: Callable[..., httpx.Client] | None = None,
    ) -> None:
        self.instances_service = instances_service
        self.metamodel_service = metamodel_service
        self._http_client_factory = http_client_factory or httpx.Client

    # ------------------------------------------------------------------
    # CSV / local sources
    # ------------------------------------------------------------------
    def profile_source(self, source_path: str | Path, *, sample_size: int = 100) -> dict[str, Any]:
        if sample_size <= 0:
            raise ValueError("sample_size must be positive")

        path = Path(source_path)
        if not path.exists():
            raise ValueError(f"Data source '{path}' not found")

        suffix = path.suffix.lower()
        if suffix not in {".csv", ".tsv"}:
            raise ValueError("Only CSV/TSV files are supported for profiling")

        delimiter = "\t" if suffix == ".tsv" else ","
        records: list[dict[str, Any]] = []
        column_order: Iterable[str] | None = None
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            column_order = reader.fieldnames or []
            for row in reader:
                normalized = {key: row.get(key) for key in (reader.fieldnames or row.keys())}
                records.append(normalized)
                if len(records) >= sample_size:
                    break

        return {
            "source_path": str(path),
            "rows_profiled": len(records),
            "columns": self._profile_records(records, column_order=column_order),
        }

    # ------------------------------------------------------------------
    # SQL sources
    # ------------------------------------------------------------------
    def profile_sql_table(
        self,
        connection_url: str,
        table_name: str,
        *,
        sample_size: int = 100,
    ) -> dict[str, Any]:
        if sample_size <= 0:
            raise ValueError("sample_size must be positive")

        parsed = urlparse(connection_url)
        if parsed.scheme != "sqlite":  # pragma: no cover - defensive guard
            raise ValueError("Only sqlite URLs are supported in this profiling helper")

        db_path = parsed.path
        if parsed.netloc:
            db_path = f"//{parsed.netloc}{parsed.path}"
        db_path = Path(db_path).resolve()

        if not db_path.exists():
            raise ValueError(f"Database '{db_path}' not found")

        if not table_name.replace("_", "").isalnum():  # pragma: no cover - basic validation
            raise ValueError("Table name contains unsupported characters")

        records: list[dict[str, Any]] = []
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT ?", (sample_size,))
            for row in cursor.fetchall():
                records.append(dict(row))

        return {
            "connection_url": connection_url,
            "table_name": table_name,
            "rows_profiled": len(records),
            "columns": self._profile_records(records),
        }

    # ------------------------------------------------------------------
    # REST / JSON sources
    # ------------------------------------------------------------------
    def profile_rest_endpoint(
        self,
        url: str,
        *,
        sample_size: int = 100,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        array_path: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> dict[str, Any]:
        if sample_size <= 0:
            raise ValueError("sample_size must be positive")

        request_method = method.upper()
        with self._http_client_factory(timeout=timeout_seconds) as client:
            response = client.request(request_method, url, headers=headers)
            response.raise_for_status()
            payload = response.json()

        records = self._extract_records(payload, array_path)
        sampled = records[:sample_size]

        return {
            "url": url,
            "rows_profiled": len(sampled),
            "columns": self._profile_records(sampled),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _profile_records(
        self,
        records: list[dict[str, Any]],
        *,
        column_order: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        if not records:
            columns = list(column_order or [])
            return [
                {
                    "name": name,
                    "inferred_type": "string",
                    "is_highly_unique": False,
                    "unique_count_in_sample": 0,
                    "null_count_in_sample": 0,
                    "example_values": [],
                }
                for name in columns
            ]

        ordered: list[str] = list(column_order or [])
        for record in records:
            for key in record.keys():
                if key not in ordered:
                    ordered.append(key)

        profiles: list[dict[str, Any]] = []
        for name in ordered:
            values = [record.get(name) for record in records]
            profiles.append(self._build_column_profile(name, values))
        return profiles

    def _build_column_profile(self, name: str, values: list[Any]) -> dict[str, Any]:
        non_null = [value for value in values if not self._is_null(value)]

        unique_markers: list[str] = []
        for value in non_null:
            marker = self._normalize_for_uniqueness(value)
            if marker not in unique_markers:
                unique_markers.append(marker)

        examples: list[str] = []
        for value in non_null:
            if len(examples) >= 3:
                break
            examples.append(self._stringify(value))

        inferred_type = self._infer_type(non_null)

        return {
            "name": name,
            "inferred_type": inferred_type,
            "is_highly_unique": len(unique_markers) == len(non_null) and len(non_null) > 0,
            "unique_count_in_sample": len(unique_markers),
            "null_count_in_sample": sum(1 for value in values if self._is_null(value)),
            "example_values": examples,
        }

    def _extract_records(self, payload: Any, array_path: str | None) -> list[dict[str, Any]]:
        target = payload
        if array_path:
            for segment in array_path.split("."):
                if isinstance(target, dict) and segment in target:
                    target = target[segment]
                else:
                    raise ValueError(f"Array path '{array_path}' not found in payload")

        if isinstance(target, dict):  # pragma: no cover - defensive
            raise ValueError("Expected an array of objects from the REST endpoint")
        if not isinstance(target, list):
            raise ValueError("REST endpoint payload must be a list or contain a list")

        normalized: list[dict[str, Any]] = []
        for item in target:
            if isinstance(item, dict):
                normalized.append(item)
            else:
                normalized.append({"value": item})
        return normalized

    @staticmethod
    def _is_null(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    def _normalize_for_uniqueness(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    def _infer_type(self, values: list[Any]) -> str:
        if not values:
            return "string"

        if all(self._looks_like_bool(v) for v in values):
            return "bool"
        if all(self._looks_like_int(v) for v in values):
            return "int"
        if all(self._looks_like_float(v) for v in values):
            return "float"
        return "string"

    def _looks_like_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.strip().lower() in {"true", "false", "yes", "no"}
        return False

    def _looks_like_int(self, value: Any) -> bool:
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("-"):
                stripped = stripped[1:]
            return stripped.isdigit()
        return False

    def _looks_like_float(self, value: Any) -> bool:
        if isinstance(value, bool):
            return False
        if isinstance(value, float):
            return True
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return False
            try:
                float(stripped)
            except ValueError:
                return False
            return not self._looks_like_int(stripped)
        if isinstance(value, int):
            return False
        try:
            float(value)
        except (TypeError, ValueError):
            return False
        return True
