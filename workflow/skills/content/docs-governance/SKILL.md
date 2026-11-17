---
name: docs-governance
description: Give every document a job, an owner and a shelf life, so a long-lived project stops generating stale pages. Use when documentation contradicts itself, when nobody knows which doc is current, or before adding another file to a folder that already has forty.
metadata:
  origin: adapted · ECC · skills/docs-governance, skills/living-docs-governance
  category: content
  phase: audit
  status: adopted
  version: 1
---

# Docs Governance

Documentation rots in a specific way: it does not disappear, it accumulates. Three
files describe the same setup, one is right, nobody knows which, and every new
engineer picks at random. Governance is not a style guide — it is assigning four roles
and enforcing them, so that "which doc is current?" has a structural answer instead of
a social one.

## When to Use

- Two documents describe the same thing and disagree.
- Nobody can say where a given fact belongs, so it lands in three places.
- A folder of docs has grown past the point anyone reads it.
- Before adding a document to a set that already has an owner for that subject.

## When Not to Use

- Writing the content of one document: `doc-writing` is the procedure.
- Deciding an architecture choice in writing: `adr-writing` owns that format.
- The API reference, which is generated and has its own completeness rules: `api-reference-writing`.

## Procedure

1. **Assign one of four roles to every document**: constitution (rules that rarely
   change), map (where things are), status (what is true now) or history (what was
   decided and when). A document with no role is a candidate for deletion.
2. **One owner per document**, a person or a team, not "everyone". An unowned document
   is nobody's job and will be wrong within a quarter.
3. **One source per fact**, with the other copies linking to it. If the same fact must
   appear twice, one copy is generated or is a link, never a retyped paragraph.
4. **Give status documents a review date**, and make the date visible in the document.
   Undated status is a claim about a past that nobody can locate.
5. **Route decisions to the record and keep them out of the map**: an ADR referenced
   from the map stays true; the same content pasted into the map goes stale twice.
6. **Delete before you add.** When a new document is proposed, name the one it replaces
   or the gap it fills. Two documents with the same role is the failure this skill exists for.
7. **Audit links and roles on a schedule**, not once: a link checker catches the
   mechanical rot, the role audit catches the duplication.
8. **Run `docs-audit`** on the inventory: it flags documents with no role, no owner or
   no review date, duplicate facts, and decisions living outside the record.

## Exit Criteria

- [ ] Every document has exactly one role, one owner and (for status) a review date.
- [ ] Every repeated fact has one source and links elsewhere.
- [ ] Decisions live in the record, referenced from the map.
- [ ] Every new document names what it replaces or the gap it fills.
- [ ] Link and role audits are scheduled with an owner.
- [ ] `docs-audit` reports no unowned document and no duplicated fact.

## Common Failures

| Failure | Fix |
|---|---|
| A document with no role | Assign one of four, or delete it |
| Owner = "the team" | Name a person or a rotating role |
| The same fact in three docs | One source, the rest link |
| Decisions pasted into the map | Reference the ADR; paste nothing |
| Adding without removing | Name the replacement at proposal time |
| One audit, never repeated | Schedule links and roles separately |
