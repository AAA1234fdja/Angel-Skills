---
name: test-suite-adoption
description: Adopt an existing test suite, or rescue one nobody trusts: measure what it actually covers, find the tests that cannot fail, and get from red to a baseline. Use when inheriting a repo, when a suite is skipped in CI, or when "the tests pass" and production disagrees.
metadata:
  origin: original
  category: tests
  phase: audit
  status: original
  version: 1
---

# Test Suite Adoption

Inheriting a test suite is not the same as inheriting confidence. A suite can have a
thousand tests and prove nothing: assertions that never run, tests that assert on
mocks, a skip list longer than the file, a green run that hides an ignored failure. The
job is to find out which tests can fail, in what order to trust them, and what the
minimum honest baseline is — not to admire the count.

## When to Use

- Inheriting a repository, a service or a test folder from another team.
- CI is green and production disagrees.
- The suite is skipped, quarantined or marked `xfail` in bulk.
- Before deleting tests, so the deletion is evidence-based.

## When Not to Use

- Writing new tests for a change: that is `tdd-workflow`.
- One test that fails intermittently: that is `flaky-test-triage`.
- Improving coverage numbers as a goal: coverage is an input, not the objective.

## Procedure

1. **Run the suite as CI runs it, before touching anything**, and record the count,
   duration, skips and warnings. That run is the baseline everything else is measured
   against.
2. **Count tests that cannot fail**: no assertions, assertions on mocks only, bare
   `assert True`, tests that catch their own exceptions. These are the dangerous ones
   because they are green.
3. **Inventory skips with reasons.** An `xfail` with a linked issue is a decision; an
   `xfail` without one is a deletion that kept the file.
4. **Classify by value, not by level**: does this test fail when the behaviour breaks?
   Mutate one behaviour by hand and see which tests notice — a cheap, brutal check on
   a small sample.
5. **Establish the honest baseline**: the set of tests you trust, run green, with the
   known failures listed by name and owner. Never a percentage that hides the list.
6. **Fix trust before adding coverage**: a suite nobody trusts is not extended, it is
   argued with.
7. **Run `suite-baseline`** on the inventory: it flags assertion-free tests, unattributed
   skips, a suite duration that would tempt anyone to disable it, and tests that pass
   while their subject is mutated.
8. **Publish the baseline as a gate**: CI must fail on new assertion-free tests and on
   new unattributed skips, or the recovery decays in a quarter.

## Exit Criteria

- [ ] A recorded baseline run: count, duration, skips, warnings, known failures.
- [ ] Assertion-free tests are counted and either fixed or deleted.
- [ ] Every skip has a reason and an owner or a linked issue.
- [ ] A sample of tests was mutation-checked against a real behaviour change.
- [ ] Known failures are listed by name, with an owner.
- [ ] CI fails on new assertion-free tests and on unattributed skips.
- [ ] `suite-baseline` reports no unattributed skip and no silent test.

## Common Failures

| Failure | Fix |
|---|---|
| Trusting the green run | Count tests that cannot fail; check a mutation sample |
| Bulk `xfail` as a cleanup | Every skip gets a reason and an owner |
| Coverage percentage as the goal | Track trusted tests and mutation detection |
| Deleting tests you do not understand | Understand it, then delete with evidence |
| Baseline recorded as a percentage | Record names, not ratios |
| No gate after the cleanup | Fail CI on new silent tests and new unattributed skips |
