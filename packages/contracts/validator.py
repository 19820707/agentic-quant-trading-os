from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ContractValidationError(Exception):
    """Raised when a payload does not satisfy a local contract schema."""


class SchemaNotFoundError(FileNotFoundError):
    """Raised when a requested local schema file does not exist."""


class InvalidSchemaError(ValueError):
    """Raised when a local schema file cannot be parsed as JSON."""


class RedactionViolationError(ValueError):
    """Raised when a payload declares or implies it contains unredacted secrets."""


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str]
    schema_id: str | None = None


@dataclass
class _CacheEntry:
    schema: dict[str, Any]
    mtime: float


class ContractValidator:
    """Load local JSON Schemas and validate JSON-compatible payloads.

    Schema files are cached in memory and invalidated when the file's
    mtime changes — safe for development workflows without requiring a
    process restart to pick up schema edits.
    """

    def __init__(self, schema_root: Path | str | None = None) -> None:
        if schema_root is None:
            schema_root = Path(__file__).resolve().parent / "schemas"
        self.schema_root = Path(schema_root).resolve()
        self._cache: dict[Path, _CacheEntry] = {}

    def schema_path(self, domain: str, name: str) -> Path:
        domain_path = Path(domain)
        name_path = Path(name)
        if domain_path.is_absolute() or name_path.is_absolute():
            raise SchemaNotFoundError("schema domain and name must be relative")
        if ".." in domain_path.parts or ".." in name_path.parts:
            raise SchemaNotFoundError("schema domain and name must not contain traversal segments")

        schema_name = name if name.endswith(".schema.json") else f"{name}.schema.json"
        candidate = (self.schema_root / domain / schema_name).resolve()
        try:
            candidate.relative_to(self.schema_root)
        except ValueError as exc:
            raise SchemaNotFoundError("schema path must stay within schema root") from exc

        return candidate

    def load_schema(self, domain: str, name: str) -> dict[str, Any]:
        path = self.schema_path(domain, name)
        if not path.is_file():
            raise SchemaNotFoundError(f"schema not found: {path}")

        try:
            current_mtime = os.stat(path).st_mtime
        except OSError:
            current_mtime = 0.0

        cached = self._cache.get(path)
        if cached is not None and cached.mtime == current_mtime:
            return cached.schema

        try:
            with path.open(encoding="utf-8") as schema_file:
                schema = json.load(schema_file)
        except json.JSONDecodeError as exc:
            raise InvalidSchemaError(f"invalid schema JSON: {path}") from exc

        if not isinstance(schema, dict):
            raise InvalidSchemaError(f"schema root must be an object: {path}")

        self._cache[path] = _CacheEntry(schema=schema, mtime=current_mtime)
        return schema

    def validate(self, domain: str, name: str, payload: dict[str, Any]) -> ValidationResult:
        schema = self.load_schema(domain, name)
        schema_id = schema.get("$id")
        payload_copy = copy.deepcopy(payload)

        try:
            import jsonschema
        except ImportError:
            errors = self._minimal_validate(schema, payload_copy)
        else:
            errors = self._jsonschema_validate(jsonschema, schema, payload_copy)

        return ValidationResult(valid=not errors, errors=errors, schema_id=schema_id)

    def validate_or_raise(self, domain: str, name: str, payload: dict[str, Any]) -> None:
        result = self.validate(domain, name, payload)
        if not result.valid:
            message = "; ".join(result.errors)
            raise ContractValidationError(message)

    def validate_redacted(self, domain: str, name: str, payload: dict[str, Any]) -> ValidationResult:
        """Validate a payload and enforce that it declares no unredacted secrets.

        Checks `contains_secrets` is absent or False before schema validation.
        Raises RedactionViolationError if the payload admits to carrying secrets —
        a hard boundary that must never be relaxed.
        """
        if payload.get("contains_secrets") is True:
            raise RedactionViolationError(
                "payload declares contains_secrets=True; redact before validation"
            )
        return self.validate(domain, name, payload)

    def _jsonschema_validate(
        self, jsonschema_module: Any, schema: dict[str, Any], payload: Any
    ) -> list[str]:
        validator_cls = jsonschema_module.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        return sorted(error.message for error in validator.iter_errors(payload))

    def _minimal_validate(self, schema: dict[str, Any], payload: Any) -> list[str]:
        errors: list[str] = []

        if not isinstance(payload, dict):
            return ["payload must be an object"]

        properties = schema.get("properties", {})
        for field_name in schema.get("required", []):
            if field_name not in payload:
                errors.append(f"missing required field: {field_name}")

        if schema.get("additionalProperties") is False:
            for field_name in payload:
                if field_name not in properties:
                    errors.append(f"additional property is not allowed: {field_name}")

        for field_name, field_schema in properties.items():
            if (
                field_name in payload
                and "const" in field_schema
                and payload[field_name] != field_schema["const"]
            ):
                errors.append(f"field {field_name} must equal {field_schema['const']!r}")

        return errors
