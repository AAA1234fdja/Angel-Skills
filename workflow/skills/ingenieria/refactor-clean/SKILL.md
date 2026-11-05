---
name: refactor-clean
description: Eliminación verificada de código muerto y consolidación de duplicados, cambio a cambio y con la suite en verde. Usar cuando el repo acumula funciones sin uso, imports huérfanos o dos implementaciones de lo mismo.
metadata:
  origin: ECC · agents/refactor-cleaner + commands/refactor-clean
  category: ingenieria
  phase: implement
  status: adoptada
  version: 1
---

# Refactor Clean

Borrar código es la operación más fácil de romper y la más difícil de deshacer.
Por eso aquí se borra **una cosa a la vez, con evidencia de que nadie la usa y la
suite en verde después de cada paso**.

## Cuándo usar

- Antes de una funcionalidad nueva que va a vivir en un módulo ya saturado.
- Cuando dos módulos implementan lo mismo y hay que quedarse con uno.
- Cuando el agente detecta imports, variables o rutas sin uso.

## Cuándo NO usar

- Durante la corrección de un defecto: primero se arregla, después se limpia.
- Sobre código que se publica como API (`export`, endpoint, ruta): puede tener
  consumidores fuera del repo, y ahí "sin uso" no se puede verificar con grep.
- Antes de un release: la limpieza no es un cambio seguro de última hora.

## Procedimiento

1. **Fijar la línea base**: suite completa en verde y anotada. Sin esto, no se
   puede distinguir lo que rompió la limpieza de lo que ya estaba roto.
2. **Detectar candidatos** con varias fuentes, no una: búsqueda de referencias,
   linter de código muerto, cobertura de tests (lo que nunca se ejecuta), y el
   historial (`git log -S`).
3. **Clasificar cada candidato**:
   - `seguro` — sin referencias y no exportado.
   - `revisar` — referencias solo en tests: puede ser un test viejo o un uso real.
   - `no tocar` — API pública, código generado, migración pendiente.
4. **Un candidato por commit**, del más simple al más arriesgado. Commit que no
   compila ni se explica, se revierte.
5. **Consolidar duplicados solo si son equivalentes de verdad**: comparar
   comportamiento con tests, no a ojo. Si difieren en algo, no son duplicados.
6. **Reejecutar la suite después de cada paso.** Si algo cae, se revierte ese
   paso y se replantea; no se acumulan roturas.
7. **Verificar el resultado global**: menos líneas, mismos tests verdes, y
   ninguna API pública eliminada sin aviso.

## Criterio de salida

- [ ] La línea base estaba en verde y se citó.
- [ ] Cada borrado tiene evidencia de ausencia de uso (comando y resultado).
- [ ] Cero eliminaciones en API pública sin marcar como cambio de contrato.
- [ ] La suite sigue en verde, con el mismo número de tests (o más, nunca menos).
- [ ] El diff total reduce líneas y se lee en menos de dos minutos.

## Errores típicos

| Error | Corrección |
|---|---|
| "Seguro que no se usa" sin buscar | Buscar, y anotar el comando |
| Borrar todo lo que el linter marca | El linter no ve uso dinámico (`importlib`, handlers por string) |
| Limpiar y arreglar un bug en el mismo commit | Un propósito por commit |
| Consolidar dos funciones que "son iguales" | Comparar con tests; suelen diferir en errores o bordes |
| Borrar tests que fallan | Un test que falla señala algo; se investiga |
| Refactor grande sin checkpoint | Commits pequeños: se puede volver atrás |
