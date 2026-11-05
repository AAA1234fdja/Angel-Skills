# CHANGELOG · workflow

Formato: fecha · versión del paquete · cambio. Cada entrada dice qué cambia
para quien consume el paquete; los cambios de comportamiento incompatibles van primero
y con la acción requerida.

## 0.4.0 — 2026-11-05

Los agentes pasan a ser servicios administrables: un agente es una API, y toda
API puede llamar subagentes. El modelo viene de Harness-Candy y aquí se vuelve
datos que el runtime valida, enruta y deja en el journal.

**compatible** — no se rompe nada de 0.3: las 44 skills, los 41 tools y los 4
contratos siguen igual. Lo nuevo es aditivo, salvo el manifiesto de Ely, que pasa
a 0.4.0 con tres comandos más.

- **added** — `angel/agents.py`: direcciones `agent://<space>/<id>@<x.y.z>#<pin>-><hop>`,
  carta de agente, `Roster` (get/resolve/child/children/parents/tree/cascade_order/
  validate), `Dispatcher` (plan + ejecución), `Call`/`Outcome`/`Delegation` y un
  journal por llamada.
- **added** — cinco reglas que el runtime hace cumplir: la carta valida contra su
  contrato; las capacidades se intersectan hacia abajo (un subagente nunca recibe
  más de lo que su padre tiene); `max_depth`/`max_calls`/`budget_share` se
  comprueban antes de llamar; un ciclo se rechaza al cargar el roster; toda llamada
  deja un árbol y un journal encadenado por hashes.
- **added** — 6 cartas en `agents/`: `isa-planner`, `xev-builder`, `xev-tester`,
  `wev-judge`, `zev-scout`, `governance-auditor`, más `agents/roster.json` (el
  índice que lee la extensión de Ely, que no puede listar directorios).
- **added** — `agent-card@1.0.0` como quinto contrato: es la firma de la carta y
  se valida al cargar el roster, no solo en `validate`.
- **added** — `workflow agents list|show|validate|tree|address|plan|call`, siete
  subcomandos (el CLI pasa de 14 a 21).
- **added** — `AGENTS.md` como documento de referencia del sistema de agentes.
- **added** — 51 tests nuevos (`tests/test_agents.py`, 47; 4 en la suite de
  consistencia): direcciones, pines obsoletos, contratos, ciclos, autorización,
  profundidad, fan-out, presupuesto, techos de ejecución, journal y CLI. Total: 176.
- **changed** — la extensión de Ely pasa a 0.4.0 con tres comandos de solo lectura
  (`agents`, `agent tree`, `agent address`). Sigue sin permiso de red.
- **changed** — `max_depth` se mide desde el propio agente (cuántos saltos por
  debajo), y el grafo se valida contra ese límite: un grafo más profundo que el
  límite declarado es un error, no un aviso.

## 0.3.0 — 2026-11-05

Reescritura completa. El paquete pasa de catálogo de markdown a runtime ejecutable.

**breaking** — una skill ya no es un `.md` suelto: es una carpeta con `SKILL.md` +
`skill.json` + `tools/` + `references/`. Las skills de 0.2 (`skills/ingenieria/`,
`skills/agentic/`) se eliminan y se recrean con el nuevo esquema. Acción: si tenías
copias locales, añádeles `skill.json` y vuelve a pasar `workflow validate --strict`.

- **added** — `angel/`, runtime en Python 3.10+ stdlib: `registry` (carga, valida y
  reconcilia disco contra registro), `router` (puntuación determinista),
  `protocols` (6 protocolos tipados y versionados), `contracts` (JSON-schema con
  versiones inmutables y diff semántico), `tools` (sandbox de builtins + allow-list
  de módulos, timeout y captura), `journal` (cadena de hashes), `runner` (plan,
  dispatch, ejecución, veredicto, gate), `errors` (taxonomía con dueño y recuperación),
  `frontmatter`, `jsonschema`, `cli` (14 subcomandos).
- **added** — 44 skills en 11 categorías activas: engineering 12, contracts 4,
  protocols 3, errors 4, agentic 5, security 4, data 4, reversing 3, governance 3,
  product 1, content 1. Todas en inglés, con `origin`, `phase` y `status`.
- **added** — 41 herramientas ejecutables, todas de riesgo `read`, puras, con
  esquema de entrada y un `sample` declarado; `workflow tool --self-test` ejecuta
  las 41 y falla si una no produce `advice`.
- **added** — 4 contratos con consumidores: `skill-report@1.1.0`,
  `message-digest@1.0.0`, `isa-plan@1.0.0`, `xev-result@1.0.0`.
- **added** — `tests/`: 118 tests sobre el runtime y el catálogo real, incluida la
  consistencia entre documentación, comandos citados y ficheros en disco.
- **added** — `WORKFLOW.md` como documento principal: propósito, comparación con
  ECC, anatomía de una skill, recorrido de 8 pasos, presupuesto de contexto, 8
  reglas no negociables, ruta de crecimiento.
- **changed** — `EXTENSION-STANDARD.md` reescrito a 0.3: las tres pruebas de una
  skill, contrato de frontmatter y de `skill.json`, tabla de riesgos, checklist,
  antipatrones, protocolo de registro y códigos de salida.
- **changed** — el router entiende español, enmascara cláusulas negadas, agrupa los
  pasos en respuestas y apoyo, y filtra (en vez de puntuar) la fase pedida.
- **changed** — `workflow validate` compara en las dos direcciones (disco ⇄ registro)
  y `--strict` convierte avisos en fallo.
- **fixed** — `workflow tool` devuelve código 7/8 cuando la herramienta dictamina
  que no hay que seguir, para que una cadena de shell se detenga.
- **fixed** — el CLI ya no contiene el hack `{"**base": None} if False else {...}`.
- **removed** — `bin/workflow.mjs` y `src/registry.mjs` (CLI Node de 0.2): el runtime
  Python los sustituye por completo. Usa `python3 -m angel.cli`.

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
