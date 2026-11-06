---
name: oncall-handoff
description: Hand over an on-call rotation so the next person starts informed: open incidents, recent changes, known noise and what is one step from breaking. Use when a rotation changes, before a holiday, or when the new responder has to read history to find out what is on fire.
metadata:
  origin: original
  category: governance
  phase: ship
  status: original
  version: 1
---

# On-call Handoff

An on-call rotation changes hands with the state of the system in one person's head.
The handoff is the only moment that state is transferred, and if it is skipped the
next responder learns it from the pager — at the worst possible time, with no
context. Fifteen minutes of writing replaces an hour of an incident.

## When to Use

- A rotation changes hands, planned or not.
- Before a holiday or an absence where the backup becomes primary.
- After a week with unusual changes: deploys, migrations, feature flags.
- When a new responder has to read history to know what is currently fragile.

## When Not to Use

- Same person, same shift: there is nothing to transfer.
- A full postmortem of the week: that is a different document.
- The handoff of a project, not a system: that is a plan, not a rotation.

## Procedure

1. **Open incidents first**, each with state (mitigated, watching, unresolved), the
   owner and the next action. A handoff that buries an open incident at the bottom is
   worse than none.
2. **What changed since the last handoff**: deploys, migrations, flags turned on,
   configuration changed by hand. Each with the rollback path if it goes wrong.
3. **Known noise**, explicitly: the alerts that fire and close themselves, with the
   reason they are tolerated. This is the single most useful section for a new
   responder, because it is the one nobody can infer from a dashboard.
4. **One step from breaking**: the component that survived the week by luck, and the
   signal that would show it failing.
5. **What is scheduled while you are away**: jobs, expirations, certificate renewals,
   vendor cutovers. A missed renewal is a self-inflicted incident.
6. **Who to call and for what**, including the person who knows the thing nobody
   documents.
7. **Run the `handoff-check` tool** on the note: it flags missing open incidents,
   missing changes, missing noise list and missing contacts.
8. **Read it back to the next person**, live or async, and let them ask. A handoff
   nobody read is a document, not a transfer.

## Exit Criteria

- [ ] Every open incident is listed with state, owner and next action.
- [ ] Every change since the last handoff is listed with its rollback.
- [ ] Known noise is written down with the reason it is tolerated.
- [ ] The fragile component and its early signal are named.
- [ ] Scheduled events during the absent window are listed with dates.
- [ ] Contacts are listed by area, including the undocumented expert.
- [ ] `handoff-check` reports no missing section, and the next person read it.

## Common Failures

| Failure | Fix |
|---|---|
| Open incident mentioned in passing | Put it first, with state, owner and next action |
| "Nothing much changed" | List deploys and flags; the responder cannot infer them |
| Noise list omitted | Explicitly tolerated alerts are the top source of wasted pages |
| No contacts | Name people by area, including the one who knows the legacy job |
| Handoff written, never read | Read it back together; questions are the point |
| Scheduled jobs forgotten | List renewals and expirations with dates |
