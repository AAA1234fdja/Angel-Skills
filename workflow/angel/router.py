"""Routing: from a stated need to the smallest set of skills that can satisfy it.

The router is deliberately *not* an LLM call. It is a scored match over the
triggers, verbs, artefacts and phases that every skill declares in its
``skill.json``. That makes routing reproducible, auditable and free — and it
means a wrong route is a data bug you can fix in a manifest, not a prompt
mystery.

Scoring (all additive, deterministic):

    trigger hit         3.0 per phrase, counted once even when one trigger is a
                        substring of another ("build is broken" inside
                        "the build is broken")
    trigger in clause   2.0 extra when the trigger sits in the clause of a verb the
                        skill declares — "review the security of the diff" gives
                        security-review the clause bonus, a skill that merely shares
                        the word "review" does not get one
    keyword hit         0.7 per token, 1.4 for a multi-word phrase, x0.4 outside a
                        declared verb's clause, total capped at 3.0
    verb match          2.2 for the first declared verb, 0.6 for each extra one;
                        a verb alone never reaches the default threshold, so a skill
                        must corroborate the verb with a trigger or a keyword
    phase filter        0 when the caller asks for a phase and the skill is not in it
    category boost      0.5 when the need names the category
    explicit id         100 (a named skill always wins)

Negated clauses are masked before matching: "sin tests" and "no tests" never
produce a test skill.

A skill scoring zero is not offered. The result carries the reasons, so a user
can see *why* a skill was chosen instead of trusting a black box.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .errors import AngelError
from .registry import Skill, Registry

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is",
    "are", "be", "it", "this", "that", "my", "we", "you", "i", "please", "can",
    "want", "need", "should", "would", "make", "do", "does", "how", "what",
    "que", "de", "la", "el", "los", "las", "un", "una", "y", "o", "para", "por",
    "con", "sin", "en", "es", "son", "me", "mi", "se", "lo",
}

WEIGHTS = {
    "trigger": 3.0,
    "clause": 2.0,
    "keyword": 0.7,
    "phrase": 1.4,
    "keyword_cap": 3.0,
    "verb": 2.2,
    "verb_extra": 0.6,
    "phase": 1.5,
    "category": 0.5,
    "explicit": 100.0,
}

#: how far after a verb hint its clause is considered to extend
CLAUSE_CHARS = 64
#: words that invert the meaning of what follows them
NEGATORS = ("no ", "sin ", "without ", "don't ", "do not ", "not ")

#: The runtime is English, the operator is not. Spanish terminology is mapped to
#: the English word the manifests already use, so a need written in Spanish routes
#: like its translation without duplicating every skill in two languages.
ES_TERMS = {
    "arreglar": "fix", "arregla": "fix", "corregir": "fix", "falla": "broken",
    "fallo": "error", "error": "error", "roto": "broken", "depurar": "debug",
    "revisar": "review", "revision": "review", "revisa": "review",
    "seguridad": "security", "seguro": "secure", "secreto": "secret",
    "dependencia": "dependency", "dependencias": "dependency",
    "prueba": "test", "pruebas": "test", "testear": "test", "cobertura": "coverage",
    "documentar": "document", "documentacion": "documentation", "readme": "readme",
    "migrar": "migrate", "migracion": "migration", "esquema": "schema",
    "tabla": "table", "datos": "data", "consultas": "query", "consulta": "query",
    "indice": "index", "cache": "cache", "rendimiento": "performance",
    "lento": "slow", "optimizar": "optimize", "refactorizar": "refactor",
    "limpiar": "clean", "auditar": "audit", "auditoria": "audit",
    "rendir": "audit", "inventario": "inventory", "diseñar": "design",
    "disenar": "design", "planificar": "plan", "plan": "plan",
    "agente": "agent", "contexto": "context", "protocolo": "protocol",
    "contrato": "contract", "contratos": "contract", "mensaje": "message",
    "mensajes": "message", "binario": "binary", "binarios": "binary",
    "ingenieria": "reverse", "inversa": "reverse", "trafico": "traffic",
    "api": "api", "endpoint": "api", "accesibilidad": "accessibility",
    "desplegar": "deploy", "rendimiento_extremo": "performance",
    "registrar": "register", "nueva": "new", "nuevo": "new", "habilidad": "skill",
    "habilidades": "skill", "flujo": "workflow", "bucle": "loop",
    "reintento": "retry", "reintentos": "retry", "incidente": "incident",
    "incidentes": "incident", "recuperacion": "recovery", "eval": "eval",
    "evaluacion": "eval", "medir": "measure", "metricas": "measure",
    "presupuesto": "budget", "tarea": "task", "tareas": "task",
    "caché": "cache", "version": "version", "versionar": "version",
    "cambio": "changelog", "changelog": "changelog", "notas": "notes",
}

#: verbs a need can express; a skill declares which ones it serves
VERBS = (
    "implement", "fix", "review", "test", "verify", "refactor", "optimize",
    "design", "plan", "document", "migrate", "audit", "secure", "debug",
    "investigate", "extract", "translate", "generate", "measure", "register",
    "ship", "validate",
)

VERB_HINTS = {
    "implement": ("implement", "build", "create", "add", "write", "code"),
    "fix": ("fix", "bug", "broken", "error", "fails", "repair"),
    "review": ("review", "critique", "pr", "diff"),
    "test": ("test", "tdd", "coverage", "spec"),
    "verify": ("verify", "validation", "gate", "check"),
    "refactor": ("refactor", "clean", "dead code", "duplicate"),
    "optimize": ("optimize", "slow", "performance", "latency", "speed"),
    "design": ("design", "architecture", "adr", "interface"),
    "plan": ("plan", "roadmap", "break down", "decompose"),
    "document": ("document", "docs", "readme", "changelog"),
    "migrate": ("migrate", "migration", "upgrade", "port"),
    "audit": ("audit", "inventory", "assess", "diagnose"),
    "secure": ("security", "secret", "vulnerability", "hardening", "exploit"),
    "debug": ("debug", "diagnose", "trace", "why"),
    "investigate": ("investigate", "reverse", "understand", "explore", "osint"),
    "extract": ("extract", "parse", "scrape", "unwrap"),
    "translate": ("translate", "i18n", "localize"),
    "generate": ("generate", "scaffold", "template", "boilerplate"),
    "measure": ("measure", "benchmark", "eval", "metric"),
    "register": ("register", "new skill", "authoring", "add skill"),
    "ship": ("ship", "release", "deploy", "publish", "launch", "rollout"),
    "validate": ("validate", "conforms", "well formed", "against the schema"),
}


#: the lifecycle order a plan is presented in (see `answer_band`)
PHASE_ORDER = ("plan", "design", "research", "implement", "test", "review",
               "verify", "ship", "debug", "audit", "document", "meta")


@dataclass
class Match:
    skill_id: str
    score: float
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"skill": self.skill_id, "score": round(self.score, 2), "reasons": self.reasons}


@dataclass
class Route:
    need: str
    matches: list[Match]
    steps: list[dict[str, Any]]
    budget: dict[str, Any] = field(default_factory=dict)
    unmatched_verbs: list[str] = field(default_factory=list)

    @property
    def skill_ids(self) -> list[str]:
        return [m.skill_id for m in self.matches]

    def to_dict(self) -> dict[str, Any]:
        return {
            "need": self.need,
            "matches": [m.to_dict() for m in self.matches],
            "steps": self.steps,
            "budget": self.budget,
            "unmatched_verbs": self.unmatched_verbs,
            "skills": self.skill_ids,
        }


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9][a-z0-9+#._-]*", text.lower())
            if t not in STOPWORDS and len(t) > 1]


def mask_negations(need: str) -> str:
    """Blank out the clause after a negator, keeping the string length stable.

    Matching against the masked text means "sin tests" cannot trigger a test skill,
    while positions still line up with the original need.
    """
    low = need.lower()
    chars = list(low)
    for negator in NEGATORS:
        start = 0
        while True:
            found = low.find(negator, start)
            if found < 0:
                break
            end = found + len(negator)
            while end < len(low) and low[end] not in ",.;:()":
                chars[end] = " " if not low[end].isspace() else " "
                end += 1
            start = end
    return "".join(chars)


def stem(word: str) -> str:
    """A deliberately shallow singular: enough for tests/test, queries/query.

    Stemming is not the goal — a full stemmer hides matching bugs. This only removes
    the plural the operator typed so the keyword a manifest declares still hits.
    """
    word = word.lower()
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def translate(need: str) -> str:
    """Append the English terms a Spanish need is really asking for."""
    words = re.findall(r"[a-záéíóúñü]+", need.lower())
    mapped = [ES_TERMS[w] for w in words if w in ES_TERMS]
    return " ".join(dict.fromkeys(mapped))


def normalise(need: str) -> str:
    """Mask negations, then append the translated vocabulary of the need."""
    masked = mask_negations(need)
    extra = translate(masked)
    return f"{masked} {extra}".strip()


def verb_clauses(need: str) -> list[tuple[int, int, str]]:
    """Spans of text that follow a verb hint, tagged with the verb they serve."""
    low = need.lower()
    spans: list[tuple[int, int, str]] = []
    for verb, hints in VERB_HINTS.items():
        for hint in hints:
            start = 0
            while True:
                found = low.find(hint, start)
                if found < 0:
                    break
                spans.append((found, min(len(low), found + len(hint) + CLAUSE_CHARS), verb))
                start = found + len(hint)
    return spans


def _in_clause(spans: list[tuple[int, int, str]], position: int, declared: set[str]) -> bool:
    return any(start <= position <= end and verb in declared for start, end, verb in spans)


def detect_verbs(need: str) -> list[str]:
    found = []
    low = need.lower()
    for verb, hints in VERB_HINTS.items():
        if any(hint in low for hint in hints):
            found.append(verb)
    return found


def score_skill(skill: Skill, need: str, *, verbs: list[str] | None = None,
                phase: str | None = None, category: str | None = None) -> Match:
    declared = {str(v) for v in skill.manifest.get("verbs") or []}
    original = need.lower()
    low = normalise(need)
    spans = verb_clauses(low)
    need_tokens = {stem(t) for t in tokens(low)}
    verbs = verbs if verbs is not None else detect_verbs(low)
    match = Match(skill.id, 0.0)

    # explicit mention wins outright
    if skill.id in original:
        match.score += WEIGHTS["explicit"]
        match.reasons.append("named explicitly")

    # triggers: longest first, no double counting, clause aware
    covered: list[str] = []
    for trigger in sorted(skill.triggers, key=len, reverse=True):
        t_low = trigger.lower()
        if not t_low or t_low in covered:
            continue
        position = low.find(t_low)
        if position < 0:
            continue
        match.score += WEIGHTS["trigger"]
        match.reasons.append(f"trigger: {trigger}")
        if _in_clause(spans, position, declared):
            match.score += WEIGHTS["clause"]
            match.reasons.append(f"trigger in clause of a declared verb")
        covered.append(t_low)

    # keywords, with multi-word phrases counted as one stronger hit
    keywords = [str(k).lower() for k in skill.manifest.get("keywords") or []]
    keyword_score = 0.0
    hits: list[str] = []
    for keyword in sorted(keywords, key=len, reverse=True):
        if not keyword:
            continue
        if " " in keyword:
            position = low.find(keyword)
            if position < 0:
                continue
            keyword_score += WEIGHTS["phrase"]
            hits.append(keyword)
            continue
        if stem(keyword) not in need_tokens:
            continue
        position = low.find(keyword)
        weight = WEIGHTS["keyword"]
        if position >= 0 and not _in_clause(spans, position, declared):
            weight *= 0.4
        keyword_score += weight
        hits.append(keyword)
    if hits:
        match.score += min(keyword_score, WEIGHTS["keyword_cap"])
        match.reasons.append("keywords: " + ", ".join(sorted(hits)))

    # verb
    verb_hit = declared & set(verbs)
    if verb_hit:
        match.score += WEIGHTS["verb"] + WEIGHTS["verb_extra"] * (len(verb_hit) - 1)
        match.reasons.append("verbs: " + ", ".join(sorted(verb_hit)))

    # phase: a requested phase is a filter, not a bonus. Scoring it as a bonus
    # leaves other phases in the answer, which is the opposite of what the caller
    # asked for.
    if phase and skill.phase != phase:
        match.score = 0.0
        match.reasons = [f"excluded: phase {phase}"]
    elif phase:
        match.score += WEIGHTS["phase"]
        match.reasons.append(f"phase: {phase}")

    # category
    if category and skill.category == category:
        match.score += WEIGHTS["category"]
        match.reasons.append(f"category: {category}")
    elif category and category != skill.category:
        match.score = 0.0
        match.reasons = [f"excluded: category {category}"]

    # a skill can forbid itself for certain needs
    for avoid in skill.routing.get("not_for") or []:
        if str(avoid).lower() in original:
            match.score = 0.0
            match.reasons = [f"excluded by not_for: {avoid}"]
            break

    return match


def route(registry: Registry, need: str, *, limit: int = 5, phase: str | None = None,
          category: str | None = None, min_score: float = 2.5) -> Route:
    """Pick skills for a need and lay them out as ordered steps.

    ``min_score`` has to be positive: a comparator bug against a lazy default once
    let everything through, so the value is now validated instead of trusted.
    """
    if not need or not need.strip():
        raise AngelError("routing needs a non-empty objective",
                         hint="pass a sentence describing the work", code="E_ROUTE_EMPTY")
    if min_score <= 0:
        raise AngelError("min_score must be greater than zero",
                         hint="use 2.5 to require a corroborated match, "
                              "or inspect near misses with `workflow route --explain`")

    verbs = detect_verbs(normalise(need))
    matches = [score_skill(s, need, verbs=verbs, phase=phase, category=category)
               for s in registry.skills.values()]
    matches = [m for m in matches if m.score >= min_score]
    matches.sort(key=lambda m: (-m.score, m.skill_id))

    chosen = matches[:limit]
    unmatched = [v for v in verbs
                 if not any(v in {str(x) for x in registry.skill(m.skill_id).manifest.get("verbs") or []}
                            for m in chosen)]

    steps = build_steps(registry, chosen)
    budget = {
        "steps": len(steps),
        "skills": len(chosen),
        "max_tools": sum(len(registry.skill(m.skill_id).tools) for m in chosen),
    }
    return Route(need=need, matches=chosen, steps=steps, budget=budget,
                 unmatched_verbs=unmatched)


def build_steps(registry: Registry, matches: list[Match]) -> list[dict[str, Any]]:
    """Order chosen skills by the lifecycle, but keep the strong matches first.

    Lifecycle order alone is wrong for a need like "the build is broken": it would
    put every implement-phase skill before the one skill that actually answered.
    So the ordering is banded: skills scoring at least 60% of the best match are
    the answer and come first in lifecycle order; the rest are supporting skills
    and come after, also in lifecycle order. A single threshold would either hide
    the support or bury the answer.
    """
    order = {phase: i for i, phase in enumerate(PHASE_ORDER)}
    top = max((m.score for m in matches), default=0.0)
    answer_cut = top * 0.6
    rows = []
    for index, match in enumerate(matches):
        skill = registry.skill(match.skill_id)
        rows.append({
            "id": f"s{index + 1}",
            "skill": skill.id,
            "phase": skill.phase,
            "verb": (skill.manifest.get("verbs") or [skill.phase])[0],
            "tools": [t.id for t in skill.tools],
            "contracts": skill.contracts,
            "criteria": skill.manifest.get("acceptance") or [],
            "why": match.reasons,
            "score": round(match.score, 2),
            "band": "answer" if match.score >= answer_cut else "support",
        })
    # stable sort: answer band first, then lifecycle, then score desc
    rows.sort(key=lambda r: (0 if r["band"] == "answer" else 1,
                             order.get(r["phase"], 9), -r["score"]))
    for i, row in enumerate(rows):
        row["id"] = f"s{i + 1}"
    return rows


def explain(registry: Registry, skill_id: str, need: str) -> dict[str, Any]:
    """Why one skill did or did not match a need — used by `workflow route --explain`."""
    skill = registry.skill(skill_id)
    match = score_skill(skill, need)
    return {
        "skill": skill_id,
        "need": need,
        "score": round(match.score, 2),
        "reasons": match.reasons,
        "triggers": skill.triggers,
        "keywords": skill.manifest.get("keywords") or [],
        "verbs": skill.manifest.get("verbs") or [],
        "phase": skill.phase,
    }
