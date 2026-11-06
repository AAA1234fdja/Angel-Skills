---
name: migration-safety
description: Write reversible migrations with backfill plans, lock analysis and a tested rollback. Use when changing a live schema, backfilling data, or when a migration must run while the old code is still deployed.
metadata:
  origin: ECC · skills/database-migrations
  category: data
  phase: implement
  status: adopted
  version: 1
---

# Migration Safety

A migration is the only change that can destroy data while everything looks green.
It runs against live traffic, with the old code still deployed, and the rollback is
often the part nobody tested.

## When to Use

- Any change to a live schema.
- A backfill touching more than a handful of rows.
- Removing a column or a table.

## When Not to Use

- A greenfield database with no data and no deployment.
- Test fixtures.
- A greenfield database with nothing to migrate: `release-readiness` covers the first deploy.

## Procedure

1. **Write the forward step and the rollback step together** — a migration without
   a rollback is a one-way door.
2. **Classify the lock**: does it rewrite the table, hold an exclusive lock, or run
   online? Say which, and the expected duration at production scale.
3. **Make it expand-contract**: add new shape, dual-write, backfill, switch reads,
   then remove the old shape in a later migration.
4. **Backfill in batches**, idempotently, resumable, with progress logged.
5. **Keep the old code working** for the duration: the migration deploys before the
   code that requires it, and removal comes after the code stops using it.
6. **Test the rollback on a copy** with production-like data volume.
7. **Write the stop conditions**: error rate, lock time, replication lag — whichever
   trips first, abort.

## Exit Criteria

- [ ] Forward and rollback written and both tested.
- [ ] Lock type and expected duration stated.
- [ ] Backfill is batched, idempotent and resumable.
- [ ] Expand-contract order documented (migration, code, cleanup).
- [ ] Stop conditions defined with thresholds.
- [ ] `migration-plan` accepts the plan.

## Common Failures

| Failure | Fix |
|---|---|
| No rollback | Write both before running either |
| A backfill in one statement | Batch it; it holds locks and times out |
| Dropping the old column immediately | Expand-contract across releases |
| Testing on an empty database | Test on production-like volume |
| No stop condition | Define error rate and lag thresholds |
| Irreversible step without consent | It is destructive (`safety-guard`) |
