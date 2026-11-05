---
name: eval-harness
description: Evaluación dirigida por evals — criterios de éxito definidos antes de tocar el agente, calificadores por código/modelo/humano y métricas pass@k y pass^k. Usar cuando se cambia un prompt, una herramienta o un modelo y hay que decidir con números si mejoró.
metadata:
  origin: ECC · skills/eval-harness
  category: agentic
  phase: verify
  status: adoptada
  version: 1
---

# Eval Harness

Si no puedes decir si un cambio en el agente lo mejoró, no lo has mejorado: lo
has cambiado. Los evals son los tests unitarios del desarrollo con IA, y se
escriben **antes** de la modificación.

## Cuándo usar

- Se cambia un prompt de sistema, una herramienta, un modelo o una versión.
- Hay que decidir entre dos configuraciones de agente.
- Un agente se comporta distinto según el día y hace falta una medida estable.

## Cuándo NO usar

- Para lógica de negocio determinista: eso es un test normal.
- Cuando no hay forma de ejecutar la tarea de forma repetible: primero se
  construye el entorno reproducible.

## Procedimiento

1. **Escribir la tarea y el criterio de éxito antes del cambio.** Cada eval es
   una tarea concreta con criterios marcables, no una impresión general.
2. **Clasificar el eval**:
   - *capacidad* — algo que el agente no sabía hacer y ahora debería;
   - *regresión* — algo que ya hacía y no puede dejar de hacer; se guarda la
     referencia (commit, versión de modelo) como línea base.
3. **Elegir el calificador**, del más barato al más caro:
   - **código**: grep, test, build, esquema, salida esperada → determinista y
     preferible siempre que se pueda;
   - **modelo**: otro modelo puntúa con una rúbrica explícita (1–5 con motivos);
     se usa para salidas abiertas y se valida contra humanos;
   - **humano**: solo para lo que ni código ni modelo pueden decidir; se reserva.
4. **Ejecutar k veces** por eval (k ≥ 3). Una sola pasada no dice nada sobre
   fiabilidad.
5. **Calcular las métricas**:
   - `pass@k` — al menos un éxito en k intentos (capacidad);
   - `pass^k` — **todos** los k intentos salen bien (fiabilidad; es el listón
     duro);
   - coste por tarea completada y reintentos por tarea.
6. **Comparar contra la base** con el mismo conjunto, mismo modelo de
   calificación y mismo entorno.
7. **Registrar el resultado** con fecha, versión y diff: un eval sin registro no
   sirve para comparar la semana siguiente.

## Criterio de salida

- [ ] Cada eval tiene tarea, criterio de éxito y calificador explícitos.
- [ ] La línea base está registrada antes del cambio.
- [ ] k ≥ 3 ejecuciones por eval; se reporta `pass@k` y `pass^k`.
- [ ] Se reporta coste por tarea completada además de la tasa de éxito.
- [ ] El veredicto es una decisión: se queda el cambio, se revierte, o se
      reformula. Sin veredicto no hay evaluación.
- [ ] Los evals de regresión quedan versionados para la próxima vez.

## Errores típicos

| Error | Corrección |
|---|---|
| Una sola ejecución y conclusión | k ≥ 3; reportar `pass^k` |
| Calificador por modelo sin rúbrica | Rúbrica con criterios y escala fijos |
| Cambiar el eval para que el cambio pase | El eval se escribe antes, y no se toca |
| Comparar contra una base de otro entorno | Mismo conjunto, mismo entorno |
| Medir solo éxito y olvidar coste | Coste por tarea completada |
| Evals que dependen del estado del repo | Entorno reproducible y limpio por corrida |
| Confundir capacidad con regresión | Series separadas: una sube, la otra no puede bajar |
