---
name: code-review
description: Revisión de un diff con contexto fresco — defectos reales ordenados por severidad, sin reescribir el diseño del autor. Usar cuando se va a abrir un PR, al recibir un cambio ajeno o cuando el mismo agente lleva demasiado tiempo con el mismo código.
metadata:
  origin: ECC · patrón reviewer (agents/code-reviewer, skills de revisión)
  category: ingenieria
  phase: review
  status: adoptada
  version: 1
---

# Code Review

El valor de una revisión depende de que quien revisa **no** sea quien escribió.
Un agente que revisa su propio contexto repite sus mismos puntos ciegos; por eso
esta skill se ejecuta sobre el diff, con la menor memoria posible de la
conversación que lo produjo.

## Cuándo usar

- Antes de abrir o mergear un PR.
- Al recibir código de otro agente o de otra persona.
- Cuando una tarea se cerró "en verde" pero algo no cuadra.

## Cuándo NO usar

- Antes de que exista diff (no hay nada que revisar).
- Como sustituto de tests: la revisión detecta lo que los tests no cubren, no
  reemplaza su ejecución (`verification-loop`).

## Procedimiento

1. **Leer el diff completo primero, sin comentar nada.** Entender la intención
   antes de juzgar las líneas.
2. **Comprobar la intención contra el pedido.** ¿El cambio resuelve lo que se
   pidió? ¿Hace algo más que no se pidió?
3. **Clasificar cada hallazgo** con una de estas etiquetas:
   - `bloqueante` — bug, pérdida de datos, secreto expuesto, rompe contrato.
   - `importante` — deuda que se pagará pronto, comportamiento no cubierto.
   - `menor` — estilo, nombres, comentarios.
   - `pregunta` — no es un defecto: falta contexto para decidir.
4. **Un comentario por hallazgo, con la línea y el porqué.** Sin reescribir el
   diseño del autor dentro del comentario.
5. **Proponer el parche mínimo** solo cuando sea evidente; si no, describir la
   condición que debe cumplirse.
6. **Cerrar con un veredicto**: aprobar, aprobar con cambios menores, o pedir
   cambios. Sin veredicto, la revisión no sirve.

## Criterio de salida

- [ ] Cada hallazgo tiene etiqueta de severidad y referencia a línea o archivo.
- [ ] Cero `bloqueante` sin resolver antes del merge.
- [ ] Veredicto explícito al final.
- [ ] No se ha comentado nada que un linter o un test ya cubran.
- [ ] Se ha revisado también lo que **falta** (tests ausentes, error no
      manejado), no solo lo que hay.

## Errores típicos

| Error | Corrección |
|---|---|
| Lista de veinte "menor" y ningún veredicto | Priorizar: bloqueantes primero, veredicto al final |
| Revisar con el mismo contexto que generó el código | Revisión en sesión limpia, solo con el diff |
| Reescribir el módulo en un comentario | Señalar el defecto y dejar decidir al autor |
| Aprobar "porque los tests pasan" | Los tests no cubren diseño ni seguridad |
| Comentar estilo que el formateador ya corrige | Ejecutar el formateador |
| Mezclar revisión de código con revisión de producto | Alcance: el diff, no el roadmap |
