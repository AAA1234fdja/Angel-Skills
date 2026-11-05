# workflow · paquete de skills de Angel

Paquete autocontenido de skills con registro, validador y dos formas de uso:
**CLI** (`node workflow/bin/workflow.mjs`) y **extensión opcional de Ely IDE**
(`angel.workflow`). Sin dependencias, sin instalación, sin servicios externos.

```text
workflow/
├── EXTENSION-STANDARD.md   ← se lee ANTES de crear o editar una skill
├── categories.json         ← registro: fuente de verdad de categorías y skill ids
├── CHANGELOG.md
├── skills/<categoria>/<skill>/SKILL.md
├── bin/workflow.mjs        ← CLI
├── src/registry.mjs        ← motor: parseo, validación, contexto
└── ely-extension/          ← extensión opcional para Ely IDE
```

## Uso rápido

```bash
node workflow/bin/workflow.mjs plan          # qué hay y qué falta por categoría
node workflow/bin/workflow.mjs list          # skills por categoría
node workflow/bin/workflow.mjs show tdd-workflow
node workflow/bin/workflow.mjs validate      # EXTENSION-STANDARD.md §7
node workflow/bin/workflow.mjs claim --phase test   # contexto mínimo para un arnés
node workflow/bin/workflow.mjs pack          # genera dist/workflow.zip
```

Atajo con enlace simbólico (`ln -s ../../workflow/bin/workflow.mjs /usr/local/bin/workflow`)
o con `alias workflow="node $PWD/workflow/bin/workflow.mjs"`.

## Las tres reglas del paquete

1. **Una skill = un procedimiento con salida verificable.** Si no se puede
   comprobar si se aplicó, no es una skill.
2. **El registro manda.** Toda skill en disco está en `categories.json` y toda
   entrada del registro tiene su `SKILL.md`. `validate` lo comprueba.
3. **Se carga una fase, no el catálogo.** `claim --phase <fase>` entrega solo lo
   necesario; el paquete existe para ahorrar contexto, no para gastarlo.

## Estado actual

| Categoría | Estado | Skills |
|---|---|---|
| `ingenieria` | activa | 11 |
| `agentic` | activa | 3 |
| `seguridad` | pendiente | 0 |
| `datos-infra` | pendiente | 0 |
| `producto` | pendiente | 0 |
| `contenido` | pendiente | 0 |

**`ingenieria`** — `tdd-workflow` (test), `verification-loop` (verify),
`build-fix` (verify), `coding-standards` (implement), `refactor-clean`
(implement), `performance-optimizer` (implement), `code-review` (review),
`search-first` (plan), `e2e-testing` (test), `ai-regression-testing` (test),
`skill-authoring` (meta).

**`agentic`** — `agent-harness-construction` (plan), `agent-architecture-audit`
(review), `eval-harness` (verify).

## Integrar en Ely (opcional)

La extensión no se activa sola: se copia al IDE y se habilita desde la vista
**Extensiones**.

```bash
node workflow/bin/workflow.mjs install --ely /ruta/al/repo/Ely
# o, con Ely clonado al lado:
node ../Ely/CLI/ely extensions install ../Angel-Skills/workflow/ely-extension
```

La segunda forma instala en `.ely/extensions/angel.workflow/`; la extensión
necesita el paquete al lado, así que en ese caso se copian también
`categories.json`, `EXTENSION-STANDARD.md` y `skills/` dentro de la carpeta
instalada (o se usa la primera forma, que lo hace por ti).

Eso deja `IDE/ely-extensions/angel.workflow/` con el manifiesto, `main.js` y una
copia del paquete (`categories.json`, `EXTENSION-STANDARD.md`, `skills/`) para
que la extensión los lea con `workspace.readFile` sin salir del sandbox.

Comandos que aporta en la paleta:

| Comando | Qué hace |
|---|---|
| `Workflow: listar skills` | Tabla por categoría con estado y disparador |
| `Workflow: cargar fase en el chat` | Pregunta la fase y envía al chat solo esas skills |
| `Workflow: abrir una skill` | Muestra el `SKILL.md` completo |
| `Workflow: validar el paquete` | Mismas reglas que el CLI, dentro del IDE |
| `Workflow: leer el estándar` | Abre `EXTENSION-STANDARD.md` |

Permisos declarados: `workspace:read`, `ui`, `commands`, `chat`. Sin red y sin
escritura: la extensión solo lee y conversa. Desactivarla deja el paquete
intacto y el CLI funcionando.

## Añadir una skill

1. Leer `EXTENSION-STANDARD.md` §1 y §7.
2. Registrar la entrada en `categories.json`.
3. Crear `skills/<categoria>/<id>/SKILL.md`.
4. `node workflow/bin/workflow.mjs validate` → verde.
5. Anotarlo en `CHANGELOG.md`.

El procedimiento completo está en la skill `skill-authoring`.

## Origen de los patrones

Las skills marcadas `status: adoptada` adaptan procedimientos de
[affaan-m/ECC](https://github.com/affaan-m/ECC) (MIT, commit `b38be6a`),
reescritos para este repositorio y con el id original conservado. Inventario
completo del origen en `../ECC-INVENTARIO.md`.
