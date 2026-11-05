---
name: tdd-workflow
description: Red-green-refactor with a coverage gate, so a task is never called done because the code looks right. Use when implementation is about to be written, or a defect is about to be fixed and needs a failing test first.
metadata:
  origin: ECC · skills/tdd-workflow
  category: engineering
  phase: test
  status: adopted
  version: 1
---

# TDD Workflow

Writing the failing test first is not ceremony: it is the only cheap proof that
the test *can* fail. A test written after the implementation passes by
construction, which is the same as not testing.

## When to Use

- New behaviour that a caller can observe.
- A reported defect, before any patch exists.
- A behaviour change in code that already has tests.

## When Not to Use

- Purely cosmetic edits with no observable behaviour (formatting, internal renames).
- Throwaway exploration that will be deleted.
- When the project has no test runner: choose one first, do not write
  implementation blind.

## Procedure

1. **Fix the interface** before the body: name, inputs, outputs, errors.
2. **Red.** Write one test that fails for the right reason. Run it and read the
   message: it must fail because the implementation is missing, not because of a
   bad import or a typo.
3. **Green.** Smallest implementation that passes. Ugly is allowed here.
4. **Confirm the rest is still green.** Fix regressions now, not later.
5. **Refactor** with the net in place: no behaviour change, suite after each step.
6. **Widen the cases**: errors, limits, empty input, concurrency if it applies.
   Each new case returns to step 2.
7. **Measure coverage** as a diagnostic, never as a goal. Every new branch needs
   a case that reaches it; a percentage is not evidence.

## Exit Criteria

- [ ] The new test failed first, and the failure message was observed.
- [ ] It now passes and the full suite is green, with the command output quoted.
- [ ] Coverage of the touched area did not drop — check with the `coverage-gate`
      tool when a report exists.
- [ ] For a defect: a test reproduces it and fails without the patch.

## Common Failures

| Failure | Fix |
|---|---|
| Test written after the implementation | Delete it and rewrite it, watching it fail |
| Test asserts internals (mocks of private calls) | Assert observable output |
| Test fails for an environment reason | Fix the environment; that is not the signal |
| "I tested it by hand" | Manual runs leave no reproducible evidence: convert to a test |
| Chasing 100% coverage | Cover new branches; the percentage is a diagnostic |
| One test for three behaviours | One test per behaviour, so the failure names the cause |
