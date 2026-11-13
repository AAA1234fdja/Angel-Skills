---
name: santa-review
description: Adversarial review where two independent reviewers must both pass a change before it ships. Use when a change is high-impact, when review has become a rubber stamp, or when one reviewer's approval has stopped predicting anything.
metadata:
  origin: adapted · ECC · skills/santa-method
  category: product
  phase: review
  status: adopted
  version: 1
---

# Santa Review

One reviewer is a filter; two independent reviewers who must both pass are a different
control, because the cheap failure of peer review is social — the second person defers
to the first, or to the author's confidence. Independence is the mechanism: separate
contexts, separate briefs, no shared conclusion before both have written theirs. The
cost is real, so this applies to the changes where being wrong is expensive.

## When to Use

- The change is high-impact: money, identity, data loss, permissions, public contracts.
- Review has become a formality: approvals arrive in minutes on large diffs.
- A defect shipped that a reviewer had "looked at".
- A single reviewer is unavailable and their absence is a blocker.

## When Not to Use

- Routine changes with tests that would catch the failure: `code-review` is enough.
- The question is whether the design is right, before code exists: `adr-writing`.
- A security-specific pass: `security-review` is that lens, and it may be one of the two.

## Procedure

1. **Define what "pass" means before either reviewer starts**: the criteria both must
   satisfy. Without a shared rubric, independence produces two opinions, not two checks.
2. **Brief both reviewers identically and separately**: the diff, the intent, the
   evidence. Neither sees the other's findings until both have written them.
3. **Give each reviewer a different lens** — one on correctness and data, one on failure
   modes and operability — so the pair covers more than two copies of one review.
4. **Collect written verdicts first**, then discuss. A verbal discussion before writing
   collapses the independence you paid for.
5. **Require both to pass.** One pass and one "concerns but approves" is a fail: the
   concerns are what the second reviewer is for.
6. **Escalate disagreement to evidence, not seniority**: what test, what measurement,
   what requirement settles it. Unresolved disagreement is a finding about the change.
7. **Record what each reviewer caught**, and review the record over time. If one lens
   never finds anything, it is not being applied.
8. **Run `dual-review`** on the two verdicts: it refuses a pass with unresolved
   blockers, a shared-context review, identical lenses, and a "pass with concerns".

## Exit Criteria

- [ ] Pass criteria are written before the reviews start.
- [ ] Both reviewers were briefed identically and reviewed independently.
- [ ] The two lenses are different and stated.
- [ ] Both verdicts were written before any discussion.
- [ ] Both reviewers pass, with zero unresolved blockers.
- [ ] Disagreements were settled by evidence, named in the record.
- [ ] `dual-review` reports two independent passes with distinct lenses.

## Common Failures

| Failure | Fix |
|---|---|
| Both reviewers read the same chat thread first | Written verdicts before any discussion |
| "Approve with concerns" counted as a pass | Concerns are blockers or they are withdrawn |
| Identical lenses | Assign correctness and operability explicitly |
| One reviewer defers to the other's seniority | Settle by evidence, name it in the record |
| Applying it to every change | Reserve it for high-impact; cost matters |
| No record of what was caught | Track it; a lens that catches nothing is not applied |
