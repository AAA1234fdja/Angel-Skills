# EXTENSION-STANDARD.md — Estándar de skills de Angel

> **Este archivo se lee antes de crear o editar cualquier skill.**
> Si el arnés (o una persona) va a tocar `workflow/`, primero lee §1 y §7, luego
> consulta la categoría en `workflow/categories.json` y solo después escribe.
> Última revisión: 2026-11-05 · versión del paquete: `0.1.0`

| | |
|---|---|
| Paquete | `workflow/` (skills + registro + CLI + extensión de Ely) |
| Consumidores | CLI `workflow` · extensión `angel.workflow` de Ely · cualquier agente que lea el ZIP |
| Fuente de patrones | [affaan-m/ECC](https://github.com/affaan-m/ECC) @ `b38be6a` (MIT) |
| Estado | Categoría `ingenieria` activa · resto declaradas como `pendiente` |

---

## 1. Qué es una skill aquí

Una **skill** es un procedimiento reutilizable, con disparador explícito y
criterio de salida **verificable**. No es documentación, no es un ensayo y no es
un prompt suelto.

Una skill se justifica solo si cumple las tres:

1. **Disparador**: existe una situación reconocible ("el build falla", "voy a
   escribir un módulo nuevo") que dice *cuándo* usarla.
2. **Procedimiento**: pasos ordenados que otra persona podría ejecutar sin
   preguntarte nada.
3. **Salida verificable**: al final hay algo que se puede comprobar (un test que
   pasa, un comando que devuelve 0, una lista con evidencia).

Si falla una de las tres, no es una skill: es una nota → va a `docs/`, no a
`workflow/skills/`.

---

## 2. Contrato del paquete (lo que el código puede asumir)

```text
workflow/
├── EXTENSION-STANDARD.md      ← este archivo (contrato humano y del arnés)
├── categories.json            ← registro: única fuente de verdad de categorías y skill ids
├── skills/<categoria>/<skill>/SKILL.md
├── bin/workflow.mjs           ← CLI (Node ≥ 18, sin dependencias)
├── src/                       ← motor: registry, validate, pack
├── ely-extension/             ← puente con Ely (ely-extension.json + main.js)
└── README.md                  ← cómo se usa el paquete
```

**Reglas de estructura — obligatorias**

| Regla | Detalle |
|---|---|
| Ruta canónica | `workflow/skills/<categoria>/<skill-id>/SKILL.md` |
| Id de skill | `^[a-z0-9]+(-[a-z0-9]+)*$`, único en todo el paquete, estable |
| Id de categoría | igual que el de skill; debe existir en `categories.json` |
| Registro | toda skill instalada **debe** figurar en `categories.json`; una skill en disco que no está en el registro es un error de validación |
| Frontmatter | obligatorio en `SKILL.md`, ver §4 |
| Tamaño | `SKILL.md` ≤ 400 líneas; si crece, se parte en `references/` |
| Colocación | una skill vive en **una sola** categoría (la de su disparador principal) |

---

## 3. Anatomía de una categoría

Cada categoría declara en `categories.json`:

| Campo | Obligatorio | Para qué |
|---|---|---|
| `id` | sí | segmento de ruta y filtro del CLI |
| `name` | sí | etiqueta visible (español) |
| `description` | sí | qué cubre y qué **no** cubre |
| `status` | sí | `activa` \| `pendiente` \| `congelada` |
| `gate` | no | condición que bloquea el cierre de una tarea en esa categoría |
| `rules` | sí (`[]` permitido) | reglas duras, una frase imperativa cada una |
| `skills` | sí (`[]` permitido) | skills instaladas, con `origin`, `status`, `phase` |
| `pending` | no | ids de ECC que se quieren adoptar después (no son skills todavía) |

`status: "pendiente"` significa **declarada pero vacía**: se puede consultar y
planificar, pero el CLI no la ofrece como cargable.

---

## 4. Frontmatter de `SKILL.md`

```markdown
---
name: tdd-workflow
description: Ciclo RED → GREEN → REFACTOR con puerta de cobertura. Usar cuando se va a escribir implementación nueva o a corregir un defecto. (ver §4.1)
metadata:
  origin: ECC · skills/tdd-workflow
  category: ingenieria
  phase: test
  status: adoptada
  version: 1
---

# TDD Workflow

## Cuándo usar
## Cuándo NO usar
## Procedimiento
## Criterio de salida
## Errores típicos
```

**§4.1 — `description`.** Es el único campo que el modelo lee para decidir si
carga la skill. Debe:

- empezar con el resultado, no con el nombre de la técnica;
- contener el disparador literal `Usar cuando` (o `Use when` en skills en inglés);
- caber en **700 caracteres** y no llevar markdown ni saltos de línea;
- distinguirse de las demás skills de su categoría (si dos descripciones se
  pueden intercambiar, una de las dos sobra).

**§4.2 — `phase`.** Vocabulario cerrado: `plan`, `implement`, `test`, `review`,
`verify`, `meta`. Sirve para ordenar el pipeline y para que el CLI agrupe.

**§4.3 — Prosa.** Español para el texto; inglés solo para términos técnicos
consagrados (`build`, `lint`, `commit`). Sin emojis. Sin "en este documento
vamos a…".

**§4.4 — Secciones obligatorias.** `Cuándo usar`, `Procedimiento`, `Criterio de
salida`. `Cuándo NO usar` y `Errores típicos` son muy recomendables; su ausencia
se marca como aviso, no como error.

---

## 5. Adoptada vs propia

| `status` | Significado | Regla |
|---|---|---|
| `adoptada` | Adaptada de ECC | Se conserva el id original de ECC; `origin` citado; texto reescrito para este repo, no copiado literal |
| `propia` | Creada aquí | `origin: propia` |
| `experimental` | En prueba | No se cuenta como base para otras skills |

Nunca se marca `adoptada` algo que no venga de una fuente citada. Si se reescribe
tanto que ya no se reconoce el original, se marca `propia` igualmente (el
`origin` se conserva como referencia histórica).

---

## 6. Orden de lectura (lo que hace el arnés)

El arnés **no** lee todo el catálogo: sería el mismo error que este repo trata de
evitar.

```text
1. workflow/categories.json        (¿qué categoría aplica?)
2. workflow/skills/<cat>/<skill>/SKILL.md   (solo las de la fase en curso)
3. workflow/EXTENSION-STANDARD.md  (solo si va a ESCRIBIR una skill)
```

Regla de coste: se cargan **como máximo las skills de una fase**; si una tarea
cruza fases, se carga por fase, no de golpe.

---

## 7. Checklist antes de guardar una skill

Errores (bloquean):

- [ ] El id cumple `^[a-z0-9]+(-[a-z0-9]+)*$` y no existe ya en el registro.
- [ ] La ruta es `workflow/skills/<categoria>/<id>/SKILL.md`.
- [ ] Frontmatter con `name`, `description`, `metadata.origin`, `metadata.category`, `metadata.phase`, `metadata.status`.
- [ ] `description` incluye el disparador y cabe en 700 caracteres.
- [ ] Existen las secciones `Cuándo usar`, `Procedimiento`, `Criterio de salida`.
- [ ] El `Criterio de salida` es comprobable (comando, test, artefacto).
- [ ] La skill está registrada en `categories.json` (`workflow validate` en verde).

Avisos (no bloquean, pero se revisan):

- [ ] Falta `Cuándo NO usar`.
- [ ] Falta `Errores típicos`.
- [ ] Supera 250 líneas (¿debería partirse?).
- [ ] Su descripción solapa con otra de la misma categoría.
- [ ] Usa rutas absolutas o nombres de máquina.

---

## 8. Anti-patrones (prohibidos)

| Anti-patrón | Por qué |
|---|---|
| Skill que describe un tema sin procedimiento | No hay forma de saber si se aplicó |
| Skill "paraguas" que hace de todo | El modelo no sabe cuándo dispararla |
| Duplicar ECC entero | 314 skills compiten por el contexto; aquí se adopta por necesidad demostrada |
| Escribir dentro de la skill rutas de `~/.claude` o de otra máquina | Rompe la portabilidad |
| Cambiar el id de una skill ya publicada | Rompe registro, enlaces y el arnés |
| Copiar hooks o scripts de ECC | Están acoplados a su estructura; aquí se reescriben si hacen falta |
| Marcar `adoptada` sin `origin` | Sin atribución no se puede auditar ni actualizar |

---

## 9. Cómo se extiende (procedimiento)

**Añadir una skill a una categoría existente**

1. `workflow plan <categoria>` → ver qué hay y qué falta.
2. Añadir la entrada a `categories.json` (`skills`, no `pending`).
3. Crear `skills/<categoria>/<id>/SKILL.md` siguiendo §4.
4. `workflow validate` → debe salir en verde.

**Añadir una categoría**

1. Entrada nueva en `categories.json` con `status: "pendiente"` y `skills: []`.
2. `workflow plan <nueva>` para revisar el hueco.
3. Al instalar su primera skill, cambiar a `status: "activa"`.

**Cambiar una skill existente**

1. Leer la skill y su `metadata.version`.
2. Aplicar el cambio sin tocar `name` ni `category`.
3. Subir `version` en el frontmatter y anotarlo en `workflow/CHANGELOG.md`.

---

## 10. Validación

`workflow validate` aplica, en este orden: JSON del registro válido → cada skill
del registro existe en disco → cada `SKILL.md` tiene frontmatter parseable →
reglas de §7 (errores) → conteo de avisos. Sin dependencias externas: si el
validador falla, el paquete no se empaqueta ni se publica en Ely.

Códigos de salida: `0` sin errores · `1` errores · `2` avisos presentes con
`--strict`.

---

## 11. Licencia y atribución

ECC es MIT. Las skills `adoptada` conservan el id y citan `origin`; si en el
futuro se incorpora texto literal de ECC, debe incluirse su aviso de copyright
MIT en `workflow/NOTICE.md`. Las skills `propia` son de este repositorio.
