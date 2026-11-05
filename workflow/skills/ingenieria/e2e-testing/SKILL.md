---
name: e2e-testing
description: Pruebas de extremo a extremo sobre la interfaz real — Page Object Model, localizadores estables, aislamiento de tests inestables y artefactos de fallo. Usar cuando el cambio toca un flujo de usuario que los tests unitarios no pueden cubrir.
metadata:
  origin: ECC · skills/e2e-testing
  category: ingenieria
  phase: test
  status: adoptada
  version: 1
---

# E2E Testing

Un test E2E cuesta cien veces más que un unitario y falla por razones que no son
el código. Solo se justifica cuando el riesgo está en la **integración real**:
login, pago, permisos, navegación entre pantallas.

## Cuándo usar

- El cambio toca un flujo que atraviesa UI, red y persistencia.
- Un defecto llegó a producción y los tests unitarios no lo vieron.
- Hay que demostrar que un flujo crítico sigue vivo antes de un release.

## Cuándo NO usar

- Lógica pura o de dominio: ahí va un test unitario (`tdd-workflow`).
- Contratos de API que se pueden probar sin navegador.
- Para "subir la cobertura": los E2E no son una métrica de cobertura.

## Procedimiento

1. **Elegir el flujo por riesgo**, no por comodidad: el que si se rompe cuesta
   dinero, datos o acceso.
2. **Un archivo por flujo**, con `describe` que nombre la capacidad del usuario
   ("el usuario paga con tarjeta", no "test de checkout").
3. **Page Object Model**: cada pantalla en su clase con localizadores y acciones.
   El test no contiene selectores; el page object sí.
4. **Localizadores estables**: `data-testid` o rol accesible. Nunca clases CSS,
   nunca rutas XPath largas, nunca texto que se traduce.
5. **Sin esperas fijas.** Prohibido `waitForTimeout`. Se espera la condición:
   respuesta de red concreta, elemento visible, URL esperada.
6. **Estado limpio por test**: datos propios, sin depender del orden de
   ejecución ni de datos sembrados por otro test.
7. **Repetir para detectar inestabilidad**: ejecutar el archivo 10 veces
   (`--repeat-each=10`). Si falla una de diez, el test está roto, no el código.
8. **Cuarentena explícita**: un test inestable se marca (`fixme` con el número de
   issue), no se ignora en silencio ni se le ponen reintentos para que pase.
9. **Artefactos de fallo activados**: captura, traza y vídeo solo al fallar.

## Criterio de salida

- [ ] Cada flujo crítico tocado tiene su test E2E y pasa de forma repetible
      (10 ejecuciones, 10 verdes).
- [ ] Cero selectores en los archivos de test: están en los page objects.
- [ ] Cero esperas fijas (`waitForTimeout`, `sleep`).
- [ ] Un test inestable está en cuarentena con issue abierto, no con reintentos.
- [ ] En el mensaje del PR se cita el comando exacto y su resultado.

## Errores típicos

| Error | Corrección |
|---|---|
| `waitForTimeout(5000)` para "que cargue" | Esperar la condición real |
| Selector por clase CSS o por texto traducido | `data-testid` o rol accesible |
| Tests que comparten usuario y base de datos | Datos por test, limpieza explícita |
| `retries: 3` para tapar inestabilidad | Diagnosticar la carrera; reintentos solo en CI y con traza |
| Test E2E para validar una función pura | Test unitario, es 100 veces más barato |
| Capturas en todos los tests | Solo en fallo: el resto es ruido y espacio |
| Un test que prueba cinco pantallas | Un test por flujo; al fallar debe decir dónde |
