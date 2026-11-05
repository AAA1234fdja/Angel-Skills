# Angel-Skills

Skills y herramientas de ingeniería para agentes de código, empaquetadas,
ejecutables y validables.

| Qué | Dónde |
|---|---|
| **Documento principal** (para qué existe, recorrido, reglas) | [`workflow/WORKFLOW.md`](workflow/WORKFLOW.md) |
| **Estándar que se lee antes de editar una skill** | [`workflow/EXTENSION-STANDARD.md`](workflow/EXTENSION-STANDARD.md) |
| **Agentes y subagentes** (un agente es una API) | [`workflow/AGENTS.md`](workflow/AGENTS.md) |
| **Paquete completo** (registro, runtime, tests, extensión de Ely) | [`workflow/README.md`](workflow/README.md) |
| **Registro de categorías y skill ids** | [`workflow/categories.json`](workflow/categories.json) |
| Inventario del repo del que se adoptaron los patrones | [`ECC-INVENTARIO.md`](ECC-INVENTARIO.md) |

## Arranque

```bash
cd workflow
python3 -m angel.cli list                  # skills por categoría, con sus tools
python3 -m angel.cli route --need "the build is broken"   # quién responde y por qué
python3 -m angel.cli run --need "the build is broken"     # plan → tools → veredicto
python3 -m angel.cli validate --strict     # registro ⇄ disco, sin avisos
python3 -m angel.cli tool --self-test      # las 41 herramientas sobre su muestra
python3 -m angel.cli agents validate --strict             # cartas, aristas, ciclos
python3 -m angel.cli agents plan --agent isa-planner --need "revisar este diff"
python3 -m unittest discover -s tests -t tests            # 174 tests
python3 -m angel.cli pack --out dist/workflow.zip         # el paquete en un zip
```

Python 3.10+ y nada más: sin dependencias, sin red, sin servicios.

## El agente

Una skill es un procedimiento; un agente es el servicio que lo ejecuta. Cada agente
publica una carta (`workflow/agents/<id>/agent.json`) y responde en una dirección
con pin: `agent://acme/xev-builder@1.0.0#3d6252a9`. La autoridad solo se estrecha
hacia abajo —un subagente recibe la intersección de lo que su padre tiene y lo que
la arista permite—, los ciclos se rechazan al cargar el roster y toda llamada deja
un árbol y un journal encadenado por hashes. Referencia: [`workflow/AGENTS.md`](workflow/AGENTS.md).

## La regla

Una skill es una **carpeta**, no un markdown: `SKILL.md` (el procedimiento) +
`skill.json` (cuándo cargarla y qué ejecutar) + `tools/` (lo ejecutable). Ninguna
entra sin pasar `validate --strict`: disparador explícito, procedimiento, criterio
de salida comprobable y herramienta con muestra ejecutable. El registro manda en
las dos direcciones: una skill en disco sin registrar es un error, y una registrada
sin carpeta también.

## Estado

**0.4.0** · 44 skills en 11 categorías activas · 41 herramientas ejecutables ·
5 contratos versionados · 6 agentes con dirección y jerarquía de subagentes ·
174 tests en verde · extensión opcional de Ely.
Detalle en [`workflow/CHANGELOG.md`](workflow/CHANGELOG.md).
