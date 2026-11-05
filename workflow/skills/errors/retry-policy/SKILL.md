---
name: retry-policy
description: Decide retryability per error code, with backoff, budget and a stop condition that cannot loop forever. Use when adding retries, when a job loops on a permanent failure, or when two layers retry the same call.
metadata:
  origin: ECC · agent-harness-construction (pattern)
  category: errors
  phase: implement
  status: adopted
  version: 1
---

# Retry Policy

Retries turn a transient failure into a success and a permanent failure into an
outage with extra load. The difference is entirely in the policy, so the policy has
to exist before the retry does.

## When to Use

- Adding retries to a network, database or subprocess call.
- A job loops on a failure that will never succeed.
- Two layers retry the same call and multiply the load.

## When Not to Use

- Operations with side effects that are not idempotent (a payment, a deploy, an
  email) unless an idempotency key exists.
- Validation failures and anything the caller must fix.

## Procedure

1. **Classify each error code** as transient or permanent, from the taxonomy — not
   from the exception message text.
2. **Retry only transient codes**, and only for idempotent operations.
3. **Bound it**: maximum attempts, exponential backoff with jitter, and a total time
   budget.
4. **One layer retries.** Pick it, and make the others propagate.
5. **Write the stop condition**: after N attempts or T seconds, surface the failure
   with the last cause attached.
6. **Log each attempt with its number** so a loop is visible after one minute, not
   after one hour.
7. **Test the stop path**, not just the happy retry.

## Exit Criteria

- [ ] Retryability declared per code in the taxonomy.
- [ ] Attempts, backoff and total time are all bounded.
- [ ] Exactly one layer in the call chain retries.
- [ ] Side-effecting calls have an idempotency key or are not retried.
- [ ] The stop path is tested and surfaces the last cause.
- [ ] `retry-plan` accepts the policy (it rejects unbounded ones).

## Common Failures

| Failure | Fix |
|---|---|
| Retrying validation errors | They never succeed: fix the input |
| Two layers retrying | Multiplicative load; pick one |
| Constant delay | Thundering herd; use exponential with jitter |
| Retrying a non-idempotent write | Duplicate side effects |
| No stop condition | The loop outlives the outage |
| Logging only the final failure | Log the attempt number and cause |
