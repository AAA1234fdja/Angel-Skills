---
name: ux-flow-review
description: Walk a user flow end to end and report where it stalls: steps, decision points, dead ends and recoverability. Use when a flow is about to ship, when support keeps explaining the same screen, when a funnel leaks at one step, or before asking for a redesign.
metadata:
  origin: original
  category: product
  phase: review
  status: original
  version: 1
---

# UX Flow Review

A flow is not a set of screens; it is a promise that someone can get from intent to
outcome. Reviewing it means walking it as a user with a specific job, counting the
steps that are the user's problem rather than the system's, and finding the places
where a mistake is unrecoverable. `accessibility-audit` checks whether a person
*can* operate the interface; this checks whether the path *exists*.

## When to Use

- A flow is about to ship or has just shipped and the funnel leaks at one step.
- Support keeps answering the same question about the same screen.
- A "small" change to one step affects three others downstream.
- Before a redesign is proposed: measure the flow before replacing it.

## When Not to Use

- Contrast, focus order, labels: that is `accessibility-audit`.
- Deciding whether the feature should exist (product policy, not a flow review).
- A single static screen with no sequence.

## Procedure

1. **Name the job, not the feature**: "renew a card that expired" beats "billing".
   One job per review; two jobs in one walk produce an average of nothing.
2. **Count the steps** from intent to outcome and classify each: `input` (the user
   must supply something), `decision` (the user must choose), `wait` (the system
   works) and `error` (a recovery path). Waits and decisions are where flows die.
3. **Mark dead ends**: an error with no way forward, a state that requires support,
   a back button that loses data. A dead end is a defect, not a nitpick.
4. **Check recoverability**: for each input, what happens after a typo? For each
   step, can the user go back without losing work? A flow that punishes a mistake
   with a restart teaches people to abandon.
5. **Run the `flow-audit` tool** on the step list. It reports step count, how much
   of the work is the user's, the dead ends and whether any step is unrecoverable.
6. **Report the three costliest steps**, with the evidence (step number and the
   observed behaviour), and one proposed change each. A review that lists twenty
   findings changes nothing.
7. **Re-walk after the change**, same job, same count. A flow review without a
   before/after count is an opinion.

## Exit Criteria

- [ ] The job is stated in one sentence and only one job was walked.
- [ ] Every step is classified and counted; the tool reports the total.
- [ ] Every dead end is either fixed or logged with an owner.
- [ ] No step is unrecoverable without a stated reason.
- [ ] The three costliest steps have a proposed change each.
- [ ] The before/after step count is recorded.

## Common Failures

| Failure | Fix |
|---|---|
| Reviewing screens instead of the job | Walk from intent to outcome; screens are incidental |
| Counting clicks as if all steps cost the same | A decision or a wait costs more than a click |
| Ignoring the empty and error states | Those are the states users are in when they give up |
| "Users will figure it out" | If it needs support, it is a flow defect |
| Twenty findings, no priority | Three costliest steps, each with one change |
| No re-walk | The count after the change is the only evidence it helped |
