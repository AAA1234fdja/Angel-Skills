---
name: dependency-audit
description: Audit imports and dependencies for unused, unpinned or unreviewed packages before they become permanent. Use when adding packages, preparing a release, or after a supply-chain advisory.
metadata:
  origin: ECC · dependencies (pattern)
  category: security
  phase: audit
  status: adopted
  version: 1
---

# Dependency Audit

A dependency is a permanent liability with a one-time benefit. The audit is the
moment to decide whether the liability is still worth paying.

## When to Use

- Adding a package.
- Preparing a release or a lockfile refresh.
- After a supply-chain advisory in the ecosystem.

## When Not to Use

- A repository with no dependency manifest.
- During an incident: audit after, restore first.

## Procedure

1. **List declared dependencies and actual imports.** Anything declared and never
   imported is removal candidate number one.
2. **Check pinning**: exact or lockfile-pinned in applications; ranges only in
   libraries, and deliberately.
3. **Check maintenance**: last release, open critical issues, whether the maintainer
   is one person with no succession.
4. **Check licence compatibility** with the project's distribution model.
5. **Check transitive weight**: how many packages arrive with this one.
6. **Check install-time scripts**: postinstall hooks are arbitrary code execution
   at install time.
7. **Record the decision** per dependency: keep, pin, replace, remove, with a reason.

## Exit Criteria

- [ ] Every declared dependency maps to at least one import (or is removed).
- [ ] Applications pin exact versions or commit a lockfile.
- [ ] Every dependency has a maintenance and licence verdict.
- [ ] Install-time scripts are reviewed or disabled.
- [ ] Removals executed and the suite still green.

## Common Failures

| Failure | Fix |
|---|---|
| Ranges in an application | Pin, or commit the lockfile |
| Keeping an unused package "in case" | Remove; it can come back |
| Ignoring transitive count | Check what arrives with it |
| No licence check until release | Check at adoption |
| Postinstall scripts unreviewed | Treat as code you are running |
| Auditing only direct dependencies | Transitives are the supply chain |
