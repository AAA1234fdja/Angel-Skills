---
name: technical-debt-ledger
description: Keep debt as a ledger with interest, not as a pile of TODOs: what it costs per month, who owns it and what pays it down. Use when debt keeps being mentioned in retros without a decision, when a rewrite is proposed as the only option, or when a shortcut is taken on purpose.
metadata:
  origin: original
  category: engineering
  phase: plan
  status: original
  version: 1
---

# Technical Debt Ledger

"Technical debt" is the most abused metaphor in the industry, because it is used to
mean both "a loan we took deliberately" and "a mess nobody has looked at". A ledger
separates them: every item has a principal (what it would cost to fix), an interest
(what it costs per month to keep) and an owner. Debt with interest lower than the
fix is fine; debt with interest above it is a decision nobody made.

## When to Use

- Debt appears in every retro and never in a plan.
- A rewrite is proposed; the ledger is the alternative to arguing from intuition.
- A shortcut is being taken on purpose — record it while the reason is known.
- A flaky area keeps consuming time and nobody can say how much.

## When Not to Use

- A single TODO with a ticket: the ticket is the record.
- Judging code style: that is `coding-standards`, and it is not debt unless it costs time.
- Deciding architecture: `adr-writing` records the decision, this records the cost.

## Procedure

1. **One row per item**, with the symptom a user or an engineer feels, not the code
   smell: "deploys take 40 minutes and roll back half the time" beats "bad CI".
2. **Estimate the principal** (hours to fix) and the **interest** (hours per month
   lost to it: workarounds, incidents, waiting, onboarding). Rough numbers, declared
   as rough, are enough; precision here is procrastination.
3. **Compute payback**: interest × 12 against principal. Payback under twelve months
   is a candidate for the next cycle; above it, the debt is cheaper than the fix and
   should be recorded as accepted.
4. **Classify each item**: `deliberate` (a loan with a reason), `inadvertent` (nobody
   chose it), `accepted` (measured, and cheaper to keep). The classification decides
   who acts.
5. **Name an owner per row.** Debt with no owner is not a ledger, it is a complaint.
6. **Run the `debt-ledger` tool** on the rows: it sorts by payback, flags missing
   interest and owner, and totals the monthly interest the team is paying.
7. **Review monthly and close rows explicitly** — fixed, or re-accepted with a new
   number. A ledger that only grows is a list of grievances with extra steps.

## Exit Criteria

- [ ] Every row states the felt symptom, the principal, the interest and the owner.
- [ ] Every row is classified deliberate, inadvertent or accepted.
- [ ] Rows are sorted by payback, and the top ones are in a plan or explicitly deferred.
- [ ] The monthly interest total is stated in one number.
- [ ] `debt-ledger` reports no row without interest or owner.
- [ ] The ledger has a review date.

## Common Failures

| Failure | Fix |
|---|---|
| Debt described as code smell | Describe the felt cost; smells have no interest rate |
| Interest never estimated | A rough hours-per-month number is enough to sort |
| No owner | Unowned debt is a complaint, not a ledger |
| Every row "high priority" | Payback sorts them; three items at a time |
| Rewrite proposed instead of a ledger | Price the rewrite against the total interest |
| Ledger never closed | Monthly review; fix or re-accept with a new number |
