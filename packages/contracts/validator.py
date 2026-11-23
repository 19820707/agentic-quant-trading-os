from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .invariants import check_invariants


class ContractValidationError(Exception):
    """Raised when a payload does not satisfy a local contract schema."""


class SchemaNotFoundError(FileNotFoundError):
    """Raised when a requested local schema file does not exist."""


class InvalidSchemaError(ValueError):
    """Raised when a local schema file cannot be parsed as JSON."""


# Keywords the standard-library fallback validator cannot evaluate. A schema
# that uses one must not be reported as satisfied by the fallback.
UNSUPPORTED_FALLBACK_KEYWORDS = frozenset(
    {
        "$ref",
        "allOf",
        "anyOf",
        "oneOf",
        "not",
        "if",
        "then",
        "else",
        "dependentRequired",
        "dependentSchemas",
        "patternProperties",
        "propertyNames",
        "contains",
        "prefixItems",
        "multipleOf",
        "minProperties",
        "maxProperties",
    }
)


def _is_valid_date_time(value: object) -> bool:
    if not isinstance(value, str):
        return True
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str]
    schema_id: str | None = None


class ContractValidator:
    """Load local JSON Schemas and validate JSON-compatible payloads."""

    def __init__(self, schema_root: Path | str | None = None) -> None:
        if schema_root is None:
            schema_root = Path(__file__).resolve().parent / "schemas"
        self.schema_root = Path(schema_root).resolve()

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
            with path.open(encoding="utf-8") as schema_file:
                schema = json.load(schema_file)
        except json.JSONDecodeError as exc:
            raise InvalidSchemaError(f"invalid schema JSON: {path}") from exc

        if not isinstance(schema, dict):
            raise InvalidSchemaError(f"schema root must be an object: {path}")

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

        # Cross-field rules a schema cannot express (for example: a rejected
        # risk decision must not be approved for execution).
        errors = errors + check_invariants(domain, name, payload_copy)

        return ValidationResult(valid=not errors, errors=errors, schema_id=schema_id)

    def validate_or_raise(self, domain: str, name: str, payload: dict[str, Any]) -> None:
        result = self.validate(domain, name, payload)
        if not result.valid:
            message = "; ".join(result.errors)
            raise ContractValidationError(message)

    def _jsonschema_validate(self, jsonschema_module: Any, schema: dict[str, Any], payload: Any) -> list[str]:
        validator_cls = jsonschema_module.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        # jsonschema ignores "format" unless a checker is supplied. Enforce
        # date-time with the same rule as the fallback so both paths agree.
        format_checker = jsonschema_module.FormatChecker(formats=())
        format_checker.checks("date-time")(_is_valid_date_time)
        validator = validator_cls(schema, format_checker=format_checker)
        return sorted(error.message for error in validator.iter_errors(payload))

    def _minimal_validate(self, schema: dict[str, Any], payload: Any) -> list[str]:
        errors: list[str] = []
        self._minimal_validate_value(schema, payload, "$", errors)
        return errors

    def _minimal_validate_value(self, schema: dict[str, Any], value: Any, path: str, errors: list[str]) -> None:
        unsupported = sorted(UNSUPPORTED_FALLBACK_KEYWORDS & schema.keys())
        if unsupported:
            errors.append(
                f"{path}: schema keyword(s) {', '.join(unsupported)} need the jsonschema package; "
                "fallback validator cannot confirm this payload"
            )

        if "const" in schema and value != schema["const"]:
            errors.append(f"{path}: expected const {schema['const']!r}")

        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path}: value {value!r} is not in enum")

        expected_type = schema.get("type")
        if expected_type is not None and not self._minimal_matches_type(value, expected_type):
            errors.append(f"{path}: expected type {expected_type!r}")
            return

        if isinstance(value, dict):
            self._minimal_validate_object(schema, value, path, errors)
        elif isinstance(value, list):
            self._minimal_validate_array(schema, value, path, errors)
        elif isinstance(value, str):
            self._minimal_validate_string(schema, value, path, errors)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            self._minimal_validate_number(schema, value, path, errors)

    def _minimal_validate_object(
        self,
        schema: dict[str, Any],
        payload: dict[str, Any],
        path: str,
        errors: list[str],
    ) -> None:
        properties = schema.get("properties", {})
        for field in schema.get("required", []):
            if field not in payload:
                errors.append(f"{path}: missing required field: {field}")

        if schema.get("additionalProperties") is False:
            for field in payload:
                if field not in properties:
                    errors.append(f"{path}.{field}: additional property is not allowed")

        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            for field, field_value in payload.items():
                if field not in properties:
                    self._minimal_validate_value(additional, field_value, f"{path}.{field}", errors)

        for field, field_schema in properties.items():
            if field in payload and isinstance(field_schema, dict):
                self._minimal_validate_value(field_schema, payload[field], f"{path}.{field}", errors)

    def _minimal_validate_array(
        self,
        schema: dict[str, Any],
        value: list[Any],
        path: str,
        errors: list[str],
    ) -> None:
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: expected at least {min_items} items")

        max_items = schema.get("maxItems")
        if isinstance(max_items, int) and len(value) > max_items:
            errors.append(f"{path}: expected at most {max_items} items")

        if schema.get("uniqueItems") is True:
            seen: list[Any] = []
            for item in value:
                if any(type(item) is type(other) and item == other for other in seen):
                    errors.append(f"{path}: items are not unique")
                    break
                seen.append(item)

        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                self._minimal_validate_value(item_schema, item, f"{path}[{index}]", errors)

    def _minimal_validate_string(
        self,
        schema: dict[str, Any],
        value: str,
        path: str,
        errors: list[str],
    ) -> None:
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: shorter than minLength {min_length}")

        max_length = schema.get("maxLength")
        if isinstance(max_length, int) and len(value) > max_length:
            errors.append(f"{path}: longer than maxLength {max_length}")

        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.search(pattern, value):
            errors.append(f"{path}: value does not match required pattern")

        if schema.get("format") == "date-time" and not _is_valid_date_time(value):
            errors.append(f"{path}: invalid date-time")

    def _minimal_validate_number(
        self,
        schema: dict[str, Any],
        value: int | float,
        path: str,
        errors: list[str],
    ) -> None:
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: below minimum {minimum}")

        maximum = schema.get("maximum")
        if isinstance(maximum, (int, float)) and value > maximum:
            errors.append(f"{path}: above maximum {maximum}")

        exclusive_maximum = schema.get("exclusiveMaximum")
        if isinstance(exclusive_maximum, (int, float)) and value >= exclusive_maximum:
            errors.append(f"{path}: not below exclusiveMaximum {exclusive_maximum}")

        exclusive_minimum = schema.get("exclusiveMinimum")
        if isinstance(exclusive_minimum, (int, float)) and value <= exclusive_minimum:
            errors.append(f"{path}: not above exclusiveMinimum {exclusive_minimum}")

    def _minimal_matches_type(self, value: Any, expected_type: str | list[str]) -> bool:
        if isinstance(expected_type, list):
            return any(self._minimal_matches_type(value, item) for item in expected_type)

        checks = {
            "object": lambda candidate: isinstance(candidate, dict),
            "array": lambda candidate: isinstance(candidate, list),
            "string": lambda candidate: isinstance(candidate, str),
            "number": lambda candidate: isinstance(candidate, (int, float)) and not isinstance(candidate, bool),
            "boolean": lambda candidate: isinstance(candidate, bool),
            "null": lambda candidate: candidate is None,
        }
        check = checks.get(expected_type)
        if check is None:
            return True
        return check(value)
