---
name: premortem
description: Assume the project already failed, then write down why: the failure modes, the earliest signal of each and the one cheap action that would have prevented it. Use when a plan is about to be committed to, when a team is unusually confident, or when a launch has no stated way to fail.
metadata:
  origin: original
  category: governance
  phase: plan
  status: original
  version: 1
---

# Premortem

A postmortem explains a failure that already happened. A premortem assumes the
failure has happened and asks the team to write the story backwards. The point is
not pessimism: it is that a group asked "what could go wrong" gives polite answers,
while a group told "it went wrong, why" gives specific ones.

## When to Use

- A plan is about to be committed to, with budget and a date.
- The team is unanimous and unusually confident — the strongest signal for a premortem.
- A launch, migration or integration has no stated way to fail.
- A previous project failed and its causes were never named.

## When Not to Use

- Choosing between options: that is a decision record (`adr-writing`).
- A one-week reversible experiment: the premortem costs more than the risk.
- Assigning blame for a completed failure: that is a postmortem, and a different one.

## Procedure

1. **Open with the fact**: "it is six months from now and this failed". The past
   tense is what unlocks specifics; the future tense produces hedging.
2. **Write failure modes individually first** (five minutes, no discussion), so the
   loudest person does not set the frame.
3. **Consolidate into five to seven modes**, each in one sentence with the mechanism,
   not the category: "the vendor's rate limit forced a queue we never built" beats
   "scalability".
4. **For each mode, name the earliest observable signal** — the thing that would be
   visible weeks before the failure. A failure mode without a signal cannot be
   monitored and will be discovered late.
5. **Score likelihood and impact** high/medium/low, then sort. Only the top three
   get action; a premortem with twelve mitigations produces none.
6. **Decide one cheap prevention per top mode**: a spike, a limit, a flag, a
   conversation, a threshold. Cheap is the criterion; expensive prevention gets
   postponed and then forgotten.
7. **Run the `premortem-scan` tool** on the modes: it flags vague modes, missing
   signals and mitigations that cost more than the risk they remove.
8. **Re-read it at the midpoint.** A premortem nobody reopens is a ritual.

## Exit Criteria

- [ ] Five to seven failure modes, each with a mechanism in the sentence.
- [ ] Every mode has an earliest observable signal.
- [ ] Every mode is scored for likelihood and impact, and sorted.
- [ ] The top three have one cheap prevention each, with an owner.
- [ ] `premortem-scan` reports no mode without a signal.
- [ ] A date is set to re-read it.

## Common Failures

| Failure | Fix |
|---|---|
| "What could go wrong?" | Use the past tense: the specifics live there |
| Categories instead of mechanisms | Say how it fails, not which bucket it is in |
| Twelve mitigations | Three, each cheap, each with an owner |
| No signals | Without a signal the mode is undetectable until it is too late |
| Written by one person | Individually first, then consolidate |
| Never reopened | Put the re-read date in the plan, not in someone's memory |
