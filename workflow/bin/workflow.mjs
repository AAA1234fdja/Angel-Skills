#!/usr/bin/env node
/* workflow · CLI del paquete de skills.
 * Uso: workflow <list|show|claim|validate|plan|pack|install|where>
 * Node >= 18, sin dependencias.
 */
import { existsSync, mkdirSync, cpSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadRegistry,
  listSkills,
  readSkill,
  validate,
  claim,
  PHASES,
} from "../src/registry.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");

const useColor = process.stdout.isTTY && !process.env.NO_COLOR;
const c = (code) => (s) => (useColor ? `\u001b[${code}m${s}\u001b[0m` : String(s));
const dim = c("2"), bold = c("1"), green = c("32"), red = c("31"), yellow = c("33"), cyan = c("36");

function packageRoot() {
  // Permite usar el CLI desde otra raíz: WORKFLOW_ROOT=/ruta workflow ...
  const env = process.env.WORKFLOW_ROOT;
  if (env) return resolve(env);
  return ROOT;
}

function help() {
  const root = packageRoot();
  const reg = safeRegistry(root);
  const cats = reg ? reg.categories.map((x) => `${x.id}(${(x.skills || []).length})`).join(" ") : "—";
  process.stdout.write(`${bold("workflow")} · paquete de skills de Angel ${dim(`(${root})`)}

${bold("USO")}
  workflow list [--phase <fase>] [--category <id>] [--json]
  workflow show <id>                       muestra la SKILL.md completa
  workflow claim --phase <fase>            contexto mínimo para el arnés
  workflow claim --skill <id> --full       una skill entera, ya renderizada
  workflow validate [--strict]             aplica EXTENSION-STANDARD.md §7
  workflow plan [<categoria>]              huecos: pendientes vs instaladas
  workflow pack [--out <zip>]              genera el zip distribuible
  workflow install --ely <ruta>            copia la extensión al IDE de Ely
  workflow where                           rutas del paquete

${bold("CATEGORÍAS")} ${cats}
${bold("FASES")} ${PHASES.join(" · ")}
`);
}

function safeRegistry(root) {
  try {
    return loadRegistry(root);
  } catch {
    return null;
  }
}

function dataPath(root, rel) {
  return join(root, rel);
}

function cmdList(root, argv) {
  const phase = flag(argv, "--phase");
  const category = flag(argv, "--category");
  const json = argv.includes("--json");
  const reg = loadRegistry(root);
  if (category && !reg.byId.has(category)) {
    process.stderr.write(`${red("✖")} categoría desconocida: ${category}\n`);
    return 1;
  }
  const rows = listSkills(root).filter(
    (r) => (!phase || r.phase === phase) && (!category || r.category === category)
  );
  if (json) {
    process.stdout.write(JSON.stringify(rows, null, 2) + "\n");
    return 0;
  }
  if (!rows.length) {
    process.stdout.write(`${dim("(sin skills para ese filtro)")}\n`);
    return 0;
  }
  const w = Math.max(...rows.map((r) => r.id.length));
  let lastCat = null;
  for (const r of rows) {
    if (r.category !== lastCat) {
      lastCat = r.category;
      process.stdout.write(`\n${bold(r.categoryName)} ${dim("· " + r.category)}\n`);
    }
    const mark = r.present ? green("●") : red("○");
    process.stdout.write(`  ${mark} ${r.id.padEnd(w)}  ${dim((r.phase || "?").padEnd(9))} ${truncate(r.description, 90)}\n`);
  }
  process.stdout.write(`\n${dim(`${rows.length} skill(s)`)}\n`);
  return 0;
}

function cmdShow(root, argv) {
  const id = argv.find((a) => !a.startsWith("-"));
  if (!id) {
    process.stderr.write("falta el id de la skill\n");
    return 1;
  }
  const row = listSkills(root).find((r) => r.id === id);
  if (!row) {
    process.stderr.write(`${red("✖")} no existe la skill ${id}\n`);
    return 1;
  }
  const skill = readSkill(root, row.category, row.id);
  if (!skill) {
    process.stderr.write(`${red("✖")} ${row.category}/${row.id} está registrada pero falta ${"SKILL.md"}\n`);
    return 1;
  }
  process.stdout.write(skill.text + "\n");
  return 0;
}

function cmdClaim(root, argv) {
  const phase = flag(argv, "--phase");
  const skillId = flag(argv, "--skill");
  const full = argv.includes("--full");
  if (phase && !PHASES.includes(phase)) {
    process.stderr.write(`${red("✖")} fase inválida: ${phase}\n`);
    return 1;
  }
  if (skillId) {
    const row = listSkills(root).find((r) => r.id === skillId);
    if (!row) {
      process.stderr.write(`${red("✖")} no existe la skill ${skillId}\n`);
      return 1;
    }
    process.stdout.write(claim(root, { category: row.category, phase: row.phase, full }) + "\n");
    return 0;
  }
  process.stdout.write(claim(root, { phase, full }) + "\n");
  return 0;
}

function cmdValidate(root, argv) {
  const strict = argv.includes("--strict");
  const { errors, warnings, skills } = validate(root);
  for (const w of warnings) process.stdout.write(`${yellow("⚠")} ${w}\n`);
  for (const e of errors) process.stdout.write(`${red("✖")} ${e}\n`);
  const ok = errors.length === 0 && !(strict && warnings.length);
  process.stdout.write(
    `\n${ok ? green("✔ válido") : red("✖ inválido")} · ${skills.length} skill(s) · ` +
      `${errors.length} error(es) · ${warnings.length} aviso(s)\n`
  );
  return ok ? 0 : strict && !errors.length ? 2 : 1;
}

function cmdPlan(root, argv) {
  const only = argv.find((a) => !a.startsWith("-"));
  const reg = loadRegistry(root);
  const rows = listSkills(root);
  for (const cat of reg.categories) {
    if (only && cat.id !== only) continue;
    const have = rows.filter((r) => r.category === cat.id).map((r) => r.id);
    const pend = (cat.pending || []).filter((p) => !have.includes(p));
    const tag = cat.status === "activa" ? green("activa") : cat.status === "pendiente" ? yellow("pendiente") : dim(cat.status);
    process.stdout.write(`\n${bold(cat.name)} ${dim("· " + cat.id)} · ${tag} · ${have.length} instalada(s)\n`);
    if (cat.gate) process.stdout.write(`  ${dim("gate:")} ${cat.gate}\n`);
    for (const id of have) process.stdout.write(`  ${green("✔")} ${id}\n`);
    for (const id of pend) process.stdout.write(`  ${dim("·")} ${dim(id)} ${dim("(pendiente)")}\n`);
    if (!have.length && !pend.length) process.stdout.write(`  ${dim("(sin definir)")}\n`);
  }
  process.stdout.write("\n");
  return 0;
}

function cmdPack(root, argv) {
  const out = resolve(flag(argv, "--out") || join(root, "dist", "workflow.zip"));
  const zip = process.env.WORKFLOW_ZIP_CMD || "zip";
  const rel = ["EXTENSION-STANDARD.md", "categories.json", "CHANGELOG.md", "README.md", "skills", "bin", "src", "ely-extension"];
  mkdirSync(dirname(out), { recursive: true });
  const args = ["-r", "-q", out, ...rel.filter((r) => existsSync(join(root, r)))];
  const res = spawnSync(zip, args, { cwd: root, stdio: "inherit" });
  if (res.error) {
    process.stderr.write(`${red("✖")} no se pudo ejecutar ${zip}: ${res.error.message}\n`);
    return 1;
  }
  process.stdout.write(`${green("✔")} ${out}\n`);
  return res.status === 0 ? 0 : 1;
}

function cmdInstall(root, argv) {
  const target = flag(argv, "--ely");
  if (!target) {
    process.stderr.write("falta --ely <ruta del repo Ely>\n");
    return 1;
  }
  const dest = join(resolve(target), "IDE", "ely-extensions", "angel.workflow");
  const src = join(root, "ely-extension");
  if (!existsSync(src)) {
    process.stderr.write(`${red("✖")} no existe workflow/ely-extension\n`);
    return 1;
  }
  // La extensión se sirve desde el sandbox: copiamos también el paquete para
  // que main.js pueda leerlo con workspace.readFile sin salir del iframe.
  mkdirSync(dest, { recursive: true });
  cpSync(src, dest, { recursive: true });
  cpSync(join(root, "categories.json"), join(dest, "categories.json"));
  cpSync(join(root, "EXTENSION-STANDARD.md"), join(dest, "EXTENSION-STANDARD.md"));
  cpSync(join(root, "skills"), join(dest, "skills"), { recursive: true });
  if (existsSync(join(root, "README.md"))) cpSync(join(root, "README.md"), join(dest, "README.md"));
  process.stdout.write(`${green("✔")} extensión instalada en ${dest}\n`);
  process.stdout.write(`${dim("Reinicia el IDE o recarga la vista Extensiones.")}\n`);
  return 0;
}

function cmdWhere(root) {
  const reg = safeRegistry(root);
  process.stdout.write(`root        ${root}\n`);
  process.stdout.write(`registro    ${join(root, "categories.json")}\n`);
  process.stdout.write(`estándar    ${join(root, "EXTENSION-STANDARD.md")}\n`);
  process.stdout.write(`skills      ${join(root, "skills")}\n`);
  process.stdout.write(`extensión   ${join(root, "ely-extension")}\n`);
  process.stdout.write(`categorías  ${reg ? reg.categories.length : "?"}\n`);
  return 0;
}

function flag(argv, name) {
  const i = argv.indexOf(name);
  return i >= 0 ? argv[i + 1] : null;
}

function truncate(s, n) {
  const t = String(s || "").replace(/\s+/g, " ");
  return t.length > n ? t.slice(0, n - 1) + "…" : t;
}

const [, , cmd = "help", ...rest] = process.argv;
const root = packageRoot();
let code = 0;
try {
  switch (cmd) {
    case "list": code = cmdList(root, rest); break;
    case "show": code = cmdShow(root, rest); break;
    case "claim": code = cmdClaim(root, rest); break;
    case "validate": code = cmdValidate(root, rest); break;
    case "plan": code = cmdPlan(root, rest); break;
    case "pack": code = cmdPack(root, rest); break;
    case "install": code = cmdInstall(root, rest); break;
    case "where": code = cmdWhere(root); break;
    case "help": case "--help": case "-h": help(); break;
    default:
      process.stderr.write(`comando desconocido: ${cmd}\n`);
      help();
      code = 1;
  }
} catch (e) {
  process.stderr.write(`${red("✖")} ${e.message}\n`);
  code = 1;
}
process.exit(code);
