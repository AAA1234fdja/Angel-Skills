"""Source audit: can a reader check this answer?

Payload::

    {"question": "should we move to Postgres 17",
     "decision": "choose the database version for the 2027 migration",
     "sub_questions": ["is 17 supported by our host", "what breaks in our extensions"],
     "claims": [{"text": "17 is GA on the host", "source": "host docs",
                 "published": "2026-09-01", "read": "2026-11-04",
                 "kind": "evidence"},
                {"text": "extensions will work unchanged", "source": "",
                 "kind": "inference"},
                {"text": "it is about 30% faster", "source": "blog",
                 "published": "", "read": "2026-11-04", "kind": "evidence"}],
     "contradictions": [{"topic": "extension support", "a": "host docs", "b": "forum",
                         "would_settle": "run the extension suite on 17"}]}

An inference without a source is fine if it is labelled; an evidence claim without
one is a fabrication risk. Undated sources and unsourced numbers are the two shapes
that survive review and then collapse in use.
"""

LABELS = {"evidence", "inference", "opinion"}


def run(payload):
    claims = [c for c in (payload.get("claims") or []) if isinstance(c, dict)]
    subs = [str(s) for s in (payload.get("sub_questions") or [])]
    contradictions = [c for c in (payload.get("contradictions") or [])
                      if isinstance(c, dict)]
    problems, unsourced, undated, numbers = [], [], [], []

    if not str(payload.get("decision") or "").strip():
        problems.append("no decision named: the answer will be trivia nobody uses")
    if not subs:
        problems.append("no sub-questions: this is a search term, not research")
    if not claims:
        problems.append("no claims: there is nothing to check")

    for index, claim in enumerate(claims):
        text = str(claim.get("text") or "").strip()
        label = f"claims[{index}]"
        if not text:
            problems.append(f"{label}: empty claim")
            continue
        kind = str(claim.get("kind") or "").strip().lower()
        if kind not in LABELS:
            problems.append(f"{label}: kind '{kind or '?'}' is not one of "
                            + "/".join(sorted(LABELS)))
        source = str(claim.get("source") or "").strip()
        if kind != "inference" and not source:
            unsourced.append(text[:60])
        if source:
            if not str(claim.get("published") or "").strip():
                undated.append(f"{text[:40]}: no publication date")
            if not str(claim.get("read") or "").strip():
                undated.append(f"{text[:40]}: read on no date")
        if any(ch.isdigit() for ch in text) and not source and kind != "inference":
            numbers.append(text[:60])

    if unsourced:
        problems.append(f"{len(unsourced)} claim(s) without a source: "
                        + "; ".join(unsourced[:3]))
    if undated:
        problems.append(f"{len(undated)} source(s) undated: " + "; ".join(undated[:3]))
    if numbers:
        problems.append("unsourced numbers: " + "; ".join(numbers[:2]))
    for index, item in enumerate(contradictions):
        if not str(item.get("would_settle") or "").strip():
            problems.append(f"contradictions[{index}]: no way to settle it, so it will "
                            "be decided by whoever argues loudest")

    return {
        "ok": not problems,
        "decision": payload.get("decision"),
        "claims": len(claims),
        "sourced": sum(1 for c in claims if str(c.get("source") or "").strip()),
        "inferences": sum(1 for c in claims
                          if str(c.get("kind") or "").lower() == "inference"),
        "sub_questions": len(subs),
        "contradictions": len(contradictions),
        "unsourced": unsourced,
        "undated": undated,
        "problems": problems,
        "advice": ("each claim is checkable and disagreements are surfaced"
                   if not problems else "; ".join(problems[:3])),
    }
