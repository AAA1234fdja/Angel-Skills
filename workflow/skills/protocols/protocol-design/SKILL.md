---
name: protocol-design
description: Design a message protocol: envelope, payload, allowed consumers, versioning and rejection rules. Use when roles must hand structured work to each other and ad-hoc dictionaries are starting to drift.
metadata:
  origin: ECC · agent-harness-construction (pattern)
  category: protocols
  phase: plan
  status: adopted
  version: 1
---

# Protocol Design

Any two roles exchanging data will invent a format. The question is whether that
format is declared once and validated, or rediscovered in every handler. This skill
declares it.

## When to Use

- Roles (planner, executor, verifier) mutually hand off structured work.
- Handlers start checking `if "field" in msg` defensively.
- A message format is about to be shared across processes or teams.

## When Not to Use

- A function call within one process: use the type system.
- A single producer with a single consumer and no versioning pressure.

## Procedure

1. **Define the envelope once**: protocol name, version, task id, origin, target,
   message id, timestamp, optional parent. Everything else goes in the payload.
2. **Declare allowed consumers per protocol.** A message nobody is allowed to
   consume is a message nobody validates.
3. **Derive the payload from the decision the receiver makes** (same rule as
   `contract-design`).
4. **Decide rejection rules up front**: unknown fields, unknown version, unknown
   role — all errors, or you inherit silent drift.
5. **Version the protocol, not just the payload.** A receiver must refuse versions
   it does not declare.
6. **Write one example per message** and use it as the test fixture.
7. **Generate the skeleton** with `protocol-skeleton` and keep it next to the code.

## Exit Criteria

- [ ] Envelope defined once and reused by every message.
- [ ] Consumers declared per protocol.
- [ ] Rejection rules written: unknown field, version and role.
- [ ] Version advertised and enforced by the receiver.
- [ ] One fixture per message type, used in tests.

## Common Failures

| Failure | Fix |
|---|---|
| Payload-only design, envelope invented per handler | Envelope first |
| Accepting unknown fields "for compatibility" | They hide producer bugs |
| One protocol for everything | Split by receiver decision |
| Version in docs, not in the message | The message carries the version |
| No fixtures | The first test becomes the fixture, late |
