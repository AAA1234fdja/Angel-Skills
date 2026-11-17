---
name: eval-harness
description: Eval-driven development: criteria written before the change, the cheapest grader that works, and pass@k versus pass^k. Use when a prompt, tool or model changed and numbers must decide whether it improved.
metadata:
  origin: ECC · skills/eval-harness
  category: agentic
  phase: verify
  status: adopted
  version: 1
---

# Eval Harness

If you cannot say whether a change improved the agent, you did not improve it: you
changed it. Evals are the unit tests of AI development, and they are written
**before** the modification.

## When to Use

- A system prompt, tool, model or version changes.
- Choosing between two agent configurations.
- An agent behaves differently from one day to the next and a stable measure is
  needed.

## When Not to Use

- Deterministic business logic: that is a normal test.
- When the task cannot be executed repeatedly: build the reproducible environment
  first.
- Deterministic business logic, where a normal test is the whole answer: `tdd-workflow`.

## Procedure

1. **Write the task and success criteria before the change.** Each eval is a
   concrete task with checkable criteria, not a general impression.
2. **Classify it**:
   - *capability* — something the agent could not do and now should;
   - *regression* — something it already did and cannot stop doing; record the
     baseline (commit, model version).
3. **Pick the cheapest grader that works**:
   - **code**: grep, test, build, schema, exact output — deterministic, always
     preferred;
   - **model**: another model scores against an explicit 1–5 rubric with reasons;
     for open outputs, validated against humans;
   - **human**: only when neither can decide; reserved.
4. **Run k ≥ 3 attempts per eval.** One run says nothing about reliability.
5. **Compute** `pass@k` (at least one success in k — capability) and `pass^k`
   (**all** k succeed — reliability, the hard bar), plus cost per completed task
   and retries per task.
6. **Compare against the baseline** with the same set, the same grader and the same
   environment.
7. **Record the result** with date, version and diff. An unrecorded eval is useless
   next week.

## Exit Criteria

- [ ] Every eval has a task, success criteria and an explicit grader.
- [ ] The baseline is recorded before the change.
- [ ] k ≥ 3 per eval, with both `pass@k` and `pass^k` reported.
- [ ] Cost per completed task reported alongside success rate.
- [ ] The verdict is a decision: keep, revert or reformulate.
- [ ] Regression evals are versioned for next time.

## Common Failures

| Failure | Fix |
|---|---|
| One run and a conclusion | k ≥ 3; report `pass^k` |
| Model grader with no rubric | Fixed criteria and scale |
| Editing the eval so the change passes | Evals are written first and not edited |
| Comparing against another environment | Same set, same environment |
| Measuring success only | Cost per completed task |
| Evals depending on repo state | Reproducible, clean environment per run |
| Mixing capability and regression | Separate series: one rises, the other cannot fall |
