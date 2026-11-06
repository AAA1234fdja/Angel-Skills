---
name: message-schema
description: Keep message schemas and code in sync by deriving one from the other, so a field cannot exist in only half the system. Use when a protocol is implemented in code and documented in a schema that both drift over time.
metadata:
  origin: ECC · agent-harness-construction
  category: protocols
  phase: implement
  status: adopted
  version: 1
---

# Message Schema

Two sources of truth for one message is one source of truth and one source of lies.
Either the schema is generated from the code, or the code is generated from the
schema — never both maintained by hand.

## When to Use

- A protocol exists as a dataclass or struct *and* as a JSON schema.
- A field was added to one side and not the other.
- Consumers validate against a schema that the producer no longer matches.

## When Not to Use

- A schema with no code behind it (pure external contract).
- One-off payloads with no consumer.
- A contract with no code behind it: `contract-design` shapes the payload, and there is nothing to drift from.

## Procedure

1. **Pick the direction** and write it down: code → schema (usual for internal
   messages) or schema → code (usual for external contracts).
2. **Generate in both directions for a *comparison*, not for maintenance**: the
   generated artefact is never edited by hand.
3. **Run the drift check in CI**: field added on one side and not the other fails
   the build.
4. **Keep ordering stable** so diffs are readable.
5. **Treat a rename as remove + add**, so the drift check catches half-done renames.
6. **Version the generated file** with the code that produced it.
7. **Snapshot the generated artefact in tests**, so a regeneration that changes the shape fails loudly instead of arriving with the next deploy.
8. **Record who owns the generator**: an unowned codegen step is the first thing to rot when the author changes team.

## Exit Criteria

- [ ] The generation direction is documented in the skill or the repo.
- [ ] No generated artefact is edited by hand.
- [ ] Drift check runs in CI and fails on any asymmetry.
- [ ] A rename is detectable (appears as removal plus addition).
- [ ] Generated files carry a "do not edit" header and the source version.

## Common Failures

| Failure | Fix |
|---|---|
| Maintaining both sides by hand | Generate one from the other |
| Editing the generated file "just this once" | Regenerate; the edit will vanish |
| Silent rename on one side | Renames are remove + add |
| Unstable field ordering | Sort or declare the order explicitly |
| Generated file with no provenance | Header with source and version |
| Generator owned by nobody | Name the owner next to the command |
