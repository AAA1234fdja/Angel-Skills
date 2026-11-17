# AGENTS.md — agents and subagents

This document defines what an **agent** is in this package, how one agent calls
another, and which rules the runtime refuses to break. It exists because an
agent is easy to write as a prompt and hard to administer as a service; the
whole point of the module is to make the service part checkable.

Everything here is enforced by `angel/agents.py`, exercised by
`tests/test_agents.py`, and readable from the CLI:

```
workflow agents list|show|validate|tree|address|plan|call
```

## 1. An agent is an API

The framing comes from **Harness-Candy**: each agent is an individual API, and
every API may call subagents. That gives four consequences, and each one is a
rule here rather than a convention.

| Consequence | What it means in this package |
|---|---|
| An API has an address | `agent://<space>/<id>@<x.y.z>#<pin>-><hop>` |
| An API has a signature | the card, `agents/<id>/agent.json`, validated by `agent-card@1.0.0` |
| An API has terms of use | `limits` (depth, calls, budget share, timeout) and `guardrails` |
| An API can be composed | `delegates`: named edges, each with a condition and an allowance |

An agent is **not** a prompt with a name. A prompt has no version, no pinned
hash, no declared output and no way to say no. The card has all four.

## 2. The address

```
agent://acme/xev-builder@1.0.0#3d6252a9        one exact card
agent://acme/xev-builder@1.0.0                 any build of 1.0.0
agent://acme/xev-builder                       latest version
agent://acme/isa-planner->xev-builder          one hop: that agent's delegate
xev-builder                                    bare id, resolved against the space
```

The pin is the first 8 hex characters of the card's **behaviour fingerprint** —
a SHA-256 over the public surface: schema, id, version, space, role, state,
inputs, outputs, skills, tools, delegates, limits, guardrails and the model
minus its temperature. Prose is excluded on purpose: rewording a `description`
or changing `owner` must not invalidate every caller that pinned the agent.

```
workflow agents address agent://acme/xev-builder@1.0.0#3d6252a9
workflow agents address agent://acme/xev-builder@1.0.0#deadbeef   # E_AGENT_STALE, exit 13
```

An exact reference that no longer matches is a **refusal**, never a silent
upgrade. That is the difference between "call the reviewer" and "call whatever
is called reviewer today".

## 3. The card

```json
{
  "schema": "angel.agent/1",
  "id": "xev-builder",
  "version": "1.0.0",
  "address_space": "acme",
  "role": "executor",
  "state": "live",
  "description": "Implements a routed plan inside one sandboxed workspace and reports the diff it produced.",
  "model": {"name": "builder-tier", "reasoning": "high", "temperature": 0.1, "context_tokens": 200000},
  "inputs":  {"fields": {"objective": {"type": "string"}, "plan": {"type": "object"}}},
  "outputs": {"fields": {"diff": {"type": "string"}, "verdict": {"type": "string", "enum": ["pass", "fail", "blocked"]}}},
  "skills": ["tdd-workflow", "verification-loop"],
  "tools": [],
  "guardrails": ["no network", "writes only inside the workspace"],
  "limits": {"max_depth": 2, "max_calls": 6, "budget_share": 1.0, "timeout_s": 1800},
  "delegates": [
    {"to": "xev-tester", "when": "tests must be written or fixed",
     "allow": ["tdd-workflow", "e2e-testing"], "budget": 0.4}
  ]
}
```

Required: `schema`, `id`, `version`, `address_space`, `role`, `state`, `model`,
`description`, `inputs`, `outputs`, `skills`, `tools`, `limits`.
Optional: `delegates`, `guardrails`, `references`, `owner`, `metadata`.

- `role` — `planner`, `executor`, `researcher`, `validator`, `governor`, `router`.
- `state` — `draft`, `live`, `deprecated`. Only `live` can be called.
- `skills` — ids that must exist in the registry; a card cannot invent a skill.
- `tools` — ids that must exist; a card that names a write tool without a
  guardrail gets a warning.
- `limits.max_depth` — how many hops **below this agent** the cascade may go.
- `limits.max_calls` — how many delegates this agent may call at once.
- `limits.budget_share` — the fraction of the parent budget this agent holds;
  it can never hand out more than it holds.

## 4. The five rules

1. **A card is a contract.** With `contracts/agent-card` installed, every card
   is validated against it before the roster is admitted. A card that does not
   match its own signature is not callable — `E_AGENT_INVALID`, exit 2.
2. **Authority only narrows.** An agent may call a subagent only if its card
   declares that edge *and* the skills the edge allows were granted to the
   caller by the chain above. Intersecting happens downward; nothing is ever
   granted from below. A skill named by an edge but never authorised above is
   silently absent from the child, and the child is *denied* rather than
   widened when nothing survives (`E_DELEGATION_DENIED`, exit 14).
3. **Depth, fan-out and budget are data.** `max_depth`, `max_calls` and the
   budget share are checked before a call is attempted, at plan time. A plan
   that would exceed them records the denial instead of trying.
4. **A cycle is a bug, not a recursion.** The card graph must be a DAG. A cycle
   is refused when the roster loads, so the cascade cannot be defined into an
   infinite loop. The graph is also checked against each agent's declared
   `max_depth`: a graph deeper than every limit "could never run" and is an
   error, not a warning.
5. **A call leaves a tree.** Every dispatch produces an addressable tree with a
   hash-chained journal, so "who called whom, with what authorisation, and what
   came back" is answered by reading, not by guessing.

## 5. Planning a cascade

Planning and execution are separate on purpose. A cascade that cannot be
planned is never attempted, and the plan is inspectable first.

```
workflow agents plan --agent isa-planner \
  --need "unfamiliar failure: trace the cause through the history and write the tests"
```

```text
isa-planner [1.0]
  agent-harness-construction, context-budget, skill-authoring
  ○ xev-builder [0.7]
     tdd-workflow
      ○ zev-scout [0.3]
      ○ xev-tester [0.4]
         ○ zev-scout [0.2]
```

Two filters decide the shape, and both are recorded:

- **The router** narrows each node to the skills this objective actually needs,
  using the same scoring as `workflow route`. An agent declares what it *can*
  do; the router decides what this objective *needs*.
- **The condition** of each edge (`when`) must apply, by either of two tests: a
  word of the condition appears in the objective, or the child can exercise a
  skill the router says is needed. The second test is what keeps a cascade
  working when an objective is reworded.

## 6. Calling for real

```
workflow agents call --agent agent://acme/xev-builder@1.0.0 --need "add the endpoint and its tests" --execute
```

With `--execute` every node runs its tools inside the same sandbox the runner
uses (`ToolBox`, profile `standard`), and each hop is journalled as `dispatch`
then `result`. Without it, the call is planned, journalled as planned, and
saved — `verdict: planned`.

Every call is written to `.workflow/calls/<timestamp>-<id>.json`; every journal
to `.workflow/journal/<run-id>.jsonl`. Both are ignored by git and safe to
delete; the tree can always be recomputed from the cards.

## 7. The shipped roster

Six cards live under `agents/`, one per role. They exist to prove the graph is
real, not to prescribe a product.

| Agent | Role | Skills | Delegates to |
|---|---|---|---|
| `isa-planner` | planner | agent-harness-construction, context-budget, skill-authoring | `xev-builder`, `wev-judge` |
| `xev-builder` | executor | tdd-workflow, verification-loop, coding-standards, build-fix | `zev-scout`, `wev-judge`, `xev-tester` |
| `xev-tester` | executor | tdd-workflow, ai-regression-testing, e2e-testing | `zev-scout` |
| `wev-judge` | validator | code-review, verification-loop, security-review, accessibility-audit | `zev-scout` |
| `zev-scout` | researcher | search-first, reverse-engineering, binary-triage, failure-forensics | — (leaf) |
| `governance-auditor` | governor | skill-audit, skill-authoring, changelog-discipline | `zev-scout` |

```
isa-planner ─┬─ xev-builder ─┬─ zev-scout
             │               ├─ wev-judge ── zev-scout
             │               └─ xev-tester ── zev-scout
             └─ wev-judge ────── zev-scout
```

Every skill a card names is a real skill in the registry, and every skill an
edge allows is a subset of what the caller holds. The validator checks both,
and `tests/test_agents.py` checks the validator.

`agents/roster.json` is the index the Ely extension reads (an iframe cannot list
a directory): it must name exactly the cards on disk, in the same space and at
the same versions. The folder remains the source of truth; the runtime refuses a
roster that disagrees.

## 8. Adding an agent

1. Write `agents/<id>/agent.json` against `agent-card@1.0.0`.
2. Choose skills that already exist: `workflow list`, or `workflow route --need "..."`
   to see which ones an objective reaches.
3. Declare `limits` before `delegates` — depth first, then fan-out, then budget.
4. Give every edge a `when` a person would say out loud, and an `allow` strictly
   narrower than what the parent holds.
5. Add the id to `categories.json` (`agents`) and to `agents/roster.json`.
6. Run:

```
workflow agents validate --strict
workflow agents plan --agent <id> --need "<a real objective>"
workflow agents call --agent <id> --need "<a real objective>" --execute
```

An agent without a checked plan is a guess with a version number.

## 9. Codes

| Code | Exit | Meaning | Owner |
|---|---|---|---|
| `E_AGENT_INVALID` | 2 | the card breaks its contract or a structural rule | author |
| `E_AGENT_NOT_FOUND` | 12 | no such id, version or card | caller |
| `E_AGENT_ADDRESS` | 12 | the address does not parse | caller |
| `E_AGENT_STALE` | 13 | a pinned card changed under the caller | caller |
| `E_AGENT_NOT_LIVE` | 13 | the card is `draft` or `deprecated` | caller |
| `E_DELEGATION_DENIED` | 14 | the target is not a declared delegate | author |
| `E_AGENT_DEPTH` | 14 | the call is deeper than `max_depth` | caller |

Every one of them is declared in `angel/errors.py` with an owner and a recovery
hint; none of them is retryable.
