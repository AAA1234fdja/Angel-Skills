"""Append-only, hash-chained journal of everything that actually ran.

Why a chain: an agent that can rewrite its own history cannot be audited. Each
line carries the hash of the previous line, so editing or deleting any entry
breaks verification and is reported as ``E_JOURNAL_CORRUPT``.

Format: JSON Lines, one object per event::

    {"seq": 0, "ts": 1762..., "kind": "run.start", "data": {...},
     "prev": "0000...", "hash": "a1b2..."}

The hash covers the canonical JSON of the entry without its ``hash`` field.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from .errors import JournalCorrupt

GENESIS = "0" * 16
KINDS = (
    "run.start", "run.end",
    "plan", "dispatch", "evidence", "result", "verdict", "meta",
    "tool.call", "tool.result",
    "gate", "error", "note",
)


@dataclass
class Entry:
    seq: int
    ts: float
    kind: str
    data: dict[str, Any]
    prev: str
    hash: str = ""

    def body(self) -> dict[str, Any]:
        return {"seq": self.seq, "ts": self.ts, "kind": self.kind,
                "data": self.data, "prev": self.prev}

    def compute(self) -> str:
        return hashlib.sha256(
            json.dumps(self.body(), sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:16]

    def finalise(self) -> "Entry":
        self.hash = self.compute()
        return self

    def to_dict(self) -> dict[str, Any]:
        return {**self.body(), "hash": self.hash}


class Journal:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._entries: list[Entry] = []
        self._lock_fd: int | None = None
        if self.path.exists():
            self._entries = list(self._read())

    # -- reading -----------------------------------------------------------
    def _read(self) -> Iterator[Entry]:
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise JournalCorrupt(f"journal line is not JSON: {exc}",
                                         hint="the file was edited outside the runtime",
                                         context={"line": line[:120]}) from exc
                yield Entry(seq=raw["seq"], ts=raw["ts"], kind=raw["kind"],
                            data=raw["data"], prev=raw["prev"], hash=raw.get("hash", ""))

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[Entry]:
        return iter(self._entries)

    @property
    def last_hash(self) -> str:
        return self._entries[-1].hash if self._entries else GENESIS

    # -- writing -----------------------------------------------------------
    def append(self, kind: str, data: dict[str, Any] | None = None) -> Entry:
        if kind not in KINDS:
            raise ValueError(f"unknown journal kind {kind!r}")
        entry = Entry(seq=len(self._entries), ts=time.time(), kind=kind,
                      data=data or {}, prev=self.last_hash).finalise()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._entries.append(entry)
        return entry

    # -- verification ------------------------------------------------------
    def verify(self) -> dict[str, Any]:
        """Recompute the chain. Returns a report instead of raising on first hit."""
        prev = GENESIS
        problems: list[str] = []
        for index, entry in enumerate(self._entries):
            if entry.seq != index:
                problems.append(f"seq {entry.seq} at position {index}: gaps or reordering")
            if entry.prev != prev:
                problems.append(f"seq {index}: prev {entry.prev} != expected {prev}")
            if entry.hash != entry.compute():
                problems.append(f"seq {index}: hash mismatch (entry edited)")
            prev = entry.hash
        return {
            "ok": not problems,
            "entries": len(self._entries),
            "last_hash": self.last_hash,
            "problems": problems,
        }

    def tail(self, count: int = 10) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._entries[-count:]]

    def find(self, kind: str) -> list[Entry]:
        return [e for e in self._entries if e.kind == kind]


def open_journal(root: Path | str, run_id: str) -> Journal:
    base = Path(root) / ".workflow" / "journal"
    return Journal(base / f"{run_id}.jsonl")


def list_journals(root: Path | str) -> list[dict[str, Any]]:
    base = Path(root) / ".workflow" / "journal"
    if not base.is_dir():
        return []
    rows = []
    for file in sorted(base.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
        journal = Journal(file)
        report = journal.verify()
        rows.append({
            "run": file.stem,
            "entries": report["entries"],
            "ok": report["ok"],
            "last": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(file.stat().st_mtime)),
        })
    return rows
