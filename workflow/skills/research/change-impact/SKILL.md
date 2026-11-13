---
name: change-impact
description: Predict what a change will touch before making it, then compare the prediction with what actually moved. Use when a change crosses a boundary, when the blast radius is unknown, or after a change surprised everyone by breaking something unrelated.
metadata:
  origin: adapted · ECC · skills/change-impact
  category: research
  phase: plan
  status: adopted
  version: 1
---

# Change Impact

Every change has a predicted radius and an actual one, and the difference is where
the incidents live. The prediction does not have to be perfect to be valuable: it has
to be written down before the change, so that the surprise is visible instead of
absorbed. This procedure makes the prediction cheap and the comparison mandatory,
because an impact analysis nobody compares with reality is a ritual.

## When to Use

- The change crosses a module, a contract, a schema or a team boundary.
- Nobody can say from memory what depends on the thing being changed.
- A previous change broke something unrelated and nobody foresaw it.
- Before a migration, a rename of a published identifier, or a permission change.

## When Not to Use

- A change inside one function with its tests: the compiler is the analysis.
- Enumerating consumers of a module as a standing ledger: `regression-ledger` maintains it.
- Deciding whether the change is a good idea: `adr-writing` records that.

## Procedure

1. **State the change as a surface delta**: which published thing changes, and how
   (renamed, removed, narrowed, semantics). "Refactor" is not a delta.
2. **Enumerate the predicted reach** with search, not memory: importers, callers,
   config references, documentation, dashboards that query the field. Write the list
   down before touching anything.
3. **Predict the second-order effects**: what those consumers do when the change
   lands — fail to compile, silently misread, or degrade. The silent ones are the
   reason this procedure exists.
4. **Mark the irreversible part**, if any: a migration that wrote data, a message
   already consumed, a release already downloaded. That part needs a rehearsal.
5. **Make the change**, then diff the actual reach against the predicted one. Every
   file in the actual set that was not predicted is a gap in your model of the repo.
6. **Explain each surprise in one line**: a missed edge, a generated file, a dynamic
   import. An unexplained surprise will happen again in the next change.
7. **Feed the surprises into a guard** — a test, a lint rule or a ledger entry — so
   the same missed edge cannot surprise twice.
8. **Run `impact-diff`** on predicted versus actual: it reports the misses, the
   over-predictions and the ratio. A prediction that covered everything is usually
   over-prediction, and it trains people to ignore the analysis.

## Exit Criteria

- [ ] The change is stated as a surface delta.
- [ ] The predicted reach is written before the change, with the search used.
- [ ] Second-order effects are predicted per consumer, including the silent ones.
- [ ] Irreversible parts are marked and rehearsed.
- [ ] Actual reach diffed against the prediction after the change.
- [ ] Every surprise is explained in one line.
- [ ] `impact-diff` reports no unexplained miss and a sane over-prediction rate.

## Common Failures

| Failure | Fix |
|---|---|
| Prediction written after the change | Write it first; the value is in the gap |
| Reach enumerated from memory | Search: importers, configs, docs, dashboards |
| Only first-order effects | Predict what each consumer does when it lands |
| Over-predicting everything | Trains people to ignore the analysis; be specific |
| Surprises absorbed silently | One line each, or the next change repeats them |
| No guard from the surprise | Test, lint or ledger entry — otherwise you learned nothing |
