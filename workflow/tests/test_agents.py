"""Agent tests: an agent is an API, and every API may call subagents.

Two kinds of test live here. The first exercises the shipped roster: six real
cards, a real delegation graph, real addresses. The second builds a disposable
roster and breaks it on purpose — a cycle, an unauthorised hop, a budget that
gives away more than it holds, a pin that no longer matches — because a
permission system that is only tested on well-formed input is not a permission
system.
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile

from support import REAL_ROOT, AngelTestCase, Path, unittest

from angel import agents, contracts, journal, registry

#: every card the package ships, so a new one cannot slip in untested
SHIPPED = ("governance-auditor", "isa-planner", "wev-judge", "xev-builder",
           "xev-tester", "zev-scout")


def _flatten(node: dict) -> list[dict]:
    """Every node of a planned tree, root first."""
    out = [node]
    for child in node.get("children") or []:
        out.extend(_flatten(child))
    return out


def real_roster() -> agents.Roster:
    return agents.load(REAL_ROOT, registry=registry.load(REAL_ROOT))


class TempRoster:
    """A disposable roster: real contracts, hand-made cards."""

    def __init__(self, cards: list[dict] | None = None,
                 registry_needed: bool = True) -> None:
        self.cards = cards
        self.registry_needed = registry_needed
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix="angel-agents-"))
        shutil.copytree(REAL_ROOT / "contracts", self.path / "contracts")
        if self.registry_needed:
            data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
            (self.path / "categories.json").write_text(json.dumps(data), encoding="utf-8")
            shutil.copytree(REAL_ROOT / "skills", self.path / "skills")
        for card in self.cards or []:
            folder = self.path / "agents" / card["id"]
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "agent.json").write_text(json.dumps(card, indent=2), encoding="utf-8")
        return self.path

    def __exit__(self, *exc) -> None:
        if self.path and self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)


def card(**overrides) -> dict:
    """A minimal valid card; overrides make it invalid on purpose."""
    base = {
        "schema": "angel.agent/1",
        "id": "probe",
        "version": "1.0.0",
        "address_space": "test",
        "role": "researcher",
        "state": "live",
        "description": "A probe agent used only by the test suite, never shipped.",
        "model": {"name": "probe-tier", "reasoning": "low", "temperature": 0.0,
                  "context_tokens": 8000},
        "inputs": {"fields": {"question": {"type": "string"}}},
        "outputs": {"fields": {"claims": {"type": "array"}}},
        "skills": ["search-first"],
        "tools": [],
        "guardrails": ["read-only"],
        "limits": {"max_depth": 1, "max_calls": 2, "budget_share": 1.0, "timeout_s": 60},
        "delegates": [],
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------
# addresses
# --------------------------------------------------------------------------
class AddressTests(AngelTestCase):
    def test_a_full_address_parses_into_its_five_parts(self):
        address = agents.parse_address("agent://acme/xev-builder@1.0.0#3d6252a9->reviewer")
        self.assertEqual(address.space, "acme")
        self.assertEqual(address.agent_id, "xev-builder")
        self.assertEqual(address.version, "1.0.0")
        self.assertEqual(address.pin, "3d6252a9")
        self.assertEqual(address.hop, "reviewer")

    def test_a_bare_id_is_a_valid_address(self):
        address = agents.parse_address("xev-builder")
        self.assertEqual(address.agent_id, "xev-builder")
        self.assertIsNone(address.version)
        self.assertIsNone(address.pin)

    def test_every_shipped_agent_publishes_an_address_that_parses_back(self):
        roster = real_roster()
        for agent in roster.agents.values():
            with self.subTest(agent=agent.id):
                address = agents.parse_address(agent.reference())
                self.assertEqual(address.agent_id, agent.id)
                self.assertEqual(address.version, agent.version)
                self.assertEqual(address.pin, agent.fingerprint()[:8])

    def test_a_malformed_address_is_refused(self):
        for bad in ("agent://", "agent:///x", "agent://acme/", "agent://acme/Xev Builder",
                    "agent://acme/xev@one.2.3"):
            with self.subTest(address=bad):
                self.assert_angel_error("E_AGENT_ADDRESS", agents.parse_address, bad)

    def test_an_address_without_a_space_is_refused(self):
        self.assert_angel_error("E_AGENT_ADDRESS", agents.parse_address, "agent://xev-builder")


# --------------------------------------------------------------------------
# the card
# --------------------------------------------------------------------------
class CardTests(AngelTestCase):
    def test_every_shipped_card_satisfies_the_agent_card_contract(self):
        contract = contracts.resolve(REAL_ROOT, "agent-card", "1.0.0")
        for name in SHIPPED:
            with self.subTest(agent=name):
                payload = json.loads((REAL_ROOT / "agents" / name / "agent.json")
                                     .read_text(encoding="utf-8"))
                contract.validate(payload)

    def test_the_shipped_roster_is_announced_in_categories(self):
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        self.assertEqual({a["id"] for a in data.get("agents", [])}, set(SHIPPED))

    def test_the_shipped_roster_is_valid_and_validates_its_cards(self):
        roster = real_roster()
        self.assertEqual(sorted(roster.agents), list(SHIPPED))
        report = roster.validate()
        self.assertEqual(report["errors"], [])

    def test_every_declared_skill_exists_in_the_registry(self):
        roster = real_roster()
        for agent in roster.agents.values():
            for skill_id in agent.skills:
                with self.subTest(agent=agent.id, skill=skill_id):
                    self.assertIn(skill_id, self.registry.skills)

    def test_a_card_that_breaks_the_contract_never_loads(self):
        broken = card(role="wizard")
        with TempRoster([broken]) as root:
            self.assert_angel_error("E_AGENT_INVALID", agents.discover, root)

    def test_a_card_missing_a_required_field_never_loads(self):
        broken = card()
        broken.pop("limits")
        with TempRoster([broken]) as root:
            self.assert_angel_error("E_AGENT_INVALID", agents.discover, root)

    def test_the_fingerprint_ignores_prose_but_not_behaviour(self):
        base = agents.Agent(card=card(), path=Path("."))
        reworded = copy.deepcopy(base.card)
        reworded["description"] = "A completely different sentence about the same agent."
        reworded["owner"] = "somebody-else"
        reworded["metadata"] = {"ticket": "ENG-1"}
        reworded["model"]["temperature"] = 1.4
        self.assertEqual(base.fingerprint(),
                         agents.Agent(card=reworded, path=Path(".")).fingerprint())

        widened = copy.deepcopy(base.card)
        widened["skills"] = ["search-first", "code-review"]
        self.assertNotEqual(base.fingerprint(),
                            agents.Agent(card=widened, path=Path(".")).fingerprint())

    def test_the_endpoint_is_the_api_description(self):
        agent = real_roster().get("wev-judge")
        endpoint = agent.endpoint()
        for key in ("address", "reference", "inputs", "outputs", "skills", "limits",
                    "delegates", "callable", "calls"):
            self.assertIn(key, endpoint)
        self.assertTrue(endpoint["callable"])
        self.assertEqual(endpoint["calls"], agent.fingerprint())


# --------------------------------------------------------------------------
# addresses resolve against the roster
# --------------------------------------------------------------------------
class ResolutionTests(AngelTestCase):
    def test_an_exact_pin_resolves_and_a_wrong_pin_is_stale(self):
        roster = real_roster()
        pinned = roster.get("agent://acme/xev-builder@1.0.0#" + roster.get("xev-builder").fingerprint()[:8])
        self.assertEqual(pinned.id, "xev-builder")
        self.assert_angel_error("E_AGENT_STALE", roster.get,
                                "agent://acme/xev-builder@1.0.0#deadbeef")

    def test_a_bare_id_resolves_the_latest_card(self):
        roster = real_roster()
        self.assertEqual(roster.get("xev-builder").version, "1.0.0")

    def test_an_unknown_agent_is_not_found(self):
        err = self.assert_angel_error("E_AGENT_NOT_FOUND", real_roster().get, "nobody")
        self.assertIn("known:", err.recovery()["root_cause_hint"])

    def test_a_hop_only_exists_when_the_edge_is_declared(self):
        roster = real_roster()
        reached = roster.resolve(agents.parse_address("agent://acme/isa-planner->xev-builder"))
        self.assertEqual(reached.id, "xev-builder")
        self.assert_angel_error("E_DELEGATION_DENIED", roster.resolve,
                                agents.parse_address("agent://acme/zev-scout->xev-builder"))

    def test_a_draft_agent_cannot_be_called(self):
        draft = card(id="draft-probe", state="draft")
        with TempRoster([draft]) as root:
            roster = agents.discover(root, registry=registry.load(root))
            self.assert_angel_error("E_AGENT_NOT_LIVE",
                                    agents.Dispatcher(roster, None).plan,
                                    "draft-probe", "look around")


# --------------------------------------------------------------------------
# the graph
# --------------------------------------------------------------------------
class GraphTests(AngelTestCase):
    def test_the_tree_reaches_every_declared_delegate(self):
        roster = real_roster()
        tree = roster.tree("isa-planner")

        def walk(node):
            yield node["id"]
            for kid in node.get("children") or []:
                yield from walk(kid)

        reached = set(walk(tree))
        self.assertEqual(reached, {"isa-planner", "xev-builder", "xev-tester",
                                   "wev-judge", "zev-scout"})

    def test_every_agent_but_the_leaf_has_parents_or_is_a_root(self):
        roster = real_roster()
        self.assertTrue(roster.parents("zev-scout"))
        self.assertEqual(sorted(a.id for a in roster.parents("xev-tester")), ["xev-builder"])

    def test_the_cascade_order_is_breadth_first_without_repeats(self):
        order = real_roster().cascade_order("isa-planner")
        self.assertEqual(order[0], "isa-planner")
        self.assertEqual(len(order), len(set(order)))
        self.assertEqual(order[1], "xev-builder")

    def test_a_cycle_is_refused_when_the_roster_loads(self):
        first = card(id="first", delegates=[
            {"to": "second", "when": "always hand off to the second agent",
             "allow": ["search-first"], "budget": 0.5}])
        second = card(id="second", delegates=[
            {"to": "first", "when": "hand it straight back to the first",
             "allow": ["search-first"], "budget": 0.5}])
        with TempRoster([first, second]) as root:
            report = agents.discover(root, registry=registry.load(root)).validate()
            self.assertTrue(any("cycle" in e for e in report["errors"]), report["errors"])

    def test_a_card_that_delegates_to_an_unknown_agent_is_refused(self):
        lonely = card(id="lonely", delegates=[
            {"to": "ghost", "when": "when the ghost is needed",
             "allow": ["search-first"], "budget": 0.5}])
        with TempRoster([lonely]) as root:
            report = agents.discover(root, registry=registry.load(root)).validate()
            self.assertTrue(any("ghost" in e for e in report["errors"]), report["errors"])

    def test_a_delegation_without_a_condition_is_refused_by_the_contract(self):
        vague = card(id="vague", delegates=[
            {"to": "probe", "when": "", "allow": ["search-first"], "budget": 0.5}])
        with TempRoster([vague, card()]) as root:
            self.assert_angel_error("E_AGENT_INVALID", agents.discover, root)

    def test_card_level_rules_still_fire_when_no_contract_is_installed(self):
        """The contract is the first gate; the roster is the second, not a copy."""
        vague = card(id="vague", delegates=[
            {"to": "probe", "when": "", "allow": ["search-first"], "budget": 0.5}])
        with TempRoster([vague, card()]) as root:
            shutil.rmtree(root / "contracts")
            report = agents.discover(root, registry=registry.load(root)).validate()
            self.assertTrue(any("needs a 'when'" in e for e in report["errors"]),
                            report["errors"])


# --------------------------------------------------------------------------
# delegation: authority only narrows
# --------------------------------------------------------------------------
class DispatchTests(AngelTestCase):
    def test_a_plan_stays_inside_the_declared_edges(self):
        roster = real_roster()
        tree = agents.Dispatcher(roster, self.registry).plan("isa-planner", "review this diff")
        self.assertTrue(tree.walk())
        for node in tree.walk():
            with self.subTest(agent=node.agent):
                declared = {d.get("to") for d in roster.get(node.agent).delegates}
                for child in node.children:
                    self.assertIn(child.agent, declared)

    def test_a_child_never_exceeds_the_authority_of_its_edge(self):
        roster = real_roster()
        tree = agents.Dispatcher(roster, self.registry).plan(
            "isa-planner", "review the security of this diff")
        for node in tree.walk():
            parent = next((p for p in tree.walk() if node in p.children), None)
            if parent is None:
                continue
            edge = next(e for e in roster.get(parent.agent).delegates
                        if e.get("to") == node.agent)
            with self.subTest(agent=node.agent):
                for skill_id in node.skills:
                    self.assertIn(skill_id, edge["allow"])
                    self.assertIn(skill_id, node.allowed)

    def test_capabilities_are_intersected_down_the_tree(self):
        """A grandchild may only exercise skills its edge names *and* the root allowed."""
        root = card(id="root", limits={"max_depth": 3, "max_calls": 4,
                                       "budget_share": 1.0, "timeout_s": 60},
                    delegates=[{"to": "middle", "when": "always pass the work down",
                                "allow": ["search-first", "code-review"], "budget": 0.8}])
        middle = card(id="middle", limits={"max_depth": 2, "max_calls": 4,
                                           "budget_share": 1.0, "timeout_s": 60},
                      skills=["search-first", "code-review"],
                      delegates=[{"to": "leaf", "when": "always reach the leaf agent",
                                  "allow": ["search-first", "secret-scan"], "budget": 0.5}])
        leaf = card(id="leaf", skills=["search-first", "secret-scan"],
                    limits={"max_depth": 0, "max_calls": 0,
                            "budget_share": 1.0, "timeout_s": 60})
        with TempRoster([root, middle, leaf]) as tmp:
            reg = registry.load(tmp)
            tree = agents.Dispatcher(agents.discover(tmp, registry=reg), reg).plan(
                "root", "always pass the work down always reach the leaf agent")
            names = {node.agent: node for node in tree.walk()}
            self.assertIn("leaf", names)
            # secret-scan is named by the leaf's edge but was never authorised above
            self.assertNotIn("secret-scan", names["leaf"].allowed)
            self.assertEqual(names["leaf"].skills, ["search-first"])

    def test_an_edge_whose_allow_list_loses_everything_is_denied_not_widened(self):
        root = card(id="root", delegates=[
            {"to": "middle", "when": "always pass the work down",
             "allow": ["code-review"], "budget": 0.8}],
            limits={"max_depth": 2, "max_calls": 4, "budget_share": 1.0, "timeout_s": 60})
        middle = card(id="middle", skills=["code-review"], delegates=[
            {"to": "leaf", "when": "always reach the leaf agent",
             "allow": ["search-first"], "budget": 0.5}],
            limits={"max_depth": 1, "max_calls": 4, "budget_share": 1.0, "timeout_s": 60})
        leaf = card(id="leaf", skills=["search-first"])
        with TempRoster([root, middle, leaf]) as tmp:
            reg = registry.load(tmp)
            tree = agents.Dispatcher(agents.discover(tmp, registry=reg), reg).plan(
                "root", "always pass the work down always reach the leaf agent")
            names = {node.agent: node for node in tree.walk()}
            self.assertNotIn("leaf", names)
            self.assertTrue(any("leaf" in d for d in names["middle"].denied))

    def test_max_depth_is_enforced_at_plan_time(self):
        deep = card(id="deep", limits={"max_depth": 0, "max_calls": 2,
                                       "budget_share": 1.0, "timeout_s": 60},
                    delegates=[{"to": "probe", "when": "always pass the work down",
                                "allow": ["search-first"], "budget": 0.5}])
        with TempRoster([deep, card()]) as tmp:
            reg = registry.load(tmp)
            tree = agents.Dispatcher(agents.discover(tmp, registry=reg), reg).plan(
                "deep", "always pass the work down")
            self.assertEqual(tree.children, [])
            self.assertTrue(any("max_depth" in d for d in tree.denied))

    def test_max_calls_bounds_the_fan_out(self):
        wide = card(id="wide", limits={"max_depth": 2, "max_calls": 1,
                                       "budget_share": 1.0, "timeout_s": 60},
                    delegates=[
                        {"to": "probe", "when": "always pass the work down",
                         "allow": ["search-first"], "budget": 0.3},
                        {"to": "probe-two", "when": "always pass the work down",
                         "allow": ["search-first"], "budget": 0.3}])
        second = card(id="probe-two")
        with TempRoster([wide, card(), second]) as tmp:
            reg = registry.load(tmp)
            tree = agents.Dispatcher(agents.discover(tmp, registry=reg), reg).plan(
                "wide", "always pass the work down")
            self.assertEqual(len(tree.children), 1)
            self.assertTrue(any("max_calls" in d for d in tree.denied))

    def test_the_budget_shrinks_at_every_hop(self):
        roster = real_roster()
        tree = agents.Dispatcher(roster, self.registry).plan(
            "isa-planner", "unfamiliar failure: trace the cause through the history "
                           "and write the tests")
        for node in tree.walk()[1:]:
            parent = next(p for p in tree.walk() if node in p.children)
            self.assertLessEqual(node.budget, parent.budget)

    def test_the_index_and_the_folder_name_the_same_agents(self):
        roster = real_roster()
        index = agents.read_index(REAL_ROOT)
        self.assertIsNotNone(index)
        self.assertEqual({e["id"] for e in index["agents"]}, set(roster.agents))

    def test_an_index_that_forgets_an_agent_is_an_error(self):
        with TempRoster([card()]) as tmp:
            (tmp / "agents" / "roster.json").write_text(json.dumps(
                {"schema": "angel.roster/1", "address_space": "test", "agents": []}))
            report = agents.discover(tmp, registry=registry.load(tmp)).validate()
            self.assertTrue(any("does not list" in e for e in report["errors"]),
                            report["errors"])

    def test_an_index_that_invents_an_agent_is_an_error(self):
        with TempRoster([card()]) as tmp:
            (tmp / "agents" / "roster.json").write_text(json.dumps(
                {"schema": "angel.roster/1", "address_space": "test",
                 "agents": [{"id": "probe"}, {"id": "ghost"}]}))
            report = agents.discover(tmp, registry=registry.load(tmp)).validate()
            self.assertTrue(any("ghost" in e and "no card" in e
                                for e in report["errors"]), report["errors"])

    def test_a_leaf_that_reserves_call_room_is_flagged(self):
        leaf = card(id="leafy", limits={"max_depth": 0, "max_calls": 3,
                                        "budget_share": 1.0, "timeout_s": 60})
        with TempRoster([leaf]) as tmp:
            report = agents.discover(tmp, registry=registry.load(tmp)).validate()
            self.assertEqual(report["errors"], [])
            self.assertTrue(any("reserves room" in w for w in report["warnings"]),
                            report["warnings"])

    def test_a_card_cannot_hand_out_more_budget_than_it_holds(self):
        greedy = card(id="greedy", limits={"max_depth": 2, "max_calls": 4,
                                           "budget_share": 0.5, "timeout_s": 60},
                      delegates=[
                          {"to": "probe", "when": "always pass the work down",
                           "allow": ["search-first"], "budget": 0.5},
                          {"to": "probe-two", "when": "always pass the work down",
                           "allow": ["search-first"], "budget": 0.5}])
        with TempRoster([greedy, card(), card(id="probe-two")]) as tmp:
            report = agents.discover(tmp, registry=registry.load(tmp)).validate()
            self.assertTrue(any("hand out" in e for e in report["errors"]), report["errors"])

    def test_the_router_narrows_a_node_to_what_the_objective_needs(self):
        roster = real_roster()
        dispatcher = agents.Dispatcher(roster, self.registry)
        security = dispatcher.plan("wev-judge", "review the security of this diff")
        self.assertIn("security-review", security.skills)
        self.assertNotEqual(sorted(security.skills), sorted(roster.get("wev-judge").skills))


# --------------------------------------------------------------------------
# calling and journaling
# --------------------------------------------------------------------------
class CallTests(AngelTestCase):
    def test_a_call_records_its_tree_and_its_journal(self):
        with TempRoster(None, registry_needed=False) as tmp:
            shutil.copytree(REAL_ROOT / "skills", tmp / "skills")
            data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
            (tmp / "categories.json").write_text(json.dumps(data), encoding="utf-8")
            shutil.copytree(REAL_ROOT / "agents", tmp / "agents")
            payload = agents.call(tmp, "agent://acme/xev-builder@1.0.0",
                                  "add the endpoint and its tests", execute=False)
            self.assertEqual(payload["resolved"]["id"], "xev-builder")
            self.assertEqual(payload["verdict"], "planned")
            self.assertGreaterEqual(payload["calls"], 1)
            self.assertTrue(Path(payload["journal"]).is_file())

            saved = agents.save_call(tmp, payload)
            self.assertTrue(saved.is_file())
            self.assertEqual(json.loads(saved.read_text())["address"], payload["address"])

            names = {p.stem for p in (tmp / ".workflow" / "calls").glob("*.json")}
            self.assertIn(saved.stem, names)

    def test_an_executed_call_journals_every_hop_it_took(self):
        with TempRoster(None, registry_needed=False) as tmp:
            shutil.copytree(REAL_ROOT / "skills", tmp / "skills")
            data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
            (tmp / "categories.json").write_text(json.dumps(data), encoding="utf-8")
            shutil.copytree(REAL_ROOT / "agents", tmp / "agents")
            payload = agents.call(tmp, "xev-tester", "write the failing test first",
                                  execute=True)
            self.assertEqual(payload["verdict"], "pass", payload["errors"])
            run_id = Path(payload["journal"]).stem
            replayed = journal.open_journal(tmp, run_id)
            self.assertTrue(replayed.verify()["ok"])
            dispatches = replayed.find("dispatch")
            self.assertTrue(dispatches)
            for entry in dispatches:
                self.assertIn("agent", entry.data)
                self.assertIn("authorised", entry.data)

    def test_a_pinned_call_resolves_the_exact_card_or_refuses(self):
        with TempRoster(None, registry_needed=False) as tmp:
            shutil.copytree(REAL_ROOT / "skills", tmp / "skills")
            data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
            (tmp / "categories.json").write_text(json.dumps(data), encoding="utf-8")
            shutil.copytree(REAL_ROOT / "agents", tmp / "agents")
            pin = agents.discover(tmp, registry=registry.load(tmp)).get("zev-scout").fingerprint()[:8]
            ok = agents.call(tmp, f"agent://acme/zev-scout@1.0.0#{pin}", "find the file",
                             execute=False)
            self.assertEqual(ok["resolved"]["id"], "zev-scout")
            self.assert_angel_error("E_AGENT_STALE", agents.call, tmp,
                                    "agent://acme/zev-scout@1.0.0#00000000",
                                    "find the file")


class ExecutionCeilingTests(AngelTestCase):
    """The second line of defence: `execute` re-checks the ceilings it plans with."""

    def _package(self, tmp: Path) -> Path:
        shutil.copytree(REAL_ROOT / "skills", tmp / "skills", dirs_exist_ok=True)
        data = json.loads((REAL_ROOT / "categories.json").read_text(encoding="utf-8"))
        (tmp / "categories.json").write_text(json.dumps(data), encoding="utf-8")
        return tmp

    def test_a_wildcard_call_is_denied_rather_than_executed(self):
        wide = card(id="wide", limits={"max_depth": 2, "max_calls": 2,
                                       "budget_share": 1.0, "timeout_s": 60},
                    delegates=[
                        {"to": "probe", "when": "always pass the work down",
                         "allow": ["search-first"], "budget": 0.4},
                        {"to": "probe-two", "when": "always pass the work down",
                         "allow": ["search-first"], "budget": 0.4}])
        with TempRoster([wide, card(), card(id="probe-two")]) as tmp:
            self._package(tmp)
            reg = registry.load(tmp)
            dispatcher = agents.Dispatcher(agents.discover(tmp, registry=reg), reg)
            tree = dispatcher.plan("wide", "always pass the work down")
            tree.children.append(copy.deepcopy(tree.children[0]))  # never planned
            result = dispatcher.execute(tree, tools=False)
            self.assertIn("fail", result["verdict"])
            self.assertTrue(any("at most" in str(e.get("message")) for e in result["errors"]),
                            result["errors"])

    def test_every_executed_hop_is_recorded_once(self):
        with TempRoster(None, registry_needed=False) as tmp:
            self._package(tmp)
            shutil.copytree(REAL_ROOT / "agents", tmp / "agents")
            reg = registry.load(tmp)
            payload = agents.call(tmp, "isa-planner",
                                  "unfamiliar failure: trace the cause through the history "
                                  "and write the tests", registry=reg, execute=True)
            agents_seen = [o["agent"] for o in payload["outcomes"]]
            # a fan-in is legitimate: the same subagent may be reached by two
            # different callers. What must never happen is a node skipped or run
            # twice, so the count is compared against the planned tree.
            self.assertEqual(len(agents_seen), payload["calls"])
            self.assertEqual(len(agents_seen), len(_flatten(payload["tree"])))
            self.assertEqual(agents_seen[0], "isa-planner")
            self.assertEqual(sorted(set(agents_seen)),
                             sorted({c["agent"] for c in _flatten(payload["tree"])}))


class CliAgentTests(AngelTestCase):
    def cli(self, *args: str):
        import os
        import subprocess
        import sys

        env = dict(os.environ, PYTHONPATH=str(REAL_ROOT))
        return subprocess.run([sys.executable, "-m", "angel.cli", "--root", str(REAL_ROOT),
                               *args], cwd=str(REAL_ROOT), env=env,
                              capture_output=True, text=True, timeout=120)

    def test_list_shows_every_agent_and_its_address(self):
        result = self.cli("agents", "list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in SHIPPED:
            self.assertIn(name, result.stdout)
        self.assertIn("agent://acme/", result.stdout)

    def test_validate_is_clean_and_strict_passes_too(self):
        for extra in ((), ("--strict",)):
            with self.subTest(args=extra):
                result = self.cli("agents", "validate", *extra)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("0 error(s)", result.stdout)
                self.assertIn("0 warning(s)", result.stdout)

    def test_address_reports_the_pin_and_the_resolution(self):
        result = self.cli("--json", "agents", "address", "agent://acme/wev-judge@1.0.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["agent"], "wev-judge")
        self.assertIsNone(payload["pin"])
        self.assertTrue(payload["endpoint"]["callable"])

    def test_a_stale_pin_exits_with_the_error_policy_code(self):
        result = self.cli("agents", "address", "agent://acme/wev-judge@1.0.0#00000000")
        self.assertEqual(result.returncode, 13)
        self.assertIn("E_AGENT_STALE", result.stdout)

    def test_plan_prints_the_cascade_it_would_run(self):
        result = self.cli("--json", "agents", "plan", "--agent", "isa-planner",
                          "--need", "unfamiliar failure: trace the cause through the history "
                                    "and write the tests")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["tree"]["agent"], "isa-planner")
        self.assertGreater(payload["calls"], 1)

    def test_tree_is_delegation_only_between_declared_agents(self):
        result = self.cli("--json", "agents", "tree", "isa-planner")
        self.assertEqual(result.returncode, 0, result.stderr)
        tree = json.loads(result.stdout)

        def walk(node):
            yield node["id"]
            for kid in node.get("children") or []:
                yield from walk(kid)

        self.assertEqual(set(walk(tree)) & set(SHIPPED), set(walk(tree)))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
