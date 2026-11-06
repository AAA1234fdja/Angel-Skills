"""Debt ledger: price the debt, then sort it by payback.

Payload::

    {"items": [{"id": "ci-40min", "symptom": "deploys take 40 minutes",
                "principal_hours": 40, "interest_hours_month": 10,
                "kind": "inadvertent", "owner": "platform"},
               {"id": "legacy-auth", "symptom": "every auth change needs two PRs",
                "principal_hours": 120, "interest_hours_month": 2,
                "kind": "accepted", "owner": "identity"}]}

Payback is principal divided by monthly interest: the number of months before fixing
costs less than keeping. Under twelve months is a candidate; above it, keeping the
debt is the rational choice and the tool says so instead of moralising.
"""

KINDS = ("deliberate", "inadvertent", "accepted")
PAYBACK_CANDIDATE = 12


def run(payload):
    items = payload.get("items") or []
    problems, rows = [], []
    total_interest = 0.0

    for index, item in enumerate(items):
        if not isinstance(item, dict) or not item.get("id"):
            problems.append(f"items[{index}]: no id")
            continue
        item_id = str(item["id"])
        issues = []
        if not str(item.get("symptom") or "").strip():
            issues.append("no felt symptom: a code smell has no interest rate")
        principal = item.get("principal_hours")
        interest = item.get("interest_hours_month")
        if not isinstance(principal, (int, float)) or principal < 0:
            issues.append("principal_hours must be a non-negative number")
            principal = None
        if not isinstance(interest, (int, float)) or interest < 0:
            issues.append("interest_hours_month is missing: the row cannot be sorted")
            interest = None
        if str(item.get("kind") or "") not in KINDS:
            issues.append(f"kind {item.get('kind')!r} not one of {', '.join(KINDS)}")
        if not str(item.get("owner") or "").strip():
            issues.append("no owner: unowned debt is a complaint")
        payback = None
        if principal is not None and interest:
            payback = round(principal / interest, 1)
            total_interest += float(interest)
            if payback <= PAYBACK_CANDIDATE and str(item.get("kind")) == "accepted":
                issues.append("marked accepted but pays back within a year: reconsider")
        elif interest == 0 and principal:
            issues.append("zero interest with a nonzero principal: there is nothing to pay back")
        rows.append({"id": item_id, "kind": item.get("kind"),
                     "principal": principal, "interest": interest,
                     "payback_months": payback, "issues": issues})
        problems.extend(f"{item_id}: {issue}" for issue in issues)

    rows.sort(key=lambda r: (r["payback_months"] is None,
                             r["payback_months"] if r["payback_months"] is not None else 0))
    candidates = [r["id"] for r in rows
                  if r["payback_months"] is not None
                  and r["payback_months"] <= PAYBACK_CANDIDATE]
    if not items:
        problems.append("no debt items: an empty ledger is not a clean ledger")
    return {
        "ok": not problems,
        "items": len(rows),
        "monthly_interest_hours": round(total_interest, 1),
        "annual_interest_hours": round(total_interest * 12, 1),
        "payback_candidates": candidates,
        "rows": rows,
        "problems": problems,
        "advice": (f"pay back {candidates[0] if candidates else 'nothing'} first: "
                   f"{round(total_interest, 1)} hours a month are being spent keeping "
                   "the current ledger" if not problems else "; ".join(problems[:3])),
    }
