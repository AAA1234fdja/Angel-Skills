---
name: harness-inventory
description: Know what your agent runtime actually has installed: skills, hooks, commands, servers, permissions and where each came from. Use when the harness behaves in a way nobody configured, when adopting a library, or before installing one more thing into it.
metadata:
  origin: adapted · ECC · skills/workspace-surface-audit
  category: harness
  phase: audit
  status: adopted
  version: 1
---

# Harness Inventory

Every harness drifts. A skill installed to try it, a hook added during an incident, a
server configured once and forgotten, a permission widened to unblock a demo — six
months later nobody can say what the agent is allowed to do, and the answer is not in
any file because it is spread across five. This procedure produces the inventory
first, because every later question ("why did it do that?", "what do we remove?",
"what is the blast radius?") is a query against it.

## When to Use

- The harness does something nobody remembers configuring.
- Before installing a library, a hook pack or a server.
- After adopting someone else's configuration, or inheriting a repo with one.
- Before an access review, or when a permission is about to be widened.

## When Not to Use

- Auditing whether installed skills are *good*: that is `skill-stocktake`.
- Deciding whether something may be installed at all: that is `harness-provenance`.
- Reasoning about what the model can infer from context: that is `context-budget`.

## Procedure

1. **Enumerate by layer, not by folder**: skills, hooks, slash commands, servers,
   permission grants, environment overrides, auto-load files. Each layer has its own
   discovery mechanism and its own failure mode.
2. **Record provenance for each entry**: built-in, adopted from a named source with a
   version, or local. "Unknown origin" is a finding, not a category to skip.
3. **Record the trigger of each entry**: what makes it load or fire. A hook you cannot
   trigger on purpose is a hook you cannot debug.
4. **Record the blast radius**: what can this entry read, write, execute or call.
   Rank by capability, not by name — the innocent-looking script with the network
   call is the one that matters.
5. **Diff against the last inventory.** New entries and widened permissions are the
   interesting ones; an inventory without a diff is a photograph, not a control.
6. **Report orphans**: entries nothing references and nobody owns. These are the ones
   that survive every cleanup.
7. **Run `surface-audit`** on the inventory: it reports unknown provenance, untriggerable
   entries, unowned orphans, wide grants and the layers that were never enumerated.
8. **Publish the inventory with a date and an owner**, and make the next one a diff.

## Exit Criteria

- [ ] All seven layers enumerated, including empty ones (stated as empty).
- [ ] Every entry has a provenance: built-in, named source with version, or local.
- [ ] Every entry has a stated trigger.
- [ ] Every entry has a blast radius, ranked by capability.
- [ ] The diff against the previous inventory is included.
- [ ] Orphans are listed with a decision: adopt with an owner, or remove.
- [ ] `surface-audit` reports no unknown provenance and no unowned orphan.

## Common Failures

| Failure | Fix |
|---|---|
| Inventory built from the folder tree | Enumerate by layer; some entries live outside the tree |
| "Installed by someone, probably" | Unknown provenance is a finding, not a shrug |
| Listing names instead of capabilities | Rank by what each can read, write and execute |
| No diff against the previous run | A static inventory controls nothing |
| Orphans left in place | Adopt with an owner, or remove in the same change |
| Audit that stops at the repo | Servers and permissions often live outside it |
