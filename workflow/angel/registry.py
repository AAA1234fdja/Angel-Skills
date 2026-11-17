"""Discovery and validation of the package.

The registry is the single source of truth: a skill that exists on disk but is
not registered is an error, and a registered skill without its folder is an
error. Nothing else in the runtime reads the filesystem directly.

A skill is a folder::

    skills/<category>/<id>/
        SKILL.md      procedure (required)
        skill.json    composition: tools, contracts, phases, triggers (required)
        tools/*.py    executable tools (optional)
        references/   long-form notes (optional)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import frontmatter
from .errors import AngelError, ManifestInvalid, RegistryError, SkillInvalid, SkillNotFound

REGISTRY = "categories.json"
STANDARD = "EXTENSION-STANDARD.md"
SKILL_FILE = "SKILL.md"
MANIFEST = "skill.json"

#: the lifecycle, top-down; `router.PHASE_ORDER` is the same tuple, and a test
#: asserts it, because two copies of an ordering is two orderings.
PHASES = ("plan", "design", "research", "implement", "test", "review", "verify",
          "ship", "debug", "audit", "document", "meta")
STATUSES = ("adopted", "original", "experimental")
RISK_LEVELS = ("read", "write", "execute", "destructive")
REQUIRED_SECTIONS = ("When to Use", "Procedure", "Exit Criteria")
ADVISED_SECTIONS = ("When Not to Use", "Common Failures")


def _err(code: str, message: str, *, hint: str = "", **context: Any) -> AngelError:
    cls = type("RegistryFailure_" + code, (AngelError,), {"code": code})
    return cls(message, hint=hint, context=context)


@dataclass
class ToolSpec:
    id: str
    entry: str
    description: str = ""
    risk: str = "read"
    input_schema: dict[str, Any] = field(default_factory=dict)
    timeout: float = 30.0
    sample: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "entry": self.entry, "description": self.description,
                "risk": self.risk, "timeout": self.timeout,
                "has_sample": bool(self.sample)}


@dataclass
class Skill:
    id: str
    category: str
    category_name: str
    path: Path
    frontmatter: dict[str, Any]
    body: str
    sections: dict[str, str]
    manifest: dict[str, Any]
    tools: list[ToolSpec] = field(default_factory=list)

    # -- convenient accessors ---------------------------------------------
    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description", ""))

    @property
    def phase(self) -> str:
        return str((self.frontmatter.get("metadata") or {}).get("phase", ""))

    @property
    def status(self) -> str:
        return str((self.frontmatter.get("metadata") or {}).get("status", ""))

    @property
    def origin(self) -> str:
        return str((self.frontmatter.get("metadata") or {}).get("origin", ""))

    @property
    def version(self) -> int:
        try:
            return int((self.frontmatter.get("metadata") or {}).get("version", 1))
        except (TypeError, ValueError):
            return 1

    @property
    def triggers(self) -> list[str]:
        return list(self.manifest.get("triggers") or [])

    @property
    def contracts(self) -> list[str]:
        return list(self.manifest.get("contracts") or [])

    @property
    def requires(self) -> list[str]:
        return list(self.manifest.get("requires") or [])

    @property
    def routing(self) -> dict[str, Any]:
        return dict(self.manifest.get("routing") or {})

    @property
    def max_risk(self) -> str:
        order = {level: i for i, level in enumerate(RISK_LEVELS)}
        if not self.tools:
            return "read"
        return max((t.risk for t in self.tools), key=lambda r: order.get(r, 0))

    def tool(self, tool_id: str) -> ToolSpec | None:
        return next((t for t in self.tools if t.id == tool_id), None)

    def to_dict(self, *, with_body: bool = False) -> dict[str, Any]:
        data = {
            "id": self.id,
            "category": self.category,
            "phase": self.phase,
            "status": self.status,
            "origin": self.origin,
            "version": self.version,
            "description": self.description,
            "triggers": self.triggers,
            "tools": [t.to_dict() for t in self.tools],
            "contracts": self.contracts,
            "requires": self.requires,
            "risk": self.max_risk,
            "path": str(self.path),
        }
        if with_body:
            data["body"] = self.body
            data["sections"] = self.sections
        return data


@dataclass
class Category:
    id: str
    name: str
    order: int
    status: str
    description: str
    gate: str | None
    rules: list[str]
    skill_ids: list[str]
    pending: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "order": self.order,
                "status": self.status, "description": self.description,
                "gate": self.gate, "rules": self.rules,
                "skills": self.skill_ids, "pending": self.pending}


class Registry:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.categories: list[Category] = []
        self.skills: dict[str, Skill] = {}
        self.meta: dict[str, Any] = {}

    # -- loading -----------------------------------------------------------
    def load(self) -> "Registry":
        file = self.root / REGISTRY
        if not file.is_file():
            raise _err("E_REGISTRY_MISSING", f"missing {REGISTRY} in {self.root}",
                       hint="pass --root pointing at the workflow package")
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise _err("E_REGISTRY_INVALID", f"{REGISTRY} is not JSON: {exc}") from exc
        if not isinstance(data.get("categories"), list):
            raise _err("E_REGISTRY_INVALID", "categories must be a list")

        self.meta = {k: v for k, v in data.items() if k != "categories"}
        for raw in data["categories"]:
            category = Category(
                id=str(raw.get("id", "")),
                name=str(raw.get("name", "")),
                order=int(raw.get("order", 0)),
                status=str(raw.get("status", "pending")),
                description=str(raw.get("description", "")),
                gate=raw.get("gate"),
                rules=list(raw.get("rules") or []),
                skill_ids=[str(s.get("id") if isinstance(s, dict) else s)
                           for s in raw.get("skills") or []],
                pending=list(raw.get("pending") or []),
            )
            self.categories.append(category)
            for skill_id in category.skill_ids:
                skill = self._read_skill(category, skill_id)
                if skill is not None:
                    self.skills[skill_id] = skill
        self.categories.sort(key=lambda c: (c.order, c.id))
        return self

    def _read_skill(self, category: Category, skill_id: str) -> Skill | None:
        folder = self.root / "skills" / category.id / skill_id
        skill_file = folder / SKILL_FILE
        if not skill_file.is_file():
            return None
        text = skill_file.read_text(encoding="utf-8")
        front, body, error = frontmatter.parse(text)
        if error:
            raise _err("E_SKILL_INVALID", f"{category.id}/{skill_id}: frontmatter {error}",
                       skill=f"{category.id}/{skill_id}")
        manifest: dict[str, Any] = {}
        manifest_file = folder / MANIFEST
        if manifest_file.is_file():
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise _err("E_MANIFEST_INVALID", f"{category.id}/{skill_id}: {MANIFEST} {exc}",
                           skill=f"{category.id}/{skill_id}") from exc
        tools = [ToolSpec(
            id=str(t.get("id", "")),
            entry=str(t.get("entry", "")),
            description=str(t.get("description", "")),
            risk=str(t.get("risk", "read")),
            input_schema=dict(t.get("input") or {}),
            timeout=float(t.get("timeout", 30)),
            sample=dict(t.get("sample") or {}),
        ) for t in manifest.get("tools") or []]
        return Skill(
            id=skill_id,
            category=category.id,
            category_name=category.name,
            path=folder,
            frontmatter=front,
            body=body,
            sections=frontmatter.sections(body),
            manifest=manifest,
            tools=tools,
        )

    # -- queries -----------------------------------------------------------
    def category(self, category_id: str) -> Category:
        for category in self.categories:
            if category.id == category_id:
                return category
        raise _err("E_REGISTRY_INVALID", f"unknown category {category_id!r}",
                   hint=", ".join(c.id for c in self.categories))

    def skill(self, skill_id: str) -> Skill:
        try:
            return self.skills[skill_id]
        except KeyError:
            raise SkillNotFound(f"unknown skill {skill_id!r}",
                                hint="run `workflow list`") from None

    def by_phase(self, phase: str) -> list[Skill]:
        return [s for s in self.skills.values() if s.phase == phase]

    def by_category(self, category_id: str) -> list[Skill]:
        return [s for s in self.skills.values() if s.category == category_id]

    def active(self) -> Iterable[Skill]:
        return (s for s in self.skills.values() if self.category(s.category).status == "activa")

    # -- validation --------------------------------------------------------
    def validate(self) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        seen: set[str] = set()

        if not (self.root / STANDARD).is_file():
            errors.append(f"missing {STANDARD}")

        for category in self.categories:
            if not category.id:
                errors.append("category without id")
            if category.status not in ("activa", "pendiente", "congelada"):
                errors.append(f"{category.id}: invalid status {category.status!r}")
            for skill_id in category.skill_ids:
                if skill_id in seen:
                    errors.append(f"duplicate skill id {skill_id!r}")
                seen.add(skill_id)
                if skill_id not in self.skills:
                    errors.append(f"{category.id}/{skill_id}: no {SKILL_FILE} on disk")

        for skill in self.skills.values():
            errors.extend(f"{skill.id}: {e}" for e in _validate_skill(skill, self.root))
            warnings.extend(f"{skill.id}: {w}" for w in _warn_skill(skill))

        on_disk = self._skills_on_disk()
        registered = {(s.category, s.id) for s in self.skills.values()}
        for category_id, skill_id in sorted(on_disk - registered):
            errors.append(f"{category_id}/{skill_id}: on disk but not registered")
        for category_id, skill_id in sorted(registered - on_disk):
            errors.append(f"{category_id}/{skill_id}: registered but missing on disk")

        warnings.extend(self._overlap_warnings())
        return {"errors": errors, "warnings": warnings, "skills": len(self.skills)}

    def _skills_on_disk(self) -> set[tuple[str, str]]:
        base = self.root / "skills"
        out: set[tuple[str, str]] = set()
        if not base.is_dir():
            return out
        for category_dir in base.iterdir():
            if not category_dir.is_dir():
                continue
            for skill_dir in category_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / SKILL_FILE).is_file():
                    out.add((category_dir.name, skill_dir.name))
        return out

    def _overlap_warnings(self) -> list[str]:
        out: list[str] = []
        buckets: dict[str, list[tuple[str, str]]] = {}
        for skill in self.skills.values():
            head = skill.description.lower()[:70]
            buckets.setdefault(head, []).append((skill.category, skill.id))
        for head, members in buckets.items():
            if len(members) > 1 and head.strip():
                names = ", ".join(f"{c}/{s}" for c, s in members)
                out.append(f"near-identical descriptions: {names}")
        return out


def _validate_skill(skill: Skill, root: Path) -> list[str]:
    errors: list[str] = []
    fm = skill.frontmatter
    if not fm.get("name"):
        errors.append("frontmatter missing name")
    elif fm["name"] != skill.id:
        errors.append(f"name {fm['name']!r} differs from folder id {skill.id!r}")
    if not fm.get("description"):
        errors.append("frontmatter missing description")
    else:
        desc = str(fm["description"])
        if not any(trigger in desc for trigger in ("Use when", "Usar cuando")):
            errors.append("description has no trigger ('Use when')")
        if len(desc) > 700:
            errors.append(f"description is {len(desc)} chars (max 700)")
    meta = fm.get("metadata") or {}
    for key in ("origin", "category", "phase", "status", "version"):
        if key not in meta:
            errors.append(f"metadata missing {key!r}")
    if meta.get("category") and meta["category"] != skill.category:
        errors.append(f"metadata.category {meta['category']!r} differs from folder")
    if meta.get("phase") and meta["phase"] not in PHASES:
        errors.append(f"invalid phase {meta['phase']!r}")
    if meta.get("status") and meta["status"] not in STATUSES:
        errors.append(f"invalid status {meta['status']!r}")

    for heading in REQUIRED_SECTIONS:
        if heading not in skill.sections:
            errors.append(f"missing section '## {heading}'")

    # manifest
    if not (skill.path / MANIFEST).is_file():
        errors.append(f"missing {MANIFEST}")
    else:
        for key in ("id", "category", "description"):
            if not skill.manifest.get(key):
                errors.append(f"{MANIFEST} missing {key!r}")
        if skill.manifest.get("id") and skill.manifest["id"] != skill.id:
            errors.append(f"{MANIFEST} id {skill.manifest['id']!r} differs from folder")
        for tool in skill.tools:
            if not tool.id:
                errors.append("tool without id")
            if tool.risk not in RISK_LEVELS:
                errors.append(f"tool {tool.id}: invalid risk {tool.risk!r}")
            entry = skill.path / tool.entry
            if not entry.is_file():
                errors.append(f"tool {tool.id}: entry {tool.entry!r} does not exist")
            elif not tool.sample:
                errors.append(f"tool {tool.id}: no sample payload, so it cannot be "
                              "self-tested and its denominator is unknown")
        if len({t.id for t in skill.tools}) != len(skill.tools):
            errors.append("duplicate tool ids")
        errors.extend(_validate_acceptance(skill))
    return errors


ACCEPTANCE_KINDS = ("tool", "command", "test", "review", "artifact")


def _validate_acceptance(skill: Skill) -> list[str]:
    """A skill's exit criteria are checkable or they are decoration.

    `acceptance` in `skill.json` is the machine-readable half of the
    `## Exit Criteria` section: each item says what proves the skill is done,
    and by which of five kinds of proof.
    """
    errors: list[str] = []
    criteria = skill.manifest.get("acceptance")
    if criteria is None:
        return errors
    if not isinstance(criteria, list) or not criteria:
        return ["acceptance must be a non-empty list when declared"]
    seen: set[str] = set()
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            errors.append(f"acceptance[{index}] must be an object")
            continue
        cid = str(criterion.get("id") or "")
        if not cid:
            errors.append(f"acceptance[{index}] has no id")
        elif cid in seen:
            errors.append(f"acceptance[{index}]: duplicate id {cid!r}")
        seen.add(cid)
        if not str(criterion.get("statement") or "").strip():
            errors.append(f"acceptance[{index}] has no statement")
        kind = criterion.get("kind")
        if kind not in ACCEPTANCE_KINDS:
            errors.append(f"acceptance[{index}] kind {kind!r} is not one of "
                          f"{', '.join(ACCEPTANCE_KINDS)}")
        if kind == "tool":
            ref = str(criterion.get("tool") or "")
            if ref not in {t.id for t in skill.tools}:
                errors.append(f"acceptance[{index}] names tool {ref!r}, which the "
                              "skill does not declare")
    return errors


def _warn_skill(skill: Skill) -> list[str]:
    warnings: list[str] = []
    for heading in ADVISED_SECTIONS:
        if heading not in skill.sections:
            warnings.append(f"no '## {heading}' section")
    lines = len(skill.body.splitlines())
    if lines > 260:
        warnings.append(f"body is {lines} lines: consider references/")
    if not skill.triggers:
        warnings.append(f"{MANIFEST} declares no triggers (routing will be weaker)")
    if skill.max_risk == "destructive":
        warnings.append("declares destructive tools: they need explicit confirmation")
    return warnings


def load(root: Path) -> Registry:
    return Registry(root).load()
