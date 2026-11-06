---
name: string-extraction
description: Pull the useful strings out of an artefact you cannot run: URLs, paths, keys, errors and formats, then decide which ones are evidence. Use when an artefact must be understood without executing it, when a binary's behaviour hints at a file or endpoint, or when a config is obfuscated.
metadata:
  origin: original
  category: reversing
  phase: research
  status: original
  version: 1
---

# String Extraction

Strings are the cheapest evidence in an artefact and the easiest to over-read. A
URL in a binary may be the update endpoint, a test fixture or a marketing link; a key
may be a public identifier. This procedure extracts them, groups them, and forces
each group to be tied to an observation before it becomes a claim.

## When to Use

- An artefact cannot be executed (wrong architecture, hostile, or a licence forbids it).
- A binary or blob hints at a file, endpoint, registry key or embedded config.
- A configuration is obfuscated and you need to know what it talks to.
- You need to decide whether an artefact is worth deeper reversing at all.

## When Not to Use

- You can run it in a sandbox: observe it first, strings are the fallback.
- The artefact is source code: read the source, do not grep the compiled form.
- You need a verdict on safety: strings suggest, they never prove.

## Procedure

1. **Record the artefact identity** first: path, size, checksum, and how it was
   obtained. A finding not tied to a hash cannot be reproduced.
2. **Extract printable runs** of at least four characters, in both ASCII and UTF-16.
   Run the `string-triage` tool on the extracted list; it groups by kind and drops
   noise rather than dumping ten thousand lines.
3. **Rank the groups by what they would prove**: endpoints and hosts, filesystem
   paths, registry keys, credentials-shaped strings, error formats, cryptography
   constants. A group with no testable consequence goes last.
4. **Tie every claim to an observation**: the offset or the section, plus what in the
   artefact's behaviour corroborates it. "The binary contacts X" needs a network
   observation, not a string.
5. **Distinguish hard-coded from generated**: a string repeated with a checksum, a
   base64 blob next to a decoder, a URL built from parts. Generated strings are
   usually more interesting than literals.
6. **Record negative findings.** "No TLS pinning string, no proxy config, no private
   key marker" is evidence a reviewer can use, and it is the part that gets lost.
7. **Stop at the boundary of the mandate**: extraction answers "what does it mention",
   not "what does it do". Anything stronger needs execution or a signature.

## Exit Criteria

- [ ] The artefact identity (path, size, checksum, provenance) is recorded.
- [ ] Strings are grouped by kind and the noise is discarded, not dumped.
- [ ] Every claim cites the group and the corroborating observation.
- [ ] Each credential-shaped hit is classified (public id, test fixture, or secret to report).
- [ ] Negative findings are recorded.
- [ ] `string-triage` reports no unclassified credential-shaped string.

## Common Failures

| Failure | Fix |
|---|---|
| Treating a URL as proof of contact | Corroborate with a network observation |
| Dumping 10k strings into a report | Group and rank; the reader needs evidence, not output |
| Reporting a public key id as a leak | Classify credentials-shaped hits before reporting |
| Comparing against the wrong architecture | Record the hash and the arch; strings differ per build |
| Ignoring UTF-16 | Windows binaries and JVM artefacts hide readable text there |
| No negative findings | State what is absent; absence is evidence too |
