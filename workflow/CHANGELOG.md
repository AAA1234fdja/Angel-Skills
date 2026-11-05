# CHANGELOG · workflow

Formato: fecha · versión del paquete · cambio.

## 0.2.0 — 2026-11-05

- `ingenieria` completada: 11 skills. Se añaden `e2e-testing` (test),
  `ai-regression-testing` (test), `refactor-clean` (implement) y
  `performance-optimizer` (implement). `pending` de la categoría queda vacío.
- `agentic` pasa a `activa` con 3 skills: `agent-harness-construction` (plan),
  `agent-architecture-audit` (review) y `eval-harness` (verify). Gate de la
  categoría: ningún cambio en un agente se acepta sin eval antes/después.
- `pending` de `agentic`: `continuous-learning-v2`, `strategic-compact`,
  `safety-guard`, `agent-eval`, `agent-self-evaluation`.
- `README.md` raíz del repo reescrito: apuntaba a un placeholder.
- `validate` en verde: 14 skills, 0 errores, 0 avisos.

## 0.1.0 — 2026-11-05

- Paquete `workflow/` creado: `EXTENSION-STANDARD.md`, `categories.json`,
  `bin/workflow.mjs`, `src/registry.mjs`, extensión `angel.workflow`, `README.md`.
- Categoría `ingenieria` activa con 7 skills: `tdd-workflow`, `verification-loop`,
  `coding-standards`, `code-review`, `search-first`, `build-fix`, `skill-authoring`.
- Categorías `agentic`, `seguridad`, `datos-infra`, `producto` y `contenido`
  declaradas en estado `pendiente`, con sus ids de ECC anotados en `pending`.
- CLI con `list`, `show`, `claim`, `validate`, `plan`, `pack`, `install`, `where`.
- Extensión de Ely con 5 comandos, permisos `workspace:read`, `ui`, `commands`,
  `chat` (sin red, sin escritura).

Pendiente para 0.3.0: `seguridad` (`security-review`, `safety-guard`, `gateguard`,
`security-bounty-hunter`) y decidir si `datos-infra` se parte en dos.
