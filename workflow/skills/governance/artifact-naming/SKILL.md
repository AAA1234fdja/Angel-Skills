---
name: artifact-naming
description: Name files, folders, versions and release artefacts so a stranger can find and trust them. Use when a build produces something consumers download, when two files claim to be the latest, or when an artefact has to be traced back to the commit that made it.
metadata:
  origin: original
  category: governance
  phase: document
  status: original
  version: 1
---

# Artifact Naming

An artefact is anything somebody else has to find later: a build, a document, a
schema, a dump, a release. Its name is an interface. `final_v2_REAL.zip` is not a
name; it is a question. This procedure fixes the scheme once, so nothing depends on
who was on call the day it was produced.

## When to Use

- A build, document or dataset is produced by a pipeline and consumed by others.
- Two artefacts claim to be the current version.
- An artefact must be traced back to the commit, date and job that produced it.
- A folder is becoming a museum of dates and initials.

## When Not to Use

- Local scratch files that never leave the machine.
- Names inside source code: those follow the language's convention, not this one.
- Renaming a large archive whose consumers already link to it — that is a migration.
- Identifiers inside source code: `coding-standards` governs those, and local scratch files need no rule.

## Procedure

1. **Fix the fields before the separator**: subject, qualifier, version, date,
   extension. Version is `x.y.z` and monotonic; a date is ISO-8601 `YYYY-MM-DD`.
   Nothing else is allowed past the version.
2. **Lowercase, hyphens, no spaces, no accents**, ASCII only. Tools split on
   underscores, shells eat spaces, and case-insensitive filesystems merge names.
3. **Never encode status in the name**: no `final`, `new`, `latest`, `v2-real`.
   Status is metadata; the artefact with the highest version and a recorded date is
   the current one.
4. **Point at the source**: the name carries the version, and the provenance record
   (commit, job id, date, checksum) lives next to it. A name alone cannot be traced.
5. **Separate the scheme from the content**: renaming is a new artefact with a new
   record, not a `mv` that breaks every link to the old one.
6. **Run the `name-audit` tool** on the list: it flags status words, non-ISO dates,
   characters that break tools, and two artefacts with the same version.
7. **Publish the scheme once** where producers can read it. A naming convention that
   lives in a review comment is applied only to the files reviewed that day.

## Exit Criteria

- [ ] Every artefact name follows subject-qualifier-version-date.
- [ ] No status word (`final`, `latest`, `new`, `copy`) appears in a name.
- [ ] Dates are ISO-8601 and versions are monotonic `x.y.z`.
- [ ] Every published artefact has a provenance record with commit and checksum.
- [ ] `name-audit` reports no status word, no duplicate version and no bad character.
- [ ] The scheme is written where producers can read it.

## Common Failures

| Failure | Fix |
|---|---|
| `report_final_v2.pdf` | `report-quarterly-1.2.0-2026-11-05.pdf` |
| `latest.zip` that is not the latest | The highest version is the latest; status is metadata |
| Renaming a published artefact | Publish a new one with a record; do not move the old |
| Underscores and mixed case | Lowercase and hyphens; tools and filesystems disagree otherwise |
| Version without provenance | Record commit, job and checksum next to the artefact |
| Scheme in a review comment | Write it where producers read it |
