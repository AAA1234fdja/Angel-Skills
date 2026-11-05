# ECC (affaan-m/ECC) — Inventario completo de skills y herramientas

> Repositorio revisado: [github.com/affaan-m/ECC](https://github.com/affaan-m/ECC)
> Commit inspeccionado: `b38be6a` (rama `main`, 30 oct 2026) · Versión `2.2.3`
> Documento generado: 2026-11-05 · Enfoque principal: **skills** y **herramientas** (agentes, comandos, hooks, MCP, scripts).

---

## 1. Qué es ECC

ECC ("the agent harness performance optimization system", antes *Everything Claude Code*) no es una colección suelta de prompts: es un **sistema operativo de harness para agentes de código**. Instalas una vez y el agente gana un proceso de ingeniería completo:

```text
plan -> test -> implement -> review -> verify -> remember -> improve
```

Filosofía declarada: *"Optimize the context window. Persist everything else."* Todo lo que se instala vive en el repo raíz y los adaptadores de cada plataforma (Claude Code, Codex, Cursor, OpenCode, Qoder, Kiro, Copilot, Gemini, Qwen, Hermes, Antigravity, Kimi…) **mapean** esos mismos artefactos en lugar de mantener copias paralelas.

| Dato | Valor |
|---|---|
| Licencia | MIT (el repo OSS es gratis para siempre; ECC Pro es un GitHub App de pago para repos privados) |
| Versión actual | 2.2.3 |
| Commits | ~4.321 |
| Lenguajes del repo | Shell, TypeScript, Python, Rust (`ecc2/`), Go, Java, Perl, Markdown |
| Distribución | Plugin `ecc@ecc`, npm `ecc-universal` + `ecc-agentshield`, GitHub App `ecc-tools`, instalador universal (`install.sh` / `install.ps1`) |
| Sitio | [ecc.tools](https://ecc.tools) · Discord propio |

---

## 2. Números del repo (lo que hay dentro)

| Componente | Cantidad | Ruta |
|---|---|---|
| **Skills** (workflows cargados on-demand) | **314** | `skills/<nombre>/SKILL.md` |
| **Agentes** (subagentes especializados) | **71** | `agents/*.md` |
| **Comandos slash** mantenidos | **98** | `commands/*.md` |
| Comandos legacy (opt-in) | 5 | `legacy-command-shims/commands/` |
| **Hooks** registrados (8 eventos) | **28** | `hooks/hooks.json` + `hooks/hooks.metadata.json` |
| Scripts de hook | 61 | `scripts/hooks/` |
| **Servidores MCP** preconfigurados | **34** | `mcp-configs/mcp-servers.json` |
| Packs de **rules** | 22 directorios · 122 archivos | `rules/` |
| Módulos de instalación | 47 | `manifests/install-modules.json` |
| Perfiles de instalación | 7 | `manifests/install-profiles.json` |
| Componentes instalables nombrados | 93 | `manifests/install-components.json` |
| Scripts (instalación, auditoría, orquestación, CI) | 374 | `scripts/` |
| Archivos de test | 534 | `tests/` |
| Documentación (incl. 26 locales) | ~1.527 `.md` | `docs/` |
| Perfil portable "Pi" | 134 skills + 24 comandos puros | `pi/core/` |

Fíjate en la proporción: **las skills son el 80 % del valor real del repo**. Los comandos son, según el propio README, "shims de compatibilidad mantenidos durante la migración" — el desarrollo nuevo va a `skills/`.

---

## 3. Cómo se organiza la raíz

```text
ECC/
├── agents/            71 subagentes (planner, reviewers por lenguaje, build resolvers…)
├── skills/            314 skills; el catálogo canónico del producto
├── commands/          98 slash-commands mantenidos (compatibilidad)
├── legacy-command-shims/  shims retirados, opt-in (agent-sort, claw, context-budget, devfleet, docs)
├── rules/             common/ + 21 packs por lenguaje/framework (coding-style, testing, security, hooks, patterns)
├── hooks/             hooks.json, metadata, memory-persistence/, strategic-compact/, variantes codex/qoder/hermes
├── scripts/           install, repair, doctor, sync, orquestación, auditorías, CI (374 archivos)
├── mcp-configs/       34 servidores MCP listos para copiar
├── manifests/         perfiles y módulos de instalación selectiva
├── contexts/          dev.md, review.md, research.md (inyección de system prompt por modo)
├── examples/          CLAUDE.md de ejemplo: SaaS Next.js, Go microservice, Django, Laravel, Rails, Rust, HarmonyOS
├── config/            project-stack-mappings.json, github-native-coordination.json
├── schemas/           17 JSON Schemas (hooks, memory, install-state, provenance, capsule…)
├── tests/             534 archivos (JS + Python)
├── docs/              guías + 26 locales traducidos
├── pi/core/           perfil portable sin hooks ni red
├── ecc2/              scaffold del control-plane Rust (alpha): TUI, SQLite store, daemon
├── docker/            context-profiles, gateguard-effectiveness, plugin-setup
├── ecc_dashboard.py   dashboard de escritorio Tkinter (916 líneas)
├── the-longform-guide.md · the-shortform-guide.md · the-security-guide.md
└── .claude-plugin/    plugin.json + marketplace.json (marketplace "ecc")
```

Adaptadores por harness incluidos en el repo: `.claude/`, `.agents/` (47 skills + marketplace), `.cursor/` (12 skills + 13 hooks), `.kiro/` (43 skills + agents + steering), `.codex/`, `.opencode/`, `.claude/enterprise`, `.claude/homunculus`.

---

## 4. Las 314 skills (inventario completo por categoría)

Formato: enlace al `SKILL.md` real + resumen de su descripción oficial. Las he agrupado por función (las categorías son mías; ECC las clasifica por módulos de instalación, ver §9).

### Resumen por categoría

| Categoría | Nº |
|---|---|
| Agentic engineering, harness y orquestación | 58 |
| Lenguajes, frameworks y plataformas móviles | 64 |
| Negocio, contenido y dominios verticales | 49 |
| Investigación, documentación y contexto | 31 |
| Backend, datos e infraestructura | 28 |
| Calidad, testing y ciclo de desarrollo | 17 |
| Medios, vídeo y creatividad | 16 |
| Meta: configuración y gobierno del harness | 15 |
| Seguridad | 14 |
| Producto, UX y craft de interfaz | 12 |
| Redes, homelab y operaciones de infra | 10 |
| **Total** | **314** |

## 5. Catálogo de skills por categoría

### Agentic engineering, harness y orquestación — 58 skills

El núcleo del repo: diseño de agentes, loops autónomos, evaluación, memoria, presupuesto de contexto y orquestación multi-agente.

| Skill | Qué hace |
|---|---|
| [`agent-architecture-audit`](https://github.com/affaan-m/ECC/blob/main/skills/agent-architecture-audit/SKILL.md) | Full-stack diagnostic for agent and LLM applications. Audits the 12-layer agent stack for wrapper regression, memory pollution, tool discipline failur… |
| [`agent-eval`](https://github.com/affaan-m/ECC/blob/main/skills/agent-eval/SKILL.md) | Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics. |
| [`agent-harness-construction`](https://github.com/affaan-m/ECC/blob/main/skills/agent-harness-construction/SKILL.md) | Design and optimize AI agent action spaces, tool definitions, and observation formatting for higher completion rates. |
| [`agent-introspection-debugging`](https://github.com/affaan-m/ECC/blob/main/skills/agent-introspection-debugging/SKILL.md) | Structured self-debugging workflow for AI agent failures using capture, diagnosis, contained recovery, and introspection reports. |
| [`agent-payment-x402`](https://github.com/affaan-m/ECC/blob/main/skills/agent-payment-x402/SKILL.md) | Add x402 payment execution to AI agents with per-task budgets, spending controls, and non-custodial wallets. |
| [`agent-runtime-gateway-smoke-test`](https://github.com/affaan-m/ECC/blob/main/skills/agent-runtime-gateway-smoke-test/SKILL.md) | Verify a local agent API, temporary gateway tunnel, and remote sandbox callback with a tool-free task, then restore the original app connection. |
| [`agent-self-evaluation`](https://github.com/affaan-m/ECC/blob/main/skills/agent-self-evaluation/SKILL.md) | Use after completing any non-trivial task. The agent self-rates its output on 5 axes — accuracy, completeness, clarity, actionability, conciseness — w… |
| [`agent-sort`](https://github.com/affaan-m/ECC/blob/main/skills/agent-sort/SKILL.md) | Build an evidence-backed ECC install plan for a specific repo by sorting skills, commands, rules, hooks, and extras into DAILY vs LIBRARY buckets usin… |
| [`agentic-engineering`](https://github.com/affaan-m/ECC/blob/main/skills/agentic-engineering/SKILL.md) | Operate as an agentic engineer using eval-first execution, decomposition, and cost-aware model routing. |
| [`agentic-os`](https://github.com/affaan-m/ECC/blob/main/skills/agentic-os/SKILL.md) | Build persistent multi-agent operating systems on Claude Code. |
| [`ai-first-engineering`](https://github.com/affaan-m/ECC/blob/main/skills/ai-first-engineering/SKILL.md) | Engineering operating model for teams where AI agents generate a large share of implementation output. |
| [`autonomous-agent-harness`](https://github.com/affaan-m/ECC/blob/main/skills/autonomous-agent-harness/SKILL.md) | Transform Claude Code into a fully autonomous agent system with persistent memory, scheduled operations, computer use, and task queuing. |
| [`autonomous-loops`](https://github.com/affaan-m/ECC/blob/main/skills/autonomous-loops/SKILL.md) | Patterns and architectures for autonomous Claude Code loops — from simple sequential pipelines to RFC-driven multi-agent DAG systems. |
| [`benchmark-optimization-loop`](https://github.com/affaan-m/ECC/blob/main/skills/benchmark-optimization-loop/SKILL.md) | Convert 'make it faster' requests into a bounded measured optimization loop — baseline first, generate one-hypothesis variants, benchmark each against… |
| [`blueprint`](https://github.com/affaan-m/ECC/blob/main/skills/blueprint/SKILL.md) | Turn a one-line objective into a step-by-step construction plan for multi-session, multi-agent engineering projects: one-PR-sized steps with self-cont… |
| [`claude-devfleet`](https://github.com/affaan-m/ECC/blob/main/skills/claude-devfleet/SKILL.md) | Orchestrate multi-agent coding tasks via Claude DevFleet — plan projects, dispatch parallel agents in isolated worktrees, monitor progress, and read s… |
| [`context-budget`](https://github.com/affaan-m/ECC/blob/main/skills/context-budget/SKILL.md) | Routes live context checks to the native Codex or Claude Code meter without scanning files, and performs a bounded static component audit only when ex… |
| [`continuous-agent-loop`](https://github.com/affaan-m/ECC/blob/main/skills/continuous-agent-loop/SKILL.md) | Patterns for continuous autonomous agent loops with quality gates, evals, and recovery controls. |
| [`continuous-learning`](https://github.com/affaan-m/ECC/blob/main/skills/continuous-learning/SKILL.md) | [DEPRECATED - use continuous-learning-v2] Legacy v1 stop-hook skill extractor. |
| [`continuous-learning-v2`](https://github.com/affaan-m/ECC/blob/main/skills/continuous-learning-v2/SKILL.md) | Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/comman… |
| [`contract-first`](https://github.com/affaan-m/ECC/blob/main/skills/contract-first/SKILL.md) | Coordinate frontend/backend or service-to-service work through one authoritative machine-checkable contract (OpenAPI, AsyncAPI, Protocol Buffers, or J… |
| [`cost-aware-llm-pipeline`](https://github.com/affaan-m/ECC/blob/main/skills/cost-aware-llm-pipeline/SKILL.md) | Cost optimization patterns for LLM API usage — model routing by task complexity, budget tracking, retry logic, and prompt caching. |
| [`cost-tracking`](https://github.com/affaan-m/ECC/blob/main/skills/cost-tracking/SKILL.md) | Track and report Claude Code token usage, spending, and budgets from the local ECC cost-tracker metrics log. |
| [`council`](https://github.com/affaan-m/ECC/blob/main/skills/council/SKILL.md) | Convene a four-voice council for ambiguous decisions, tradeoffs, and go/no-go calls. |
| [`council-multi-model`](https://github.com/affaan-m/ECC/blob/main/skills/council-multi-model/SKILL.md) | Add one optional external Codex critique after the existing council has produced a decision draft. |
| [`deepseek-harness-setup`](https://github.com/affaan-m/ECC/blob/main/skills/deepseek-harness-setup/SKILL.md) | Install and operate Everything Claude Code (ECC) on the DeepSeek Harness (DSH): native skill roots (~/.dsh/skills, .agents/skills), the @deepseek-ai/d… |
| [`dmux-workflows`](https://github.com/affaan-m/ECC/blob/main/skills/dmux-workflows/SKILL.md) | Multi-agent orchestration using dmux (tmux pane manager for AI agents). |
| [`enterprise-agent-ops`](https://github.com/affaan-m/ECC/blob/main/skills/enterprise-agent-ops/SKILL.md) | Operational controls for long-lived or cloud-hosted agent systems — runtime lifecycle (start, pause, stop, restart), observability (logs, metrics, tra… |
| [`eval-harness`](https://github.com/affaan-m/ECC/blob/main/skills/eval-harness/SKILL.md) | Eval-driven development (EDD) framework for AI coding sessions — define capability and regression evals before coding, grade with code-based, model-ba… |
| [`gan-style-harness`](https://github.com/affaan-m/ECC/blob/main/skills/gan-style-harness/SKILL.md) | GAN-inspired Generator-Evaluator agent harness for building high-quality applications autonomously. |
| [`loop-design-check`](https://github.com/affaan-m/ECC/blob/main/skills/loop-design-check/SKILL.md) | Design a goal-oriented agent loop or review one for failure modes: spinning, Goodhart-gaming the verifier, or running a wrong answer to completion. |
| [`operator-approval-loop`](https://github.com/affaan-m/ECC/blob/main/skills/operator-approval-loop/SKILL.md) | Operator approval contract with internal filing notices for agent-drafted outbound messages, hashed drafts, epoch-keyed decisions, durable delivery cl… |
| [`plan-orchestrate`](https://github.com/affaan-m/ECC/blob/main/skills/plan-orchestrate/SKILL.md) | Read a plan document, decompose it into steps, classify each step, and emit the ready-to-paste ECC slash command for that step, carrying the step iden… |
| [`ralphinho-rfc-pipeline`](https://github.com/affaan-m/ECC/blob/main/skills/ralphinho-rfc-pipeline/SKILL.md) | Split an RFC into a multi-agent execution DAG — decompose into work units with dependencies and acceptance tests, run research, plan, implement, test,… |
| [`recursive-decision-ledger`](https://github.com/affaan-m/ECC/blob/main/skills/recursive-decision-ledger/SKILL.md) | Run repeated rollouts ("Prime Gauss" style recursive prompting) while keeping an append-only decision ledger of trials, marks, coherence checks, and p… |
| [`santa-method`](https://github.com/affaan-m/ECC/blob/main/skills/santa-method/SKILL.md) | Multi-agent adversarial verification: two independent reviewers with the same rubric must both pass before output ships, with a fix-and-re-review conv… |
| [`strategic-compact`](https://github.com/affaan-m/ECC/blob/main/skills/strategic-compact/SKILL.md) | Suggests manual context compaction at logical intervals to preserve context through task phases rather than arbitrary auto-compaction. |
| [`story-lifecycle`](https://github.com/affaan-m/ECC/blob/main/skills/story-lifecycle/SKILL.md) | Manage a file-based epic → story → sprint development loop without requiring an external project management tool. |
| [`team-agent-orchestration`](https://github.com/affaan-m/ECC/blob/main/skills/team-agent-orchestration/SKILL.md) | Run team-based orchestration for agent squads: work items with owners and scope, agent Kanban state, branch isolation, control pane visibility, and me… |
| [`team-builder`](https://github.com/affaan-m/ECC/blob/main/skills/team-builder/SKILL.md) | Interactive picker that discovers available agent personas via the claude agents command and agents/ markdown globs, groups them into domains, has the… |
| [`terminal-opener`](https://github.com/affaan-m/ECC/blob/main/skills/terminal-opener/SKILL.md) | Open an executable and its argument array in a visible terminal window through a reusable, shell-free launch plan with dry-run, JSON, capability detec… |
| [`token-budget-advisor`](https://github.com/affaan-m/ECC/blob/main/skills/token-budget-advisor/SKILL.md) | Offer a choice of response depth (25%/50%/75%/100%) with token estimates before answering, then answer at that level. |
| [`token-card`](https://github.com/affaan-m/ECC/blob/main/skills/token-card/SKILL.md) | Render a token-usage stat card from local Claude Code, Codex, Gemini CLI, and OpenCode session logs and commit it into the repository as a file. |
| [`prompt-caching-strategy`](https://github.com/affaan-m/ECC/blob/main/skills/prompt-caching-strategy/SKILL.md) | Optimize LLM prompt caching hit rate to reduce API costs and improve latency. |
| [`prompt-optimizer`](https://github.com/affaan-m/ECC/blob/main/skills/prompt-optimizer/SKILL.md) | Analyze draft prompts, detect intent and missing context, match ECC commands, skills, and agents, and output a ready-to-paste optimized prompt with di… |
| [`parallel-execution-optimizer`](https://github.com/affaan-m/ECC/blob/main/skills/parallel-execution-optimizer/SKILL.md) | Speed up a task by turning it into a dependency graph of parallel lanes with a lane matrix, batched reads and checks, write surfaces isolated by file,… |
| [`nanoclaw-repl`](https://github.com/affaan-m/ECC/blob/main/skills/nanoclaw-repl/SKILL.md) | Operate and extend NanoClaw, ECC's zero-dependency session-aware REPL, with persistent markdown-backed sessions and slash commands for model switching… |
| [`openclaw-persona-forge`](https://github.com/affaan-m/ECC/blob/main/skills/openclaw-persona-forge/SKILL.md) | 为 OpenClaw AI Agent 锻造完整的龙虾灵魂方案。根据用户偏好或随机抽卡， 输出身份定位、灵魂描述(SOUL.md)、角色化底线规则、名字和头像生图提示词。 如当前环境提供已审核的生图 skill，可自动生成统一风格头像图片。 当用户需要创建、设计或定制 OpenClaw 龙虾灵魂时使… |
| [`orch-add-feature`](https://github.com/affaan-m/ECC/blob/main/skills/orch-add-feature/SKILL.md) | Orchestrate building a brand-new feature end to end — research, plan, TDD implementation, review, and gated commit — by delegating each phase to the m… |
| [`orch-build-mvp`](https://github.com/affaan-m/ECC/blob/main/skills/orch-build-mvp/SKILL.md) | Orchestrate bootstrapping a working MVP from a design or spec document — ingest the SDD/PRD, plan thin vertical slices, scaffold the first end-to-end… |
| [`orch-change-feature`](https://github.com/affaan-m/ECC/blob/main/skills/orch-change-feature/SKILL.md) | Orchestrate altering an existing, working feature to new desired behavior — update its tests to the new spec, change the implementation to match, revi… |
| [`orch-fix-defect`](https://github.com/affaan-m/ECC/blob/main/skills/orch-fix-defect/SKILL.md) | Orchestrate fixing a bug — reproduce it as a failing regression test, fix to green, review, and gated commit — by delegating each phase to the matchin… |
| [`orch-pipeline`](https://github.com/affaan-m/ECC/blob/main/skills/orch-pipeline/SKILL.md) | Shared orchestration engine behind the orch-* skill family — the gated Research-Plan-TDD-Review-Commit pipeline, size classifier, agent and command ma… |
| [`orch-refine-code`](https://github.com/affaan-m/ECC/blob/main/skills/orch-refine-code/SKILL.md) | Orchestrate a behavior-preserving refactor — confirm tests are green, restructure without changing behavior, keep tests green, review, and gated commi… |
| [`verification-loop`](https://github.com/affaan-m/ECC/blob/main/skills/verification-loop/SKILL.md) | Run a six-phase verification of a Claude Code session's work — build, type check, lint, tests with coverage, security grep, and diff review — then pro… |
| [`dev-team`](https://github.com/affaan-m/ECC/blob/main/skills/dev-team/SKILL.md) | Simulate a collaborative dev team session where multiple role-based personas (PM, Architect, Developer, QA) respond to the same problem together in on… |
| [`dynamic-workflow-mode`](https://github.com/affaan-m/ECC/blob/main/skills/dynamic-workflow-mode/SKILL.md) | Design task-local harnesses, eval gates, and reusable skill extraction for Claude dynamic workflow mode and other adaptive agent harnesses. |
| [`project-flow-ops`](https://github.com/affaan-m/ECC/blob/main/skills/project-flow-ops/SKILL.md) | Operate execution flow across GitHub and Linear by triaging issues and pull requests, linking active work, and keeping GitHub public-facing while Line… |

### Meta: configuración, auditoría y gobierno del propio harness — 15 skills

Skills que se aplican a ECC mismo: instalación guiada, inventario, auditoría de skills, portabilidad entre harnesses y limpieza de configuración.

| Skill | Qué hace |
|---|---|
| [`configure-ecc`](https://github.com/affaan-m/ECC/blob/main/skills/configure-ecc/SKILL.md) | Run the conversational ECC setup wizard inside the current harness: inventory the install, collect scope (user/project/local) and hook mode (off/minim… |
| [`ecc-guide`](https://github.com/affaan-m/ECC/blob/main/skills/ecc-guide/SKILL.md) | Answer questions about ECC by reading the live repo surface — agents, skills, commands, hooks, rules, install profiles, and docs — instead of memory. |
| [`ecc-recipes`](https://github.com/affaan-m/ECC/blob/main/skills/ecc-recipes/SKILL.md) | Map a described workflow to the right ECC command group with run-order and stop condition, or browse all command-group recipe families read live from… |
| [`automation-audit-ops`](https://github.com/affaan-m/ECC/blob/main/skills/automation-audit-ops/SKILL.md) | Evidence-first automation inventory and overlap audit workflow for ECC. |
| [`workspace-surface-audit`](https://github.com/affaan-m/ECC/blob/main/skills/workspace-surface-audit/SKILL.md) | Audit the active repo, MCP servers, plugins, connectors, env surfaces, and harness setup, then recommend the highest-value ECC-native skills, hooks, a… |
| [`skill-comply`](https://github.com/affaan-m/ECC/blob/main/skills/skill-comply/SKILL.md) | Visualize whether skills, rules, and agent definitions are actually followed — auto-generates scenarios at 3 prompt strictness levels, runs agents, cl… |
| [`skill-host-compat`](https://github.com/affaan-m/ECC/blob/main/skills/skill-host-compat/SKILL.md) | Lint ECC skills for Codex/Cursor-safe frontmatter and Claude-only substitutions before a skill PR. |
| [`skill-scout`](https://github.com/affaan-m/ECC/blob/main/skills/skill-scout/SKILL.md) | Search existing local, marketplace, GitHub, and web skill sources before creating a new skill. |
| [`skill-stocktake`](https://github.com/affaan-m/ECC/blob/main/skills/skill-stocktake/SKILL.md) | Use when auditing Claude skills and commands for quality. Supports Quick Scan (changed skills only) and Full Stocktake modes with sequential subagent… |
| [`rules-distill`](https://github.com/affaan-m/ECC/blob/main/skills/rules-distill/SKILL.md) | Scan skills to extract cross-cutting principles and distill them into rules — append, revise, or create new rule files. |
| [`config-gc`](https://github.com/affaan-m/ECC/blob/main/skills/config-gc/SKILL.md) | Garbage collection for your Claude Code configuration. Periodically scans ~/.claude (skills, memory, hooks, permissions, MCP servers, caches) for redu… |
| [`ecc-tools-cost-audit`](https://github.com/affaan-m/ECC/blob/main/skills/ecc-tools-cost-audit/SKILL.md) | Evidence-first ECC Tools burn and billing audit workflow. Use when investigating runaway PR creation, quota bypass, premium-model leakage, duplicate j… |
| [`hermes-imports`](https://github.com/affaan-m/ECC/blob/main/skills/hermes-imports/SKILL.md) | Convert local Hermes operator workflows into sanitized ECC skills and release-pack artifacts. |
| [`hookify-rules`](https://github.com/affaan-m/ECC/blob/main/skills/hookify-rules/SKILL.md) | Create and configure hookify rules — markdown files with YAML frontmatter that match bash, file, prompt, or stop events by regex or conditions and sho… |
| [`opensource-pipeline`](https://github.com/affaan-m/ECC/blob/main/skills/opensource-pipeline/SKILL.md) | Open-source pipeline: fork, sanitize, and package private projects for safe public release. Chains 3 agents (forker, sanitizer, packager). |

### Calidad, testing y ciclo de desarrollo — 17 skills

TDD, estándares de código, revisión de commits e issues, E2E, regresión y puertas de entrega.

| Skill | Qué hace |
|---|---|
| [`tdd-workflow`](https://github.com/affaan-m/ECC/blob/main/skills/tdd-workflow/SKILL.md) | Test-driven development workflow: write a failing test first, watch it fail, implement the smallest change to green, then refactor with 80%+ coverage… |
| [`coding-standards`](https://github.com/affaan-m/ECC/blob/main/skills/coding-standards/SKILL.md) | Baseline cross-project coding conventions for naming, readability, immutability, and code-quality review. |
| [`conventional-commit-review`](https://github.com/affaan-m/ECC/blob/main/skills/conventional-commit-review/SKILL.md) | Reviews staged changes and drafts a Conventional Commits-compliant commit message with the right type, scope, and length. |
| [`git-workflow`](https://github.com/affaan-m/ECC/blob/main/skills/git-workflow/SKILL.md) | Git workflow patterns including branching strategies, commit conventions, keeping history clean and readable, tidying local commits before merging, me… |
| [`issue-review`](https://github.com/affaan-m/ECC/blob/main/skills/issue-review/SKILL.md) | Review a GitHub issue the way /code-review reviews a PR. Fetches the issue with the gh CLI, checks the report against the current codebase, searches f… |
| [`brownfield-retrospective`](https://github.com/affaan-m/ECC/blob/main/skills/brownfield-retrospective/SKILL.md) | Run the ECC engineering process retroactively against an existing project slice. |
| [`e2e-testing`](https://github.com/affaan-m/ECC/blob/main/skills/e2e-testing/SKILL.md) | Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies. |
| [`windows-desktop-e2e`](https://github.com/affaan-m/ECC/blob/main/skills/windows-desktop-e2e/SKILL.md) | E2E testing for Windows native desktop apps (WPF, WinForms, Win32/MFC, Qt) using pywinauto and Windows UI Automation. |
| [`ai-regression-testing`](https://github.com/affaan-m/ECC/blob/main/skills/ai-regression-testing/SKILL.md) | Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and… |
| [`test-collaboration`](https://github.com/affaan-m/ECC/blob/main/skills/test-collaboration/SKILL.md) | Inventory and govern a project's test assets. Connect requirements, business rules, risks, bugs, and cross-boundary contracts to stable TEST-IDs and e… |
| [`module-regression`](https://github.com/affaan-m/ECC/blob/main/skills/module-regression/SKILL.md) | Govern cross-module regression in large repositories with a REGRESSION.md ledger that records each module's downstream consumers and executable accept… |
| [`production-audit`](https://github.com/affaan-m/ECC/blob/main/skills/production-audit/SKILL.md) | Local-evidence production readiness audit for shipped apps, pre-launch reviews, post-merge checks, and "what breaks in prod?" questions without sendin… |
| [`plan-canvas`](https://github.com/affaan-m/ECC/blob/main/skills/plan-canvas/SKILL.md) | Open plans and HTML artifacts in a local browser canvas where the human annotates elements, chats, and approves or requests changes without leaving th… |
| [`intent-driven-development`](https://github.com/affaan-m/ECC/blob/main/skills/intent-driven-development/SKILL.md) | Turn ambiguous or high-impact product and engineering changes into scoped, verifiable acceptance criteria before or alongside implementation. |
| [`delivery-gate`](https://github.com/affaan-m/ECC/blob/main/skills/delivery-gate/SKILL.md) | Stop hook that blocks Claude from finishing until quality checks pass. |
| [`i18n-sync`](https://github.com/affaan-m/ECC/blob/main/skills/i18n-sync/SKILL.md) | Translate and synchronize application JSON locale files using source-key usage, project terminology, and focused validation. |
| [`plankton-code-quality`](https://github.com/affaan-m/ECC/blob/main/skills/plankton-code-quality/SKILL.md) | Write-time code quality enforcement using Plankton — auto-formatting, linting, and Claude-powered fixes on every file edit via hooks. |

### Seguridad — 14 skills

Endurecimiento de agentes, revisión de vulnerabilidades, caza de bugs de bounty, guardas contra operaciones destructivas y auditoría de la propia configuración.

| Skill | Qué hace |
|---|---|
| [`agent-security-hardening`](https://github.com/affaan-m/ECC/blob/main/skills/agent-security-hardening/SKILL.md) | Security hardening guidance for AI agent frameworks that process untrusted content, invoke tools, write workspace files, manage runtime identifiers, o… |
| [`defi-amm-security`](https://github.com/affaan-m/ECC/blob/main/skills/defi-amm-security/SKILL.md) | Security checklist for Solidity AMM contracts, liquidity pools, and swap flows. |
| [`django-security`](https://github.com/affaan-m/ECC/blob/main/skills/django-security/SKILL.md) | Django security best practices, authentication, authorization, CSRF protection, SQL injection prevention, XSS prevention, and secure deployment config… |
| [`gateguard`](https://github.com/affaan-m/ECC/blob/main/skills/gateguard/SKILL.md) | PreToolUse fact-forcing gate that denies the first Edit/Write/Bash (including MultiEdit and NotebookEdit) attempt until the agent presents concrete fa… |
| [`laravel-security`](https://github.com/affaan-m/ECC/blob/main/skills/laravel-security/SKILL.md) | Laravel security best practices — authentication, authorization, Eloquent safety, CSRF, XSS prevention, API security, and secure deployment configurat… |
| [`perl-security`](https://github.com/affaan-m/ECC/blob/main/skills/perl-security/SKILL.md) | Comprehensive Perl security covering taint mode, input validation, safe process execution, DBI parameterized queries, web security (XSS/SQLi/CSRF), an… |
| [`quarkus-security`](https://github.com/affaan-m/ECC/blob/main/skills/quarkus-security/SKILL.md) | Quarkus security implementation patterns: JWT and OIDC authentication, @RolesAllowed RBAC and SecurityIdentity checks, Bean Validation and custom vali… |
| [`repo-scan`](https://github.com/affaan-m/ECC/blob/main/skills/repo-scan/SKILL.md) | Bootstrap pointer that installs the external repo-scan skill from a pinned, reviewable commit. |
| [`safety-guard`](https://github.com/affaan-m/ECC/blob/main/skills/safety-guard/SKILL.md) | Guard against destructive operations with three modes: Careful intercepts dangerous commands (rm -rf, git push --force, DROP TABLE) for confirmation,… |
| [`security-bounty-hunter`](https://github.com/affaan-m/ECC/blob/main/skills/security-bounty-hunter/SKILL.md) | Hunt for exploitable, bounty-worthy security issues in repositories. |
| [`security-review`](https://github.com/affaan-m/ECC/blob/main/skills/security-review/SKILL.md) | Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive featur… |
| [`security-scan`](https://github.com/affaan-m/ECC/blob/main/skills/security-scan/SKILL.md) | Scan your Claude Code configuration (.claude/ directory) for security vulnerabilities, misconfigurations, and injection risks using AgentShield. |
| [`springboot-security`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-security/SKILL.md) | Spring Security best practices for authn/authz, validation, CSRF, secrets, headers, rate limiting, and dependency security in Java Spring Boot service… |
| [`llm-trading-agent-security`](https://github.com/affaan-m/ECC/blob/main/skills/llm-trading-agent-security/SKILL.md) | Security patterns for autonomous trading agents with wallet or transaction authority. |

### Lenguajes, frameworks y plataformas móviles — 64 skills

Packs por stack: patterns, testing, verificación y seguridad específicos de cada lenguaje o framework.

| Skill | Qué hace |
|---|---|
| [`android-clean-architecture`](https://github.com/affaan-m/ECC/blob/main/skills/android-clean-architecture/SKILL.md) | Clean Architecture patterns for Android and Kotlin Multiplatform projects — module structure, dependency rules, UseCases, Repositories, and data layer… |
| [`angular-developer`](https://github.com/affaan-m/ECC/blob/main/skills/angular-developer/SKILL.md) | Generates Angular code and provides architectural guidance. Trigger when creating projects, components, or services, or for best practices on reactivi… |
| [`bun-runtime`](https://github.com/affaan-m/ECC/blob/main/skills/bun-runtime/SKILL.md) | Bun as runtime, package manager, bundler, and test runner. When to choose Bun vs Node, migration notes, and Vercel support. |
| [`compose-multiplatform-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/compose-multiplatform-patterns/SKILL.md) | Compose Multiplatform and Jetpack Compose patterns for KMP projects — state management, navigation, theming, performance, and platform-specific UI. |
| [`cpp-coding-standards`](https://github.com/affaan-m/ECC/blob/main/skills/cpp-coding-standards/SKILL.md) | C++ coding standards based on the C++ Core Guidelines (isocpp.github.io). |
| [`cpp-testing`](https://github.com/affaan-m/ECC/blob/main/skills/cpp-testing/SKILL.md) | Use only when writing/updating/fixing C++ tests, configuring GoogleTest/CTest, diagnosing failing or flaky tests, or adding coverage/sanitizers. |
| [`csharp-testing`](https://github.com/affaan-m/ECC/blob/main/skills/csharp-testing/SKILL.md) | C# and .NET testing patterns with xUnit, FluentAssertions, mocking, integration tests, and test organization best practices. |
| [`dart-flutter-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/dart-flutter-patterns/SKILL.md) | Production-ready Dart and Flutter patterns covering null safety, immutable state with Freezed, async composition, widget architecture, state managemen… |
| [`django-celery`](https://github.com/affaan-m/ECC/blob/main/skills/django-celery/SKILL.md) | Django + Celery async task patterns — configuration, task design, beat scheduling, retries, canvas workflows, monitoring, and testing. |
| [`django-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/django-patterns/SKILL.md) | Django architecture patterns, REST API design with DRF, ORM best practices, caching, signals, middleware, and production-grade Django apps. |
| [`django-tdd`](https://github.com/affaan-m/ECC/blob/main/skills/django-tdd/SKILL.md) | Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs. |
| [`django-verification`](https://github.com/affaan-m/ECC/blob/main/skills/django-verification/SKILL.md) | Run the full Django verification loop — environment check, mypy/ruff/black linting, migration safety, pytest with coverage targets, pip-audit and band… |
| [`dotnet-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/dotnet-patterns/SKILL.md) | Idiomatic C# and .NET patterns, conventions, dependency injection, async/await, and best practices for building robust, maintainable .NET applications… |
| [`fastapi-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/fastapi-patterns/SKILL.md) | FastAPI best practices covering project structure, Pydantic v2 schemas, dependency injection, async handlers, authentication, authorization, transacti… |
| [`flutter-dart-code-review`](https://github.com/affaan-m/ECC/blob/main/skills/flutter-dart-code-review/SKILL.md) | Library-agnostic Flutter/Dart code review checklist covering widget best practices, state management patterns (BLoC, Riverpod, Provider, GetX, MobX, S… |
| [`foundation-models-on-device`](https://github.com/affaan-m/ECC/blob/main/skills/foundation-models-on-device/SKILL.md) | Apple FoundationModels framework for on-device LLM — text generation, guided generation with @Generable, tool calling, and snapshot streaming in iOS 2… |
| [`fsharp-testing`](https://github.com/affaan-m/ECC/blob/main/skills/fsharp-testing/SKILL.md) | F# testing patterns with xUnit, FsUnit, Unquote, FsCheck property-based testing, integration tests, and test organization best practices. |
| [`generating-python-installer`](https://github.com/affaan-m/ECC/blob/main/skills/generating-python-installer/SKILL.md) | Commercial-grade Python installer expert for Windows: Nuitka extreme compilation, dist slimming, DLL footprint analysis, and Inno Setup packaging to s… |
| [`golang-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/golang-patterns/SKILL.md) | Idiomatic Go patterns, best practices, and conventions for building robust, efficient, and maintainable Go applications. |
| [`golang-testing`](https://github.com/affaan-m/ECC/blob/main/skills/golang-testing/SKILL.md) | Go testing patterns including table-driven tests, subtests, benchmarks, fuzzing, and test coverage. |
| [`ios-icon-gen`](https://github.com/affaan-m/ECC/blob/main/skills/ios-icon-gen/SKILL.md) | Generate iOS app icons as PNG imagesets for Xcode asset catalogs from SF Symbols (5000+ Apple-native) or Iconify API (275k+ open source icons from 200… |
| [`java-coding-standards`](https://github.com/affaan-m/ECC/blob/main/skills/java-coding-standards/SKILL.md) | Java coding standards for Spring Boot and Quarkus services: naming, immutability, Optional usage, streams, exceptions, generics, CDI, reactive pattern… |
| [`jpa-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/jpa-patterns/SKILL.md) | JPA/Hibernate patterns for entity design, relationships, query optimization, transactions, auditing, indexing, pagination, and pooling in Spring Boot.… |
| [`kotlin-coroutines-flows`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-coroutines-flows/SKILL.md) | Kotlin Coroutines and Flow patterns for Android and KMP — structured concurrency, Flow operators, StateFlow, error handling, and testing. |
| [`kotlin-exposed-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-exposed-patterns/SKILL.md) | JetBrains Exposed ORM patterns including DSL queries, DAO pattern, transactions, HikariCP connection pooling, Flyway migrations, and repository patter… |
| [`kotlin-ktor-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-ktor-patterns/SKILL.md) | Ktor server patterns including routing DSL, plugins, authentication, Koin DI, kotlinx.serialization, WebSockets, and testApplication testing. |
| [`kotlin-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-patterns/SKILL.md) | Idiomatic Kotlin patterns, best practices, and conventions for building robust, efficient, and maintainable Kotlin applications with coroutines, null… |
| [`kotlin-testing`](https://github.com/affaan-m/ECC/blob/main/skills/kotlin-testing/SKILL.md) | Kotlin testing patterns with Kotest, MockK, coroutine testing, property-based testing, and Kover coverage. |
| [`laravel-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/laravel-patterns/SKILL.md) | Laravel architecture patterns, routing/controllers, Eloquent ORM, service layers, queues, events, caching, and API resources for production apps. |
| [`laravel-plugin-discovery`](https://github.com/affaan-m/ECC/blob/main/skills/laravel-plugin-discovery/SKILL.md) | Discover and evaluate Laravel packages via LaraPlugins.io MCP. |
| [`laravel-tdd`](https://github.com/affaan-m/ECC/blob/main/skills/laravel-tdd/SKILL.md) | Laravel testing strategies with PHPUnit, Pest, model factories, HTTP tests, Sanctum authentication testing, mocking, and coverage. |
| [`laravel-verification`](https://github.com/affaan-m/ECC/blob/main/skills/laravel-verification/SKILL.md) | Verification loop for Laravel projects: env checks, linting, static analysis, tests with coverage, security scans, and deployment readiness. |
| [`mybatis-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/mybatis-patterns/SKILL.md) | MyBatis and MyBatis-Spring patterns for mapper design, XML and annotation SQL, result mapping, dynamic SQL safety, transactions, batching, pagination,… |
| [`nestjs-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/nestjs-patterns/SKILL.md) | NestJS architecture patterns for modules, controllers, providers, DTO validation, guards, interceptors, config, and production-grade TypeScript backen… |
| [`nextjs-turbopack`](https://github.com/affaan-m/ECC/blob/main/skills/nextjs-turbopack/SKILL.md) | Next.js 16+ and Turbopack guidance — incremental Rust bundling, file-system caching, faster dev startup and HMR, Turbopack vs webpack tradeoffs, and t… |
| [`perl-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/perl-patterns/SKILL.md) | Modern Perl 5.36+ idioms, best practices, and conventions for building robust, maintainable Perl applications. |
| [`perl-testing`](https://github.com/affaan-m/ECC/blob/main/skills/perl-testing/SKILL.md) | Perl testing patterns using Test2::V0, Test::More, prove runner, mocking, coverage with Devel::Cover, and TDD methodology. |
| [`prisma-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/prisma-patterns/SKILL.md) | Prisma ORM patterns for TypeScript backends — schema design, query optimization, transactions, pagination, and critical traps like updateMany returnin… |
| [`python-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/python-patterns/SKILL.md) | Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications. |
| [`python-testing`](https://github.com/affaan-m/ECC/blob/main/skills/python-testing/SKILL.md) | Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements. |
| [`pytorch-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/pytorch-patterns/SKILL.md) | PyTorch deep learning patterns and best practices for building robust, efficient, and reproducible training pipelines, model architectures, and data l… |
| [`quarkus-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/quarkus-patterns/SKILL.md) | Quarkus 3.x LTS architecture patterns with Camel for messaging, RESTful API design, CDI services, data access with Panache, and async processing. |
| [`quarkus-tdd`](https://github.com/affaan-m/ECC/blob/main/skills/quarkus-tdd/SKILL.md) | Test-driven development for Quarkus 3.x LTS using JUnit 5, Mockito, REST Assured, Camel testing, and JaCoCo. |
| [`quarkus-verification`](https://github.com/affaan-m/ECC/blob/main/skills/quarkus-verification/SKILL.md) | Verification loop for Quarkus projects: build, static analysis (Checkstyle, PMD, SpotBugs), tests with JaCoCo coverage, OWASP dependency and container… |
| [`rails-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/rails-patterns/SKILL.md) | Ruby on Rails framework patterns for Rails 7.1+ and 8.x apps. Covers the directory contract, skinny controllers with service objects, form objects, qu… |
| [`react-native-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/react-native-patterns/SKILL.md) | React Native and Expo app patterns — Expo Router navigation, state separation (server/client/route/form), TanStack Query data fetching with Zod, perfo… |
| [`react-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/react-patterns/SKILL.md) | React 18/19 patterns including hooks discipline, server/client component boundaries, Suspense + error boundaries, form actions, data fetching, state m… |
| [`react-performance`](https://github.com/affaan-m/ECC/blob/main/skills/react-performance/SKILL.md) | React and Next.js performance optimization patterns adapted from Vercel Engineering's React Best Practices (https://github.com/vercel-labs/agent-skill… |
| [`react-testing`](https://github.com/affaan-m/ECC/blob/main/skills/react-testing/SKILL.md) | React component testing with React Testing Library, Vitest/Jest, MSW for network mocking, accessibility assertions with axe, and the decision boundary… |
| [`rust-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/rust-patterns/SKILL.md) | Idiomatic Rust patterns, ownership, error handling, traits, concurrency, and best practices for building safe, performant applications. |
| [`rust-testing`](https://github.com/affaan-m/ECC/blob/main/skills/rust-testing/SKILL.md) | Rust testing patterns including unit tests, integration tests, async testing, property-based testing, mocking, and coverage. Follows TDD methodology. |
| [`springboot-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-patterns/SKILL.md) | Spring Boot architecture patterns, REST API design, layered services, data access, caching, async processing, and logging. |
| [`springboot-tdd`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-tdd/SKILL.md) | Test-driven development for Spring Boot using JUnit 5, Mockito, MockMvc, Testcontainers, and JaCoCo. |
| [`springboot-verification`](https://github.com/affaan-m/ECC/blob/main/skills/springboot-verification/SKILL.md) | Run the full Spring Boot verification loop — Maven or Gradle build, SpotBugs, PMD, and Checkstyle static analysis, unit and Testcontainers integration… |
| [`swift-actor-persistence`](https://github.com/affaan-m/ECC/blob/main/skills/swift-actor-persistence/SKILL.md) | Thread-safe data persistence in Swift using actors — in-memory cache with file-backed storage, eliminating data races by design. |
| [`swift-concurrency-6-2`](https://github.com/affaan-m/ECC/blob/main/skills/swift-concurrency-6-2/SKILL.md) | Swift 6.2 Approachable Concurrency — single-threaded by default, @concurrent for explicit background offloading, isolated conformances for main actor… |
| [`swift-protocol-di-testing`](https://github.com/affaan-m/ECC/blob/main/skills/swift-protocol-di-testing/SKILL.md) | Protocol-based dependency injection for testable Swift code — mock file system, network, and external APIs using focused protocols and Swift Testing. |
| [`swiftui-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/swiftui-patterns/SKILL.md) | SwiftUI architecture patterns, state management with @Observable, view composition, navigation, performance optimization, and modern iOS/macOS UI best… |
| [`tinystruct-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/tinystruct-patterns/SKILL.md) | Expert guidance for developing with the tinystruct Java framework. |
| [`typescript-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/typescript-patterns/SKILL.md) | TypeScript patterns for strict, type-safe, maintainable code in modern TypeScript and JavaScript applications. |
| [`vite-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/vite-patterns/SKILL.md) | Vite build tool patterns including config, plugins, HMR, env variables, proxy setup, SSR, library mode, dependency pre-bundling, and build optimizatio… |
| [`vue-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/vue-patterns/SKILL.md) | Vue.js 3 Composition API patterns, component architecture, reactivity best practices, Pinia state management, Vue Router navigation, and Nuxt SSR patt… |
| [`nuxt4-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/nuxt4-patterns/SKILL.md) | Nuxt 4 app patterns for hydration safety, performance, route rules, lazy loading, and SSR-safe data fetching with useFetch and useAsyncData. |
| [`bengali-nlp`](https://github.com/affaan-m/ECC/blob/main/skills/bengali-nlp/SKILL.md) | Bengali (Bangla) text processing patterns including Unicode normalization, script detection, tokenization, conjunct handling, and Bangla-specific NLP… |

### Backend, datos e infraestructura — 28 skills

APIs, bases de datos, caché, migraciones, Docker/despliegue, MCP servers y tuberías de datos/ML.

| Skill | Qué hace |
|---|---|
| [`api-connector-builder`](https://github.com/affaan-m/ECC/blob/main/skills/api-connector-builder/SKILL.md) | Build a new API connector or provider by matching the target repo's existing integration pattern exactly. |
| [`api-design`](https://github.com/affaan-m/ECC/blob/main/skills/api-design/SKILL.md) | REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production… |
| [`backend-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/backend-patterns/SKILL.md) | Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.js API routes. |
| [`clickhouse-io`](https://github.com/affaan-m/ECC/blob/main/skills/clickhouse-io/SKILL.md) | ClickHouse database patterns, query optimization, analytics, and data engineering best practices for high-performance analytical workloads. |
| [`codehealth-mcp`](https://github.com/affaan-m/ECC/blob/main/skills/codehealth-mcp/SKILL.md) | Real-time structural Code Health via CodeScene MCP — review before edits, verify score deltas after changes, gate commits and PRs. |
| [`content-hash-cache-pattern`](https://github.com/affaan-m/ECC/blob/main/skills/content-hash-cache-pattern/SKILL.md) | Cache expensive file processing results using SHA-256 content hashes — path-independent, auto-invalidating, with service layer separation. |
| [`dashboard-builder`](https://github.com/affaan-m/ECC/blob/main/skills/dashboard-builder/SKILL.md) | Build monitoring dashboards that answer real operator questions for Grafana, SigNoz, and similar platforms. |
| [`data-throughput-accelerator`](https://github.com/affaan-m/ECC/blob/main/skills/data-throughput-accelerator/SKILL.md) | Diagnose and accelerate large data movement — ingestion, backfill, export, ETL, warehouse loading, manifest catch-up, and table synchronization — by i… |
| [`database-migrations`](https://github.com/affaan-m/ECC/blob/main/skills/database-migrations/SKILL.md) | Safe, reversible database migration patterns: forward-only production changes, expand-contract zero-downtime renames, concurrent indexes, batched back… |
| [`deployment-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/deployment-patterns/SKILL.md) | Deployment workflows, CI/CD pipeline patterns, Docker containerization, health checks, rollback strategies, and production readiness checklists for we… |
| [`docker-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/docker-patterns/SKILL.md) | Docker and Docker Compose patterns for local development, hardened CLI installer harnesses, container security, networking, volumes, and multi-service… |
| [`mysql-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/mysql-patterns/SKILL.md) | MySQL and MariaDB schema, query, indexing, transaction, replication, and connection-pool patterns for production backends. |
| [`postgres-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/postgres-patterns/SKILL.md) | PostgreSQL database patterns for query optimization, schema design, indexing, and security. Based on Supabase best practices. |
| [`redis-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/redis-patterns/SKILL.md) | Redis data structure patterns, caching strategies, distributed locks, rate limiting, pub/sub, and connection management for production applications. |
| [`uncloud`](https://github.com/affaan-m/ECC/blob/main/skills/uncloud/SKILL.md) | Use when managing an Uncloud cluster — deploying services, configuring Caddy ingress, adding static proxy routes for non-cluster devices, publishing p… |
| [`kubernetes-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/kubernetes-patterns/SKILL.md) | Kubernetes workload patterns, resource management, RBAC, probes, autoscaling, ConfigMap/Secret handling, and kubectl debugging for production-grade de… |
| [`mcp-server-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/mcp-server-patterns/SKILL.md) | Build MCP servers with Node/TypeScript SDK — tools, resources, prompts, Zod validation, stdio vs Streamable HTTP. |
| [`mcp-dependency-review`](https://github.com/affaan-m/ECC/blob/main/skills/mcp-dependency-review/SKILL.md) | Statically review MCP configuration for mutable package references before approval or CI, without executing discovered MCP servers. |
| [`canary-watch`](https://github.com/affaan-m/ECC/blob/main/skills/canary-watch/SKILL.md) | Use this skill to monitor and verify a deployed URL after releases — checks HTTP endpoints, SSE streams, static assets, console errors, and performanc… |
| [`latency-critical-systems`](https://github.com/affaan-m/ECC/blob/main/skills/latency-critical-systems/SKILL.md) | Optimize and verify latency-sensitive systems — realtime dashboards, market data feeds, streaming agents, execution gateways, queues, and caches — by… |
| [`flox-environments`](https://github.com/affaan-m/ECC/blob/main/skills/flox-environments/SKILL.md) | Create reproducible, cross-platform (macOS/Linux) development environments with Flox, a declarative Nix-based environment manager. |
| [`error-handling`](https://github.com/affaan-m/ECC/blob/main/skills/error-handling/SKILL.md) | Patterns for robust error handling across TypeScript, Python, and Go. |
| [`hexagonal-architecture`](https://github.com/affaan-m/ECC/blob/main/skills/hexagonal-architecture/SKILL.md) | Design, implement, and refactor Ports & Adapters systems with clear domain boundaries, dependency inversion, and testable use-case orchestration acros… |
| [`recsys-pipeline-architect`](https://github.com/affaan-m/ECC/blob/main/skills/recsys-pipeline-architect/SKILL.md) | Design composable recommendation, ranking, and feed pipelines using the six-stage Source→Hydrator→Filter→Scorer→Selector→SideEffect framework populari… |
| [`mle-workflow`](https://github.com/affaan-m/ECC/blob/main/skills/mle-workflow/SKILL.md) | Production machine-learning engineering workflow for data contracts, reproducible training, model evaluation, deployment, monitoring, and rollback. |
| [`ml-adoption-playbook`](https://github.com/affaan-m/ECC/blob/main/skills/ml-adoption-playbook/SKILL.md) | End-to-end methodology for AI agents and software engineers to add machine learning algorithms to existing non-ML codebases. |
| [`regex-vs-llm-structured-text`](https://github.com/affaan-m/ECC/blob/main/skills/regex-vs-llm-structured-text/SKILL.md) | Decision framework for parsing structured text (quizzes, forms, invoices, receipts, tables) with a hybrid regex-first pipeline — regex extraction hand… |
| [`nasiko-control-plane`](https://github.com/affaan-m/ECC/blob/main/skills/nasiko-control-plane/SKILL.md) | Manage the experimental Nasiko CLI lifecycle through ECC — read-only status checks, consent-gated install of the pinned qualified version with dry-run… |

### Redes, homelab y operaciones de infra — 10 skills

Diseño y diagnóstico de red, automatización SSH, VPN y segmentación VLAN.

| Skill | Qué hace |
|---|---|
| [`cisco-ios-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/cisco-ios-patterns/SKILL.md) | Cisco IOS and IOS-XE review patterns for show commands, config hierarchy, wildcard masks, ACL placement, interface hygiene, and safe change-window ver… |
| [`homelab-network-readiness`](https://github.com/affaan-m/ECC/blob/main/skills/homelab-network-readiness/SKILL.md) | Readiness checklist for homelab VLAN segmentation, local DNS filtering (Pi-hole, AdGuard Home), and WireGuard-style remote access. |
| [`homelab-network-setup`](https://github.com/affaan-m/ECC/blob/main/skills/homelab-network-setup/SKILL.md) | Practical home and homelab network planning for gateways, switches, access points, IP ranges, DHCP reservations, DNS, cabling, and common beginner mis… |
| [`homelab-pihole-dns`](https://github.com/affaan-m/ECC/blob/main/skills/homelab-pihole-dns/SKILL.md) | Pi-hole installation, blocklist management, DNS-over-HTTPS setup, DHCP integration, local DNS records, and troubleshooting broken DNS resolution on a… |
| [`homelab-vlan-segmentation`](https://github.com/affaan-m/ECC/blob/main/skills/homelab-vlan-segmentation/SKILL.md) | Segmenting home networks into VLANs for IoT, guest, trusted, and server traffic using UniFi, pfSense/OPNsense, and MikroTik — including switch trunk c… |
| [`homelab-wireguard-vpn`](https://github.com/affaan-m/ECC/blob/main/skills/homelab-wireguard-vpn/SKILL.md) | WireGuard VPN server setup, peer configuration, key generation, split tunneling vs full tunnel routing, and remote access to a home network from mobil… |
| [`network-bgp-diagnostics`](https://github.com/affaan-m/ECC/blob/main/skills/network-bgp-diagnostics/SKILL.md) | Diagnostics-only BGP troubleshooting patterns for neighbor state, route exchange, prefix policy, AS path inspection, and safe evidence collection. |
| [`network-config-validation`](https://github.com/affaan-m/ECC/blob/main/skills/network-config-validation/SKILL.md) | Pre-deployment checks for router and switch configuration, including dangerous commands, duplicate addresses, subnet overlaps, stale references, manag… |
| [`network-interface-health`](https://github.com/affaan-m/ECC/blob/main/skills/network-interface-health/SKILL.md) | Diagnose interface errors, drops, CRCs, duplex mismatches, flapping, speed negotiation issues, and counter trends on routers, switches, and Linux host… |
| [`netmiko-ssh-automation`](https://github.com/affaan-m/ECC/blob/main/skills/netmiko-ssh-automation/SKILL.md) | Safe Python Netmiko patterns for read-only collection, bounded batch SSH, TextFSM parsing, guarded config changes, timeouts, and network automation er… |

### Investigación, documentación y contexto — 31 skills

Investigación con fuentes, OSINT, literatura científica, ADRs, onboarding de codebase y memoria compartida entre harnesses.

| Skill | Qué hace |
|---|---|
| [`research-ops`](https://github.com/affaan-m/ECC/blob/main/skills/research-ops/SKILL.md) | Evidence-first current-state research workflow for ECC. Use when the user wants fresh facts, comparisons, enrichment, or a recommendation built from c… |
| [`deep-research`](https://github.com/affaan-m/ECC/blob/main/skills/deep-research/SKILL.md) | Produce cited research reports from multiple web sources using firecrawl and exa MCP tools — plan sub-questions, search and deep-read sources, then sy… |
| [`osint-investigation`](https://github.com/affaan-m/ECC/blob/main/skills/osint-investigation/SKILL.md) | Sparse-clue OSINT investigation methodology for extracting overlooked leads, connecting fragmented evidence, and testing explanations across sources. |
| [`market-research`](https://github.com/affaan-m/ECC/blob/main/skills/market-research/SKILL.md) | Conduct market research, competitive analysis, investor due diligence, and industry intelligence with source attribution and decision-oriented summari… |
| [`benchmark`](https://github.com/affaan-m/ECC/blob/main/skills/benchmark/SKILL.md) | Measure performance baselines and detect regressions across browser Core Web Vitals (LCP, INP, CLS, page weight), API endpoint latency percentiles, an… |
| [`benchmark-methodology`](https://github.com/affaan-m/ECC/blob/main/skills/benchmark-methodology/SKILL.md) | Score a scoped competitor set into comparable profile cards: nine weighted dimensions (positioning, voice, visual craft, offer packaging, evidence, en… |
| [`competitive-platform-analysis`](https://github.com/affaan-m/ECC/blob/main/skills/competitive-platform-analysis/SKILL.md) | Use when scoping a competitive landscape — identifying, categorising, and score-filtering a competitor set before any benchmarking begins. |
| [`competitive-report-structure`](https://github.com/affaan-m/ECC/blob/main/skills/competitive-report-structure/SKILL.md) | Assemble scored competitor profile cards (from benchmark-methodology) into a decision-grade competitive report with landscape map, competitor tiers, b… |
| [`scientific-db-pubmed-database`](https://github.com/affaan-m/ECC/blob/main/skills/scientific-db-pubmed-database/SKILL.md) | Direct PubMed and NCBI E-utilities search workflows for biomedical literature, MeSH queries, PMID lookup, citation retrieval, and API-backed literatur… |
| [`scientific-db-uspto-database`](https://github.com/affaan-m/ECC/blob/main/skills/scientific-db-uspto-database/SKILL.md) | USPTO patent and trademark data workflow for official record lookup, PatentSearch queries, TSDR checks, assignment data, and reproducible IP research… |
| [`scientific-pkg-gget`](https://github.com/affaan-m/ECC/blob/main/skills/scientific-pkg-gget/SKILL.md) | gget CLI and Python workflow for quick genomic database queries, sequence lookup, BLAST-style searches, enrichment checks, and reproducible bioinforma… |
| [`scientific-thinking-literature-review`](https://github.com/affaan-m/ECC/blob/main/skills/scientific-thinking-literature-review/SKILL.md) | Systematic literature-review workflow for academic, biomedical, technical, and scientific topics, including search planning, source screening, synthes… |
| [`scientific-thinking-scholar-evaluation`](https://github.com/affaan-m/ECC/blob/main/skills/scientific-thinking-scholar-evaluation/SKILL.md) | Structured scholarly-work evaluation for papers, proposals, literature reviews, methods sections, evidence quality, citation support, and research-wri… |
| [`search-first`](https://github.com/affaan-m/ECC/blob/main/skills/search-first/SKILL.md) | Research-before-coding workflow: search npm/PyPI, MCP servers, skills, and GitHub for existing tools before writing custom code, then adopt, extend, o… |
| [`documentation-lookup`](https://github.com/affaan-m/ECC/blob/main/skills/documentation-lookup/SKILL.md) | Use up-to-date library and framework docs via Context7 MCP instead of training data. |
| [`docs-governance`](https://github.com/affaan-m/ECC/blob/main/skills/docs-governance/SKILL.md) | Route broad documentation-governance requests to existing ECC skills and run an opt-in, read-only audit of mapped documentation roles, links, ADR inde… |
| [`living-docs-governance`](https://github.com/affaan-m/ECC/blob/main/skills/living-docs-governance/SKILL.md) | Keep a long-lived project's documentation from rotting by assigning existing project docs clear constitution, map, status, and history roles, then wir… |
| [`context-and-decisions`](https://github.com/affaan-m/ECC/blob/main/skills/context-and-decisions/SKILL.md) | Govern stable domain context with a narrowly scoped CONTEXT.md when needed, and route hard-to-reverse decisions to ECC's existing architecture-decisio… |
| [`change-impact`](https://github.com/affaan-m/ECC/blob/main/skills/change-impact/SKILL.md) | Perform evidence-backed impact analysis before changing code, data, interfaces, or governance documents, then compare the planned impact with the actu… |
| [`architecture-decision-records`](https://github.com/affaan-m/ECC/blob/main/skills/architecture-decision-records/SKILL.md) | Capture architectural decisions as numbered ADR markdown files in docs/adr/ with context, alternatives considered, consequences, and an index README. |
| [`code-tour`](https://github.com/affaan-m/ECC/blob/main/skills/code-tour/SKILL.md) | Create CodeTour `.tour` files — persona-targeted, step-by-step walkthroughs with real file and line anchors. |
| [`codebase-onboarding`](https://github.com/affaan-m/ECC/blob/main/skills/codebase-onboarding/SKILL.md) | Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and a starter CLAUDE.m… |
| [`module-governance`](https://github.com/affaan-m/ECC/blob/main/skills/module-governance/SKILL.md) | Establish or maintain a business module's local agent instructions, domain-context links, and interface ownership when implementing a new module or ch… |
| [`unified-memory`](https://github.com/affaan-m/ECC/blob/main/skills/unified-memory/SKILL.md) | Share durable, inspectable context and handoffs between Claude, Codex, Hermes, Cursor, OpenCode, and other agents through the local ECC Memory Vault. |
| [`ck`](https://github.com/affaan-m/ECC/blob/main/skills/ck/SKILL.md) | Persistent per-project memory for Claude Code (Context Keeper) driven by deterministic Node.js /ck commands: init, save, resume, info, list, forget, a… |
| [`iterative-retrieval`](https://github.com/affaan-m/ECC/blob/main/skills/iterative-retrieval/SKILL.md) | Pattern for progressively refining context retrieval to solve the subagent context problem. |
| [`exa-search`](https://github.com/affaan-m/ECC/blob/main/skills/exa-search/SKILL.md) | Neural search via Exa MCP for web, code, and company research. |
| [`data-scraper-agent`](https://github.com/affaan-m/ECC/blob/main/skills/data-scraper-agent/SKILL.md) | Build a fully automated AI-powered data collection agent for any public source — job boards, prices, news, GitHub, sports, anything. |
| [`visa-doc-translate`](https://github.com/affaan-m/ECC/blob/main/skills/visa-doc-translate/SKILL.md) | Translate visa document images (bank deposit, employment, income, and retirement certificates; |
| [`nutrient-document-processing`](https://github.com/affaan-m/ECC/blob/main/skills/nutrient-document-processing/SKILL.md) | Process, convert, OCR, extract, redact, sign, and fill documents using the Nutrient DWS API. Works with PDFs, DOCX, XLSX, PPTX, HTML, and images. |
| [`lead-intelligence`](https://github.com/affaan-m/ECC/blob/main/skills/lead-intelligence/SKILL.md) | AI-native lead intelligence and outreach pipeline. Replaces Apollo, Clay, and ZoomInfo with agent-powered signal scoring, mutual ranking, warm path di… |

### Negocio, contenido, marketing y dominios verticales — 49 skills

Escritura de largo formato, marca, SEO, distribución social, inversión, y skills de dominio muy específicas (logística, aduanas, salud, energy, prediction markets).

| Skill | Qué hace |
|---|---|
| [`article-writing`](https://github.com/affaan-m/ECC/blob/main/skills/article-writing/SKILL.md) | Write articles, guides, blog posts, tutorials, newsletter issues, and other long-form content in a distinctive voice derived from supplied examples or… |
| [`brand-discovery`](https://github.com/affaan-m/ECC/blob/main/skills/brand-discovery/SKILL.md) | Run a structured, resumable multi-session brand identity interview across 8 modules (purpose, positioning, audience, personality, voice, narrative, fo… |
| [`brand-voice`](https://github.com/affaan-m/ECC/blob/main/skills/brand-voice/SKILL.md) | Build a source-derived writing style profile from real posts, essays, launch notes, docs, or site copy, then reuse that profile across content, outrea… |
| [`carrier-relationship-management`](https://github.com/affaan-m/ECC/blob/main/skills/carrier-relationship-management/SKILL.md) | Manage truckload, LTL, and intermodal carrier portfolios: sourcing and FMCSA vetting, freight rate and fuel-surcharge negotiation, RFPs and routing gu… |
| [`connections-optimizer`](https://github.com/affaan-m/ECC/blob/main/skills/connections-optimizer/SKILL.md) | Reorganize the user's X and LinkedIn network with review-first pruning, add/follow recommendations, and channel-specific warm outreach drafted in the… |
| [`content-engine`](https://github.com/affaan-m/ECC/blob/main/skills/content-engine/SKILL.md) | Create platform-native content systems for X, LinkedIn, TikTok, YouTube, newsletters, and repurposed multi-platform campaigns. |
| [`crosspost`](https://github.com/affaan-m/ECC/blob/main/skills/crosspost/SKILL.md) | Multi-platform content distribution across X, LinkedIn, Threads, and Bluesky. Adapts content per platform using content-engine patterns. |
| [`customer-billing-ops`](https://github.com/affaan-m/ECC/blob/main/skills/customer-billing-ops/SKILL.md) | Operate customer billing workflows such as subscriptions, refunds, churn triage, billing-portal recovery, and plan analysis using connected billing to… |
| [`customs-trade-compliance`](https://github.com/affaan-m/ECC/blob/main/skills/customs-trade-compliance/SKILL.md) | Codified customs and trade compliance expertise — HS/HTS tariff classification with GRI rules, commercial invoices and entry documentation, Incoterms… |
| [`email-ops`](https://github.com/affaan-m/ECC/blob/main/skills/email-ops/SKILL.md) | Evidence-first mailbox triage, drafting, send verification, and sent-mail-safe follow-up workflow for ECC. |
| [`energy-procurement`](https://github.com/affaan-m/ECC/blob/main/skills/energy-procurement/SKILL.md) | Procure electricity and natural gas for commercial and industrial facilities: tariff and rate-schedule optimization, demand-charge mitigation, supplie… |
| [`finance-billing-ops`](https://github.com/affaan-m/ECC/blob/main/skills/finance-billing-ops/SKILL.md) | Evidence-first revenue, pricing, refunds, team-billing, and billing-model truth workflow for ECC. |
| [`github-ops`](https://github.com/affaan-m/ECC/blob/main/skills/github-ops/SKILL.md) | GitHub repository operations, automation, and management. Issue triage, PR management, CI/CD operations, release management, and security monitoring u… |
| [`google-workspace-ops`](https://github.com/affaan-m/ECC/blob/main/skills/google-workspace-ops/SKILL.md) | Operate across Google Drive, Docs, Sheets, and Slides as one workflow surface for plans, trackers, decks, and shared documents. |
| [`healthcare-cdss-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/healthcare-cdss-patterns/SKILL.md) | Clinical Decision Support System (CDSS) development patterns. Drug interaction checking, dose validation, clinical scoring (NEWS2, qSOFA), alert sever… |
| [`healthcare-emr-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/healthcare-emr-patterns/SKILL.md) | EMR/EHR development patterns for healthcare applications. Clinical safety, encounter workflows, prescription generation, clinical decision support int… |
| [`healthcare-phi-compliance`](https://github.com/affaan-m/ECC/blob/main/skills/healthcare-phi-compliance/SKILL.md) | Protected Health Information (PHI) and PII compliance patterns for healthcare applications: data classification, row-level access control, tamper-proo… |
| [`hipaa-compliance`](https://github.com/affaan-m/ECC/blob/main/skills/hipaa-compliance/SKILL.md) | HIPAA-specific entrypoint for healthcare privacy and security work. |
| [`investor-materials`](https://github.com/affaan-m/ECC/blob/main/skills/investor-materials/SKILL.md) | Create and update pitch decks, one-pagers, investor memos, accelerator applications, financial models, and fundraising materials. |
| [`investor-outreach`](https://github.com/affaan-m/ECC/blob/main/skills/investor-outreach/SKILL.md) | Draft cold emails, warm intro blurbs, follow-ups, update emails, and investor communications for fundraising. |
| [`knowledge-ops`](https://github.com/affaan-m/ECC/blob/main/skills/knowledge-ops/SKILL.md) | Knowledge base management, ingestion, sync, and retrieval across multiple storage layers (local files, MCP memory, vector stores, Git repos). |
| [`marketing-campaign`](https://github.com/affaan-m/ECC/blob/main/skills/marketing-campaign/SKILL.md) | End-to-end marketing campaign planning and execution. Covers audience research, positioning, campaign angle definition, landing page copy, email seque… |
| [`messages-ops`](https://github.com/affaan-m/ECC/blob/main/skills/messages-ops/SKILL.md) | Evidence-first live messaging workflow for ECC. Use when the user wants to read texts or DMs, recover a recent one-time code, inspect a thread before… |
| [`returns-reverse-logistics`](https://github.com/affaan-m/ECC/blob/main/skills/returns-reverse-logistics/SKILL.md) | Codified expertise for returns authorization, receipt and inspection, disposition decisions, refund processing, fraud detection, and warranty claims m… |
| [`seo`](https://github.com/affaan-m/ECC/blob/main/skills/seo/SKILL.md) | Audit, plan, and implement SEO improvements across technical SEO, on-page optimization, structured data, Core Web Vitals, and content strategy. |
| [`social-graph-ranker`](https://github.com/affaan-m/ECC/blob/main/skills/social-graph-ranker/SKILL.md) | Weighted social-graph ranking for warm intro discovery, bridge scoring, and network gap analysis across X and LinkedIn. |
| [`social-publisher`](https://github.com/affaan-m/ECC/blob/main/skills/social-publisher/SKILL.md) | Agent-driven scheduling and publishing of social media posts across 13 platforms via SocialClaw. |
| [`terminal-ops`](https://github.com/affaan-m/ECC/blob/main/skills/terminal-ops/SKILL.md) | Evidence-first repo execution workflow for ECC. Use when the user wants a command run, a repo checked, a CI failure debugged, or a narrow fix pushed w… |
| [`unified-notifications-ops`](https://github.com/affaan-m/ECC/blob/main/skills/unified-notifications-ops/SKILL.md) | Operate notifications as one ECC-native workflow across GitHub, Linear, desktop alerts, hooks, and connected communication surfaces. |
| [`x-api`](https://github.com/affaan-m/ECC/blob/main/skills/x-api/SKILL.md) | X/Twitter API integration for posting tweets, threads, reading timelines, search, and analytics. |
| [`jira-integration`](https://github.com/affaan-m/ECC/blob/main/skills/jira-integration/SKILL.md) | Use this skill when retrieving Jira tickets, analyzing requirements, updating ticket status, adding comments, or transitioning issues. |
| [`inventory-demand-planning`](https://github.com/affaan-m/ECC/blob/main/skills/inventory-demand-planning/SKILL.md) | Codified demand planning expertise for multi-location retailers: demand forecasting method selection, ABC/XYZ segmentation, safety stock and reorder-p… |
| [`logistics-exception-management`](https://github.com/affaan-m/ECC/blob/main/skills/logistics-exception-management/SKILL.md) | Codified freight-exception handling expertise for shipment delays, damages, losses, shortages, and carrier disputes, with escalation protocols, carrie… |
| [`master-agreement-generator`](https://github.com/affaan-m/ECC/blob/main/skills/master-agreement-generator/SKILL.md) | Generate review drafts of counterparty master agreements from one template plus a JSON spec, with role-selected clauses and a Schedule A workflow limi… |
| [`esign-field-placement`](https://github.com/affaan-m/ECC/blob/main/skills/esign-field-placement/SKILL.md) | Deterministic method for placing signature, date, and text fields in a web e-signature composer through a browser automation session, using a fixed si… |
| [`production-scheduling`](https://github.com/affaan-m/ECC/blob/main/skills/production-scheduling/SKILL.md) | Codified expertise for production scheduling, job sequencing, line balancing, changeover optimization, and bottleneck resolution in discrete and batch… |
| [`quality-nonconformance`](https://github.com/affaan-m/ECC/blob/main/skills/quality-nonconformance/SKILL.md) | Quality control and non-conformance management for regulated manufacturing (FDA 21 CFR 820, IATF 16949, AS9100): NCR lifecycle and disposition, 5-Why/… |
| [`counterparty-channel-discipline`](https://github.com/affaan-m/ECC/blob/main/skills/counterparty-channel-discipline/SKILL.md) | Per-channel strict prompts, mention gating, silent observation, and a communication autonomy policy for agents that sit in shared channels with extern… |
| [`growth-log`](https://github.com/affaan-m/ECC/blob/main/skills/growth-log/SKILL.md) | Write growth log entries that extract reusable patterns from completed work — root cause, transferable rule, and a recognizable signal — instead of di… |
| [`healthcare-eval-harness`](https://github.com/affaan-m/ECC/blob/main/skills/healthcare-eval-harness/SKILL.md) | Patient safety evaluation harness for healthcare application deployments. |
| [`ito-baskets`](https://github.com/affaan-m/ECC/blob/main/skills/ito-baskets/SKILL.md) | Read-only Itô basket and prediction-market data skill. Index the live basket catalog, compare a basket against user-supplied research or a watchlist,… |
| [`ito-compute`](https://github.com/affaan-m/ECC/blob/main/skills/ito-compute/SKILL.md) | Query live GPU inventory, submit an authenticated Itô fixed-rate RFQ, inspect RFQ or procurement status, revoke device credentials, and run explicitly… |
| [`ito-inference`](https://github.com/affaan-m/ECC/blob/main/skills/ito-inference/SKILL.md) | Inspect the availability of model serving on a completed Itô compute booking and, when the canonical backend becomes available, hand off an explicitly… |
| [`ito-training`](https://github.com/affaan-m/ECC/blob/main/skills/ito-training/SKILL.md) | Inspect the availability of ML training on a completed Itô compute booking and, when the canonical backend becomes available, hand off an explicitly c… |
| [`prediction-market-risk-review`](https://github.com/affaan-m/ECC/blob/main/skills/prediction-market-risk-review/SKILL.md) | Review prediction-market, basket, oracle, and trading-agent workflows for compliance, safety, data-quality, privacy, and execution risk. |
| [`prediction-market-oracle-research`](https://github.com/affaan-m/ECC/blob/main/skills/prediction-market-oracle-research/SKILL.md) | Research prediction markets as data sources or oracle signals for products, agents, dashboards, and corporate decision intelligence. |
| [`evm-token-decimals`](https://github.com/affaan-m/ECC/blob/main/skills/evm-token-decimals/SKILL.md) | Prevent silent decimal mismatch bugs across EVM chains. Covers runtime decimal lookup, chain-aware caching, bridged-token precision drift, and safe no… |
| [`nodejs-keccak256`](https://github.com/affaan-m/ECC/blob/main/skills/nodejs-keccak256/SKILL.md) | Prevent Ethereum hashing bugs in JavaScript and TypeScript. Node's sha3-256 is NIST SHA3, not Ethereum Keccak-256, and silently breaks selectors, sign… |
| [`mailtrap-email-integration`](https://github.com/affaan-m/ECC/blob/main/skills/mailtrap-email-integration/SKILL.md) | Guides agents through integrating transactional email sending via Mailtrap's Email API, including sandbox testing, domain verification, and API authen… |

### Medios, vídeo y creatividad — 16 skills

Generación y edición de vídeo/imagen, estilo visual, Remotion, Manim y automatización de demos de UI.

| Skill | Qué hace |
|---|---|
| [`blender-motion-state-inspection`](https://github.com/affaan-m/ECC/blob/main/skills/blender-motion-state-inspection/SKILL.md) | Use this skill when inspecting Blender characters, rigs, poses, animation retargeting, ground contact, facing direction, or model-vs-motion alignment… |
| [`fal-ai-media`](https://github.com/affaan-m/ECC/blob/main/skills/fal-ai-media/SKILL.md) | Unified media generation via fal.ai MCP — image, video, and audio. |
| [`frontend-slides`](https://github.com/affaan-m/ECC/blob/main/skills/frontend-slides/SKILL.md) | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. |
| [`manim-video`](https://github.com/affaan-m/ECC/blob/main/skills/manim-video/SKILL.md) | Build reusable Manim explainers for technical concepts, graphs, system diagrams, and product walkthroughs, then hand off to the wider ECC video stack… |
| [`remotion-video-creation`](https://github.com/affaan-m/ECC/blob/main/skills/remotion-video-creation/SKILL.md) | Best practices for Remotion - Video creation in React. 29 domain-specific rules covering 3D, animations, audio, captions, charts, transitions, and mor… |
| [`taste`](https://github.com/affaan-m/ECC/blob/main/skills/taste/SKILL.md) | Creative-direction layer for music videos and short-form edits in the angelcore / cloud-trance / hyperpop family — a named-genre aesthetic vocabulary,… |
| [`taste-application`](https://github.com/affaan-m/ECC/blob/main/skills/taste-application/SKILL.md) | Generate new video against a distilled style pack and cut it into a finished piece - plan takes from the reference's cut rhythm, generate on fal, grad… |
| [`taste-distillation`](https://github.com/affaan-m/ECC/blob/main/skills/taste-distillation/SKILL.md) | Measure a set of reference videos into a reusable style pack - colour grade as a 3D LUT, cut rhythm as a shot-length distribution, hero stills, screen… |
| [`tasteforge-video`](https://github.com/affaan-m/ECC/blob/main/skills/tasteforge-video/SKILL.md) | Use for file-driven multimodal image, video, and 3D-asset discovery; taste interviews; distill or apply workflows; style-pack validation; |
| [`ui-demo`](https://github.com/affaan-m/ECC/blob/main/skills/ui-demo/SKILL.md) | Record polished UI demo videos using Playwright. Use when the user asks to create a demo, walkthrough, screen recording, or tutorial video of a web ap… |
| [`video-editing`](https://github.com/affaan-m/ECC/blob/main/skills/video-editing/SKILL.md) | AI-assisted video editing workflows for cutting, structuring, and augmenting real footage. |
| [`videodb`](https://github.com/affaan-m/ECC/blob/main/skills/videodb/SKILL.md) | Ingest, index, search, edit, and monitor video and audio with the VideoDB Python SDK — upload from files, URLs, or RTSP feeds, build spoken and scene… |
| [`liquid-glass-design`](https://github.com/affaan-m/ECC/blob/main/skills/liquid-glass-design/SKILL.md) | iOS 26 Liquid Glass design system — dynamic glass material with blur, reflection, and interactive morphing for SwiftUI, UIKit, and WidgetKit. |
| [`motion-advanced`](https://github.com/affaan-m/ECC/blob/main/skills/motion-advanced/SKILL.md) | Advanced motion patterns for React / Next.js — drag & drop, gestures, text animations, SVG path drawing, custom hooks, imperative sequences (useAnimat… |
| [`motion-foundations`](https://github.com/affaan-m/ECC/blob/main/skills/motion-foundations/SKILL.md) | Motion tokens, spring presets, performance rules, device adaptation, accessibility enforcement, and SSR safety for React / Next.js using motion/react.… |
| [`motion-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/motion-patterns/SKILL.md) | Production-ready animation patterns for React / Next.js — button, modal, toast, stagger, page transitions, exit animations, scroll, and layout — built… |

### Producto, UX y craft de interfaz — 12 skills

Accesibilidad, auditoría de flujos de clic, sistemas de diseño, QA en navegador y dirección visual.

| Skill | Qué hace |
|---|---|
| [`accessibility`](https://github.com/affaan-m/ECC/blob/main/skills/accessibility/SKILL.md) | Design, implement, and audit accessible UI to WCAG 2.2 Level AA across Web, iOS, and Android — semantic ARIA roles and labels, accessibility traits an… |
| [`browser-qa`](https://github.com/affaan-m/ECC/blob/main/skills/browser-qa/SKILL.md) | Run automated post-deploy UI verification with a browser automation MCP (claude-in-chrome, Playwright, or Puppeteer): console-error and Core Web Vital… |
| [`click-path-audit`](https://github.com/affaan-m/ECC/blob/main/skills/click-path-audit/SKILL.md) | Trace every user-facing button/touchpoint through its full state change sequence to find bugs where functions individually work but cancel each other… |
| [`design-system`](https://github.com/affaan-m/ECC/blob/main/skills/design-system/SKILL.md) | Generate a design system from an existing codebase or audit one for visual consistency: extract tokens (colors, typography, spacing, shadows) into des… |
| [`frontend-a11y`](https://github.com/affaan-m/ECC/blob/main/skills/frontend-a11y/SKILL.md) | Accessibility patterns for React and Next.js — semantic HTML, ARIA attributes, form labeling, keyboard navigation, focus management, and screen reader… |
| [`frontend-design-direction`](https://github.com/affaan-m/ECC/blob/main/skills/frontend-design-direction/SKILL.md) | Set an ECC-specific frontend design direction for production UI work. |
| [`frontend-patterns`](https://github.com/affaan-m/ECC/blob/main/skills/frontend-patterns/SKILL.md) | Frontend development patterns for React, Next.js, state management, performance optimization, and UI best practices. |
| [`make-interfaces-feel-better`](https://github.com/affaan-m/ECC/blob/main/skills/make-interfaces-feel-better/SKILL.md) | Apply concrete design-engineering details that make interfaces feel polished. |
| [`product-capability`](https://github.com/affaan-m/ECC/blob/main/skills/product-capability/SKILL.md) | Translate PRD intent, roadmap asks, or product discussions into an implementation-ready capability plan that exposes constraints, invariants, interfac… |
| [`product-lens`](https://github.com/affaan-m/ECC/blob/main/skills/product-lens/SKILL.md) | Validate the why before building through four product diagnostics — a YC-style product diagnostic that produces PRODUCT-BRIEF.md with a go/no-go recom… |
| [`ui-to-vue`](https://github.com/affaan-m/ECC/blob/main/skills/ui-to-vue/SKILL.md) | Use when the user has UI screenshots or design exports that need batch conversion into Vue 3 components, especially with Vant, Element Plus, or Ant De… |
| [`inherit-legacy-style`](https://github.com/affaan-m/ECC/blob/main/skills/inherit-legacy-style/SKILL.md) | Prevent AI style drift on legacy projects by scanning the codebase for implicit conventions, resolving conflicts with the operator one at a time, and… |

### Las 12 skills "estrella" si vienes de otro sistema de skills

Si solo vas a copiar/portar unas pocas, el propio repo las trata como el núcleo del método:

| Skill | Por qué importa |
|---|---|
| `tdd-workflow` | RED → GREEN → REFACTOR con verificación de cobertura. Es la base de todos los `*-tdd` por lenguaje. |
| `verification-loop` | Verificación en 6 fases (build, tipos, lint, tests+cobertura, seguridad, diff review). |
| `eval-harness` | Convierte "creo que funciona" en una métrica de regresión para agentes. |
| `continuous-learning-v2` | Instintos atómicos con score de confianza; v1 está deprecada. |
| `strategic-compact` | Compactación manual en fronteras lógicas en vez de auto-compact reactivo. |
| `search-first` | Buscar en npm/PyPI/MCP/GitHub antes de escribir código. |
| `agent-harness-construction` | Cómo diseñar action space, tool definitions y formato de observaciones. |
| `agent-architecture-audit` | Diagnóstico de 12 capas del stack de agentes; findings con severidad. |
| `safety-guard` | Tres modos (Careful/Balanced/Aggressive) contra `rm -rf`, `git push --force`, etc. |
| `unified-memory` | Handoffs de contexto entre Claude, Codex, Cursor, OpenCode, Hermes… |
| `santa-method` | Verificación adversarial: dos revisores independientes deben pasar ambos. |
| `configure-ecc` | Asistente conversacional de instalación dentro del propio harness. |

---

## 6. Los 71 agentes (subagentes)

Cada agente es un `.md` con frontmatter (`name`, `description`, `tools`, `model`) y un "Prompt Defense Baseline" (no cambiar de rol, no filtrar secretos, etc.). La mayoría usa `model: opus` para revisión y `sonnet` para ejecución.

#### Planificación, arquitectura y exploración de código (5)

| Agente | Qué hace |
|---|---|
| [`planner`](https://github.com/affaan-m/ECC/blob/main/agents/planner.md) | Expert planning specialist for complex features and refactoring. |
| [`architect`](https://github.com/affaan-m/ECC/blob/main/agents/architect.md) | Software architecture specialist for system design, scalability, and technical decision-making. |
| [`code-architect`](https://github.com/affaan-m/ECC/blob/main/agents/code-architect.md) | Designs feature architectures by analyzing existing codebase patterns and conventions, then providing implementatio… |
| [`code-explorer`](https://github.com/affaan-m/ECC/blob/main/agents/code-explorer.md) | Deeply analyzes existing codebase features by tracing execution paths, mapping architecture layers, and documenting… |
| [`spec-miner`](https://github.com/affaan-m/ECC/blob/main/agents/spec-miner.md) | Extracts behavioral specs from existing codebases for OpenSpec. |

#### Revisión de código, calidad y análisis (15)

| Agente | Qué hace |
|---|---|
| [`code-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/code-reviewer.md) | Expert code review specialist. Proactively reviews code for quality, security, and maintainability. |
| [`code-simplifier`](https://github.com/affaan-m/ECC/blob/main/agents/code-simplifier.md) | Simplifies and refines code for clarity, consistency, and maintainability while preserving behavior. |
| [`comment-analyzer`](https://github.com/affaan-m/ECC/blob/main/agents/comment-analyzer.md) | Analyze code comments for accuracy, completeness, maintainability, and comment rot risk. |
| [`type-design-analyzer`](https://github.com/affaan-m/ECC/blob/main/agents/type-design-analyzer.md) | Analyze type design for encapsulation, invariant expression, usefulness, and enforcement. |
| [`silent-failure-hunter`](https://github.com/affaan-m/ECC/blob/main/agents/silent-failure-hunter.md) | Review code for silent failures, swallowed errors, bad fallbacks, and missing error propagation. |
| [`pr-test-analyzer`](https://github.com/affaan-m/ECC/blob/main/agents/pr-test-analyzer.md) | Review pull request test coverage quality and completeness, with emphasis on behavioral coverage and real bug preve… |
| [`commit-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/commit-reviewer.md) | Reviews a staged diff and drafts a Conventional Commits-compliant message matching the repository's actual history… |
| [`a11y-architect`](https://github.com/affaan-m/ECC/blob/main/agents/a11y-architect.md) | Accessibility Architect specializing in WCAG 2.2 compliance for Web and Native platforms. |
| [`performance-optimizer`](https://github.com/affaan-m/ECC/blob/main/agents/performance-optimizer.md) | Performance analysis and optimization specialist. Use PROACTIVELY for identifying bottlenecks, optimizing slow code… |
| [`refactor-cleaner`](https://github.com/affaan-m/ECC/blob/main/agents/refactor-cleaner.md) | Dead code cleanup and consolidation specialist. Use PROACTIVELY for removing unused code, duplicates, and refactori… |
| [`agent-evaluator`](https://github.com/affaan-m/ECC/blob/main/agents/agent-evaluator.md) | Evaluates agent output against 5-axis quality rubric (accuracy, completeness, clarity, actionability, conciseness).… |
| [`conversation-analyzer`](https://github.com/affaan-m/ECC/blob/main/agents/conversation-analyzer.md) | Use this agent when analyzing conversation transcripts to find behaviors worth preventing with hooks. |
| [`harness-optimizer`](https://github.com/affaan-m/ECC/blob/main/agents/harness-optimizer.md) | Improve local agent-harness configuration reliability and cost using eval-driven grading (pass@k/pass^k) derived fr… |
| [`security-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/security-reviewer.md) | Security vulnerability detection and remediation specialist. |
| [`tdd-guide`](https://github.com/affaan-m/ECC/blob/main/agents/tdd-guide.md) | Test-Driven Development specialist enforcing write-tests-first methodology. |

#### Revisores por lenguaje / framework (22)

| Agente | Qué hace |
|---|---|
| [`typescript-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/typescript-reviewer.md) | Expert TypeScript/JavaScript code reviewer specializing in type safety, async correctness, Node/web security, and i… |
| [`react-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/react-reviewer.md) | Expert React/JSX code reviewer specializing in hook correctness, render performance, server/client component bounda… |
| [`vue-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/vue-reviewer.md) | Expert Vue.js code reviewer specializing in Composition API correctness, reactivity pitfalls, component architectur… |
| [`python-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/python-reviewer.md) | Expert Python code reviewer specializing in PEP 8 compliance, Pythonic idioms, type hints, security, and performanc… |
| [`fastapi-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/fastapi-reviewer.md) | Reviews FastAPI applications for async correctness, dependency injection, Pydantic schemas, security, OpenAPI quali… |
| [`django-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/django-reviewer.md) | Expert Django code reviewer specializing in ORM correctness, DRF patterns, migration safety, security misconfigurat… |
| [`go-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/go-reviewer.md) | Expert Go code reviewer specializing in idiomatic Go, concurrency patterns, error handling, and performance. |
| [`rust-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/rust-reviewer.md) | Expert Rust code reviewer specializing in ownership, lifetimes, error handling, unsafe usage, and idiomatic pattern… |
| [`java-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/java-reviewer.md) | Expert Java code reviewer for Spring Boot and Quarkus projects. |
| [`kotlin-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/kotlin-reviewer.md) | Kotlin and Android/KMP code reviewer. Reviews Kotlin code for idiomatic patterns, coroutine safety, Compose best pr… |
| [`flutter-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/flutter-reviewer.md) | Flutter and Dart code reviewer. Reviews Flutter code for widget best practices, state management patterns, Dart idi… |
| [`php-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/php-reviewer.md) | Expert PHP code reviewer specializing in PSR-12 compliance, PHP type system, Eloquent ORM patterns, security, and p… |
| [`ruby-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/ruby-reviewer.md) | Expert Ruby and Rails code reviewer specializing in idiomatic Ruby, Active Record query safety, Rails security defa… |
| [`csharp-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/csharp-reviewer.md) | Expert C# code reviewer specializing in .NET conventions, async patterns, security, nullable reference types, and p… |
| [`fsharp-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/fsharp-reviewer.md) | Expert F# code reviewer specializing in functional idioms, type safety, pattern matching, computation expressions,… |
| [`cpp-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/cpp-reviewer.md) | Expert C++ code reviewer specializing in memory safety, modern C++ idioms, concurrency, and performance. |
| [`swift-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/swift-reviewer.md) | Expert Swift code reviewer specializing in protocol-oriented design, value semantics, ARC memory management, Swift… |
| [`bengali-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/bengali-reviewer.md) | Reviews code handling Bengali (Bangla) text for Unicode correctness, proper normalization, script-aware processing,… |
| [`healthcare-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/healthcare-reviewer.md) | Reviews healthcare application code for clinical safety, CDSS accuracy, PHI compliance, and medical data integrity.… |
| [`database-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/database-reviewer.md) | PostgreSQL database specialist for query optimization, schema design, security, and performance. |
| [`mle-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/mle-reviewer.md) | Production machine-learning engineering reviewer for data contracts, feature pipelines, training reproducibility, o… |
| [`rag-pipeline-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/rag-pipeline-reviewer.md) | Reviews RAG (Retrieval-Augmented Generation) pipelines for retrieval quality, chunking strategy, embedding choices,… |

#### Resolvedores de errores de build (12)

| Agente | Qué hace |
|---|---|
| [`build-error-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/build-error-resolver.md) | Build and TypeScript error resolution specialist. Use PROACTIVELY when build fails or type errors occur. |
| [`react-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/react-build-resolver.md) | Diagnose and fix React build failures across Vite, webpack, Next.js, CRA, Parcel, esbuild, and Bun. |
| [`django-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/django-build-resolver.md) | Django/Python build, migration, and dependency error resolution specialist. |
| [`dart-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/dart-build-resolver.md) | Dart/Flutter build, analysis, and dependency error resolution specialist. |
| [`go-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/go-build-resolver.md) | Go build, vet, and compilation error resolution specialist. |
| [`rust-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/rust-build-resolver.md) | Rust build, compilation, and dependency error resolution specialist. |
| [`java-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/java-build-resolver.md) | Java/Maven/Gradle build, compilation, and dependency error resolution specialist. |
| [`kotlin-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/kotlin-build-resolver.md) | Kotlin/Gradle build, compilation, and dependency error resolution specialist. |
| [`swift-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/swift-build-resolver.md) | Swift/Xcode build, compilation, and dependency error resolution specialist. |
| [`cpp-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/cpp-build-resolver.md) | C++ build, CMake, and compilation error resolution specialist. |
| [`pytorch-build-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/pytorch-build-resolver.md) | PyTorch runtime, CUDA, and training error resolution specialist. |
| [`harmonyos-app-resolver`](https://github.com/affaan-m/ECC/blob/main/agents/harmonyos-app-resolver.md) | HarmonyOS application development expert specializing in ArkTS and ArkUI. |

#### Ejecución, orquestación y operaciones (10)

| Agente | Qué hace |
|---|---|
| [`loop-operator`](https://github.com/affaan-m/ECC/blob/main/agents/loop-operator.md) | Operate autonomous agent loops, monitor progress, and intervene safely when loops stall. |
| [`e2e-runner`](https://github.com/affaan-m/ECC/blob/main/agents/e2e-runner.md) | End-to-end testing specialist using Vercel Agent Browser (preferred) with Playwright fallback. |
| [`doc-updater`](https://github.com/affaan-m/ECC/blob/main/agents/doc-updater.md) | Documentation and codemap specialist. Use PROACTIVELY for updating codemaps and documentation. |
| [`docs-lookup`](https://github.com/affaan-m/ECC/blob/main/agents/docs-lookup.md) | When the user asks how to use a library, framework, or API or needs up-to-date code examples, use Context7 MCP to f… |
| [`gan-planner`](https://github.com/affaan-m/ECC/blob/main/agents/gan-planner.md) | GAN Harness — Planner agent. Expands a one-line prompt into a full product specification with features, sprints, ev… |
| [`gan-generator`](https://github.com/affaan-m/ECC/blob/main/agents/gan-generator.md) | GAN Harness — Generator agent. Implements features according to the spec, reads evaluator feedback, and iterates un… |
| [`gan-evaluator`](https://github.com/affaan-m/ECC/blob/main/agents/gan-evaluator.md) | GAN Harness — Evaluator agent. Tests the live running application via Playwright, scores against rubric, and provid… |
| [`chief-of-staff`](https://github.com/affaan-m/ECC/blob/main/agents/chief-of-staff.md) | Personal communication chief of staff that triages email, Slack, LINE, and Messenger. |
| [`marketing-agent`](https://github.com/affaan-m/ECC/blob/main/agents/marketing-agent.md) | Marketing strategist and copywriter for campaign planning, audience research, positioning, copy creation, and conte… |
| [`seo-specialist`](https://github.com/affaan-m/ECC/blob/main/agents/seo-specialist.md) | SEO specialist for technical SEO audits, on-page optimization, structured data, Core Web Vitals, and content/keywor… |

#### Dominio: redes, homelab y open source (7)

| Agente | Qué hace |
|---|---|
| [`homelab-architect`](https://github.com/affaan-m/ECC/blob/main/agents/homelab-architect.md) | Designs home and small-lab network plans from hardware inventory, goals, and operator experience level, with safe s… |
| [`network-architect`](https://github.com/affaan-m/ECC/blob/main/agents/network-architect.md) | Designs enterprise or multi-site network architecture from requirements, using existing network skills for focused… |
| [`network-config-reviewer`](https://github.com/affaan-m/ECC/blob/main/agents/network-config-reviewer.md) | Reviews router and switch configurations for security, correctness, stale references, risky change-window commands,… |
| [`network-troubleshooter`](https://github.com/affaan-m/ECC/blob/main/agents/network-troubleshooter.md) | Diagnoses network connectivity, routing, DNS, interface, and policy symptoms with a read-only OSI-layer workflow an… |
| [`opensource-forker`](https://github.com/affaan-m/ECC/blob/main/agents/opensource-forker.md) | Fork any project for open-sourcing. Copies files, strips secrets and credentials (20+ patterns), replaces internal… |
| [`opensource-packager`](https://github.com/affaan-m/ECC/blob/main/agents/opensource-packager.md) | Generate complete open-source packaging for a sanitized project. |
| [`opensource-sanitizer`](https://github.com/affaan-m/ECC/blob/main/agents/opensource-sanitizer.md) | Verify an open-source fork is fully sanitized before release. |

**Patrón interesante:** casi todo lenguaje tiene trío `X-reviewer` + `X-build-resolver` + skill `X-patterns`/`X-testing`. Es el modelo "reviewer + resolver" el que hace que el harness se auto-corrija en lugar de solo avisar.

---

## 7. Los 98 comandos slash

Son la capa de entrada rápida; internamente delegan en agentes y skills.

#### Planificación y desarrollo de features (13)

| Comando | Qué hace |
|---|---|
| [`/plan`](https://github.com/affaan-m/ECC/blob/main/commands/plan.md) | Restate requirements, assess risks, and create step-by-step implementation plan. |
| [`/plan-prd`](https://github.com/affaan-m/ECC/blob/main/commands/plan-prd.md) | Generate a lean, problem-first PRD and hand off to /plan for implementation planning. |
| [`/plan-canvas`](https://github.com/affaan-m/ECC/blob/main/commands/plan-canvas.md) | Open a plan or HTML artifact in the browser Plan Canvas for annotate-and-approve review. |
| [`/feature-dev`](https://github.com/affaan-m/ECC/blob/main/commands/feature-dev.md) | Guided feature development with codebase understanding and architecture focus |
| [`/prp-plan`](https://github.com/affaan-m/ECC/blob/main/commands/prp-plan.md) | Create comprehensive feature implementation plan with codebase analysis and pattern extraction |
| [`/prp-prd`](https://github.com/affaan-m/ECC/blob/main/commands/prp-prd.md) | Interactive PRD generator - problem-first, hypothesis-driven product spec with back-and-forth questioning |
| [`/prp-implement`](https://github.com/affaan-m/ECC/blob/main/commands/prp-implement.md) | Execute an implementation plan with rigorous validation loops |
| [`/prp-commit`](https://github.com/affaan-m/ECC/blob/main/commands/prp-commit.md) | Quick commit with natural language file targeting — describe what to commit in plain English |
| [`/prp-pr`](https://github.com/affaan-m/ECC/blob/main/commands/prp-pr.md) | Alias of /pr for the PRP workflow series. Use when creating a pull request mid-PRP workflow; otherwise use /pr. |
| [`/build-fix`](https://github.com/affaan-m/ECC/blob/main/commands/build-fix.md) | Detect the project build system and incrementally fix build/type errors with minimal safe changes. |
| [`/refactor-clean`](https://github.com/affaan-m/ECC/blob/main/commands/refactor-clean.md) | Safely identify and remove dead code with verification after each change. |
| [`/quality-gate`](https://github.com/affaan-m/ECC/blob/main/commands/quality-gate.md) | Run the ECC formatter quality gate for a single file and report remediation steps. |
| [`/checkpoint`](https://github.com/affaan-m/ECC/blob/main/commands/checkpoint.md) | Create, verify, or list workflow checkpoints after running verification checks. |

#### Revisión y verificación (10)

| Comando | Qué hace |
|---|---|
| [`/code-review`](https://github.com/affaan-m/ECC/blob/main/commands/code-review.md) | Code review — local uncommitted changes or GitHub PR (pass PR number/URL for PR mode). |
| [`/review-pr`](https://github.com/affaan-m/ECC/blob/main/commands/review-pr.md) | Comprehensive PR review using specialized agents (code-reviewer, comment-analyzer, pr-test-analyzer, silent-failure… |
| [`/issue-review`](https://github.com/affaan-m/ECC/blob/main/commands/issue-review.md) | Review a GitHub issue the way /code-review reviews a PR — verify the report against the codebase, find duplicates a… |
| [`/security-scan`](https://github.com/affaan-m/ECC/blob/main/commands/security-scan.md) | Run AgentShield against agent, hook, MCP, permission, and secret surfaces. |
| [`/santa-loop`](https://github.com/affaan-m/ECC/blob/main/commands/santa-loop.md) | Adversarial dual-review convergence loop — two independent model reviewers must both approve before code ships. |
| [`/astra-review`](https://github.com/affaan-m/ECC/blob/main/commands/astra-review.md) | Send Claude-written code to GPT-6-Astra (ChatGPT, via Codex CLI) for an independent cross-provider review, then fix… |
| [`/harness-audit`](https://github.com/affaan-m/ECC/blob/main/commands/harness-audit.md) | Run a deterministic repository harness audit and return a prioritized scorecard. |
| [`/test-coverage`](https://github.com/affaan-m/ECC/blob/main/commands/test-coverage.md) | Analyze coverage, identify gaps, and generate missing tests toward the target threshold. |
| [`/update-docs`](https://github.com/affaan-m/ECC/blob/main/commands/update-docs.md) | Sync documentation from source-of-truth files such as scripts, schemas, routes, and exports. |
| [`/update-codemaps`](https://github.com/affaan-m/ECC/blob/main/commands/update-codemaps.md) | Scan project structure and generate token-lean architecture codemaps. |

#### TDD y por lenguaje (build / review / test) (22)

| Comando | Qué hace |
|---|---|
| [`/go-build`](https://github.com/affaan-m/ECC/blob/main/commands/go-build.md) | Fix Go build errors, go vet warnings, and linter issues incrementally. |
| [`/go-review`](https://github.com/affaan-m/ECC/blob/main/commands/go-review.md) | Comprehensive Go code review for idiomatic patterns, concurrency safety, error handling, and security. |
| [`/go-test`](https://github.com/affaan-m/ECC/blob/main/commands/go-test.md) | Enforce TDD workflow for Go. Write table-driven tests first, then implement. |
| [`/rust-build`](https://github.com/affaan-m/ECC/blob/main/commands/rust-build.md) | Fix Rust build errors, borrow checker issues, and dependency problems incrementally. |
| [`/rust-review`](https://github.com/affaan-m/ECC/blob/main/commands/rust-review.md) | Comprehensive Rust code review for ownership, lifetimes, error handling, unsafe usage, and idiomatic patterns. |
| [`/rust-test`](https://github.com/affaan-m/ECC/blob/main/commands/rust-test.md) | Enforce TDD workflow for Rust. Write tests first, then implement. Verify 80%+ coverage with cargo-llvm-cov. |
| [`/cpp-build`](https://github.com/affaan-m/ECC/blob/main/commands/cpp-build.md) | Fix C++ build errors, CMake issues, and linker problems incrementally. |
| [`/cpp-review`](https://github.com/affaan-m/ECC/blob/main/commands/cpp-review.md) | Comprehensive C++ code review for memory safety, modern C++ idioms, concurrency, and security. |
| [`/cpp-test`](https://github.com/affaan-m/ECC/blob/main/commands/cpp-test.md) | Enforce TDD workflow for C++. Write GoogleTest tests first, then implement. Verify coverage with gcov/lcov. |
| [`/react-build`](https://github.com/affaan-m/ECC/blob/main/commands/react-build.md) | Fix React build failures (Vite, webpack, Next.js, CRA, Parcel, esbuild, Bun) incrementally — JSX/TSX compile errors… |
| [`/react-review`](https://github.com/affaan-m/ECC/blob/main/commands/react-review.md) | Comprehensive React/JSX code review for hook correctness, render performance, server/client component boundaries, a… |
| [`/react-test`](https://github.com/affaan-m/ECC/blob/main/commands/react-test.md) | Enforce TDD workflow for React. Write React Testing Library tests first (behavior-focused, accessibility-first), th… |
| [`/vue-review`](https://github.com/affaan-m/ECC/blob/main/commands/vue-review.md) | Comprehensive Vue.js code review for Composition API correctness, reactivity, composable patterns, template securit… |
| [`/python-review`](https://github.com/affaan-m/ECC/blob/main/commands/python-review.md) | Comprehensive Python code review for PEP 8 compliance, type hints, security, and Pythonic idioms. |
| [`/fastapi-review`](https://github.com/affaan-m/ECC/blob/main/commands/fastapi-review.md) | Review a FastAPI application for architecture, async correctness, dependency injection, Pydantic schemas, security,… |
| [`/flutter-build`](https://github.com/affaan-m/ECC/blob/main/commands/flutter-build.md) | Fix Dart analyzer errors and Flutter build failures incrementally. |
| [`/flutter-review`](https://github.com/affaan-m/ECC/blob/main/commands/flutter-review.md) | Review Flutter/Dart code for idiomatic patterns, widget best practices, state management, performance, accessibilit… |
| [`/flutter-test`](https://github.com/affaan-m/ECC/blob/main/commands/flutter-test.md) | Run Flutter/Dart tests, report failures, and incrementally fix test issues. |
| [`/kotlin-build`](https://github.com/affaan-m/ECC/blob/main/commands/kotlin-build.md) | Fix Kotlin/Gradle build errors, compiler warnings, and dependency issues incrementally. |
| [`/kotlin-review`](https://github.com/affaan-m/ECC/blob/main/commands/kotlin-review.md) | Comprehensive Kotlin code review for idiomatic patterns, null safety, coroutine safety, and security. |
| [`/kotlin-test`](https://github.com/affaan-m/ECC/blob/main/commands/kotlin-test.md) | Enforce TDD workflow for Kotlin. Write Kotest tests first, then implement. Verify 80%+ coverage with Kover. |
| [`/gradle-build`](https://github.com/affaan-m/ECC/blob/main/commands/gradle-build.md) | Fix Gradle build errors for Android and KMP projects |

#### Orquestación multi-agente y model routing (17)

| Comando | Qué hace |
|---|---|
| [`/multi-plan`](https://github.com/affaan-m/ECC/blob/main/commands/multi-plan.md) | Create a multi-model (Codex + Antigravity) implementation plan without modifying production code. |
| [`/multi-execute`](https://github.com/affaan-m/ECC/blob/main/commands/multi-execute.md) | Execute a multi-model implementation plan while preserving Claude as the only filesystem writer. |
| [`/multi-backend`](https://github.com/affaan-m/ECC/blob/main/commands/multi-backend.md) | Run a backend-focused multi-model workflow for APIs, algorithms, data, and business logic. |
| [`/multi-frontend`](https://github.com/affaan-m/ECC/blob/main/commands/multi-frontend.md) | Run a frontend-focused multi-model workflow for components, layouts, animation, and UI polish. |
| [`/multi-workflow`](https://github.com/affaan-m/ECC/blob/main/commands/multi-workflow.md) | Run a full multi-model development workflow with research, planning, execution, optimization, and review. |
| [`/model-route`](https://github.com/affaan-m/ECC/blob/main/commands/model-route.md) | Recommend the best model tier for the current task based on complexity, risk, and budget. |
| [`/orch-add-feature`](https://github.com/affaan-m/ECC/blob/main/commands/orch-add-feature.md) | Orchestrate building a brand-new feature end to end — research, plan, TDD, review, gated commit. |
| [`/orch-build-mvp`](https://github.com/affaan-m/ECC/blob/main/commands/orch-build-mvp.md) | Orchestrate bootstrapping a working MVP from a design/spec doc — ingest, slice, scaffold, TDD, review, gated commit… |
| [`/orch-change-feature`](https://github.com/affaan-m/ECC/blob/main/commands/orch-change-feature.md) | Orchestrate altering an existing, working feature to new desired behavior — update tests to the new spec, change im… |
| [`/orch-fix-defect`](https://github.com/affaan-m/ECC/blob/main/commands/orch-fix-defect.md) | Orchestrate fixing a bug — reproduce it as a failing regression test, fix to green, review, gated commit. |
| [`/orch-refine-code`](https://github.com/affaan-m/ECC/blob/main/commands/orch-refine-code.md) | Orchestrate a behavior-preserving refactor — confirm tests green, restructure without changing behavior, keep green… |
| [`/orch-review`](https://github.com/affaan-m/ECC/blob/main/commands/orch-review.md) | Run the orch-review native Workflow over a diff (local changes or a GitHub PR) and report blocking vs advisory find… |
| [`/loop-start`](https://github.com/affaan-m/ECC/blob/main/commands/loop-start.md) | Prepare a managed autonomous loop pattern with safety defaults and explicit stop conditions, then print the command… |
| [`/loop-status`](https://github.com/affaan-m/ECC/blob/main/commands/loop-status.md) | Inspect active loop state, progress, failure signals, and recommended intervention. |
| [`/gan-build`](https://github.com/affaan-m/ECC/blob/main/commands/gan-build.md) | Run a generator/evaluator build loop for implementation tasks with bounded iterations and scoring. |
| [`/gan-design`](https://github.com/affaan-m/ECC/blob/main/commands/gan-design.md) | Run a generator/evaluator design loop for frontend or visual work with bounded iterations and scoring. |
| [`/pm2`](https://github.com/affaan-m/ECC/blob/main/commands/pm2.md) | Analyze a project and generate PM2 service commands for detected frontend, backend, or database services. |

#### Épicas / coordinación GitHub (11)

| Comando | Qué hace |
|---|---|
| [`/epic-claim`](https://github.com/affaan-m/ECC/blob/main/commands/epic-claim.md) | Claim an epic issue, stamp coordination state, and sync local ownership. |
| [`/epic-decompose`](https://github.com/affaan-m/ECC/blob/main/commands/epic-decompose.md) | Break an epic into task children without creating task branches. |
| [`/epic-publish`](https://github.com/affaan-m/ECC/blob/main/commands/epic-publish.md) | Publish a validated epic update back to the issue and local cache. |
| [`/epic-review`](https://github.com/affaan-m/ECC/blob/main/commands/epic-review.md) | Mark epic review requested, approved, or changes requested. |
| [`/epic-sync`](https://github.com/affaan-m/ECC/blob/main/commands/epic-sync.md) | Sync epic issue bodies, labels, and local coordination snapshots from GitHub. |
| [`/epic-unblock`](https://github.com/affaan-m/ECC/blob/main/commands/epic-unblock.md) | Sweep blocked epic issues and reopen anything whose dependencies are closed. |
| [`/epic-validate`](https://github.com/affaan-m/ECC/blob/main/commands/epic-validate.md) | Validate epic readiness, dependencies, and coordination policy. |
| [`/jira`](https://github.com/affaan-m/ECC/blob/main/commands/jira.md) | Retrieve a Jira ticket, analyze requirements, update status, or add comments. |
| [`/projects`](https://github.com/affaan-m/ECC/blob/main/commands/projects.md) | List known projects and their instinct statistics |
| [`/project-init`](https://github.com/affaan-m/ECC/blob/main/commands/project-init.md) | Detect a project's stack and produce a dry-run ECC onboarding plan using the repository's install manifests and sta… |
| [`/pr`](https://github.com/affaan-m/ECC/blob/main/commands/pr.md) | Create a GitHub PR from current branch with unpushed commits — discovers templates, analyzes changes, pushes |

#### Aprendizaje, memoria y curaduría de skills (15)

| Comando | Qué hace |
|---|---|
| [`/learn`](https://github.com/affaan-m/ECC/blob/main/commands/learn.md) | Extract reusable patterns from the current session and save them as candidate skills or guidance. |
| [`/learn-eval`](https://github.com/affaan-m/ECC/blob/main/commands/learn-eval.md) | Extract reusable patterns from the session, self-evaluate quality before saving, and determine the right save locat… |
| [`/evolve`](https://github.com/affaan-m/ECC/blob/main/commands/evolve.md) | Analyze instincts and suggest or generate evolved structures |
| [`/instinct-status`](https://github.com/affaan-m/ECC/blob/main/commands/instinct-status.md) | Show learned instincts (project + global) with confidence |
| [`/instinct-import`](https://github.com/affaan-m/ECC/blob/main/commands/instinct-import.md) | Import instincts from file or URL into project/global scope |
| [`/instinct-export`](https://github.com/affaan-m/ECC/blob/main/commands/instinct-export.md) | Export instincts from project/global scope to a file |
| [`/prune`](https://github.com/affaan-m/ECC/blob/main/commands/prune.md) | Delete pending instincts older than 30 days that were never promoted. |
| [`/promote`](https://github.com/affaan-m/ECC/blob/main/commands/promote.md) | Promote project-scoped instincts to global scope |
| [`/skill-create`](https://github.com/affaan-m/ECC/blob/main/commands/skill-create.md) | Analyze local git history to extract coding patterns and generate SKILL.md files. |
| [`/skill-health`](https://github.com/affaan-m/ECC/blob/main/commands/skill-health.md) | Show skill portfolio health dashboard with charts and analytics. |
| [`/skill-host-compat`](https://github.com/affaan-m/ECC/blob/main/commands/skill-host-compat.md) | Lint ECC skills for Codex/Cursor-safe frontmatter and Claude-only substitutions before a skill PR. |
| [`/sessions`](https://github.com/affaan-m/ECC/blob/main/commands/sessions.md) | Manage Claude Code session history, aliases, and session metadata. |
| [`/save-session`](https://github.com/affaan-m/ECC/blob/main/commands/save-session.md) | Save current session state to a dated file in ~/.claude/session-data/ so work can be resumed in a future session wi… |
| [`/resume-session`](https://github.com/affaan-m/ECC/blob/main/commands/resume-session.md) | Load the most recent session file from ~/.claude/session-data/ and resume work with full context from where the las… |
| [`/aside`](https://github.com/affaan-m/ECC/blob/main/commands/aside.md) | Answer a quick side question without interrupting or losing context from the current task. |

#### Operación, coste y hooks (10)

| Comando | Qué hace |
|---|---|
| [`/cost-report`](https://github.com/affaan-m/ECC/blob/main/commands/cost-report.md) | Generate a local Claude Code cost report from the ECC cost-tracker metrics log. |
| [`/token-card`](https://github.com/affaan-m/ECC/blob/main/commands/token-card.md) | Render a token-usage stat card from local agent session logs and commit it to the repo. |
| [`/auto-update`](https://github.com/affaan-m/ECC/blob/main/commands/auto-update.md) | Pull the latest ECC repo changes and reinstall the current managed targets. |
| [`/hookify`](https://github.com/affaan-m/ECC/blob/main/commands/hookify.md) | Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions. |
| [`/hookify-configure`](https://github.com/affaan-m/ECC/blob/main/commands/hookify-configure.md) | Enable or disable hookify rules interactively |
| [`/hookify-list`](https://github.com/affaan-m/ECC/blob/main/commands/hookify-list.md) | List all configured hookify rules |
| [`/hookify-help`](https://github.com/affaan-m/ECC/blob/main/commands/hookify-help.md) | Get help with the hookify system |
| [`/setup-pm`](https://github.com/affaan-m/ECC/blob/main/commands/setup-pm.md) | Configure your preferred package manager (npm/pnpm/yarn/bun) |
| [`/ecc-guide`](https://github.com/affaan-m/ECC/blob/main/commands/ecc-guide.md) | Navigate ECC's current agents, skills, commands, hooks, install profiles, and docs from the live repository surface… |
| [`/marketing-campaign`](https://github.com/affaan-m/ECC/blob/main/commands/marketing-campaign.md) | Plan and execute a full marketing campaign. Accepts a product brief and returns positioning, landing page copy, ema… |

Familia destacada: **PRP** (`prp-prd → prp-plan → prp-implement → prp-commit → prp-pr`) y **orch-** (`orch-add-feature`, `orch-build-mvp`, `orch-change-feature`, `orch-fix-defect`, `orch-refine-code`, `orch-review`), que son pipelines end-to-end.

---

## 8. Hooks: la capa de automatización en runtime

8 eventos, 28 hooks. Se pueden perfilar (`minimal` / `standard` / `strict`) o desactivar por ID.

| Evento | Hooks |
|---|---|
| **PreToolUse** (10) | `pre:bash:dispatcher` (dispatcher consolidado de calidad/tmux/push/GateGuard) · `pre:powershell:gateguard-fact-force` · `pre:write:doc-file-warning` · `pre:edit-write:suggest-compact` · `pre:observe:continuous-learning` · `pre:governance-capture` · `pre:config-protection` (bloquea tocar configs de linter/formatter) · `pre:mcp-health-check` · `pre:edit-write:gateguard-fact-force` · `pre:hookify-runtime` |
| **UserPromptSubmit** (1) | `prompt:hookify-runtime` (reglas locales del proyecto antes del prompt) |
| **PreCompact** (1) | `pre:compact` — guarda estado antes de compactar |
| **SessionStart** (2) | `session:start` (carga contexto previo + detecta package manager) · `session-start:plan-canvas-sessions` |
| **PostToolUse** (2) | `post:dispatcher:sync` · `post:dispatcher:async` (un solo proceso, preserva orden) |
| **PostToolUseFailure** (2) | `post:mcp-health-check` (marca MCP unhealthy y reintenta) · `post:skill:track` |
| **Stop** (8) | `stop:hookify-runtime` · `stop:plan-canvas-pending` · `stop:format-typecheck` (Biome/Prettier + tsc en lote) · `stop:check-console-log` · `stop:session-end` · `stop:evaluate-session` · `stop:cost-tracker` · `stop:desktop-notify` |
| **SessionEnd** (1) | `session:end:marker` |

Los 61 scripts de `scripts/hooks/` incluyen, entre otros: `cost-tracker.js`, `gateguard-fact-force.js`, `gateguard-heredoc.js`, `check-console-log.js`, `post-edit-typecheck.js`, `post-edit-format.js`, `pre-bash-dev-server-block.js`, `block-no-verify.js`, `insaits-security-monitor.py`, `mcp-health-check.js`, `ecc-statusline.js`, `ecc-context-monitor.js`, `desktop-notify.js`, `plan-canvas-*.js`, `hookify-runtime.js`.

**Filosofía de hooks**: un *dispatcher* por evento para no arrancar 10 procesos Node; gates "fact-forcing" que obligan al agente a mirar el estado real antes de editar.

---

## 9. Instalación selectiva: perfiles, módulos y componentes

En vez de "instalar todo y comer 40k tokens de contexto", ECC trae un sistema de instalación por capas (`manifests/`).

**Perfiles** (`install-profiles.json`): `minimal`, `core`, `developer`, `opencode`, `security`, `research`, `full`.

**Módulos** (47): `rules-core`, `agents-core`, `commands-core`, `hooks-runtime`, `hermes-hooks`, `platform-configs`, `framework-language`, `database`, `workflow-quality`, `security`, `research-apis`, `business-content`, `operator-workflows`, `optimization-workflows`, `prediction-market-skills`, `operator-desk-patterns`, `ito-compute`, `nasiko-control-plane`, `social-distribution`, `media-generation`, `orchestration`, `agentic-patterns`, `devops-infra`, `machine-learning`, `supply-chain-domain`, `document-processing`, `documentation-*` (4), `skill-unified-memory`, `shared-script-utils` + 12 módulos `docs-<locale>`.

**Componentes** (93) con IDs tipo `baseline:rules`, `lang:typescript`, `framework:react`, `capability:security`, `agent:code-reviewer`, `skill:tdd-workflow`, `locale:es` (ojo: el componente `locale:es` no aparece listado en `install-components.json` de este commit; sí existen docs en `docs/es/`).

Skill asociada: **`agent-sort`** construye un plan de instalación a medida para un repo concreto; **`configure-ecc`** es el wizard interactivo.

---

## 10. Herramientas: CLI, scripts y utilidades

### CLI `ecc` (npm `ecc-universal`)
Bins: `ecc`, `ecc-universal`, `ecc-install`, `ecc-control-pane`, `ecc-memory-mcp`, `ecc-plan-canvas`.

Subcomandos: `setup` · `welcome` · `install` · `plan` · `catalog` · `consult` · `profile` · `ito` · `nasiko` · `memory` · `doctor` · `feedback` · `repair` · `status` · `sessions` · `uninstall`.

`npm scripts` relevantes: `catalog:check`, `harness:adapters`, `harness:audit`, `harness:eval`, `observability:ready`, `operator:dashboard`, `platform:audit`, `security:ioc-scan`, `orchestrate:{status,worker,tmux}`, `test:validators`, `coverage`, `dashboard`, `dashboard:web`.

### Scripts de orquestación y auditoría (`scripts/`)
| Script | Función |
|---|---|
| `orchestrate-worktrees.js` | Un worktree aislado por agente; base de la orquestación multi-agente |
| `harness-audit.js` | Auditoría determinista del harness con scorecard priorizado |
| `platform-audit.js` | Paridad entre plataformas/harnesses |
| `harness-adapter-compliance.js` | Verifica que cada adaptador cumple el contrato |
| `eval-harness.js` | Ejecuta el harness de evaluación |
| `memory.js` / `memory-mcp.mjs` | Memory Vault local (create-only, sin revisión) expuesto por MCP |
| `sessions-cli.js` / `session-inspect.js` | Historial e inspección de sesiones |
| `control-pane.js` / `operator-readiness-dashboard.js` | Paneles de operador |
| `plan-canvas.js` | Canvas en navegador para anotar y aprobar planes |
| `mcp-inventory.js` | Inventario de MCP disponibles |
| `doctor.js` / `repair.js` | Diagnóstico y reparación de la instalación |
| `catalog.js` | Catálogo canónico de skills/agentes/comandos |
| `agent-convert.js`, `gemini-adapt-agents.js`, `qwen-adapt-agents.js`, `build-opencode.js`, `build-pi-core.js` | Conversión del catálogo a cada harness |
| `gan-harness.sh` | Loop generador/evaluador con score |
| `observability-readiness.js`, `gateguard-report.js`, `coordination-inventory.js`, `orchestration-status.js` | Observabilidad y coordinación |
| `scripts/ci/*` | `pr-burst-guard`, `issue-submission-guard`, `scan-supply-chain-iocs`, `check-unicode-safety`, `generate-command-registry`… |

### Otros artefactos
- `ecc_dashboard.py` — GUI Tkinter (Agents/Skills/Commands/Rules/Settings, búsqueda, temas).
- `ecc2/` — control-plane en Rust (alpha): TUI, store SQLite, daemon, risk scoring, sesiones worktree-aware.
- `pi/core/` — perfil portable de 134 skills + 24 comandos, **cero hooks, cero red** (para entornos restringidos).
- `docker/` — context-profiles, medición de efectividad de GateGuard, plugin-setup.
- `schemas/` — 18 JSON Schemas para validar todo lo anterior (hooks, memoria, install-state, provenance, capsule envelope…).
- `workflows/orch-review.workflow.js` — workflow nativo de revisión.

---

## 11. Los 34 servidores MCP preconfigurados

`mcp-configs/mcp-servers.json` listo para copiar a `~/.claude.json` / `.mcp.json`.

| Grupo | Servidores |
|---|---|
| Memoria / contexto | `memory`, `omega-memory`, `memxus`, `ecc-memory-vault`, `longhand` (historial de sesión sin pérdida), `context7` (docs en vivo), `sequential-thinking` |
| Código y repos | `github`, `jira`, `confluence`, `codescene`, `evalview` (regresión de agentes), `filesystem` |
| Datos | `supabase`, `clickhouse` |
| Web / investigación | `firecrawl`, `exa-web-search`, `parallel-search`, `browserbase`, `browser-use`, `playwright` |
| Deploy / infra | `vercel`, `railway`, `cloudflare-docs`, `cloudflare-workers-builds`, `cloudflare-workers-bindings`, `cloudflare-observability` |
| Agentes / coste | `devfleet` (agentes paralelos en worktrees), `nexus` (proxy local de coste/privacidad), `token-optimizer` (−95 % contexto) |
| Media / UI | `fal-ai`, `magic` |
| Otros | `ito-compute`, `laraplugins` |

---

## 12. Rules: los estándares siempre-activos

`rules/common/` (10 archivos): `agents`, `code-review`, `coding-style`, `development-workflow`, `git-workflow`, `hooks`, `patterns`, `performance`, `security`, `testing` (incluye requisito de 80 % de cobertura).

Packs por lenguaje (5 archivos cada uno: `coding-style`, `patterns`, `testing`, `security`, `hooks`): `typescript`, `python`, `golang`, `rust`, `java`, `kotlin`, `swift`, `php`, `ruby`, `cpp`, `csharp`, `fsharp`, `perl`, `arkts`, `dart`.
Packs de framework: `react`, `vue`, `angular`, `nuxt`, `react-native` (añade `accessibility.md`, `performance.md`, `production-readiness.md`), `web` (`design-quality.md`, `performance.md`).

---

## 13. Soporte de harness (dónde puedes instalarlo)

| Harness | Estado | Nota |
|---|---|---|
| Claude Code | Estable (primario) | Plugin o instalador selectivo |
| Codex | Plugin nativo | Hooks propios con trust explícito |
| Qoder | Plugin nativo | Solo el hook SessionStart revisado |
| Cursor | Beta | Instalador selectivo en `.cursor/` |
| OpenCode | Beta | Plugin construido, subconjunto del catálogo |
| GitHub Copilot Chat / CLI | Instruction-only / Beta | Sin hooks adaptados |
| Gemini, Zed, Antigravity, Qwen, Hermes, OpenClaw, Kimi, CodeBuddy, JoyCode | Experimental | Adaptadores mínimos, sin paridad total |

Plataformas: Linux/macOS/Windows+WSL soportados en el core; Windows nativo tiene defectos abiertos en learning v2 y memory vault.

---

## 14. Lectura crítica (lo que conviene saber antes de adoptarlo)

**Fortalezas**
- Las skills están escritas como procedimientos con criterios de salida, no como "ensayos": cada una trae *When to Use*, conceptos, pasos y verificación.
- Instalación selectiva real (perfiles/módulos/componentes) — se puede evitar el coste de contexto.
- Doble red de seguridad: hooks deterministas + agentes revisores. El patrón `reviewer` + `build-resolver` por lenguaje es lo más reutilizable del repo.
- Portabilidad probada por tests (`harness-adapter-compliance`, `platform-audit`), no solo prometida.

**Costes y riesgos**
- **Volumen brutal**: 314 skills + 98 comandos + 71 agentes. Sin instalación selectiva, el catálogo compite por el context window. El propio README insiste en perfiles y en `agent-sort`.
- **Ruido/duplicación**: hay solapes claros (`continuous-learning` vs `-v2`, `benchmark` vs `benchmark-methodology`, `investor-materials` vs `investor-outreach`, `deep-research` vs `research-ops`). La propia skill `skill-stocktake` existe para auditar esto.
- **Hooks con efecto real** en tu máquina: bloquean ediciones, matan `--no-verify`, notifican, miden coste. Perfil `minimal` o `--no-hooks` si no quieres automatización.
- **Superficie comercial**: muchas skills apuntan a servicios de terceros (Itô compute, Nasiko, SocialClaw, VideoDB, DevFleet, Nexus). No son dependencias del core, pero sí ruido de catálogo.
- **Madurez desigual**: `ecc2/` es alpha, Windows nativo tiene bugs abiertos, y varios adaptadores son "experimentales".
- Verifica siempre la fuente: el README advierte sobre mirrors no oficiales.

---

## 15. Cómo aprovecharlo en este repo (`Angel-Skills`)

Ruta sugerida, de menor a mayor compromiso:

1. **Copiar el patrón, no el volumen.** Portar `tdd-workflow`, `verification-loop`, `search-first`, `safety-guard`, `agent-harness-construction` y `skill-stocktake` como plantilla de estilo de skill.
2. **Adoptar la estructura de frontmatter** (`name` + `description` con "Use when…" explícito, + `metadata.origin`) — es lo que hace que el modelo sepa cuándo disparar la skill.
3. **Adoptar la separación reviewer / resolver** para cada stack que os importe.
4. **Reusar `rules/common/`** como estándares base y añadir packs por lenguaje según necesidad.
5. **Integrar la instalación selectiva** (perfiles/módulos) si el repo va a crecer a decenas de skills.
6. **No copiar los hooks tal cual**: están acoplados a la estructura de ECC y a rutas de Claude Code.

---

### Fuentes primarias verificadas
- README.md (2.209 líneas), `AGENTS.md`, `CLAUDE.md`, `the-longform-guide.md`
- `skills/*/SKILL.md` (314), `agents/*.md` (71), `commands/*.md` (98)
- `hooks/hooks.json`, `hooks/hooks.metadata.json`
- `manifests/install-{profiles,modules,components}.json`
- `mcp-configs/mcp-servers.json`, `rules/`, `package.json`, `.claude-plugin/plugin.json`
