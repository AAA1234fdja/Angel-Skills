"""Angel workflow runtime — stdlib only.

A skill is a *folder*, not a markdown file: it carries its procedure
(``SKILL.md``), its composition (``skill.json``) and, when the work can be
automated, executable tools under ``tools/``.

Layers
------
registry    discover and validate the package
protocols   typed, versioned envelopes for every hand-off
errors      one taxonomy, one policy, one place
contracts   JSON-schema subset + breaking-change detection
tools       discover, authorise and execute per-skill tools
router      map a need to the smallest set of skills that can satisfy it
journal     append-only, hash-chained trace of what actually ran
runner      execute a routed plan with budget, gates and policy
agents      an agent is an API; every API may call subagents
cli         the single entry point
"""

__version__ = "0.5.0"
PACKAGE = "workflow"
