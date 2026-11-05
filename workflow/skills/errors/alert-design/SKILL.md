---
name: alert-design
description: Design alerts a tired person can act on: a symptom, a threshold with a reason, and a runbook line. Use when adding monitoring, when an alert is being silenced or ignored, when an incident was found before any alert fired, or when paging volume is growing faster than incidents.
metadata:
  origin: original
  category: errors
  phase: implement
  status: original
  version: 1
---

# Alert Design

An alert is a request for a human to stop what they are doing. That is the most
expensive resource in an on-call rotation, so every alert spends it: it must name a
symptom a user can feel, explain why the threshold is what it is, and say what to do
first. Everything else is a dashboard, and dashboards do not wake people up.

## When to Use

- Adding monitoring for a new feature or service.
- An alert is routinely silenced, or its channel is muted.
- An incident was found by a customer before any alert fired.
- Paging volume is growing while the number of real incidents is not.

## When Not to Use

- Choosing an observability vendor: that is procurement.
- Debugging one incident now: use `failure-forensics`.
- Metrics nobody should be woken for — those belong on a dashboard, deliberately.

## Procedure

1. **Start from the symptom a user feels**, not from a cause: "checkout fails",
   "logins are slow", "the export never arrives". A CPU alert is a cause graph
   detail; it earns an alert only when it has been shown to precede a symptom.
2. **State the threshold and why it is that number.** "5xx above 2% for 5 minutes"
   needs the reason it is 2% and not 5%: the error budget, the historical baseline,
   the point where support starts getting calls. A number without a reason is a
   number someone will change arbitrarily.
3. **Write the first line of the runbook** into the alert itself: the one command
   or the one page a responder should open. If it cannot fit in one line, the
   alert is not ready; the responder will be reading a wiki during an outage.
4. **Decide who is woken**, and at what hour. A business-hours alert in a
   pager rotation is a defect; so is paging a team that cannot fix the cause.
5. **Set the auto-resolution.** An alert that does not close itself when the
   symptom stops teaches responders to ignore stale pages.
6. **Run the `alert-audit` tool** on the alert list: it flags cause-only alerts,
   missing thresholds, missing runbook lines and alert-to-incident ratio.
7. **Prune on a schedule.** Every quarter, delete the alerts that never fired and
   the ones that always fire. An alert inventory that only grows is a noise
   generator with a retention policy.

## Exit Criteria

- [ ] Every alert names a user-visible symptom, not only a cause.
- [ ] Every threshold has a written reason and a duration.
- [ ] Every alert carries a one-line first action for the responder.
- [ ] `alert-audit` reports no missing symptom, threshold or runbook line.
- [ ] The alert closes itself when the symptom clears.
- [ ] Silenced or never-firing alerts have a deletion date.

## Common Failures

| Failure | Fix |
|---|---|
| Alerts on causes (CPU, queue depth) with no symptom | Page on the symptom; keep the cause as context |
| Threshold copied from a blog | Derive it from the error budget or the support baseline |
| Runbook is a wiki link | Put the first line in the alert; the wiki does not load during an outage |
| Alert storms: 300 pages for one cause | Group by symptom and page once per incident |
| Silenced "for now" | A silence with no expiry date and owner is a deleted alert in disguise |
| More alerts as the fix for a miss | Add the alert that would have caught the symptom, not five that might |
