/* Plain node test, no device and no jest: run with `node lib/videoLink.test.js`.
 *
 * The card may only ever offer a zone video that is genuinely published. A
 * link built from a blank, malformed or missing id would look exactly like a
 * working one until somebody pressed it, on the screen they are working from.
 */
const assert = require("assert");
const { videoUrl } = require("./videoLink");

function run(name, fn) {
  fn();
  console.log("ok  " + name);
}

run("a published id becomes a youtube watch url", () => {
  assert.strictEqual(
    videoUrl({ zone: "Landing Zone", video: "HJ2Uy0kSXkM" }),
    "https://www.youtube.com/watch?v=HJ2Uy0kSXkM"
  );
});

run("a zone with no video field offers nothing", () => {
  assert.strictEqual(videoUrl({ zone: "Sock Drawer" }), null);
});

run("null and undefined zones are safe", () => {
  assert.strictEqual(videoUrl(null), null);
  assert.strictEqual(videoUrl(undefined), null);
});

run("an empty or whitespace id offers nothing", () => {
  assert.strictEqual(videoUrl({ video: "" }), null);
  assert.strictEqual(videoUrl({ video: "   " }), null);
});

run("a malformed id is refused rather than linked", () => {
  assert.strictEqual(videoUrl({ video: "short" }), null);
  assert.strictEqual(videoUrl({ video: "waytoolongforanid" }), null);
  assert.strictEqual(videoUrl({ video: "bad id chars" }), null);
  assert.strictEqual(videoUrl({ video: "HJ2Uy0kSXk!" }), null);
});

run("a non-string id is refused", () => {
  assert.strictEqual(videoUrl({ video: 12345678901 }), null);
  assert.strictEqual(videoUrl({ video: { id: "HJ2Uy0kSXkM" } }), null);
});

run("the bundled corpus carries exactly the published videos, all valid", () => {
  const corpus = require("../assets/quest-corpus.json");
  const withVideo = corpus.zones.filter((z) => z.video);
  assert.ok(withVideo.length > 0, "no zone in the corpus carries a video");
  withVideo.forEach((z) => {
    assert.ok(videoUrl(z), "corpus zone " + z.zone + " has an unusable video id");
  });
  console.log("    " + withVideo.length + " of " + corpus.zones.length +
              " zones carry a usable video id");
});

console.log("\n  videoLink: all cases pass");
