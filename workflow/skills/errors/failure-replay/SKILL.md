---
name: failure-replay
description: Rebuild a failure from the record until it happens again on demand, then turn it into a test. Use when a failure is described but not reproducible, when the logs are the only witness, or when a fix cannot be called fixed because nobody can make it fail.
metadata:
  origin: original
  category: errors
  phase: debug
  status: original
  version: 1
---

# Failure Replay

A failure you cannot reproduce is a rumour with a stack trace. The work is not to
guess the cause; it is to reconstruct the conditions until the failure happens on
demand, because only then does a fix have something to be verified against. This sits
between forensics (which explains what happened) and the regression test (which keeps
it from happening again), and without it both of those are guesswork.

## When to Use

- A failure is described but nobody can make it happen again.
- Logs are the only witness: no trace, no repro, no failing test.
- A fix was merged without a failing test that preceded it.
- An intermittent failure has been "fixed" twice and returned.

## When Not to Use

- The journal explains the run and you need the causal chain: `failure-forensics`.
- The failure is a timing artefact with no stable conditions: `flaky-test-triage` classifies it first.
- You need the error to carry better recovery information: `error-recovery`.

## Procedure

1. **Freeze the failure description** into a record: what was done, in what order,
   with what input, at what time, on what version. Anything not in the record is a
   variable you will accidentally change.
2. **List the variables the record does not pin** — data volume, clock, locale, network
   state, concurrency, feature flags. This list is your search space, ranked by how
   plausible each variable is.
3. **Replay the cheapest plausible variable one at a time.** Two at once and a success
   teaches you nothing about which mattered.
4. **Make the observation deterministic before making the reproduction fast**: a fixed
   seed, a frozen clock, a captured payload. Speed comes after, if ever.
5. **Prove the reproduction is the same failure** — same code path, same message, same
   state — not merely a similar error. A repro of a different bug is worse than none.
6. **Reduce to the smallest input that still fails**, and keep the reduction steps in
   the commit message or the issue. Someone will need to widen it later.
7. **Turn it into a test that fails before the fix**, and confirm it fails for the
   right reason. Then fix, then watch the same test pass.
8. **Run `replay-check`** on the record: it flags an unpinned variable list, a
   reproduction claimed without the same signature, several variables changed at once,
   and a fix with no preceding failing test.

## Exit Criteria

- [ ] The failure is frozen into a record with version, input, time and order.
- [ ] Unpinned variables are listed and ranked by plausibility.
- [ ] Variables were replayed one at a time.
- [ ] The reproduction is proven to be the same failure (path, message, state).
- [ ] The minimal failing input is recorded with its reduction steps.
- [ ] A test fails before the fix and passes after, for the stated reason.
- [ ] `replay-check` reports a pinned record, a proven signature and a preceding test.

## Common Failures

| Failure | Fix |
|---|---|
| Guessing the cause from the stack trace | Replay until it happens on demand |
| Changing many variables at once | One at a time, or you learn nothing |
| Repro that is a different bug | Compare path, message and state, not vibes |
| Fixing without a failing test | The test is the proof the fix does anything |
| Reproduction that depends on your machine | Pin seed, clock, locale and data |
| Never reducing the input | The reduction is what makes the test maintainable |
