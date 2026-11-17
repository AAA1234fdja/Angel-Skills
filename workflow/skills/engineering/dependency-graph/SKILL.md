---
name: dependency-graph
description: Audit a dependency graph before changing it: cycles, layers, fan-in, fan-out and orphans. Use when a refactor could cascade, when the build order is disputed, when a module seems to know about everything, or before extracting a shared package.
metadata:
  origin: original
  category: engineering
  phase: plan
  status: original
  version: 1
---

# Dependency Graph

Most "big refactors" are one edge in the wrong direction. Before touching code,
look at the graph: which module is imported by everything, which pair imports each
other, which layer quietly reaches back up. The graph answers in a minute what a
week of reading answers badly.

## When to Use

- A change in one module keeps breaking a distant one.
- The build order is disputed, or a cycle makes it nondeterministic.
- A shared package is being extracted — it must be a layer, not a dumping ground.
- A module's test suite is huge, suspiciously coupled to everything else.
- Someone proposes "just one more import" across a boundary.

## When Not to Use

- A single-file project: the graph is the file.
- Judging *design quality*: a clean dependency graph can still be the wrong
  design. This skill measures coupling, not intent.
- As a gate on every PR: run it when the shape of the code is in question.
- Whether the design is any good: a clean graph is still the wrong design — that is `code-review`, and cycles inside one package belong to `dependency-audit`.

## Procedure

1. **Collect the edges** as `{"from": "...", "to": "..."}` from the real imports,
   not from what the architecture document claims. If the two disagree, the code
   is the truth and the document is the bug.
2. **Run the `dependency-audit` tool** on the edges. It reports cycles, the
   longest chain, the most-depended-on nodes, and orphans.
3. **Name every cycle and decide which single edge is wrong.** A cycle is never
   fixed by adding an interface in both directions: one of the two edges must go.
4. **Check the layer direction.** In a layered design, an edge that points
   backwards (domain importing infrastructure, library importing app) is worse
   than a cycle of two utilities, because it will be copied.
5. **Look at fan-in before deleting anything.** A node with fan-in 12 is a
   contract whether or not anyone called it one: change it as a version, not as a
   refactor.
6. **Record the decision** — the edge removed, the layer rule, or the accepted
   cycle with its reason — next to the graph, so the next audit starts informed.
7. **Re-run the audit after the refactor**, not only before: a cycle removed in one file often reappears through the helper introduced to remove it.

## Exit Criteria

- [ ] Every cycle listed by `dependency-audit` has a named edge to remove or a
      written justification with an owner.
- [ ] No layer violation remains unaddressed (fixed, or recorded as accepted).
- [ ] High fan-in nodes changed in the change set are treated as contract changes.
- [ ] Orphans are either deleted or explained.
- [ ] The direction rule the project now follows is written down in one sentence.

## Common Failures

| Failure | Fix |
|---|---|
| Auditing the documented architecture, not the imports | Feed the tool real edges from the build |
| "The cycle is fine, it works" | It forbids independent testing and deterministic order; break one edge |
| Extracting a shared package that imports both sides | That is a third layer, not a shared one |
| Deleting a high fan-in module as "unused" | Fan-in zero is needed first; check the count |
| Fixing a cycle by adding a callback in both directions | Same cycle, more indirection |
| Running the audit once and never again | Re-run on the boundaries that keep breaking |
