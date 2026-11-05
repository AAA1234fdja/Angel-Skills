---
name: doc-writing
description: Write and review documentation that stays true: named source of truth, audience, failure modes and examples that actually run. Use when documenting a feature, writing a README, or when docs and code have already drifted.
metadata:
  origin: ECC · article-writing + update-docs
  category: content
  phase: document
  status: adopted
  version: 1
---

# Doc Writing

Documentation that drifts is worse than none: it teaches something false with
authority. The only documentation worth keeping is the kind that names what it can
be wrong about and how to check it.

## When to Use

- Documenting a feature, a module, a CLI or a process.
- A reader asked a question the docs should have answered.
- Docs and code have already drifted.

## When Not to Use

- When the code can say it better: a well-named function over a paragraph.
- Generated reference for a public API: generate it instead of writing it.

## Procedure

1. **Name the audience and the decision they are making.** "Developers who need to
   add an endpoint" is an audience; "everyone" is not.
2. **Name the source of truth** the doc describes (file, command, schema), so a
   reader can check whether it is stale.
3. **Put the runnable example first**: a command that works, copy-pasteable.
4. **Document the failure modes**: what goes wrong, what the error looks like, what
   to do — this is the section readers actually need.
5. **Link instead of duplicating**: a second copy of the truth drifts first.
6. **State the last-verified date and the version** it applies to.
7. **Review by following it literally**, on a machine that is not yours.

## Exit Criteria

- [ ] Audience and their decision are stated.
- [ ] Source of truth is named.
- [ ] At least one example was executed as written.
- [ ] Failure modes documented with the error text.
- [ ] No duplicated truth: links instead of copies.
- [ ] Last-verified date and applicable version present.
- [ ] `doc-lint` reports no blocking issue.

## Common Failures

| Failure | Fix |
|---|---|
| Docs written from memory | Follow them on a clean machine |
| Examples that nearly work | Execute them; paste the real output |
| No failure section | Readers hit errors and leave |
| Duplicated truth | Link to the source |
| No date or version | Nobody can judge staleness |
| Explaining the code line by line | Explain the decision and the constraint |
