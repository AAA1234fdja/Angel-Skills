# workflow · the skill package of Angel

Package **0.5.0** — a self-contained set of **52 skills, 49 executable tools,
5 contracts and 6 agents**, with a registry, a validator, a router, a run engine,
an agent dispatcher and an optional Ely extension. No external dependencies, no
network, no services: Python 3.10+ standard library only.

```text
workflow/
├── WORKFLOW.md            ← read first: purpose, routing path, rules
├── EXTENSION-STANDARD.md  ← read before creating or editing a skill
├── categories.json        ← registry: the source of truth for categories, ids, agents
├── skills/<category>/<id>/
│   ├── SKILL.md           the procedure (when, when not, steps, exit criteria)
│   ├── skill.json         the composition (phase, verbs, triggers, tools, contracts)
│   └── tools/*.py         executables: run(payload) -> dict
├── contracts/<name>/<version>.schema.json   versioned promises, immutable
├── agents/<id>/agent.json the card: an agent is an API with an address
├── agents/roster.json     the index the Ely extension reads
├── AGENTS.md              agents and subagents: addresses, cards, the five rules
├── angel/                 the runtime (registry, router, protocols, contracts,
│                          tools, journal, runner, agents, errors, cli)
├── tests/                 194 tests over the runtime, the catalogue and the extension
├── tools/                 maintenance scripts (add_samples.py)
└── ely-extension/         optional extension for Ely IDE (angel.workflow)
```

## Quick start

From `workflow/`:

```bash
python3 -m angel.cli list                     # skills by category, with tools
python3 -m angel.cli show tdd-workflow        # one skill, with its manifest
python3 -m angel.cli validate --strict        # registry ⇄ disk, no warnings
python3 -m angel.cli route --need "the build is broken"      # who answers, and why
python3 -m angel.cli run --need "the build is broken"        # plan → tools → verdict
python3 -m angel.cli tool --self-test         # every tool on its declared sample
python3 -m angel.cli contract --check         # contract history and compatibility
python3 -m angel.cli journal --all            # verify every run's hash chain
python3 -m angel.cli agents list              # the roster, with pinned addresses
python3 -m angel.cli agents validate --strict # cards, edges, depth, budgets, cycles
python3 -m angel.cli agents plan --agent isa-planner --need "review this diff"
python3 -m angel.cli agents call --agent xev-builder --need "add the endpoint" --execute
python3 -m angel.cli pack --out dist/workflow.zip
```

`--json` before the subcommand gives machine-readable output; the exit code is the
contract (see `EXTENSION-STANDARD.md` §10).

## The six rules of the package

1. **A skill is a folder with a procedure and a composition.** `SKILL.md` says what
   to do; `skill.json` says when to load it and what to run. One without the other
   is half a skill and fails validation.
2. **The registry and the disk never disagree.** Every skill on disk is registered;
   every registered skill has a `SKILL.md`. `validate` compares both directions.
3. **Routing is data, not a prompt.** A need is scored against the triggers, verbs
   and keywords each manifest declares. A wrong route is a manifest bug you can fix
   and re-run, and the reasons are printed.
4. **Tools are pure and sandboxed.** A tool receives its whole payload and never
   touches the filesystem, the network or the process table; it may import only
   pure-computation modules. Every tool ships a `sample`, which is what makes
   `tool --self-test` possible.
5. **A run leaves evidence.** Every hand-off is a typed protocol message and every
   run writes a hash-chained journal: what ran, in what order, under what budget.
6. **An agent is an API that cannot widen itself.** Its card is a contract, its
   address carries a behaviour pin, its subagents only ever receive an intersection
   of what it holds, and a call graph with a cycle is refused before it runs.

## Current state

| Category | Status | Skills | Gate |
|---|---|---|---|
| `engineering` | activa | 15 | no change finished without tdd-workflow + verification-loop evidence |
| `contracts` | activa | 5 | versions are immutable; a breaking change is a new major |
| `protocols` | activa | 3 | zero malformed messages accepted |
| `errors` | activa | 5 | no error crosses a boundary without code, owner and recovery |
| `agentic` | activa | 5 | no agent change without an eval before and after |
| `security` | activa | 5 | high-severity findings block the run |
| `data` | activa | 5 | no migration without a tested reverse path |
| `reversing` | activa | 3 | every finding is tied to an artefact |
| `governance` | activa | 3 | nothing enters without `validate --strict` + a registry record |
| `product` | activa | 2 | accessibility AA failures block |
| `content` | activa | 1 | nothing published without an executed example |

Each skill's `phase`, `verbs`, `triggers` and tools are in
`skills/<category>/<id>/skill.json`; the catalogue with descriptions is
`categories.json`.

## Routing path

```text
need (one sentence)
  → route: score every skill, keep the answers, print the reasons
  → plan: order the steps, attach criteria, budget
  → dispatch (yev-dispatch) → execute: run each tool with its sample or payload
  → result (xev-result) → verdict (wev-verdict) → gate → journal
```

The router understands English and Spanish terminology, masks negated clauses ("sin
tests" never routes to a test skill), and never offers a skill that only shares a
verb with the need. `route --explain <skill> --need ...` shows the score breakdown.

## Agents and subagents

An **agent is an API**: it publishes a card, it answers at an address, and every
API may call subagents. `AGENTS.md` is the reference; the short version:

```
workflow agents list                      # roster, versions, addresses
workflow agents show xev-builder          # one card in full
workflow agents validate --strict         # contract, edges, limits, cycles
workflow agents tree isa-planner          # the delegation graph
workflow agents address agent://acme/isa-planner->xev-builder
workflow agents plan  --agent isa-planner --need "review the security of this diff"
workflow agents call  --agent xev-builder --need "add the endpoint and its tests" --execute
```

Addresses carry a pin: `agent://acme/xev-builder@1.0.0#3d6252a9`. The pin is a
hash of the card's behaviour surface, so an exact reference refuses a card that
changed instead of quietly upgrading it (`E_AGENT_STALE`, exit 13). Authority is
intersected down the tree, `max_depth`/`max_calls`/budget are checked before a
call is attempted, a cycle is refused when the roster loads, and every call
leaves a tree plus a hash-chained journal.

Six cards ship in `agents/`: `isa-planner`, `xev-builder`, `xev-tester`,
`wev-judge`, `zev-scout`, `governance-auditor`. Their skills are real skills from
the registry, checked by `agents validate`, so the graph cannot drift into
fiction.

## Adding a skill

1. Read `EXTENSION-STANDARD.md` §1–§7.
2. `python3 -m angel.cli new <id> --category <category> --phase <phase> --verb <verb>`
   — it scaffolds the folder **and** registers it atomically.
3. Fill in `SKILL.md`, then `skill.json` (tools, triggers, contracts).
4. `python3 -m angel.cli validate --strict` → green, or no commit.
5. Add a line to `CHANGELOG.md`.

The full procedure is the `skill-authoring` skill.

## Integrating with Ely (optional)

The extension never activates by itself: it is copied into the IDE and enabled from
the **Extensions** view.

```bash
python3 -m angel.cli install --ely /path/to/Ely
```

That leaves `IDE/ely-extensions/angel.workflow/` with the manifest, `main.js` and a
copy of the package so the extension can read it through `workspace.readFile`
without leaving its sandbox. Commands it adds to the palette:

| Command | What it does |
|---|---|
| `Workflow: list skills` | table by category with status and trigger |
| `Workflow: load phase into chat` | asks for a phase and sends only those skills |
| `Workflow: open a skill` | shows the full `SKILL.md` |
| `Workflow: tools of a skill` | its tools, risks and contracts |
| `Workflow: validate the package` | same rules as the CLI, inside the IDE |
| `Workflow: read the standard` | opens `EXTENSION-STANDARD.md` |
| `Workflow: pack agents` | every card with its address, limits and edges |
| `Workflow: agent tree` | the delegation graph reached from each root |
| `Workflow: agent address` | one card's address, inputs, outputs, guardrails |

Declared permissions: `workspace:read`, `ui`, `commands`, `chat`. No network, no
writes. Disabling it leaves the package intact and the CLI working.

## Line budget

The package has a stated size: **10,000 ≤ total lines ≤ 25,000**. It is measured,
not estimated, with one command from `workflow/`:

```bash
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.json" -o -name "*.mjs" -o -name "*.js" \) \
  -not -path "./dist/*" -not -path "./.workflow/*" -not -path "*/__pycache__/*" \
  | sort | xargs wc -l | tail -1
```

Current figure: **21,615 lines** (13.5% below the ceiling).

### Why the ceiling moved

The previous ceiling was 20,000 and the package sat 4.8% below it with eight skills
to add. Rather than pad files or trim procedures to fit a number chosen when the
catalogue had 44 skills, the budget was renegotiated once, in the open, with a
reason: **52 skills, 49 executable tools, 5 contracts and 6 agents** do not fit in
20,000 lines at the current density (~250 lines per skill with its tool). A ceiling
that forces worse skills is measuring the wrong thing.

The rule did not change, only the number:

- measured, never estimated: the command above, quoted in the README;
- a change that breaks the ceiling is a decision, recorded in the changelog;
- density is not a target: a skill is as long as its exit criteria need.

| Block | Lines |
|---|---|
| skill tools | 3,156 |
| `SKILL.md` procedures | 3,327 |
| manifests and contracts (`skill.json`, `categories.json`, schemas) | 5,508 |
| runtime `angel/` | 5,034 |
| tests | 2,242 |
| main documents | 1,086 |
| Ely extension | 528 |
| agent cards and index (`agents/`) | 451 |
| maintenance scripts | 240 |

The remaining 3,385 lines are roughly thirteen more skills at the current density,
or a smaller number if the next batch carries tools as heavy as these eight
(~490 lines each: a procedure, a tool, a sample and an acceptance list). That
trade-off is the budget's actual job: it forces the choice to be made out loud.

## Origin of the patterns

Skills marked `status: adoptada` adapt procedures from
[affaan-m/ECC](https://github.com/affaan-m/ECC) (MIT, commit `b38be6a`), rewritten
for this repository with the original id kept in `metadata.origin`. The complete
inventory is `../ECC-INVENTARIO.md`; what this package does differently is in
`WORKFLOW.md` §1.
