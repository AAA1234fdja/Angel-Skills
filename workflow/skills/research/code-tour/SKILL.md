---
name: code-tour
description: Write a walkthrough that leads a reader through a real code path, anchored to files and lines that exist. Use when onboarding someone to one flow, when a change needs explaining in order, or when a diagram would be less useful than eight steps through the code.
metadata:
  origin: adapted · ECC · skills/code-tour
  category: research
  phase: document
  status: adopted
  version: 1
---

# Code Tour

A tour is not a summary of the repository; it is a route through it with a purpose.
The failure mode is a walkthrough that either points at nothing ("the service layer",
with no file) or points at everything ("read these twelve files"), and both leave the
reader where they started. A good tour has a reader, a question they arrive with, and
eight or fewer anchored steps that answer it.

## When to Use

- Onboarding someone to one flow, not to the repository.
- A change needs explaining in the order it happens.
- A reviewer will need context the diff cannot carry.
- After a refactor that moved the code everyone used to know where to find.

## When Not to Use

- Teaching the whole codebase: `codebase-onboarding` gets a person to a first change.
- Recording why a decision was made: `adr-writing`.
- A runbook for an operational procedure: `runbook-writing`.

## Procedure

1. **Name the reader and their question** before the first step: "a backend dev who
   needs to know where a refund is authorised". A tour without a reader is a table of
   contents.
2. **Pick the route as a sequence of decisions**, not of files: the request enters
   here, the decision to allow it happens here, the effect is written here.
3. **Anchor every step to a real location** — file and symbol, ideally a line. A step
   without an anchor is an instruction to search, which is where tours lose people.
4. **Keep it to eight steps.** Past eight, the reader is reading a book; split the
   tour or cut the steps that do not answer the question.
5. **Say what to notice at each step**, in one sentence: the guard, the surprising
   default, the thing that will bite. The anchor is where; this is why you stopped.
6. **Mark the branches you do not tour** and where they lead. A reader who wonders
   "what about the async path?" should find the answer in one line, not by exploring.
7. **Verify every anchor after the final edit** — the tour must be run, not written.
   Anchors rot faster than prose because they point at lines that move.
8. **Run `tour-check`** on the tour: it flags missing reader, too many steps, steps
   with no anchor, anchors whose file does not exist, and steps with nothing to notice.

## Exit Criteria

- [ ] The reader and their question are stated at the top.
- [ ] Every step is a decision in the flow, in the order it happens.
- [ ] Every step has a file (and symbol or line) anchor.
- [ ] Eight steps or fewer.
- [ ] Every step says what to notice, in one sentence.
- [ ] Untoured branches are marked with where they lead.
- [ ] Every anchor was verified after the last edit.
- [ ] `tour-check` reports no broken anchor and no unanchored step.

## Common Failures

| Failure | Fix |
|---|---|
| A tour of the repository | One flow, one reader, one question |
| "The service layer" as an anchor | File and symbol, or it is not an anchor |
| Twenty steps | Eight or fewer; split the tour instead |
| Steps that only say "read this" | Add what to notice in one sentence |
| Anchors never re-verified | Run the tour after editing; lines move |
| Hidden branches | Mark them and say where they lead |
