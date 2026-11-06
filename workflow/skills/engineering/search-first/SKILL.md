---
name: search-first
description: Search the repository, npm, PyPI and GitHub before writing a dependency, helper or module that probably already exists. Use when about to add a package or a general-purpose utility instead of reusing what is available.
metadata:
  origin: ECC · skills/search-first
  category: engineering
  phase: plan
  status: adopted
  version: 1
---

# Search First

The cheapest code to maintain is the code that is never written. This skill turns
"let's implement X" into a decision backed by evidence: it exists, it is already
in the repo, or it genuinely does not and must be built.

## When to Use

- Before adding a dependency.
- Before writing a general-purpose helper (dates, parsing, HTTP, CLI).
- When starting a non-trivial task in a repository you do not know.
- When an agent proposes "create a module for…" without having looked around.

## When Not to Use

- Domain logic: it is in no package, and searching wastes the turn.
- When the repository forbids new dependencies by policy.
- The catalogue, rather than the package ecosystem: `skill-scout` searches what already exists here.

## Procedure

1. **Search the repository first** — fastest and already integrated:
   `grep -r`, `git log --all -S`, and read the neighbouring folder.
2. **Search the ecosystem registry** (npm, PyPI, crates, pkg.go.dev). Minimum bar
   to accept a package: recent maintenance, compatible licence, dependencies not
   disproportionate, small API surface you can audit.
3. **Search GitHub for the problem**, not for the name of your imagined solution:
   "parse invoice pdf", not "pdfHelper".
4. **Record the decision in three lines** in the commit or the plan: what you
   searched, what you found, why you chose it (or why you wrote it by hand).
5. **If writing by hand**, keep it minimal, define the interface first and add a
   test (hand off to `tdd-workflow`).
6. **Set a time box on the search**: thirty minutes for the repository, thirty more for the ecosystem. Past that, the information gain is lower than the cost of writing it.
7. **Write down what you rejected, in one line each**: the next person will search the same three packages, and the reasons are the only thing that saves them the trip.

## Exit Criteria

- [ ] The search is on record (command or URL) along with the decision.
- [ ] No new dependency entered without a written justification.
- [ ] If something in the repository was reused, it is linked.
- [ ] If written by hand, the reason is explicit — not "faster this way".

## Common Failures

| Failure | Fix |
|---|---|
| Pulling a 40-dependency package to format a date | Write ten lines with a test |
| Reimplementing something already in `src/utils` | Search before writing |
| Choosing the most popular package without checking maintenance | Look at last release and open issues |
| Searching the name of the solution you already have in mind | Search the problem |
| Adopting code with an incompatible licence | Check the licence before integrating |
| Searching until the perfect package appears | Time box it; decide with what you have |
