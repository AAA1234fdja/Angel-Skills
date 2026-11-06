---
name: performance-optimizer
description: Turn a slowness complaint into a measured change: baseline with dispersion, one bottleneck, one hypothesis, comparison against the baseline. Use when there is a concrete performance complaint or a latency budget being missed.
metadata:
  origin: ECC · agent performance-optimizer
  category: engineering
  phase: implement
  status: adopted
  version: 1
---

# Performance Optimizer

Optimising without measuring is changing code and believing it improved. The rule
is simple: **baseline first, then one hypothesis, and the number decides**.

## When to Use

- A concrete slowness complaint ("the list takes seconds", "the build takes four minutes").
- A latency or memory budget that is being missed.
- Before scaling a service, to know where it hurts.

## When Not to Use

- With no possible measurement: if it cannot be measured it cannot be optimised.
- When the cause is a network or database wait: fix the cause (N+1, missing index)
  before touching client code.
- Code that is not on the critical path and has not been profiled.
- Optimisation with no measurement behind it: `benchmark-discipline` produces the number first.

## Procedure

1. **Define the metric and scenario**: what is measured (p50, p95, total time,
   memory, tokens), with which data, under which reproducible command.
2. **Take the baseline** at least three times and record dispersion. A single
   number cannot show whether a change helped.
3. **Profile, do not guess**: language profiler, `--cpu-prof`, `py-spy`, `perf`,
   `EXPLAIN` in SQL, network waterfall in the browser.
4. **Pick ONE bottleneck** and write the hypothesis: "70% of the time is in X; if
   Y changes, it drops".
5. **Apply the minimal change** that tests the hypothesis. Do not rewrite the
   module on the way.
6. **Measure again the same way** (three runs, same scenario). If it does not
   improve beyond the dispersion, revert: an unproven optimisation is not kept.
7. **Verify correctness**: full suite green. Gaining speed by breaking behaviour is
   not an improvement.
8. **Record** before → after and why that change was chosen.

## Exit Criteria

- [ ] Baseline measured and quoted, with dispersion.
- [ ] One hypothesis per change, backed by a profile or plan (`bench-compare`
      says whether the difference is real).
- [ ] Post-change measurement with the same method, outside the noise band.
- [ ] Suite green and behaviour identical.
- [ ] If there was no improvement, the change is reverted.
- [ ] The pull request summarises before → after in a table.

## Common Failures

| Failure | Fix |
|---|---|
| Optimising on intuition | Profile first |
| Changing three things and measuring once | One hypothesis per iteration |
| Comparing a measurement from another environment | Same scenario, same data |
| Changing behaviour for speed without saying so | That is a contract change: document it |
| "300% faster" with no baseline | Without a baseline there is no improvement |
| Adding a cache as the first move | A cache hides a cause: last resort |
| Micro-optimising the 2% | Attack the bottleneck from step 3 |
