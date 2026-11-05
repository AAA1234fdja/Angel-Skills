---
name: tdd-workflow
description: Ciclo RED → GREEN → REFACTOR con puerta de cobertura antes de dar una tarea por terminada. Usar cuando se va a escribir implementación nueva, corregir un defecto o cambiar comportamiento existente.
metadata:
  origin: ECC · skills/tdd-workflow
  category: ingenieria
  phase: test
  status: adoptada
  version: 1
---

# TDD Workflow

Escribir el test que falla primero no es una ceremonia: es la única forma barata
de saber que el test puede fallar. Un test escrito después de la implementación
pasa siempre, y por eso no verifica nada.

## Cuándo usar

- Implementación nueva con comportamiento observable.
- Corrección de un defecto (el defecto se reproduce como test antes del parche).
- Cambio de comportamiento en código existente (el test viejo se actualiza primero).

## Cuándo NO usar

- Cambios puramente cosméticos sin comportamiento (formato, renombrado interno).
- Configuración o documentación sin lógica.
- Exploración desechable: si el código se va a borrar, no se testea.
- Cuando el proyecto no tiene runner de tests: primero se elige uno (ver
  `verification-loop`), no se escribe implementación a ciegas.

## Procedimiento

1. **Definir la interfaz antes del cuerpo.** Nombre de la función o endpoint,
   entradas, salidas y errores esperados. Sin esto, el test no se puede escribir.
2. **RED — escribir un test que falle por la razón correcta.** Ejecutarlo y leer
   el mensaje: debe fallar porque falta la implementación, no por un import mal
   puesto o un typo. Un test que falla por la razón equivocada no cuenta.
3. **GREEN — la implementación mínima.** Nada de generalizar antes de tiempo. Se
   permite código feo con tal de que el test pase y el resto siga pasando.
4. **Verificar que los demás tests siguen verdes.** Si algo se rompió, se
   arregla ahora, no después.
5. **REFACTOR — limpiar con la red puesta.** Sin cambiar comportamiento; los
   tests se ejecutan después de cada paso pequeño.
6. **Ampliar casos**: errores, límites, entradas vacías, concurrencia si aplica.
   Cada caso nuevo vuelve al paso 2.
7. **Cobertura**: medirla solo como diagnóstico. El objetivo es que cada rama
   nueva tenga un caso que la recorra, no alcanzar un porcentaje.

## Criterio de salida

- [ ] El test nuevo **falló** primero y se vio el mensaje de fallo (queda en el
      historial de la sesión).
- [ ] Ahora pasa, y el runner completo sigue en verde (comando ejecutado y
      pegado en la respuesta final).
- [ ] La cobertura del archivo tocado no baja.
- [ ] Si es un defecto: existe un test que lo reproduce y falla sin el parche.

## Errores típicos

| Error | Corrección |
|---|---|
| Test escrito después de implementar | Borrar el test y reescribirlo viéndolo fallar |
| Test que verifica la implementación (mocks internos) | Verificar la salida observable |
| Test que falla por error de entorno | Arreglar el entorno; el fallo no es la señal que buscamos |
| "Ya lo probé a mano" | Probar a mano no deja evidencia reproducible: se convierte en test |
| Buscar el 100 % de cobertura | Cubrir ramas nuevas; el porcentaje es diagnóstico, no meta |
| Un test para tres comportamientos | Un test por comportamiento; si falla, debe decir cuál |
