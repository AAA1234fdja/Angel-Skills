---
name: security-review
description: Adversarial review of a diff for reachable vulnerabilities, ranked by exploitability. Use when a change touches authentication, input handling, secrets, file paths or anything exposed to the network.
metadata:
  origin: ECC · skills/security-review
  category: security
  phase: review
  status: adopted
  version: 1
---

# Security Review

A security review that lists generic advice is worthless. The only useful output is
a reachable path from an attacker-controlled input to an effect, plus the patch that
closes it.

## When to Use

- A change touches authentication, authorisation, input parsing, secrets, file
  paths, subprocesses or anything reachable from the network.
- Before shipping a feature that accepts user content.
- When a dependency or a configuration change alters exposure.

## When Not to Use

- Pure refactors with no behavioural change: `code-review` covers them.
- As a substitute for an external pentest on a high-risk surface.

## Procedure

1. **Map the inputs first**: which of them can an attacker control? Everything else
   is a lower priority, not a finding.
2. **Trace each input to its effects**: query, shell, filesystem, template,
   redirect, deserialisation, LLM prompt.
3. **Check the four usual families**:
   - injection (SQL, shell, template, path traversal);
   - broken access control (missing authorisation, IDOR, trusting a client claim);
   - secret exposure (in code, logs, errors, URLs);
   - unsafe deserialisation and untrusted archives.
4. **Verify reachability.** A pattern in unreachable code is a note, not a
   vulnerability. State the path.
5. **Rank by exploitability**, not by how clever the pattern is.
6. **Write the patch** for anything above `low`, or the condition that must change.
7. **Check the dependency delta**: new packages, new versions, new postinstall
   scripts.

## Exit Criteria

- [ ] Every finding states input, path and effect, or it is downgraded to a note.
- [ ] Findings ranked by exploitability with severity.
- [ ] Zero `high`/`critical` findings unresolved before shipping.
- [ ] Patches proposed for everything above `low`.
- [ ] The dependency delta is reviewed.

## Common Failures

| Failure | Fix |
|---|---|
| Listing patterns without reachability | Trace the input or downgrade |
| Treating a linter finding as a vulnerability | Verify the path |
| Reviewing only new lines | Check what the change exposes, not just what it adds |
| Missing authorisation checks | For each new endpoint, ask who may call it |
| Ignoring the package delta | New dependencies are new attack surface |
| "Internal tool, no need" | Internal tools hold the credentials |
