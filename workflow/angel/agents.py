"""Agents as addresses: administration, delegation and the cascade.

An agent is not a prompt with a name. It is a **service**: it publishes a card
(its signature), it is reachable at an address, it has a version and a pinned
hash, and it may call other agents — subagents — through addresses its ancestors
authorised. That framing comes from Harness-Candy, where an agent is an
individual API that can in turn call subagents; this module turns it into data
the runtime can validate, route and journal.

The address
-----------
    agent://<space>/<id>@<major.minor.patch>#<card-hash>

    agent://acme/xev-builder@1.0.0#9f2c0d1e        one exact agent
    agent://acme/xev-builder@1.0.0                 any build of 1.0.0
    agent://acme/xev-builder                       latest version
    .../xev-builder@1.0.0#reviewer                 one hop: ask that agent for
                                                   the address of its delegate

The hash pins the card. Pinning is the difference between "call the reviewer"
and "call whatever is called reviewer today": an exact reference that no longer
matches is a refusal, not a silent upgrade.

The five rules the runtime enforces
-----------------------------------
1. **An agent is a card with a contract.** Required fields, a declared model, a
   declared input and output. A card that does not satisfy its contract is
   refused before it can be called.
2. **Capabilities are closed.** An agent may call a subagent only if its own
   card declares that delegation *and* every ancestor up to the root allowed it
   transitively. Authorisation is intersected down the tree, never granted from
   below.
3. **Depth, fan-out and budget are bounded.** `max_depth`, `max_calls` and the
   budget share are data, checked before a call is attempted.
4. **A cycle is a bug, not a recursion.** Cards form a DAG; a cycle is refused
   when the roster loads, so the cascade cannot be defined into an infinite
   loop.
5. **A call leaves a tree.** Every dispatch produces an addressable tree with a
   journal, so "who called whom, with what authorisation, and what came back" is
   answered by reading, not by guessing.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import AngelError
from .journal import open_journal
from .registry import Registry
from .router import route
from .tools import ToolBox

AGENTS_DIR = "agents"
CARD_FILE = "agent.json"
ROSTER_FILE = "roster.json"
CALLS_DIR = "calls"

SCHEMA = "angel.agent/1"
CONTRACT_NAME = "agent-card"
CONTRACT_VERSION = "1.0.0"
STATES = ("draft", "live", "deprecated")
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SPACE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

#: the card is the API description, so its shape is fixed
REQUIRED = ("schema", "id", "version", "address_space", "role", "state", "model",
            "description", "inputs", "outputs", "skills", "tools", "limits")
OPTIONAL = ("delegates", "guardrails", "references", "owner", "metadata")

WRITABLE_RISKS = ("write", "execute", "destructive")


def _err(code: str, message: str, *, hint: str = "", **context: Any) -> AngelError:
    extras = {k: v for k, v in context.items() if v is not None}
    return AngelError(message, hint=hint, context=extras, code=code)


# --------------------------------------------------------------------------
# addressing
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Address:
    """A parsed agent reference. Immutable: an address is a value, not a cursor."""

    space: str
    agent_id: str
    version: str | None = None
    pin: str | None = None
    hop: str | None = None

    def __str__(self) -> str:
        text = f"agent://{self.space}/{self.agent_id}"
        if self.version:
            text += f"@{self.version}"
        if self.pin:
            text += f"#{self.pin}"
        if self.hop:
            text += f"->{self.hop}"
        return text

    def to_dict(self) -> dict[str, Any]:
        return {"space": self.space, "id": self.agent_id, "version": self.version,
                "pin": self.pin, "hop": self.hop, "text": str(self)}


ADDRESS_RE = re.compile(
    r"^agent://(?P<space>[a-z0-9-]+)/(?P<agent>[a-z0-9-]+)"
    r"(?:@(?P<version>\d+\.\d+\.\d+))?"
    r"(?:#(?P<pin>[0-9a-f]{4,16}))?"
    r"(?:->(?P<hop>[a-z0-9-]+))?$")
BARE_RE = re.compile(r"^(?P<agent>[a-z0-9]+(?:-[a-z0-9]+)*)"
                     r"(?:@(?P<version>\d+\.\d+\.\d+))?"
                     r"(?:#(?P<pin>[0-9a-f]{4,16}))?"
                     r"(?:->(?P<hop>[a-z0-9-]+))?$")


def parse_address(text: str) -> Address:
    """Parse `agent://space/id@version#pin->hop`, or a bare `id`.

    A bare id is an address too: it means "the latest card called `id`, in
    whatever space holds it". It only becomes ambiguous if two spaces define the
    same id, and `Roster.get` refuses that rather than picking one.
    """
    raw = str(text).strip()
    full = ADDRESS_RE.match(raw)
    if full:
        parts = full.groupdict()
        return Address(parts["space"], parts["agent"], parts["version"],
                       parts["pin"], parts["hop"])
    bare = BARE_RE.match(raw)
    if bare and not raw.startswith("agent"):
        parts = bare.groupdict()
        return Address("*", parts["agent"], parts["version"], parts["pin"], parts["hop"])
    raise _err("E_AGENT_ADDRESS", f"not an agent address: {text!r}",
               hint="use agent://<space>/<id>@<x.y.z>#<pin>-><hop>, or a bare id")


# --------------------------------------------------------------------------
# the card
# --------------------------------------------------------------------------
@dataclass
class Agent:
    """One agent: a card on disk plus the folder its delegates live in."""

    card: dict[str, Any]
    path: Path
    category: str = "agents"

    # -- identity ----------------------------------------------------------
    @property
    def id(self) -> str:
        return str(self.card["id"])

    @property
    def version(self) -> str:
        return str(self.card["version"])

    @property
    def major(self) -> int:
        return int(self.version.split(".")[0])

    @property
    def space(self) -> str:
        return str(self.card["address_space"])

    @property
    def role(self) -> str:
        return str(self.card["role"])

    @property
    def state(self) -> str:
        return str(self.card["state"])

    @property
    def model(self) -> dict[str, Any]:
        return dict(self.card.get("model") or {})

    @property
    def limits(self) -> dict[str, Any]:
        return dict(self.card.get("limits") or {})

    @property
    def skills(self) -> list[str]:
        return [str(s) for s in self.card.get("skills") or []]

    @property
    def tools(self) -> list[str]:
        return [str(s) for s in self.card.get("tools") or []]

    @property
    def delegates(self) -> list[dict[str, Any]]:
        return [dict(d) for d in self.card.get("delegates") or []]

    @property
    def guardrails(self) -> list[str]:
        return [str(g) for g in self.card.get("guardrails") or []]

    def edges(self) -> list["Delegation"]:
        """The delegations this card declares, as data rather than a dict."""
        return [Delegation(caller=self.id, target=str(edge.get("to") or ""),
                           when=str(edge.get("when") or ""),
                           allow=[str(a) for a in edge.get("allow") or []],
                           budget=float(edge.get("budget") or 0.0),
                           address=f"agent://{self.space}/{edge.get('to')}")
                for edge in self.delegates]

    # -- addressing --------------------------------------------------------
    def fingerprint(self) -> str:
        """Hash of the parts that change behaviour: the card's public surface.

        Documentation, owner and free-form metadata are excluded on purpose, so
        rewording a description does not invalidate every pinned reference.
        """
        surface = {
            "schema": self.card.get("schema"),
            "id": self.id, "version": self.version, "space": self.space,
            "role": self.role, "state": self.state,
            "inputs": self.card.get("inputs"), "outputs": self.card.get("outputs"),
            "skills": self.skills, "tools": self.tools,
            "delegates": self.card.get("delegates") or [],
            "limits": self.limits, "guardrails": self.guardrails,
            "model": {k: v for k, v in self.model.items() if k != "temperature"},
        }
        raw = json.dumps(surface, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def reference(self, pin: bool = True) -> str:
        text = f"agent://{self.space}/{self.id}@{self.version}"
        return f"{text}#{self.fingerprint()[:8]}" if pin else text

    def address(self, hop: str | None = None) -> Address:
        return Address(self.space, self.id, self.version,
                       self.fingerprint()[:8] if hop is None else None, hop)

    # -- the API description -------------------------------------------------
    def endpoint(self) -> dict[str, Any]:
        """What a caller gets when it asks for this agent's API."""
        return {
            "schema": SCHEMA,
            "address": str(self.address()),
            "reference": self.reference(),
            "id": self.id,
            "version": self.version,
            "space": self.space,
            "role": self.role,
            "state": self.state,
            "description": self.card.get("description"),
            "model": self.model,
            "inputs": self.card.get("inputs"),
            "outputs": self.card.get("outputs"),
            "skills": self.skills,
            "tools": self.tools,
            "guardrails": self.guardrails,
            "limits": self.limits,
            "delegates": [{"to": d.get("to"), "when": d.get("when"),
                           "allow": d.get("allow") or [], "budget": d.get("budget"),
                           "address": f"agent://{self.space}/{d.get('to')}"}
                          for d in self.delegates],
            "callable": self.state == "live",
            "calls": self.fingerprint(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "version": self.version, "space": self.space,
                "role": self.role, "state": self.state, "path": str(self.path),
                "reference": self.reference()}


# --------------------------------------------------------------------------
# delegation and calls
# --------------------------------------------------------------------------
@dataclass
class Delegation:
    """One edge in the call graph, as seen from the caller."""

    caller: str
    target: str
    when: str
    allow: list[str]
    budget: float
    address: str

    def to_dict(self) -> dict[str, Any]:
        return {"caller": self.caller, "target": self.target, "when": self.when,
                "allow": self.allow, "budget": self.budget, "address": self.address}


@dataclass
class Call:
    """A node in a cascade. The tree is the record: no node exists without a parent."""

    agent: str
    reference: str
    depth: int
    objective: str
    status: str = "planned"
    caller: str | None = None
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    allowed: list[str] = field(default_factory=list)
    denied: list[str] = field(default_factory=list)
    children: list["Call"] = field(default_factory=list)
    note: str = ""
    depth_budget: int = 0
    budget: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {"agent": self.agent, "reference": self.reference, "depth": self.depth,
                "objective": self.objective, "status": self.status,
                "caller": self.caller, "skills": self.skills, "tools": self.tools,
                "allowed": self.allowed, "denied": self.denied, "note": self.note,
                "depth_budget": self.depth_budget, "budget": self.budget,
                "children": [c.to_dict() for c in self.children]}

    def walk(self) -> list["Call"]:
        nodes = [self]
        for child in self.children:
            nodes.extend(child.walk())
        return nodes

    def size(self) -> int:
        return len(self.walk())


@dataclass
class Outcome:
    """What came back from one node, validated against the declared outputs."""

    agent: str
    status: str
    verdict: str
    score: float
    outputs: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"agent": self.agent, "status": self.status, "verdict": self.verdict,
                "score": round(self.score, 3), "outputs": self.outputs,
                "findings": self.findings, "ms": round(self.ms, 2)}


# --------------------------------------------------------------------------
# the roster
# --------------------------------------------------------------------------
class Roster:
    """Every agent in the package, addressable, with its call graph."""

    def __init__(self, agents: dict[str, list[Agent]], root: Path) -> None:
        self.root = Path(root)
        self._agents = agents

    # -- lookup ------------------------------------------------------------
    @property
    def agents(self) -> dict[str, Agent]:
        """Latest version of every agent, by id."""
        return {agent_id: versions[-1] for agent_id, versions in self._agents.items()}

    def versions(self, agent_id: str) -> list[Agent]:
        return list(self._agents.get(agent_id) or [])

    def get(self, text: str) -> Agent:
        """Resolve an id or a full address, honouring the pin when it carries one."""
        if not text:
            raise _err("E_AGENT_NOT_FOUND", "an agent reference is required",
                       hint="run `workflow agents list`")
        if text.startswith("agent://"):
            address = parse_address(text)
            agent_id, version, pin = address.agent_id, address.version, address.pin
        else:
            agent_id, _, version = text.partition("@")
            pin = None
            if "#" in version:
                version, _, pin = version.partition("#")
            version = version or None
        found = self._agents.get(agent_id)
        if not found:
            raise _err("E_AGENT_NOT_FOUND", f"unknown agent {agent_id!r}",
                       hint=f"known: {', '.join(sorted(self.agents))}")
        if version:
            match = [a for a in found if a.version == version]
            if not match:
                raise _err("E_AGENT_NOT_FOUND", f"{agent_id}@{version} does not exist",
                           hint=f"available: {', '.join(a.version for a in found)}")
            agent = match[0]
        else:
            agent = found[-1]
        if pin:
            actual = agent.fingerprint()
            if not actual.startswith(pin):
                raise _err("E_AGENT_STALE",
                           f"{agent_id}@{agent.version} is pinned to {pin} but its card "
                           f"hashes to {actual[:len(pin)]}",
                           hint="the card changed under a pinned caller: repin on "
                                "purpose, do not re-resolve silently",
                           agent=agent_id, pinned=pin, actual=actual[:len(pin)])
        return agent

    def resolve(self, address: Address) -> Agent:
        """Resolve a parsed address, following one hop when it names a delegate."""
        agent = self.get(f"agent://{address.space}/{address.agent_id}"
                         + (f"@{address.version}" if address.version else "")
                         + (f"#{address.pin}" if address.pin else ""))
        if not address.hop:
            return agent
        return self.child(agent, address.hop)

    def child(self, agent: Agent, target: str) -> Agent:
        """The agent `target` as reached from `agent`, honouring the declared edge."""
        allowed = {d.get("to") for d in agent.delegates}
        if target not in allowed:
            raise _err("E_DELEGATION_DENIED",
                       f"{agent.id} does not delegate to {target!r}",
                       hint=f"declared: {', '.join(sorted(a for a in allowed if a)) or 'none'}",
                       caller=agent.id, target=target)
        return self.get(target)

    # -- graph -------------------------------------------------------------
    def children(self, agent_id: str) -> list[Agent]:
        agent = self.get(agent_id)
        out = []
        for edge in agent.delegates:
            target = str(edge.get("to") or "")
            if target in self.agents:
                out.append(self.agents[target])
        return out

    def parents(self, agent_id: str) -> list[Agent]:
        return [a for a in self.agents.values()
                if any(str(d.get("to")) == agent_id for d in a.delegates)]

    def tree(self, agent_id: str) -> dict[str, Any]:
        """The call graph reachable from one agent, depth-limited and cycle-safe."""
        agent = self.get(agent_id)

        def node(current: Agent, seen: tuple[str, ...], depth: int) -> dict[str, Any]:
            if depth >= 6:
                return {"id": current.id, "reference": current.reference(),
                        "truncated": True, "children": []}
            children = []
            for edge in current.delegates:
                target_id = str(edge.get("to") or "")
                if target_id in seen:
                    children.append({"id": target_id, "cycle": True, "children": []})
                    continue
                target = self.agents.get(target_id)
                if target is None:
                    children.append({"id": target_id, "missing": True, "children": []})
                    continue
                children.append(node(target, seen + (target_id,), depth + 1))
            return {"id": current.id, "reference": current.reference(),
                    "role": current.role, "state": current.state,
                    "depth": depth, "children": children}

        return node(agent, (agent.id,), 0)

    def cascade_order(self, agent_id: str) -> list[str]:
        """Deterministic top-down order: declared order, breadth first, no repeats."""
        seen: list[str] = []
        queue = [self.get(agent_id).id]
        while queue:
            current = queue.pop(0)
            if current in seen or current not in self.agents:
                continue
            seen.append(current)
            queue.extend(str(d.get("to")) for d in self.agents[current].delegates)
        return seen

    # -- validation --------------------------------------------------------
    def validate(self) -> dict[str, Any]:
        report: dict[str, Any] = {"agents": len(self.agents), "errors": [], "warnings": []}
        for agent in self.agents.values():
            errors, warnings = self._check(agent)
            report["errors"].extend(f"{agent.id}: {e}" for e in errors)
            report["warnings"].extend(f"{agent.id}: {w}" for w in warnings)
        report["errors"].extend(self._check_graph())
        report["errors"].extend(_check_index(self.root, self))
        report["warnings"].extend(self._check_overlap())
        return report

    def _check(self, agent: Agent) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        card = agent.card

        for key in REQUIRED:
            if key not in card:
                errors.append(f"card is missing {key!r}")
        if errors:
            return errors, warnings

        if card.get("schema") != SCHEMA:
            errors.append(f"schema must be {SCHEMA!r}, got {card.get('schema')!r}")
        if not ID_RE.match(str(card.get("id"))):
            errors.append("id must be lowercase words separated by single hyphens")
        if not SPACE_RE.match(str(card.get("address_space"))):
            errors.append("address_space must be lowercase words separated by hyphens")
        if not VERSION_RE.match(str(card.get("version"))):
            errors.append("version must be x.y.z")
        if card.get("state") not in STATES:
            errors.append(f"state must be one of {', '.join(STATES)}")
        if not str(card.get("role") or "").strip():
            errors.append("role is required")
        if len(str(card.get("description") or "")) < 20:
            errors.append("description must say what the agent does, in a sentence")

        model = card.get("model") or {}
        if not str(model.get("name") or "").strip():
            errors.append("model.name is required")
        if model.get("temperature") is not None:
            value = model.get("temperature")
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 2:
                errors.append("model.temperature must be between 0 and 2")

        errors.extend(self._check_io(agent))

        unknown_skills = [s for s in agent.skills if s not in self._registry_skills]
        if unknown_skills:
            errors.append(f"declares skills that do not exist: {', '.join(unknown_skills)}")
        unknown_tools = [t for t in agent.tools if t not in self._registry_tools]
        if unknown_tools:
            errors.append(f"declares tools that do not exist: {', '.join(unknown_tools)}")
        if agent.tools and self._registry_skills:
            risky = [t for t in agent.tools
                     if self._registry_risk.get(t) in WRITABLE_RISKS]
            if risky and not agent.guardrails:
                warnings.append(f"uses {', '.join(risky)} with no guardrail declared")

        limits = card.get("limits") or {}
        for key, ceiling in (("max_depth", 8), ("max_calls", 200)):
            value = limits.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"limits.{key} must be a non-negative integer")
            elif value > ceiling:
                warnings.append(f"limits.{key}={value} is above the sane ceiling {ceiling}")
        budget = limits.get("budget_share", 1.0)
        if not isinstance(budget, (int, float)) or not 0 < float(budget) <= 1:
            errors.append("limits.budget_share must be in (0, 1]")
        if not isinstance(limits.get("timeout_s"), (int, float)) or limits["timeout_s"] <= 0:
            errors.append("limits.timeout_s must be a positive number")

        if agent.state == "live" and not agent.delegates:
            if int(limits.get("max_calls", 0) or 0) > 0:
                warnings.append("declares max_calls but no delegates: it reserves "
                                "room for calls it can never make")
            elif int(limits.get("max_depth", 0) or 0) > 0:
                warnings.append("declares max_depth but no delegates: a leaf that "
                                "promises depth it cannot use")

        for index, edge in enumerate(agent.delegates):
            errors.extend(self._check_edge(agent, edge, index))
        handed_out = sum(float(e.get("budget") or 0) for e in agent.delegates)
        share = float(limits.get("budget_share", 1.0) or 1.0)
        if handed_out > share + 1e-9:
            errors.append(f"delegates hand out {handed_out:g} of budget but "
                          f"limits.budget_share is {share:g}: it cannot give "
                          "away more than it holds")
        return errors, warnings

    def _check_io(self, agent: Agent) -> list[str]:
        errors: list[str] = []
        for side in ("inputs", "outputs"):
            spec = agent.card.get(side)
            if not isinstance(spec, dict):
                errors.append(f"{side} must be an object")
                continue
            fields = spec.get("fields")
            if not isinstance(fields, dict) or not fields:
                errors.append(f"{side}.fields must declare at least one field")
                continue
            for name, field_spec in fields.items():
                if not isinstance(field_spec, dict) or "type" not in field_spec:
                    errors.append(f"{side}.{name} needs a type")
        return errors

    def _check_edge(self, agent: Agent, edge: dict[str, Any], index: int) -> list[str]:
        errors: list[str] = []
        target = str(edge.get("to") or "")
        if not target:
            return [f"delegates[{index}] has no 'to'"]
        if target == agent.id:
            errors.append("cannot delegate to itself")
        if target not in self.agents:
            errors.append(f"delegates[{index}] points at unknown agent {target!r}")
        if not str(edge.get("when") or "").strip():
            errors.append(f"delegates[{index}] needs a 'when': a call without a "
                          "condition is a guess")
        allow = edge.get("allow") or []
        if not isinstance(allow, list) or not all(isinstance(a, str) for a in allow):
            errors.append(f"delegates[{index}].allow must be a list of skills")
        else:
            unknown = [a for a in allow if a not in self._registry_skills]
            if unknown:
                errors.append(f"delegates[{index}].allow names unknown skills: "
                              f"{', '.join(unknown)}")
        budget = edge.get("budget")
        if budget is not None and (not isinstance(budget, (int, float))
                                   or not 0 < float(budget) <= 1):
            errors.append(f"delegates[{index}].budget must be in (0, 1]")
        return errors

    def _check_graph(self) -> list[str]:
        errors: list[str] = []
        # cycles
        state: dict[str, int] = {}

        def visit(agent_id: str, trail: tuple[str, ...]) -> None:
            state[agent_id] = 1
            for edge in self.agents[agent_id].delegates:
                target = str(edge.get("to") or "")
                if target not in self.agents:
                    continue
                if state.get(target) == 1:
                    cycle = " -> ".join((*trail, agent_id, target))
                    errors.append(f"delegation cycle: {cycle}: a card graph must be "
                                  "a DAG, and this one can recurse forever")
                    continue
                if state.get(target) is None:
                    visit(target, (*trail, agent_id))
            state[agent_id] = 2

        for agent_id in sorted(self.agents):
            if state.get(agent_id) is None:
                visit(agent_id, ())

        # declared depth must be reachable within each agent's own limit
        for agent_id in sorted(self.agents):
            agent = self.agents[agent_id]
            deepest = self._depth(agent, (), 0)
            limit = int(agent.limits.get("max_depth", 0) or 0)
            if deepest > limit:
                errors.append(f"the graph below {agent_id} reaches depth {deepest} but "
                              f"its limits.max_depth is {limit}: the cascade could never "
                              "run, so either raise the limit or cut the edge")
        return errors

    def _depth(self, agent: Agent, seen: tuple[str, ...], depth: int) -> int:
        if depth > 8:
            return depth
        deepest = depth
        for edge in agent.delegates:
            target = str(edge.get("to") or "")
            if target not in self.agents or target in seen:
                continue
            deepest = max(deepest, self._depth(self.agents[target],
                                               (*seen, target), depth + 1))
        return deepest

    def _check_overlap(self) -> list[str]:
        warnings: list[str] = []
        seen: dict[str, str] = {}
        for agent in self.agents.values():
            key = (agent.role, tuple(sorted(agent.skills)), tuple(sorted(agent.tools)))
            other = seen.get(str(key))
            if other:
                warnings.append(f"{agent.id} has the same role, skills and tools as {other}")
            else:
                seen[str(key)] = agent.id
        return warnings

    # -- registry bridge ---------------------------------------------------
    _registry_skills: set[str] = set()
    _registry_tools: set[str] = set()
    _registry_risk: dict[str, str] = {}

    def bind(self, registry: Registry | None) -> "Roster":
        """Attach the skill registry so cards can be checked against reality."""
        if registry is None:
            return self
        self._registry_skills = set(registry.skills)
        self._registry_risk = {tool.id: tool.risk
                               for skill in registry.skills.values()
                               for tool in skill.tools}
        self._registry_tools = set(self._registry_risk)
        return self


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def _agent_root(root: Path) -> Path:
    return Path(root) / AGENTS_DIR


def read_index(root: Path) -> dict[str, Any] | None:
    """The roster index, if the package publishes one.

    The folder is the source of truth; the index exists so a reader without
    directory access — the Ely extension runs in a sandbox and can only read
    named files — can still enumerate the agents. `validate` keeps them honest.
    """
    path = _agent_root(root) / ROSTER_FILE
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise _err("E_AGENT_INVALID", f"{ROSTER_FILE}: not JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("agents"), list):
        raise _err("E_AGENT_INVALID",
                   f"{ROSTER_FILE} must be an object with an 'agents' list")
    return data


def _check_index(root: Path, roster: "Roster") -> list[str]:
    """The index and the folder must name exactly the same agents."""
    index = read_index(root)
    if index is None:
        return []
    errors: list[str] = []
    listed = {str(entry.get("id")) for entry in index["agents"]}
    on_disk = set(roster.agents)
    for missing in sorted(on_disk - listed):
        errors.append(f"{AGENTS_DIR}/{ROSTER_FILE} does not list {missing!r}, which has "
                      "a card on disk")
    for ghost in sorted(listed - on_disk):
        errors.append(f"{AGENTS_DIR}/{ROSTER_FILE} lists {ghost!r}, which has no card")
    space = index.get("address_space")
    for agent in roster.agents.values():
        if space and agent.space != space:
            errors.append(f"{agent.id} lives in space {agent.space!r} but {ROSTER_FILE} "
                          f"says {space!r}")
    for entry in index["agents"]:
        agent = roster.agents.get(str(entry.get("id")))
        if agent and entry.get("version") not in (None, agent.version):
            errors.append(f"{agent.id}: {ROSTER_FILE} pins v{entry.get('version')} but "
                          f"the card is v{agent.version}")
    return errors


def _card_contract(root: Path) -> Any:
    """The agent-card contract, when the package ships one."""
    try:
        from . import contracts as contracts_mod

        return contracts_mod.resolve(Path(root), CONTRACT_NAME, CONTRACT_VERSION)
    except AngelError:
        return None


def discover(root: Path, *, registry: Registry | None = None) -> Roster:
    """Load every card under `agents/`, grouped by id and sorted by version.

    When `contracts/agent-card` is installed, every card is validated against it
    before it is admitted: the contract is the signature, and an agent that does
    not match its own signature is not callable.
    """
    base = _agent_root(root)
    contract = _card_contract(root)
    agents: dict[str, list[Agent]] = {}
    if not base.is_dir():
        return Roster({}, root).bind(registry)
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        card_path = folder / CARD_FILE
        if not card_path.is_file():
            continue
        try:
            card = json.loads(card_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise _err("E_AGENT_INVALID", f"{folder.name}/{CARD_FILE}: not JSON: {exc}",
                       agent=folder.name) from exc
        if not isinstance(card, dict):
            raise _err("E_AGENT_INVALID", f"{folder.name}/{CARD_FILE}: the card must be "
                       "an object", agent=folder.name)
        if contract is not None:
            try:
                contract.validate(card)
            except AngelError as exc:
                raise _err("E_AGENT_INVALID",
                           f"{folder.name}/{CARD_FILE} does not satisfy "
                           f"{CONTRACT_NAME}@{CONTRACT_VERSION}: {exc.message}",
                           hint="fix the card or bump the contract on purpose",
                           agent=folder.name) from exc
        agent = Agent(card=card, path=folder)
        agents.setdefault(agent.id, []).append(agent)
    for versions in agents.values():
        versions.sort(key=lambda a: tuple(int(x) for x in a.version.split("."))
                      if VERSION_RE.match(a.version) else (0, 0, 0))
    return Roster(agents, root).bind(registry)


# --------------------------------------------------------------------------
# dispatch: the cascade as data
# --------------------------------------------------------------------------
class Dispatcher:
    """Turns one objective into a call tree, then optionally executes it.

    Planning and execution are separate on purpose: a cascade that cannot be
    planned is not attempted, and the plan is inspectable before anything runs.
    """

    def __init__(self, roster: Roster, registry: Registry | None = None,
                 root: Path | None = None) -> None:
        self.roster = roster
        self.registry = registry
        self.root = Path(root) if root else roster.root

    # -- planning ----------------------------------------------------------
    def plan(self, caller: str, objective: str, *, depth: int = 0,
             inherited: list[str] | None = None,
             remaining: int | None = None) -> Call:
        """Plan one node and, recursively, the subagents its card authorises.

        `inherited` is the authority the caller holds: the `allow` list of the
        edge that reached it. Capabilities are intersected with it, never
        extended by it — a subagent can do less than its caller allowed, never
        more, and never anything the chain above did not name.
        """
        agent = self.roster.get(caller)
        if agent.state != "live":
            raise _err("E_AGENT_NOT_LIVE",
                       f"{agent.id} is {agent.state}; only live agents can be called",
                       hint="promote it in the card when it is ready",
                       agent=agent.id, state=agent.state)
        # max_depth is measured from the agent itself: how many hops below it a
        # cascade may go. A subagent is also bounded by what its caller has left.
        declared = int(agent.limits.get("max_depth", 0) or 0)
        cap = declared if remaining is None else min(declared, remaining)

        authority = self._authority(agent, inherited)
        node = Call(agent=agent.id, reference=agent.reference(), depth=depth,
                    objective=objective, caller=None, allowed=authority, depth_budget=cap)
        node.skills = [s for s in agent.skills if s in authority] if authority \
            else list(agent.skills)
        node.tools = self._tools_for(node.skills)
        routed: set[str] = set()
        if self.registry is not None:
            routed = self._route(node, objective)

        for edge in agent.delegates:
            target_id = str(edge.get("to") or "")
            share = float(edge.get("budget", 0.5))
            if cap < 1:
                node.denied.append(f"{target_id}: beyond max_depth "
                                   f"({declared} hop(s) below {agent.id})")
                continue
            if len(node.children) >= int(agent.limits.get("max_calls", 0)):
                node.denied.append(f"{target_id}: beyond max_calls")
                continue
            child_allow = [a for a in (edge.get("allow") or []) if a in authority] \
                if authority else list(edge.get("allow") or [])
            if not child_allow:
                node.denied.append(f"{target_id}: none of its allow list survives "
                                   f"the authority granted to {agent.id}")
                continue
            if not _reaches(edge, objective, routed, child_allow):
                node.note = _append(node.note, f"skipped {target_id}: "
                                    f"'{edge.get('when')}' did not match")
                continue
            child = self.plan(target_id, objective, depth=depth + 1,
                              inherited=child_allow, remaining=cap - 1)
            child.caller = agent.id
            child.allowed = child_allow
            child.budget = round(node.budget * share, 4)
            node.children.append(child)

        return node

    def _authority(self, agent: Agent, inherited: list[str] | None) -> list[str]:
        """What this node is allowed to exercise.

        Inherited when it was reached through an edge; at the root, the card
        owns the process, so its authority is its own skills plus everything it
        names on its own edges.
        """
        if inherited is not None:
            return list(inherited)
        granted = [s for s in agent.skills]
        for edge in agent.delegates:
            for skill in edge.get("allow") or []:
                if skill not in granted:
                    granted.append(str(skill))
        return granted

    def _tools_for(self, skills: list[str]) -> list[str]:
        if self.registry is None:
            return []
        tools: list[str] = []
        for skill_id in skills:
            skill = self.registry.skills.get(skill_id)
            if skill:
                tools.extend(t.id for t in skill.tools)
        return tools

    def _route(self, node: Call, objective: str) -> set[str]:
        """Keep the node's skills that the router also considers relevant.

        An agent declares what it *can* do; the router decides what this
        objective *needs*. Both must agree, otherwise the cascade would fan out
        into every capability an agent owns. Returns everything the router
        found, so delegation conditions can be checked against it too.
        """
        if self.registry is None:
            return set()
        routed = {step["skill"] for step in
                  route(self.registry, objective, limit=8).steps}
        narrowed = [s for s in node.skills if s in routed]
        if narrowed:
            node.skills = narrowed
            node.tools = self._tools_for(narrowed)
        elif node.skills:
            node.note = _append(node.note, "no declared skill matched the "
                                "objective; call kept with its full capability")
        return routed

    # -- execution ---------------------------------------------------------
    def execute(self, tree: Call, *, journal: Any = None, profile: str = "standard",
                tools: bool = True) -> dict[str, Any]:
        """Walk the planned tree, enforcing authorisation at every hop."""
        box = ToolBox(self.registry, profile=profile) if (self.registry and tools) else None
        outcomes: list[Outcome] = []
        errors: list[dict[str, Any]] = []

        executed = 0

        def visit(node: Call, ancestors: tuple[str, ...], depth_left: int,
                  calls_left: int) -> None:
            """Run one node, then its children, under both its ceilings.

            `depth_left` is what the chain above still allows; `calls_left` is how
            many calls the ancestors permit in this subtree. Both are checked
            here as well as at plan time, because the second is the one that
            costs something to get wrong.
            """
            nonlocal executed
            started = time.time()
            try:
                agent = self.roster.get(node.agent)
            except AngelError as exc:
                node.status = "error"
                errors.append(exc.to_dict())
                return
            if depth_left < 0:
                node.status = "denied"
                errors.append(_err("E_AGENT_DEPTH",
                                   f"{agent.id} is deeper than its caller allows",
                                   agent=agent.id).to_dict())
                return
            executed += 1
            own_depth = min(depth_left, int(agent.limits.get("max_depth", 0) or 0))
            own_calls = min(calls_left, int(agent.limits.get("max_calls", 0) or 0))

            findings: list[dict[str, Any]] = []
            if box is not None:
                for tool_id in node.tools:
                    owner = self._owner_of(tool_id)
                    if owner is None:
                        continue
                    result = box.run(owner, tool_id, box.sample_for(owner, tool_id))
                    if not result.ok:
                        findings.append({"severity": "high", "tool": tool_id,
                                         "message": str((result.error or {}).get("message"))})
            node.status = "error" if findings else "ok"
            verdict = "fail" if findings else "pass"
            outcomes.append(Outcome(
                agent=agent.id, status=node.status, verdict=verdict,
                score=0.0 if findings else 1.0,
                outputs={"skills": node.skills, "depth": node.depth,
                         "authorised": node.allowed},
                findings=findings, ms=(time.time() - started) * 1000))
            if journal is not None:
                journal.append("dispatch", {"agent": agent.id, "depth": node.depth,
                                            "caller": node.caller,
                                            "skills": node.skills,
                                            "authorised": node.allowed})
                journal.append("result", {"agent": agent.id, "status": node.status,
                                          "verdict": verdict,
                                          "findings": len(findings)})

            for index, child in enumerate(node.children):
                if own_depth < 1:
                    child.status = "denied"
                    errors.append(_err("E_AGENT_DEPTH",
                                       f"{child.agent}: {agent.id} may not go deeper",
                                       agent=child.agent).to_dict())
                    continue
                if index >= own_calls:
                    child.status = "denied"
                    errors.append(_err("E_AGENT_DEPTH",
                                       f"{child.agent}: {agent.id} may make at most "
                                       f"{own_calls} call(s)", agent=child.agent).to_dict())
                    continue
                visit(child, (*ancestors, agent.id), own_depth - 1,
                      own_calls - index - 1)

        root_agent = self.roster.get(tree.agent)
        visit(tree, (), int(root_agent.limits.get("max_depth", 0) or 0),
              int(root_agent.limits.get("max_calls", 0) or 0))
        failed = [o for o in outcomes if o.verdict != "pass"]
        return {
            "root": tree.agent,
            "calls": tree.size(),
            "executed": len(outcomes),
            "verdict": "pass" if not failed and not errors else "fail",
            "score": round(1 - len(failed) / len(outcomes), 3) if outcomes else 0.0,
            "outcomes": [o.to_dict() for o in outcomes],
            "errors": errors,
        }

    def _owner_of(self, tool_id: str) -> str | None:
        if self.registry is None:
            return None
        for skill in self.registry.skills.values():
            if any(t.id == tool_id for t in skill.tools):
                return skill.id
        return None


def _append(note: str, line: str) -> str:
    return f"{note}; {line}" if note else line


def _reaches(edge: dict[str, Any], objective: str, routed: set[str],
             allow: list[str]) -> bool:
    """Does this delegation condition apply to this objective?

    Two independent ways to say yes, because `when` is prose a person wrote:

    * a word of the condition appears in the objective, or
    * the child can exercise a skill the router says this objective needs.

    The second check is what keeps a cascade honest under rewording: an
    objective phrased in new words still reaches the subagent that owns the
    matching skill.
    """
    words = {w for w in re.findall(r"[a-z0-9]{4,}", str(edge.get("when") or "").lower())}
    if not words:
        return True
    if any(word in objective.lower() for word in words):
        return True
    return bool(routed & set(allow))


# --------------------------------------------------------------------------
# entry points used by the CLI
# --------------------------------------------------------------------------
def load(root: Path, registry: Registry | None = None) -> Roster:
    return discover(root, registry=registry)


def plan(root: Path, root_agent: str, objective: str,
         registry: Registry | None = None) -> dict[str, Any]:
    roster = discover(root, registry=registry)
    dispatcher = Dispatcher(roster, registry, root)
    tree = dispatcher.plan(root_agent, objective)
    return {"root": root_agent, "objective": objective, "calls": tree.size(),
            "addresses": [f"agent://{roster.get(c.agent).space}/{c.agent}@{c.depth}"
                          for c in tree.walk()],
            "tree": tree.to_dict()}


def call(root: Path, reference: str, objective: str, *,
         registry: Registry | None = None, execute: bool = False,
         profile: str = "standard") -> dict[str, Any]:
    """One hop: resolve the address, check authorisation, route, optionally run."""
    roster = discover(root, registry=registry)
    address = parse_address(reference) if reference.startswith("agent://") else None
    target = roster.resolve(address) if address else roster.get(reference)
    dispatcher = Dispatcher(roster, registry, root)

    started = time.time()
    run_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    journal = open_journal(root, run_id)
    journal.append("run.start", {"kind": "agent-call", "address": str(address or reference),
                                 "objective": objective})
    try:
        tree = dispatcher.plan(target.id, objective)
        tree.reference = target.reference()
        result = (dispatcher.execute(tree, journal=journal, profile=profile)
                  if execute else {"verdict": "planned", "outcomes": [], "errors": []})
    except AngelError as exc:
        journal.append("error", exc.to_dict())
        raise
    journal.append("run.end", {"verdict": result["verdict"], "calls": tree.size()})
    return {
        "address": str(address or reference),
        "resolved": target.to_dict(),
        "caller": (address.hop if address else None),
        "objective": objective,
        "executed": execute,
        "verdict": result["verdict"],
        "calls": tree.size(),
        "tree": tree.to_dict(),
        "outcomes": result["outcomes"],
        "errors": result["errors"],
        "journal": str(journal.path),
        "ms": round((time.time() - started) * 1000, 2),
    }


def save_call(root: Path, payload: dict[str, Any]) -> Path:
    """Persist a cascade so it can be read later without re-running anything."""
    folder = Path(root) / ".workflow" / CALLS_DIR
    folder.mkdir(parents=True, exist_ok=True)
    name = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6] + ".json"
    path = folder / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
