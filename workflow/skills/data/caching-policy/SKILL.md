---
name: caching-policy
description: Decide what to cache, for how long and how to invalidate, before adding a cache. Use when a cache is proposed as a performance fix, or when stale data starts producing bugs nobody can reproduce.
metadata:
  origin: ECC · redis-patterns + content-hash-cache-pattern
  category: data
  phase: design
  status: adopted
  version: 1
---

# Caching Policy

A cache is a correctness decision disguised as a performance one. Adding it without
writing the invalidation rule is how "we fixed the speed" becomes "we cannot
reproduce the bug".

## When to Use

- A cache is proposed as a fix for slowness.
- Stale or inconsistent data is appearing intermittently.
- A new read-heavy endpoint is about to be built.

## When Not to Use

- Before profiling: if you do not know the bottleneck, the cache may be irrelevant.
- Data that must be strongly consistent for a transaction to be correct.
- Finding the bottleneck in the first place: `performance-optimizer` profiles before anything is cached.

## Procedure

1. **State the reader's tolerance for staleness**: seconds, minutes, or never. If
   "never", do not cache.
2. **Choose the key from the data identity**, not from the function name; include
   every parameter that changes the result.
3. **Choose the TTL from the tolerance**, and make it shorter than the worst
   tolerable staleness — never longer.
4. **Write the invalidation path** before the cache code: who deletes the key, on
   which event, and what happens if that event is missed.
5. **Decide the failure mode**: if the cache is unavailable, do you serve stale, or
   fail? Write it down.
6. **Bound the size** and the eviction policy; an unbounded cache is a memory leak
   with good intentions.
7. **Instrument hit rate and age**; a cache nobody measures is a guess forever.

## Exit Criteria

- [ ] Staleness tolerance stated in time.
- [ ] Key includes every parameter that affects the result.
- [ ] TTL is not longer than the tolerance.
- [ ] Invalidation path written with its failure mode.
- [ ] Behaviour on cache outage decided.
- [ ] Hit rate and age are measured.

## Common Failures

| Failure | Fix |
|---|---|
| Cache added before profiling | Profile first |
| TTL longer than the tolerance | TTL follows the business rule |
| Key without all parameters | Ghost results across users |
| No invalidation | Stale data with no reproduction path |
| Unbounded cache | Bound it and evict |
| No metrics | You cannot tell if it helps |
