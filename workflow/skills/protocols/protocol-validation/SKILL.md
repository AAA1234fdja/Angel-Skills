---
name: protocol-validation
description: Validate a file or stream of protocol messages and report the first rejection with its stable code. Use when a producer changed, a queue contains suspicious payloads, or a receiver must prove it refuses malformed input.
metadata:
  origin: ECC · agent-harness-construction
  category: protocols
  phase: verify
  status: adopted
  version: 1
---

# Protocol Validation

A receiver that accepts everything is not permissive, it is unverified. This
procedure proves the receiver refuses what it must refuse.

## When to Use

- A producer changed and messages started behaving oddly.
- A queue or log contains payloads from an unknown version.
- Before shipping a receiver: prove it rejects the bad cases.

## When Not to Use

- Messages you just built with the typed factory in the same process.
- Transport-level validation (TLS, size limits): a different layer.

## Procedure

1. **Parse before you process.** Never index into an unvalidated dict.
2. **Check version against the receiver's advertised set.** Refuse others.
3. **Check the origin/target pair** against the declared consumers.
4. **Reject unknown fields**; log the field name, not the whole payload (it may
   contain secrets).
5. **Report the first violation with its code** — deterministic, quotable.
6. **Keep a corpus of bad messages** and run it as a test: one message per
   rejection class.
7. **Count rejections** over time; a rising rate is a producer regression.

## Exit Criteria

- [ ] Version, role and consumer checks run before payload access.
- [ ] Unknown fields rejected with the field name logged.
- [ ] Rejection carries a stable code and a path.
- [ ] A corpus covers each rejection class and runs in the suite.
- [ ] Rejection count is observable (log or metric).

## Common Failures

| Failure | Fix |
|---|---|
| `msg["x"]` before validating | Parse, validate, then access |
| Accepting unknown versions "to be tolerant" | Tolerant receivers hide producer bugs |
| Logging the whole payload on rejection | It may contain secrets; log the path |
| No corpus of bad messages | The first production incident becomes the corpus |
| Retrying a rejected message unchanged | Rejection is not transient (`retry-policy`) |
