---
name: safety-guard
description: Put destructive operations behind risk levels and explicit confirmation instead of trusting good intentions. Use when an agent or a script can delete, force-push, rewrite history or change permissions.
metadata:
  origin: ECC · skills/safety-guard
  category: security
  phase: implement
  status: adopted
  version: 1
---

# Safety Guard

Every destructive accident has the same shape: the operation was available, it was
one call away, and nothing asked. The guard is not mistrust of the operator, it is
the removal of the one-call distance.

## When to Use

- An agent or script can delete files, rewrite history, drop tables, change
  permissions or deploy.
- Building a CLI whose commands include irreversible operations.
- After an incident caused by a command that "someone ran".

## When Not to Use

- Read-only tooling: there is nothing to guard.
- Operations with a verified, instant reversal, unless the reversal is automated.
- An autonomous system that must be stoppable, not merely guarded: `kill-switch` is the control that survives an incident.

## Procedure

1. **Enumerate the irreversible operations** honestly: deletion, force push, history
   rewrite, schema drop, permission change, rotation, deploy.
2. **Assign a risk level** to each: `read`, `write`, `execute`, `destructive`.
3. **Make the level data**, not code: declared in the manifest or the command
   table, so it can be reviewed.
4. **Require explicit consent for `destructive`**: a flag the caller must pass, never
   a default, never inferred from context.
5. **Add a dry-run** to every destructive operation: show what would be affected.
6. **Log before and after**: a guard that only logs after is a condolence.
7. **Make the refusal instructive**: say which flag enables it and what it will do.

## Exit Criteria

- [ ] Every irreversible operation has a declared risk level.
- [ ] `destructive` requires an explicit flag plus a dry-run by default.
- [ ] Refusals name the flag and the consequence.
- [ ] The operation is logged before execution, with its target.
- [ ] `classify-command` agrees with the declared levels.

## Common Failures

| Failure | Fix |
|---|---|
| "The agent is careful" | Carefulness is not a mechanism |
| Confirmation inferred from conversation | Explicit flag, every time |
| Dry-run that does not print the targets | Print the exact list |
| Logging only on success | Log the intent before acting |
| Guard on deletes but not on force-push | Enumerate all, not the obvious one |
| A `--yes` that also disables the dry-run | Separate concerns |
