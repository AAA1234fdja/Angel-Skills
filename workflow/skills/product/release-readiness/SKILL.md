---
name: release-readiness
description: Decide whether a change may ship: the five gates, the rollback path and the evidence for each. Use when a release is being announced, a flag is about to be turned on, a hotfix skips the normal path, or someone asks "can we ship this today".
metadata:
  origin: original
  category: product
  phase: ship
  status: original
  version: 1
---

# Release Readiness

A release is not a date. It is a claim — "this is safe to run for everyone" — and
a claim needs evidence or it is a hope with a version number. This procedure turns
the claim into five gates, each of which is either proven, waived by a named
person, or a blocker. The output is a verdict, never a "looks good to me".

## When to Use

- A change is about to reach users: deploy, flag on, migration, public API.
- A hotfix wants to skip the normal path — that is exactly when the gates matter.
- Someone asks whether a release is ready, and the answer must be evidence, not
  confidence.
- A release failed and the team is deciding whether to roll forward or back.

## When Not to Use

- Routine merges to a branch nobody runs (nothing ships).
- Pure refactors already covered by an automated gate that reports on every PR.
- Deciding *what* to build: that is a product decision, not a readiness check.
- What should be built, and what counts as done: `intent-driven-development` decides it before any release exists.

## Procedure

1. **Name the change.** One sentence, in user terms: what becomes possible, what
   stops working, and who is affected. If it cannot be said in one sentence, the
   release is carrying more than one change and should be split.
2. **Score the five gates.** Each gate is `pass`, `waived` (with a name and a
   reason) or `blocked`:
   - **tests** — the suite ran on the artefact being shipped, not on a branch.
   - **rollback** — the way back is written down and has been executed once.
   - **observability** — there is a signal that would show this change failing.
   - **blast radius** — the affected surface is known and is as small as possible.
   - **communication** — whoever must support it knows it is coming.
3. **Run the `release-gate` tool** on the collected evidence. It returns the
   overall verdict and the exact gates that stop the release. Do not argue with
   it: an unproven gate is `blocked`, not "probably fine".
4. **Resolve every blocker** by one of three routes: fix it, obtain a waiver from
   the owner of that gate, or remove the risky part from this release. Removing
   scope is always allowed and usually the cheapest.
5. **Write the rollback line before shipping**, not after: the command, the
   expected duration, the signal that tells you to execute it. A rollback plan
   invented under pressure is a plan that fails.
6. **Ship small and watch.** One change, one deployment, one metric to compare for
   a stated window. If the window is not stated, the release is not over.
7. **Close the release in writing**: the window, the metric, the verdict. A release nobody declared finished is still being watched by nobody.

## Exit Criteria

- [ ] The change is named in one sentence, in user terms, with its blast radius.
- [ ] All five gates are `pass` or `waived` with a name attached; the `release-gate`
      tool reports `ok: true`, or every blocker it lists is resolved.
- [ ] The rollback command is written down and has been run at least once in a
      non-production environment.
- [ ] The metric and the observation window are stated before the deploy.
- [ ] The people who support the change know it is going out.

## Common Failures

| Failure | Fix |
|---|---|
| "Tests pass" but on a branch, not the artefact | Run the suite on what is being shipped (tag, digest, build id) |
| Rollback plan invented during the outage | Execute the rollback once in staging, before the release |
| Five changes in one release | Split; one change per release is the cheapest gate of all |
| Waiver with no name | A waiver is a decision by a person; anonymous waivers are blockers |
| Watching a dashboard nobody set up | The observability gate is about the signal, not the tool |
| Release "done" at deploy time | It is done when the observation window closes clean |
