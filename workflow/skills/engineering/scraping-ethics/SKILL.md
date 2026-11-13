---
name: scraping-ethics
description: Decide whether and how to collect data from a public source before writing the collector: terms, robots, rate, personal data and load on someone else's system. Use when building a scraper, when an agent will fetch at scale, or when someone points it at a site nobody asked permission from.
metadata:
  origin: adapted · ECC · skills/data-scraper-agent
  category: engineering
  phase: design
  status: adopted
  version: 1
---

# Scraping Ethics

Technically fetching a page is not the same as being allowed to. The decision is
made before the code exists, in five questions that are cheap to answer and expensive
to discover in a legal letter: may I, at what rate, whose data is it, does it break
their terms, and what do I do when they say stop. A collector that skips this section
is a liability that keeps running on a schedule.

## When to Use

- Building a collector for a site, an API or a dataset you do not own.
- An agent will fetch at volume, on a schedule, or through rotating identities.
- The data includes anything that could identify a person.
- Somebody asks to "just scrape it" and nobody has read the terms.

## When Not to Use

- Reading your own systems or a source you operate: `security-review` does not apply either, and the limits are internal.
- One manual fetch of a public page you are reading yourself: no collector, no policy.
- Licensing questions about a dependency: `dependency-audit` covers that.

## Procedure

1. **Read the terms and `robots.txt` and record what they say**, quoting the relevant
   line. "No explicit prohibition" is not permission; it is an unanswered question, and
   an unanswered question goes to a person, not to production.
2. **Prefer the official interface**: an API, a bulk export or a data licence. The
   cheapest legal path is almost always the documented one, and it is also more stable.
3. **Classify the data** before collecting: public facts, personal data, or special
   category. Personal data changes the obligations, retention and the right to be
   forgotten, and none of that is retrofittable.
4. **Set a rate and honour it**: a stated requests-per-second budget, a descriptive
   user agent with contact, and a stop when the source degrades. Load on someone else's
   system is the harm that gets noticed first.
5. **Do not evade controls**: no rotating proxies to defeat a block, no CAPTCHA
   solving, no login sharing. A block is an answer to the question you asked.
6. **Record the provenance of every record** — source URL, timestamp, terms version —
   so a later question about a specific row has an answer.
7. **Write the takedown path before the first run**: who reads a complaint, what is
   deleted, and how the schedule is stopped. It should be one command and one person.
8. **Run `scrape-policy`** on the plan: it refuses no terms review, no rate, personal
   data without a basis, evasion, and no takedown path.

## Exit Criteria

- [ ] Terms and `robots.txt` were read, with the relevant line recorded.
- [ ] The official interface was considered and its rejection justified.
- [ ] Data is classified, and personal data has a legal basis and a retention period.
- [ ] A rate budget and a descriptive user agent are set.
- [ ] No evasion of blocks, CAPTCHAs or logins.
- [ ] Provenance is recorded per record.
- [ ] The takedown path names a command and a person.
- [ ] `scrape-policy` refuses nothing.

## Common Failures

| Failure | Fix |
|---|---|
| "It's public, so it's allowed" | Public visibility is not a licence; read the terms |
| Ignoring `robots.txt` | Read it and record what it says |
| No rate limit | State requests per second and honour it |
| Rotating proxies around a block | A block is an answer; escalate to a person |
| Personal data with no basis | Classify first; it cannot be retrofitted |
| No takedown path | One command and one owner, written before the first run |
