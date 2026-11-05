---
name: search-first
description: Buscar en npm, PyPI, GitHub y el propio repo antes de escribir una dependencia, un helper o un módulo nuevo. Usar cuando aparece la tentación de implementar algo que probablemente ya existe o ya está en el código.
metadata:
  origin: ECC · skills/search-first
  category: ingenieria
  phase: plan
  status: adoptada
  version: 1
---

# Search First

El código más barato de mantener es el que no se escribe. Esta skill convierte
"vamos a implementar X" en una decisión con evidencia: ya existe, ya está en el
repo, o no existe y hay que construirlo.

## Cuándo usar

- Antes de añadir una dependencia.
- Antes de escribir un helper de propósito general (fechas, parseo, HTTP, CLI).
- Al empezar una tarea no trivial en un repo que no conoces.
- Cuando el agente propone "crear un módulo para…" sin haber mirado alrededor.

## Cuándo NO usar

- Lógica de negocio propia del dominio: no está en ningún paquete y buscarla es
  perder el tiempo.
- Cuando el repo ya prohíbe dependencias nuevas por política.

## Procedimiento

1. **Buscar en el propio repo primero** (es lo más rápido y lo que ya está
   integrado): `grep -r`, `git log --all -S`, y mirar la carpeta vecina.
2. **Buscar en el registro del ecosistema**: npm / PyPI / crates / pkg.go.dev.
   Criterios mínimos para aceptar un paquete: mantenimiento reciente, licencia
   compatible, sin dependencias desproporcionadas, superficie de API pequeña.
3. **Buscar en GitHub** por el nombre del problema, no por el nombre de la
   solución ("parse invoice pdf", no "pdfHelper").
4. **Anotar la decisión en tres líneas** en el commit o en el plan:
   - qué se buscó,
   - qué se encontró,
   - por qué se elige eso (o por qué se escribe a mano).
5. **Si se escribe a mano**, hacerlo mínimo, con la interfaz definida antes y
   con test (entra en `tdd-workflow`).

## Criterio de salida

- [ ] Existe constancia de la búsqueda (comando o URL) y de la decisión.
- [ ] Ninguna dependencia nueva entra sin justificación escrita.
- [ ] Si se reutilizó algo del repo, se enlaza el archivo.
- [ ] Si se escribe a mano, hay una razón explícita (no "es más rápido así").

## Errores típicos

| Error | Corrección |
|---|---|
| Instalar un paquete de 40 dependencias para formatear una fecha | Escribir 10 líneas con test |
| Reimplementar algo que ya está en `src/utils` | Buscar en el repo antes |
| Elegir el paquete más popular sin mirar mantenimiento | Comprobar último release y issues abiertos |
| Buscar el nombre de la solución que ya tienes en la cabeza | Buscar el problema |
| Adoptar una librería sin licencia compatible | Verificar licencia antes de integrar |
