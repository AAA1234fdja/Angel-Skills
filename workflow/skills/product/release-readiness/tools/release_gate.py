"""Release gate: turn a list of gate evidence into a ship / no-ship verdict.

Payload::

    {"gates": [{"id": "tests", "status": "pass", "evidence": "..."},
               {"id": "rollback", "status": "waived", "waiver": "ana",
                "reason": "static change, revert is the revert"}],
     "required": ["tests", "rollback", "observability", "blast_radius",
                  "communication"]}

Three rules, and the tool exists because people forget them under deadline
pressure:

* a gate that is absent is **blocked**, not assumed;
* a waiver without a name is a blocker, because a waiver is a decision somebody
  made;
* the verdict is `ship` only when every required gate is pass or named waiver.

The tool never reads files or contacts a deploy system: the evidence is passed
in, so the answer is reproducible from the payload alone.
"""

REQUIRED = ("tests", "rollback", "observability", "blast_radius", "communication")
STATUSES = ("pass", "waived", "blocked")


def run(payload):
    required = [str(g) for g in (payload.get("required") or REQUIRED)]
    declared = {}
    malformed = []
    for index, gate in enumerate(payload.get("gates") or []):
        if not isinstance(gate, dict) or not gate.get("id"):
            malformed.append(f"gates[{index}]")
            continue
        declared[str(gate["id"])] = gate

    rows, blockers, waivers = [], [], []
    for gate_id in required:
        gate = declared.get(gate_id)
        if gate is None:
            rows.append({"gate": gate_id, "status": "missing", "ok": False,
                         "reason": "no evidence was supplied for this gate"})
            blockers.append(f"{gate_id}: missing")
            continue
        status = str(gate.get("status") or "blocked")
        ok = status == "pass"
        reason = str(gate.get("reason") or "")
        if status == "waived":
            owner = str(gate.get("waiver") or "").strip()
            if owner:
                ok = True
                waivers.append(f"{gate_id}: {owner}")
                reason = reason or f"waived by {owner}"
            else:
                reason = "a waiver needs a name: an anonymous waiver is a blocker"
                status = "blocked"
        elif status not in STATUSES:
            reason = f"unknown status {status!r}"
            status = "blocked"
        rows.append({"gate": gate_id, "status": status, "ok": ok,
                     "reason": reason,
                     "evidence": gate.get("evidence") or ""})
        if not ok:
            blockers.append(f"{gate_id}: {status}")

    extra = sorted(set(declared) - set(required))
    verdict = "ship" if not blockers and not malformed else "no-ship"
    return {
        "ok": verdict == "ship",
        "verdict": verdict,
        "gates": rows,
        "blockers": blockers,
        "waivers": waivers,
        "not_required": extra,
        "malformed": malformed,
        "advice": ("all required gates are proven or waived: ship one change and "
                   "watch it" if verdict == "ship" else
                   "do not ship yet; resolve: " + ", ".join(blockers[:5])),
    }
