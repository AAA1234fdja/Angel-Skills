---
name: build-fix
description: Diagnóstico y corrección incremental de errores de build, tipos y linter — un error por ciclo, con causa raíz antes del parche. Usar cuando el build falla, el chequeo de tipos no pasa o el linter bloquea el cierre.
metadata:
  origin: ECC · agents/build-error-resolver + commands/build-fix
  category: ingenieria
  phase: verify
  status: adoptada
  version: 1
---

# Build Fix

Un build roto no se arregla a base de parches: se arregla entendiendo el primer
error. Los demás suelen ser consecuencia. Por eso el ciclo es **uno por vez**.

## Cuándo usar

- Compilación fallida, errores de tipos o de resolución de módulos.
- Linter bloqueante que impide cerrar la tarea.
- Dependencia rota tras un cambio de versión o un merge.

## Cuándo NO usar

- Cuando el fallo es de entorno (falta un binario, SDK, credenciales): eso se
  arregla en el entorno, no en el código.
- Cuando el fallo viene de código vendorizado o generado: se regenera.

## Procedimiento

1. **Reproducir el fallo con un comando exacto** y guardar la salida completa.
   Sin reproducción no hay diagnóstico, solo adivinación.
2. **Leer el primer error, no el último.** Copiar el mensaje y la ruta.
3. **Explicar la causa raíz en una frase.** Si no se puede, se busca más
   contexto (firma de la función, versión de la dependencia, commit que lo
   introdujo: `git log -S`).
4. **Aplicar el parche mínimo** que elimina la causa, no el síntoma. Nada de
   `any`, `# type: ignore`, `@ts-expect-error` ni `--no-verify` para pasar.
5. **Reejecutar el mismo comando.** Si el número de errores no bajó, el parche
   era el equivocado: revertir y volver al paso 3.
6. **Repetir** hasta cero, y luego ejecutar la suite completa (puede haber
   errores enmascarados).
7. Si el parche obliga a tocar una interfaz pública, anotarlo: es un cambio de
   contrato, no una corrección.

## Criterio de salida

- [ ] El comando que fallaba ahora termina con código 0, y su salida está
      citada en la respuesta final.
- [ ] Cero supresiones nuevas (`any`, `ignore`, `expect-error`, `--no-verify`).
- [ ] La causa raíz está escrita en el mensaje del commit.
- [ ] La suite completa sigue en verde.
- [ ] Si cambió una interfaz pública, está documentado en el diff.

## Errores típicos

| Error | Corrección |
|---|---|
| Silenciar el error con un cast | Arreglar el tipo real en el origen |
| Arreglar diez errores a la vez | Uno por ciclo, verificando cada vez |
| Reinstalar dependencias "por si acaso" | Solo si el error apunta al árbol de dependencias |
| Tocar la configuración del compilador para que pase | Cambiar config es un PR aparte con motivo |
| Commitear con `--no-verify` | Prohibido: el hook existe por algo |
