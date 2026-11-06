---
name: secret-scan
description: Find credentials and high-entropy strings in the working tree and the diff, then say what to rotate. Use when committing, when a repository becomes public, or after a member leaves.
metadata:
  origin: ECC · skills/security-scan
  category: security
  phase: verify
  status: adopted
  version: 1
---

# Secret Scan

A secret in a repository is not a lint error, it is an incident. Deleting the line
does not undo the exposure: the value must be rotated, because it lives in every
clone, cache and backup.

## When to Use

- Before a commit that touches configuration.
- When a repository becomes public or its visibility changes.
- After a contributor leaves or a laptop is lost.
- On a schedule, as a cheap guard.

## When Not to Use

- As a replacement for rotation: the scan finds, the rotation fixes.
- For values that are demonstrably public (a public client id in a public SDK).
- The fix rather than the finding: rotate first, and `incident-comms` owns who is told and when.

## Procedure

1. **Scan three surfaces**: current tree, staged diff, and history (`git log -p`).
   The history is the one everybody forgets.
2. **Classify findings**: confirmed secret, probable (high entropy with a variable
   name), false positive (test fixture, obvious placeholder).
3. **Rotate first for confirmed secrets**, before cleaning anything. Cleaning
   without rotating is theatre.
4. **Remove from history only if the secret is already dead.** Rewriting history is
   destructive and needs consent.
5. **Add the pattern to the project's scanner config** so it cannot return.
6. **Document the incident**: what leaked, exposure window, rotation time.
7. **Make the scan asynchronous to the incident**: a pre-commit hook and a scheduled history scan, so detection does not depend on somebody remembering to look.

## Exit Criteria

- [ ] Tree, diff and history scanned, all three reported.
- [ ] Every confirmed secret rotated, with the time recorded.
- [ ] History rewritten only for dead credentials, with consent.
- [ ] A scanner rule prevents the same shape from returning.
- [ ] A short incident note exists with the exposure window.

## Common Failures

| Failure | Fix |
|---|---|
| Deleting the line and calling it fixed | Rotate: the value is already out |
| Scanning only the working tree | History and caches hold it too |
| Rewriting history for a live secret | Rotate first; history is secondary |
| Ignoring high-entropy strings | Verify each: a key usually looks random |
| No rule added afterwards | The same shape returns next month |
| Manual scans only | Hook the diff and schedule the history scan |
