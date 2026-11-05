---
name: api-compatibility
description: Check a consumer against a producer across major versions and report exactly what breaks and where. Use when upgrading a dependency, coordinating a producer/consumer release, or verifying that a pinned major still matches.
metadata:
  origin: ECC · api-design
  category: contracts
  phase: review
  status: adopted
  version: 1
---

# API Compatibility

Compatibility is not a feeling about semver: it is a set of pairs — consumer pin
against producer version — each of which either works or does not. This skill makes
the matrix explicit so an upgrade is a decision instead of a hope.

## When to Use

- Upgrading a dependency that other components consume.
- Coordinating a producer release with its consumers.
- Verifying that a pinned major still matches what is deployed.

## When Not to Use

- A single-module repository where producer and consumer ship together.
- Before a producer exists: that is `contract-design`.

## Procedure

1. **Enumerate producers and their available majors.**
2. **Enumerate consumers and the major each pins.**
3. **Build the matrix** and mark each cell compatible or not, with the reason.
4. **Find the unsafe pairs** — a consumer whose pinned major is deprecated or gone.
5. **Decide per consumer**: upgrade now, keep the old major alive, or cut the
   consumer.
6. **Record the sunset date** for every deprecated major; without one, "deprecated"
   means "forever".
7. **Re-run the matrix in CI** when either side changes.

## Exit Criteria

- [ ] Every consumer appears in the matrix with its pinned major.
- [ ] No consumer pins a major that no producer serves.
- [ ] Deprecated majors have a sunset date and an owning consumer list.
- [ ] The migration path per consumer is written, not implied.
- [ ] `compat-matrix` returns zero unsafe pairs.

## Common Failures

| Failure | Fix |
|---|---|
| Upgrading the producer and "hoping" consumers cope | Build the matrix first |
| Deprecating a major with no sunset date | Date it and name the consumers |
| Consumers pinning "latest" | Pin a major; latest is a moving target |
| Treating semver as a guarantee | Check the diff; the number is a claim |
| Matrix built once and never refreshed | Run it in CI on both sides |
