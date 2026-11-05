---
name: error-taxonomy
description: Keep one error taxonomy and one policy table: every failure carries a stable code, a severity, an owner and a retry rule. Use when introducing error codes, when two modules name the same failure differently, or when the CLI needs stable exit codes.
metadata:
  origin: ECC · error-handling + safety-guard (pattern)
  category: engineering
  phase: implement
  status: adopted
  version: 1
---

# Error Taxonomy

One taxonomy, defined once, is what lets a caller branch on a failure, a CLI return
a stable exit code, and a human read a journal six months later.

## When to Use

- Introducing error codes in a codebase that only has messages.
- Two modules naming the same failure differently.
- A CLI or API needs stable exit codes or status mapping.
- Reviewing an error table before it hardens into a public contract.

## When Not to Use

- A single throwaway script: a message is enough.
- Language-native exceptions that already carry type and context and are consumed
  locally.

## Procedure

1. **Name the axes first**: severity (`info|warn|error|fatal`), owner
   (`user|author|caller|runtime|producer`), retryable (boolean), exit code.
2. **Assign codes by layer**, not by message: `E_REGISTRY_INVALID`, not
   `E_BAD_JSON`. Codes are stable; messages are for humans and may change.
3. **One code per decision.** If two codes always appear together, they are one.
4. **Every code gets a remediation hint.** A code without a hint forces the reader
   to read the source.
5. **Publish the table** where callers can see it (docs, help text, or a
   `--list` command) and keep it generated from the single source.
6. **Treat the table as a contract**: adding a code is minor, changing the meaning
   or exit code of an existing one is breaking (`schema-evolution`).

## Exit Criteria

- [ ] Every failure path uses a code from the table — no ad-hoc strings.
- [ ] Each code has severity, owner, retryable and exit code.
- [ ] Each code has a hint a reader can act on.
- [ ] `taxonomy-check` reports no duplicates, orphan severities or exit-code clashes.
- [ ] The published table is generated from the same source the code uses.

## Common Failures

| Failure | Fix |
|---|---|
| Codes named after messages | Name after the decision the caller makes |
| Two codes for the same condition | Merge and keep an alias in docs |
| Exit codes assigned ad hoc per command | Derive them from the table only |
| A `fatal` that the process can recover from | Severity describes the goal, not the mood |
| Retryable defaults to true "to be safe" | Retry only provably transient failures |
| Table in docs, codes in code, never reconciled | Generate docs from the table |
