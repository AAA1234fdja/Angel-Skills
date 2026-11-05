---
name: contract-design
description: Design a contract from the consumers' needs: minimal fields, explicit required set, versioned from day one. Use when two components need to exchange structured data and no schema exists yet.
metadata:
  origin: ECC · api-design + contract-first
  category: contracts
  phase: plan
  status: adopted
  version: 1
---

# Contract Design

A contract is a promise with a machine-checkable shape. Designing one backwards —
from what a consumer must decide — produces fewer fields and fewer breakages than
designing from what a producer happens to have.

## When to Use

- Two components exchange structured data and no schema exists.
- A field is about to be added "quickly" to an existing payload.
- An API is being extracted from an internal function.

## When Not to Use

- Data that never crosses a boundary (a local variable, a private helper).
- A single consumer that owns the producer: the contract is the code.

## Procedure

1. **List the consumers** and, for each, the decision it makes with the payload.
2. **Derive fields from decisions**, not from the producer's model. A field no
   consumer reads is not part of the contract.
3. **Mark the required set explicitly.** Required means "the consumer cannot act
   without it", not "the producer always sends it".
4. **Choose types narrow enough to validate**: enums over free strings, explicit
   nullability, units in the name (`duration_ms`).
5. **Version from day one** (`1.0.0`) and record who consumes it.
6. **Write the failure behaviour into the contract**: what a consumer does with a
   missing optional field.
7. **Generate a skeleton** with `contract-skeleton` and commit it under
   `workflow/contracts/<name>/`.

## Exit Criteria

- [ ] Every field maps to a consumer decision (or it was removed).
- [ ] Required set is explicit and justified per field.
- [ ] Version is `1.0.0` and consumers are listed.
- [ ] Enums and nullability are explicit; units are in field names.
- [ ] The schema validates a real sample: `workflow contract --validate`.

## Common Failures

| Failure | Fix |
|---|---|
| Designing from the producer's internal model | Start from consumer decisions |
| Everything required "to be safe" | Required blocks evolution; require only what is needed |
| Free strings where an enum exists | Enums make evolution detectable |
| No version on v1 | Retro-fitting versions is a breaking change |
| Contract describes transport (headers, retries) | Contract shapes the payload only |
