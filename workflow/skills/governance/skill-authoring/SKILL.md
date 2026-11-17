---
name: skill-authoring
description: Register and author a new skill end to end: the three decision tests, scaffolding, manifest, validation and changelog. Use when the runtime or a person is about to add, move or restructure anything inside workflow/skills.
metadata:
  origin: ECC · skill-create + configure-ecc
  category: governance
  phase: meta
  status: original
  version: 1
---

# Skill Authoring

This skill exists so the package does not degrade. Every time an agent "improves" a
skill without following the contract, the registry and reality separate, and the
runtime starts loading things that no longer exist.

## When to Use

- Adding a skill to a category.
- Editing or correcting an existing skill.
- Creating a category.
- When `workflow validate` fails and the reason is not obvious.

## When Not to Use

- General documentation: that goes to `docs/`, not `skills/`.
- Changing the standard itself: a design decision, discussed first, bumps the
  package version.
- General documentation that is not a procedure: `doc-writing`.

## Procedure

1. **Apply the three tests**: trigger, procedure, checkable exit. If one fails,
   stop — it is a note, not a skill.
2. **Choose the category** from `categories.json`. One skill, one category: the one
   of its primary trigger.
3. **Check for an equivalent**: `workflow list`, `workflow plan <category>`, and the
   descriptions of its neighbours. If two descriptions can be swapped, one is
   redundant.
4. **Register before writing**: add the entry to `categories.json` — or let
   `workflow new` do both steps atomically.
5. **Write `SKILL.md`** with the frontmatter of the standard and the required
   sections. Body at most 260 lines; longer text goes to `references/`.
6. **Write `skill.json`**: phase, verbs, triggers, keywords, tools, contracts.
   Without it, routing is blind.
7. **Add tools only where the exit criteria are mechanical**, with the lowest risk
   that works and a schema for the input.
8. **Validate**: `workflow validate --strict`. Green or no commit.
9. **Changelog**: bump `metadata.version`, add a line to `CHANGELOG.md`.

## Exit Criteria

- [ ] The three tests pass and are written in one line each.
- [ ] `workflow validate --strict` exits 0.
- [ ] `name` matches the folder id; the id is new and stable.
- [ ] Description contains the trigger and fits in 700 characters.
- [ ] Required sections exist; the exit criteria are checkable.
- [ ] `skill.json` declares phase, verbs, triggers; tools are listed with risk.
- [ ] `CHANGELOG.md` updated and `metadata.version` bumped.

## Common Failures

| Failure | Fix |
|---|---|
| Creating the folder and forgetting the registry | `validate` must fail: register first |
| Copying an ECC skill verbatim | Rewrite for this repo and cite `origin` |
| Changing `name` while editing | The id is stable; renaming breaks everything |
| A skill with no exit criteria | It is a note |
| Description starting with the technique | Start with the outcome |
| Hand-editing the registry after scaffolding | Let `workflow new` keep both in sync |
