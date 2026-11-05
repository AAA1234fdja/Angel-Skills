"""Per-skill tools: discovery, authorisation, execution, capture.

A tool is a Python file inside ``skills/<category>/<id>/tools/`` that exposes
``run(payload: dict) -> dict``. It is executed **in this process** with a
restricted builtins set and a wall-clock timeout, and it must return a JSON
object. Anything else is a tool failure, not a crash.

Why in-process: the package has to run with no dependencies and no subprocess
overhead on Windows. The safety boundary here is *authorisation + risk level +
timeout + output capture*, not a container. A tool that needs real isolation
must shell out itself and say so in its manifest.

Authorisation is by risk level against a profile:

    read         always allowed
    write        allowed unless profile is ``observe``
    execute      allowed in ``standard`` and above
    destructive  only with ``allow_destructive`` (explicit user consent)
"""

from __future__ import annotations

import io
import json
import threading
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .errors import AngelError, ToolError
from .registry import RISK_LEVELS, Registry, Skill, ToolSpec

PROFILES: dict[str, set[str]] = {
    "observe": {"read"},
    "standard": {"read", "write", "execute"},
    "full": {"read", "write", "execute", "destructive"},
}

#: builtins a tool may use. Everything else (eval, exec, open, __import__ of
#: arbitrary modules) is removed before the tool runs.
SAFE_BUILTINS = {
    "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float", "format",
    "frozenset", "int", "isinstance", "issubclass", "iter", "len", "list", "map",
    "max", "min", "next", "object", "print", "range", "repr", "reversed", "round",
    "set", "slice", "sorted", "str", "sum", "tuple", "type", "zip", "True",
    "False", "None", "Exception", "ValueError", "TypeError", "KeyError",
    "IndexError", "StopIteration", "ArithmeticError", "ZeroDivisionError",
    "NotImplementedError", "RuntimeError", "AttributeError", "LookupError",
    "callable", "divmod", "hex", "oct", "ord", "chr", "pow", "hash", "id", "vars",
}


def _err(code: str, message: str, *, hint: str = "", **context: Any) -> AngelError:
    cls = type("ToolFailure_" + code, (AngelError,), {"code": code})
    return cls(message, hint=hint, context=context)


#: modules a tool may import. Pure computation only: no filesystem, no network,
#: no subprocess, no introspection into the runtime that is executing it.
SAFE_MODULES = {
    "re", "math", "json", "hashlib", "collections", "itertools", "statistics",
    "textwrap", "difflib", "string", "unicodedata", "base64", "binascii",
    "functools", "decimal", "fractions", "heapq", "bisect", "datetime", "typing",
}


def _safe_import(name: str, globals: Any = None, locals: Any = None,  # noqa: A002
                 fromlist: Any = (), level: int = 0) -> Any:
    """A whitelist ``__import__``: a tool may import pure computation only."""
    root = str(name).split(".")[0]
    if root not in SAFE_MODULES:
        raise ImportError(
            f"module {name!r} is not available to tools; "
            f"allowed: {', '.join(sorted(SAFE_MODULES))}")
    import importlib

    return importlib.import_module(name)


def _safe_builtins() -> dict[str, Any]:
    """The builtins dict handed to tool modules: an explicit allow-list."""
    import builtins as _builtins

    table = {name: getattr(_builtins, name) for name in SAFE_BUILTINS if hasattr(_builtins, name)}
    table["__import__"] = _safe_import
    table["__build_class__"] = _builtins.__build_class__
    table["__name__"] = "angel_tool"
    return table


@dataclass
class ToolCall:
    skill_id: str
    tool_id: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    skill_id: str
    tool_id: str
    ok: bool
    output: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    stdout: str = ""
    stderr: str = ""
    ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill_id,
            "tool": self.tool_id,
            "ok": self.ok,
            "output": self.output,
            "error": self.error,
            "stdout": self.stdout[-4000:],
            "stderr": self.stderr[-4000:],
            "ms": round(self.ms, 2),
        }


class ToolBox:
    """Loads, authorises and runs the tools of one package."""

    def __init__(self, registry: Registry, *, profile: str = "standard",
                 allow_destructive: bool = False) -> None:
        self.registry = registry
        if profile not in PROFILES:
            raise _err("E_TOOL_NOT_AUTHORISED", f"unknown profile {profile!r}",
                       hint=", ".join(PROFILES))
        self.profile = profile
        self.allow_destructive = allow_destructive
        self.allowed_risks = set(PROFILES[profile])
        if allow_destructive:
            self.allowed_risks.add("destructive")
        self._cache: dict[tuple[str, str], Callable[..., Any]] = {}

    # -- discovery ---------------------------------------------------------
    def sample_for(self, skill_id: str, tool_id: str) -> dict[str, Any]:
        """The declared sample payload for a tool, or an empty payload."""
        _, spec = self.resolve(skill_id, tool_id)
        return dict(spec.sample)

    def catalog(self) -> list[dict[str, Any]]:
        out = []
        for skill in self.registry.skills.values():
            for tool in skill.tools:
                out.append({
                    "skill": skill.id,
                    "category": skill.category,
                    "id": tool.id,
                    "risk": tool.risk,
                    "description": tool.description,
                    "authorised": self.is_authorised(tool),
                    "timeout": tool.timeout,
                    "has_sample": bool(tool.sample),
                })
        return sorted(out, key=lambda row: (row["skill"], row["id"]))

    def is_authorised(self, tool: ToolSpec) -> bool:
        return tool.risk in self.allowed_risks

    def resolve(self, skill_id: str, tool_id: str) -> tuple[Skill, ToolSpec]:
        skill = self.registry.skill(skill_id)
        spec = skill.tool(tool_id)
        if spec is None:
            raise _err("E_TOOL_UNKNOWN", f"{skill_id} has no tool {tool_id!r}",
                       hint=", ".join(t.id for t in skill.tools) or "no tools",
                       skill=skill_id, tool=tool_id)
        return skill, spec

    # -- loading -----------------------------------------------------------
    def _load(self, skill: Skill, spec: ToolSpec) -> Callable[..., Any]:
        key = (skill.id, spec.id)
        if key in self._cache:
            return self._cache[key]
        entry = (skill.path / spec.entry).resolve()
        if not entry.is_file():
            raise _err("E_TOOL_UNKNOWN", f"{skill.id}/{spec.id}: missing {spec.entry}",
                       skill=skill.id)
        source = entry.read_text(encoding="utf-8")
        safe = _safe_builtins()
        namespace: dict[str, Any] = {
            "__name__": f"angel_tool_{skill.id}_{spec.id}",
            "__file__": str(entry),
            "__builtins__": safe,
            "__package__": None,
        }
        try:
            exec(compile(source, str(entry), "exec"), namespace)  # noqa: S102 - sandboxed builtins
        except Exception as exc:  # noqa: BLE001 - boundary
            raise _err("E_TOOL_FAILED", f"{skill.id}/{spec.id}: failed to load: {exc}",
                       hint="the tool module must import cleanly with only safe builtins",
                       skill=skill.id, tool=spec.id) from exc
        fn = namespace.get("run")
        if not callable(fn):
            raise _err("E_TOOL_FAILED", f"{skill.id}/{spec.id}: no run(payload) in {spec.entry}",
                       skill=skill.id, tool=spec.id)
        self._cache[key] = fn
        return fn

    # -- execution ---------------------------------------------------------
    def run(self, skill_id: str, tool_id: str, payload: dict[str, Any] | None = None) -> ToolResult:
        skill, spec = self.resolve(skill_id, tool_id)
        if not self.is_authorised(spec):
            raise _err("E_TOOL_NOT_AUTHORISED",
                       f"{skill_id}/{tool_id} needs risk '{spec.risk}', profile is '{self.profile}'",
                       hint="raise --profile or pass --allow-destructive for destructive tools",
                       skill=skill_id, tool=tool_id, risk=spec.risk)
        fn = self._load(skill, spec)
        payload = dict(payload or {})
        self._check_input(spec, payload)

        out_buf, err_buf = io.StringIO(), io.StringIO()
        started = time.time()
        box: dict[str, Any] = {}

        def target() -> None:
            try:
                with redirect_stdout(out_buf), redirect_stderr(err_buf):
                    box["result"] = fn(payload)
            except BaseException as exc:  # noqa: BLE001 - captured, not swallowed
                box["error"] = exc
                box["traceback"] = traceback.format_exc(limit=6)

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=spec.timeout)
        elapsed = (time.time() - started) * 1000

        if thread.is_alive():
            return ToolResult(
                skill_id, tool_id, ok=False, stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
                error=_err("E_TOOL_TIMEOUT",
                           f"{skill_id}/{tool_id} exceeded {spec.timeout}s",
                           hint="raise the tool's timeout in skill.json or bound the work",
                           skill=skill_id, tool=tool_id).to_dict(),
                ms=elapsed,
            )

        if "error" in box:
            exc = box["error"]
            return ToolResult(
                skill_id, tool_id, ok=False, stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
                error=_err("E_TOOL_FAILED", f"{type(exc).__name__}: {exc}",
                           hint="see context.traceback",
                           skill=skill_id, tool=tool_id,
                           traceback=box.get("traceback", "")).to_dict(),
                ms=elapsed,
            )

        result = box.get("result")
        if not isinstance(result, dict):
            return ToolResult(
                skill_id, tool_id, ok=False, stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
                error=_err("E_TOOL_FAILED",
                           f"{skill_id}/{tool_id} must return a dict, got {type(result).__name__}",
                           hint="tools return JSON-serialisable dicts",
                           skill=skill_id, tool=tool_id).to_dict(),
                ms=elapsed,
            )
        try:
            json.dumps(result)
        except (TypeError, ValueError) as exc:
            return ToolResult(
                skill_id, tool_id, ok=False, stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
                error=_err("E_TOOL_FAILED", f"{skill_id}/{tool_id} returned non-JSON: {exc}",
                           skill=skill_id, tool=tool_id).to_dict(),
                ms=elapsed,
            )
        return ToolResult(skill_id, tool_id, ok=True, output=result,
                          stdout=out_buf.getvalue(), stderr=err_buf.getvalue(), ms=elapsed)

    def _check_input(self, spec: ToolSpec, payload: dict[str, Any]) -> None:
        from . import jsonschema

        if not spec.input_schema:
            return
        try:
            jsonschema.validate(payload, spec.input_schema)
        except jsonschema.SchemaError as exc:
            raise _err("E_TOOL_INPUT", f"{spec.id}: {exc}",
                       hint="check the tool's input schema in skill.json",
                       tool=spec.id) from exc
        except jsonschema.UnsupportedSchema:
            # a manifest with an exotic schema degrades to "no validation" but
            # is reported by `workflow validate`, never silently ignored here
            return


def risk_allowed(risk: str, profile: str, *, allow_destructive: bool = False) -> bool:
    allowed = set(PROFILES.get(profile, {"read"}))
    if allow_destructive:
        allowed.add("destructive")
    return risk in allowed


def describe_risks() -> list[dict[str, Any]]:
    return [{"risk": level, "profiles": [p for p, risks in PROFILES.items() if level in risks]}
            for level in RISK_LEVELS]
