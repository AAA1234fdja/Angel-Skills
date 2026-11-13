---
name: sourced-answer
description: Answer a factual question so a reader can check it: one source per claim, the date it was read, and the contradictions stated instead of smoothed. Use when the answer will drive a decision, when the sources may have moved since training, or when two documents disagree.
metadata:
  origin: original
  category: research
  phase: research
  status: original
  version: 1
---

# Sourced Answer

An answer without a source is a memory with a confident tone. The failure is not
being wrong — it is being uncheckable, so nobody can tell whether you were right.
This procedure is about the shape of an answer that survives review: every claim
points at where it came from and when, contradictions are surfaced rather than
averaged, and the recommendation is separated from the evidence that supports it.

## When to Use

- The answer feeds a decision somebody will act on.
- The topic may have changed since training: versions, prices, APIs, regulations.
- Two sources disagree and someone needs to know which to trust.
- A claim is being repeated internally and nobody remembers its origin.

## When Not to Use

- Deciding whether a pattern exists in this repository: `search-first` reads the code.
- The question is "which of these two designs is better": `adr-writing` records the choice.
- Comparing measured performance rather than reading about it: `benchmark-discipline`.

## Procedure

1. **Restate the question as a decision**, because "what is X" almost always means
   "should we do Y". The restatement decides which facts matter and which are trivia.
2. **Plan the sub-questions** — three to six — each of which can be answered by a
   source. A question with no sub-questions is a search term, not research.
3. **Prefer primary sources** and record for each: publisher, date, URL or path, and
   the exact claim it supports. A source that supports "roughly" supports nothing.
4. **Record the date you read it**, distinct from the date it was published. Both
   matter, and only one of them tells you whether it may have moved since.
5. **Surface contradictions explicitly**: what each side says, what would settle it,
   and what you did with the disagreement. Averaging two sources is inventing a third.
6. **Separate evidence from inference** and label the inference. "The docs say X" and
   "therefore Y for us" are different sentences with different confidence.
7. **Write the recommendation with its condition**: under what circumstance it holds
   and what would change it. An unconditional recommendation hides the assumption.
8. **Run `source-audit`** on the draft: it flags claims with no source, sources with
   no date, sub-questions with no evidence, unresolved contradictions and unsourced
   numbers — the last being where most fabricated precision lives.

## Exit Criteria

- [ ] The question is restated as a decision, with the sub-questions listed.
- [ ] Every claim names a source with publisher and date.
- [ ] Every source records when it was read, not only when it was published.
- [ ] Contradictions are stated with what would settle them.
- [ ] Inference is labelled and kept separate from evidence.
- [ ] The recommendation states the condition under which it holds.
- [ ] `source-audit` reports no unsourced claim and no undated source.

## Common Failures

| Failure | Fix |
|---|---|
| Confident answer with no sources | One source per claim, or mark it as your inference |
| Averaging two disagreeing sources | State both and what would settle it |
| Source with no date | Date published and date read; both change the meaning |
| A number with no origin | Numbers need sources more than prose does |
| Recommendation with no condition | Say what has to be true for it to hold |
| Research that answers the literal question | Restate it as the decision behind it |
