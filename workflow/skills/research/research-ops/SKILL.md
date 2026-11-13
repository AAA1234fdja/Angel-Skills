---
name: research-ops
description: Run a research task as an operation with a question, a plan and a stop condition, instead of an open-ended browse. Use when a question needs several sources, when time is bounded, or when somebody will act on the answer and nobody agreed what "enough" means.
metadata:
  origin: adapted · ECC · skills/research-ops
  category: research
  phase: research
  status: adopted
  version: 1
---

# Research Ops

Research without a stop condition expands to fill the time available, and the last
twenty-percent usually changes nothing. The operational view is the opposite of the
scholarly one: fix the question, fix the budget, fix the evidence bar, and stop when
the bar is met — then say what confidence you have and what would change it. This is
the procedure around `sourced-answer`, which governs the shape of what you write.

## When to Use

- A question needs more than one source and someone will act on the answer.
- The time is bounded and the answer is needed today.
- A previous research effort produced a long document and no decision.
- Nobody agreed what evidence would be enough before starting.

## When Not to Use

- Writing up the answer itself: `sourced-answer` governs claims, dates and contradictions.
- Verifying something in the repository: `search-first` reads the code.
- Measuring rather than reading: `benchmark-discipline` produces the number.

## Procedure

1. **Fix the question and the decision it serves** in one sentence each. Research
   that cannot name the decision will not be read by the person who makes it.
2. **Set the evidence bar before searching**: what would a "yes" look like, what would
   a "no" look like, and what would be enough to say "I don't know yet". Without this,
   every extra source looks equally necessary.
3. **Plan the searches, cheapest and most authoritative first**: primary documentation,
   then the source or changelog, then reputable secondary sources, then communities.
4. **Time-box each phase** and record the timestamps. When a phase runs long, the note
   "budget exceeded here" is itself a finding about the question's difficulty.
5. **Stop at the bar, not at exhaustion.** Write down what you did not read: an
   explicit gap is honest; an implicit one reads as coverage.
6. **Record confidence per finding** — high when a primary source states it, medium
   when one secondary source does, low when it is inference from several.
7. **End with the decision, the gaps and what would change the answer.** That last
   line is how a later reader knows whether the research is still valid.
8. **Run `research-plan`** on the record: it flags a missing decision, a missing
   evidence bar, phases with no budget, findings with no confidence, and research that
   stopped with no stated gaps.

## Exit Criteria

- [ ] The question and the decision it serves are each one sentence.
- [ ] The evidence bar is written before the searches.
- [ ] Searches are ordered by authority and each phase is time-boxed.
- [ ] Confidence is recorded per finding.
- [ ] What was not read is listed as a gap.
- [ ] The record ends with the decision and what would change it.
- [ ] `research-plan` reports no missing bar and no finding without confidence.

## Common Failures

| Failure | Fix |
|---|---|
| Open-ended browsing | Fix the bar and stop when it is met |
| Research with no decision attached | Name the decision, or do not start |
| Every source weighted equally | Order by authority and record confidence |
| No time boxes | Timestamp each phase; overruns are findings |
| Implicit gaps | List what you did not read |
| Ending without "what would change this" | The answer has a shelf life; state it |
