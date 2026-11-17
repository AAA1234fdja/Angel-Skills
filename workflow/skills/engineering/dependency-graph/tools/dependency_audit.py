"""Dependency audit: cycles, longest chain, fan-in and orphans in one pass.

Payload::

    {"edges": [{"from": "app.api", "to": "domain.model"},
               {"from": "domain.model", "to": "infra.db"}],
     "layer_order": ["app", "domain", "infra"]}

`layer_order` is optional and names the layers top-down: an edge that points from
a later layer to an earlier one is reported as a layer violation, which is the
expensive kind of coupling because it gets copied.

The traversal is iterative on purpose: a graph with ten thousand nodes should not
hit a recursion limit in a tool whose job is to find cycles.
"""


def _cycle_path(graph, start):
    """Depth-first search that returns the first cycle reachable from `start`."""
    stack = [(start, [start])]
    seen = set()
    while stack:
        node, path = stack.pop()
        for target in graph.get(node, ()):
            if target == start:
                return path + [start]
            if target in path or target in seen:
                continue
            if len(path) < 50:
                stack.append((target, path + [target]))
        seen.add(node)
    return None


def _longest_chain(graph):
    """Longest simple path, bounded: deep chains are reported, not enumerated."""
    best = []

    def walk(node, path):
        nonlocal best
        if len(path) > len(best):
            best = list(path)
        if len(path) >= 40:
            return
        for target in graph.get(node, ()):
            if target not in path:
                walk(target, path + [target])

    for node in sorted(graph):
        walk(node, [node])
    return best


def run(payload):
    raw = payload.get("edges") or []
    order = [str(x) for x in (payload.get("layer_order") or [])]
    graph, fan_in, malformed = {}, {}, []
    for index, edge in enumerate(raw):
        if not isinstance(edge, dict) or not edge.get("from") or not edge.get("to"):
            malformed.append(f"edges[{index}]")
            continue
        source, target = str(edge["from"]), str(edge["to"])
        if source == target:
            malformed.append(f"self-import {source}")
            continue
        graph.setdefault(source, set()).add(target)
        graph.setdefault(target, set())
        fan_in[target] = fan_in.get(target, 0) + 1

    cycles, seen_cycle = [], set()
    for node in sorted(graph):
        path = _cycle_path(graph, node)
        if not path:
            continue
        key = tuple(sorted(set(path)))
        if key in seen_cycle:
            continue
        seen_cycle.add(key)
        cycles.append(path)

    layer_index = {name: i for i, name in enumerate(order)} if order else {}
    violations = []
    if layer_index:
        layer_of = {}

        def layer(node):
            if node in layer_of:
                return layer_of[node]
            head = node.split(".")[0]
            layer_of[node] = layer_index.get(head, len(order))
            return layer_of[node]

        for source, targets in graph.items():
            for target in targets:
                if layer(source) > layer(target):
                    violations.append(f"{source} -> {target}")

    fan_out = {node: len(targets) for node, targets in graph.items()}
    top_in = sorted(fan_in.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    orphans = sorted(n for n in graph if fan_in.get(n, 0) == 0 and not graph[n])
    roots = sorted(n for n in graph if fan_in.get(n, 0) == 0 and graph[n])
    chain = _longest_chain(graph)

    problems = len(cycles) + len(violations)
    advice = []
    if cycles:
        advice.append("break one edge per cycle: " + ", ".join(" -> ".join(c) for c in cycles[:2]))
    if violations:
        advice.append(f"{len(violations)} edge(s) point backwards through the layers")
    if not advice:
        advice.append("no cycles and no layer violations: the graph can be built in one pass")
    return {
        "ok": problems == 0 and not malformed,
        "nodes": len(graph),
        "edges": sum(len(t) for t in graph.values()),
        "cycles": cycles,
        "layer_violations": violations,
        "longest_chain": chain,
        "longest_chain_length": len(chain),
        "most_depended_on": [{"node": n, "fan_in": c} for n, c in top_in],
        "roots": roots,
        "orphans": orphans,
        "widest_fan_out": sorted(fan_out.items(), key=lambda kv: (-kv[1], kv[0]))[:3],
        "malformed": malformed,
        "advice": "; ".join(advice),
    }
