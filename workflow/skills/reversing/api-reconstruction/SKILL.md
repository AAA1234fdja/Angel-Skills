---
name: api-reconstruction
description: Rebuild an undocumented HTTP API from captured traffic into an openapi-style spec and a validated client. Use when integrating with a service that has no documentation and traffic captures exist.
metadata:
  origin: ECC · api-connector-builder
  category: reversing
  phase: implement
  status: adopted
  version: 1
---

# API Reconstruction

Captured traffic is the most honest documentation an undocumented API has. The work
is turning samples into a spec — and a spec into something validated on the next
request instead of discovered again.

## When to Use

- A service has no documentation and traffic captures exist.
- A client library has to be reimplemented.
- A reverse-engineered integration must become maintainable.

## When Not to Use

- Documentation exists but is partial: read it first, fill the gaps.
- The capture was taken without authorisation: check first.

## Procedure

1. **Collect samples per endpoint**, at least three per shape, including one error
   response and one empty result.
2. **Normalise paths**: replace ids with placeholders (`/users/123` →
   `/users/{id}`) and count how many shapes each placeholder takes.
3. **Infer the schema per field across samples**: type, nullability, enum when the
   value set is small and stable.
4. **Capture the auth mechanism** from headers, and what changes when it is missing
   or expired.
5. **Record the error envelope**: status codes, body shape, retry-after behaviour.
6. **Write the spec** in openapi style and generate a client that validates
   responses against it.
7. **Validate against held-out samples** — traffic not used to build the spec. If it
   fails, the spec is incomplete, and that is the finding.

## Exit Criteria

- [ ] At least three samples per endpoint shape, including error and empty.
- [ ] Paths normalised with placeholder cardinality recorded.
- [ ] Field types and nullability inferred from samples, not guessed.
- [ ] Auth and error behaviour documented.
- [ ] Spec validated against held-out traffic.
- [ ] Unknowns (rare paths, undocumented headers) listed.

## Common Failures

| Failure | Fix |
|---|---|
| One sample per endpoint | Three minimum, including errors |
| Field types guessed | Infer across samples; record contradictions |
| Ignoring error responses | They carry the retry semantics |
| No held-out validation | A spec that only fits the training samples |
| Hardcoding an id from a capture | Normalise paths first |
| Missing the auth refresh path | It is the first thing that breaks |
