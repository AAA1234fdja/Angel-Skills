"""Style and silence smells over provided file contents.

Payload: ``{"files": {"src/a.py": "…"}, "max_function_lines": 40,
           "max_line_length": 120}``

Pure text analysis: no filesystem, no imports of the analysed language. It is a
first pass that catches the patterns a formatter will never see.
"""

BARE_EXCEPT = ("except:", "except Exception:", "catch (e) {}", "catch {}", "catch (_)")
SILENT = ("pass", "return None", "return null", "continue", "// ignore", "# noqa")


def _indent_of(line):
    return len(line) - len(line.lstrip(" 	"))


def _functions(lines):
    """Yield (name, start, end, length) for def/function/func blocks by indent."""
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        marker = None
        for prefix in ("def ", "async def ", "function ", "func "):
            if stripped.startswith(prefix):
                marker = prefix
                break
        if not marker:
            continue
        name = stripped[len(marker):].split("(")[0].strip()
        base = _indent_of(line)
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if not lines[j].strip():
                continue
            if _indent_of(lines[j]) <= base:
                end = j
                break
        out.append((name, i, end, end - i))
    return out


def run(payload):
    files = payload.get("files") or {}
    max_fn = int(payload.get("max_function_lines", 40))
    max_len = int(payload.get("max_line_length", 120))
    findings = []

    for path in sorted(files):
        text = files[path]
        if not isinstance(text, str):
            continue
        lines = text.splitlines()
        if len(lines) > 600:
            findings.append({"file": path, "kind": "file_too_long", "line": 0,
                             "detail": f"{len(lines)} lines"})
        for number, line in enumerate(lines, 1):
            if len(line) > max_len:
                findings.append({"file": path, "kind": "line_too_long", "line": number,
                                 "detail": f"{len(line)} chars"})
            if "	" in line[: _indent_of(line) + 1]:
                findings.append({"file": path, "kind": "tab_indent", "line": number,
                                 "detail": "mixed indentation"})
            for pattern in BARE_EXCEPT:
                if pattern in line:
                    following = " ".join(l.strip() for l in lines[number: number + 2])
                    if any(sil in following for sil in SILENT):
                        findings.append({"file": path, "kind": "silent_exception",
                                         "line": number, "detail": "exception caught and ignored"})
            if "TODO" in line and "(" not in line:
                findings.append({"file": path, "kind": "todo_without_owner", "line": number,
                                 "detail": "TODO without owner or issue"})
        for name, start, _end, length in _functions(lines):
            if length > max_fn:
                findings.append({"file": path, "kind": "function_too_long", "line": start + 1,
                                 "detail": f"{name} is {length} lines"})
            if name and (name[0].isupper() and "_" not in name and len(name) < 3):
                findings.append({"file": path, "kind": "suspicious_name", "line": start + 1,
                                 "detail": name})

    kinds = {}
    for finding in findings:
        kinds[finding["kind"]] = kinds.get(finding["kind"], 0) + 1
    return {
        "ok": not any(k in kinds for k in ("silent_exception", "function_too_long")),
        "files": len(files),
        "findings": findings[:200],
        "counts": kinds,
        "advice": ("clean enough to review" if not findings else
                   "fix silent_exception and function_too_long before review"),
    }
