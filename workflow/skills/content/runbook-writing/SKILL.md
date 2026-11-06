---
name: runbook-writing
description: Write a runbook someone can follow at 3 a.m. under stress: symptom, first command, decision points and how to know it is over. Use when an alert has no answer, when an incident needed a person who was on holiday, or when the same fix is rediscovered every time.
metadata:
  origin: original
  category: content
  phase: document
  status: original
  version: 1
---

# Runbook Writing

A runbook is read by someone tired, mid-incident, who did not write it. That reader
cannot evaluate options or reason about architecture; they can follow steps and check
things. So the document is written in the imperative, starts from the symptom they
were paged for, and says when to stop and escalate — the part that separates a
runbook from a wiki page.

## When to Use

- An alert exists with no documented first action.
- An incident was resolved by someone reconstructing the fix from memory.
- The same intervention is rediscovered quarterly.
- A procedure has a risky step that must be executed the same way every time.

## When Not to Use

- Explaining how a system works: that is architecture documentation.
- A one-off operation with no recurrence (write the ticket instead).
- Deciding what to alert on: `alert-design` owns that; the runbook follows it.

## Procedure

1. **Title it with the symptom the responder sees**, not with the cause. The reader
   arrives from a page; they search for what is on fire.
2. **First line is the first action**: the command or the dashboard. If they have to
   read a paragraph to begin, the runbook starts too late.
3. **Steps in the imperative, one action each**, with the expected output inline.
   "You should see `status: healthy`" tells them they are on track; without it, they
   guess and improvise.
4. **Decision points get an explicit branch**: if X, do A; if Y, do B; if neither,
   escalate to the named owner with the named evidence. An unbranched runbook is a
   script, and scripts break.
5. **State how it is over**: the metric or command that proves recovery, plus the
   observation window before standing down.
6. **Write the rollback and the dangerous step in bold**, with what makes it
   dangerous. The one step that can make things worse must look different.
7. **Run the `runbook-check` tool** on the step list: it flags missing first action,
   destructive steps without a confirmation, missing escalation and missing
   recovery criterion.
8. **Rehearse it once** on a non-production instance or a tabletop, by someone who
   did not write it. A runbook that has never been executed is a draft.

## Exit Criteria

- [ ] The title is the symptom, and the first line is an action.
- [ ] Every step has one action and an expected observation.
- [ ] Every decision point has branches and an escalation with a named owner.
- [ ] The dangerous step is marked and has a confirmation.
- [ ] The recovery criterion and observation window are stated.
- [ ] `runbook-check` reports no missing action, escalation or recovery criterion.
- [ ] Someone who did not write it followed it end to end.

## Common Failures

| Failure | Fix |
|---|---|
| Title is the cause ("replica lag") | Title the symptom the responder was paged for |
| Paragraphs of context before the first command | First line is the action; context goes after |
| "Investigate the logs" | Say which command, which filter, what to look for |
| No escalation path | Name a person and the evidence to bring |
| No end condition | Metric plus window, or the incident never closes |
| Never rehearsed | Rehearse by someone else; fix what they stumbled on |
