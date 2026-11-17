---
name: error-recovery
description: Attach a recovery contract to every failure path: root-cause hint, safe retry, stop condition. Use when an error message would leave an agent or a person guessing what to do next.
metadata:
  origin: ECC · agent-introspection-debugging
  category: errors
  phase: implement
  status: adopted
  version: 1
---

# Error Recovery

An error that only says what went wrong is half an error. The other half is what to
do about it — and that half is what makes an agent able to continue without a
human reading the source.

## When to Use

- Writing an error a caller or an agent will have to act on.
- An agent retries the same failing call because the message gave it nothing else.
- Reviewing error messages before they become a public contract.

## When Not to Use

- Errors consumed only by the enclosing function and re-raised immediately.
- Assertions that encode programmer mistakes, which should never be recovered.
- Programmer mistakes that should not be recovered: `error-taxonomy` records them, and the assertion stands.

## Procedure

1. **Answer three questions for every error path**:
   - root cause hint: what likely produced this;
   - safe retry: may the same operation be repeated unchanged;
   - stop condition: when to give up instead of looping.
2. **Make the retry answer a decision, not a mood.** "Safe to retry once" beats
   "try again later".
3. **Include the minimum context** needed to reproduce: identifier, path, phase —
   never credentials or full payloads.
4. **Point to the fix when it is deterministic**: which file, which command, which
   config key.
5. **Keep the hint stable across versions** if code branches on it; put volatile
   detail in the context object.
6. **Test the recovery path**: one test asserting the hint and the retry flag are
   present for each error class.
7. **Check that the recovery advice is executable**: a hint that requires a tool the caller does not have is decoration. Name the command, not the concept.

## Exit Criteria

- [ ] Every error has hint, retryability and stop condition.
- [ ] Retryability is a boolean decision, not prose.
- [ ] Context carries ids and paths, never secrets.
- [ ] A test asserts the recovery contract per error class.
- [ ] `recovery-audit` reports zero incomplete errors.

## Common Failures

| Failure | Fix |
|---|---|
| "Something went wrong" | Name the operation and the id |
| Retry advice in free text | A boolean plus a bounded count |
| Hint that names the source file only | Point at the fix, the command or the config |
| Context dumping the whole payload | Ids and paths; payloads may hold secrets |
| Recovery hint that changes every release | Stable hint, volatile detail in context |
| Hint that names a concept | Name the command or the file |
