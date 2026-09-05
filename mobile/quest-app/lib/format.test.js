/* Plain node test, no device and no jest: run with `node lib/format.test.js`.
 *
 * Guards the exact defect fixed 2026-09-05: a missing space where "is"/"are"
 * meets the surrounding text, the shape a JSX line break silently produces.
 */
const assert = require("assert");
const { zonesHoldingLine } = require("./format");

function run(name, fn) {
  fn();
  console.log("ok  " + name);
}

run("singular zone uses 'is' with a space on both sides", () => {
  assert.strictEqual(
    zonesHoldingLine(1, 114),
    "1 of 114 zones in the house is holding."
  );
});

run("plural zones use 'are' with a space on both sides", () => {
  assert.strictEqual(
    zonesHoldingLine(5, 114),
    "5 of 114 zones in the house are holding."
  );
});

run("zero zones uses 'are', not 'is'", () => {
  assert.strictEqual(
    zonesHoldingLine(0, 114),
    "0 of 114 zones in the house are holding."
  );
});

run("no word is run together: every expected word boundary has a space", () => {
  const line = zonesHoldingLine(1, 114);
  ["house is", "is holding"].forEach((phrase) => {
    assert.ok(line.includes(phrase), phrase + " missing from: " + line);
  });
});
