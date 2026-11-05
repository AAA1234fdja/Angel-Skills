---
name: skill-authoring
description: Procedimiento para crear o editar una skill de este paquete cumpliendo EXTENSION-STANDARD.md — registro, frontmatter, secciones y validación. Usar cuando el arnés o una persona va a añadir, modificar o mover algo dentro de workflow/.
metadata:
  origin: propia
  category: ingenieria
  phase: meta
  status: propia
  version: 1
---

# Skill Authoring

Esta skill existe para que el propio paquete no se degrade. Cada vez que un
agente "mejora" una skill sin seguir el contrato, el registro y la realidad se
separan, y el arnés empieza a cargar cosas que ya no existen.

## Cuándo usar

- Añadir una skill nueva a una categoría.
- Editar o corregir una skill existente.
- Crear una categoría nueva.
- Cuando `workflow validate` falla y hay que entender por qué.

## Cuándo NO usar

- Para escribir documentación general: eso va a `docs/`, no a `skills/`.
- Para cambiar el estándar en sí (`EXTENSION-STANDARD.md`): es una decisión de
  diseño, se discute antes y se sube `version` del paquete.

## Procedimiento

1. **Decidir si es skill** con las tres pruebas de §1 del estándar: disparador,
   procedimiento, salida verificable. Si falla una, parar.
2. **Elegir categoría** mirando `categories.json`. Una skill vive en una sola
   categoría: la de su disparador principal, no la de su tema.
3. **Comprobar que no existe** algo equivalente: `workflow list`, `workflow plan
   <categoria>` y lectura de las descripciones vecinas. Si dos descripciones se
   pueden intercambiar, una de las dos sobra.
4. **Registrar antes de escribir**: añadir la entrada a `categories.json` con
   `id`, `origin`, `status`, `phase` y `description`.
5. **Escribir `SKILL.md`** en `skills/<categoria>/<id>/` con el frontmatter de
   §4 y las secciones obligatorias. Máximo 400 líneas; si crece, `references/`.
6. **Pasar el checklist** de §7 del estándar, incluidos los avisos.
7. **Validar**: `workflow validate`. Sin verde no hay commit.
8. **Anotar el cambio** en `workflow/CHANGELOG.md` y subir `metadata.version` en
   la skill tocada.

## Criterio de salida

- [ ] `workflow validate` termina con código 0.
- [ ] La skill está registrada y el `name` del frontmatter coincide con el id.
- [ ] `description` incluye el disparador y cabe en 700 caracteres.
- [ ] Existen `Cuándo usar`, `Procedimiento` y `Criterio de salida`.
- [ ] El criterio de salida es comprobable con un comando o un artefacto.
- [ ] `CHANGELOG.md` actualizado y `metadata.version` incrementada si era edición.

## Errores típicos

| Error | Corrección |
|---|---|
| Crear la carpeta y olvidar el registro | `validate` debe fallar: registra siempre primero |
| Copiar una skill de ECC tal cual | Reescribir para este repo y citar `origin` |
| Cambiar el `name` al editar | El id es estable; renombrar rompe el registro |
| Skill sin `Criterio de salida` | No es una skill, es una nota |
| Descripción que empieza por el nombre de la técnica | Empezar por el resultado que produce |
| Añadir una categoría con una sola skill "por simetría" | Una categoría se justifica con un hueco real |
