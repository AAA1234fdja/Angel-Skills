---
name: prototype-spike
description: Run a spike with a question, a timebox and a delete date, so a throwaway answers one unknown and leaves. Use when an estimate hides an unknown, a library choice needs evidence, or the team is arguing about feasibility instead of measuring it.
metadata:
  origin: original
  category: engineering
  phase: research
  status: original
  version: 1
---

# Prototype Spike

A spike is a question with a deadline. Without the question it becomes a
prototype someone ships; without the deadline it becomes the product. The whole
discipline is: write down what you are trying to learn, learn it in the cheapest
form that can be wrong, then throw the code away and keep the finding.

## When to Use

- An estimate contains "we think it will work" with nothing behind it.
- Two libraries or two designs need a measurement, not an opinion.
- A performance or integration risk is cheaper to test than to argue about.
- An unfamiliar API must be exercised before a plan can be written.

## When Not to Use

- The work is well understood: build it properly instead of twice.
- The question is a product decision, not a technical unknown.
- Nobody has agreed to the timebox: an unbounded spike is a rewrite.
- The answer can be found by reading the source or the docs for ten minutes.

## Procedure

1. **One question, in one sentence**, answerable by yes/no or by a number. If it
   needs an "and", it is two spikes.
2. **Set the box**: hours (not days), and what you will do when it runs out —
   answer anyway with what you have, or escalate. A spike without an exit clause
   is a commitment.
3. **Decide the delete date now.** The code will be deleted on a named date; the
   finding is the deliverable. Put the date in the folder name or the first line.
4. **Write the cheapest thing that can answer the question.** No auth, no error
   handling, no tests beyond the one that measures. Ugly here is a feature: it
   stops the spike from being adopted.
5. **Measure, do not demo.** Record the number or the observed behaviour with the
   command that produced it. A demo shows what works; the finding says what does
   not.
6. **Write the finding** in five lines: question, answer, evidence, what this
   changes in the plan, what remains unknown.
7. **Delete the code on the date.** If the finding is worth keeping, the
   production version is written properly — with tests — from the finding, not by
   promoting the spike.

## Exit Criteria

- [ ] The question is one sentence and was written before the code.
- [ ] The spike stayed inside its timebox, and the answer exists whether or not
      the code worked.
- [ ] The finding is five lines with the command and the number as evidence.
- [ ] The delete date is recorded, and the code is gone by it.
- [ ] The plan or the estimate was updated with the answer.

## Common Failures

| Failure | Fix |
|---|---|
| Spike becomes the implementation | Delete on the date; write the real version from the finding |
| Question written after the code | The code answered something else; write the question first |
| Demo instead of measurement | No number, no finding |
| Timebox "until it works" | Set the box before starting; the exit clause is part of the box |
| Finding in a chat thread | Five lines in the repo, next to the plan it changes |
| Several questions in one spike | Split: each question gets its own box and its own deletion |
