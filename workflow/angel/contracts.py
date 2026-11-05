"""Contracts: the machine-checkable promises skills make to each other.

A *contract* is a JSON-schema plus a version and a list of consumers. It is the
only legal way for one skill to hand structured data to another, which is what
keeps "protocols" from decaying into conventions.

Layout::

    workflow/contracts/<name>/<version>.schema.json
    workflow/contracts/<name>/CHANGELOG.md     (optional, human notes)

Rules enforced here
-------------------
1. A contract version is immutable. Changing the file means a new version file.
2. Adding an optional property, or widening an enum, is ``minor``.
3. Removing a property, adding a required one, changing a type or narrowing an
   enum is ``major`` and needs a new ``<major+1>.0.0`` file.
4. Data validated against a contract that declares a ``format`` we do not know
   is reported as a warning, never silently accepted as valid.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import jsonschema
from .errors import AngelError, ContractError

CONTRACTS_DIR = "contracts"
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.schema\.json$")


def _err(code: str, message: str, *, hint: str = "", **context: Any) -> AngelError:
    cls = type("ContractFailure_" + code, (AngelError,), {"code": code})
    return cls(message, hint=hint, context=context)


@dataclass
class Contract:
    name: str
    version: str
    schema: dict[str, Any]
    path: Path
    consumers: list[str] = field(default_factory=list)

    @property
    def major(self) -> int:
        return int(self.version.split(".")[0])

    def validate(self, payload: Any) -> None:
        try:
            jsonschema.validate(payload, self.schema)
        except jsonschema.SchemaError as exc:
            raise _err("E_CONTRACT_INVALID", f"{self.name}@{self.version} {exc}",
                       hint="the payload does not satisfy the contract schema",
                       contract=self.name, version=self.version) from exc
        except jsonschema.UnsupportedSchema as exc:
            raise _err("E_SCHEMA_UNSUPPORTED",
                       f"{self.name}@{self.version}: {exc}",
                       hint="add the keyword to angel/jsonschema.py or simplify the contract",
                       contract=self.name) from exc

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "version": self.version,
                "consumers": self.consumers, "path": str(self.path)}


def contracts_root(root: Path) -> Path:
    return Path(root) / CONTRACTS_DIR


def discover(root: Path) -> dict[str, list[Contract]]:
    """Every contract in the package, grouped by name and sorted by version."""
    base = contracts_root(root)
    out: dict[str, list[Contract]] = {}
    if not base.is_dir():
        return out
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        versions: list[Contract] = []
        for file in sorted(folder.iterdir()):
            match = VERSION_RE.match(file.name)
            if not match:
                continue
            schema = json.loads(file.read_text(encoding="utf-8"))
            problems = jsonschema.check_schema(schema)
            if problems:
                raise _err("E_SCHEMA_UNSUPPORTED", f"{folder.name}/{file.name}: {problems[0]}",
                           contract=folder.name)
            consumers = schema.get("x-consumers") or []
            versions.append(Contract(folder.name, ".".join(match.groups()), schema, file,
                                     list(consumers)))
        if versions:
            versions.sort(key=lambda c: tuple(int(x) for x in c.version.split(".")))
            out[folder.name] = versions
    return out


def latest(root: Path, name: str) -> Contract:
    found = discover(root).get(name)
    if not found:
        raise _err("E_CONTRACT_INVALID", f"unknown contract {name!r}",
                   hint="run `workflow contract --list`")
    return found[-1]


def resolve(root: Path, name: str, version: str | None = None) -> Contract:
    found = discover(root).get(name)
    if not found:
        raise _err("E_CONTRACT_INVALID", f"unknown contract {name!r}")
    if version is None:
        return found[-1]
    for contract in found:
        if contract.version == version:
            return contract
    majors = sorted({c.version for c in found})
    raise _err("E_CONTRACT_INVALID", f"{name}@{version} does not exist",
               hint=f"available: {', '.join(majors)}", contract=name)


def compatible(root: Path, name: str, producer_version: str) -> bool:
    """A consumer pinned to a major version accepts any same-major producer."""
    try:
        contract = resolve(root, name, producer_version)
    except AngelError:
        return False
    return contract.major == latest(root, name).major


def diff_versions(root: Path, name: str, old: str, new: str) -> dict[str, Any]:
    found = {c.version: c for c in discover(root).get(name, [])}
    for version in (old, new):
        if version not in found:
            raise _err("E_CONTRACT_INVALID", f"{name}@{version} does not exist")
    changes = jsonschema.diff(found[old].schema, found[new].schema)
    kind = jsonschema.classify(changes)
    declared = _bump(old, found[new].version)
    return {
        "contract": name,
        "from": old,
        "to": new,
        "changes": changes,
        "required_bump": kind,
        "declared_bump": declared,
        "ok": kind == declared or (kind == "patch" and declared in ("patch", "minor")),
    }


def _bump(old: str, new: str) -> str:
    a = [int(x) for x in old.split(".")]
    b = [int(x) for x in new.split(".")]
    if b[0] != a[0]:
        return "major"
    if b[1] != a[1]:
        return "minor"
    return "patch"


def validate_all(root: Path) -> list[dict[str, Any]]:
    """Check every contract is loadable and its versions form a sane history."""
    report: list[dict[str, Any]] = []
    for name, versions in discover(root).items():
        majors = [c.major for c in versions]
        if majors != sorted(majors):
            report.append({"contract": name, "ok": False, "reason": "versions out of order"})
            continue
        for older, newer in zip(versions, versions[1:]):
            result = diff_versions(root, name, older.version, newer.version)
            if not result["ok"]:
                report.append({
                    "contract": name,
                    "ok": False,
                    "reason": (f"{older.version} -> {newer.version} needs a {result['required_bump']} "
                               f"bump but declares {result['declared_bump']}"),
                    "changes": result["changes"],
                })
        report.append({"contract": name, "ok": True, "versions": [c.version for c in versions]})
    return report


def write_contract(root: Path, name: str, version: str, schema: dict[str, Any]) -> Path:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise _err("E_CONTRACT_INVALID", f"version must be x.y.z, got {version!r}")
    folder = contracts_root(root) / name
    folder.mkdir(parents=True, exist_ok=True)
    problems = jsonschema.check_schema(schema)
    if problems:
        raise _err("E_SCHEMA_UNSUPPORTED", f"{name}@{version}: {problems[0]}",
                   hint="add the keyword to angel/jsonschema.py or simplify the contract",
                   contract=name, version=version)
    path = folder / f"{version}.schema.json"
    if path.exists():
        raise _err("E_CONTRACT_INVALID", f"{name}@{version} already exists",
                   hint="contract versions are immutable: write a new version")
    path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
