/* Motor del paquete workflow · sin dependencias.
 * Responsabilidades: leer el registro, leer el frontmatter de las skills,
 * validar el paquete y producir el texto que un arnés consume.
 */
import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, dirname } from "node:path";

export const PHASES = ["plan", "implement", "test", "review", "verify", "meta"];
export const STATUSES = ["adoptada", "propia", "experimental"];
export const ID_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
export const SKILL_FILE = "SKILL.md";
export const REGISTRY = "categories.json";
export const STANDARD = "EXTENSION-STANDARD.md";

/** Parser del subconjunto de YAML que usa el frontmatter: escalares y un mapa
 *  anidado de un nivel (metadata:). No pretende ser YAML completo. */
export function parseFrontmatter(text) {
  if (!text.startsWith("---")) return { data: null, body: text, error: "sin bloque ---" };
  const end = text.indexOf("\n---", 3);
  if (end === -1) return { data: null, body: text, error: "bloque --- sin cerrar" };
  const raw = text.slice(3, end);
  const body = text.slice(end + 4).replace(/^\r?\n/, "");
  const data = {};
  let parent = null;
  for (const line of raw.split(/\r?\n/)) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    const nested = /^\s+([A-Za-z0-9_.-]+):\s*(.*)$/.exec(line);
    if (nested && parent) {
      const [, k, v] = nested;
      if (data[parent] === null || typeof data[parent] !== "object") data[parent] = {};
      data[parent][k] = unquote(v);
      continue;
    }
    const top = /^([A-Za-z0-9_.-]+):\s*(.*)$/.exec(line);
    if (!top) continue;
    const [, k, v] = top;
    if (v === "") {
      data[k] = null;
      parent = k;
    } else {
      data[k] = unquote(v);
      parent = null;
    }
  }
  return { data, body, error: null };
}

function unquote(v) {
  const t = String(v).trim();
  if ((t.startsWith('"') && t.endsWith('"')) || (t.startsWith("'") && t.endsWith("'"))) {
    return t.slice(1, -1).replace(/\\"/g, '"');
  }
  return t;
}

export function loadRegistry(root) {
  const file = join(root, REGISTRY);
  if (!existsSync(file)) throw new Error(`No existe ${REGISTRY} en ${root}`);
  const data = JSON.parse(readFileSync(file, "utf8"));
  const byId = new Map((data.categories || []).map((c) => [c.id, c]));
  return { data, categories: data.categories || [], byId };
}

export function skillDir(root, categoryId, skillId) {
  return join(root, "skills", categoryId, skillId);
}

export function readSkill(root, categoryId, skillId) {
  const dir = skillDir(root, categoryId, skillId);
  const file = join(dir, SKILL_FILE);
  if (!existsSync(file)) return null;
  const text = readFileSync(file, "utf8");
  const { data, body, error } = parseFrontmatter(text);
  return {
    id: skillId,
    category: categoryId,
    dir,
    file,
    text,
    body,
    frontmatter: data,
    frontmatterError: error,
    lines: text.split("\n").length,
  };
}

/** Todas las skills declaradas en el registro que existen en disco. */
export function listSkills(root) {
  const reg = loadRegistry(root);
  const rows = [];
  for (const cat of reg.categories) {
    for (const s of cat.skills || []) {
      const skill = readSkill(root, cat.id, s.id);
      rows.push({
        id: s.id,
        category: cat.id,
        categoryName: cat.name,
        phase: (skill?.frontmatter?.metadata?.phase) || s.phase || null,
        status: (skill?.frontmatter?.metadata?.status) || s.status || null,
        origin: (skill?.frontmatter?.metadata?.origin) || s.origin || null,
        description: (skill?.frontmatter?.description) || s.description || "",
        present: !!skill,
        lines: skill?.lines || 0,
        dir: skill ? relative(root, skill.dir) : null,
      });
    }
  }
  return rows;
}

/** Skills que existen en disco pero no están en el registro, y viceversa. */
export function orphans(root) {
  const reg = loadRegistry(root);
  const declared = new Set(reg.categories.flatMap((c) => (c.skills || []).map((s) => `${c.id}/${s.id}`)));
  const onDisk = [];
  const base = join(root, "skills");
  if (existsSync(base)) {
    for (const cat of readdirSync(base)) {
      const catPath = join(base, cat);
      if (!statSync(catPath).isDirectory()) continue;
      for (const s of readdirSync(catPath)) {
        const p = join(catPath, s);
        if (!statSync(p).isDirectory()) continue;
        if (existsSync(join(p, SKILL_FILE))) onDisk.push(`${cat}/${s}`);
      }
    }
  }
  return {
    notRegistered: onDisk.filter((k) => !declared.has(k)),
    notOnDisk: [...declared].filter((k) => !onDisk.includes(k)),
  };
}

/** Validación según EXTENSION-STANDARD.md §7. */
export function validate(root) {
  const errors = [];
  const warnings = [];
  let reg;
  try {
    reg = loadRegistry(root);
  } catch (e) {
    return { errors: [`registro ilegible: ${e.message}`], warnings, skills: [] };
  }
  const cfg = reg.data.rules || {};
  const seenIds = new Set();
  const descriptions = [];

  if (!existsSync(join(root, STANDARD))) errors.push(`falta ${STANDARD}`);

  for (const cat of reg.categories) {
    if (!ID_RE.test(cat.id)) errors.push(`categoría con id inválido: ${cat.id}`);
    if (!cat.name) errors.push(`categoría ${cat.id} sin name`);
    if (!cat.description) warnings.push(`categoría ${cat.id} sin description`);
    if (!["activa", "pendiente", "congelada"].includes(cat.status)) {
      errors.push(`categoría ${cat.id}: status inválido (${cat.status})`);
    }
    if (!Array.isArray(cat.rules)) errors.push(`categoría ${cat.id}: rules debe ser lista`);
    if (!Array.isArray(cat.skills)) errors.push(`categoría ${cat.id}: skills debe ser lista`);

    for (const entry of cat.skills || []) {
      const id = entry.id;
      if (!ID_RE.test(id || "")) errors.push(`skill con id inválido en ${cat.id}: ${id}`);
      if (seenIds.has(id)) errors.push(`id duplicado: ${id}`);
      seenIds.add(id);

      const skill = readSkill(root, cat.id, id);
      if (!skill) {
        errors.push(`${cat.id}/${id}: falta ${SKILL_FILE}`);
        continue;
      }
      if (skill.frontmatterError) {
        errors.push(`${cat.id}/${id}: frontmatter ${skill.frontmatterError}`);
        continue;
      }
      const fm = skill.frontmatter || {};
      for (const key of ["name", "description", "metadata"]) {
        if (!(key in fm)) errors.push(`${cat.id}/${id}: frontmatter sin "${key}"`);
      }
      if (fm.name && fm.name !== id) errors.push(`${cat.id}/${id}: name "${fm.name}" != id "${id}"`);
      const meta = fm.metadata || {};
      for (const key of ["origin", "category", "phase", "status"]) {
        if (!meta[key]) errors.push(`${cat.id}/${id}: metadata sin "${key}"`);
      }
      if (meta.category && meta.category !== cat.id) {
        errors.push(`${cat.id}/${id}: metadata.category "${meta.category}" no coincide con la carpeta`);
      }
      if (meta.phase && !PHASES.includes(meta.phase)) {
        errors.push(`${cat.id}/${id}: phase inválida "${meta.phase}" (${PHASES.join("|")})`);
      }
      if (meta.status && !STATUSES.includes(meta.status)) {
        errors.push(`${cat.id}/${id}: status inválido "${meta.status}" (${STATUSES.join("|")})`);
      }
      const desc = String(fm.description || "");
      const triggers = cfg.descriptionMustContain || ["Use when", "Usar cuando"];
      if (desc && !triggers.some((t) => desc.includes(t))) {
        errors.push(`${cat.id}/${id}: description sin disparador (${triggers.join(" | ")})`);
      }
      if (cfg.descriptionMaxChars && desc.length > cfg.descriptionMaxChars) {
        errors.push(`${cat.id}/${id}: description ${desc.length} > ${cfg.descriptionMaxChars} caracteres`);
      }
      if (desc) descriptions.push({ id, desc });

      for (const heading of ["Cuándo usar", "Procedimiento", "Criterio de salida"]) {
        if (!skill.body.includes(heading)) errors.push(`${cat.id}/${id}: falta la sección "${heading}"`);
      }
      for (const heading of ["Cuándo NO usar", "Errores típicos"]) {
        if (!skill.body.includes(heading)) warnings.push(`${cat.id}/${id}: sin "${heading}"`);
      }
      if (cfg.maxSkillLines && skill.lines > cfg.maxSkillLines) {
        errors.push(`${cat.id}/${id}: ${skill.lines} líneas > ${cfg.maxSkillLines}`);
      } else if (skill.lines > 250) {
        warnings.push(`${cat.id}/${id}: ${skill.lines} líneas, ¿debería partirse?`);
      }
    }
  }

  const o = orphans(root);
  for (const k of o.notRegistered) errors.push(`skill en disco sin registrar: ${k}`);
  for (const k of o.notOnDisk) errors.push(`skill registrada sin archivo: ${k}`);

  // Solapamiento de descripciones dentro de la misma categoría (§4.1).
  const byPair = new Map();
  for (const d of descriptions) {
    const key = d.id;
    byPair.set(key, d.desc.toLowerCase().slice(0, 60));
  }
  for (const [id, head] of byPair) {
    for (const [other, head2] of byPair) {
      if (id < other && head === head2) warnings.push(`${id} y ${other} tienen descripciones casi idénticas`);
    }
  }

  return { errors, warnings, skills: listSkills(root) };
}

/** Texto de contexto para un arnés: solo las skills de una fase (§6). */
export function claim(root, { phase = null, category = null, full = false } = {}) {
  const reg = loadRegistry(root);
  const rows = listSkills(root).filter(
    (r) => (!phase || r.phase === phase) && (!category || r.category === category)
  );
  const std = join(root, STANDARD);
  const out = [];
  out.push("# workflow · contexto de skills");
  out.push("");
  out.push(`Paquete: ${reg.data.version} · estándar: ${STANDARD} · regla: cargar solo una fase.`);
  if (existsSync(std)) {
    out.push("");
    out.push("## Reglas duras del estándar");
    out.push("");
    for (const line of hardRules(join(root, STANDARD))) out.push(`- ${line}`);
  }
  out.push("");
  out.push(`## Skills (${rows.length})`);
  for (const r of rows) {
    out.push("");
    out.push(`### ${r.id}  ·  ${r.categoryName}  ·  fase ${r.phase || "?"}`);
    out.push(`disparador: ${r.description}`);
    if (full) {
      const skill = readSkill(root, r.category, r.id);
      if (skill) out.push("", skill.body.trim());
    }
  }
  return out.join("\n");
}

function hardRules(file) {
  const text = readFileSync(file, "utf8");
  const start = text.indexOf("**Reglas de estructura");
  if (start === -1) return [];
  const lines = text.slice(start).split("\n");
  const rows = [];
  let begun = false;
  for (const line of lines) {
    const isRow = line.startsWith("|");
    if (isRow) {
      begun = true;
      if (line.includes("---") || line.startsWith("| Regla")) continue;
      const cells = line.split("|").map((c) => c.trim()).filter(Boolean);
      if (cells.length) rows.push(cells.join(" — "));
    } else if (begun) {
      break;
    }
  }
  return rows;
}
