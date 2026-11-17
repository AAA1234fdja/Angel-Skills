---
name: reverse-engineering
description: Recover the behaviour of an unknown system from artefacts: static triage, dynamic observation, protocol reconstruction and a written report. Use when there is a binary, a capture or an undocumented service whose behaviour must be understood before building on top of it.
metadata:
  origin: ECC · osint-investigation (method) + repo-scan
  category: reversing
  phase: research
  status: adopted
  version: 1
---

# Reverse Engineering

Reconstructing what a system does is an evidence discipline, not a guessing game.
Every claim must be tied to an artefact — an offset, a string, a packet — or it is a
hypothesis and must be labelled as one.

## When to Use

- An undocumented binary, service or file format must be understood.
- Captured traffic has to become a spec.
- A third-party client has to be reimplemented or interoperated with.

## When Not to Use

- Source is available: read it, do not reverse it.
- The licence or the law forbids it: check first and document the basis.
- Source is available: `code-review`, because reversing what you can read is guesswork with extra steps.

## Procedure

1. **Define the question** the investigation must answer. "Understand the app" is
   not a question; "what does this endpoint require to authenticate" is.
2. **Static triage first, never execute an unknown artefact** outside an isolated
   environment. Type, architecture, strings, imports, packing signals.
3. **Form hypotheses from artefacts**, each written with the artefact that supports
   it: `offset 0x1f40`, `string "X-Sig"`, `packet 12`.
4. **Dynamic observation in a sandbox**: run with logging of file, network and
   process activity. Note what the artefact *does*, not what it says.
5. **Reconstruct the protocol** from captured traffic: fields, ordering, encoding,
   signatures, error paths.
6. **Validate by replay**: reimplement the minimum client and reproduce an observed
   exchange byte-for-byte (or semantically, when bytes vary).
7. **Write the report**: question, artefacts, method, findings with confidence
   levels, and what remains unknown.

## Exit Criteria

- [ ] The question the investigation answered is written down.
- [ ] Every finding cites an artefact (offset, string, packet, hash).
- [ ] Confidence is stated per finding: confirmed, probable or hypothesis.
- [ ] Nothing was executed outside an isolated environment.
- [ ] The reconstruction is validated by replaying an observed exchange.
- [ ] Unknowns are listed, not silently omitted.

## Common Failures

| Failure | Fix |
|---|---|
| Executing an unknown sample to "see what happens" | Static first, sandbox always |
| Findings without artefacts | Cite offset, string or packet, or mark as hypothesis |
| Reimplementation never replayed | Validate against captured traffic |
| Reporting only what worked | List unknowns and dead ends |
| Ignoring licensing | Document the legal basis before starting |
| One sample as the whole truth | Multiple samples reveal optional paths |
