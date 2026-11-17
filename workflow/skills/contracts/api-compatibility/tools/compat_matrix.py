"""Consumer/producer compatibility matrix.

Payload::

    {"producers": [{"name": "api", "versions": ["1.4.0", "2.0.0"]}],
     "consumers": [{"name": "web", "pins": {"api": 1}},
                   {"name": "mobile", "pins": {"api": 2}}]}

A consumer pinning major N is compatible if the producer serves any N.x.y.
"""


def _major(version):
    try:
        return int(str(version).split(".")[0])
    except (TypeError, ValueError):
        return None


def run(payload):
    producers = {str(p.get("name")): [str(v) for v in (p.get("versions") or [])]
                 for p in payload.get("producers") or []}
    consumers = list(payload.get("consumers") or [])

    served = {name: {_major(v) for v in versions if _major(v) is not None}
              for name, versions in producers.items()}

    rows, unsafe, unpinned = [], [], []
    for consumer in consumers:
        name = str(consumer.get("name"))
        pins = consumer.get("pins") or {}
        for producer in sorted(producers):
            if producer not in pins:
                unpinned.append(f"{name} -> {producer}")
                continue
            pin = _major(pins[producer])
            compatible = pin in served.get(producer, set())
            rows.append({"consumer": name, "producer": producer,
                         "pinned_major": pin, "served": sorted(
                             m for m in served.get(producer, set()) if m is not None),
                         "compatible": compatible})
            if not compatible:
                unsafe.append(f"{name} pins {producer}@{pin} (served: "
                              f"{sorted(served.get(producer, set()))})")

    return {
        "ok": not unsafe,
        "matrix": rows,
        "unsafe": unsafe,
        "unpinned": unpinned,
        "advice": ("every consumer matches a served major" if not unsafe else
                   "decide per consumer: upgrade, keep the old major, or cut it"),
    }
