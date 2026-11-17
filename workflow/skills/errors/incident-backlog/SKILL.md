---
name: incident-backlog
description: Turn recurring failures into tracked, deduplicated work items with evidence, severity and an owner. Use when the same failure keeps appearing in journals, or when reports need to become a queue instead of a conversation.
metadata:
  origin: ECC · issue-review
  category: errors
  phase: audit
  status: adopted
  version: 1
---

# Incident Backlog

A failure that repeats is not a bug report, it is a resource allocation problem.
Without deduplication the backlog grows faster than the fixes, and severity becomes
whoever shouted last.

## When to Use

- The same failure appears in several journals or reports.
- Reports arrive from several channels and need one queue.
- Before a planning session, to rank what actually hurts.

## When Not to Use

- A single one-off failure that is already being fixed.
- When the failure rate is unknown: instrument first.
- A single failure already being fixed: `failure-forensics` explains that one.

## Procedure

1. **Normalise each report** to a signature: error code plus the operation plus the
   failing component. Drop ids, timestamps and payloads.
2. **Cluster by signature** before reading anything else.
3. **Rank by frequency × severity**, not by recency.
4. **Attach evidence to the surviving item**: journal run ids, counts, first and
   last seen.
5. **Assign exactly one owner** per item and a next action with a date.
6. **Close duplicates explicitly**, linking them to the canonical item.
7. **Re-run the clustering monthly**: a closed item that keeps appearing means the
   fix did not hold.
8. **Report the queue's own health**: how many items were closed, reopened and merged this cycle. A backlog that only grows is a journal, not a queue.

## Exit Criteria

- [ ] Every report maps to a signature and a cluster.
- [ ] Duplicates linked, not left open.
- [ ] Ranking is frequency × severity, written down.
- [ ] Each open item has one owner and one next action.
- [ ] Recurrence after a fix is flagged, not silently re-opened.

## Common Failures

| Failure | Fix |
|---|---|
| One ticket per report | Cluster by signature first |
| Ranking by who complained last | Frequency × severity |
| Severity set by the reporter | Severity from the taxonomy's policy |
| No owner | Unassigned items are wishes |
| Closing without checking recurrence | Re-run clustering; fixes regress |
| Ranking by recency | Frequency × severity; the newest is rarely the biggest |
