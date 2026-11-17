---
name: autonomous-loop
description: Run unattended loops safely: explicit stop conditions, budgets, checkpoints and human gates. Use when a task should repeat without supervision, or when an existing loop keeps running past its usefulness.
metadata:
  origin: ECC · autonomous-loops + continuous-agent-loop
  category: agentic
  phase: implement
  status: adopted
  version: 1
---

# Autonomous Loop

An unattended loop without a stop condition is an outage waiting for a clock. The
only difference between "keeps improving the code" and "keeps breaking the code
forever" is the guards you write before starting.

## When to Use

- A task is repetitive and verifiable by machine (fix until green, iterate on a
  benchmark, sweep a backlog).
- Running overnight or in CI without a human watching.
- Turning a manual retry habit into a bounded loop.

## When Not to Use

- The success condition is subjective.
- Steps are destructive or irreversible: those need human gates.
- The task is a one-off; a loop adds machinery for nothing.
- Choosing what the loop should pursue: the task space is `agent-harness-construction`.

## Procedure

1. **Write the success test first** — the exact command that means "done".
2. **Write the stop conditions**: max iterations, max wall-clock, max cost, no
   progress in N iterations, and any appearance of a blocking error.
3. **Write the failure policy**: what happens on iteration failure — retry once,
   revert the iteration, or stop.
4. **Add checkpoints**: after each successful iteration, leave a recoverable state
   (commit, snapshot, journal entry).
5. **Add human gates** for irreversible actions (deploy, delete, permission change).
6. **Guarantee progress detection**: compare a metric per iteration; if it does not
   improve for N iterations, stop.
7. **Log every iteration** with what changed and the metric, so a post-mortem is
   reading, not archaeology.

## Exit Criteria

- [ ] Success test is a command that exits 0 or 1.
- [ ] At least three independent stop conditions.
- [ ] Failure policy written per iteration.
- [ ] A checkpoint exists after every successful iteration.
- [ ] Irreversible actions sit behind a gate.
- [ ] `loop-guard` accepts the definition.

## Common Failures

| Failure | Fix |
|---|---|
| "Until it works" | A command plus a max iteration count |
| Stopping only on time | Add no-progress and cost limits |
| No checkpoint | One bad iteration loses the good ones |
| Destructive steps inside the loop | Move them behind a gate |
| Metric not compared per iteration | Progress detection is the safety net |
| Logs without iteration numbers | Post-mortem becomes guesswork |
