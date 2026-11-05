"""WCAG contrast ratios for declared colour pairs.

Payload:: ``{"pairs": [{"fg": "#777777", "bg": "#ffffff", "large": false}]}``
"""


def _rgb(value):
    text = str(value).strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return None
    try:
        return tuple(int(text[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return None


def _luminance(rgb):
    def channel(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def run(payload):
    pairs = list(payload.get("pairs") or [])
    rows, failures = [], []

    for pair in pairs:
        fg = _rgb(pair.get("fg"))
        bg = _rgb(pair.get("bg"))
        large = bool(pair.get("large"))
        if not fg or not bg:
            rows.append({"fg": pair.get("fg"), "bg": pair.get("bg"), "error": "invalid colour"})
            continue
        l1, l2 = _luminance(fg), _luminance(bg)
        lighter, darker = max(l1, l2), min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)
        required = 3.0 if large else 4.5
        ok = ratio >= required
        rows.append({"fg": pair.get("fg"), "bg": pair.get("bg"),
                     "ratio": round(ratio, 2), "required": required,
                     "large": large, "ok": ok})
        if not ok:
            failures.append(f"{pair.get('fg')} on {pair.get('bg')}: {ratio:.2f} < {required}")

    return {
        "ok": not failures,
        "pairs": rows,
        "failures": failures,
        "advice": ("all pairs meet AA" if not failures else
                   "raise contrast: " + failures[0]),
    }
