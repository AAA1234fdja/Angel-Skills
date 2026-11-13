---
name: webhook-contract
description: Design the webhook you send so a consumer can trust it: signature, replay window, ordering guarantee, retry schedule and dead-letter path. Use when publishing events to other teams or customers, or when a consumer reports duplicates, gaps or unverifiable deliveries.
metadata:
  origin: original
  category: protocols
  phase: design
  status: original
  version: 1
---

# Webhook Contract

A webhook is an async API where every failure is invisible unless you designed for it.
The consumer cannot re-read what it missed, cannot tell a duplicate from a second
event, and cannot prove the call came from you. Each of those is a decision made once,
in the contract, and expensive to add after customers have built on the endpoint —
which is why this is a design procedure and not an operational one.

## When to Use

- Publishing events to another team, a customer or a partner endpoint.
- A consumer reports duplicates, gaps, out-of-order events or "we got nothing".
- An existing webhook has no signature or no retry policy.
- Before adding a new event type to a feed somebody already depends on.

## When Not to Use

- Changing an event's schema without breaking consumers: `event-versioning`.
- The message format inside an internal protocol: `protocol-design`.
- Delivering reliably inside your own system, where you control both ends: `retry-policy`.

## Procedure

1. **Make delivery verifiable**: sign the exact body with a shared secret, include a
   timestamp and a delivery id, and document the verification algorithm. A consumer who
   cannot verify has to trust the network.
2. **Bound replay**: the signature covers a timestamp and the consumer rejects anything
   older than the stated window. Say the window; an unbounded signature is replayable
   forever.
3. **Guarantee at-least-once and say so**, with an idempotency key per event. Consumers
   that assume exactly-once will double-process, and it will be your name on the incident.
4. **State the ordering answer**: per-entity ordering only, with the key named, or no
   ordering at all. "Ordered" without a key is a promise nobody can keep.
5. **Publish the retry schedule**: attempts, intervals, backoff and the total window.
   A consumer needs to know when to expect the last attempt, to decide when to reconcile.
6. **Define the dead-letter outcome**: what happens after the last attempt — dropped,
   replayed on request, or visible in a dashboard. Silent drop is the default nobody chose.
7. **Version the payload in the header**, not only in the body, so a consumer can route
   without parsing. Breaking changes need a new version, not a new field.
8. **Run `webhook-contract-check`** on the design: it refuses missing signature or
   timestamp, no replay window, exactly-once claims, unordered promises without a key,
   no retry schedule and no dead-letter path.

## Exit Criteria

- [ ] The body is signed, with the algorithm documented, and a timestamp included.
- [ ] A replay window is stated and enforced by the consumer.
- [ ] At-least-once is stated, with an idempotency key per event.
- [ ] The ordering guarantee names its key, or says there is none.
- [ ] The retry schedule is published with attempt count and total window.
- [ ] The dead-letter outcome is defined and visible.
- [ ] The version is in the header.
- [ ] `webhook-contract-check` refuses nothing.

## Common Failures

| Failure | Fix |
|---|---|
| Unsigned payloads | Sign the body; document the verification |
| Signature with no timestamp | A captured call is replayable forever |
| "Exactly once" | At-least-once plus an idempotency key |
| "Events arrive in order" | Per-entity ordering with a named key, or none |
| Unlimited retries | Publish the schedule and the total window |
| Dropped after N attempts, silently | Define the dead-letter outcome |
| Version only in the body | Put it in the header as well |
