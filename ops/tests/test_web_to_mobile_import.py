"""Prove a real web Quest backup imports into the mobile app.

lib/importProgress.test.js proves the merge rules against backups this project
wrote by hand. That is the right test for the rules and the wrong test for the
question a person actually has, which is "I used the website, will the app keep
my progress". Hand written fixtures agree with whatever shape the person writing
them believed in. This drives the real web Quest in a real browser, takes the
file its own backup() button would produce, and feeds that to the real mobile
parser.

It is the same class of check as everything else here: the web app and the app
are two products that must agree, and nothing had ever compared their actual
output rather than their intended output.

Needs a real Chromium-family browser (Edge or the sandbox's own Chromium,
see ops/browser.py) and node. Says so rather than passing when either is
missing.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
APP = os.path.join(ROOT, "mobile", "quest-app")
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import browser as B                                           # noqa: E402

# Drives the Quest the way a person would, then reports exactly what backup()
# would have written: JSON.stringify(state), not a reconstruction of it.
WRAPPER = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:390px;height:1400px;border:0}</style>
</head><body><iframe id="f" src="quest.html"></iframe><script>
var frame = document.getElementById("f"), phase = 0;
function done(o){ document.title = "B>>" + JSON.stringify(o) + "<<E"; }
frame.addEventListener("load", function(){
  var d;
  try { d = frame.contentDocument; } catch (e) { return done({error: "blocked"}); }
  if (!d || !d.body) return done({error: "no document"});
  if (phase === 0) {                       // clear, then reload for a clean start
    phase = 1;
    try { d.defaultView.localStorage.clear(); } catch (e) {}
    frame.contentWindow.location.reload();
    return;
  }
  if (phase !== 1) return;
  phase = 2;
  setTimeout(function(){
    var go = d.getElementById("go-first");
    if (!go) return done({error: "no start button"});
    go.click();
    setTimeout(function(){
      var clicks = 0;
      (function step(){
        var b = d.getElementById("c-done");
        if (b && clicks < 4) { clicks++; b.click(); return setTimeout(step, 240); }
        // Exactly what backup() serialises: the whole state object.
        var raw;
        try { raw = d.defaultView.localStorage.getItem("6s.quest.v1"); }
        catch (e) { raw = null; }
        done({ clicks: clicks, backupText: raw });
      })();
    }, 700);
  }, 800);
});
</script></body></html>"""


def main() -> int:
    found = B.find_browser()
    if not found:
        print("  no browser here, so no real backup could be produced. NOT VERIFIED.")
        return 0
    edge, extra = found
    if not shutil.which("node"):
        print("  no node here, so the mobile parser could not be run. NOT VERIFIED.")
        return 0

    profile = tempfile.mkdtemp(prefix="6s-import-")
    wrap = os.path.join(SITE, "_import_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=520,1440", "--virtual-time-budget=20000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=300)
        dom = r.stdout.decode("utf-8", "replace")
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    m = re.search(r"B(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the browser probe did not run, so nothing was compared. "
              "Unchecked, not working.")
        return 1
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        out = json.loads(raw)
    except ValueError:
        print("  probe output unreadable: %s" % raw[:200])
        return 1
    if out.get("error"):
        print("  probe error: %s" % out["error"])
        return 1

    backup_text = out.get("backupText")
    if not backup_text:
        print("  the web Quest stored nothing after %s cards, so there was no "
              "backup to import." % out.get("clicks"))
        return 1

    # What backup() writes is JSON.stringify(state). Hand the mobile parser
    # exactly that, through its own module, with no reshaping in between.
    node_src = """
const path = require("path");
const P = require(path.join(process.argv[2], "lib", "importProgress.js"));
const text = require("fs").readFileSync(process.argv[3], "utf8");
const parsed = P.parseBackup(text);
if (!parsed) { console.log(JSON.stringify({ok:false, why:"parseBackup rejected the real web backup"})); process.exit(0); }
const keys = Object.keys(parsed.done);
const merged = P.mergeDone({}, parsed.done);

// The assertion that matters. Matching key SHAPE is not enough: if the web
// writes a zone name the corpus does not carry, the import succeeds, the
// count looks right, and none of that progress ever marks a card done in the
// app. So every key from the real backup must resolve to a real zone and a
// real pass in the corpus the app actually ships.
const CORPUS = require(path.join(process.argv[2], "assets", "quest-corpus.json"));
const known = new Set();
for (const z of CORPUS.zones)
  for (const st of z.steps) known.add(z.room + "|" + z.zone + "|" + st.s);
const orphans = keys.filter(k => !known.has(k));

console.log(JSON.stringify({
  ok: true,
  cards: keys.length,
  sampleKey: keys[0] || null,
  mergedCards: Object.keys(merged.done).length,
  changed: merged.changed,
  orphans: orphans.length,
  orphanSample: orphans.slice(0, 3)
}));
"""
    tmp = tempfile.mkdtemp(prefix="6s-import-node-")
    try:
        bf = os.path.join(tmp, "backup.json")
        io.open(bf, "w", encoding="utf-8", newline="").write(backup_text)
        js = os.path.join(tmp, "run.js")
        io.open(js, "w", encoding="utf-8", newline="").write(node_src)
        nr = subprocess.run(["node", js, APP, bf], capture_output=True,
                            text=True, timeout=180)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if nr.returncode != 0:
        print("  the mobile parser errored on the real backup:\n%s"
              % (nr.stderr or "")[:400])
        return 1
    try:
        res = json.loads((nr.stdout or "").strip().splitlines()[-1])
    except Exception:                                         # noqa: BLE001
        print("  unreadable parser output: %s" % (nr.stdout or "")[:200])
        return 1

    bad = []
    if not res.get("ok"):
        bad.append(res.get("why", "the mobile parser rejected the real backup"))
    if res.get("cards", 0) < 1:
        bad.append("the real backup carried no cards")
    if res.get("mergedCards") != res.get("cards"):
        bad.append("merging the real backup into an empty phone changed the "
                   "card count: %s in, %s out"
                   % (res.get("cards"), res.get("mergedCards")))
    key = res.get("sampleKey") or ""
    if key.count("|") != 2:
        bad.append("the web writes card keys the app does not recognise: %r" % key)
    if res.get("orphans"):
        bad.append("%d card(s) in the real backup name a zone or pass that is "
                   "not in the app's corpus, so that progress would import and "
                   "then mark nothing done: %s"
                   % (res["orphans"], res.get("orphanSample")))

    for b in bad:
        print("  FAIL " + b)
    if bad:
        return 1
    print("  ok  a real web backup of %d card(s) parses, merges, and every key "
          "resolves to a real zone and pass in the app's corpus"
          % res["cards"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
