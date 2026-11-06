---
name: incident-comms
description: Say what is broken, for whom, and when the next update comes: the first notice, the cadence and the closing message. Use when an incident is user-visible, when support is being asked the same question, or when the silence is becoming the story.
metadata:
  origin: original
  category: content
  phase: ship
  status: original
  version: 1
---

# Incident Communications

During an incident, silence is interpreted as incompetence and speculation is
interpreted as fact. The only defence is a short, frequent, honest message: what is
affected, who is affected, what is being done, when the next update will be. Note
that the last one is a promise, and its value is that it is kept.

## When to Use

- An incident is user-visible, or support is receiving reports.
- A status page, a customer email or an internal channel is waiting for a first notice.
- The team is silent because "we do not know yet" — that is when a notice matters most.
- An incident is closing and nobody has said it is over.

## When Not to Use

- An internal-only blip that no user can observe: fix it, then record it.
- Writing the technical postmortem: that comes later and is a different document.
- Explaining a decision that has not been made yet — say that it has not been made.
- The technical postmortem, which explains causes rather than informing users: `failure-forensics`.

## Procedure

1. **Publish the first notice within the stated window**, even with little known.
   The minimum is: what users see, what is affected, that it is being worked on, and
   when the next update comes. "We do not know yet" is a valid sentence; silence is not.
2. **Separate confirmed from unknown** in every message. Mark speculation as
   speculation; a wrong detail repeated by support becomes a wrong fact.
3. **Never estimate the fix time you do not have.** Give the next update time
   instead; a missed ETA is read as a missed promise, a kept cadence reads as control.
4. **Keep one voice and one channel.** Two sources of truth produce three versions;
   the channel of record is named in the first notice.
5. **Write for the reader's question**: "can I use it", "is my data safe", "do I need
   to do anything". Answer those three before the engineering detail.
6. **Close explicitly**: what was affected, for how long, what has changed, and what
   users may still notice. An incident without a closing message never ends for the
   people it touched.
7. **Run the `comms-check` tool** on the message set: it flags a missing cadence, an
   ETA, speculation stated as fact and a missing closing message.

## Exit Criteria

- [ ] A first notice exists with impact, affected users, status and next-update time.
- [ ] The cadence was kept, or the missed update was acknowledged in the next one.
- [ ] No message states an unverified cause as fact.
- [ ] No message promises a fix time that was not known.
- [ ] A closing message states duration, resolution and residual effects.
- [ ] `comms-check` reports no missing cadence, ETA or closing message.

## Common Failures

| Failure | Fix |
|---|---|
| Silence until the cause is known | Publish impact first; cause comes when confirmed |
| "Should be fixed in 20 minutes" | Promise the next update, not the fix |
| Cause stated as fact, then retracted | Mark unverified claims as unverified |
| Three channels, three versions | One channel of record, named in the first notice |
| No closing message | Close with duration, resolution and what may still be off |
| Blame in the message | Describe impact and action; causes belong in the postmortem |
