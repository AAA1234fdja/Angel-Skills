"""Lint a proposed skill before it is written to disk.

Payload::

    {"skill": {"id": "x", "category": "engineering",
               "frontmatter": {"description": "…"},
               "sections": ["When to Use", "Procedure", "Exit Criteria"],
               "manifest": {"phase": "test", "verbs": ["test"]}}}
"""

import re

REQUIRED_SECTIONS = ("When to Use", "Procedure", "Exit Criteria")
ADVISED_SECTIONS = ("When Not to Use", "Common Failures")
PHASES = ("plan", "design", "research", "implement", "test", "review",
          "verify", "debug", "audit", "document", "meta")
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def run(payload):
    skill = payload.get("skill") or {}
    skill_id = str(skill.get("id") or "")
    category = str(skill.get("category") or "")
    frontmatter = skill.get("frontmatter") or {}
    sections = [str(s) for s in skill.get("sections") or []]
    manifest = skill.get("manifest") or {}

    errors, warnings = [], []

    if not ID_RE.match(skill_id):
        errors.append("id must match ^[a-z0-9]+(-[a-z0-9]+)*$")
    if not category:
        errors.append("category is required")

    description = str(frontmatter.get("description") or "")
    if "Use when" not in description:
        errors.append("description has no trigger ('Use when')")
    if len(description) > 700:
        errors.append(f"description is {len(description)} chars (max 700)")

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"missing section '{section}'")
    for section in ADVISED_SECTIONS:
        if section not in sections:
            warnings.append(f"missing advised section '{section}'")

    phase = str(manifest.get("phase") or frontmatter.get("phase") or "")
    if phase not in PHASES:
        errors.append(f"invalid phase {phase!r}")
    if not manifest.get("verbs"):
        warnings.append("manifest declares no verbs: routing will be weaker")
    if not manifest.get("triggers"):
        warnings.append("manifest declares no triggers")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "ready": not errors and not warnings,
        "advice": ("ready to register" if not errors else
                   "fix errors: the runtime will reject this skill"),
    }
