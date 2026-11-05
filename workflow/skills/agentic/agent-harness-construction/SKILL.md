---
name: agent-harness-construction
description: Diseñar el espacio de acción de un agente — herramientas, granularidad, formato de observación y recuperación de errores — para subir la tasa de tareas completadas. Usar cuando se define o revisa el conjunto de herramientas, el action space o el formato de observaciones de un agente.
metadata:
  origin: ECC · skills/agent-harness-construction
  category: agentic
  phase: plan
  status: adoptada
  version: 1
---

# Agent Harness Construction

La calidad de un agente no la decide solo el modelo: la deciden cuatro cosas que
se pueden diseñar — el espacio de acción, la observación, la recuperación y el
presupuesto de contexto. Este procedimiento las diseña en ese orden.

## Cuándo usar

- Se define el conjunto de herramientas de un agente nuevo.
- Un agente falla en tareas que "debería" poder hacer.
- Se revisa por qué un agente repite llamadas, elige mal la herramienta o se
  queda sin contexto a mitad de tarea.

## Cuándo NO usar

- Cuando el problema es el prompt de personalidad o el tono: eso es otra capa.
- Cuando no hay forma de medir si la tarea se completó (`eval-harness` primero).

## Procedimiento

1. **Definir qué es "tarea completada"** antes de diseñar herramientas. Sin
   criterio de éxito, el diseño no es verificable.
2. **Espacio de acción**: nombres estables y explícitos; entradas con esquema y
   estrechas; salidas con forma determinista. Nada de herramientas "que hacen
   todo" salvo que el aislamiento sea imposible.
3. **Granularidad** según riesgo:
   - micro-herramienta para operaciones de alto impacto (desplegar, migrar,
     tocar permisos): un paso, un efecto, confirmación explícita;
   - herramienta media para ciclos de leer / editar / buscar;
   - macro-herramienta solo cuando el coste dominante son los viajes de ida y vuelta.
4. **Observación**: toda respuesta de herramienta devuelve `status`
   (`success|warning|error`), `summary` de una línea, `next_actions` y
   `artifacts` (rutas o ids). Una observación sin siguiente paso deja al agente
   adivinando.
5. **Contrato de recuperación**: cada ruta de error incluye pista de causa raíz,
   instrucción de reintento seguro y condición de parada explícita. "Error 500"
   no es una observación, es un callejón.
6. **Presupuesto de contexto**: system prompt mínimo e invariante; la guía larga
   vive en skills que se cargan bajo demanda; referencias a archivos antes que
   documentos inline; compactar en fronteras de fase, no por umbral de tokens.
7. **Medir**: tasa de completado, reintentos por tarea, pass@1 y pass@3, y coste
   por tarea completada. Sin estos cinco números no hay mejora demostrable.

## Criterio de salida

- [ ] Existe una definición escrita de "tarea completada" y cómo se comprueba.
- [ ] Cada herramienta tiene esquema de entrada y forma de salida documentados.
- [ ] Toda herramienta devuelve los cuatro campos de observación.
- [ ] Toda ruta de error tiene reintento seguro y condición de parada.
- [ ] El system prompt no contiene guía que pueda vivir en una skill.
- [ ] Se midieron los cinco indicadores del paso 7 antes y después del cambio.

## Errores típicos

| Error | Corrección |
|---|---|
| Muchas herramientas con semántica solapada | El agente elige mal: fusionar o eliminar |
| Salida opaca ("algo falló") | `status` + `summary` + `next_actions` |
| Herramienta de despliegue que hace tres cosas | Partir en pasos con confirmación |
| Meter la guía de estilo entera en el system prompt | Skill cargada bajo demanda |
| Compactar a un número fijo de tokens | Compactar en fronteras de fase |
| Añadir herramientas sin volver a medir | Cada cambio se mide igual que la base |
| Diseñar para el caso ideal | Diseñar el contrato de error primero |
