---
name: performance-optimizer
description: Convertir "esto va lento" en un cambio medido — línea base, un cuello de botella, una hipótesis, comparación contra la base. Usar cuando hay una queja de rendimiento o un presupuesto de latencia que se incumple.
metadata:
  origin: ECC · agents/performance-optimizer + skills/benchmark-optimization-loop
  category: ingenieria
  phase: implement
  status: adoptada
  version: 1
---

# Performance Optimizer

Optimizar sin medir es cambiar código y creer que mejoró. La regla es simple:
**primero la línea base, después una sola hipótesis, y el número decide**.

## Cuándo usar

- Queja concreta de lentitud ("el listado tarda", "el build tarda 4 minutos").
- Un presupuesto de latencia o memoria que se incumple.
- Antes de escalar un servicio y querer saber dónde aprieta.

## Cuándo NO usar

- Sin una medición posible: si no se puede medir, no se puede optimizar.
- Cuando el problema es una espera de red o de la base: primero se ataca la
  causa (N+1, falta de índice), no el código del cliente.
- Código que aún no está en el camino crítico ni se ha perfilado.

## Procedimiento

1. **Definir la métrica y el escenario**: qué se mide (p50, p95, tiempo total,
   memoria, tokens), con qué datos y con qué comando reproducible.
2. **Tomar la línea base** al menos 3 veces y anotar dispersión. Un número sin
   dispersión no permite saber si el cambio sirvió.
3. **Perfilar, no adivinar**: profiler del lenguaje o `--cpu-prof`,
   `py-spy`, `perf`, `EXPLAIN` en SQL, network waterfall en navegador.
4. **Elegir UN cuello de botella** y escribir la hipótesis: "el 70 % del tiempo
   está en X; si se hace Y, bajará".
5. **Aplicar el cambio mínimo** que valida la hipótesis. Sin reescribir el
   módulo de paso.
6. **Medir de nuevo igual que la base** (3 veces, mismo escenario). Si no mejora
   de forma medible, revertir: no se conserva una optimización sin evidencia.
7. **Verificar corrección**: suite completa en verde; ganar velocidad rompiendo
   comportamiento no es una mejora.
8. **Documentar** base → después, y por qué se eligió ese cambio.

## Criterio de salida

- [ ] Línea base medida y citada (comando + números, con dispersión).
- [ ] Una sola hipótesis por cambio, con el dato que la sustenta (perfil, EXPLAIN).
- [ ] Medición posterior con el mismo método, y mejora fuera de la dispersión.
- [ ] Suite en verde y comportamiento idéntico.
- [ ] Si no hubo mejora, el cambio está revertido.
- [ ] El PR resume base → después en una tabla.

## Errores típicos

| Error | Corrección |
|---|---|
| Optimizar por intuición | Perfilar primero |
| Cambiar tres cosas y medir una vez | Una hipótesis por iteración |
| Comparar una medición con otra de otro entorno | Mismo escenario, mismos datos |
| Cambiar comportamiento para ganar velocidad sin decirlo | Es un cambio de contrato: se documenta |
| "Mejora de 300 %" sin base | Sin línea base no hay mejora, hay opinión |
| Añadir caché como primera opción | La caché esconde una causa; es el último recurso |
| Micro-optimizar el 2 % del tiempo | Atacar el cuello del paso 3 |
