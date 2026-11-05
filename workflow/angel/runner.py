"""Execute a routed plan with budget, gates, authorisation and a journal.

The runner is the only place that *does* things. It never decides what to do:
the router (or an explicit plan) decides, and the runner enforces the rules —
which is the separation that makes the whole thing auditable.

A run produces, in order:
    run.start -> plan -> (dispatch, tool.call, tool.result, result, verdict)*
              -> gate -> run.end

Every hand-off between those stages is a typed protocol message, and a message
that fails its schema stops the run instead of degrading silently.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import protocols
from .errors import AngelError, BudgetExceeded, GateFailed
from .journal import Journal, open_journal
from .registry import Registry
from .router import Route, route
from .tools import ToolBox, ToolResult


def _criterion(raw: Any, step_id: str) -> protocols.Criterion:
    """Build a Criterion from loose manifest data without trusting its shape."""
    if isinstance(raw, protocols.Criterion):
        return raw
    if isinstance(raw, str):
        return protocols.Criterion(id=f"{step_id}-c", statement=raw)
    data = dict(raw or {})
    return protocols.Criterion(
        id=str(data.get("id") or f"{step_id}-c"),
        statement=str(data.get("statement") or data.get("text") or "step exit criteria met"),
        kind=str(data.get("kind") or "review"),
        command=data.get("command"),
        expect=data.get("expect"),
    )


@dataclass
class Budget:
    steps: int = 12
    tool_calls: int = 40
    seconds: float = 300.0
    spent_steps: int = 0
    spent_tools: int = 0
    started: float = field(default_factory=time.time)

    def spend_step(self) -> None:
        self.spent_steps += 1
        if self.spent_steps > self.steps:
            raise BudgetExceeded(f"step budget exhausted ({self.steps})",
                                 hint="raise --budget-steps or split the objective")

    def spend_tool(self) -> None:
        self.spent_tools += 1
        if self.spent_tools > self.tool_calls:
            raise BudgetExceeded(f"tool budget exhausted ({self.tool_calls})",
                                 hint="raise --budget-tools or reduce tool use")
        if time.time() - self.started > self.seconds:
            raise BudgetExceeded(f"time budget exhausted ({self.seconds}s)",
                                 hint="raise --budget-seconds")

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": {"limit": self.steps, "used": self.spent_steps},
            "tools": {"limit": self.tool_calls, "used": self.spent_tools},
            "seconds": {"limit": self.seconds,
                        "used": round(time.time() - self.started, 1)},
        }


@dataclass
class StepOutcome:
    step_id: str
    skill: str
    status: str = "ok"
    tools: list[dict[str, Any]] = field(default_factory=list)
    verdict: dict[str, Any] | None = None
    findings: list[dict[str, Any]] = field(default_factory=list)
    score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {"step": self.step_id, "skill": self.skill, "status": self.status,
                "tools": self.tools, "verdict": self.verdict,
                "findings": self.findings, "score": round(self.score, 3)}


@dataclass
class RunReport:
    run_id: str
    objective: str
    steps: list[StepOutcome]
    budget: dict[str, Any]
    verdict: str
    score: float
    journal: str
    errors: list[dict[str, Any]] = field(default_factory=list)
    started: float = field(default_factory=time.time)

    @property
    def ok(self) -> bool:
        return self.verdict == "pass" and not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "objective": self.objective,
            "verdict": self.verdict,
            "score": round(self.score, 3),
            "steps": [s.to_dict() for s in self.steps],
            "budget": self.budget,
            "journal": self.journal,
            "errors": self.errors,
            "seconds": round(time.time() - self.started, 2),
        }


GATE_ACTIONS = ("pass", "fail", "blocked")


class Runner:
    def __init__(self, registry: Registry, *, root: Path | None = None,
                 profile: str = "standard", allow_destructive: bool = False,
                 budget: Budget | None = None) -> None:
        self.registry = registry
        self.root = Path(root) if root else registry.root
        self.box = ToolBox(registry, profile=profile, allow_destructive=allow_destructive)
        self.budget = budget or Budget()

    # -- journal helpers ---------------------------------------------------
    def _journal(self, run_id: str) -> Journal:
        return open_journal(self.root, run_id)

    # -- planning ----------------------------------------------------------
    def plan(self, objective: str, *, limit: int = 5, phase: str | None = None,
             category: str | None = None) -> tuple[Route, protocols.Plan]:
        routed = route(self.registry, objective, limit=limit, phase=phase, category=category)
        if not routed.matches:
            raise AngelError("no skill matched the objective",
                             hint="run `workflow route --need ... --min-score 0` to see near misses")
        steps = []
        for step in routed.steps:
            steps.append({
                "id": step["id"],
                "verb": step["verb"],
                "skills": [step["skill"]],
                "tools": step["tools"],
                "criteria": step["criteria"] or [{
                    "id": f"{step['id']}-exit",
                    "statement": f"{step['skill']} reached its exit criteria",
                    "kind": "review",
                }],
            })
        message = protocols.make(
            "isa-plan",
            task_id=objective[:48],
            objective=objective,
            steps=steps,
            budget=self.budget.to_dict(),
            risks=[],
        )
        return routed, message

    # -- execution ---------------------------------------------------------
    def run(self, objective: str, *, tools: bool = True, limit: int = 5,
            phase: str | None = None, category: str | None = None,
            dry_run: bool = False, continue_on_error: bool = False) -> RunReport:
        run_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
        journal = self._journal(run_id)
        journal.append("run.start", {"objective": objective, "profile": self.box.profile,
                                     "dry_run": dry_run})

        routed, plan = self.plan(objective, limit=limit, phase=phase, category=category)
        journal.append("plan", plan.to_dict())

        outcomes: list[StepOutcome] = []
        errors: list[dict[str, Any]] = []

        try:
            for step in plan.steps:
                self.budget.spend_step()
                outcome, step_errors = self._run_step(run_id, journal, step, tools=tools,
                                                      dry_run=dry_run)
                outcomes.append(outcome)
                errors.extend(step_errors)
                if step_errors and not continue_on_error:
                    break
        except AngelError as exc:
            errors.append(exc.to_dict())
            journal.append("error", exc.to_dict())

        verdict, score = self._gate(outcomes, errors)
        journal.append("run.end", {"verdict": verdict, "score": round(score, 3),
                                   "steps": len(outcomes), "errors": len(errors)})
        return RunReport(run_id=run_id, objective=objective, steps=outcomes,
                         budget=self.budget.to_dict(), verdict=verdict, score=score,
                         journal=str(journal.path), errors=errors)

    def _run_step(self, run_id: str, journal: Journal, step: dict[str, Any],
                  *, tools: bool, dry_run: bool) -> tuple[StepOutcome, list[dict[str, Any]]]:
        skill_id = step["skills"][0]
        skill = self.registry.skill(skill_id)
        criteria = [_criterion(c, step["id"]) for c in step["criteria"]]

        dispatch = protocols.make(
            "yev-dispatch",
            task_id=step["id"],
            step_id=step["id"],
            origin="yev",
            target="xev",
            skills=[skill_id],
            tools=step.get("tools") or [],
            inputs={},
            criteria=criteria,
        )
        journal.append("dispatch", dispatch.to_dict())

        outcome = StepOutcome(step_id=step["id"], skill=skill_id)
        errors: list[dict[str, Any]] = []

        if not tools or not step.get("tools"):
            outcome.status = "ok"
            journal.append("result", protocols.make(
                "xev-result", task_id=step["id"], step_id=step["id"],
                status="ok", outputs={"mode": "procedure-only"}, artifacts=[]).to_dict())
            return outcome, errors

        for tool_id in step["tools"]:
            self.budget.spend_tool()
            journal.append("tool.call", {"skill": skill_id, "tool": tool_id})
            if dry_run:
                outcome.tools.append({"tool": tool_id, "ok": None, "dry_run": True})
                continue
            payload = self.box.sample_for(skill_id, tool_id)
            result: ToolResult = self.box.run(skill_id, tool_id, payload)
            outcome.tools.append(result.to_dict())
            journal.append("tool.result", result.to_dict())
            if not result.ok:
                outcome.status = "error"
                errors.append(result.error or {"code": "E_TOOL_FAILED",
                                               "message": f"{skill_id}/{tool_id} failed"})
                break

        if outcome.status == "ok" and not dry_run:
            journal.append("result", protocols.make(
                "xev-result", task_id=step["id"], step_id=step["id"], status="ok",
                outputs={"tools": len(outcome.tools)}, artifacts=[]).to_dict())
        elif outcome.status != "ok":
            journal.append("result", protocols.make(
                "xev-result", task_id=step["id"], step_id=step["id"], status="error",
                outputs={}, artifacts=[],
                error={"code": "E_TOOL_FAILED", "message": "a tool failed"}).to_dict())

        return outcome, errors

    def _gate(self, outcomes: list[StepOutcome], errors: list[dict[str, Any]]) -> tuple[str, float]:
        if not outcomes:
            return "blocked", 0.0
        if errors:
            return "fail", 0.0
        clean = sum(1 for o in outcomes if o.status == "ok")
        return ("pass" if clean == len(outcomes) else "fail"), clean / len(outcomes)


def execute(registry: Registry, objective: str, **kwargs: Any) -> RunReport:
    return Runner(registry, **kwargs).run(objective)
