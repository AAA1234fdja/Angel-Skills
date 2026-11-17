---
name: release-notes-audit
description: Check that release notes describe what actually shipped: every user-visible change, the breaking ones first, and nothing that is still behind a flag. Use when publishing a release, or when notes and the changelog disagree.
metadata:
  origin: original
  category: content
  phase: ship
  status: original
  version: 1
---

# Release Notes Audit

Release notes are a contract with the people who have to upgrade. They fail in two
directions: they omit a breaking change, which breaks someone's release, or they
announce something that is not on by default, which wastes a support cycle explaining
that the feature is behind a flag. The audit is mechanical because the material is:
diff the shipped surface against the claims, and refuse notes that cannot be resolved
to a change.

## When to Use

- Before publishing a release or a version bump.
- The changelog and the release notes disagree, or one is empty.
- A change touches the public surface: API, CLI, config, schema, permissions.
- After a hotfix, where notes are usually written from memory.

## When Not to Use

- Writing the changelog entry itself: that is `changelog-discipline`.
- Deciding whether the release is ready: that is `release-readiness`.
- Internal refactors nobody can observe: they should not generate notes at all.

## Procedure

1. **Derive the change list from the diff, not from memory**: commits, merged PRs and
   the published surface. Notes written from memory omit exactly the change somebody
   made at 6 pm.
2. **Classify every entry**: breaking, added, changed, fixed, removed. Breaking entries
   go first and name the required action, not just the change.
3. **Tie each note to a change** — a commit, an issue or a PR — so a reader can verify
   it and an author cannot invent it.
4. **Refuse notes for unshipped work**: a feature behind a flag that is off by default
   is not released, it is planned. Say which, in those words.
5. **State the upgrade requirement** for anything that needs one: migration command,
   config change, dependency bump, data backfill.
6. **Check the audience**: a note that names internal services is noise for a library
   consumer; a note that only says "improvements" is noise for everyone.
7. **Run `notes-audit`** on the draft: it flags breaking entries without a required
   action, notes with no linked change, announced work behind a disabled flag, and
   notes that mention no upgrade path despite a breaking change.
8. **Publish the notes with the release, in the same change** as the version bump. Notes
   written after the fact describe a release nobody made.

## Exit Criteria

- [ ] The change list came from the diff and merged changes, not from memory.
- [ ] Every breaking entry is first and names the required action.
- [ ] Every note links to a commit, issue or PR.
- [ ] Work behind a disabled flag is not announced as shipped.
- [ ] Upgrade requirements are stated for every change that needs one.
- [ ] The notes are checked against the audience.
- [ ] `notes-audit` reports no unlinked note and no undocumented breaking change.

## Common Failures

| Failure | Fix |
|---|---|
| Notes written from memory | Derive the list from the diff and merges |
| "Breaking changes" with no action | Name the required action, not just the change |
| Announcing flagged-off features | Say "planned" or leave it out |
| No links to changes | One link per note, or it did not happen |
| Notes as a list of PR titles | Say what changed for the user, not who changed it |
| Publishing before the notes exist | Ship them in the same change as the version |
