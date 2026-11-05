"""Shared helpers for the workflow test suite.

Every test module imports from here so that path setup, the loaded registry and
the temporary-package builder are defined exactly once. A test that builds its own
environment is a test that will drift from the real one.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

WORKFLOW = Path(__file__).resolve().parents[1]
if str(WORKFLOW) not in sys.path:
    sys.path.insert(0, str(WORKFLOW))

from angel import contracts, journal, protocols, registry, router, tools  # noqa: E402
from angel.errors import AngelError, POLICY  # noqa: E402

#: the real, shipped package — tests never mock it, they exercise it
REAL_ROOT = WORKFLOW


def load_real() -> registry.Registry:
    return registry.load(REAL_ROOT)


class TempPackage:
    """A throwaway package directory for tests that must break something.

    Copies the real categories.json and only the skill folders a test names, so a
    whole registry loads in milliseconds and a test can mutate it freely.
    """

    def __init__(self, skills: list[str] | None = None) -> None:
        self.skills = skills
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix="angel-test-"))
        source = REAL_ROOT / "categories.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        wanted = set(self.skills or [])
        if wanted:
            for category in data["categories"]:
                kept = [s for s in category["skills"] if s["id"] in wanted]
                category["skills"] = kept
                if not kept:
                    category["status"] = "activa"
        (self.path / "categories.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        for folder in (REAL_ROOT / "skills").glob("*/*"):
            if not wanted or folder.name in wanted:
                shutil.copytree(folder, self.path / "skills" / folder.parent.name / folder.name)
        if (REAL_ROOT / "contracts").is_dir():
            shutil.copytree(REAL_ROOT / "contracts", self.path / "contracts")
        return self.path

    def __exit__(self, *exc: Any) -> None:
        if self.path and self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)


class AngelTestCase(unittest.TestCase):
    """Base class with the assertions every module here needs."""

    maxDiff = 4000

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_real()

    def assert_angel_error(self, code: str, fn, *args, **kwargs) -> AngelError:
        """Assert that ``fn`` raises an AngelError whose code matches ``code``."""
        with self.assertRaises(AngelError) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code,
                         f"expected {code}, got {caught.exception.code}: {caught.exception}")
        return caught.exception


__all__ = [
    "AngelTestCase", "TempPackage", "REAL_ROOT", "WORKFLOW", "load_real",
    "contracts", "journal", "protocols", "registry", "router", "tools", "POLICY",
    "AngelError", "json", "Path", "unittest",
]
