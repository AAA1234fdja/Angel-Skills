---
name: contract-validation
description: Validate payloads against their contract before they are used, reporting the first violation with its path. Use when a producer or consumer needs to guarantee that what crosses the boundary matches the declared schema.
metadata:
  origin: ECC · contract-first
  category: contracts
  phase: verify
  status: adopted
  version: 1
---

# Contract Validation

Validating after something breaks is debugging. Validating before use is a
contract. The difference is whether the failure names the boundary and the path, or
whether it surfaces three layers down as `undefined is not a function`.

## When to Use

- A producer is about to hand structured data to another component.
- A consumer receives data from outside the process (queue, HTTP, file).
- A contract changed and consumers must be checked.

## When Not to Use

- Inside a single function's local data, where the type system already holds.
- For data you just constructed in the same statement.

## Procedure

1. **Resolve the contract by name and version**, never by "latest" in production.
2. **Validate before use** and fail the operation on the first violation —
   deterministic order, no accumulated errors that nobody reads.
3. **Report the path and the violated keyword**, not just "invalid".
4. **Never repair silently.** If a payload can be coerced, that coercion is a
   migration, not a validation.
5. **Treat unknown fields as errors** unless the contract explicitly allows them:
   unknown fields hide producer bugs.
6. **Log the contract version with the payload** so a later failure can be traced.
7. **Test both sides**: one test with a valid payload and one per rejected case.

## Exit Criteria

- [ ] Validation happens at the boundary, before any use of the data.
- [ ] Failure names the contract, version, path and keyword.
- [ ] Unknown fields are rejected (or explicitly allowed by the schema).
- [ ] No silent coercion or defaulting in the validation path.
- [ ] Tests cover one valid payload and each rejection class.

## Common Failures

| Failure | Fix |
|---|---|
| Validating after using the data | Validate first, always |
| Catching the validation error and continuing | That is a swallowed failure (`error-handling`) |
| "Latest" contract in production | Pin the major version |
| Allowing any extra field | Unknown fields hide producer regressions |
| Repairing the payload in the validator | Coercion belongs to an explicit migration |
