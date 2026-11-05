# Angel-Skills

Skills y herramientas de ingeniería para agentes de código, empaquetadas y
validables.

| Qué | Dónde |
|---|---|
| **Paquete de skills** (registro, estándar, CLI, extensión de Ely) | [`workflow/`](workflow/README.md) |
| **Estándar que se lee antes de editar una skill** | [`workflow/EXTENSION-STANDARD.md`](workflow/EXTENSION-STANDARD.md) |
| **Registro de categorías y skill ids** | [`workflow/categories.json`](workflow/categories.json) |
| Inventario del repo del que se adoptaron los patrones | [`ECC-INVENTARIO.md`](ECC-INVENTARIO.md) |

## Arranque

```bash
node workflow/bin/workflow.mjs plan        # qué hay y qué falta por categoría
node workflow/bin/workflow.mjs list        # skills instaladas
node workflow/bin/workflow.mjs validate    # debe estar en verde
```

## La regla

Ninguna skill entra sin pasar `validate`: disparador explícito, procedimiento y
**criterio de salida comprobable**. El registro manda: una skill en disco que no
está en `categories.json` es un error, no un detalle.

## Estado

`ingenieria` (11 skills) y `agentic` (3) activas · `seguridad`, `datos-infra`,
`producto` y `contenido` declaradas como pendientes.
