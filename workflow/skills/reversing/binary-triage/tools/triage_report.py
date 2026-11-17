"""Static triage report from supplied metadata.

Payload::

    {"metadata": {"sha256": "…", "kind": "pe", "arch": "x86_64", "size": 900000,
                  "entropy": 7.4, "imports": ["socket", "CreateProcessA"],
                  "sections_writable_executable": 2, "strings": ["UPX!", "http://x"]}}
"""

CAPABILITY_HINTS = {
    "network": ("socket", "connect", "winhttp", "curl", "getaddrinfo", "internetopen"),
    "process": ("createprocess", "fork", "execve", "system", "popen", "shellexecute"),
    "filesystem": ("createfile", "open", "write", "unlink", "remove"),
    "registry": ("regopenkey", "regsetvalue", "regcreatekey"),
    "crypto": ("cryptencrypt", "aes", "evp_", "bcrypt", "rijndael"),
    "antidebug": ("isdebuggerpresent", "ptrace", "checkremotedebugger",
                  "ntqueryinformationprocess"),
    "persistence": ("createservice", "schtasks", "crontab", "launchagent", "runonce"),
    "injection": ("virtualallocex", "writeprocessmemory", "createremotethread", "dlopen"),
}


def run(payload):
    meta = payload.get("metadata") or {}
    imports = [str(i) for i in meta.get("imports") or []]
    strings = [str(s) for s in meta.get("strings") or []]
    entropy = float(meta.get("entropy") or 0.0)
    wx = int(meta.get("sections_writable_executable") or 0)

    capabilities = []
    for capability in sorted(CAPABILITY_HINTS):
        needles = CAPABILITY_HINTS[capability]
        hits = [i for i in imports if any(n in i.lower() for n in needles)]
        if hits:
            capabilities.append({"capability": capability, "evidence": hits[:3]})

    indicators, score = [], 0
    if entropy >= 7.2:
        indicators.append(f"high entropy {entropy}: likely packed or encrypted")
        score += 3
    if wx > 0:
        indicators.append(f"{wx} writable+executable section(s)")
        score += 2
    if len(imports) < 10:
        indicators.append("very small import table")
        score += 2
    if any("UPX" in s for s in strings):
        indicators.append("UPX marker found")
        score += 2
    if any(c["capability"] in ("injection", "antidebug") for c in capabilities):
        indicators.append("injection or anti-debug capability")
        score += 3
    if any(s.startswith("http") for s in strings):
        indicators.append("embedded URL")
        score += 1

    risk = "high" if score >= 6 else "medium" if score >= 3 else "low"
    return {
        "ok": risk != "high",
        "sha256": meta.get("sha256"),
        "kind": meta.get("kind"),
        "arch": meta.get("arch"),
        "size": meta.get("size"),
        "risk": risk,
        "score": score,
        "capabilities": capabilities,
        "indicators": indicators,
        "next_step": ("isolated sandbox with network capture" if risk == "high" else
                      "deeper static analysis if the sample matters" if risk == "medium" else
                      "no indicators found; keep the hash and move on"),
        "unknowns": ["runtime behaviour", "network destinations", "persistence mechanism"],
        "advice": "never execute the sample outside an isolated environment",
    }
