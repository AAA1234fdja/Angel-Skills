"""Journal tests: the record is the evidence, so it must resist editing."""

import json
import shutil
import tempfile

from support import AngelTestCase, Path, journal


class JournalTests(AngelTestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="angel-journal-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_entries_chain_from_genesis(self):
        book = journal.open_journal(self.root, "run-1")
        book.append("run.start", {"objective": "x"})
        book.append("plan", {"steps": 2})
        book.append("run.end", {"verdict": "pass"})
        report = book.verify()
        self.assertTrue(report["ok"])
        self.assertEqual(report["entries"], 3)
        self.assertEqual(report["last_hash"], book.last_hash)

    def test_a_tampered_entry_is_detected(self):
        book = journal.open_journal(self.root, "run-2")
        book.append("run.start", {"objective": "x"})
        book.append("run.end", {"verdict": "pass"})
        path = Path(book.path)
        lines = path.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["data"]["objective"] = "something else"
        lines[0] = json.dumps(first)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        report = journal.open_journal(self.root, "run-2").verify()
        self.assertFalse(report["ok"])
        self.assertTrue(report["problems"])

    def test_a_removed_entry_breaks_the_chain(self):
        book = journal.open_journal(self.root, "run-3")
        for index in range(3):
            book.append("note", {"i": index})
        path = Path(book.path)
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="utf-8")
        report = journal.open_journal(self.root, "run-3").verify()
        self.assertFalse(report["ok"])

    def test_journals_are_listable_and_independent(self):
        for name in ("a", "b"):
            book = journal.open_journal(self.root, name)
            book.append("run.start", {"run": name})
        found = {row["run"] for row in journal.list_journals(self.root)}
        self.assertEqual(found, {"a", "b"})

    def test_entries_are_json_lines_with_a_stable_shape(self):
        book = journal.open_journal(self.root, "run-4")
        entry = book.append("dispatch", {"step_id": "s1"})
        data = entry.to_dict()
        self.assertEqual(data["kind"], "dispatch")
        self.assertEqual(data["seq"], 0)
        self.assertEqual(data["prev"], journal.GENESIS)
        self.assertRegex(data["hash"], r"^[0-9a-f]{16}$")
        row = json.loads(Path(book.path).read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(set(row), {"seq", "ts", "kind", "data", "prev", "hash"})

    def test_an_unknown_kind_is_refused(self):
        book = journal.open_journal(self.root, "run-5")
        with self.assertRaises(ValueError):
            book.append("made-up-kind", {})
