# EXTENSION-STANDARD.md — how a skill is written here

> Read this **before** creating or editing any skill. `WORKFLOW.md` explains the
> purpose; this file is the contract. Package `0.3.0` · updated 2026-11-05
>
> Machine check: `workflow validate --strict` implements §5 and §6. If the
> standard and the validator disagree, the validator wins and this file is a bug.

---

## 1. The three tests of a skill

A skill is justified only if all three hold:

1. **Trigger** — a recognisable situation says *when* to use it.
2. **Procedure** — ordered steps someone else could execute without asking you.
3. **Checkable exit** — something can be *verified* at the end: a command, a test,
   an artefact, a signed review.

If any fails, it is a note → `docs/`, not `skills/`.

---

## 2. Anatomy

```text
skills/<category>/<id>/
├── SKILL.md       required — the procedure
├── skill.json     required — the composition (routing + execution)
├── tools/*.py     optional — each exposes run(payload) -> dict
└── references/    optional — long-form notes, loaded only on demand
```

| Rule | Detail |
|---|---|
| Canonical path | `workflow/skills/<category>/<id>/SKILL.md` |
| Skill id | `^[a-z0-9]+(-[a-z0-9]+)*$`, unique, **stable forever** |
| Category id | same pattern; must exist in `categories.json` |
| Registry | a skill on disk that is not registered is an **error** |
| Size | `SKILL.md` ≤ 400 lines, body ≤ 260 before splitting into `references/` |
| Placement | one skill lives in exactly one category: the one of its primary trigger |

---

## 3. `SKILL.md` contract

```markdown
---
name: tdd-workflow
description: Red-green-refactor with a coverage gate so a task is never called done on inspection alone. Use when implementation is about to be written or a defect is about to be fixed.
metadata:
  origin: ECC · skills/tdd-workflow
  category: engineering
  phase: test
  status: adopted
  version: 1
---

# TDD Workflow

## When to Use
## When Not to Use
## Procedure
## Exit Criteria
## Common Failures
```

**3.1 `description`** — the only field a model reads to decide whether to load the
skill. It must: start with the outcome, contain the literal trigger `Use when`,
fit in **700 characters**, carry no markdown or newlines, and be distinguishable
from every other skill in its category. If two descriptions can be swapped, one of
them is redundant.

**3.2 `metadata`** — `origin`, `category`, `phase`, `status`, `version` are
required. `phase` ∈ `plan · design · research · implement · test · review · verify · debug · audit · document · meta`. `status`
∈ `adopted · original · experimental`.

**3.3 Sections** — `When to Use`, `Procedure`, `Exit Criteria` are **required**.
`When Not to Use` and `Common Failures` are strongly advised; their absence is a
warning, not an error.

**3.4 Prose** — English. Imperative. No emojis. No "in this document we will".
Exit criteria are a checklist, each item checkable by a machine or a named person.

---

## 4. `skill.json` contract

```json
{
  "id": "tdd-workflow",
  "category": "engineering",
  "description": "…",
  "phase": "test",
  "verbs": ["test", "implement"],
  "triggers": ["write the failing test", "red green refactor"],
  "keywords": ["tdd", "test", "coverage"],
  "tools": [
    {
      "id": "coverage-gate",
      "entry": "tools/coverage_gate.py",
      "description": "Checks a coverage report against a threshold.",
      "risk": "read",
      "timeout": 20,
      "input": {"type": "object", "properties": {}, "required": []}
    }
  ],
  "contracts": ["skill-report@1.0.0"],
  "requires": ["verification-loop"],
  "routing": {"not_for": ["one-off exploration"]},
  "acceptance": [{"id": "exit", "statement": "tests fail first, then pass", "kind": "test"}]
}
```

| Field | Required | Consumed by |
|---|---|---|
| `id`, `category`, `description` | yes | validation |
| `phase` | yes | routing filter and step order |
| `verbs` | recommended | router (×2.5) |
| `triggers` | recommended | router (×3.0) |
| `keywords` | recommended | router (×1.0) |
| `tools[]` | if the skill automates anything | `tool`, `run` |
| `contracts[]` | if it exchanges structured data | `contract --check` |
| `requires[]` | if it cannot run alone | `route` ordering |
| `routing.not_for[]` | optional | router exclusion |
| `acceptance[]` | recommended | the criteria the runner attaches to a step |

**4.1 Risk levels for tools**

| Risk | Meaning | Allowed in profile |
|---|---|---|
| `read` | observes, never mutates | all |
| `write` | mutates files inside the workspace | `standard`, `full` |
| `execute` | runs subprocesses or the network | `standard`, `full` |
| `destructive` | deletes, rewrites history, force-pushes | `full` + explicit consent |

**4.2 Tool files** — a module with `run(payload) -> dict`. It runs with an
allow-listed builtins set (no `open`, no `eval`, no `__import__` of arbitrary
modules), a wall-clock timeout, and captured stdout/stderr. It must return a
JSON-serialisable dict; anything else is `E_TOOL_FAILED`. If a tool needs to
write files, it does so through explicit paths passed in the payload.

---

## 5. Checklist before saving

Errors (block):

- [ ] id matches the pattern and is unique
- [ ] path is `skills/<category>/<id>/`
- [ ] frontmatter has `name`, `description`, `metadata.origin/category/phase/status/version`
- [ ] `description` contains `Use when` and ≤ 700 chars
- [ ] `When to Use`, `Procedure`, `Exit Criteria` exist
- [ ] `skill.json` exists with `id`, `category`, `description`
- [ ] every declared tool has an existing `entry` file and a valid `risk`
- [ ] registered in `categories.json` (`workflow validate` green)

Warnings (review):

- [ ] missing `When Not to Use` / `Common Failures`
- [ ] body > 260 lines (should it be split?)
- [ ] no `triggers` in the manifest (routing will be weak)
- [ ] destructive tool without a documented confirmation path
- [ ] description overlaps another skill in the same category

---

## 6. Anti-patterns (forbidden)

| Anti-pattern | Why |
|---|---|
| A skill that describes a topic without a procedure | no way to tell whether it was applied |
| An umbrella skill that does everything | the model cannot tell when to fire it |
| Copying ECC wholesale | 314 skills compete for context; adopt on demonstrated need |
| Absolute paths or machine names inside a skill | breaks portability |
| Renaming a published id | breaks registry, routing, contracts and journals |
| A tool that mutates without declaring `write` | bypasses authorisation |
| Hooks or scripts lifted from ECC | they are coupled to its structure; rewrite if needed |

---

## 7. Registering a new skill (the only supported path)

```bash
workflow new my-skill --category engineering --phase implement --verb refactor \
  --description "One sentence with the outcome." --when "the trigger situation"
workflow validate --strict
```

`workflow new` does five things: validates the id, refuses duplicates, creates
`SKILL.md` + `skill.json` from the template, registers the skill in
`categories.json`, and removes it from `pending`. Editing the template by hand is
allowed; registering by hand is not — the CLI is what keeps the registry and the
disk in sync.

Then:

1. Rewrite the procedure sections with real steps.
2. Add `tools/` if the exit criteria can be checked mechanically, and declare each
   tool in `skill.json` with the lowest risk that works.
3. Add `contracts/` if the skill exchanges structured data with another skill.
4. `workflow validate --strict` and `workflow tool --list`.
5. Bump `metadata.version` and add a `CHANGELOG.md` line.

---

## 8. Changing an existing skill

1. Read the skill and its `metadata.version`.
2. Change the body freely; **never** change `name`, `category` or the id.
3. If routing changed (triggers, verbs, keywords), say so in the changelog.
4. If a tool's payload shape changed, that is a contract change: new contract
   version, and `workflow contract --check` must pass.
5. Bump `metadata.version`, add the changelog line, run `validate --strict`.

---

## 9. Validation and exit codes

`workflow validate` runs, in order: registry JSON → every registered skill exists
→ frontmatter parses → §5 errors → §5 warnings → contracts (`contract --check`).

| Code | Meaning |
|---|---|
| 0 | valid |
| 1 | errors |
| 2 | warnings present with `--strict` |

Nothing is packed (`workflow pack`) or installed into Ely while validation fails.

---

## 10. Licence and attribution

ECC is MIT. Skills marked `adopted` keep ECC's id, cite `origin`, and are
rewritten for this repository — not copied verbatim. `original` skills are this
repository's own. Any future verbatim inclusion needs ECC's MIT notice in
`NOTICE.md`.
