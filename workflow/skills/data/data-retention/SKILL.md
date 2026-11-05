---
name: data-retention
description: Decide what is kept, for how long and what deletes it: purpose, retention window, legal hold and the deletion path. Use when a new dataset is added, when someone asks to be forgotten, when an audit asks why a record still exists, or when a backup outlives the policy it was written under.
metadata:
  origin: original
  category: data
  phase: design
  status: original
  version: 1
---

# Data Retention

Data does not expire by itself. Every field you keep is a liability with a
maintenance cost, a leak surface and a legal meaning; every field you delete is a
decision someone has to sign. The purpose of this procedure is to make retention a
decision per dataset instead of an accident of what the database accepted.

## When to Use

- A new dataset, table, event stream or log line holds personal or regulated data.
- A deletion request arrives and nobody knows which copies exist.
- An audit or a questionnaire asks for the retention period.
- A backup, replica or warehouse outlives the policy it was created under.

## When Not to Use

- Choosing the storage engine: that is a data modelling decision.
- Fields with no personal or regulated content and no cost to keep.
- Retroactively justifying what already exists — that is an audit, and it should
  produce the same table, honestly dated.

## Procedure

1. **State the purpose** of each dataset in one sentence. Data without a purpose
   cannot have a retention period, only a habit.
2. **Classify the content** with the `retention-audit` tool: personal, sensitive,
   financial, health, operational. Classification decides the default window.
3. **Set the window and the trigger**: "90 days after the last support ticket
   closes" is a rule; "90 days" alone is not, because nobody knows when it starts.
4. **Name every copy**: primary, read replica, backup, warehouse, cache, logs,
   analytics export, and the vendor's copy. A deletion that misses a copy is not a
   deletion. This list is the part that audits actually find.
5. **Write the deletion path** — the job, the query, the schedule, who can run it
   by hand — and prove it once end to end on a non-production copy.
6. **Handle the exceptions explicitly**: legal hold, fraud prevention, dispute
   window, statutory minimum. An exception without an owner and an expiry is
   retention by inertia.
7. **Re-run the audit** when a new copy is added. Backups are where retention
   policies go to die.

## Exit Criteria

- [ ] Every dataset has a stated purpose and a classification.
- [ ] Every dataset has a window, a trigger and a named owner.
- [ ] The copy inventory lists primary, backup, warehouse, cache and vendor copies.
- [ ] The deletion job exists, ran end to end once, and is scheduled.
- [ ] `retention-audit` reports no dataset without a purpose, a window or a copy list.
- [ ] Every exception has an owner and an expiry date.

## Common Failures

| Failure | Fix |
|---|---|
| "We delete it after 90 days" with no trigger | Say what starts the clock |
| Backups forgotten | Put them in the copy inventory; the policy applies there too |
| Deletion without a verification query | Count before, count after, store the result |
| Legal hold used as a permanent excuse | Owner plus expiry, reviewed |
| Purpose described as "analytics" | Name the decision the data supports |
| Deleting from the primary only | Delete from the replicas and the warehouse in the same run |
