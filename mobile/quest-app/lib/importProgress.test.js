/* Plain node test, no device and no jest: run with `node lib/importProgress.test.js`.
 * Proves the merge rule against the cases that matter before it ever touches
 * a real backup file, per CLAUDE.md step 5d: verify a claim before acting on it.
 */
const assert = require("assert");
const { parseBackup, mergeDone } = require("./importProgress");

function run(name, fn) {
  fn();
  console.log("ok  " + name);
}

run("rejects text that is not JSON", () => {
  assert.strictEqual(parseBackup("not json"), null);
});

run("rejects JSON with no done object", () => {
  assert.strictEqual(parseBackup(JSON.stringify({ foo: "bar" })), null);
  assert.strictEqual(parseBackup(JSON.stringify({ done: "nope" })), null);
  assert.strictEqual(parseBackup(JSON.stringify({ done: null })), null);
});

run("accepts a real backup shape", () => {
  const b = parseBackup(JSON.stringify({ done: { "Entryway|Landing Zone|sort": 1000 } }));
  assert.deepStrictEqual(b.done, { "Entryway|Landing Zone|sort": 1000 });
});

run("a card only on the phone is kept untouched", () => {
  const existing = { "A|Z|sort": 500 };
  const { done, changed } = mergeDone(existing, {});
  assert.deepStrictEqual(done, { "A|Z|sort": 500 });
  assert.strictEqual(changed, 0);
});

run("a card only in the backup is added", () => {
  const { done, changed } = mergeDone({}, { "A|Z|sort": 500 });
  assert.deepStrictEqual(done, { "A|Z|sort": 500 });
  assert.strictEqual(changed, 1);
});

run("a card on both sides keeps the earlier timestamp, phone earlier", () => {
  const existing = { "A|Z|sort": 100 };
  const { done, changed } = mergeDone(existing, { "A|Z|sort": 900 });
  assert.strictEqual(done["A|Z|sort"], 100);
  assert.strictEqual(changed, 0);
});

run("a card on both sides keeps the earlier timestamp, backup earlier", () => {
  const existing = { "A|Z|sort": 900 };
  const { done, changed } = mergeDone(existing, { "A|Z|sort": 100 });
  assert.strictEqual(done["A|Z|sort"], 100);
  assert.strictEqual(changed, 1);
});

run("importing never removes a card the phone already had done", () => {
  const existing = { "A|Z|sort": 1, "A|Z|straighten": 2, "A|Z|shine": 3 };
  const { done } = mergeDone(existing, { "A|Z|sort": 500 });
  assert.strictEqual(Object.keys(done).length, 3);
});

run("importing the same backup twice is idempotent", () => {
  const existing = {};
  const incoming = { "A|Z|sort": 500, "A|Z|straighten": 600 };
  const once = mergeDone(existing, incoming);
  const twice = mergeDone(once.done, incoming);
  assert.deepStrictEqual(once.done, twice.done);
  assert.strictEqual(twice.changed, 0);
});

run("a corrupted entry (non-numeric value) is dropped, not merged", () => {
  const b = parseBackup(JSON.stringify({ done: { "A|Z|sort": "corrupted", "A|Z|straighten": 500 } }));
  assert.deepStrictEqual(b.done, { "A|Z|straighten": 500 });
});

run("a corrupted entry can never erase a card the phone already had done", () => {
  const b = parseBackup(JSON.stringify({ done: { "A|Z|sort": "corrupted" } }));
  const existing = { "A|Z|sort": 1700000000000 };
  const { done, changed } = mergeDone(existing, b.done);
  assert.strictEqual(done["A|Z|sort"], 1700000000000);
  assert.strictEqual(changed, 0);
});

run("zero, negative and NaN timestamps are dropped, not treated as real", () => {
  const b = parseBackup(JSON.stringify({ done: { a: 0, b: -500, c: NaN, d: 1700000000000 } }));
  assert.deepStrictEqual(b.done, { d: 1700000000000 });
});

run("a corrupted existing (on-device) value cannot poison the merge into NaN", () => {
  const existing = { "A|Z|sort": "corrupted-legacy-value" };
  const incoming = { "A|Z|sort": 1700000000000 };
  const { done, changed } = mergeDone(existing, incoming);
  assert.strictEqual(done["A|Z|sort"], 1700000000000);
  assert.strictEqual(Number.isNaN(done["A|Z|sort"]), false);
  assert.strictEqual(changed, 1);
});

run("a zero or negative existing value is treated as absent, not as earliest", () => {
  const existing = { "A|Z|sort": 0, "A|Z|straighten": -5 };
  const incoming = { "A|Z|sort": 1700000000000, "A|Z|straighten": 1700000000000 };
  const { done } = mergeDone(existing, incoming);
  assert.strictEqual(done["A|Z|sort"], 1700000000000);
  assert.strictEqual(done["A|Z|straighten"], 1700000000000);
});

run("a full-house backup merges without dropping or inventing any card", () => {
  const CORPUS = require("../assets/quest-corpus.json");
  const backupDone = {};
  CORPUS.zones.forEach((z) => {
    z.steps.forEach((st) => {
      backupDone[z.room + "|" + z.zone + "|" + st.s] = 1700000000000;
    });
  });
  const { done, changed } = mergeDone({}, backupDone);
  assert.strictEqual(Object.keys(done).length, CORPUS.cardCount);
  assert.strictEqual(changed, CORPUS.cardCount);
});

console.log("\nall importProgress tests passed");
