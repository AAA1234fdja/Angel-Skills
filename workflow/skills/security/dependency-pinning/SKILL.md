---
name: dependency-pinning
description: Pin and verify what you install: exact versions, lockfile integrity, transitive surface and a path to update. Use when converting ranges to pins, when two machines resolve different versions, when an audit asks what you ship, or before adding a dependency that brings thirty more.
metadata:
  origin: original
  category: security
  phase: implement
  status: original
  version: 1
---

# Dependency Pinning

A dependency declared as a range is a decision deferred to install time, on a
machine you do not control. Pinning is not paranoia: it is the difference between
"this build is reproducible" and "this build was reproducible on my laptop last
Tuesday". The other half is honesty — a pinned direct dependency with forty
unpinned transitive ones is a lockfile with a story.

## When to Use

- Converting ranges to pins, or investigating why two machines resolve differently.
- An audit asks what the artefact actually contains.
- A dependency is being added that pulls in a large transitive surface.
- An advisory lands and you need to know whether you are affected, fast.

## When Not to Use

- Auditing a dependency's licence or provenance: `dependency-audit` owns that.
- Choosing between two packages: that is a design decision, not a pinning one.
- Internal packages built from the same monorepo commit: they are already pinned.

## Procedure

1. **Pin direct dependencies to exact versions** and commit the lockfile. A range in
   the manifest plus a lockfile is acceptable; a range without a lockfile is not.
2. **Verify integrity hashes** for every artefact the lockfile names. A pin without a
   hash pins a name, not a file.
3. **Count the transitive surface** before adding a dependency — the `pin-audit` tool
   does it — and require a reason for anything that triples it.
4. **Keep one lockfile per application**, not per library, and never resolve two
   versions of the same package without recording why.
5. **Automate the update path**: a bot that opens a pinned bump with the changelog is
   the difference between pinning and freezing. A pin nobody updates becomes a
   vulnerability with a date on it.
6. **Record the advisory path**: when a CVE lands, the question is "which pinned
   version am I on", and the answer must be one command, not a search.
7. **Re-run the audit on every lockfile change**, in CI. A pin audit that runs
   quarterly audits a state nobody remembers.

## Exit Criteria

- [ ] Every direct dependency is pinned to an exact version.
- [ ] A lockfile is committed, with integrity hashes for every entry.
- [ ] The transitive surface is counted, and large additions have a stated reason.
- [ ] No package resolves to two versions without a recorded reason.
- [ ] `pin-audit` reports no floating range, no missing hash and no duplicate version.
- [ ] An update path exists (bot or scheduled task) with an owner.

## Common Failures

| Failure | Fix |
|---|---|
| Ranges in the manifest, no lockfile | Commit the lockfile; the range is only acceptable with it |
| Pin without an integrity hash | Pin the file, not the name |
| Pinning everything and never updating | Automate bumps; a frozen pin is a future CVE |
| Two versions of the same package | Record why, or unify; silent duplication hides risk |
| Counting only direct dependencies | The transitive surface is what ships |
| Auditing once before a release | Run it on every lockfile change |
