---
name: skill-stocktake
description: Audit an existing skill library for quality instead of adding to it: dead skills, duplicate ownership, drifting procedures and criteria nobody can check. Use when a new skill is about to be authored, after a batch of additions, or when the library has grown faster than anyone can recall what is in it.
metadata:
  origin: adapted · ECC · skills/skill-stocktake
  category: governance
  phase: audit
  status: adopted
  version: 1
---

# Skill Stocktake

A skill library fails quietly. Nothing breaks when two skills own the same decision,
when a procedure drifted away from what the team does, or when an exit criterion
stopped being checkable — it just stops being read. This procedure audits the
library as an inventory with owners, not as a pile of documents, and it is meant to
run **before** authoring, because the cheapest new skill is the one that already
exists under another name.

## When to Use

- Before authoring a skill: the case may already have an owner.
- After a batch of additions, to catch overlap the reviewer of each PR could not see.
- When the router returns two skills for one need, or none for a common one.
- When nobody can say how many skills the library has without running a command.

## When Not to Use

- Reviewing one skill's procedure for quality: that is `skill-audit`.
- Deciding whether a skill is *allowed* in (schema, acceptance, sample): `validate --strict`.
- Judging whether a tool computes the right thing: that is the tool's own tests.

## Procedure

1. **Inventory from the registry, never from memory.** Ids, category, phase, tool
   count, acceptance count. A library audited by recollection audits the skills
   someone happens to remember.
2. **Find duplicate ownership**: two skills whose "when to use" clauses would both
   answer the same sentence. That is not a wording problem, it is an undecided
   boundary — and the router will resolve it by scoring, which is to say arbitrarily.
3. **Find dead skills**: never routed, no tool, no sibling reference, not mentioned in
   any document. A skill nobody reaches is a document with a `description` field.
4. **Find drift**: a procedure whose steps name artefacts that no longer exist, or
   whose exit criteria a new team member could not satisfy without asking. Drift is
   invisible per-file and obvious in a stocktake.
5. **Find unmeasurable criteria**: exit criteria phrased as intentions ("is clear",
   "is robust") rather than observations. Count them; the number is the library's real
   debt.
6. **Rank the findings by what they cost**: a duplicate owner costs a wrong answer per
   use; a dead skill costs context; a drifting procedure costs trust.
7. **Decide per finding**: fold (into the owner), fix (procedure or criteria), retire
   (with the reason recorded), or leave with a note. A stocktake with no decisions is
   a report nobody acts on.
8. **Run the `stocktake` tool** over the inventory: it reports the duplicate pairs,
   the orphans, the skills with no executable criterion, and the ones whose tools are
   thinner than their prose.
9. **Do the removals in the same change as the audit.** A "to remove" list that
   survives the quarter becomes permanent.

## Exit Criteria

- [ ] The inventory came from the registry, with a date.
- [ ] Every duplicate pair is resolved to one owner, or the boundary is stated.
- [ ] Every dead skill is folded, retired or justified in one sentence.
- [ ] Drifted procedures are corrected, not annotated.
- [ ] The count of unmeasurable criteria is recorded, and lower than last time.
- [ ] Every finding has one of four decisions: fold, fix, retire, leave.
- [ ] `stocktake` reports no duplicate ownership and no skill without an executable criterion.

## Common Failures

| Failure | Fix |
|---|---|
| Auditing from memory or from the folder listing | Read the registry, with phases and tools |
| Two skills "both plausibly" own a case | Pick the owner and write the boundary in both `not_for` lists |
| Counting skills as a health metric | Count decisions covered, and criteria checkable |
| Renaming drift as "legacy" | Correct the procedure or retire the skill |
| A report with findings and no decisions | Four outcomes only: fold, fix, retire, leave |
| Removing skills in a later change | Remove in the same change; otherwise it never happens |
