---
name: failure-forensics
description: Reconstruct a failed run from its journal: what ran, what failed, what was retried, and where the chain of evidence breaks. Use when a run failed and the console output is not enough to explain it.
metadata:
  origin: ECC · agent-architecture-audit
  category: errors
  phase: debug
  status: adopted
  version: 1
---

# Failure Forensics

The console tells you the run failed. The journal tells you *when, in what order,
with what authorisation*. Forensics is the discipline of reading the second one
before forming a hypothesis.

## When to Use

- A run failed and the console summary is not enough.
- A run "passed" but produced the wrong result.
- A failure happens intermittently and needs a reproducible account.

## When Not to Use

- No journal exists: instrument first (`agent-harness-construction`), then
  investigate.
- A failure reproduced trivially in one step: fix it, forensics is overhead.

## Procedure

1. **Verify the chain first.** A journal that does not verify is the finding — it
   means the record was edited outside the runtime.
2. **Build the timeline** in sequence order: run.start, plan, dispatch, tool calls,
   results, verdicts, gate, run.end.
3. **Find the first anomaly**, not the loudest one: the last event is usually a
   consequence.
4. **Compare the plan with what actually executed.** Steps that never dispatched,
   dispatches with no result, results with no verdict.
5. **Check the budget** at the moment of failure: steps, tools, seconds.
6. **State the causal chain in three lines**: A caused B because C. If it takes
   longer, it is still a hypothesis.
7. **Write the guard**: an eval or a test that would have caught it
   (`eval-harness`, `ai-regression-testing`).

## Exit Criteria

- [ ] Chain verification result reported (ok or broken, with the first broken seq).
- [ ] Timeline produced with the first anomaly identified.
- [ ] The mismatch between plan and execution is named.
- [ ] Causal chain written in three lines.
- [ ] A guard exists that fails on the same cause.

## Common Failures

| Failure | Fix |
|---|---|
| Reading the last error and stopping | Start at the first anomaly |
| Ignoring a broken chain | The broken record is the finding |
| Hypothesising before the timeline | Timeline first, always |
| Blaming the tool | Check authorisation and payload in the journal |
| No guard added afterwards | Without a guard, it returns |
