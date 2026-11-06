---
name: error-handling
description: Make failures loud, typed and recoverable instead of swallowed, logged twice or converted to null. Use when writing code that can fail, or when a silent failure is suspected in existing code.
metadata:
  origin: ECC · skills/error-handling (pattern)
  category: engineering
  phase: implement
  status: adopted
  version: 1
---

# Error Handling

Most production incidents are not "something threw"; they are "something threw and
nobody found out". This skill is about the second kind.

## When to Use

- Writing code with an error path (I/O, network, parsing, permissions).
- Suspecting a silent failure: the UI empty, the list short, the job "successful"
  with no data.
- Reviewing a diff that adds `try`/`catch`.

## When Not to Use

- Pure computation that cannot fail for the inputs it receives.
- Places where the language already propagates and the caller handles it: adding a
  layer there is noise.
- Language-native propagation the caller already handles: `error-taxonomy` gives the code, and no layer is added.

## Procedure

1. **List every failure the function can produce** (inputs, environment,
   dependencies) and decide for each: propagate, translate, retry or absorb.
2. **Propagate by default.** Let it bubble to the layer that can decide.
3. **Translate at boundaries**: convert a library error into a domain error with
   context (what was being done, with which id) — never into a bare string.
4. **Retry only if the operation is idempotent and the failure is transient**, with
   a bounded count and a stop condition.
5. **Absorb only with a logged reason** and a visible degraded state. A fallback
   that returns empty must say so where a human will see it.
6. **Never swallow**: an empty `catch`/`except` is a bug, not error handling.
7. **No double logging**: log once, at the layer that decides. Intermediate layers
   add context and re-raise.

## Exit Criteria

- [ ] Every failure path is propagate, translate, retry or absorb — written down.
- [ ] Zero empty catch blocks; `silence-scan` reports none.
- [ ] Retries are bounded and idempotent.
- [ ] An absorbed failure leaves a visible trace (log with context, status flag).
- [ ] No `null`/`undefined` returned to signal an error without saying so in the name.

## Common Failures

| Failure | Fix |
|---|---|
| `except: pass` to "keep going" | Propagate with context |
| Catching and logging at every layer | Log once, where the decision is made |
| Returning `null` on error | Raise, or return a result type |
| Infinite retry on a permanent failure | Classify retryability; bound the count |
| Error message "Something went wrong" | Name the operation and the id |
| Swallowing in a background job | Surface a failure counter or alert |
