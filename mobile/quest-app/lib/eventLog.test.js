/* Plain node test, no device and no jest: run with `node lib/eventLog.test.js`.
 *
 * Written alongside the "Diagnostics" screen so an on-device pass produces a
 * record of what actually happened instead of relying on memory, per
 * CLAUDE.md step 5d: verify a claim before acting on it, applied to this
 * app's own future on-device checks.
 */
const assert = require("assert");
const { MAX_EVENTS, logEvent, summarize, formatForDisplay } = require("./eventLog");

function run(name, fn) {
  fn();
  console.log("ok  " + name);
}

run("an empty log summarizes to zero with no bounds", () => {
  const sum = summarize([]);
  assert.strictEqual(sum.count, 0);
  assert.deepStrictEqual(sum.byType, {});
  assert.strictEqual(sum.firstAt, null);
  assert.strictEqual(sum.lastAt, null);
});

run("logEvent appends without mutating the original array", () => {
  const before = [];
  const after = logEvent(before, "card_done", "A|Z|sort", 1000);
  assert.strictEqual(before.length, 0, "the original array must be untouched");
  assert.strictEqual(after.length, 1);
  assert.deepStrictEqual(after[0], { type: "card_done", detail: "A|Z|sort", at: 1000 });
});

run("detail defaults to null rather than undefined", () => {
  const [entry] = logEvent([], "stopped", undefined, 5);
  assert.strictEqual(entry.detail, null);
});

run("summarize counts by type and reports the real span", () => {
  let log = [];
  log = logEvent(log, "card_done", "a", 100);
  log = logEvent(log, "card_done", "b", 200);
  log = logEvent(log, "card_skipped", "c", 300);
  const sum = summarize(log);
  assert.strictEqual(sum.count, 3);
  assert.deepStrictEqual(sum.byType, { card_done: 2, card_skipped: 1 });
  assert.strictEqual(sum.firstAt, 100);
  assert.strictEqual(sum.lastAt, 300);
});

run("the log never grows past MAX_EVENTS, oldest dropped first", () => {
  let log = [];
  for (let i = 0; i < MAX_EVENTS + 10; i++) {
    log = logEvent(log, "card_done", String(i), i);
  }
  assert.strictEqual(log.length, MAX_EVENTS);
  assert.strictEqual(log[0].detail, "10", "the ten oldest entries must be gone");
  assert.strictEqual(log[log.length - 1].detail, String(MAX_EVENTS + 9));
});

run("formatForDisplay on an empty log says so plainly, not a blank string", () => {
  const text = formatForDisplay([]);
  assert.strictEqual(text, "No activity recorded yet this install.");
});

run("formatForDisplay includes the type counts and the most recent entries", () => {
  let log = [];
  log = logEvent(log, "card_done", "A|Z|sort", 0);
  log = logEvent(log, "zone_finished", "Landing Zone", 60000);
  const text = formatForDisplay(log);
  assert.ok(text.includes("2 event(s) recorded"), text);
  assert.ok(text.includes("card_done: 1"), text);
  assert.ok(text.includes("zone_finished: 1"), text);
  assert.ok(text.includes("Landing Zone"), text);
});

console.log("\nall eventLog tests passed");
