---
name: harness-gc
description: Remove what the harness no longer needs: unused skills, silent hooks, forgotten servers, expired grants and orphaned config. Use when the config has grown by accretion, when context is being spent on things nobody uses, or on a schedule.
metadata:
  origin: adapted · ECC · skills/config-gc
  category: harness
  phase: meta
  status: adopted
  version: 1
---

# Harness GC

Configuration only ever grows. Each addition was justified at the time; none of them
is re-justified later, so the harness accumulates skills nobody routes to, hooks that
fire into empty space, and grants that outlived their incident. Garbage collection is
the only procedure that reverses this, and it has one rule that makes it safe:
**nothing is removed on suspicion — only on evidence and with a way back**.

## When to Use

- The harness has grown by accretion: many additions, no removals.
- Context is being spent loading things nobody uses.
- A grant, server or hook outlived the incident or project that justified it.
- On a schedule, with the diff from `harness-inventory` as input.

## When Not to Use

- Deciding whether an installed thing is good: that is `skill-stocktake`.
- Cleaning code or build artefacts: that is a different kind of garbage.
- Removing something that is still being investigated: evidence first, removal later.

## Procedure

1. **Collect evidence of non-use** over a stated window: routing counts, invocation
   logs, references in configs and docs. State the window, because "unused" without a
   window is an opinion.
2. **Separate categories**, because they carry different risk: unused (no evidence),
   superseded (a successor exists), expired (its justification expired), orphaned (no
   owner) and broken (fails on load).
3. **Never collect the last copy of a capability.** Before removing, check that the
   capability is reachable another way — a sibling skill, a documented command, a
   config default.
4. **Quarantine before deleting** when the evidence is thin: disable, keep for one
   cycle, watch. Deletion is a last step, not a first one.
5. **Remove the whole entry**: the artefact, its registration, its reference in docs
   and its permission. A half-removed entry is worse than none, because it lies.
6. **Record the removal with the evidence** in the same change, so the next audit does
   not re-litigate it.
7. **Run `gc-plan`** on the candidate list: it refuses removals with no evidence
   window, removals of a capability's last copy, and deletions that skip quarantine
   when evidence is thin.
8. **Re-run the inventory after collecting**, and diff: a GC that leaves the count
   unchanged did not collect.

## Exit Criteria

- [ ] An evidence window is stated for every "unused" claim.
- [ ] Every candidate is categorised: unused, superseded, expired, orphaned, broken.
- [ ] No removal takes the last path to a capability.
- [ ] Thin-evidence candidates are quarantined, not deleted.
- [ ] Artefact, registration, docs reference and permission removed together.
- [ ] Each removal records its evidence in the changelog.
- [ ] `gc-plan` refuses nothing, and the inventory diff shows the reduction.

## Common Failures

| Failure | Fix |
|---|---|
| Removing on suspicion | State the window and the evidence, or quarantine |
| Deleting the artefact, leaving the registration | Remove all four: artefact, registration, docs, permission |
| Collecting a capability's only path | Check for a sibling before removing |
| Permanent quarantine | A quarantine with no expiry is a deletion with extra steps |
| No record of the removal | Record evidence in the same change |
| GC that never runs | Put it on a schedule with an owner |
