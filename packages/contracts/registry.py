"""Local schema index with mtime-aware $id caching.

Reads the schema file only when the file has changed (mtime comparison).
Does not validate payloads or interpret contracts — index only.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "SchemaInfo",
    "SchemaRegistry",
    "SchemaRegistryError",
    "UnknownSchemaError",
]


class SchemaRegistryError(Exception):
    """Raised when the local schema registry cannot resolve a schema."""


class UnknownSchemaError(SchemaRegistryError):
    """Raised when a requested schema is not registered locally."""


@dataclass(frozen=True)
class SchemaInfo:
    domain: str
    name: str
    path: Path
    schema_id: str | None = None


@dataclass
class _SchemaCacheLine:
    schema_id: str | None
    mtime: float


class SchemaRegistry:
    """Local schema index with mtime-aware $id caching.

    The registry reads each schema file once per mtime window. When a file
    changes on disk (mtime advances), the cached entry is invalidated and the
    file is re-read on the next access — safe for development workflows without
    requiring a process restart to pick up schema edits.
    """

    def __init__(self, schema_root: Path | str | None = None) -> None:
        if schema_root is None:
            schema_root = Path(__file__).resolve().parent / "schemas"
        self.schema_root = Path(schema_root).resolve()
        self._id_cache: dict[Path, _SchemaCacheLine] = {}

    def list_domains(self) -> list[str]:
        domains = {
            path.parent.name
            for path in self.schema_root.glob("*/*.schema.json")
            if self._is_inside_schema_root(path)
        }
        return sorted(domains)

    def list_schemas(self, domain: str | None = None) -> list[SchemaInfo]:
        if domain is not None:
            domain_path = self._resolve_domain(domain)
            paths = sorted(domain_path.glob("*.schema.json"))
        else:
            paths = sorted(self.schema_root.glob("*/*.schema.json"))

        return [self._schema_info(path) for path in paths if self._is_inside_schema_root(path)]

    def get(self, domain: str, name: str) -> SchemaInfo:
        candidate = self._schema_path(domain, name)
        if not candidate.is_file():
            raise UnknownSchemaError(f"schema is not registered: {self.schema_key(domain, name)}")
        return self._schema_info(candidate)

    def exists(self, domain: str, name: str) -> bool:
        try:
            self.get(domain, name)
        except UnknownSchemaError:
            return False
        return True

    def schema_key(self, domain: str, name: str) -> str:
        schema_name = name.removesuffix(".schema.json")
        return f"{domain}/{schema_name}"

    def _schema_path(self, domain: str, name: str) -> Path:
        domain_path = Path(domain)
        name_path = Path(name)
        if domain_path.is_absolute() or name_path.is_absolute():
            raise UnknownSchemaError("schema domain and name must be relative")
        if ".." in domain_path.parts or ".." in name_path.parts:
            raise UnknownSchemaError("schema domain and name must not contain traversal segments")

        schema_name = name if name.endswith(".schema.json") else f"{name}.schema.json"
        candidate = (self.schema_root / domain / schema_name).resolve()
        if not self._is_inside_schema_root(candidate):
            raise UnknownSchemaError("schema path must stay within schema root")
        return candidate

    def _resolve_domain(self, domain: str) -> Path:
        domain_path = Path(domain)
        if domain_path.is_absolute() or ".." in domain_path.parts:
            raise UnknownSchemaError(
                "schema domain must be relative and must not contain traversal segments"
            )
        candidate = (self.schema_root / domain).resolve()
        if not self._is_inside_schema_root(candidate):
            raise UnknownSchemaError("schema domain must stay within schema root")
        return candidate

    def _is_inside_schema_root(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.schema_root)
        except ValueError:
            return False
        return True

    def _schema_info(self, path: Path) -> SchemaInfo:
        resolved = path.resolve()
        if not self._is_inside_schema_root(resolved):
            raise UnknownSchemaError("schema path must stay within schema root")

        schema_id = self._read_schema_id(resolved)
        domain = resolved.parent.name
        name = resolved.name.removesuffix(".schema.json")
        return SchemaInfo(domain=domain, name=name, path=resolved, schema_id=schema_id)

    def _read_schema_id(self, path: Path) -> str | None:
        """Return the $id from a schema file, using mtime cache to avoid redundant I/O."""
        try:
            current_mtime = os.stat(path).st_mtime
        except OSError:
            current_mtime = 0.0

        cached = self._id_cache.get(path)
        if cached is not None and cached.mtime == current_mtime:
            return cached.schema_id

        with path.open(encoding="utf-8") as schema_file:
            schema: Any = json.load(schema_file)

        schema_id: str | None = None
        if isinstance(schema, dict):
            candidate_id = schema.get("$id")
            if isinstance(candidate_id, str):
                schema_id = candidate_id

        self._id_cache[path] = _SchemaCacheLine(schema_id=schema_id, mtime=current_mtime)
        return schema_id
