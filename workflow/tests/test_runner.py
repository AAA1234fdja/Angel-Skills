"""Runner tests: the only component that does things, so it is tested end to end."""

import json
import shutil
import tempfile

from support import AngelTestCase, Path, journal, protocols, registry, router
from angel import runner as runner_mod


class BudgetTests(AngelTestCase):
    def test_budget_stops_at_the_limit(self):
        budget = runner_mod.Budget(steps=1, tool_calls=2, seconds=1)
        budget.spend_step()
        self.assert_angel_error("E_BUDGET_EXCEEDED", budget.spend_step)

    def test_tool_budget_is_separate_from_step_budget(self):
        budget = runner_mod.Budget(steps=5, tool_calls=0, seconds=5)
        budget.spend_step()  # allowed
        self.assert_angel_error("E_BUDGET_EXCEEDED", budget.spend_tool)

    def test_snapshot_reports_every_dimension(self):
        budget = runner_mod.Budget(steps=3, tool_calls=4, seconds=10)
        budget.spend_step()
        snapshot = budget.to_dict()
        for key in ("steps", "tools", "seconds"):
            self.assertIn(key, snapshot)


class RunnerTests(AngelTestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="angel-run-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def _runner(self, **kwargs):
        options = {"budget": runner_mod.Budget(steps=12, tool_calls=40, seconds=60)}
        options.update(kwargs)
        return runner_mod.Runner(self.registry, root=self.root, **options)

    def test_a_real_run_passes_and_writes_a_verifiable_journal(self):
        report = self._runner().run("the build is broken, fix it")
        self.assertEqual(report.verdict, "pass", report.to_dict())
        self.assertEqual(report.score, 1.0)
        self.assertTrue(report.steps)
        book = journal.open_journal(self.root, report.run_id)
        self.assertTrue(book.verify()["ok"])
        kinds = [entry.kind for entry in book]
        for kind in ("run.start", "plan", "dispatch", "tool.call", "tool.result",
                     "result", "run.end"):
            self.assertIn(kind, kinds)

    def test_every_step_uses_the_declared_sample_payload(self):
        report = self._runner().run("review the security of this diff")
        self.assertEqual(report.verdict, "pass", report.to_dict())
        for step in report.steps:
            for tool in step.tools:
                self.assertTrue(tool["ok"], tool)

    def test_a_dry_run_executes_nothing(self):
        report = self._runner().run("document the CLI in the readme", dry_run=True)
        for step in report.steps:
            for tool in step.tools:
                self.assertIsNone(tool["ok"])
                self.assertTrue(tool["dry_run"])

    def test_no_tools_still_produces_a_plan_and_a_journal(self):
        report = self._runner().run("audit dependencies", tools=False)
        self.assertEqual(report.verdict, "pass")
        book = journal.open_journal(self.root, report.run_id)
        self.assertTrue(book.verify()["ok"])

    def test_the_plan_message_is_a_valid_protocol_message(self):
        routed, plan = self._runner().plan("migrate the orders table safely")
        self.assertEqual(plan.protocol, "isa-plan")
        parsed = protocols.parse(json.loads(json.dumps(plan.to_dict())))
        self.assertEqual(parsed.objective, "migrate the orders table safely")
        for step in parsed.steps:
            self.assertTrue(step["skills"])

    def test_an_unroutable_need_is_refused_before_anything_runs(self):
        self.assert_angel_error("E_INTERNAL", self._runner().plan, "secure")

    def test_the_budget_stops_a_run_that_is_too_greedy(self):
        report = self._runner(budget=runner_mod.Budget(
            steps=12, tool_calls=1, seconds=60)).run(
            "the build is broken, fix it", continue_on_error=True)
        codes = [error["code"] for error in report.errors]
        self.assertIn("E_BUDGET_EXCEEDED", codes)

    def test_a_failing_tool_fails_the_run(self):
        engine = self._runner()
        engine.box.sample_for = lambda skill_id, tool_id: {}
        report = engine.run("review my change")
        self.assertIn(report.verdict, ("fail", "blocked"))
        codes = [error["code"] for error in report.errors]
        self.assertIn("E_TOOL_INPUT", codes)

    def test_gate_blocks_a_run_with_no_steps(self):
        verdict, score = self._runner()._gate([], [])
        self.assertEqual((verdict, score), ("blocked", 0.0))

    def test_two_runs_get_distinct_ids_and_separate_journals(self):
        engine = self._runner()
        first = engine.run("audit dependencies", tools=False)
        second = engine.run("audit dependencies", tools=False)
        self.assertNotEqual(first.run_id, second.run_id)
        self.assertNotEqual(first.journal, second.journal)
        self.assertEqual(len(journal.list_journals(self.root)), 2)
