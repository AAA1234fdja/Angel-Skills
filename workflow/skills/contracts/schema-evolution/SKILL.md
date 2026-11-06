---
name: schema-evolution
description: Evolve a schema without breaking consumers: classify every change as major, minor or patch and require the matching version bump. Use when adding, removing or retyping fields in a contract that already has consumers.
metadata:
  origin: ECC · database-migrations (pattern)
  category: contracts
  phase: implement
  status: adopted
  version: 1
---

# Schema Evolution

Schemas outlive the code that wrote them. The only way to change one without
breaking consumers is to classify every change *before* making it, and to make the
version number carry that classification.

## When to Use

- Adding, removing, renaming or retyping a field in an existing contract.
- Tightening validation (new required field, narrower enum).
- Planning a migration where old and new payloads coexist.

## When Not to Use

- A contract with no consumers yet: change freely, still keep the history.
- A private schema that never leaves one module.
- A greenfield schema with no consumers yet: `contract-design` decides it once, without a migration.

## Procedure

1. **List each intended change individually** — one line per field.
2. **Classify it** with the rules below and let `bump-advisor` confirm.
3. **Choose the bump**: any major-classified change means a new major version file.
4. **Keep the old version readable** for the deprecation window; consumers pin
   majors, so both must coexist.
5. **Write the migration note**: what a consumer must change and by when.
6. **Backfill or default** for required fields: a new required field needs data in
   existing payloads.
7. **Verify with `workflow contract --diff old new`**: the tool must agree with your
   classification, or the tool is right.

Classification:

| Change | Class |
|---|---|
| add optional property, widen enum, relax constraint | minor |
| remove property, add required property, narrow enum, change type, forbid extra fields | major |
| docs, examples, descriptions | patch |

## Exit Criteria

- [ ] Every change classified, one line each.
- [ ] The version bump matches the highest class.
- [ ] Old version still validates during the deprecation window.
- [ ] Migration note written for consumers.
- [ ] `workflow contract --check` and `--diff` both pass.

## Common Failures

| Failure | Fix |
|---|---|
| Adding a required field as "minor" | Existing payloads fail: it is major |
| Editing a published version in place | Versions are immutable |
| Narrowing an enum quietly | Consumers receiving old values now fail |
| Removing a field with no deprecation window | Announce, then remove in a major |
| Trusting your own classification | Let `--diff` decide; it has no ego |
