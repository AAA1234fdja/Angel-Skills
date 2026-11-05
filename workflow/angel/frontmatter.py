"""Frontmatter parsing and emission (YAML subset, no dependency).

The subset is deliberately small: scalars, booleans, ints, floats, inline lists
(``[a, b]``), block lists (``- item``) and one level of nested mapping. That is
everything a skill header legitimately needs, and keeping it small is what makes
validation deterministic.
"""

from __future__ import annotations

import re
from typing import Any

_FENCE = "---"
_KEY = re.compile(r"^([A-Za-z0-9_.-]+):\s*(.*)$")


def unquote(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        inner = text[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\") if text[0] == '"' else inner
    return text


def coerce(value: str) -> Any:
    text = value.strip()
    if text == "":
        return None
    if text in ("true", "yes", "on"):
        return True
    if text in ("false", "no", "off"):
        return False
    if text in ("null", "~"):
        return None
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [coerce(part) for part in inner.split(",")]
    try:
        if re.fullmatch(r"-?\d+", text):
            return int(text)
        if re.fullmatch(r"-?\d+\.\d+", text):
            return float(text)
    except ValueError:  # pragma: no cover - regex guards this
        pass
    return unquote(text)


def parse(text: str) -> tuple[dict[str, Any], str, str | None]:
    """Return ``(frontmatter, body, error)``.

    ``error`` is a plain string so callers can decide the taxonomy code; this
    module never raises.
    """
    if not text.startswith(_FENCE):
        return {}, text, "missing opening ---"
    end = text.find("\n" + _FENCE, 3)
    if end == -1:
        return {}, text, "unterminated frontmatter"
    raw = text[3:end]
    body = text[end + 4:]
    if body.startswith("\n"):
        body = body[1:]

    data: dict[str, Any] = {}
    parent: str | None = None
    list_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if list_key is None:
                return {}, body, f"list item without a key: {stripped[:40]!r}"
            bucket = data if parent is None else data[parent]
            if not isinstance(bucket.get(list_key), list):
                bucket[list_key] = []
            bucket[list_key].append(coerce(stripped[2:]))
            continue
        match = _KEY.match(stripped)
        if not match:
            return {}, body, f"unparseable line: {stripped[:40]!r}"
        key, value = match.group(1), match.group(2)
        nested = line.startswith(" ") or line.startswith("\t")
        if nested and parent:
            bucket = data[parent]
            if not isinstance(bucket, dict):
                bucket = {}
                data[parent] = bucket
            bucket[key] = coerce(value) if value else {}
        elif value == "":
            data[key] = {}
            parent = key
            list_key = key
        else:
            data[key] = coerce(value)
            parent = None
            list_key = None
    return data, body, None


def emit(data: dict[str, Any]) -> str:
    """Serialise a flat-ish mapping back to the same subset."""
    lines = [_FENCE]
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub, subvalue in value.items():
                lines.append(f"  {sub}: {_scalar(subvalue)}")
        elif isinstance(value, list):
            lines.append(f"{key}: [{', '.join(_scalar(v) for v in value)}]")
        else:
            lines.append(f"{key}: {_scalar(value)}")
    lines.append(_FENCE)
    return "\n".join(lines)


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if any(ch in text for ch in ":#[]\"'\n"):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def sections(body: str) -> dict[str, str]:
    """Split a markdown body into ``{heading: text}`` using level-2 headings."""
    out: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                out[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf).strip()
    return out
