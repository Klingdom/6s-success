"""Drive the Home Quest's finish-screen offer past a single zone and check the
button that gets pitched actually matches the sentence beside it.

Nothing has ever exercised this in a real browser. `quest.js` (renderFinish())
decides which of two pitches to show by counting held zones and the rooms they
sit in, then repoints one shared button's href, data-sku and label to match:

    held zones in >= 2 different rooms  -> "The same cards on paper, $19"
                                            (PACK-HOUSE, a Stripe link)
    held zones, still inside one room   -> "Get the printable deck, free"
                                            (DECK-ENTRY, deck.html)

The button ships in the markup already wearing the PACK-HOUSE identity, so a
test that only ever finishes ONE zone (every existing quest test, including
test_quest_flow.py) can never tell whether the swap runs at all: the
untouched default already looks correct by coincidence. This is why
BACKLOG-2026-09-07.md's own handoff named this path, and a static text/link
audit (gate_no_stale_hardcoded_stripe_link) already proves the PACK-HOUSE
href is a live Stripe link, but that says nothing about whether the OTHER
branch, the one that overwrites it with the free deck, ever actually fires.

Forces the free-deck branch by seeding two full zones inside one room
(Entryway) via localStorage, exactly the shape a real visitor's own saves
would take, then finishing the one card left. A second pass seeds one room
fully plus a second room down to its last card, to prove the multi-room
branch still produces the shipped PACK-HOUSE identity on purpose, not by
never having moved.

Driven through an iframe at phone width, same method as test_quest_flow.py.
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
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import browser as B                                           # noqa: E402

WRAPPER = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}iframe{width:390px;height:1400px;border:0}</style>
</head><body><iframe id="f" src="quest.html"></iframe><script>
var out = { A: {}, B: {} };
function done(){ document.title = "Q>>" + JSON.stringify(out) + "<<E"; }
function vis(d, id){ var e = d.getElementById(id); return !!e && !e.hidden
    && getComputedStyle(e).display !== "none"; }
function txt(d, id){ var e = d.getElementById(id); return e ? (e.textContent||"").trim() : ""; }
function attr(d, id, name){ var e = d.getElementById(id); return e ? e.getAttribute(name) : null; }

function findRoom(win, name){
  return win.QUEST.rooms.filter(function (r) { return r.room === name; })[0];
}

// Seeds state.done so every zone in every named room is fully finished,
// except the LAST zone of the LAST room in the list, which is left one step
// (its own last step) short. That leaves exactly one card in the queue when
// that room is picked in "Work a room" mode, so completing it is one click,
// not a whole room's worth.
function seedAlmostDone(win, roomNames){
  var doneObj = {};
  var now = Date.now();
  roomNames.forEach(function (name, ri) {
    var room = findRoom(win, name);
    var isLastRoom = ri === roomNames.length - 1;
    room.zones.forEach(function (z, zi) {
      var isTargetZone = isLastRoom && zi === room.zones.length - 1;
      var steps = isTargetZone ? z.steps.slice(0, z.steps.length - 1) : z.steps;
      steps.forEach(function (st) {
        doneObj[name + "|" + z.zone + "|" + st.s] = now;
      });
    });
  });
  return { done: doneObj };
}

function targetRoomLastZoneName(win, roomName){
  var room = findRoom(win, roomName);
  return room.zones[room.zones.length - 1].zone;
}

var frame = document.getElementById("f");
var phase = 0;    // 0: initial load, clear.  1: seed A, reload.
                  // 2: drive A, seed B, reload.  3: drive B, done.

function driveRoom(d, w, roomName, targetZoneName, bucket){
  var sel = d.getElementById("room-select");
  sel.value = roomName;
  sel.dispatchEvent(new w.Event("change"));
  var go = d.getElementById("go-room");
  go.click();

  setTimeout(function () {
    bucket.cardShown = vis(d, "view-card");
    bucket.zoneLine  = txt(d, "c-where");
    bucket.count     = txt(d, "c-count");
    bucket.matchesTarget = bucket.zoneLine.indexOf(targetZoneName) !== -1;

    var doneBtn = d.getElementById("c-done");
    bucket.hasDone = !!doneBtn;
    if (!doneBtn) { return afterBucket(bucket); }
    doneBtn.click();

    setTimeout(function () {
      bucket.finishShown = vis(d, "view-finish");
      bucket.offerShown  = vis(d, "f-offer");
      bucket.offerHead   = txt(d, "f-offer-head");
      bucket.offerBody   = txt(d, "f-offer-body");
      bucket.ctaLabel    = txt(d, "f-offer-cta");
      bucket.ctaHref     = attr(d, "f-offer-cta", "href");
      bucket.ctaSku      = attr(d, "f-offer-cta", "data-sku");
      var evts = (w.__evt || []).filter(function (e) { return e[0] === "quest-offer-shown"; });
      bucket.offerEvent = evts.length ? evts[evts.length - 1][1] : null;
      afterBucket(bucket);
    }, 500);
  }, 500);
}

function afterBucket(bucket){
  if (bucket === out.A) {
    // Scenario A done. Wipe storage, seed the cross-room scenario, reload.
    var d = frame.contentDocument, w = d.defaultView;
    var seedB = seedAlmostDone(w, ["Entryway", "Kitchen"]);
    try {
      w.localStorage.setItem("6s.quest.v1", JSON.stringify(seedB));
    } catch (e) { out.seedBError = String(e); return done(); }
    phase = 3;
    frame.contentWindow.location.reload();
    return;
  }
  done();
}

frame.addEventListener("load", function () {
  var d, w;
  try { d = frame.contentDocument; w = d.defaultView; }
  catch (e) { out.error = "blocked: " + e.message; return done(); }
  if (!d || !d.body) { out.error = "no document"; return done(); }

  if (phase === 0) {
    phase = 1;
    try { w.localStorage.clear(); } catch (e) {}
    frame.contentWindow.location.reload();
    return;
  }

  if (phase === 1) {
    phase = 2;
    var seedA = seedAlmostDone(w, ["Entryway"]);
    try {
      w.localStorage.setItem("6s.quest.v1", JSON.stringify(seedA));
    } catch (e) { out.seedAError = String(e); return done(); }
    frame.contentWindow.location.reload();
    return;
  }

  if (phase === 2) {
    setTimeout(function () {
      w.__evt = [];
      w.Measure = { track: function (name, data) { w.__evt.push([name, data || {}]); } };
      out.A.roomSelectVisible = vis(d, "mode-list");
      driveRoom(d, w, "Entryway", targetRoomLastZoneName(w, "Entryway"), out.A);
    }, 500);
    return;
  }

  if (phase === 3) {
    setTimeout(function () {
      w.__evt = [];
      w.Measure = { track: function (name, data) { w.__evt.push([name, data || {}]); } };
      out.B.roomSelectVisible = vis(d, "mode-list");
      driveRoom(d, w, "Kitchen", targetRoomLastZoneName(w, "Kitchen"), out.B);
    }, 500);
    return;
  }
});
</script></body></html>"""


def main() -> int:
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-offer-profile-")
    wrap = os.path.join(SITE, "_quest_offer_cta_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=520,1440", "--virtual-time-budget=25000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=180)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"Q(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so the offer path was NOT exercised. "
              "This is unchecked, not working.")
        return 1
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        o = json.loads(raw)
    except ValueError:
        print("  probe output unreadable: %s" % raw[:200])
        return 1

    if o.get("error"):
        print("  probe error: %s" % o["error"])
        return 1
    if o.get("seedAError") or o.get("seedBError"):
        print("  could not seed localStorage: %s"
              % (o.get("seedAError") or o.get("seedBError")))
        return 1

    a, b = o.get("A") or {}, o.get("B") or {}
    bad = []

    if not a.get("roomSelectVisible"):
        bad.append("A: a returning visitor with saved progress is not shown "
                    "the room picker (mode-list stayed hidden)")
    if not a.get("cardShown"):
        bad.append("A: picking 'Work a room' on Entryway with one card left "
                    "did not open that card")
    if a.get("count") and a.get("count") != "one card":
        bad.append("A: expected exactly one card left in the seeded zone, "
                    "got count=%r" % a.get("count"))
    if not a.get("matchesTarget"):
        bad.append("A: the card opened is not the seeded zone's own last "
                    "step (zoneLine=%r)" % a.get("zoneLine"))
    if not a.get("finishShown"):
        bad.append("A: finishing the last seeded card did not reach the "
                    "finish view")
    if not a.get("offerShown"):
        bad.append("A: two zones held inside one room did not trigger the "
                    "further-offer block at all")
    if a.get("ctaSku") != "DECK-ENTRY":
        bad.append("A: two zones held in ONE room should pitch the free "
                    "Entryway deck (DECK-ENTRY); the button still carries "
                    "data-sku=%r, so the branch that repoints it away from "
                    "the default $19 pack either never ran or ran wrong"
                    % a.get("ctaSku"))
    if a.get("ctaHref") and "buy.stripe.com" in a.get("ctaHref"):
        bad.append("A: the free-deck pitch still links to a Stripe checkout "
                    "(%r); a visitor told 'free, no email needed' would be "
                    "asked to pay" % a.get("ctaHref"))
    if a.get("ctaLabel") and "$19" in a.get("ctaLabel") and a.get("ctaSku") == "DECK-ENTRY":
        bad.append("A: the button's label (%r) still names the $19 price "
                    "although its own data-sku says the free deck"
                    % a.get("ctaLabel"))
    if a.get("offerEvent") and a.get("offerEvent", {}).get("offer") != "entryway-deck":
        bad.append("A: quest-offer-shown fired with offer=%r, expected "
                    "'entryway-deck'" % a.get("offerEvent", {}).get("offer"))

    if not b.get("roomSelectVisible"):
        bad.append("B: a returning visitor with saved progress is not shown "
                    "the room picker")
    if not b.get("cardShown"):
        bad.append("B: picking 'Work a room' on Kitchen with one card left "
                    "did not open that card")
    if not b.get("matchesTarget"):
        bad.append("B: the card opened is not the seeded zone's own last "
                    "step (zoneLine=%r)" % b.get("zoneLine"))
    if not b.get("finishShown"):
        bad.append("B: finishing the last seeded card did not reach the "
                    "finish view")
    if not b.get("offerShown"):
        bad.append("B: zones held across two different rooms did not "
                    "trigger the further-offer block at all")
    if b.get("ctaSku") != "PACK-HOUSE":
        bad.append("B: zones held in TWO rooms should pitch the paper pack "
                    "(PACK-HOUSE); got data-sku=%r" % b.get("ctaSku"))
    if b.get("ctaHref") and "buy.stripe.com" not in (b.get("ctaHref") or ""):
        bad.append("B: the paper-pack pitch does not link to a Stripe "
                    "checkout at all (href=%r)" % b.get("ctaHref"))
    if b.get("offerEvent") and b.get("offerEvent", {}).get("offer") != "print-pack":
        bad.append("B: quest-offer-shown fired with offer=%r, expected "
                    "'print-pack'" % b.get("offerEvent", {}).get("offer"))
    if b.get("offerEvent") and b.get("offerEvent", {}).get("rooms", 0) < 2:
        bad.append("B: quest-offer-shown reported rooms=%r although two "
                    "different rooms were seeded held"
                    % b.get("offerEvent", {}).get("rooms"))

    for msg in bad:
        print("  FAIL " + msg)
    if bad:
        print("  observed A: %s" % json.dumps(a)[:500])
        print("  observed B: %s" % json.dumps(b)[:500])
        return 1

    print("  ok  one room held twice pitches %r (%s), two rooms held pitch "
          "%r (%s)" % (a.get("ctaSku"), a.get("ctaLabel"),
                        b.get("ctaSku"), b.get("ctaLabel")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
