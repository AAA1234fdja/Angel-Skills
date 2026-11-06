---
name: benchmark-discipline
description: Produce a number someone can trust: a baseline, a stated environment, repeated runs and the variance. Use when claiming a speedup, comparing two implementations, when a benchmark decides a dependency, or when someone says it feels faster.
metadata:
  origin: original
  category: data
  phase: verify
  status: original
  version: 1
---

# Benchmark Discipline

A benchmark without a baseline and a variance is an anecdote with decimals. The
number itself is the least interesting part: what matters is whether the difference
survives the noise, whether the machine and the data are stated, and whether the
measurement is what the user experiences. This procedure is short because the
failure mode is always the same — measuring once, on a warm cache, and rounding
towards the conclusion.

## When to Use

- Claiming a speedup, an improvement or a regression.
- Choosing between two implementations or two dependencies.
- A performance budget is being enforced in CI.
- Someone reports "it feels slower" and needs a number, not an argument.

## When Not to Use

- Correctness: a benchmark says nothing about whether the result is right.
- A single long-running job where variance is irrelevant and one run is the truth.
- Capacity planning at a scale you cannot reproduce: that needs a model, not a micro-benchmark.
- Correctness questions, where a benchmark proves nothing: `verification-loop`.

## Procedure

1. **State the question and the metric** before running anything: latency p50/p99,
   throughput, memory high-water mark. "Faster" is not a metric.
2. **Measure the baseline first, on the same machine, the same data and the same
   commit style.** A baseline from last week on another host is not a baseline.
3. **Run enough iterations** to see the noise: at least ten, warm-up discarded,
   and report the spread, not just the mean.
4. **Control the environment**: CPU governor, container limits, background load,
   dataset size, cache state. If it is not controlled, it is not stated — and an
   unstated environment makes the number unreproducible.
5. **Compare distributions**: median and tail together. A faster median with a worse
   p99 is a regression for anyone on the tail.
6. **Run the `bench-compare` tool** on the two sample sets. It reports the change, the
   spread and whether the difference exceeds the noise; a delta inside the noise is
   reported as no difference, however inconvenient.
7. **Record the command and the artefact** so the run can be repeated. A benchmark
   nobody can rerun decays into folklore within a release.

## Exit Criteria

- [ ] The question and the metric are stated before the run.
- [ ] A baseline exists, measured on the same machine and data.
- [ ] At least ten iterations, warm-up discarded, spread reported.
- [ ] Environment is controlled and stated (CPU, limits, data, cache).
- [ ] The comparison is on distributions, including the tail.
- [ ] `bench-compare` reports whether the difference exceeds the noise.
- [ ] The command and the artefact are recorded for reproduction.

## Common Failures

| Failure | Fix |
|---|---|
| One run, mean only | Ten runs, report spread; the mean hides the tail |
| Baseline from another machine | Re-measure the baseline in the same environment |
| Warm cache, cold cache mixed | State the cache state; measure both if it matters |
| Comparing medians only | Compare p99 too; regressions hide there |
| Delta inside the noise, reported as a win | Say no difference; the noise is the finding |
| No command recorded | Record it; unreproducible benchmarks are folklore |
