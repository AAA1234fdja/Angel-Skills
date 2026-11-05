---
name: verification-loop
description: Six-phase verification (build, types, lint, tests with coverage, security, diff review) with quotable evidence for every phase. Use when a task is being closed, before a commit, or when someone hands over a change to accept or reject.
metadata:
  origin: ECC · skills/verification-loop
  category: engineering
  phase: verify
  status: adopted
  version: 1
---

# Verification Loop

A task is not finished when the code looks right; it is finished when there is
evidence that it is right. This procedure produces that evidence and **stops at
the first failure** instead of stacking debt.

## When to Use

- Closing any task that touched executable code.
- Before a commit or a pull request.
- When another agent or person delivers a change to accept or reject.
- After a merge or a rebase.

## When Not to Use

- Changes that only touch non-executable text (a README with no commands).
- When CI already ran exactly these phases on the same commit: quote CI instead
  of repeating it.

## Procedure

Run in order. **Every phase produces a quotable result** (command plus a summary
of output). A failure restarts the loop at that phase.

1. **Build.** Compile or bundle. Cheapest filter first.
2. **Types.** Static check with no artefacts written (`tsc --noEmit`, `mypy`,
   `go vet`, `cargo check`).
3. **Lint and format.** With the repository configuration, without reformatting
   untouched files.
4. **Tests with coverage.** The whole suite, not only the touched file.
5. **Security.** Secrets in the diff, unjustified new dependencies, unvalidated
   input, file paths built from external data.
6. **Diff review.** Read `git diff` top to bottom with one question: is this the
   smallest change that solves the task? Everything else is out.

## Exit Criteria

- [ ] All six phases ran, each with command and result recorded — the `gate` tool
      refuses a phase with no evidence.
- [ ] Zero open failures; anything postponed is listed as explicit debt with a
      reason.
- [ ] The diff contains no temporary files, logs, binaries or secrets.
- [ ] Someone other than the author read the diff (phase 6) — `code-review` if
      the context is stale.

## Common Failures

| Failure | Fix |
|---|---|
| Jumping to tests without building | Fixed order: it fails earlier and cheaper |
| "Works on my machine" | Record command and environment; CI decides |
| Green after deleting a failing test | Check the test count did not drop |
| Fixing lint by reformatting half the repo | Format only what you touched |
| Closing with a TODO and no owner | Do it, or record it as debt with a reason |
| Reviewing the diff with the author's context | Fresh review pass |
