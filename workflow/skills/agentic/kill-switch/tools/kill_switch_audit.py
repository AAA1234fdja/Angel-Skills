"""Kill switch audit: could a person who did not build it stop this thing?

Payload::

    {"switches": [{"capability": "auto-merge PRs", "name": "flag:agent.automerge",
                   "owner": "platform", "restart_owner": "platform",
                   "safe_state": "no further merges, queue keeps items",
                   "reachable_without_deploy": true, "in_flight": "finishes the current PR",
                   "tested_on": "2026-09-14", "today": "2026-11-05"}]}

An untested switch is a belief and a switch only a deploy can flip is not a switch.
The tool reports both, plus the two ambiguities that cost minutes in an incident:
no stated safe state, and no named person allowed to restart.
"""


def _days_apart(a, b):
    try:
        from datetime import date

        return (date.fromisoformat(str(b)) - date.fromisoformat(str(a))).days
    except (TypeError, ValueError):
        return None


def run(payload):
    switches = payload.get("switches") or []
    problems, rows = [], []
    for index, switch in enumerate(switches):
        if not isinstance(switch, dict) or not switch.get("capability"):
            problems.append(f"switches[{index}]: no capability named")
            continue
        capability = str(switch["capability"])
        issues = []
        if not str(switch.get("name") or "").strip():
            issues.append("no switch name: a responder cannot find it")
        if not str(switch.get("owner") or "").strip():
            issues.append("no owner: nobody is accountable for stopping it")
        if not str(switch.get("restart_owner") or "").strip():
            issues.append("nobody named to restart: a stop with no restart path is an outage")
        if not str(switch.get("safe_state") or "").strip():
            issues.append("no safe state: what is true after the stop?")
        if switch.get("reachable_without_deploy") is not True:
            issues.append("only reachable by deploying: it does not exist under pressure")
        if not str(switch.get("in_flight") or "").strip():
            issues.append("in-flight behaviour undocumented: abort, finish or half-written?")
        days = _days_apart(switch.get("tested_on"), switch.get("today"))
        if days is None:
            issues.append("never tested (or no test date)")
        elif days > 90:
            issues.append(f"last tested {days} days ago: an untested switch is a belief")
        rows.append({"capability": capability, "issues": issues})
        problems.extend(f"{capability}: {issue}" for issue in issues)

    if not switches:
        problems.append("no switches: an autonomous capability without one is unsupervised")
    return {
        "ok": not problems,
        "switches": len(rows),
        "rows": rows,
        "problems": problems,
        "advice": ("each capability can be stopped by a person without a deploy, and "
                   "was tested this quarter" if not problems else "; ".join(problems[:3])),
    }
