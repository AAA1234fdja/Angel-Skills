# WORKFLOW.md — what this package is for

> **This is the first file to read.** `EXTENSION-STANDARD.md` says *how* a skill
> is written; this file says *why the package exists*, what it must beat, and how
> a need travels from a sentence to a verified result.
> Package `0.4.0` · updated 2026-11-05

---

## 1. Purpose

ECC (affaan-m/ECC, MIT) proved something worth copying: a harness beats a prompt,
and a catalogue of procedures beats a catalogue of opinions. It ships 314 skills,
71 agents and 98 commands and it works.

It also shows the ceiling of that design: a catalogue so large that it competes
with the context window, skills that are single markdown files with no way to
*do* anything, hand-offs described in prose instead of typed messages, and quality
enforced by convention plus a lot of hooks.

**This package targets the same outcome as ECC — an agent that plans, tests,
reviews, verifies and remembers — with four structural upgrades:**

| ECC approach | Here | Why it is better |
|---|---|---|
| skill = one `SKILL.md` | skill = **folder**: `SKILL.md` + `skill.json` + `tools/` | the procedure and the executable composition live together and are validated together |
| hand-offs in prose | **typed, versioned protocols** (`angel/protocols.py`) | a malformed message is rejected with a code, not silently obeyed |
| quality by convention | **contracts** (JSON-schema + version + consumers) and a **failure taxonomy** | breaking changes are detected mechanically, failures have owners |
| everything loaded at once | **router** scoring triggers/verbs/phases, phase loading | cheapest context that can do the job, and you can see *why* a skill was picked |
| "it ran" | **hash-chained journal** + budgets + risk profiles | auditable: what ran, in what order, with what authorisation |

The objective, stated plainly:

> **Given a need in one sentence, load the smallest set of skills that can satisfy
> it, execute their tools under an explicit budget and permission model, verify
> the result against declared criteria, and leave a trace that can be audited
> without trusting the agent that produced it.**

Everything in the package serves that sentence, or it does not belong here.

---

## 2. The shape of a skill

```text
skills/<category>/<id>/
├── SKILL.md      the procedure: when, when not, steps, exit criteria, failures
├── skill.json    the composition: phase, verbs, triggers, keywords, tools, contracts
├── tools/        optional executables, each `run(payload) -> dict`
└── references/   optional long-form notes, loaded only on demand
```

A skill without tools is still a skill: its exit criteria are checked by a person
or by another skill. A skill with tools is *eval-driven*: the tool produces
evidence that the exit criteria can be checked against.

`skill.json` is what makes routing and execution possible. Without it a skill is
prose; with it, the runtime can decide when to load it and what to run.

---

## 3. Categories and the routing path

Eleven categories, each with a gate (a rule that blocks "done" inside it) and a
set of rules. All eleven are active: 44 skills, 41 tools, 4 contracts. A category
exists only if it names a hole the others do not cover — that is why there are
eleven and not forty.

| # | Category | Gate |
|---|---|---|
| 1 | `engineering` | no change finished without tdd-workflow + verification-loop evidence |
| 2 | `contracts` | contract versions are immutable; breaking change = new major |
| 3 | `protocols` | zero malformed messages accepted |
| 4 | `errors` | no error crosses a boundary without code, owner and recovery contract |
| 5 | `agentic` | no agent change without an eval before and after |
| 6 | `security` | high-severity findings block the run |
| 7 | `data` | no migration without a tested reverse path |
| 8 | `reversing` | every finding tied to an artefact |
| 9 | `governance` | nothing enters without `validate --strict` and a registry record |
| 10 | `product` | accessibility AA failures block |
| 11 | `content` | nothing published without an executed example and a named source of truth |

### The route, step by step

```text
need (one sentence)
   │
   ├─ 1. route      normalise the need (Spanish terms mapped, negated clauses
   │                masked), then score every skill: trigger ×3 (+2 when it sits in
   │                the clause of a verb the skill declares), keyword ×0.7 (×0.4
   │                outside that clause, capped at 3), verb ×2.2, explicit id ×100;
   │                drop zeros, `not_for` and anything below 2.5
   │                → steps banded into answers (≥60% of the best score) and support;
   │                  each band ordered by lifecycle (plan → … → verify → meta)
   │
   ├─ 2. plan       emit isa-plan: objective, steps, per-step criteria, budget
   │
   ├─ 3. dispatch   per step emit yev-dispatch: skill, tools, criteria
   │
   ├─ 4. authorise  tool risk (read/write/execute/destructive) vs profile
   │                observe < standard < full; destructive needs consent
   │
   ├─ 5. execute    run the tool with safe builtins, timeout and output capture
   │                emit xev-result (ok/error/partial) — error needs an error
   │
   ├─ 6. verdict    emit wev-verdict: findings with severity, score, verdict
   │                a pass verdict may not carry high/critical findings
   │
   ├─ 7. gate       run-level verdict: any failure → fail; else pass with score
   │
   └─ 8. journal    hash-chained append-only record of every message and tool call
```

Nothing in that chain asks the model to remember a rule: each stage validates its
input and refuses bad data with a taxonomy code.

---

## 4. What to load, and what not to

The package is a **library**, not a prompt. The rule:

| Situation | Load | Do not load |
|---|---|---|
| Starting a task | `route --need "…"` (no skill bodies) | the catalogue |
| Executing a phase | the skills of that phase only (`route --need … --phase …`) | skills of other phases |
| Writing or editing a skill | `SKILL.md` + `EXTENSION-STANDARD.md` §4–§7 | everything else |
| Debugging a run | the journal of that run | the whole journal directory |
| Adding a capability | `skill-authoring` | the 44 existing skills |

Budget: one phase, at most five skills, tools only for the steps that need them.
`workflow run` enforces this by construction — it never loads a skill body.

---

## 5. Agents: an API that may call subagents

A skill is a procedure; an agent is the service that runs it. Each agent publishes
a card (`agents/<id>/agent.json`, contract `agent-card@1.0.0`) and answers at
`agent://<space>/<id>@<x.y.z>#<pin>`. The pin hashes the behaviour surface, not the
prose, so a pinned reference refuses a changed card instead of silently upgrading.

Authority only narrows: a subagent receives the intersection of what its caller
holds and what the edge `allow`s, never the union. `max_depth`, `max_calls` and the
budget share are checked at plan time, a cycle is refused when the roster loads,
and every call leaves a tree plus a hash-chained journal. `AGENTS.md` is the
reference; `workflow agents validate --strict` is the check.

## 6. Non-negotiable rules

1. **The registry is the source of truth.** On disk without registered is an
   error; registered without a folder is an error.
2. **A skill states a checkable exit.** Not "review the code" but "the six phases
   ran and their output is quoted".
3. **Tools are declared, authorised and captured.** A tool that is not in
   `skill.json` does not exist for the runtime.
4. **Failures are typed.** `angel/errors.py` is the only place a code is defined.
5. **Messages are validated before use.** Unknown fields are errors.
6. **Contracts are immutable per version.** Need a change? New file, new version,
   and the diff tells you if it is major.
7. **Every run leaves a chain.** If the chain does not verify, the run did not
   happen.
8. **Ids never change.** Renaming a skill breaks routing, contracts and journals.

---

## 7. Growth path

| Phase | What happens | Status |
|---|---|---|
| 0.1 | registry, standard, CLI, Ely extension | done |
| 0.2 | engineering + agentic catalogues in Spanish | superseded |
| 0.3 | folder skills, protocols, contracts, errors, tools, router, journal; 44 skills, 41 tools, 4 contracts, 125 tests | done |
| **0.4** | **agents as APIs: cards, pinned addresses, cascade planning, `agent-card@1.0.0`; 6 agents, 5 contracts, 176 tests** | **current** |
| 0.5 | `product` and `content` filled; tools for the remaining skills | next |
| 1.0 | contracts frozen at major 1; every active skill has at least one tool or a sibling check | later |

Adding a category is a data change in `categories.json`; adding a skill is
`workflow new` (see `skill-authoring`). Neither requires touching the runtime —
that is the test of whether this design is real or decorative.

---

## 8. What "better than ECC" concretely means

Not "more skills" — ECC wins that and it does not matter. It means:

- **smaller context** for the same capability (router + phase loading, measured by
  `workflow route --json | jq .budget`);
- **executable procedures** instead of described ones (tools with tests);
- **refusals instead of drift**: unknown protocol, broken contract, unauthorised
  tool, malformed message all fail loudly with a code and an owner;
- **auditability**: any run can be replayed from its journal and verified;
- **self-administration**: the package can register, audit and validate itself
  (`new`, `validate --strict`, `skill-audit`) without a human reading markdown.

If a change does not move one of those five, it is decoration.
