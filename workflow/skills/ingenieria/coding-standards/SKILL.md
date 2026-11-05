---
name: coding-standards
description: Convenciones base de código — nombres, legibilidad, inmutabilidad y tamaño de unidad — para que una revisión no discuta estilo. Usar cuando se crean módulos nuevos, al refactorizar o cuando el código existente no tiene convención escrita.
metadata:
  origin: ECC · skills/coding-standards
  category: ingenieria
  phase: implement
  status: adoptada
  version: 1
---

# Coding Standards

Las convenciones no existen para que el código quede bonito: existen para que
una revisión discuta **qué hace** el código y no **cómo se escribe**. Si el repo
ya tiene una convención, esa gana; este documento solo cubre lo que no suele
estar escrito.

## Cuándo usar

- Crear un módulo, paquete o archivo nuevo.
- Refactorizar código que se va a tocar en varias sesiones.
- Revisar código sin convención declarada en el repo.

## Cuándo NO usar

- Cuando el repo tiene un linter y un formateador configurados: se ejecutan las
  herramientas, no se discute el estilo a mano.
- Estilo de un archivo generado o vendorizado.

## Procedimiento

1. **Buscar la convención existente** antes de inventar una: `ls`, leer dos o
   tres archivos vecinos, buscar `.editorconfig`, `eslint`, `ruff`, `gofmt`.
2. **Nombres.** El nombre dice qué es, no cómo se implementa: `invoiceTotal`
   (valor) vs `calculateInvoice` (acción) vs `isPaid` (booleano). Sin
   abreviaturas que no estén ya en el dominio.
3. **Unidad pequeña.** Función que cabe en una pantalla y hace una cosa. Si
   necesita un comentario "parte 1 / parte 2", son dos funciones.
4. **Inmutabilidad por defecto.** Preferir `const`, valores nuevos y funciones
   puras; mutar solo con motivo (rendimiento medido, buffer explícito).
5. **Errores explícitos.** Un fallo se devuelve o se lanza con contexto; nunca
   se traga en silencio ni se convierte en `null` sin decirlo en el nombre.
6. **Comentarios de porqué, no de qué.** El código dice qué hace; el comentario
   dice por qué se eligió así, o qué se rompe si se cambia.
7. **Dependencias.** Antes de añadir una, ver `search-first`; después, justificar
   en el propio commit por qué no bastaba lo que ya había.

## Criterio de salida

- [ ] El código nuevo sigue la convención encontrada en el paso 1 (o la de este
      documento si no había ninguna).
- [ ] No hay funciones que hagan dos cosas ni nombres engañosos.
- [ ] Los errores no se silencian.
- [ ] Cada dependencia nueva está justificada en el commit.
- [ ] Lint y formato en verde sin excepciones añadidas al archivo de config.

## Errores típicos

| Error | Corrección |
|---|---|
| Añadir una regla de linter `off` para que pase | Arreglar el código o cambiar la regla en el PR de configuración |
| Renombrar por gusto dentro de un PR funcional | Renombrado en commit aparte |
| Comentarios que repiten el código | Comentario de intención o se borra |
| `try { … } catch (e) {}` para "que no falle" | Fallar rápido con contexto |
| Módulo de 900 líneas "porque está todo junto" | Partir por responsabilidad, con tests que lo respalden |
