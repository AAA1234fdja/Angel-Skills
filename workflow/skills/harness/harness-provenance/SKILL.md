---
name: harness-provenance
description: Decide whether something may be installed into the harness, and on what terms: a named source, a pinned version, a reviewable diff and a removal path. Use when adding a skill pack, a hook, a server or a permission is proposed, or when someone proposes installing from a moving branch.
metadata:
  origin: adapted · ECC · skills/skill-scout, skills/repo-scan
  category: harness
  phase: design
  status: adopted
  version: 1
---

# Harness Provenance

Installing into a harness is an act of trust with a blast radius: hooks run without
being asked, servers expose their tools to the model, permissions widen what an agent
may do while nobody is watching. The question is never "is this library good?" but
"which exact commit am I trusting, who reviewed it, what can it reach, and how do I get
it out?" A moving branch answers none of those, which is why `latest` is a refusal,
not a version.

## When to Use

- Someone proposes installing a skill pack, a hook set, a server or a CLI.
- A dependency arrives as `curl | bash`, a plugin marketplace entry or a branch ref.
- A permission is about to be widened to unblock work.
- Reviewing a config change that adds an auto-loading artefact.

## When Not to Use

- Inventorying what is already installed: that is `harness-inventory`.
- Writing the skill yourself: that is `skill-authoring`.
- Judging an existing skill's quality: that is `skill-stocktake`.

## Procedure

1. **Name the exact source**: repository and commit, or registry and integrity hash.
   A branch, a `latest` tag or an unversioned URL is refused, not noted.
2. **Read the diff you are trusting**, at least the parts that execute: hooks,
   install scripts, server entry points. If the diff cannot be reviewed, it cannot be
   installed.
3. **State the capability delta**: what the harness can now do that it could not
   before, layer by layer. "It only adds a skill" is a claim, and usually false.
4. **Record the removal path and test it once.** Uninstall instructions that were
   never executed are a hope.
5. **Pin in the harness config, not in a README**, so the pin is what runs. A pin that
   lives in prose protects nothing.
6. **Set the update policy before the first install**: who reviews a bump, and what
   evidence a bump needs (changelog, diff, tests). Otherwise "pin" quietly becomes
   "freeze".
7. **Run `install-gate`** on the proposal: it refuses moving refs, missing integrity,
   unreviewed executable surface, absent removal path and unstated capability delta.
8. **Record the decision** — installed, refused, or deferred — with the reason, in the
   changelog of whoever owns the harness.

## Exit Criteria

- [ ] The source is a commit or a hash, not a branch or `latest`.
- [ ] The executable surface was read and named.
- [ ] The capability delta is stated per layer.
- [ ] A removal path exists and was executed at least once.
- [ ] The pin lives in the config that actually runs.
- [ ] The update policy names a reviewer and the evidence a bump needs.
- [ ] `install-gate` refuses nothing, and the decision is recorded with its reason.

## Common Failures

| Failure | Fix |
|---|---|
| `latest`, a branch ref, or an unpinned URL | Pin the commit; a moving ref is not a version |
| Reviewing the README instead of the diff | Read what executes: hooks, scripts, entry points |
| "It only adds docs" | State the capability delta per layer, then decide |
| Uninstall path never tried | Execute it once, before you need it |
| Pin written in documentation | Put the pin where the runtime reads it |
| Pinning and never updating | Name the reviewer and the evidence a bump needs |
| Installing without a recorded reason | Record installed / refused / deferred, and why |
