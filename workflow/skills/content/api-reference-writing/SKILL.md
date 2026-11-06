---
name: api-reference-writing
description: Write a reference a caller can act on: every operation, its parameters, what comes back and what fails. Use when an endpoint ships undocumented, when the docs are generated but unreadable, or when support keeps answering "what does this parameter do".
metadata:
  origin: original
  category: content
  phase: document
  status: original
  version: 1
---

# API Reference Writing

A reference is not a tutorial and not a spec: it is the page a caller opens with a
failed request in hand. That reader has one question — what did I send wrong — and
will leave if the answer is not on the operation they just called. This procedure
produces pages that answer it, from the same source as the code, with an example
that actually runs.

## When to Use

- An operation ships with no reference, or with a generated page nobody reads.
- The reference and the code disagree (a parameter that "works anyway").
- Support answers the same question about the same field repeatedly.
- A breaking change is being made and the reference must show the new shape.

## When Not to Use

- Teaching a first integration: that is a tutorial, and its order is by task.
- Writing the *contract* (schema, versioning, compatibility): `api-design` and
  `contract-design` own that; the reference describes it.
- Internal functions: their docstrings are the reference.

## Procedure

1. **One page per operation**, titled with the verb and the resource, not with the
   internal method name. The caller searches for what it does, not for its symbol.
2. **State the shape before the prose**: method, path, auth requirement, and
   whether it is idempotent. Those four lines answer most of the incoming tickets.
3. **Every parameter gets a table row** with type, whether it is required, its
   default and — the row people skip — what happens if it is omitted or wrong.
4. **One request example and one response example, both real.** Copy-pasteable
   values; no placeholders like `<YOUR_ID>`. If the example cannot run, the page is
   a decoration.
5. **Every error the endpoint can return**, with code, meaning and whether retrying
   helps. The error table is the half of the reference that gets used at 2 a.m.
6. **Run the `doc-completeness` tool** over the page's declared sections. It scores
   what is missing per operation and refuses to average a missing error table.
7. **Generate what can be generated** (fields, types) from the schema, and write by
   hand what cannot be: the intent of a parameter and the recovery from an error.

## Exit Criteria

- [ ] Every operation has its own page with method, path, auth and idempotency.
- [ ] Every parameter has type, required, default and wrong-value behaviour.
- [ ] Every operation has one runnable request and one response example.
- [ ] Every error code is listed with meaning and retry guidance.
- [ ] `doc-completeness` reports no operation below the bar.
- [ ] The examples were executed against a real instance at least once.

## Common Failures

| Failure | Fix |
|---|---|
| Placeholder examples (`<token>`, `example.com`) | Real values from a test instance; placeholders are never run |
| Missing error table | Most support tickets live there; list every code |
| "See the schema" | The reference states the shape; the schema is the machine copy |
| Generated page with no prose | Generate fields, write intent and recovery by hand |
| Documenting the implementation | Document the promise; callers cannot see internals |
| One page for a whole resource | One page per operation; the caller arrives with one call |
