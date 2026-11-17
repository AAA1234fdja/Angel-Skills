---
name: kill-switch
description: Give an autonomous system a way to be stopped by a person who did not build it: one switch, one owner, one test. Use when an agent can act without approval, when a loop can spend money or touch production, or after an incident where stopping took longer than starting.
metadata:
  origin: original
  category: agentic
  phase: implement
  status: original
  version: 1
---

# Kill Switch

An autonomous loop you cannot stop is not autonomous, it is unsupervised. The
switch is a design requirement, not an operational nicety: it has to exist before the
loop does, be reachable by someone who did not write it, and be tested often enough
that nobody discovers it is broken during an incident.

## When to Use

- An agent acts without per-action approval, or runs unattended on a schedule.
- A loop can spend money, write to production, send messages or open PRs.
- An incident took longer to stop than to start.
- A new integration gives an agent a capability it did not have before.

## When Not to Use

- A tool that only reads and cannot cause an external effect: no switch needed.
- Emergency stops for infrastructure: that is the platform's job, not this skill's.
- Deciding whether to grant the capability: that is `agent-harness-construction`.

## Procedure

1. **One switch per capability**, named so a responder can find it: a flag, an
   endpoint, a queue pause. Two switches for one loop means nobody knows which one
   stops it.
2. **Stopping is the safe state.** The default after a stop must be "no further
   actions"; a switch that leaves work queued is a pause, not a stop, and say which
   one it is.
3. **Reachable without the system**: a flag in a console, a file, a command. If
   flipping it requires a successful deploy, it does not exist.
4. **Name the owner and the permission**: who may stop it, and who may restart it.
   Restart after a stop is a new decision, not a reflex.
5. **Test the switch on a schedule**, in production, at a moment when the loop is
   idle. An untested switch is a belief.
6. **Record what a stop does in flight**: does it abort the current action, let it
   finish, or leave a half-written state? The answer must be known before it is used.
7. **Run the `kill-switch-audit` tool** on the switch description: it flags missing
   owner, missing safe state, switch only reachable by deploy, and no test date.

## Exit Criteria

- [ ] One switch exists per autonomous capability, with a findable name.
- [ ] The safe state after a stop is stated (and it is "no further actions").
- [ ] A person without deploy rights can flip it.
- [ ] Stopping and restarting each have a named owner.
- [ ] The in-flight behaviour of a stop is documented.
- [ ] The switch was tested in production within the last quarter.
- [ ] `kill-switch-audit` reports no missing owner, safe state or test date.

## Common Failures

| Failure | Fix |
|---|---|
| Switch only reachable by deploying | Expose a flag or a command that works without a deploy |
| Switch that pauses but leaves the queue | Say it is a pause, or drain the queue on stop |
| Nobody knows who may restart | Name both owners explicitly |
| Untested switch | Schedule a stop-and-restart while idle, quarterly |
| Stopping leaves half-written state | Document in-flight behaviour, and make the stop idempotent |
| Two switches, ambiguous precedence | One per capability; if you need two, document the order |
