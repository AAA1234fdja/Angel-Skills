---
name: data-contracts
description: Define the shape and invariants of persisted data before the code that touches it. Use when a new table, collection or file format is about to be created, or when two codepaths disagree about what a field means.
metadata:
  origin: ECC · database-patterns + api-design
  category: data
  phase: plan
  status: adopted
  version: 1
---

# Data Contracts

Code is rewritten every year; data is migrated for a decade. Defining the shape and
the invariants before writing the code that writes the data is the cheapest
decision in the whole system.

## When to Use

- A new table, collection, index or persisted file format.
- Two code paths disagree about what a field means.
- A field is about to become nullable "temporarily".

## When Not to Use

- Ephemeral data that never leaves one request.
- Caches whose content can be rebuilt from the source of truth.

## Procedure

1. **Name the entity and its identity**: what makes a record unique and immutable.
2. **List fields with meaning, unit and nullability** — `amount_cents`, not
   `amount`; `created_at` in UTC, not local time.
3. **Write the invariants**: things true in every valid state (balances never
   negative, end after start, one active subscription per account).
4. **Decide which invariants the database enforces** and which the application
   does, and why.
5. **Define deletion semantics**: hard delete, soft delete, retention window.
6. **Define the audit trail**: who changed what, when, from where.
7. **Write sample records** and validate them with `invariant-check` before
   creating the storage.

## Exit Criteria

- [ ] Identity and immutability rules are written.
- [ ] Every field has meaning, unit and nullability.
- [ ] Invariants listed with the layer that enforces each.
- [ ] Deletion and retention semantics decided.
- [ ] Sample records pass the invariant check.

## Common Failures

| Failure | Fix |
|---|---|
| Nullable "for now" | Nullability is a contract; decide now |
| Units implicit | Put them in the name |
| Invariants only in application code | Some belong in the database |
| No deletion semantics | Deletion becomes an incident |
| No audit trail | "Who changed this" becomes unanswerable |
| Timestamps in local time | Store UTC, render local |
