"""A small, strict subset of JSON Schema, plus contract diffing.

Why not a dependency: the contract layer must run in a sandbox with no network
and no install step. The subset implemented here is what contracts in this
package actually use, and anything outside it is reported as
``E_SCHEMA_UNSUPPORTED`` instead of being silently ignored — a validator that
quietly skips a keyword is worse than no validator.

Supported keywords
------------------
type, properties, required, additionalProperties, items, enum, const,
minimum, maximum, minLength, maxLength, pattern, minItems, maxItems,
uniqueItems, anyOf, allOf
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SUPPORTED = {
    "type", "properties", "required", "additionalProperties", "items", "enum",
    "const", "minimum", "maximum", "minLength", "maxLength", "pattern",
    "minItems", "maxItems", "uniqueItems", "anyOf", "allOf", "description",
    "title", "default", "examples", "$schema", "$id", "definitions", "$defs",
    "format", "deprecated", "x-consumers",
}

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


class SchemaError(ValueError):
    """A value does not satisfy its schema."""

    def __init__(self, message: str, path: str = "/") -> None:
        super().__init__(message)
        self.message = message
        self.path = path

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.path}: {self.message}"


class UnsupportedSchema(ValueError):
    """The schema uses a keyword this validator does not implement."""


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    py = TYPES.get(expected)
    if py is None:
        raise UnsupportedSchema(f"unknown type {expected!r}")
    if expected == "object":
        return isinstance(value, dict)
    return isinstance(value, py)


def validate(instance: Any, schema: dict[str, Any], *, path: str = "/") -> None:
    """Raise ``SchemaError`` on the first violation. Deterministic order."""
    if not isinstance(schema, dict):
        raise UnsupportedSchema("schema must be an object")

    unknown = set(schema) - SUPPORTED
    if unknown:
        raise UnsupportedSchema(f"unsupported keywords: {sorted(unknown)}")

    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"expected constant {schema['const']!r}", path)

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{instance!r} not in {schema['enum']!r}", path)

    if "anyOf" in schema:
        errors = []
        for i, sub in enumerate(schema["anyOf"]):
            try:
                validate(instance, sub, path=path)
                break
            except SchemaError as exc:
                errors.append(f"[{i}] {exc}")
        else:
            raise SchemaError("does not match anyOf: " + "; ".join(errors), path)

    if "allOf" in schema:
        for sub in schema["allOf"]:
            validate(instance, sub, path=path)

    expected = schema.get("type")
    if expected is not None:
        options = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(instance, opt) for opt in options):
            raise SchemaError(f"expected {expected}, got {type(instance).__name__}", path)

    if isinstance(instance, str):
        _validate_string(instance, schema, path)
    elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
        _validate_number(instance, schema, path)
    elif isinstance(instance, list):
        _validate_array(instance, schema, path)
    elif isinstance(instance, dict):
        _validate_object(instance, schema, path)


def _validate_string(value: str, schema: dict[str, Any], path: str) -> None:
    if "minLength" in schema and len(value) < schema["minLength"]:
        raise SchemaError(f"shorter than minLength {schema['minLength']}", path)
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        raise SchemaError(f"longer than maxLength {schema['maxLength']}", path)
    if "pattern" in schema and not re.search(schema["pattern"], value):
        raise SchemaError(f"does not match pattern {schema['pattern']!r}", path)


def _validate_number(value: float, schema: dict[str, Any], path: str) -> None:
    if "minimum" in schema and value < schema["minimum"]:
        raise SchemaError(f"below minimum {schema['minimum']}", path)
    if "maximum" in schema and value > schema["maximum"]:
        raise SchemaError(f"above maximum {schema['maximum']}", path)


def _validate_array(value: list[Any], schema: dict[str, Any], path: str) -> None:
    if "minItems" in schema and len(value) < schema["minItems"]:
        raise SchemaError(f"fewer than minItems {schema['minItems']}", path)
    if "maxItems" in schema and len(value) > schema["maxItems"]:
        raise SchemaError(f"more than maxItems {schema['maxItems']}", path)
    if schema.get("uniqueItems"):
        seen = [json.dumps(v, sort_keys=True) for v in value]
        if len(seen) != len(set(seen)):
            raise SchemaError("items are not unique", path)
    if "items" in schema:
        for i, item in enumerate(value):
            validate(item, schema["items"], path=f"{path.rstrip('/')}/{i}")


def _validate_object(value: dict[str, Any], schema: dict[str, Any], path: str) -> None:
    for key in schema.get("required", []):
        if key not in value:
            raise SchemaError(f"missing required property {key!r}", path)
    properties = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)
    for key, item in value.items():
        if key in properties:
            validate(item, properties[key], path=f"{path.rstrip('/')}/{key}")
        elif additional is False:
            raise SchemaError(f"unexpected property {key!r}", path)
        elif isinstance(additional, dict):
            validate(item, additional, path=f"{path.rstrip('/')}/{key}")


# --------------------------------------------------------------------------
# contract diffing
# --------------------------------------------------------------------------
#: changes that break consumers
BREAKING = {
    "type_changed",
    "property_removed",
    "required_added",
    "enum_narrowed",
    "additional_properties_narrowed",
}


def diff(old: dict[str, Any], new: dict[str, Any], *, path: str = "") -> list[dict[str, Any]]:
    """Structural diff of two schemas, classified as breaking or compatible."""
    changes: list[dict[str, Any]] = []
    where = path or "/"

    if old.get("type") != new.get("type"):
        changes.append({"kind": "type_changed", "path": where,
                        "before": old.get("type"), "after": new.get("type")})

    if "enum" in old and "enum" in new:
        removed = [v for v in old["enum"] if v not in new["enum"]]
        added = [v for v in new["enum"] if v not in old["enum"]]
        if removed:
            changes.append({"kind": "enum_narrowed", "path": where, "removed": removed})
        if added:
            changes.append({"kind": "enum_widened", "path": where, "added": added})

    old_props = old.get("properties", {})
    new_props = new.get("properties", {})
    for key in old_props:
        if key not in new_props:
            changes.append({"kind": "property_removed", "path": f"{where}{key}",
                            "property": key})
    for key in new_props:
        if key not in old_props:
            changes.append({"kind": "property_added", "path": f"{where}{key}",
                            "property": key})

    added_required = [k for k in new.get("required", []) if k not in old.get("required", [])]
    if added_required:
        changes.append({"kind": "required_added", "path": where, "properties": added_required})
    removed_required = [k for k in old.get("required", []) if k not in new.get("required", [])]
    if removed_required:
        changes.append({"kind": "required_removed", "path": where, "properties": removed_required})

    if old.get("additionalProperties", True) is not False and new.get("additionalProperties") is False:
        changes.append({"kind": "additional_properties_narrowed", "path": where})

    for key in old_props:
        if key in new_props:
            changes.extend(diff(old_props[key], new_props[key], path=f"{where}{key}/"))

    return changes


def classify(changes: list[dict[str, Any]]) -> str:
    """``major`` if anything breaks consumers, else ``minor`` or ``patch``."""
    if any(change["kind"] in BREAKING for change in changes):
        return "major"
    if changes:
        return "minor"
    return "patch"


def load(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check_schema(schema: dict[str, Any]) -> list[str]:
    """Self-check: every keyword used must be one we implement."""
    problems: list[str] = []
    unknown = set(schema) - SUPPORTED
    if unknown:
        problems.append(f"unsupported keywords: {sorted(unknown)}")
    for key, sub in (schema.get("properties") or {}).items():
        problems.extend(f"properties.{key}: {p}" for p in check_schema(sub))
    if isinstance(schema.get("items"), dict):
        problems.extend(f"items: {p}" for p in check_schema(schema["items"]))
    for combinator in ("anyOf", "allOf"):
        for index, sub in enumerate(schema.get(combinator) or []):
            problems.extend(f"{combinator}[{index}]: {p}" for p in check_schema(sub))
    for name, sub in (schema.get("$defs") or schema.get("definitions") or {}).items():
        problems.extend(f"definitions.{name}: {p}" for p in check_schema(sub))
    return problems


def keywords_used(schema: dict[str, Any]) -> set[str]:
    """Every keyword a schema actually relies on, for the manifest audit."""
    used = set(schema)
    for sub in (schema.get("properties") or {}).values():
        if isinstance(sub, dict):
            used |= keywords_used(sub)
    if isinstance(schema.get("items"), dict):
        used |= keywords_used(schema["items"])
    for combinator in ("anyOf", "allOf"):
        for sub in schema.get(combinator) or []:
            if isinstance(sub, dict):
                used |= keywords_used(sub)
    return used
