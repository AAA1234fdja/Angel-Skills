---
name: agent-architecture-audit
description: Layer-by-layer diagnosis of an agent stack with severity-ranked findings and a concrete patch for each. Use when an agent misbehaves and it is unclear whether the fault is the prompt, memory, tools or transport.
metadata:
  origin: ECC · skills/agent-architecture-audit
  category: agentic
  phase: review
  status: adopted
  version: 1
---

# Agent Architecture Audit

When an agent fails, the reflex is to rewrite the prompt. It is rarely the prompt.
This skill walks the layers in order and **proves** which one failed before touching
anything.

## When to Use

- The agent ignores instructions that are in the prompt.
- It repeats calls, picks the wrong tool, or "forgets" what it just did.
- Output is corrupted (broken markdown, invalid JSON, truncated text).
- Before shipping an agent application to production.

## When Not to Use

- A single tool is already identified as broken: fix that tool.
- There is no trace: instrument first (`agent-harness-construction`).

## Procedure

1. **Collect evidence first**: a full trace of one failing run — input, effective
   system prompt, tools available, every tool response, every model output.
2. **Walk the layers in order**, eliminating each with a datum:
   1. user input and validation;
   2. prompt assembly (is the effective system prompt what you think?);
   3. tool selection (were they available and well described?);
   4. tool execution (did they return what the schema says?);
   5. memory and retrieved context (did junk enter, or important context vanish?);
   6. transport and rendering (truncated, badly escaped, dropped message?).
3. **Name the failure pattern**:
   - *wrapper regression* — an intermediate layer rewrites the message;
   - *memory contamination* — stale or irrelevant memory enters the context;
   - *tool discipline failure* — description or schema induces misuse;
   - *rendering/transport corruption* — content is right but arrives wrong;
   - *hidden layer* — an unaccounted proxy, template or cache.
4. **Write the finding** with severity, layer, trace excerpt and a concrete patch.
5. **Order findings by impact** and propose the fix order.
6. **Verify with an eval** of the failing case (`eval-harness`), not with a run that
   "looks fine now".
7. **Say what an eval would have to change to catch this**: if the failure cannot be turned into a check, the diagnosis is a story, not a finding.

## Exit Criteria

- [ ] Each finding states layer, severity and a trace excerpt.
- [ ] Each finding carries a concrete patch, not "review the prompt".
- [ ] Each earlier layer was eliminated with a datum.
- [ ] The failing case has a regression eval that failed before the fix.
- [ ] The failure pattern is named, or its absence is explained.

## Common Failures

| Failure | Fix |
|---|---|
| Rewriting the prompt without reading the trace | The trace decides |
| Fixing layer 1 without checking layer 6 | Order is mandatory |
| Findings without evidence | Trace excerpt or it is not a finding |
| "Memory seems noisy" | Show what memory entered and why |
| Fixing five things at once | One finding, one change, one eval |
| Closing with "works now" | Eval the case, before and after |
