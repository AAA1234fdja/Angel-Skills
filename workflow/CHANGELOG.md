# CHANGELOG · workflow

Formato: fecha · versión del paquete · cambio.

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
- `validate` en verde: 7 skills, 0 errores, 0 avisos.

Pendiente para 0.2.0: adoptar las skills `pendiente` de `agentic` una vez
acordado el criterio de evaluación; decidir si `datos-infra` se parte en dos.
