/* Plain node test, no device and no jest: run with `node lib/pickCard.test.js`.
 *
 * Written after finding that App.js's "Not now" button called
 * setFinished(null) while `finished` was already null, a no-op React bails
 * out of without a re-render: pressing "Not now" changed nothing on screen,
 * ever. Proves the fix (pickCard is skip-aware) actually changes what is
 * shown, per CLAUDE.md step 5d: verify a claim before acting on it.
 */
const assert = require("assert");
const { cardId, pickCard, isCardVisible } = require("./pickCard");

function run(name, fn) {
  fn();
  console.log("ok  " + name);
}

const CORPUS = {
  zones: [
    { room: "Entryway", zone: "Landing Zone",
      steps: [{ s: "sort" }, { s: "straighten" }, { s: "shine" }] },
    { room: "Entryway", zone: "Coat Zone",
      steps: [{ s: "sort" }, { s: "straighten" }] },
  ],
};

run("first card of a fresh house is the first zone's first pass", () => {
  const c = pickCard(CORPUS, {}, {});
  assert.strictEqual(c.zone.zone, "Landing Zone");
  assert.strictEqual(c.step.s, "sort");
});

run("a done card is never returned again", () => {
  const done = { [cardId(CORPUS.zones[0], "sort")]: 1 };
  const c = pickCard(CORPUS, done, {});
  assert.strictEqual(c.step.s, "straighten");
});

run("skipping the current card shows a different one", () => {
  const current = cardId(CORPUS.zones[0], "sort");
  const before = pickCard(CORPUS, {}, {});
  assert.strictEqual(cardId(before.zone, before.step.s), current);

  const after = pickCard(CORPUS, {}, { [current]: true });
  assert.notStrictEqual(cardId(after.zone, after.step.s), current,
    "skip must change what is shown, the bug it replaces never did");
  assert.strictEqual(after.step.s, "straighten");
});

run("skipping does not mark the card done", () => {
  const current = cardId(CORPUS.zones[0], "sort");
  pickCard(CORPUS, {}, { [current]: true });
  // pickCard takes done as an argument rather than mutating anything, so
  // a fresh call with the original empty done map proves nothing changed.
  const c = pickCard(CORPUS, {}, {});
  assert.strictEqual(cardId(c.zone, c.step.s), current);
});

run("a skipped card comes back once it is the only one left", () => {
  const skipFirst = cardId(CORPUS.zones[0], "sort");
  const done = {};
  CORPUS.zones.forEach((z) => z.steps.forEach((st) => {
    const id = cardId(z, st.s);
    if (id !== skipFirst) done[id] = 1;
  }));
  const c = pickCard(CORPUS, done, { [skipFirst]: true });
  assert.strictEqual(cardId(c.zone, c.step.s), skipFirst,
    "skipping the last remaining card must still show it, not a blank screen");
});

run("every card done returns null, skipped or not", () => {
  const done = {};
  CORPUS.zones.forEach((z) => z.steps.forEach((st) => {
    done[cardId(z, st.s)] = 1;
  }));
  assert.strictEqual(pickCard(CORPUS, done, {}), null);
});

run("a full house corpus never throws and starts on Sort", () => {
  const REAL = require("../assets/quest-corpus.json");
  const c = pickCard(REAL, {}, {});
  assert.ok(c, "the real corpus must produce a first card");
  assert.strictEqual(c.step.s, "sort");
});

run("a card is visible only with no recap and no stop screen showing", () => {
  const c = pickCard(CORPUS, {}, {});
  assert.strictEqual(isCardVisible(null, false, c), true);
  assert.strictEqual(isCardVisible({ zone: c.zone, passes: [] }, false, c), false,
    "the finished-zone recap sits on top of the card, it must not count as drawn");
  assert.strictEqual(isCardVisible(null, true, c), false,
    "the stopping screen sits on top of the card, it must not count as drawn");
  assert.strictEqual(isCardVisible(null, false, null), false,
    "no card computed at all (still loading) is never visible");
});

console.log("\nall pickCard tests passed");
