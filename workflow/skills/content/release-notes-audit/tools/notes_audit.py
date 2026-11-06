"""Notes audit: do the release notes describe what shipped?

Payload::

    {"version": "2.4.0",
     "changes": [{"id": "c1", "surface": "api", "breaking": true},
                 {"id": "c2", "surface": "cli", "breaking": false}],
     "notes": [{"text": "removed the v1 token endpoint", "kind": "breaking",
                "change": "c1", "action": "migrate to /v2/token"},
               {"text": "announcing dark mode!", "kind": "added", "change": "c9",
                "flag": "dark_mode", "flag_enabled": false},
               {"text": "improvements", "kind": "changed", "change": ""}],
     "audience": "library consumers"}

A note with no linked change cannot be verified; a breaking note with no required
action cannot be acted on; and announcing work behind a disabled flag is the most
expensive kind of accuracy, because it is accurate about the wrong release.
"""

KINDS = {"breaking", "added", "changed", "fixed", "removed"}


def run(payload):
    changes = {str(c.get("id")): c for c in (payload.get("changes") or [])
               if isinstance(c, dict)}
    notes = [n for n in (payload.get("notes") or []) if isinstance(n, dict)]
    problems, unlinked, flag_off = [], [], []

    if not str(payload.get("version") or "").strip():
        problems.append("no version: notes without a version are a blog post")
    if not notes:
        problems.append("no notes: the release ships undocumented")

    for index, note in enumerate(notes):
        text = str(note.get("text") or "").strip()
        label = f"notes[{index}]"
        if not text:
            problems.append(f"{label}: empty note")
        kind = str(note.get("kind") or "").strip().lower()
        if kind not in KINDS:
            problems.append(f"{label}: kind '{kind or '?'}' is not one of "
                            + "/".join(sorted(KINDS)))
        change_id = str(note.get("change") or "").strip()
        if not change_id:
            unlinked.append(label)
        elif change_id not in changes:
            problems.append(f"{label}: links to unknown change '{change_id}'")
        if kind == "breaking":
            base = changes.get(change_id) or {}
            if not base.get("breaking"):
                problems.append(f"{label}: labelled breaking but the change is not")
            if not str(note.get("action") or "").strip():
                problems.append(f"{label}: breaking note with no required action")
        if note.get("flag") and note.get("flag_enabled") is not True:
            flag_off.append(f"{label}: '{note.get('flag')}' is off by default")
        if len(text.split()) <= 2:
            problems.append(f"{label}: '{text}' tells a reader nothing")

    undocumented = [cid for cid, change in changes.items() if change.get("breaking")
                   and not any(str(n.get("change") or "") == cid for n in notes)]
    if undocumented:
        problems.append(f"{len(undocumented)} breaking change(s) with no note: "
                        + ", ".join(undocumented[:3]))
    if unlinked:
        problems.append(f"{len(unlinked)} note(s) with no linked change: "
                        + ", ".join(unlinked[:3]))
    if flag_off:
        problems.append("announced work behind a disabled flag: " + "; ".join(flag_off[:2]))

    kinds = [str(n.get("kind") or "").lower() for n in notes]
    if "breaking" in kinds and kinds.index("breaking") != 0:
        problems.append("breaking entries are not first: the reader finds them last")

    return {
        "ok": not problems,
        "version": payload.get("version"),
        "notes": len(notes),
        "changes": len(changes),
        "breaking": sum(1 for n in notes if str(n.get("kind")).lower() == "breaking"),
        "unlinked": unlinked,
        "undocumented_breaking": undocumented,
        "announced_but_flagged_off": flag_off,
        "audience": payload.get("audience"),
        "problems": problems,
        "advice": ("notes resolve to changes, breaking first, nothing flagged-off "
                   "announced" if not problems else "; ".join(problems[:3])),
    }
