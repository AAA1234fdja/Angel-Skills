"""Classify an artefact from its header bytes and plan the next step.

Payload::

    {"artefact": {"path": "sample.bin", "size": 1048576,
                  "head_hex": "7f454c46", "strings": ["UPX!", "/api/v2"]}}

No file I/O: the head bytes and strings are supplied, so the tool is honest about
what it is looking at and safe to run anywhere.
"""

MAGIC = (
    ("7f454c46", "elf", "ELF binary", "readelf -a, then strings"),
    ("4d5a", "pe", "Windows PE/executable", "objdump -p, then strings"),
    ("cafebabe", "macho-fat", "Mach-O universal", "otool -l per architecture"),
    ("cffaedfe", "macho", "Mach-O 64", "otool -l, nm -m"),
    ("504b0304", "zip", "ZIP archive (or jar/docx/apk)", "unzip -l, look for the manifest"),
    ("1f8b", "gzip", "gzip stream", "zcat and re-triage the result"),
    ("89504e47", "png", "PNG image", "exiftool, then steganalysis if relevant"),
    ("25504446", "pdf", "PDF document", "pdfinfo, then qpdf --qdf"),
    ("52494646", "riff", "RIFF container (wav/avi/webp)", "inspect the fourcc"),
)
PACKERS = (("UPX!", "upx -d on a copy"), ("PyInstaller", "pyinstxtractor"),
           ("dnSpy", "decompile with ilspy"), ("Electron", "extract app.asar"))
INTERESTING = ("http", "token", "key", "secret", "api", "license", "trial",
               "serial", "authorization", "/v1", "/v2")


def run(payload):
    artefact = payload.get("artefact") or {}
    head = str(artefact.get("head_hex") or "").lower().replace(" ", "")
    size = int(artefact.get("size") or 0)
    strings = [str(s) for s in artefact.get("strings") or []]

    kind, label, step = "unknown", "unrecognised", "hexdump the first 256 bytes"
    for magic, key, description, next_step in MAGIC:
        if head.startswith(magic):
            kind, label, step = key, description, next_step
            break

    packers = [{"signal": signal, "action": action}
               for signal, action in PACKERS
               if any(signal.lower() in s.lower() for s in strings)]
    leads = sorted({s for s in strings
                    if any(word in s.lower() for word in INTERESTING)})[:20]
    endpoints = [s for s in strings if s.startswith(("http://", "https://", "/api/"))][:10]

    return {
        "ok": True,
        "kind": kind,
        "label": label,
        "size": size,
        "confidence": "high" if kind != "unknown" else "low",
        "next_step": ("decompress first, then re-triage" if kind in ("gzip", "zip") else step),
        "packers": packers,
        "interesting_strings": leads,
        "endpoints": endpoints,
        "advice": "cite the artefact for every claim, or label it as a hypothesis",
        "plan": [
            "do not execute outside an isolated environment",
            f"static: {step}",
            "map strings to hypotheses, each citing an artefact",
            "dynamic in a sandbox with network capture, only if needed",
        ],
    }
