// Standalone harness for the Ely extension test.
//
// The extension runs inside Ely as an iframe with a sandboxed API object, so the
// only honest way to test it is to hand it a mock of that API and call every
// command it registers. Everything else here is deliberately dumb: it records what
// the extension asked the IDE to show.
//
// Usage: node harness.mjs <workspace-root> <relative path to main.js>

import { readFile } from "node:fs/promises";

const [, , base, entry] = process.argv;
const shown = [];
const messages = [];
const registered = {};

const ely = {
  i18n: { locale: "en" },
  l10n: (_es, en) => en,
  on: () => {},
  log: (message) => messages.push({ log: String(message).slice(0, 60) }),
  workspace: {
    async readFile(path) {
      try {
        return await readFile(`${base}/${path}`, "utf8");
      } catch (error) {
        return null;
      }
    },
    async root() {
      return base;
    },
  },
  window: {
    async showDocument({ title, text }) {
      shown.push({ title, text });
    },
    async showMessage(message, kind) {
      messages.push({ message: String(message).slice(0, 80), kind });
    },
    async showQuickPick({ items }) {
      return items && items.length ? items[0] : null;
    },
    async showInputBox() {
      return "review";
    },
    async setStatusBar(...args) {
      messages.push({ status: args });
    },
  },
  commands: {
    async register(id, title, fn) {
      registered[id] = fn;
    },
  },
  chat: {
    async send(text) {
      messages.push({ chat: String(text).slice(0, 120) });
    },
  },
};

const module = await import(`${base}/${entry}`);
await module.activate(ely);

const failures = [];
for (const [id, fn] of Object.entries(registered)) {
  try {
    await fn();
  } catch (error) {
    failures.push(`${id}: ${error && error.message}`);
  }
}

console.log(JSON.stringify({
  commands: Object.keys(registered).sort(),
  failures,
  documents: shown.map((doc) => ({ title: doc.title, chars: doc.text.length })),
  messages,
}, null, 1));
