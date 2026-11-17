"""Typed, versioned hand-off messages between roles.

Design borrowed from Harness-Candy (``protocols.py``): a common envelope plus
role-specific payloads, and **a message that does not match its schema is
rejected before it is processed**. The goal is not "few malformed messages";
it is zero.

Roles
-----
isa   plans: objective -> steps with acceptance criteria
yev   dispatches: step -> assigned skill + tools
zev   evidence: what was read, where it came from, how trustworthy
xev   execution: what ran, with what bytes in and out
wev   verdict: pass/fail against explicit criteria
ely   meta: did the whole run actually satisfy the objective

Every protocol declares its version. Receivers advertise SUPPORTED versions and
refuse anything else, so an old producer cannot silently talk to a new consumer.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Callable

from .errors import AngelError

PROTOCOL_VERSION = "1.0"
SUPPORTED = frozenset({PROTOCOL_VERSION})

ROLES = ("isa", "yev", "zev", "xev", "wev", "ely")
SEVERITIES = ("low", "medium", "high", "critical")
VERDICTS = ("pass", "fail", "blocked")

#: which role may consume which protocol
CONSUMERS: dict[str, tuple[str, ...]] = {
    "isa-plan": ("yev", "ely"),
    "yev-dispatch": ("zev", "xev", "wev"),
    "zev-evidence": ("yev", "xev", "wev"),
    "xev-result": ("wev", "yev"),
    "wev-verdict": ("yev", "ely"),
    "ely-meta": ("isa",),
}


# --------------------------------------------------------------------------
# envelope
# --------------------------------------------------------------------------
@dataclass
class Envelope:
    # Every field defaults so subclasses can override any of them without
    # tripping dataclass ordering rules; presence is enforced in check().
    protocol: str = ""
    task_id: str = ""
    origin: str = ""
    target: str = ""
    version: str = PROTOCOL_VERSION
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ts: float = field(default_factory=time.time)
    parent: str | None = None

    def base(self) -> dict[str, Any]:
        data = {
            "protocol": self.protocol,
            "version": self.version,
            "task_id": self.task_id,
            "origin": self.origin,
            "target": self.target,
            "msg_id": self.msg_id,
            "ts": self.ts,
        }
        if self.parent:
            data["parent"] = self.parent
        return data

    def check(self) -> None:
        if self.protocol not in CONSUMERS:
            raise _code_error("E_PROTOCOL_UNKNOWN", f"unknown protocol {self.protocol!r}",
                              hint=f"known: {', '.join(sorted(CONSUMERS))}",
                              protocol=self.protocol)
        if self.version not in SUPPORTED:
            raise _code_error("E_PROTOCOL_VERSION", f"unsupported version {self.version!r}",
                              hint=f"supported: {', '.join(sorted(SUPPORTED))}",
                              protocol=self.protocol, version=self.version)
        if self.origin not in ROLES:
            raise _code_error("E_PROTOCOL_MALFORMED", f"unknown origin role {self.origin!r}",
                              hint=f"roles: {', '.join(ROLES)}", origin=self.origin)
        if self.target not in CONSUMERS[self.protocol]:
            raise _code_error("E_PROTOCOL_TARGET", f"{self.target!r} may not consume {self.protocol!r}",
                              hint=f"consumers: {', '.join(CONSUMERS[self.protocol])}",
                              protocol=self.protocol, target=self.target)
        if not self.task_id:
            raise _code_error("E_PROTOCOL_MALFORMED", "task_id is required")


_ERRORS: dict[str, type[AngelError]] = {}


def _code_error(code: str, message: str, *, hint: str = "", **context: Any) -> AngelError:
    """Build an AngelError carrying a specific taxonomy code (cached class)."""
    cls = _ERRORS.get(code)
    if cls is None:
        cls = type("Failure_" + code, (AngelError,), {"code": code})
        _ERRORS[code] = cls
    return cls(message, hint=hint, context=context)


# --------------------------------------------------------------------------
# payloads
# --------------------------------------------------------------------------
@dataclass
class Criterion:
    """An acceptance criterion that a machine or a person can check."""

    id: str
    statement: str
    kind: str = "check"          # check | test | command | review
    command: str | None = None
    expect: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {"id": self.id, "statement": self.statement, "kind": self.kind}
        if self.command:
            data["command"] = self.command
        if self.expect:
            data["expect"] = self.expect
        return data


@dataclass
class Plan(Envelope):
    protocol: str = "isa-plan"
    origin: str = "isa"
    target: str = "yev"
    objective: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    budget: dict[str, Any] = field(default_factory=dict)
    risks: list[str] = field(default_factory=list)

    def validate(self) -> None:
        self.check()
        if not self.objective.strip():
            raise _code_error("E_PROTOCOL_MALFORMED", "plan has no objective")
        if not self.steps:
            raise _code_error("E_PROTOCOL_MALFORMED", "plan has no steps")
        seen: set[str] = set()
        for step in self.steps:
            sid = str(step.get("id") or "")
            if not sid:
                raise _code_error("E_PROTOCOL_MALFORMED", "step without id", step=step)
            if sid in seen:
                raise _code_error("E_PROTOCOL_MALFORMED", f"duplicate step id {sid!r}")
            seen.add(sid)
            if not step.get("verb"):
                raise _code_error("E_PROTOCOL_MALFORMED", f"step {sid} has no verb", step=step)
            if not step.get("skills"):
                raise _code_error("E_PROTOCOL_MALFORMED", f"step {sid} is not bound to any skill", step=step)

    def to_dict(self) -> dict[str, Any]:
        data = self.base()
        data.update({
            "objective": self.objective,
            "steps": self.steps,
            "budget": self.budget,
            "risks": self.risks,
        })
        return data


@dataclass
class Dispatch(Envelope):
    protocol: str = "yev-dispatch"
    origin: str = "yev"
    target: str = "xev"
    step_id: str = ""
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    criteria: list[Criterion] = field(default_factory=list)

    def validate(self) -> None:
        self.check()
        if not self.skills:
            raise _code_error("E_PROTOCOL_MALFORMED", "dispatch must name at least one skill")
        if not self.criteria:
            raise _code_error("E_PROTOCOL_MALFORMED", "dispatch must carry acceptance criteria",
                              step=self.step_id)

    def to_dict(self) -> dict[str, Any]:
        data = self.base()
        data.update({
            "step_id": self.step_id,
            "skills": self.skills,
            "tools": self.tools,
            "inputs": self.inputs,
            "criteria": [c.to_dict() if isinstance(c, Criterion) else c for c in self.criteria],
        })
        return data


@dataclass
class Evidence(Envelope):
    protocol: str = "zev-evidence"
    origin: str = "zev"
    target: str = "wev"
    claims: list[dict[str, Any]] = field(default_factory=list)

    def validate(self) -> None:
        self.check()
        for claim in self.claims:
            if not claim.get("statement"):
                raise _code_error("E_PROTOCOL_MALFORMED", "evidence claim without statement", claim=claim)
            if not claim.get("source"):
                raise _code_error("E_PROTOCOL_MALFORMED",
                                  "evidence claim without source: unsourced claims are not evidence",
                                  claim=claim)

    def to_dict(self) -> dict[str, Any]:
        data = self.base()
        data["claims"] = self.claims
        return data


@dataclass
class Result(Envelope):
    protocol: str = "xev-result"
    origin: str = "xev"
    target: str = "wev"
    step_id: str = ""
    status: str = "ok"           # ok | error | partial
    outputs: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    error: dict[str, Any] | None = None

    def validate(self) -> None:
        self.check()
        if self.status not in ("ok", "error", "partial"):
            raise _code_error("E_PROTOCOL_MALFORMED", f"invalid status {self.status!r}")
        if self.status == "error" and not self.error:
            raise _code_error("E_PROTOCOL_MALFORMED", "error result without an error object")

    def to_dict(self) -> dict[str, Any]:
        data = self.base()
        data.update({
            "step_id": self.step_id,
            "status": self.status,
            "outputs": self.outputs,
            "artifacts": self.artifacts,
            "error": self.error,
        })
        return data


@dataclass
class Verdict(Envelope):
    protocol: str = "wev-verdict"
    origin: str = "wev"
    target: str = "yev"
    step_id: str = ""
    verdict: str = "fail"
    score: float = 0.0
    findings: list[dict[str, Any]] = field(default_factory=list)

    def validate(self) -> None:
        self.check()
        if self.verdict not in VERDICTS:
            raise _code_error("E_PROTOCOL_MALFORMED", f"invalid verdict {self.verdict!r}")
        if not 0.0 <= float(self.score) <= 1.0:
            raise _code_error("E_PROTOCOL_MALFORMED", "score must be within [0, 1]", score=self.score)
        for finding in self.findings:
            sev = finding.get("severity", "medium")
            if sev not in SEVERITIES:
                raise _code_error("E_PROTOCOL_MALFORMED", f"invalid severity {sev!r}", finding=finding)
        if self.verdict == "pass" and any(f.get("severity") in ("critical", "high") for f in self.findings):
            raise _code_error("E_PROTOCOL_MALFORMED",
                              "a pass verdict cannot carry high/critical findings")

    def penalty(self) -> float:
        """Severity-weighted penalty, same shape as the reference harness."""
        weights = {"low": 0.05, "medium": 0.20, "high": 0.50, "critical": 1.00}
        return sum(weights.get(f.get("severity", "medium"), 0.20) for f in self.findings)

    def to_dict(self) -> dict[str, Any]:
        data = self.base()
        data.update({
            "step_id": self.step_id,
            "verdict": self.verdict,
            "score": self.score,
            "findings": self.findings,
        })
        return data


@dataclass
class Meta(Envelope):
    protocol: str = "ely-meta"
    origin: str = "ely"
    target: str = "isa"
    objective_met: bool = False
    coverage: float = 0.0
    regressions: list[str] = field(default_factory=list)
    notes: str = ""

    def validate(self) -> None:
        self.check()
        if not 0.0 <= float(self.coverage) <= 1.0:
            raise _code_error("E_PROTOCOL_MALFORMED", "coverage must be within [0, 1]")

    def to_dict(self) -> dict[str, Any]:
        data = self.base()
        data.update({
            "objective_met": self.objective_met,
            "coverage": self.coverage,
            "regressions": self.regressions,
            "notes": self.notes,
        })
        return data


KINDS: dict[str, Callable[..., Envelope]] = {
    "isa-plan": Plan,
    "yev-dispatch": Dispatch,
    "zev-evidence": Evidence,
    "xev-result": Result,
    "wev-verdict": Verdict,
    "ely-meta": Meta,
}


# --------------------------------------------------------------------------
# factory + parser
# --------------------------------------------------------------------------
def make(kind: str, **fields: Any) -> Envelope:
    """Build a message, validate it, and return it. Raises on anything wrong."""
    cls = KINDS.get(kind)
    if cls is None:
        raise _code_error("E_PROTOCOL_UNKNOWN", f"unknown protocol {kind!r}",
                          hint=f"known: {', '.join(sorted(KINDS))}")
    envelope_fields = {k: fields.pop(k) for k in ("task_id", "origin", "target", "parent")
                       if k in fields}
    msg = cls(**envelope_fields, **fields)  # type: ignore[arg-type]
    msg.validate()
    return msg


def parse(data: dict[str, Any] | str) -> Envelope:
    """Parse an untrusted message. Anything malformed is rejected, not repaired."""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise _code_error("E_PROTOCOL_MALFORMED", f"not JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise _code_error("E_PROTOCOL_MALFORMED", "message must be a JSON object")
    kind = data.get("protocol")
    cls = KINDS.get(str(kind))
    if cls is None:
        raise _code_error("E_PROTOCOL_UNKNOWN", f"unknown protocol {kind!r}",
                          hint=f"known: {', '.join(sorted(KINDS))}")
    known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    extra = set(data) - known
    if extra:
        raise _code_error("E_PROTOCOL_MALFORMED", f"unknown fields: {sorted(extra)}")
    msg = cls(**data)  # type: ignore[arg-type]
    msg.validate()
    return msg


#: envelope fields that identify *an instance* of a message rather than what it
#: says. A digest that includes them cannot detect a replay, which is the whole
#: point of having one.
IDENTITY_FIELDS = ("msg_id", "ts", "parent")


def content(msg: Envelope) -> dict[str, Any]:
    """The message without its identity: what it claims, not who sent it when."""
    return {k: v for k, v in msg.to_dict().items() if k not in IDENTITY_FIELDS}


def digest(msg: Envelope) -> str:
    """Stable content hash used by the journal chain.

    Identity and timestamp are excluded on purpose: the same claim delivered twice
    must hash the same, otherwise a duplicate looks like new information.
    """
    payload = json.dumps(content(msg), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def label(msg: Envelope) -> str:
    """One line a human can read in a journal or a log."""
    detail = msg.to_dict()
    interesting = [f"{k}={detail[k]}" for k in ("step_id", "verdict", "status", "score",
                                               "objective", "score")
                   if detail.get(k) is not None]
    return (f"{msg.protocol}@{msg.version} {msg.origin}->{msg.target} "
            f"task={msg.task_id} " + " ".join(dict.fromkeys(interesting)))


#: known-good payload per protocol. `workflow protocol <kind> --sample` prints one,
#: and the tests parse all of them, so the documented shape cannot drift.
SAMPLES: dict[str, dict[str, Any]] = {
    "isa-plan": {
        "objective": "close the build failure with evidence",
        "steps": [
            {"id": "s1", "verb": "fix", "phase": "verify", "skills": ["build-fix"],
             "tools": ["error-digest"],
             "criteria": [{"id": "s1-c1", "statement": "the build command exits 0",
                           "kind": "command", "command": "npm run build"}]},
            {"id": "s2", "verb": "verify", "phase": "test", "skills": ["tdd-workflow"],
             "tools": ["coverage-gate"]},
        ],
        "budget": {"max_steps": 12, "max_tool_calls": 40, "max_seconds": 300},
        "risks": ["the suite may not cover the failing path"],
    },
    "yev-dispatch": {
        "task_id": "close-build-failure", "step_id": "s1",
        "skills": ["build-fix"], "tools": ["error-digest"],
        "inputs": {"command": "npm run build"},
        "criteria": [{"id": "s1-c1", "statement": "the build command exits 0",
                      "kind": "command", "command": "npm run build"}],
    },
    "zev-evidence": {
        "task_id": "close-build-failure", "origin": "zev", "target": "wev",
        "claims": [{"statement": "the error is a narrow type mismatch",
                    "source": "npm run build", "confidence": "confirmed"}],
    },
    "xev-result": {
        "task_id": "close-build-failure", "step_id": "s1", "status": "ok",
        "outputs": {"files_touched": 1}, "artifacts": ["src/app.ts"],
    },
    "wev-verdict": {
        "task_id": "close-build-failure", "step_id": "s1", "verdict": "pass",
        "score": 1.0,
        "findings": [{"severity": "low", "message": "the test is narrower than the bug"}],
    },
    "ely-meta": {
        "task_id": "close-build-failure", "objective_met": True, "coverage": 0.92,
        "regressions": [], "notes": "the guard is a regression eval, not a new test",
    },
}


def sample(kind: str) -> dict[str, Any]:
    """A full message for ``kind``: envelope, identity and a known-good payload."""
    cls = KINDS.get(kind)
    if cls is None:
        raise _code_error("E_PROTOCOL_UNKNOWN", f"unknown protocol {kind!r}",
                          hint=f"known: {', '.join(sorted(KINDS))}")
    payload = SAMPLES[kind]
    fields = {k: v for k, v in payload.items()
              if k not in ("task_id", "origin", "target", "parent")}
    return make(kind, task_id=payload.get("task_id", "sample-task"), **fields).to_dict()


def describe() -> list[dict[str, Any]]:
    """Machine-readable catalogue, used by `workflow protocol --list`."""
    out = []
    for kind, cls in KINDS.items():
        out.append({
            "protocol": kind,
            "version": PROTOCOL_VERSION,
            "dataclass": cls.__name__,
            "consumers": list(CONSUMERS[kind]),
            "fields": [f.name for f in cls.__dataclass_fields__.values()],  # type: ignore[attr-defined]
        })
    return out
