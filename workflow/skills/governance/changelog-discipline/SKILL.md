---
name: changelog-discipline
description: Keep a changelog a consumer can act on: what changed, what breaks and what to do about it. Use when releasing, when a skill version changes, or when readers cannot tell whether an update affects them.
metadata:
  origin: ECC · conventional-commit-review
  category: governance
  phase: document
  status: adopted
  version: 1
---

# Changelog Discipline

A changelog is not a commit log with dates. It is the document a consumer reads to
decide whether to act — and if it does not answer "does this affect me", it is
decoration.

## When to Use

- Releasing a version of the package or a skill.
- A skill's version changes in a way consumers can notice.
- A contract or protocol changes.

## When Not to Use

- Internal refactors with no observable change.
- During the change itself: write the entry when the change is ready.
- The release view of the same change: `release-notes-audit` checks that the notes match what shipped.

## Procedure

1. **Write for the consumer**, not the author: what changed in behaviour, not which
   file was touched.
2. **Lead with impact**: breaking, deprecated, added, changed, fixed, security,
   removed.
3. **State the action** for a breaking change: what to do, by when.
4. **Link the detail** (commit, skill id, contract version) rather than inlining it.
5. **Group by version**, newest first, with a date the reader can trust.
6. **Name the consumer**: a caller of the API, an operator, a skill author. An
   entry without a subject makes the reader work out whether it applies to them.
7. **Use the same verbs every time** so a reader can scan; inconsistent language
   turns a changelog into prose.
8. **Never rewrite published entries.** Corrections go in a new entry.

## Exit Criteria

- [ ] Every entry states observable impact, not file changes.
- [ ] Breaking changes state the required action.
- [ ] Security fixes are called out separately.
- [ ] Entries are grouped by version with dates.
- [ ] Published entries are untouched.
- [ ] `changelog-lint` reports no vague entry and no entry without an audience.

## Common Failures

| Failure | Fix |
|---|---|
| "Various improvements" | Name the observable change |
| Breaking change buried in a list | Lead with it and state the action |
| Rewriting old entries | Add a correction entry |
| No dates | A changelog without dates cannot be trusted |
| Commit messages pasted in | Translate to impact |
| Security fixes mentioned in passing | Separate section, always |
