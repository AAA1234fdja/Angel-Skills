---
name: intent-driven-development
description: Turn an ambiguous or high-impact request into scoped, verifiable acceptance criteria before writing code. Use when a request is a sentence long but the change is a week long, when two people read the request differently, or when "done" is being negotiated at review time.
metadata:
  origin: adapted · ECC · skills/intent-driven-development
  category: product
  phase: design
  status: adopted
  version: 1
---

# Intent-Driven Development

A request arrives as a sentence and leaves as a diff, and the gap between the two is
where most rework is born. The procedure closes the gap before the code exists: the
intent is written as observable criteria, the non-goals are written down with the same
care, and every criterion names how it will be checked. The test of a good intent is
brutal — could two people independently implement it and produce the same behaviour?

## When to Use

- A one-sentence request implies a week of work.
- Two stakeholders read the same request differently.
- "Done" is being negotiated during review instead of before implementation.
- The change is irreversible, expensive, or touches money, identity or data.

## When Not to Use

- A typo, a rename, a dependency bump: the request *is* the criterion.
- Choosing between designs: that is `adr-writing` once options exist.
- Deciding whether a release may ship: that is `release-readiness`.

## Procedure

1. **Write the intent in one sentence as an outcome for a user**, not as a change to
   the system. "Users can resume an abandoned checkout" is intent; "add a resume
   endpoint" is an implementation guess.
2. **Extract the observable behaviours** and phrase each as a criterion someone could
   test without reading the code: given / when / then, or a number with a unit.
3. **Name the non-goals explicitly.** The cheapest scope control is the sentence
   "this does not include…", written before anybody builds it.
4. **State the ambiguity you resolved and who resolved it.** An unrecorded
   interpretation resurfaces at review as a disagreement.
5. **Attach the check to each criterion**: a test, a query, a tool, a manual step with
   an owner. A criterion with no check is a wish with a checkbox.
6. **Fix the verification boundary**: what must be true before this is done, and what
   is explicitly deferred to a later change.
7. **Run `intent-check`** on the criteria: it refuses intentions ("fast", "clean",
   "robust"), criteria with no check, empty non-goals, and unresolved ambiguities.
8. **Re-read the intent against the request** with the person who asked, before
   implementation. Fifteen minutes here is cheaper than a rewritten diff.

## Exit Criteria

- [ ] One intent sentence, phrased as a user-visible outcome.
- [ ] Every behaviour has a criterion with an observable check.
- [ ] Non-goals are listed, not implied.
- [ ] Resolved ambiguities name who resolved them.
- [ ] The verification boundary is stated (done vs. deferred).
- [ ] `intent-check` refuses nothing.
- [ ] The requester read the intent back and agreed.

## Common Failures

| Failure | Fix |
|---|---|
| Intent phrased as an implementation | Phrase it as the outcome a user gets |
| "Fast", "clean", "robust" as criteria | Numbers and units, or a given/when/then |
| Non-goals left implicit | Write them; they are the cheapest scope control |
| Interpretation resolved in someone's head | Record the reading and who chose it |
| Criterion with no check | Attach a test, query or owned manual step |
| Intent written, never read back | Read it with the requester before the first commit |
