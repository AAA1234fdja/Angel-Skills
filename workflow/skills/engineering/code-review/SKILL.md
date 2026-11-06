---
name: code-review
description: Fresh-context review of a diff: real defects ranked by severity, a verdict at the end, and no redesign of the author's approach. Use when a change is ready for a pull request, arrives from someone else, or a task was closed green but something feels off.
metadata:
  origin: ECC · reviewer pattern (agents/code-reviewer)
  category: engineering
  phase: review
  status: adopted
  version: 1
---

# Code Review

The value of a review depends on the reviewer **not** being the author. An agent
reviewing its own context repeats its own blind spots, so this procedure runs on
the diff, with as little memory as possible of the conversation that produced it.

## When to Use

- Before opening or merging a pull request.
- When code arrives from another agent or person.
- When a task closed "green" but the result does not feel right.

## When Not to Use

- Before a diff exists: there is nothing to review.
- As a substitute for tests: review finds what tests do not cover, it does not
  replace running them (`verification-loop`).

## Procedure

1. **Read the whole diff first, commenting on nothing.** Understand the intent.
2. **Check the intent against the request.** Does it solve what was asked? Does it
   do something that was not asked?
3. **Label each finding**:
   - `blocking` — bug, data loss, exposed secret, contract break;
   - `important` — debt that will be paid soon, uncovered behaviour;
   - `minor` — style, naming, comments;
   - `question` — not a defect: context is missing.
4. **One comment per finding**, with the line and the reason. Do not redesign the
   author's approach inside a comment.
5. **Propose the minimal patch** only when it is obvious; otherwise state the
   condition that must hold.
6. **Close with a verdict**: approve, approve with minors, or request changes.
7. **Refuse a diff you cannot hold in your head**: ask for it to be split, and say where. "Reviewing" two thousand lines in ten minutes is approving, not reviewing.

## Exit Criteria

- [ ] Every finding has a severity and a line or file reference.
- [ ] Zero `blocking` findings unresolved before merge.
- [ ] An explicit verdict at the end — `diff-review` supplies the mechanical pass.
- [ ] Nothing commented that a linter or a test already covers.
- [ ] What is **missing** was reviewed too (absent tests, unhandled error).

## Common Failures

| Failure | Fix |
|---|---|
| Twenty "minor" notes and no verdict | Prioritise: blocking first, verdict last |
| Reviewing with the context that wrote the code | Fresh session, diff only |
| Rewriting the module in a comment | Name the defect and let the author decide |
| Approving "because tests pass" | Tests cover neither design nor security |
| Commenting style the formatter already fixes | Run the formatter |
| A 2000-line diff approved in minutes | Ask for a split; approval is not review |
