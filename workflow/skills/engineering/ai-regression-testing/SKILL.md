---
name: ai-regression-testing
description: Turn every fixed defect and every AI-generated change into a permanent regression test that runs without external services. Use when a defect has just been fixed, or when generated code touches an area with a history of failures.
metadata:
  origin: ECC · skills/ai-regression-testing
  category: engineering
  phase: test
  status: adopted
  version: 1
---

# AI Regression Testing

When an agent generates code quickly, the risk stops being "it does not work" and
becomes **"it worked and stopped working"**. This skill turns every defect into a
net that cannot be broken again unnoticed.

## When to Use

- A defect has just been fixed: the reproducing test is mandatory.
- Generated code touches an area with a history of failures.
- You want a suite that runs with no database and no external services.

## When Not to Use

- New behaviour that does not exist yet: that is a feature test (`tdd-workflow`).
- Defects that only reproduce in deployment: not a unit-level guard.

## Procedure

1. **Reproduce the defect in a failing test**, using the real minimal case (or an
   anonymised subset of it).
2. **Sandbox the test**: no live database, no network, no credentials. Doubles
   return the same *shape* as the real system.
3. **Verify parity**: confirm the double responds like the real system for that
   case. If they differ, a green test means nothing.
4. **Add the case to the regression register**, grouped by area, with the issue
   number in the name or the comment.
5. **Run the register before accepting generated changes**, not only in CI.
6. **When a test fails, ask first whether the code or the test is wrong.** An old
   test may be obsolete after a legitimate contract change: update it in the same
   commit and say why.

## Exit Criteria

- [ ] The defect has a test that **failed before** the patch and passes after.
- [ ] The test runs with no external service.
- [ ] Double parity is verified or documented as an assumption.
- [ ] The test name or comment references the issue.
- [ ] `regression-matrix` reports zero unguarded fixed defects.

## Common Failures

| Failure | Fix |
|---|---|
| Fixing the bug with no test | Without a test it returns in three weeks |
| Test coupled to internals (private mocks) | Assert observable output |
| A double that does not resemble the real system | Check shape and error cases of the contract |
| Regression test needing a live database | Replace with a double or an ephemeral container |
| Deleting a test because "it no longer applies" | Update it to the new contract and explain |
| Two thousand slow tests | Group by area, keep the register fast |
