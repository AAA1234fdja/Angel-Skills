---
name: agent-architecture-audit
description: Diagnóstico por capas de una aplicación con agentes o LLM — localizar en qué capa está la falla y producir hallazgos con severidad y parche concreto. Usar cuando un agente "se comporta raro" y no se sabe si el problema es el prompt, la memoria, las herramientas o el transporte.
metadata:
  origin: ECC · skills/agent-architecture-audit
  category: agentic
  phase: review
  status: adoptada
  version: 1
---

# Agent Architecture Audit

Cuando un agente falla, el reflejo es reescribir el prompt. Casi nunca es el
prompt. Esta skill obliga a recorrer las capas en orden y a **demostrar** en cuál
está la falla antes de tocar nada.

## Cuándo usar

- El agente ignora instrucciones que están en el prompt.
- Repite llamadas, elige la herramienta equivocada o "olvida" lo que ya hizo.
- La salida se corrompe (markdown roto, JSON inválido, texto cortado).
- Antes de publicar una aplicación con agentes en producción.

## Cuándo NO usar

- Cuando el fallo es de una sola herramienta concreta y ya está identificado:
  se arregla esa herramienta.
- Cuando no hay traza de la ejecución: primero se instrumenta
  (`agent-harness-construction`, paso de observación).

## Procedimiento

1. **Reunir evidencia antes de opinar**: traza completa de una ejecución fallida
   (entrada, system prompt efectivo, herramientas disponibles, cada respuesta de
   herramienta, cada salida del modelo).
2. **Recorrer las capas en orden**, descartando cada una con un dato:
   1. entrada del usuario y validación;
   2. ensamblado del prompt (¿el system prompt efectivo es el que crees?);
   3. selección de herramientas (¿estaban disponibles y bien descritas?);
   4. ejecución de herramientas (¿devolvieron lo que dice el esquema?);
   5. memoria / contexto recuperado (¿entró basura o se perdió lo importante?);
   6. transporte y render (¿se truncó, se escapó mal, se perdió un mensaje?).
3. **Nombrar el patrón de falla** entre los conocidos:
   - *wrapper regression* — una capa intermedia cambia el mensaje y el agente
     responde a otra cosa;
   - *memory contamination* — memoria vieja o irrelevante entra en el contexto;
   - *tool discipline failure* — la descripción o el esquema de la herramienta
     induce mal uso;
   - *rendering/transport corruption* — el contenido es correcto pero se trunca
     o se escapa mal;
   - *hidden layer* — hay un sistema intermedio (proxy, plantilla, caché) que no
     se tenía en cuenta.
4. **Escribir el hallazgo** con severidad (`bloqueante` / `importante` / `menor`),
   capa, evidencia (fragmento de traza) y **parche propuesto concreto**.
5. **Ordenar los hallazgos por impacto** y proponer el orden de arreglo.
6. **Verificar el arreglo con un eval** del caso que fallaba
   (`eval-harness`), no con una ejecución "que ya se ve bien".

## Criterio de salida

- [ ] Cada hallazgo dice capa, severidad y evidencia textual de la traza.
- [ ] Cada hallazgo trae parche concreto, no "revisar el prompt".
- [ ] Se descartó explícitamente cada capa anterior con un dato.
- [ ] El caso que fallaba tiene un eval de regresión que antes fallaba.
- [ ] Se identificó el patrón de falla o se explica por qué no encaja en ninguno.

## Errores típicos

| Error | Corrección |
|---|---|
| Reescribir el prompt sin leer la traza | La traza decide, no la intuición |
| Arreglar la capa 1 sin haber mirado la 6 | Orden obligatorio |
| Hallazgos sin evidencia | Fragmento de traza o no es hallazgo |
| "Parece que la memoria mete ruido" | Mostrar qué memoria entró y por qué |
| Arreglar cinco cosas a la vez | Un hallazgo, un cambio, un eval |
| Cerrar con "ya funciona" | Eval del caso, antes y después |
