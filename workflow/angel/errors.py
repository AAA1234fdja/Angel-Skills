"""The single error taxonomy and the single error policy.

Every failure in the runtime is an ``AngelError`` with a stable ``code``.
Nothing raises bare exceptions across a boundary: the code is what callers,
the journal and the CLI branch on.

Policy is data, not code: each code maps to how severe it is, whether the
operation may be retried, and which layer owns the fix.
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Iterable

# --------------------------------------------------------------------------
# taxonomy
# --------------------------------------------------------------------------
# severity      how bad it is for the user's goal
# retryable     safe to repeat the same operation unchanged
# owner         which layer must fix it
# exit          process exit code when it reaches the CLI
POLICY: dict[str, dict[str, Any]] = {
    # discovery / registry
    "E_PACKAGE_MISSING": {"severity": "fatal", "retryable": False, "owner": "user", "exit": 3},
    "E_REGISTRY_INVALID": {"severity": "fatal", "retryable": False, "owner": "author", "exit": 2},
    "E_REGISTRY_MISSING": {"severity": "fatal", "retryable": False, "owner": "author", "exit": 3},
    "E_SKILL_NOT_FOUND": {"severity": "error", "retryable": False, "owner": "user", "exit": 4},
    "E_SKILL_INVALID": {"severity": "error", "retryable": False, "owner": "author", "exit": 2},
    "E_SKILL_DUPLICATE": {"severity": "error", "retryable": False, "owner": "author", "exit": 2},
    "E_MANIFEST_INVALID": {"severity": "error", "retryable": False, "owner": "author", "exit": 2},
    # protocols
    "E_PROTOCOL_UNKNOWN": {"severity": "error", "retryable": False, "owner": "author", "exit": 5},
    "E_PROTOCOL_VERSION": {"severity": "error", "retryable": False, "owner": "author", "exit": 5},
    "E_PROTOCOL_MALFORMED": {"severity": "error", "retryable": False, "owner": "producer", "exit": 5},
    "E_PROTOCOL_TARGET": {"severity": "error", "retryable": False, "owner": "producer", "exit": 5},
    # contracts
    "E_CONTRACT_INVALID": {"severity": "error", "retryable": False, "owner": "author", "exit": 6},
    "E_CONTRACT_BREAKING": {"severity": "error", "retryable": False, "owner": "producer", "exit": 6},
    "E_SCHEMA_UNSUPPORTED": {"severity": "error", "retryable": False, "owner": "author", "exit": 2},
    # tools
    "E_TOOL_UNKNOWN": {"severity": "error", "retryable": False, "owner": "author", "exit": 7},
    "E_TOOL_NOT_AUTHORISED": {"severity": "error", "retryable": False, "owner": "caller", "exit": 7},
    "E_TOOL_INPUT": {"severity": "error", "retryable": False, "owner": "caller", "exit": 7},
    "E_TOOL_TIMEOUT": {"severity": "error", "retryable": True, "owner": "runtime", "exit": 7},
    "E_TOOL_FAILED": {"severity": "error", "retryable": False, "owner": "tool", "exit": 7},
    "E_TOOL_DESTRUCTIVE": {"severity": "error", "retryable": False, "owner": "user", "exit": 8},
    # routing / running
    "E_ROUTE_EMPTY": {"severity": "warn", "retryable": False, "owner": "user", "exit": 4},
    "E_BUDGET_EXCEEDED": {"severity": "fatal", "retryable": False, "owner": "user", "exit": 9},
    "E_GATE_FAILED": {"severity": "error", "retryable": False, "owner": "producer", "exit": 10},
    "E_STEP_FAILED": {"severity": "error", "retryable": False, "owner": "runtime", "exit": 10},
    "E_JOURNAL_CORRUPT": {"severity": "fatal", "retryable": False, "owner": "runtime", "exit": 11},
    # meta
    "E_INTERNAL": {"severity": "fatal", "retryable": False, "owner": "runtime", "exit": 1},
}

SEVERITIES = ("info", "warn", "error", "fatal")


class AngelError(Exception):
    """Base failure: always carries a stable code and a policy."""

    code = "E_INTERNAL"

    def __init__(self, message: str, *, hint: str = "", context: dict[str, Any] | None = None,
                 cause: BaseException | None = None, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            # the policy is the source of truth; a code that is not declared there
            # is a bug in the caller, not a variant spelling.
            if code not in POLICY:
                raise KeyError(f"undeclared error code {code!r}: add it to POLICY first")
            self.code = code
        self.message = str(message)
        self.hint = hint
        self.context = context or {}
        self.cause = cause

    # -- policy ------------------------------------------------------------
    @property
    def policy(self) -> dict[str, Any]:
        return POLICY.get(self.code, POLICY["E_INTERNAL"])

    @property
    def severity(self) -> str:
        return self.policy["severity"]

    @property
    def retryable(self) -> bool:
        return bool(self.policy["retryable"])

    @property
    def owner(self) -> str:
        return str(self.policy["owner"])

    @property
    def exit_code(self) -> int:
        return int(self.policy["exit"])

    # -- recovery ----------------------------------------------------------
    def recovery(self) -> dict[str, Any]:
        """The recovery contract: cause hint, safe retry, stop condition.

        Every error path in this runtime answers the three questions an agent
        needs to keep going without guessing.
        """
        return {
            "root_cause_hint": self.hint or _default_hint(self.code),
            "safe_retry": self.retryable,
            "retry_instruction": ("repeat the same operation once; if it fails again treat it as fatal"
                                  if self.retryable else "do not retry unchanged; fix the cause first"),
            "stop_condition": ("stop after 1 retry" if self.retryable else "stop immediately"),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "owner": self.owner,
            "retryable": self.retryable,
            "exit": self.exit_code,
            "context": self.context,
            "recovery": self.recovery(),
        }

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code}: {self.message}"


_DEFAULT_HINTS = {
    "E_REGISTRY_INVALID": "run `workflow validate` and fix the first reported error",
    "E_REGISTRY_MISSING": "create workflow/categories.json or run with WORKFLOW_ROOT pointing at the package",
    "E_SKILL_NOT_FOUND": "run `workflow list` to see the ids that exist",
    "E_SKILL_INVALID": "read EXTENSION-STANDARD.md section 7 and fix the checklist",
    "E_MANIFEST_INVALID": "skill.json must declare id, category and description (see the standard)",
    "E_PROTOCOL_MALFORMED": "build messages with angel.protocols.make() instead of hand-written dicts",
    "E_PROTOCOL_VERSION": "the receiver only accepts the versions it declares in SUPPORTED",
    "E_PROTOCOL_TARGET": "check the envelope destino against the role that consumes it",
    "E_CONTRACT_BREAKING": "a breaking change needs a major bump in the contract version",
    "E_TOOL_UNKNOWN": "the skill manifest did not declare that tool id",
    "E_TOOL_NOT_AUTHORISED": "tools run only for profiles that allow their risk level",
    "E_TOOL_INPUT": "check the tool's input schema in skill.json",
    "E_TOOL_DESTRUCTIVE": "destructive tools require --allow-destructive or an explicit confirmation",
    "E_BUDGET_EXCEEDED": "raise --budget or split the objective into smaller steps",
    "E_GATE_FAILED": "the step output did not satisfy its acceptance criteria",
    "E_JOURNAL_CORRUPT": "the hash chain broke: a journal line was edited outside the runtime",
}


def _default_hint(code: str) -> str:
    return _DEFAULT_HINTS.get(code, "inspect the context and the journal entry for this code")


# --------------------------------------------------------------------------
# concrete errors
# --------------------------------------------------------------------------
class RegistryError(AngelError):
    pass


class SkillNotFound(AngelError):
    code = "E_SKILL_NOT_FOUND"


class SkillInvalid(AngelError):
    code = "E_SKILL_INVALID"


class ManifestInvalid(AngelError):
    code = "E_MANIFEST_INVALID"


class ProtocolError(AngelError):
    code = "E_PROTOCOL_MALFORMED"


class ContractError(AngelError):
    code = "E_CONTRACT_INVALID"


class ToolError(AngelError):
    code = "E_TOOL_FAILED"


class BudgetExceeded(AngelError):
    code = "E_BUDGET_EXCEEDED"


class GateFailed(AngelError):
    code = "E_GATE_FAILED"


class JournalCorrupt(AngelError):
    code = "E_JOURNAL_CORRUPT"


# --------------------------------------------------------------------------
# guard helper: turn any exception into a taxonomy failure
# --------------------------------------------------------------------------
def guard(fn, *args, code: str = "E_INTERNAL", **kwargs):
    """Call ``fn`` and re-raise anything as an AngelError with ``code``."""
    try:
        return fn(*args, **kwargs)
    except AngelError:
        raise
    except Exception as exc:  # noqa: BLE001 - boundary
        raise AngelError(
            f"{type(exc).__name__}: {exc}",
            hint="unexpected failure; see context.traceback",
            context={"traceback": traceback.format_exc(limit=4)},
            cause=exc,
        ) from exc


def worst(errors: Iterable[AngelError]) -> str:
    """Highest severity among errors, as a policy decision."""
    order = {"info": 0, "warn": 1, "error": 2, "fatal": 3}
    result = "info"
    for err in errors:
        if order.get(err.severity, 0) > order.get(result, 0):
            result = err.severity
    return result


def as_json(err: AngelError) -> str:
    return json.dumps(err.to_dict(), ensure_ascii=False, indent=2)
