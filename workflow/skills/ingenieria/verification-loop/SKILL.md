---
name: verification-loop
description: Verificación en seis fases — build, tipos, lint, tests con cobertura, seguridad y revisión del diff — con evidencia real de cada paso. Usar cuando se cierra una tarea, antes de un commit o al recibir un cambio que hay que aceptar o rechazar.
metadata:
  origin: ECC · skills/verification-loop
  category: ingenieria
  phase: verify
  status: adoptada
  version: 1
---

# Verification Loop

Una tarea no está terminada cuando el código parece correcto: está terminada
cuando hay evidencia de que lo es. Este procedimiento produce esa evidencia y
**se detiene en el primer fallo**: no se sigue adelante acumulando deuda.

## Cuándo usar

- Al cerrar cualquier tarea que tocó código.
- Antes de un commit o de abrir un PR.
- Cuando otro agente o persona entrega un cambio y hay que aceptarlo.
- Después de un merge o un rebase.

## Cuándo NO usar

- Cambios que solo tocan texto no ejecutable (un README sin comandos).
- Cuando el pipeline de CI ya ejecutó exactamente estas fases sobre el mismo
  commit: entonces se cita el resultado de CI en lugar de repetirlo.

## Procedimiento

Ejecutar en orden. **Cada fase produce un resultado pegable** (comando +
salida resumida). Si una fase falla, se corrige y se reinicia desde esa fase.

1. **Build.** Compilar o empaquetar el proyecto. Es el filtro más barato: si no
   compila, nada de lo demás importa.
2. **Tipos.** Si el lenguaje tiene chequeo estático (`tsc --noEmit`, `mypy`,
   `go vet`, `cargo check`), ejecutarlo sin escribir artefactos.
3. **Lint y formato.** Con la configuración del repo, sin reformatear archivos
   que no se tocaron.
4. **Tests con cobertura.** Suite completa, no solo el archivo tocado. Anotar
   cobertura del área modificada.
5. **Seguridad.** Buscar secretos en el diff, dependencias nuevas sin justificar,
   entradas sin validar, rutas de fichero construidas con datos externos.
6. **Revisión del diff.** `git diff` leído de arriba abajo con una pregunta:
   ¿esto es lo mínimo que resuelve la tarea? Todo lo que no lo sea, fuera.

## Criterio de salida

- [ ] Las seis fases ejecutadas, con el comando y su resultado anotados.
- [ ] Cero fallos abiertos; los que se decidan posponer, listados como deuda
      explícita con motivo.
- [ ] El diff no contiene archivos temporales, logs, binarios ni secretos.
- [ ] Alguien distinto del autor (humano o agente con contexto fresco) leyó el
      diff: es la fase 6.

## Errores típicos

| Error | Corrección |
|---|---|
| Saltar a tests sin compilar | Orden obligatorio: falla antes y más barato |
| "En mi máquina pasa" | Anotar el comando y el entorno; si el repo tiene CI, es CI quien decide |
| Tests en verde tras borrar un test que fallaba | Comprobar que el número de tests no bajó |
| Arreglar el lint reformateando medio repo | Formatear solo lo tocado |
| Cerrar con un TODO "para después" sin dueño | O se hace, o se registra como deuda con motivo |
| Revisar el diff con el mismo contexto que lo escribió | Pedir revisión fresca (`code-review`) |
