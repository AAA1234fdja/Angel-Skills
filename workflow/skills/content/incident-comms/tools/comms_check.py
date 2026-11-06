"""Comms check: did the incident get told, on a cadence, honestly?

Payload::

    {"incident": "checkout 500s", "channel": "#incident-checkout",
     "promised_cadence_minutes": 30,
     "messages": [{"at": "2026-11-05T10:00:00Z", "kind": "first",
                   "confirmed": ["card payments fail"], "unknown": ["cause"],
                   "next_update": "10:30", "eta": None},
                  {"at": "2026-11-05T10:34:00Z", "kind": "update",
                   "confirmed": ["vendor timeout"], "next_update": "11:00"},
                  {"at": "2026-11-05T11:05:00Z", "kind": "resolved",
                   "duration_minutes": 65, "residual": "none"}]}

The cadence is computed from the promised interval, not from good intentions: a
34-minute gap after a 30-minute promise is reported, because the promise is the
thing the reader is holding on to. An ETA is reported separately — promising a fix
time is the most common way a good response reads as a bad one.
"""

KINDS = ("first", "update", "resolved")


def _minutes(ts):
    """Minutes since midnight-ish: ISO timestamps compared lexically are enough here."""
    text = str(ts or "")
    try:
        hh = int(text[11:13])
        mm = int(text[14:16])
    except (ValueError, IndexError):
        return None
    return hh * 60 + mm


def run(payload):
    messages = payload.get("messages") or []
    cadence = payload.get("promised_cadence_minutes")
    problems, rows = [], []
    gaps = []
    previous = None

    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            problems.append(f"messages[{index}] is not an object")
            continue
        kind = str(message.get("kind") or "")
        if kind not in KINDS:
            problems.append(f"messages[{index}]: kind {kind!r} not one of {', '.join(KINDS)}")
        minute = _minutes(message.get("at"))
        if minute is None:
            problems.append(f"messages[{index}]: no usable timestamp")
        elif previous is not None:
            gaps.append(minute - previous)
        if minute is not None:
            previous = minute
        if kind in ("first", "update"):
            if not message.get("confirmed"):
                problems.append(f"messages[{index}]: states nothing confirmed")
            if not message.get("next_update"):
                problems.append(f"messages[{index}]: no next-update time: the reader "
                                "cannot tell if anyone is still working")
            if message.get("eta"):
                problems.append(f"messages[{index}]: promises an ETA; promise the next "
                                "update instead")
        if kind == "first" and not payload.get("channel"):
            problems.append("no channel of record: two sources become three versions")
        if kind == "resolved" and not message.get("duration_minutes"):
            problems.append(f"messages[{index}]: resolved without a duration")
        rows.append({"kind": kind, "at": message.get("at"),
                     "confirmed": len(message.get("confirmed") or [])})

    if not messages:
        problems.append("no messages: silence is read as incompetence")
    elif not any(m.get("kind") == "first" for m in messages if isinstance(m, dict)):
        problems.append("no first notice")
    if messages and not any(m.get("kind") == "resolved" for m in messages
                            if isinstance(m, dict)):
        problems.append("no closing message: the incident never ends for the reader")
    if isinstance(cadence, (int, float)) and cadence > 0:
        late = [g for g in gaps if g > cadence]
        if late:
            problems.append(f"{len(late)} update gap(s) exceeded the promised "
                            f"{cadence:g} minutes (largest {max(late)}m)")
    elif messages:
        problems.append("no promised cadence: readers have no idea when to look again")

    return {
        "ok": not problems,
        "messages": len(rows),
        "gaps_minutes": gaps,
        "promised_cadence": cadence,
        "problems": problems,
        "advice": ("impact was told on a kept cadence, with an explicit close"
                   if not problems else "; ".join(problems[:3])),
    }
