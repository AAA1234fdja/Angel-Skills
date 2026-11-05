---
name: refactor-clean
description: Verified removal of dead code and duplicate logic, one candidate per commit with the suite green throughout. Use when the repository accumulates unused functions, orphan imports or two implementations of the same thing.
metadata:
  origin: ECC · agent refactor-cleaner
  category: engineering
  phase: implement
  status: adopted
  version: 1
---

# Refactor Clean

Deleting code is the easiest thing to break and the hardest to undo. So here it is
done **one candidate at a time, with evidence that nobody uses it and the suite
green after each step**.

## When to Use

- Before a new feature lands in an already saturated module.
- When two modules implement the same thing and one must win.
- When an agent finds imports, variables or routes with no usage.

## When Not to Use

- While fixing a defect: fix first, clean later.
- On code published as an API (exports, endpoints, routes): consumers may exist
  outside the repository, so "unused" cannot be verified by grep.
- Before a release: cleanup is not a safe last-minute change.

## Procedure

1. **Pin the baseline**: full suite green, recorded. Without it you cannot tell
   your breakage from what was already broken.
2. **Find candidates from several sources**: reference search, dead-code lint,
   test coverage (never executed), and history (`git log -S`).
3. **Classify** each candidate: `safe` (no references, not exported),
   `review` (references only in tests), `keep` (public API, generated,
   pending migration).
4. **One candidate per commit**, simplest first. A commit that does not build or
   cannot be explained is reverted.
5. **Consolidate duplicates only when they are truly equivalent**: compare
   behaviour with tests, not by eye. If they differ anywhere, they are not
   duplicates.
6. **Re-run the suite after every step.** If something fails, revert that step and
   rethink; do not stack breakage.
7. **Check the global result**: fewer lines, same tests green, no public API
   removed without notice.

## Exit Criteria

- [ ] The baseline was green and is quoted.
- [ ] Every deletion has evidence of non-use (command and output).
- [ ] Zero public API removals without a contract-change note.
- [ ] The suite is still green with the same number of tests (or more, never fewer).
- [ ] The total diff reduces lines and reads in under two minutes.

## Common Failures

| Failure | Fix |
|---|---|
| "Surely nobody uses it" | Search, and record the command |
| Deleting everything the linter flags | Linters miss dynamic use (`importlib`, string handlers) |
| Cleaning and fixing a bug in one commit | One purpose per commit |
| Consolidating two "identical" functions | Compare with tests; they usually differ at edges |
| Deleting failing tests | A failing test points at something: investigate |
| A big refactor with no checkpoints | Small commits you can revert |
