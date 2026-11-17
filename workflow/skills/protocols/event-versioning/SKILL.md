---
name: event-versioning
description: Change an event schema without breaking consumers who read the old shape: additive first, dual-write, then retire. Use when a field is added to an event, when a consumer breaks after a producer deploy, or when "just add a field" is the plan.
metadata:
  origin: original
  category: protocols
  phase: document
  status: original
  version: 1
---

# Event Versioning

Events are read by consumers you do not deploy. That is the whole difficulty: a
producer can ship in a minute, a consumer fleet takes a week, and the events sent in
between are read by both old and new code. So an event change is a rollout, not an
edit — and the cheap changes (adding an optional field) and the expensive ones
(renaming, changing type, making a field required) must be told apart before anyone
writes code.

## When to Use

- A field is being added, renamed, retyped or removed from an event.
- A consumer broke after a producer deploy nobody considered breaking.
- Two versions of the same event are already in flight and nobody knows which is authoritative.
- An event has to stay readable by both old and new consumers for a transition window.

## When Not to Use

- An event with exactly one consumer deployed together with the producer: that is a function call with extra steps.
- Designing the protocol itself: `protocol-design` owns the shape; this owns the change.
- Validating a single message against its schema: `protocol-validation`.

## Procedure

1. **Classify the change** before writing it: additive (optional field, new enum value
   consumers may ignore) is safe; renaming, retyping, tightening or making required
   is breaking. The `event-compat` tool does the classification against the two shapes.
2. **Additive changes go out alone**, with a default and a declared "consumers may
   ignore this" rule. One field per release; a batch of additive fields is a breaking
   change wearing a disguise.
3. **Breaking changes are dual-written**: the producer emits both shapes, old and new,
   for a window with a stated end. Consumers migrate during the window; the window is
   not extended by silence.
4. **Never reuse a field name with a new meaning.** `amount` in cents read by a
   consumer that assumed dollars is worse than a missing field, because it fails
   silently and looks correct.
5. **Record the window and the owners** in the changelog: who consumes the old shape,
   what date the old shape stops, what happens if a consumer has not migrated.
6. **Retire the old shape on the date**, with a final event count per consumer. A
   dual-write without a retirement is two protocols forever.
7. **Run the `event-compat` tool** on producer and consumer schema versions in CI, so
   the classification is enforced rather than remembered.

## Exit Criteria

- [ ] Every change is classified as additive or breaking before implementation.
- [ ] Additive changes ship one per release, with a default and an ignore rule.
- [ ] Breaking changes are dual-written, with a window and a retirement date.
- [ ] No field name was reused with a different meaning.
- [ ] Every consumer of the old shape is named, with an owner.
- [ ] `event-compat` reports the change as compatible, or the window is recorded.

## Common Failures

| Failure | Fix |
|---|---|
| Renaming a field "because it is clearer" | Add the new name, dual-write, retire the old one |
| Adding a required field to a v1 event | Optional with a default; required is a new major |
| Reusing a field name with new units | Add a new field; silent unit changes corrupt data |
| Dual-write with no end date | Set the retirement date when the window opens |
| Assuming consumers read the docs | Check the consumer list; events outlive the conversation |
| Discovering consumers during the incident | Maintain the consumer list as part of the schema |
