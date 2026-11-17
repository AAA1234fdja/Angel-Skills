/* Angel Workflow · extensión opcional de Ely IDE.
 *
 * Corre en un iframe con sandbox (sin acceso al DOM ni a red propia): solo usa
 * la API `ely`. Lee el paquete desde el workspace y lo inyecta en el chat del
 * perfil activo, así el modelo recibe únicamente las skills de la fase pedida.
 */
/* The bundle can live in three places depending on how it was installed: the
 * workspace's `workflow/` folder (CLI checkout), next to the extension
 * (`workflow install --ely`), or at the workspace root. The first one that
 * answers with a categories.json wins; the probe is done once. */
const BUNDLE_CANDIDATES = ["workflow", "angel.workflow",
  "IDE/ely-extensions/angel.workflow", ""];
let bundlePath = null;

async function resolveBundle(ely) {
  if (bundlePath !== null) return bundlePath;
  for (const candidate of BUNDLE_CANDIDATES) {
    const path = candidate ? `${candidate}/categories.json` : "categories.json";
    const raw = await readText(ely, path);
    if (raw) {
      bundlePath = candidate;
      return bundlePath;
    }
  }
  bundlePath = "workflow";
  return bundlePath;
}

function bundleOf() {
  return bundlePath === null ? "workflow" : bundlePath;
}

function join(relative) {
  const base = bundleOf();
  return base ? `${base}/${relative}` : relative;
}

const t = (ely, es, en) => ely.l10n(es, en);

/* ------------------------------------------------------------------ lectura */
async function readText(ely, path) {
  try {
    const res = await ely.workspace.readFile(path);
    if (typeof res === "string") return res;
    if (res && typeof res.text === "string") return res.text;
    if (res && typeof res.content === "string") return res.content;
    return "";
  } catch (e) {
    return "";
  }
}

function parseFrontmatter(text) {
  if (!text.startsWith("---")) return { data: {}, body: text };
  const end = text.indexOf("\n---", 3);
  if (end === -1) return { data: {}, body: text };
  const raw = text.slice(3, end);
  const body = text.slice(end + 4).replace(/^\r?\n/, "");
  const data = {};
  for (const line of raw.split(/\r?\n/)) {
    const m = /^\s*([A-Za-z0-9_.-]+):\s*(.*)$/.exec(line);
    if (!m) continue;
    const key = m[1];
    let value = m[2].trim().replace(/^["']|["']$/g, "");
    if (!value) continue;
    if (line.startsWith("  ") || line.startsWith("\t")) data.meta = { ...(data.meta || {}), [key]: value };
    else data[key] = value;
  }
  return { data, body };
}

async function loadRegistry(ely) {
  await resolveBundle(ely);
  const raw = await readText(ely, join("categories.json"));
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    await ely.window.showMessage(
      t(ely, "categories.json no es JSON válido", "categories.json is not valid JSON"),
      "error"
    );
    return null;
  }
}

async function loadManifest(ely, category, id) {
  const raw = await readText(ely, join(`skills/${category}/${id}/skill.json`));
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

async function loadSkills(ely, registry, filter = {}) {
  const rows = [];
  for (const cat of registry.categories || []) {
    if (filter.category && cat.id !== filter.category) continue;
    for (const entry of cat.skills || []) {
      const file = join(`skills/${cat.id}/${entry.id}/SKILL.md`);
      const text = await readText(ely, file);
      const { data, body } = parseFrontmatter(text || "");
      const meta = data.meta || {};
      const manifest = await loadManifest(ely, cat.id, entry.id);
      const phase = (manifest && manifest.phase) || meta.phase || entry.phase || "";
      if (filter.phase && phase !== filter.phase) continue;
      rows.push({
        id: entry.id,
        category: cat.id,
        categoryName: cat.name || cat.id,
        phase,
        status: meta.status || entry.status || "",
        description: data.description || entry.description || "",
        present: !!text,
        tools: (manifest && manifest.tools) || [],
        contracts: (manifest && manifest.contracts) || [],
        triggers: (manifest && manifest.triggers) || [],
        body
      });
    }
  }
  return rows;
}


/* ------------------------------------------------------------------ agentes */
/* An agent is a card under agents/<id>/agent.json. This extension only *reads*
 * them: the authorisation checks live in the Python runtime, which is the one
 * that can refuse a call. */
async function loadAgents(ely) {
  const reg = await loadRegistry(ely);
  if (!reg) return [];
  const rows = [];
  for (const entry of reg.agents || []) {
    const raw = await readText(ely, join(`agents/${entry.id}/agent.json`));
    if (!raw) {
      rows.push({ id: entry.id, present: false });
      continue;
    }
    try {
      const card = JSON.parse(raw);
      rows.push({ ...card, present: true });
    } catch (e) {
      rows.push({ id: entry.id, present: false, broken: true });
    }
  }
  return rows;
}

function agentTree(agents, id, seen) {
  const card = agents.find((a) => a.id === id);
  if (!card || seen.includes(id)) return { id, missing: !card, cycle: seen.includes(id), children: [] };
  const edges = card.delegates || [];
  return {
    id,
    role: card.role || "",
    state: card.state || "",
    children: edges.map((e) => agentTree(agents, e.to, [...seen, id]))
  };
}

function drawAgent(node, prefix = "", last = true) {
  const head = prefix === "" ? "" : last ? "└─ " : "├─ ";
  const mark = node.missing ? " (falta)" : node.cycle ? " (ciclo)" : "";
  const role = node.role ? ` · ${node.role}` : "";
  const out = [`${prefix}${head}${node.id}${role}${mark}`];
  const next = prefix + (prefix === "" ? "" : last ? "   " : "│  ");
  const kids = node.children || [];
  kids.forEach((kid, i) => out.push(...drawAgent(kid, next, i === kids.length - 1)));
  return out;
}

/* ------------------------------------------------------------------ formato */
function asMarkdown(rows, title) {
  const out = [`# ${title}`, ""];
  let last = null;
  for (const r of rows) {
    if (r.category !== last) {
      last = r.category;
      out.push(`## ${r.categoryName}`, "");
    }
    out.push(`### ${r.id} · fase ${r.phase || "?"}`);
    out.push(`Disparador: ${r.description}`);
    out.push("");
    if (r.body) out.push(r.body.trim(), "");
  }
  return out.join("\n");
}

function asList(rows) {
  return rows.map((r) => ({ label: r.id, description: `${r.categoryName} · ${r.phase || "?"} · ${r.description}` }));
}

/* ------------------------------------------------------------------ comandos */
async function openText(ely, title, text) {
  const body = String(text || "");
  if (typeof ely.window.showDocument === "function") {
    /* Ely expone showDocument({title, text}) — no posicional. */
    try {
      await ely.window.showDocument({ title, text: body });
      return;
    } catch (e) {
      /* cae al mensaje si la firma cambia en otra versión del IDE */
    }
  }
  await ely.window.showMessage(body.slice(0, 200), "info");
}

async function cmdList(ely) {
  const reg = await loadRegistry(ely);
  if (!reg) {
    await ely.window.showMessage(
      t(ely, `No encuentro ${join("categories.json")} en el workspace`, `Cannot find ${join("categories.json")} in the workspace`),
      "warn"
    );
    return;
  }
  const rows = await loadSkills(ely, reg);
  const missing = rows.filter((r) => !r.present);
  const lines = [
    `# ${t(ely, "Skills del paquete", "Pack skills")} ${bundleOf() || "."}`,
    "",
    `${rows.length} ${t(ely, "declaradas", "declared")} · ${missing.length} ${t(ely, "sin archivo", "missing file")}`,
    ""
  ];
  for (const cat of reg.categories || []) {
    const own = rows.filter((r) => r.category === cat.id);
    lines.push(`## ${cat.name || cat.id} (${cat.id}) · ${cat.status} · ${own.length}`);
    if (cat.gate) lines.push(`gate: ${cat.gate}`);
    for (const r of own) lines.push(`- ${r.present ? "●" : "○"} ${r.id} — ${r.phase} — ${r.description}`);
    if (!own.length) lines.push(t(ely, "- (sin skills todavía)", "- (no skills yet)"));
    lines.push("");
  }
  await openText(ely, t(ely, "Workflow · skills", "Workflow · skills"), lines.join("\n"));
}

async function cmdPhase(ely) {
  const reg = await loadRegistry(ely);
  if (!reg) return;
  const rows = await loadSkills(ely, reg);
  if (!rows.length) {
    await ely.window.showMessage(t(ely, "El paquete no tiene skills", "The pack has no skills"), "warn");
    return;
  }
  const phases = [...new Set(rows.map((r) => r.phase).filter(Boolean))];
  const picked = await ely.window.showQuickPick({
    items: phases.map((p) => ({
      label: p,
      description: `${rows.filter((r) => r.phase === p).length} ${t(ely, "skills", "skills")}`
    })),
    options: { title: t(ely, "¿Qué fase vas a trabajar?", "Which phase are you working on?") }
  });
  const phase = typeof picked === "string" ? picked : picked && picked.label;
  if (!phase) return;
  const sel = rows.filter((r) => r.phase === phase);
  const text = asMarkdown(sel, `${t(ely, "Contexto de fase", "Phase context")}: ${phase}`);
  await ely.chat.send(text);
  await ely.window.showMessage(
    t(ely, `${sel.length} skill(s) de "${phase}" enviadas al chat`, `${sel.length} "${phase}" skill(s) sent to chat`),
    "info"
  );
}

async function cmdSkill(ely) {
  const reg = await loadRegistry(ely);
  if (!reg) return;
  const rows = await loadSkills(ely, reg);
  const picked = await ely.window.showQuickPick({
    items: asList(rows),
    options: { title: t(ely, "Abrir una skill", "Open a skill") }
  });
  if (!picked) return;
  const id = typeof picked === "string" ? picked : picked.label;
  const row = rows.find((r) => r.id === id);
  if (!row) return;
  await openText(ely, `${row.id} · ${row.categoryName}`, row.body || row.description);
}

async function cmdTools(ely) {
  const reg = await loadRegistry(ely);
  if (!reg) return;
  const rows = await loadSkills(ely, reg);
  if (!rows.length) return;
  const picked = await ely.window.showQuickPick({
    items: asList(rows.filter((r) => r.tools.length)),
    options: { title: t(ely, "Herramientas de una skill", "Tools of a skill") }
  });
  if (!picked) return;
  const id = typeof picked === "string" ? picked : picked.label;
  const row = rows.find((r) => r.id === id);
  if (!row) return;
  const lines = [
    `# ${row.id} · ${row.categoryName}`,
    "",
    `${t(ely, "Fase", "Phase")}: ${row.phase || "?"} · status: ${row.status || "?"}`,
    `${t(ely, "Disparadores", "Triggers")}: ${(row.triggers || []).join(", ") || "—"}`,
    `${t(ely, "Contratos", "Contracts")}: ${(row.contracts || []).join(", ") || "—"}`,
    "",
    "| tool | risk | timeout | what it does |",
    "|---|---|---|---|"
  ];
  for (const tool of row.tools) {
    lines.push(`| ${tool.id} | ${tool.risk} | ${tool.timeout}s | ${tool.description || ""} |`);
  }
  lines.push("", t(ely, "Para ejecutarlas", "To run them") + ": `workflow tool --self-test`");
  await openText(ely, `tools · ${row.id}`, lines.join("\n"));
}


async function cmdAgents(ely) {
  const agents = await loadAgents(ely);
  if (!agents.length) {
    await ely.window.showMessage(
      t(ely, "El paquete no declara agentes en categories.json", "The pack declares no agents in categories.json"),
      "warn"
    );
    return;
  }
  const lines = [`# ${t(ely, "Agentes del paquete", "Pack agents")}`, ""];
  const missing = agents.filter((a) => !a.present).length;
  lines.push(`${agents.length} ${t(ely, "agente(s)", "agent(s)")} · ${missing} ${t(ely, "sin carta", "missing card")}`, "");
  for (const a of agents) {
    if (!a.present) {
      lines.push(`- ○ ${a.id} — ${t(ely, "sin agent.json", "no agent.json")}`);
      continue;
    }
    lines.push(`## ${a.id} · v${a.version} · ${a.role} · ${a.state}`);
    lines.push(`agent://${a.address_space}/${a.id}@${a.version}`);
    lines.push("");
    lines.push(a.description || "");
    lines.push("");
    lines.push(`${t(ely, "Skills", "Skills")}: ${(a.skills || []).join(", ") || "—"}`);
    const limits = a.limits || {};
    lines.push(`${t(ely, "Límites", "Limits")}: depth ${limits.max_depth} · calls ${limits.max_calls} · budget ${limits.budget_share}`);
    for (const edge of a.delegates || []) {
      lines.push(`- → ${edge.to} ${t(ely, "cuando", "when")} "${edge.when}" (${(edge.allow || []).join(", ")})`);
    }
    lines.push("");
  }
  await openText(ely, t(ely, "Workflow · agentes", "Workflow · agents"), lines.join("\n"));
}

async function cmdAgentTree(ely) {
  const agents = await loadAgents(ely);
  const present = agents.filter((a) => a.present);
  if (!present.length) {
    await ely.window.showMessage(t(ely, "No hay agentes que dibujar", "No agents to draw"), "warn");
    return;
  }
  const hasParent = new Set(present.flatMap((a) => (a.delegates || []).map((e) => e.to)));
  const roots = present.filter((a) => !hasParent.has(a.id));
  const lines = [`# ${t(ely, "Árbol de delegación", "Delegation tree")}`, ""];
  for (const root of roots.length ? roots : present) {
    lines.push(...drawAgent(agentTree(present, root.id, [])));
    lines.push("");
  }
  lines.push(t(ely, "Para planificar o llamar de verdad", "To plan or actually call") + ": `workflow agents plan --agent <id> --need \"...\"`");
  await openText(ely, t(ely, "Workflow · árbol de agentes", "Workflow · agent tree"), lines.join("\n"));
}

async function cmdAgentAddress(ely) {
  const agents = (await loadAgents(ely)).filter((a) => a.present);
  if (!agents.length) {
    await ely.window.showMessage(t(ely, "No hay agentes con carta", "No agents with a card"), "warn");
    return;
  }
  const picked = await ely.window.showQuickPick({
    items: agents.map((a) => ({
      label: a.id,
      description: `${a.role} · v${a.version} · ${(a.delegates || []).length} ${t(ely, "delegado(s)", "delegate(s)")}`
    })),
    options: { title: t(ely, "Dirección de un agente", "Address of an agent") }
  });
  const id = typeof picked === "string" ? picked : picked && picked.label;
  const card = agents.find((a) => a.id === id);
  if (!card) return;
  const lines = [
    `agent://${card.address_space}/${card.id}@${card.version}`,
    "",
    `${t(ely, "Rol", "Role")}: ${card.role} · ${t(ely, "estado", "state")}: ${card.state}`,
    `${t(ely, "Entradas", "Inputs")}: ${Object.keys((card.inputs || {}).fields || {}).join(", ") || "—"}`,
    `${t(ely, "Salidas", "Outputs")}: ${Object.keys((card.outputs || {}).fields || {}).join(", ") || "—"}`,
    `${t(ely, "Guardarraíles", "Guardrails")}: ${(card.guardrails || []).join("; ") || "—"}`,
    "",
    t(ely, "El pin (#hash) lo calcula el runtime al cargar la carta;", "The pin (#hash) is computed by the runtime when it loads the card;"),
    t(ely, "pídelo con", "ask for it with") + ": `workflow agents address agent://<space>/" + card.id + "`"
  ];
  await openText(ely, `agent · ${card.id}`, lines.join("\n"));
}

async function cmdValidate(ely) {
  const reg = await loadRegistry(ely);
  if (!reg) return;
  const errors = [];
  const warnings = [];
  const rows = await loadSkills(ely, reg);
  const seen = new Set();
  for (const r of rows) {
    if (seen.has(r.id)) errors.push(`${t(ely, "id duplicado", "duplicate id")}: ${r.id}`);
    seen.add(r.id);
    if (!r.present) {
      errors.push(`${r.category}/${r.id}: ${t(ely, "falta SKILL.md", "missing SKILL.md")}`);
      continue;
    }
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(r.id)) errors.push(`${r.id}: ${t(ely, "id con formato inválido", "invalid id format")}`);
    if (!/Usar cuando|Use when/.test(r.description)) {
      errors.push(`${r.id}: ${t(ely, "la descripción no tiene disparador", "description has no trigger")}`);
    }
    if (r.description.length > 700) errors.push(`${r.id}: description > 700`);
    if (!r.phase) errors.push(`${r.id}: ${t(ely, "sin fase", "no phase")}`);
    for (const h of ["When to Use", "Procedure", "Exit Criteria"]) {
      if (!r.body.includes(h)) errors.push(`${r.id}: ${t(ely, "falta la sección", "missing section")} "${h}"`);
    }
    if (!r.body.includes("When Not to Use")) warnings.push(`${r.id}: ${t(ely, "sin", "no")} "When Not to Use"`);
    if (!r.body.includes("Common Failures")) warnings.push(`${r.id}: ${t(ely, "sin", "no")} "Common Failures"`);
  }
  const lines = [`# ${t(ely, "Validación", "Validation")} · ${rows.length} skill(s)`, ""];
  lines.push(`${errors.length} ${t(ely, "error(es)", "error(s)")} · ${warnings.length} ${t(ely, "aviso(s)", "warning(s)")}`, "");
  for (const w of warnings) lines.push(`- ⚠ ${w}`);
  for (const e of errors) lines.push(`- ✖ ${e}`);
  if (!errors.length) lines.push(t(ely, "- ✔ paquete válido", "- ✔ pack is valid"));
  await openText(ely, t(ely, "Workflow · validación", "Workflow · validation"), lines.join("\n"));
  await ely.window.setStatusBar(
    "workflow",
    errors.length ? `✖ ${errors.length}` : "✔ workflow",
    `${rows.length} skills · ${warnings.length} ${t(ely, "avisos", "warnings")}`
  );
}

async function cmdStandard(ely) {
  const text = await readText(ely, join("EXTENSION-STANDARD.md"));
  if (!text) {
    await ely.window.showMessage(t(ely, "No encuentro EXTENSION-STANDARD.md", "Cannot find EXTENSION-STANDARD.md"), "warn");
    return;
  }
  await openText(ely, "EXTENSION-STANDARD.md", text);
}

/* ------------------------------------------------------------------ registro */
async function registerCommands(ely) {
  await ely.commands.register("angel.workflow.tools", t(ely, "Workflow: ver herramientas de una skill", "Workflow: tools of a skill"), () => cmdTools(ely));
  await ely.commands.register("angel.workflow.list", t(ely, "Workflow: listar skills", "Workflow: list skills"), () => cmdList(ely));
  await ely.commands.register("angel.workflow.phase", t(ely, "Workflow: cargar fase en el chat", "Workflow: load phase into chat"), () => cmdPhase(ely));
  await ely.commands.register("angel.workflow.skill", t(ely, "Workflow: abrir una skill", "Workflow: open a skill"), () => cmdSkill(ely));
  await ely.commands.register("angel.workflow.validate", t(ely, "Workflow: validar el paquete", "Workflow: validate the pack"), () => cmdValidate(ely));
  await ely.commands.register("angel.workflow.standard", t(ely, "Workflow: leer el estándar", "Workflow: read the standard"), () => cmdStandard(ely));
  await ely.commands.register("angel.workflow.agents", t(ely, "Workflow: agentes del paquete", "Workflow: pack agents"), () => cmdAgents(ely));
  await ely.commands.register("angel.workflow.agenttree", t(ely, "Workflow: árbol de agentes", "Workflow: agent tree"), () => cmdAgentTree(ely));
  await ely.commands.register("angel.workflow.agentaddress", t(ely, "Workflow: dirección de un agente", "Workflow: agent address"), () => cmdAgentAddress(ely));
}


async function activate(ely) {
  await registerCommands(ely);
  await ely.window.setStatusBar("workflow", "workflow", t(ely, "Paquete de skills Angel", "Angel skill pack"));
  ely.on("language", () => registerCommands(ely));
  ely.log(t(ely, "Angel Workflow activo", "Angel Workflow active"));
}

if (typeof module !== "undefined" && module.exports) module.exports = { activate };
