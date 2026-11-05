---
name: flaky-test-triage
description: Turn a flaky test into a diagnosis: quarantine it, reproduce it, name the source of nondeterminism and fix or delete it. Use when CI fails and passes without a code change, when "just retry" is becoming policy, or before a suite's signal stops being trusted.
metadata:
  origin: original
  category: engineering
  phase: debug
  status: original
  version: 1
---

# Flaky Test Triage

A flaky test is worse than no test: it costs the time of everyone who reads its
failure, and it teaches the team to ignore red. The only wrong response is the
retry button. This procedure quarantines the test so the suite stays trustworthy,
then finds the actual source of nondeterminism — which is almost always in the
code under test, not in the test.

## When to Use

- A test fails and passes without any relevant change.
- CI shows "failed on the first attempt, passed on retry".
- A suite is being made required, and something in it is already intermittent.
- A developer says "it's just flaky" and moves on.

## When Not to Use

- A test that fails consistently in one environment: that is an environment bug,
  not flakiness.
- Timing assertions in a load test where variance is the subject.
- Quarantining more than a handful of tests at once: that is a broken suite, and
  the fix is the suite.

## Procedure

1. **Prove it is flaky, not broken.** Run it ten times unchanged and record the
   pass/fail sequence. One failure in ten and nine in ten are different bugs; the
   sequence is the evidence.
2. **Quarantine it in the same commit**, visibly: a marker on the test with a link
   to the ticket, and the count of runs. A quarantined test still runs in a
   separate job, so it cannot silently rot.
3. **Classify the source** with the `flake-classifier` tool on the observations:
   time, ordering, shared state, network, randomness, concurrency, or resource
   leak. The classification decides the fix; skipping it makes the fix a guess.
4. **Reproduce deterministically** before fixing: a seed, a fixed clock, a forced
   interleaving, a stubbed network. If it cannot be reproduced on demand, the
   diagnosis is not finished.
5. **Fix the cause, not the assertion.** Raising a timeout is a fix only when the
   slow path is legitimate. Sleeps, retries and `waitFor` loops hide the bug in
   the product and make the next flake slower to find.
6. **Un-quarantine only with evidence**: the same ten-run check now passes
   reliably, and the ticket records what the source was.
7. **Delete tests that cannot be made deterministic** if they assert nothing a
   user can observe. A test that only proves the clock moved is not a test.

## Exit Criteria

- [ ] The pass/fail sequence over ten runs is recorded.
- [ ] The test is quarantined visibly, with a ticket, if it is still failing.
- [ ] `flake-classifier` names the source category, and the reproduction is
      deterministic.
- [ ] The fix addresses the cause; any timeout change states why the slow path is
      legitimate.
- [ ] Ten clean runs after the fix, quoted in the ticket.
- [ ] The suite has no unacknowledged quarantine markers.

## Common Failures

| Failure | Fix |
|---|---|
| Retry the job until green | The signal is gone; quarantine and diagnose instead |
| Raising the timeout | Only legitimate if the slow path is real; otherwise it hides the bug |
| `sleep(1)` in the test | Fix the synchronisation or assert on the observable state |
| "It's the CI machine" | Prove it: run the same test locally on a constrained CPU |
| Quarantine with no ticket | A disabled test with no owner is a deleted test nobody knows about |
| Fixing the test, not the code | Shared state and leaks are product bugs the test found |
