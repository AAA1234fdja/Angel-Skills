---
name: query-review
description: Review queries with their access plan: N+1, missing indexes and unbounded scans. Use when a listing is slow, a query looks harmless, or a new endpoint touches a large table.
metadata:
  origin: ECC · skills/postgres-patterns
  category: data
  phase: review
  status: adopted
  version: 1
---

# Query Review

A query is not reviewed by reading it; it is reviewed with the plan it produces and
the cardinality it touches. Two identical-looking queries can differ by three
orders of magnitude.

## When to Use

- A listing, report or dashboard is slow.
- A new endpoint touches a large table.
- A query was written by an ORM and nobody has seen the SQL.

## When Not to Use

- Queries on tables with tens of rows: the plan cannot matter yet.
- Analytical workloads where a full scan is the correct plan.

## Procedure

1. **Get the SQL actually executed** (the ORM logs it), not the code that builds it.
2. **Get the plan** (`EXPLAIN ANALYZE`, `explain()` in Mongo) and look at the widest
   node: sequential scan, nested loop with a large outer set, sorts spilling to disk.
3. **Check the filter columns against the indexes**, including order and
   selectivity: a leading low-selectivity column wastes the index.
4. **Look for N+1**: one query per row of a previous result, usually from lazy
   loading in a loop.
5. **Check the shape**: `SELECT *` pulls columns nobody uses; a missing `LIMIT`
   makes an endpoint unbounded.
6. **Check pagination**: offset pagination degrades with depth; keyset does not.
7. **Propose the smallest change**: an index, a join instead of a loop, a projection.

## Exit Criteria

- [ ] The executed SQL is captured, not inferred.
- [ ] The plan was read and the widest node identified.
- [ ] Filter columns are backed by an index (or the absence is justified).
- [ ] No N+1 in the access pattern.
- [ ] Projections and limits are explicit.
- [ ] `query-smells` reports no blocking smell.

## Common Failures

| Failure | Fix |
|---|---|
| Reading the ORM code, not the SQL | Log the statement |
| Adding an index by intuition | Read the plan first |
| Index exists but unused (function on the column) | Compare the raw column |
| Offset pagination at depth | Keyset pagination |
| `SELECT *` in a wide table | Project the used columns |
| N+1 hidden behind lazy loading | Eager load or batch |
