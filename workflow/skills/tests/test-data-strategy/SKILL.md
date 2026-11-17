---
name: test-data-strategy
description: Decide where test data comes from and how it stays deterministic: factories, fixtures, snapshots and seeds with a stated owner. Use when tests share state, when fixtures rot, when a suite depends on production dumps, or before adopting a database in tests.
metadata:
  origin: original
  category: tests
  phase: design
  status: original
  version: 1
---

# Test Data Strategy

Most "flaky tests" are not timing problems. They are data problems: a fixture that
another test mutated, a seed that is not replayed, a production dump somebody
committed three years ago, an auto-increment id that a test hard-coded. The strategy is
small and it is decided once: every test declares the data it needs, every test gets it
in a way that is order-independent, and nothing in the suite depends on the state left
by another test.

## When to Use

- Tests pass alone and fail in a full run, or pass in one order only.
- Fixtures are shared, edited by hand, or older than the code they feed.
- A test depends on a production dump or on real user identifiers.
- Before adopting a database, a queue or an external service in tests.

## When Not to Use

- Non-determinism that is genuinely timing or concurrency: that is `flaky-test-triage`.
- Deciding where the suite runs: that is CI configuration, not data.
- Production data retention policy: that is `data-retention`.

## Procedure

1. **Classify each need**: reference data (stable, read-only, versioned), entity data
   (created per test), or edge data (the ugly cases: unicode, nulls, boundary sizes).
   The three have different lifetimes and different owners.
2. **Prefer builders over fixtures.** A factory that states only what the test cares
   about survives schema changes; a fixture blob does not.
3. **Make every test own its data**: create in the test, delete after, or use a
   transaction rollback. Order-independent by construction, not by convention.
4. **Ban shared mutable fixtures** explicitly. The shared row that two tests edit is
   the classic order-dependent failure.
5. **Never derive test data from production** without an anonymisation step and a
   record. A real email in a fixture is a personal-data incident waiting for a `git log`.
6. **Pin the clock, the random seed and the ids** where behaviour depends on them.
   Determinism is a property you configure, not one you hope for.
7. **Run `data-strategy-check`** on the inventory: it flags shared mutable fixtures,
   tests with no data ownership, production-derived data without anonymisation, and
   unseeded randomness or unpinned clocks.
8. **Bound the volume of reference data**: a fixture set nobody can read is a database
   with worse tooling.

## Exit Criteria

- [ ] Each data need is classified as reference, entity or edge.
- [ ] Entity data is created and cleaned per test, or rolled back.
- [ ] No shared mutable fixture remains.
- [ ] Production-derived data is anonymised and recorded as such.
- [ ] Clock, random seed and identifiers are pinned where behaviour depends on them.
- [ ] Reference data is versioned and small enough to read.
- [ ] `data-strategy-check` reports no shared state and no unseeded determinism gaps.

## Common Failures

| Failure | Fix |
|---|---|
| Shared fixture edited by several tests | Create per test, or roll back |
| Fixtures hand-maintained | Builders that state only the relevant fields |
| Production dump committed | Anonymise, record it, or synthesise |
| Random ids and real clocks in assertions | Pin the seed and the clock |
| Reference data that grew into a database | Bound it; keep only what decides behaviour |
| "Order-dependent but stable in CI" | It is not stable, it is lucky |
