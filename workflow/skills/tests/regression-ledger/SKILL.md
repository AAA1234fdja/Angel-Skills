---
name: regression-ledger
description: Keep a ledger of cross-module regressions: which module a change can break downstream, and the executable acceptance that proves it did not. Use when a repo has modules whose consumers nobody has listed, or after a change broke a distant caller.
metadata:
  origin: adapted · ECC · skills/module-regression
  category: tests
  phase: verify
  status: adopted
  version: 1
---

# Regression Ledger

In a repository of one module, the compiler is the regression test. In a repository of
forty, the interesting breakage happens in a module nobody imported in the change —
and it is found by a customer. The ledger makes the downstream surface legible: for
each module, who depends on it and what executable check proves the dependency still
holds. It is deliberately boring, and that is the point: it only works if updating it
is cheaper than being surprised.

## When to Use

- A change broke a distant caller that no test covered.
- A module has consumers nobody can enumerate from memory.
- Before refactoring a shared module, or changing a contract it publishes.
- When onboarding needs a map of what is coupled to what.

## When Not to Use

- Build-time dependency cycles: that is `dependency-graph`.
- One failing test in one module: that is `flaky-test-triage` or `build-fix`.
- Full release gating: that is `release-readiness`.

## Procedure

1. **One ledger entry per module**, with its published surface: functions, events,
   endpoints, tables — whatever a consumer can depend on.
2. **List downstream consumers**, one level at least, from imports or usage search.
   "Unknown" is an entry, and it is the most valuable one in the file.
3. **For each consumer, one executable acceptance**: the check that fails when the
   module breaks it. A ledger entry without an executable check is a comment.
4. **Record the coupling type**: compile-time, runtime, data, or contract. Each breaks
   differently and gets caught by a different check.
5. **Update the ledger in the same change** that modifies a published surface. A ledger
   updated later describes a system that no longer exists.
6. **Run `regression-ledger-check`** on it: it flags entries with no consumers recorded,
   consumers with no executable check, unknown consumers left unresolved, and entries
   untouched for a long window while their module changed.
7. **Sample the ledger once a quarter** by breaking a module on purpose and confirming
   that the listed checks fail. An unverified ledger is a diagram.
8. **Delete entries for removed modules** in the same change that removes them.

## Exit Criteria

- [ ] Every module with a published surface has an entry.
- [ ] Each entry lists its consumers, one level down, with `unknown` marked as such.
- [ ] Each consumer has an executable acceptance check.
- [ ] The coupling type is recorded per consumer.
- [ ] The ledger was updated in the change that touched the surface.
- [ ] A sample was verified by breaking a module on purpose.
- [ ] `regression-ledger-check` reports no unchecked consumer and no stale entry.

## Common Failures

| Failure | Fix |
|---|---|
| Consumers listed as prose | One executable check per consumer |
| "Nobody else uses this" | Mark it `unknown` and let the check prove it |
| Ledger updated after the merge | Update it in the same change |
| One coupling type for everything | Compile, runtime, data and contract break differently |
| Stale entries for deleted modules | Delete in the same change as the module |
| Ledger never verified | Break a module on purpose, once a quarter |
