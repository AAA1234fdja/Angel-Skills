"""Contract tests: versions are immutable and a breaking change needs a major."""

import json
import shutil
import tempfile

from support import AngelTestCase, REAL_ROOT, contracts, Path

SCHEMA_V1 = {
    "type": "object",
    "required": ["name", "version"],
    "additionalProperties": False,
    "properties": {"name": {"type": "string"}, "version": {"type": "string"},
                   "note": {"type": "string"}},
}


class ContractTests(AngelTestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="angel-contracts-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        contracts.write_contract(self.root, "demo", "1.0.0", SCHEMA_V1)

    def test_write_then_resolve_round_trips(self):
        contract = contracts.resolve(self.root, "demo")
        self.assertEqual(contract.version, "1.0.0")
        contract.validate({"name": "a", "version": "1"})

    def test_a_version_cannot_be_overwritten(self):
        self.assert_angel_error("E_CONTRACT_INVALID", contracts.write_contract,
                                self.root, "demo", "1.0.0", SCHEMA_V1)

    def test_unknown_contract_and_version_are_rejected(self):
        self.assert_angel_error("E_CONTRACT_INVALID", contracts.resolve,
                                self.root, "nope")
        self.assert_angel_error("E_CONTRACT_INVALID", contracts.resolve,
                                self.root, "demo", "9.9.9")

    def test_validation_reports_the_offending_path(self):
        error = self.assert_angel_error(
            "E_CONTRACT_INVALID", contracts.latest(self.root, "demo").validate,
            {"name": "a", "extra": True})
        self.assertIn("version", error.message)

    def test_adding_an_optional_field_is_a_minor_bump(self):
        widened = json.loads(json.dumps(SCHEMA_V1))
        widened["properties"]["extra"] = {"type": "string"}
        contracts.write_contract(self.root, "demo", "1.1.0", widened)
        result = contracts.diff_versions(self.root, "demo", "1.0.0", "1.1.0")
        self.assertEqual(result["required_bump"], "minor")
        self.assertTrue(result["ok"])

    def test_removing_a_field_without_a_major_bump_is_flagged(self):
        narrower = json.loads(json.dumps(SCHEMA_V1))
        del narrower["properties"]["note"]
        contracts.write_contract(self.root, "demo", "1.1.0", narrower)
        result = contracts.diff_versions(self.root, "demo", "1.0.0", "1.1.0")
        self.assertEqual(result["required_bump"], "major")
        self.assertFalse(result["ok"])
        report = contracts.validate_all(self.root)
        self.assertTrue(any(not row["ok"] for row in report))

    def test_adding_a_required_field_is_breaking(self):
        stricter = json.loads(json.dumps(SCHEMA_V1))
        stricter["required"].append("note")
        contracts.write_contract(self.root, "demo", "2.0.0", stricter)
        result = contracts.diff_versions(self.root, "demo", "1.0.0", "2.0.0")
        self.assertEqual(result["required_bump"], "major")
        self.assertTrue(result["ok"], "a major bump is allowed to break")

    def test_compatible_accepts_same_major_only(self):
        self.assertTrue(contracts.compatible(self.root, "demo", "1.0.0"))
        self.assertFalse(contracts.compatible(self.root, "demo", "2.0.0"))

    def test_the_shipped_contracts_are_all_valid(self):
        report = contracts.validate_all(REAL_ROOT)
        self.assertTrue(report)
        for row in report:
            with self.subTest(contract=row["contract"]):
                self.assertTrue(row["ok"], row)

    def test_skill_declared_contracts_exist(self):
        found = contracts.discover(REAL_ROOT)
        for skill in self.registry.skills.values():
            for reference in skill.contracts:
                name, _, version = reference.partition("@")
                with self.subTest(skill=skill.id, contract=reference):
                    self.assertIn(name, found, f"{skill.id} declares {reference}")
                    if version:
                        versions = [c.version for c in found[name]]
                        self.assertIn(version, versions)

    def test_unsupported_schema_keyword_is_rejected_loudly(self):
        # a validator that silently ignores a keyword is worse than none, so an
        # unsupported keyword must fail at discovery time, not pass quietly.
        bad = {"type": "object", "properties": {"a": {"type": "string", "oneOf": []}}}
        self.assert_angel_error("E_SCHEMA_UNSUPPORTED", contracts.write_contract,
                                self.root, "bad", "1.0.0", bad)
