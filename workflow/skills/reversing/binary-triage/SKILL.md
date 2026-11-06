---
name: binary-triage
description: First pass on an unknown binary: type, architecture, strings, imports and packing signals, without executing it. Use when a sample arrives and the question is what it is before anything else happens.
metadata:
  origin: ECC · security-bounty-hunter (triage pattern)
  category: reversing
  phase: research
  status: adopted
  version: 1
---

# Binary Triage

Triage answers three questions in order: what is it, what could it do, and what
should happen next. It never executes the sample, and it never skips the boring step
of reading the header.

## When to Use

- An unknown file arrives and must be classified before use.
- A dependency ships a native binary.
- Reviewing a sample before deciding whether it deserves deeper analysis.

## When Not to Use

- Source is available: read it.
- Full reverse engineering is the goal: triage is the first step, not the work.
- Source is available: `code-review` reads it without guessing from a binary.

## Procedure

1. **Hash it** (sha256) and record the hash in every note that follows.
2. **Identify the container and architecture** from the header; note unusual
   sections, entry point and timestamps.
3. **Extract strings** and separate four kinds: boilerplate, libraries, paths and
   URLs, suspicious (obfuscated, encoded, base64 blobs).
4. **List imports and symbols**: which capabilities are reachable (network, file,
   process, registry, crypto, anti-debug).
5. **Look for packing**: high entropy sections, tiny import table, known packer
   markers, writable+executable sections.
6. **Score the risk indicators** and write the next step: discard, deeper static
   analysis, sandboxed dynamic analysis, or escalate.
7. **Record what is unknown** — a triage that claims certainty is a bad triage.

## Exit Criteria

- [ ] SHA-256 recorded.
- [ ] Container, architecture and entry point identified.
- [ ] Strings categorised, not dumped.
- [ ] Capabilities inferred from imports, listed explicitly.
- [ ] Packing assessed with evidence.
- [ ] A next step is named and the unknowns are listed.

## Common Failures

| Failure | Fix |
|---|---|
| Running the sample "just to check" | Static triage never executes |
| Dumping 20k strings | Categorise and count |
| Ignoring entropy | Packed files look boring until you measure |
| No hash in the report | The analysis cannot be referenced later |
| Claiming it is benign without evidence | List the unknowns; say "no indicators found" |
| Triage with no recommendation | End with discard, static, dynamic or escalate |
