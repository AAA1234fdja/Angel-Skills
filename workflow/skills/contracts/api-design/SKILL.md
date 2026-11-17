---
name: api-design
description: Specify the shape of a call before anyone implements it: operations, errors, idempotency and what the consumer may ignore. Use when an endpoint, SDK method or shared schema is being added, when a client broke because the surface was never written down, or when two teams disagree about what a "simple" call returns.
metadata:
  origin: original
  category: contracts
  phase: design
  status: original
  version: 1
---

# API Design

An API is a promise made to someone who cannot see the code. Most breakage is not
a bug: it is a surface that was never specified, so every consumer guessed a
different contract. This procedure writes the surface down — operations, errors,
idempotency, and what a consumer is allowed to ignore — before it exists.

## When to Use

- A new endpoint, SDK method, event or shared schema is being added.
- Two teams describe the same call differently.
- A consumer broke on a change nobody thought was breaking.
- A field is being added and it is unclear whether it is required.

## When Not to Use

- An internal function with exactly one caller in the same module: the signature
  is the contract and the compiler checks it.
- Prototypes that will be deleted (see `prototype-spike`).
- Negotiating *product* behaviour: this skill shapes the interface, not the policy.

## Procedure

1. **Name the resource and the operations.** Nouns are stable; verbs are
   operations on them. If an operation needs three nouns, it is probably two
   operations or the wrong boundary.
2. **Write the request and response as examples first**, with real values. A
   schema written before an example tends to describe the implementation.
3. **Decide idempotency per operation**, explicitly: which operations are safe to
   repeat, which carry a client-generated key, which are fire-and-forget. An API
   whose retry semantics are unknown forces every consumer to invent its own.
4. **Enumerate the errors** with a stable code, an owner and whether retrying can
   help. "500 something went wrong" is not an error contract; it is an absence.
5. **State what a consumer may ignore.** Unknown fields, extra headers, ordering:
   saying "additional fields may appear" once is what lets you add fields without
   a version bump.
6. **Run the `surface-audit` tool** on the operation list. It flags missing
   idempotency, undocumented errors, operations that both read and write, and
   required fields added without a compatibility note.
7. **Freeze the v1 surface** in the changelog with the version and the date, so
   later changes are measured against a written promise.

## Exit Criteria

- [ ] Every operation has a request example, a response example and an error list.
- [ ] Every operation states its idempotency and its retry semantics.
- [ ] The "may ignore" rule is written (unknown fields, ordering, extension points).
- [ ] `surface-audit` reports no missing idempotency and no undocumented error.
- [ ] The surface is recorded with a version and a date before implementation.

## Common Failures

| Failure | Fix |
|---|---|
| Schema designed before any example | Write the JSON a caller sends and gets, then derive |
| Retry semantics left to the client | Declare idempotency per operation |
| Errors as free text | Stable code, owner and retryability |
| Requiring a new field in a minor version | Optional with a default, or a new major |
| One operation that reads and writes | Split; the consumer's caching and retries depend on it |
| "We'll document it later" | The implementation becomes the spec, and it is unreadable |
