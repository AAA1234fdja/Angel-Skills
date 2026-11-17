---
name: harness-context-profiles
description: Give one harness several working modes — build, review, research — each with its own instructions, without duplicating the skills underneath. Use when the same runtime needs different behaviour per phase, or when one always-on instruction file has grown to serve every case and serves none.
metadata:
  origin: adapted · ECC · contexts/, .cursor/, .kiro/
  category: harness
  phase: design
  status: adopted
  version: 1
---

# Harness Context Profiles

One instruction file that must serve planning, building and reviewing ends up being
read by nobody: the reviewer skims the build rules, the builder skips the review
rules, and the file grows every time somebody is annoyed. A profile is the smallest
unit of mode: instructions, allowed tools, and a definition of done — layered on top
of shared skills that do not get copied per mode. The failure to avoid is profile
divergence: three copies of the same rule that drift apart within a month.

## When to Use

- The same harness needs different behaviour per phase (build / review / research).
- An always-on instruction file has grown to serve every case.
- Different risk appetites per mode: research may read broadly, build may not.
- Adopting a runtime whose adapters want one config per environment.

## When Not to Use

- Splitting one profile into two that share 90% of their content: that is divergence.
- Deciding what the agent may reach at all: that is `harness-inventory`.
- Compacting a single long session: that is `context-budget`.

## Procedure

1. **Define the modes by decision, not by persona**: build decides implementation,
   review decides admissibility, research decides direction. A mode with no distinct
   decision does not deserve a profile.
2. **Keep shared rules in exactly one place** and reference them from every profile.
   Three copies of "never force-push" is three copies that will diverge.
3. **State per profile**: the instructions that differ, the tools it may use, the
   definition of done, and what it must hand over to the next mode.
4. **Make the handover between modes explicit**: review receives the diff, the intent
   and the evidence, not the whole session. That handover is where context profiles
   earn their keep.
5. **Bound each profile's loaded context**: a profile that loads everything is an
   always-on prompt with a new name.
6. **Write the switching rule**: who or what switches mode, and what happens to work in
   flight. A mode switch that silently abandons a half-built plan is worse than none.
7. **Run `profile-check`** on the profile set: it flags duplicated rules, profiles with
   no distinct decision, missing handovers, unbounded context and missing switch rules.
8. **Review the set as one artefact**, not profile by profile: divergence is invisible
   in a single file and obvious side by side.

## Exit Criteria

- [ ] Each profile names the decision it owns, distinct from the others.
- [ ] Shared rules live in one place and are referenced, not copied.
- [ ] Each profile states its tools, its definition of done and its handover.
- [ ] Each profile has a bounded set of context it loads.
- [ ] The switching rule is written, including what happens to work in flight.
- [ ] The set was reviewed side by side for divergence.
- [ ] `profile-check` reports no duplicated rule and no profile without a decision.

## Common Failures

| Failure | Fix |
|---|---|
| One profile per persona | Define modes by the decision they own |
| Copying rules into each profile | Reference a single shared block |
| Handover = "the whole session" | Hand over the diff, the intent and the evidence |
| Profile that loads everything | Bound it; otherwise it is an always-on prompt |
| No switching rule | State who switches, and what happens to in-flight work |
| Reviewing profiles one at a time | Review the set; divergence shows up side by side |
