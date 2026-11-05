---
name: context-budget
description: Spend context deliberately: measure what is loaded, cap it, and compact at phase boundaries instead of reactively. Use when sessions run long, the agent forgets early instructions, or the catalogue itself is eating the window.
metadata:
  origin: ECC · context-budget + strategic-compact
  category: agentic
  phase: plan
  status: adopted
  version: 1
---

# Context Budget

Context is a budget with a hard ceiling and no overdraft. Watching it reactively
means the agent forgets the instructions from the beginning of the session at the
exact moment it needs them.

## When to Use

- Long sessions, multi-phase tasks, or a large skill catalogue.
- The agent stops following instructions it followed an hour ago.
- Deciding what to load for a task before loading it.

## When Not to Use

- Sessions under a few thousand tokens: the overhead exceeds the benefit.
- When the real problem is a bloated system prompt — fix that first.

## Procedure

1. **Measure what is loaded now**: system prompt, skill bodies, tool descriptions,
   file excerpts, conversation. One line each, in characters or tokens.
2. **Set a cap per category**: for example 20% system, 30% skills, 30% working
   files, 20% history.
3. **Load by phase, not by catalogue**: only the skills of the phase in play
   (`workflow plan --phase …`, or `workflow route --need … --phase …`).
4. **Prefer references to inlined content**: name the file and load the section on
   demand.
5. **Compact at phase boundaries**, in a planned way: summarise decisions and
   evidence, drop exploration.
6. **Never compact mid-reasoning**: you lose the thread exactly when you need it.
7. **Record what was dropped**, so a later "why didn't you know X" has an answer.

## Exit Criteria

- [ ] Current load measured per category, with numbers.
- [ ] Caps declared per category and respected.
- [ ] Only the phase's skills are loaded, not the catalogue.
- [ ] Compaction happens at phase boundaries with a summary kept.
- [ ] `budget-model` reports no phase over its cap.

## Common Failures

| Failure | Fix |
|---|---|
| Loading every skill "just in case" | Load the phase |
| Reacting to compaction prompts | Plan the compaction at a phase boundary |
| Inlining a 2000-line file | Reference it and load the section |
| Trimming the system prompt first | Trim history and exploration first |
| Losing decisions after compaction | Keep a decisions block in the summary |
