---
name: codebase-onboarding
description: Learn an unfamiliar codebase fast enough to change it safely: the entry points, the three paths that matter, and the first change that proves you understand it. Use when joining a repository, when inheriting a service, or before a change in a codebase you have only read.
metadata:
  origin: adapted · ECC · skills/codebase-onboarding
  category: research
  phase: research
  status: adopted
  version: 1
---

# Codebase Onboarding

Reading a codebase is not onboarding. The test of onboarding is a change: you can
predict what a small edit will touch, you can run it, and the prediction holds.
Diagrams and folder tours feel like progress and produce nothing you can execute, so
this procedure spends most of its time on the paths that a real request will travel
and ends at a change, not at a document.

## When to Use

- Joining a repository, or inheriting a service from another team.
- About to make a first change in a codebase you have only read.
- A new contributor needs to become useful within days, not weeks.
- The documentation disagrees with the code and nobody knows which is current.

## When Not to Use

- Measuring what a specific change will break: `change-impact` predicts it.
- Producing a guided walkthrough for others: `code-tour` anchors it to lines.
- Assessing whether the design is any good: `code-review` is not the tool — that is a design discussion with `adr-writing` at the end.

## Procedure

1. **Find the entry points by executing them**, not by reading the README: the
   command that starts the app, the one that runs the tests, the one that runs one
   test. If a README command fails, that is the first finding, and it is a good one.
2. **Trace three real requests end to end**: one read, one write, one failure. They
   cover routing, persistence and error handling, which is most of any service.
3. **Name the boundaries**: where an external call happens, where data is validated,
   where the transaction begins and ends. These are the places every change touches.
4. **Read the tests before the implementation** for the area you will change. Tests
   that exist describe intent; tests that are missing describe risk.
5. **Write down the conventions you inferred** — naming, error style, where business
   logic lives — and check three of them against a real file. An inferred convention
   that nobody confirms is how a newcomer introduces a style drift.
6. **Predict one small change before making it**: files touched, tests to run, what
   could break. Then make it and compare. The gap between prediction and reality is
   your actual understanding, measured.
7. **Record the questions you could not answer** and who could. A new person's
   questions are the best documentation audit available and they expire in a week.
8. **Run `onboarding-check`** on your notes: it flags missing entry points, fewer
   than three traced paths, unconfirmed conventions and no predicted-then-actual change.

## Exit Criteria

- [ ] Start, test and single-test commands are recorded and were executed.
- [ ] Three paths traced end to end: read, write and failure.
- [ ] Boundaries named: external calls, validation, transaction scope.
- [ ] Three inferred conventions confirmed against real files.
- [ ] One change predicted, made, and the prediction compared with reality.
- [ ] Open questions recorded with the person who could answer them.
- [ ] `onboarding-check` reports no missing path and no unconfirmed convention.

## Common Failures

| Failure | Fix |
|---|---|
| Reading the README instead of running it | Execute the commands; a broken README is a finding |
| Folder tour as onboarding | Trace three requests; folders do not run |
| Skipping the failing path | Errors are where the architecture actually lives |
| Assuming conventions from one file | Confirm three of them against real code |
| No first change | End at a change, predicted and compared; that is the only proof |
| Questions kept private | Record them with an owner; they expire fast |
