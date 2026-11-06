---
name: coding-standards
description: Baseline conventions for naming, unit size, immutability and error visibility, so a review discusses behaviour instead of style. Use when creating modules, refactoring, or reviewing code whose repository has no written convention.
metadata:
  origin: ECC · skills/coding-standards
  category: engineering
  phase: implement
  status: adopted
  version: 1
---

# Coding Standards

Conventions exist so that review argues about **what the code does**, not about
how it is typed. If the repository already has a convention, that convention
wins; this document covers what is usually left unwritten.

## When to Use

- Creating a module, package or file.
- Refactoring code that will be touched across several sessions.
- Reviewing code in a repository with no declared convention.

## When Not to Use

- When a linter and formatter are configured: run them instead of debating.
- Generated or vendored files.
- A rule the team disagrees with: change it in its own change, and `code-review` judges the result.

## Procedure

1. **Find the existing convention first**: read two or three neighbouring files,
   look for `.editorconfig`, `eslint`, `ruff`, `gofmt`.
2. **Names say what, not how**: `invoiceTotal` (value), `calculateInvoice`
   (action), `isPaid` (boolean). No abbreviations that are not already domain
   vocabulary.
3. **Small units.** A function that fits on a screen and does one thing. If it
   needs "part 1 / part 2" comments, it is two functions.
4. **Immutable by default.** Prefer constants, new values and pure functions;
   mutate only with a measured reason.
5. **Errors are explicit.** A failure is returned or raised with context; never
   swallowed and never turned into `null` without saying so in the name.
6. **Comments explain why.** The code says what; the comment says why this way,
   or what breaks if it changes.
7. **Dependencies.** Check `search-first` before adding one; justify in the
   commit why what already exists was not enough.

## Exit Criteria

- [ ] New code follows the convention found in step 1 (or this document).
- [ ] No function does two things; no name misleads.
- [ ] Errors are not silenced; `style-scan` reports zero silence smells.
- [ ] Every new dependency is justified in the commit message.
- [ ] Lint and format green without adding exceptions to the config.

## Common Failures

| Failure | Fix |
|---|---|
| Turning a lint rule off so the build passes | Fix the code, or change the rule in its own PR |
| Renaming inside a functional PR | Renames go in a separate commit |
| Comments that restate the code | Comment intent, or delete it |
| `try { } catch (e) {}` to "avoid failures" | Fail fast with context |
| A 900-line module "because it belongs together" | Split by responsibility, backed by tests |
| Convention discovered after the PR | Read two neighbouring files before the first line |
