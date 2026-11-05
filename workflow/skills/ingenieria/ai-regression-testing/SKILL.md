---
name: ai-regression-testing
description: Convertir cada defecto y cada cambio generado por IA en un test de regresión permanente, con paridad entre entorno aislado y real. Usar cuando el agente corrige un defecto o cuando un cambio generado tiene que quedar cubierto para siempre.
metadata:
  origin: ECC · skills/ai-regression-testing
  category: ingenieria
  phase: test
  status: adoptada
  version: 1
---

# AI Regression Testing

Cuando un agente genera código rápido, el riesgo deja de ser "no funciona" y
pasa a ser **"funcionaba y dejó de funcionar"**. Esta skill convierte cada
defecto en una red que no se puede volver a romper sin que suene.

## Cuándo usar

- Se ha corregido un defecto: el test que lo reproduce es obligatorio.
- Un cambio generado por IA toca código con historial de fallos.
- Se quiere un conjunto de pruebas que corra sin base de datos ni servicios
  externos (entorno aislado).

## Cuándo NO usar

- Para comportamiento nuevo que aún no existe: eso es un test de feature
  (`tdd-workflow`).
- Cuando el defecto es de entorno o de despliegue y no es reproducible en test.

## Procedimiento

1. **Reproducir el defecto en un test que falla**, con el caso mínimo real: los
   datos exactos que lo provocaron (o un subconjunto anonimizado).
2. **Entorno aislado**: el test no depende de base de datos viva, red ni
   credenciales. Se sustituyen por dobles que devuelven la misma forma que el
   sistema real.
3. **Verificar paridad**: comprobar que el doble responde igual que el sistema
   real en ese caso; si difieren, el test verde no significa nada.
4. **Añadir el caso al registro de regresiones** agrupado por área, con el
   número de issue en el nombre o el comentario.
5. **Ejecutar la regresión antes de cada cambio generado**, no solo en CI: es lo
   que detecta que el agente tocó algo que no debía.
6. **Cuando el test falla, primero se pregunta si el código o el test están
   mal.** Un test viejo puede estar obsoleto por un cambio de contrato legítimo:
   entonces se actualiza en el mismo commit y se explica.

## Criterio de salida

- [ ] El defecto tiene un test que **fallaba antes** del parche y pasa después.
- [ ] El test corre en un entorno sin servicios externos.
- [ ] La paridad del doble está comprobada o documentada como supuesto.
- [ ] El nombre o comentario del test referencia el issue.
- [ ] La suite de regresión se ejecuta antes de aceptar cualquier cambio generado.

## Errores típicos

| Error | Corrección |
|---|---|
| Arreglar el bug y no dejar test | Sin test, el bug vuelve en tres semanas |
| Test acoplado a la implementación (mocks internos) | Verificar la salida observable |
| Doble que no se parece al sistema real | Comprobar forma y errores del contrato |
| Test de regresión que necesita base de datos real | Sustituir por doble o usar contenedor efímero |
| Borrar un test porque "ya no aplica" | Actualizarlo al contrato nuevo y explicarlo |
| Acumular 2000 tests lentos | Agrupar por área y mantener el conjunto rápido |
