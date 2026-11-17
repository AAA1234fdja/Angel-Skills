---
name: skill-scout
description: Search what already exists — local library, sibling repos, external packs — before authoring a new skill or installing one. Use when a case feels new, when someone asks for a skill and nobody checked, or before pulling in a library for one procedure.
metadata:
  origin: adapted · ECC · skills/skill-scout
  category: governance
  phase: research
  status: adopted
  version: 1
---

# Skill Scout

The most expensive skill is the one written twice under two names. Authorship is
rewarding and search is boring, so the boring part happens first: what is already in
this library, what is in the repositories we already depend on, and what is published
under a licence we can carry. Scouting is not research theatre — it ends in one of
three decisions, and "author it" is the last of them.

## When to Use

- A case feels new and nobody has checked the library.
- Someone asks for a skill, a tool or an agent and the answer might already exist.
- Before adopting a library for a single procedure it happens to contain.
- Before a rewrite of a skill whose description sounds familiar.

## When Not to Use

- Auditing the quality of what exists: that is `skill-stocktake`.
- Deciding whether an existing candidate may be installed: that is `harness-provenance`.
- Writing the skill once the decision is made: that is `skill-authoring`.

## Procedure

1. **Search the local library by decision, not by name.** "This decides how to retire
   a schema" finds `schema-evolution` even though the words differ.
2. **Search by trigger**: does any skill's "when to use" already answer this sentence?
   That is a duplicate owner, not a new case.
3. **Search the repos you already depend on**, at a pinned commit, before searching
   the internet. A dependency you already audit is cheaper than a new one.
4. **Search external sources with the licence and the commit in hand**: an
   MIT-licensed pack at a named commit is evidence; a blog post is a hint.
5. **For every hit, record three things**: what it covers, what it does not, and why
   adapting it is better or worse than authoring here.
6. **Prefer, in order**: reuse as-is → adapt with an `origin` note → author new.
   Authoring is the fallback because a new skill costs maintenance forever.
7. **Run `scout-report`** on the candidate list: it refuses a "new" decision when a
   high-overlap hit exists, and flags reuse without a licence or a pinned version.
8. **Write the decision down** in the skill's `origin` field, so the next scout sees
   why this exists instead of recreating it.

## Exit Criteria

- [ ] The local library was searched by decision and by trigger.
- [ ] Dependencies already in use were searched before external sources.
- [ ] Each external hit records licence and pinned commit.
- [ ] For each hit: what it covers, what it does not, why adapt or author.
- [ ] The decision is one of three: reuse, adapt, author — with a reason.
- [ ] `scout-report` accepts the decision, with no high-overlap hit left unexplained.
- [ ] The chosen skill records its `origin`.

## Common Failures

| Failure | Fix |
|---|---|
| Searching by name | Search by decision and by trigger phrase |
| Jumping to the internet | Search the dependencies you already audit first |
| "MIT, presumably" | Record the licence and the commit you actually read |
| Adapting without noting origin | The `origin` field is the scout's output |
| Authoring because adapting feels like less credit | Authoring costs maintenance forever |
| Scout that ends without a decision | Three outcomes only: reuse, adapt, author |
