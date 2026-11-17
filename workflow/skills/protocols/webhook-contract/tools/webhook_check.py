"""Webhook contract check: can a consumer trust this feed?

Payload::

    {"event": "invoice.paid",
     "signature": {"algorithm": "hmac-sha256", "header": "X-Sig",
                   "covers_body": true, "timestamp_header": "X-Timestamp",
                   "replay_window_s": 300},
     "delivery": {"idempotency_key": "event_id", "semantics": "exactly-once",
                  "ordering": "ordered", "ordering_key": ""},
     "retries": {"attempts": 0, "window_s": 0, "backoff": ""},
     "dead_letter": {"mode": "", "visible": false},
     "version_header": ""}

"Exactly-once" is refused rather than corrected: it is a promise no webhook can keep,
and accepting it in a design review is how consumers end up double-processing and
blaming the sender.
"""


def run(payload):
    signature = payload.get("signature") or {}
    delivery = payload.get("delivery") or {}
    retries = payload.get("retries") or {}
    dead = payload.get("dead_letter") or {}
    problems = []

    if not str(payload.get("event") or "").strip():
        problems.append("no event named")
    if not str(signature.get("algorithm") or "").strip():
        problems.append("no signature algorithm: the consumer must trust the network")
    if signature.get("covers_body") is not True:
        problems.append("signature does not cover the body")
    if not str(signature.get("timestamp_header") or "").strip():
        problems.append("no signed timestamp: a captured call is replayable forever")
    window = signature.get("replay_window_s")
    if not isinstance(window, int) or window <= 0:
        problems.append("no replay window stated")

    if not str(delivery.get("idempotency_key") or "").strip():
        problems.append("no idempotency key: retries become duplicate effects")
    semantics = str(delivery.get("semantics") or "").strip().lower()
    if "exactly" in semantics:
        problems.append("exactly-once is not a webhook guarantee: say at-least-once")
    elif semantics not in ("at-least-once", "at_least_once"):
        problems.append(f"delivery semantics '{semantics or '?'}' must be at-least-once")

    ordering = str(delivery.get("ordering") or "").strip().lower()
    if ordering and ordering not in ("none", "per-entity", "per_entity"):
        if not str(delivery.get("ordering_key") or "").strip():
            problems.append(f"claims '{ordering}' ordering with no key: nobody can keep "
                            "that promise")
    elif ordering in ("per-entity", "per_entity") and not str(
            delivery.get("ordering_key") or "").strip():
        problems.append("per-entity ordering with no key named")

    attempts = retries.get("attempts")
    if not isinstance(attempts, int) or attempts <= 0:
        problems.append("no retry schedule: the consumer cannot plan reconciliation")
    if not isinstance(retries.get("window_s"), int) or retries.get("window_s") <= 0:
        problems.append("no total retry window: 'eventually' is not an SLA")
    if not str(retries.get("backoff") or "").strip():
        problems.append("no backoff strategy: retries will arrive in a burst")

    if not str(dead.get("mode") or "").strip():
        problems.append("no dead-letter outcome: silent drop is the default nobody chose")
    if dead.get("mode") and dead.get("visible") is not True:
        problems.append("dead letters are not visible to anyone")

    if not str(payload.get("version_header") or "").strip():
        problems.append("no version header: consumers must parse the body to route")

    return {
        "ok": not problems,
        "event": payload.get("event"),
        "signed": bool(signature.get("algorithm")) and signature.get("covers_body") is True,
        "replay_window_s": window if isinstance(window, int) else None,
        "semantics": semantics or None,
        "retry_attempts": attempts if isinstance(attempts, int) else None,
        "dead_letter": dead.get("mode") or None,
        "problems": problems,
        "advice": ("a consumer can verify, dedupe, order by key and reconcile a gap"
                   if not problems else "; ".join(problems[:3])),
    }
