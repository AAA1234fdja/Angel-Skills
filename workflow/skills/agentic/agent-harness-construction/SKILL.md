---
name: agent-harness-construction
description: Design action space, tool granularity, observation format and context budget so an agent finishes more tasks. Use when defining or revising an agent's tool set, its observation format, or why it keeps failing halfway.
metadata:
  origin: ECC · skills/agent-harness-construction
  category: agentic
  phase: plan
  status: adopted
  version: 1
---

# Agent Harness Construction

An agent's quality is not decided only by the model. It is decided by four things
you can design — action space, observation, recovery and context budget — and this
procedure designs them in that order.

## When to Use

- Defining the tool set of a new agent.
- An agent fails at tasks it "should" be able to do.
- Reviewing why an agent repeats calls, picks the wrong tool, or runs out of
  context halfway.

## When Not to Use

- When the problem is tone or persona: that is another layer.
- When there is no way to measure completion (`eval-harness` first).

## Procedure

1. **Define "task completed"** before designing tools. Without success criteria
   the design is not verifiable.
2. **Action space**: stable explicit names, schema-first narrow inputs,
   deterministic output shapes. No catch-all tool unless isolation is impossible.
3. **Granularity by risk**:
   - micro-tool for high-impact operations (deploy, migrate, permissions): one
     step, one effect, explicit confirmation;
   - medium tool for read/edit/search loops;
   - macro-tool only when round trips dominate the cost.
4. **Observation**: every tool response returns `status`
   (`success|warning|error`), a one-line `summary`, `next_actions` and `artifacts`.
   An observation without a next step leaves the agent guessing.
5. **Recovery contract**: every error path carries a root-cause hint, a safe retry
   and an explicit stop condition.
6. **Context budget**: minimal invariant system prompt; long guidance in skills
   loaded on demand; references to files over inlined documents; compact at phase
   boundaries, not at token thresholds.
7. **Measure**: completion rate, retries per task, pass@1 and pass@3, cost per
   completed task. Without those five numbers there is no demonstrable improvement.

## Exit Criteria

- [ ] "Task completed" is written down and checkable.
- [ ] Every tool has a documented input schema and output shape.
- [ ] Every tool returns the four observation fields.
- [ ] Every error path has safe retry and a stop condition.
- [ ] No guidance in the system prompt that could live in a skill.
- [ ] The five metrics were measured before and after the change.

## Common Failures

| Failure | Fix |
|---|---|
| Many tools with overlapping semantics | The agent picks wrong: merge or remove |
| Opaque output ("something failed") | `status` + `summary` + `next_actions` |
| A deploy tool that does three things | Split into confirmed steps |
| Whole style guide in the system prompt | Skill loaded on demand |
| Compacting at a fixed token count | Compact at phase boundaries |
| Adding tools without remeasuring | Every change measured like the baseline |
