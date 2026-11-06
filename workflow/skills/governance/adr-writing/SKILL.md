---
name: adr-writing
description: Record a decision with its context, the options rejected and what would reverse it. Use when a choice will be expensive to undo, when the same debate returns every few months, when a new team member asks why it is like this, or before a refactor that assumes the decision.
metadata:
  origin: original
  category: governance
  phase: document
  status: original
  version: 1
---

# ADR Writing

A decision without a record becomes folklore: everyone knows the rule, nobody knows
why, and it survives long after the reason expired. An Architecture Decision Record
is one page — context, decision, the options that lost, and the condition that would
reverse it — kept next to the code and dated. The value is not the document; it is
that writing it forces the alternatives to be named.

## When to Use

- A choice is expensive to undo: a datastore, a protocol, a public surface, a
  vendor, a module boundary.
- The same argument returns every few months with the same outcome.
- A newcomer asks why something is the way it is, and the answer is "we always did".
- A refactor is about to assume a decision nobody has written down.

## When Not to Use

- Reversible-in-an-hour choices: the cost of the record exceeds the decision.
- Style conventions the linter enforces: the rule is the record.
- A decision already made elsewhere and merely relayed: link to that record.

## Procedure

1. **Write the context as facts**, not preferences: constraints, forces, numbers,
   deadlines. If a number is unknown, say it is unknown — that is the most useful
   sentence in many ADRs.
2. **State the decision in one sentence, in the active voice**, and date it. "We
   will store sessions in Redis" beats a paragraph that describes Redis.
3. **List the options considered**, including the one you rejected and the status
   quo. An ADR with one option is a press release.
4. **Give the reason each option lost** in one line. This is the part that stops the
   debate returning: the next person can check whether the reason still holds.
5. **State the consequences**, good and bad, including what becomes harder. An ADR
   that lists only benefits is marketing, and it will be reopened.
6. **Name the reversal condition**: the observable fact that would make this decision
   wrong (a cost threshold, a latency, a team size). A decision with no reversal
   condition is a belief.
7. **Run the `adr-check` tool** over the record; it flags the missing option, the
   missing consequence and the missing reversal condition.
8. **Supersede, never rewrite.** A new decision is a new ADR that marks the old one
   superseded; editing history defeats the purpose.

## Exit Criteria

- [ ] Context states the forces and the numbers, with unknowns marked as unknown.
- [ ] The decision is one sentence in the active voice, dated.
- [ ] At least two options are listed, including the status quo.
- [ ] Each rejected option has the reason it lost.
- [ ] Consequences include what becomes harder.
- [ ] A reversal condition is stated in observable terms.
- [ ] `adr-check` reports no missing section.

## Common Failures

| Failure | Fix |
|---|---|
| ADR written after the fact as justification | Write it before, or mark it clearly as retroactive |
| One option, dressed as analysis | List the status quo at minimum |
| Only benefits listed | State what becomes harder; that is the reviewable part |
| No reversal condition | Name the observable fact that would reopen it |
| Editing a published ADR | Supersede it with a new one |
| ADR in a chat thread | Keep it in the repo next to the code it governs |
