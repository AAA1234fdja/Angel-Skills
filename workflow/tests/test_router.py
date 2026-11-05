"""Router tests: routing is data, so a wrong route is a bug you can reproduce."""

from support import AngelTestCase, router


class RouterTests(AngelTestCase):
    def route(self, need: str, **kwargs):
        return router.route(self.registry, need, **kwargs)

    def assert_top(self, need: str, expected: str, **kwargs):
        result = self.route(need, **kwargs)
        self.assertTrue(result.matches, f"nothing routed for {need!r}")
        self.assertEqual(result.steps[0]["skill"], expected,
                         f"{need!r} routed to {[s['skill'] for s in result.steps]}")

    def test_a_named_skill_always_wins(self):
        result = self.route("run verification-loop before I commit")
        self.assertEqual(result.steps[0]["skill"], "verification-loop")
        self.assertIn("named explicitly", result.steps[0]["why"])

    def test_broken_build_routes_to_build_fix_first(self):
        self.assert_top("the build is broken with a type error", "build-fix")

    def test_flaky_browser_test_routes_to_e2e(self):
        self.assert_top("my browser test is flaky in CI", "e2e-testing")

    def test_migration_need_routes_to_migration_safety(self):
        self.assert_top("migrate the orders table without losing data", "migration-safety")

    def test_spanish_need_routes_the_same_way(self):
        self.assert_top("hay que migrar la tabla de ordenes sin perder datos",
                        "migration-safety")

    def test_negation_masks_the_clause(self):
        masked = router.mask_negations("no tests please, just review the diff")
        self.assertNotIn("tests", masked)
        self.assertIn("review", masked)

    def test_negated_need_does_not_route_to_a_test_skill(self):
        result = self.route("no tests please, just review the diff")
        skills = [s["skill"] for s in result.steps]
        self.assertEqual(skills[0], "code-review")
        self.assertNotIn("tdd-workflow", skills)

    def test_a_verb_alone_does_not_reach_the_threshold(self):
        # "review" is both a verb and a declared keyword, so it corroborates itself
        # for the skill whose whole job is review; a bare verb with no keyword does
        # not reach the threshold.
        only_verb = self.route("secure")
        self.assertEqual(only_verb.matches, [])
        self.assertEqual(self.route("review").steps[0]["skill"], "code-review")

    def test_zero_min_score_is_refused(self):
        self.assert_angel_error("E_INTERNAL", self.route, "review", min_score=0)

    def test_scores_are_deterministic(self):
        first = self.route("audit the security of this diff").to_dict()
        second = self.route("audit the security of this diff").to_dict()
        self.assertEqual(first["matches"], second["matches"])

    def test_empty_need_is_rejected(self):
        self.assert_angel_error("E_ROUTE_EMPTY", router.route, self.registry, "   ")

    def test_phase_filter_excludes_other_phases(self):
        result = self.route("security", phase="test")
        for step in result.steps:
            self.assertEqual(step["phase"], "test")

    def test_category_filter_excludes_other_categories(self):
        result = self.route("review", category="security")
        for step in result.steps:
            self.assertEqual(self.registry.skill(step["skill"]).category, "security")

    def test_answer_band_comes_before_support(self):
        result = self.route("the build is broken, fix it")
        bands = [step["band"] for step in result.steps]
        self.assertEqual(bands[0], "answer")

    def test_explain_reports_why_a_skill_did_not_match(self):
        detail = router.explain(self.registry, "tdd-workflow", "deploy the database")
        self.assertIn("score", detail)
        self.assertLess(detail["score"], 2.5)

    def test_every_skill_can_be_reached_by_its_own_name(self):
        for skill in self.registry.skills.values():
            with self.subTest(skill=skill.id):
                result = self.route(f"please run {skill.id}")
                self.assertEqual(result.steps[0]["skill"], skill.id)
