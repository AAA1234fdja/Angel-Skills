---
name: skill-audit
description: Audit the catalogue for overlap, dead skills, weak triggers and skills that never fire. Use when the catalogue grows, before a release, or when two skills keep being loaded for the same need.
metadata:
  origin: ECC · skills/skill-stocktake
  category: governance
  phase: meta
  status: adopted
  version: 1
---

# Skill Audit

A catalogue grows by addition and rots by addition. The audit is the periodic
subtraction: which skills fire for the same need, which never fire at all, and which
describe a topic instead of a procedure.

## When to Use

- The catalogue grew significantly.
- Two skills are routinely loaded for one need.
- Before a release, as a quality gate.

## When Not to Use

- A catalogue under ten skills: overlap is not yet a problem.
- During active authoring of one skill: audit afterwards.
- A catalogue small enough that overlap is not yet a problem: `skill-authoring` is the whole job.

## Procedure

1. **Measure firing**: from the journal, which skills were routed and which were
   never routed in the last N runs.
2. **Score overlap**: compare triggers, keywords and verbs pairwise; pairs above the
   threshold need a decision.
3. **Classify every skill** as: keep, merge into X, split (too broad), or retire.
4. **Check the exit criteria are still checkable** — a skill whose command no longer
   exists is dead even if it is loaded.
5. **Check the description still matches the body**: the body drifts, the
   description lies.
6. **Act on the classification**: merging is a major change with a changelog entry,
   retiring is a registry removal plus a note.
7. **Repeat on a schedule**, not when it hurts.

## Exit Criteria

- [ ] Firing data for the last N runs is included.
- [ ] Every overlapping pair has a decision: keep both, merge, or split.
- [ ] Never-fired skills are explained, not just listed.
- [ ] Dead exit criteria identified (missing commands, removed scripts).
- [ ] Merges and retirements have changelog entries.
- [ ] The audit date and the next audit date are recorded.

## Common Failures

| Failure | Fix |
|---|---|
| Listing overlap with no decision | Every pair gets keep/merge/split |
| Retiring a skill without a note | The next person re-adds it |
| Auditing only descriptions | Read the body; drift lives there |
| No firing data | Instrument the router first |
| Auditing in a hurry | Sample properly, or do not audit |
| Merging two skills into a monster | Merge only when the trigger is one |
