---
name: threat-model
description: Model what can go wrong before it is built: assets, trust boundaries, STRIDE coverage and the mitigation each threat needs. Use when a design adds an entry point or a permission, when data crosses a boundary it did not cross before, or when a security review has to start somewhere other than a blank page.
metadata:
  origin: original
  category: security
  phase: design
  status: original
  version: 1
---

# Threat Model

`security-review` looks at code that exists. A threat model looks at a design that
does not, when changing it is still cheap. It is a short, boring document: what we
protect, where the boundary is, what could go wrong at that boundary, and what we
decided to do about each thing. Written after the incident, it is called a
postmortem.

## When to Use

- A design adds an entry point, a permission, a queue or a trust boundary.
- Data moves somewhere it did not move before (new region, new vendor, new cache).
- A feature lets one tenant, user or agent act on another's resources.
- An existing component is exposed to a network it was not written for.

## When Not to Use

- Reviewing code for known bug classes: use `security-review`.
- Scanning for committed secrets: use `secret-scan`.
- A model of the whole company: that is a programme, not a design review. One
  boundary per session.

## Procedure

1. **List the assets** in one line each, with the harm if they leak or change:
   credentials, personal data, money, availability, integrity of a decision.
2. **Draw the boundaries**: browser → API, service → service, service → datastore,
   agent → tool, vendor → us. A boundary is anywhere the level of trust changes.
3. **Walk STRIDE over each boundary**, not over the system: spoofing, tampering,
   repudiation, information disclosure, denial of service, elevation of privilege.
   Most cells are empty; the empty cells are the point — they show what was
   considered.
4. **Score only the threats that survived**: likelihood and impact, high/medium/
   low. A threat without a score becomes a wish.
5. **Decide per threat**: mitigate (with the mechanism), accept (with the owner),
   transfer (with the contract), or eliminate (remove the feature). "Note it in
   the backlog" is acceptance without an owner and does not count.
6. **Run the `threat-coverage` tool** on the filled matrix. It reports which
   STRIDE categories have no entry at all — usually the honest finding of the
   session.
7. **Re-run the model when the boundary changes**, not on a calendar. A stale
   threat model is worse than none: it says "we thought about it" about a design
   that no longer exists.

## Exit Criteria

- [ ] Assets are listed with the harm if they leak or change.
- [ ] Every trust boundary is named, and every boundary has been walked through
      all six STRIDE categories (empty is fine, unvisited is not).
- [ ] Every surviving threat has a decision and, when mitigated, a named mechanism.
- [ ] Every accepted threat has an owner.
- [ ] `threat-coverage` reports no unvisited category for a boundary that changed.
- [ ] The model is dated and tied to the design version it describes.

## Common Failures

| Failure | Fix |
|---|---|
| Threat model of "the system" | One session per boundary; the whole thing is unactionable |
| Only listing threats you already mitigate | Walk all six categories and record the empty ones |
| "Accepted" with no owner | Acceptance is a person's decision, not a mood |
| Model written after implementation | You will rationalise what was built; model the design |
| Never revisited | Tie it to the design version; re-run when the boundary moves |
| Confusing threat with vulnerability | A threat is possible harm; a vulnerability is a way it happens now |
