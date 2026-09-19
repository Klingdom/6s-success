"""Drive 'Work a room' and 'One S across a room' with the room dropdown left
on its own default, and prove they refuse rather than silently run the whole
house.

Both controls carry the caption "Uses the room chosen above" directly under
them. build()'s own room filter is skipped entirely whenever the room name it
is given is falsy, which is correct and deliberate for mode "draw" (room
passed as null on purpose, meaning "anywhere in the house") but was also
happening, unguarded, for modes "room" and "spass" whenever #room-select was
still on its default "Choose a room" option (value ""). A visitor who tapped
either button without picking a room first got a real card, with no error
and no indication anything was different, from a queue built across every
room in the house: for "spass" on a fresh house that is 114 cards, not the
roughly 30-40 a single room holds. The copy promised a room; the control
silently gave the whole house instead, the exact "copy and control disagree"
shape CLAUDE.md 0.6/section 6 treats as a trust defect, not a polish item.

Confirmed live before fixing: room-select.value was "", and the card that
opened read "1 of 114", the whole-house Sort-pass count, not a single room's.

Run:  python ops/tests/test_quest_mode_requires_room.py
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
var out = {};
function done(){ document.title = "Q>>" + JSON.stringify(out) + "<<E"; }
function txt(d, id){ var e = d.getElementById(id); return e ? (e.textContent||"").trim() : ""; }
function hid(d, id){ var e = d.getElementById(id); return e ? !!e.hidden : "MISSING"; }

var frame = document.getElementById("f");
var phase = 0;
frame.addEventListener("load", function(){
  var d;
  try { d = frame.contentDocument; } catch (e) { out.error = "blocked"; return done(); }
  if (!d || !d.body) { out.error = "no document"; return done(); }
  if (phase === 0) {
    phase = 1;
    try { d.defaultView.localStorage.clear(); } catch (e) {}
    frame.contentWindow.location.reload();
    return;
  }
  if (phase !== 1) return;
  phase = 2;

  setTimeout(function(){
    var symOther = d.getElementById("sym-other");
    if (!symOther) { out.error = "no #sym-other"; return done(); }
    symOther.click();
    setTimeout(function(){
      var goOther = d.getElementById("go-other");
      if (!goOther) { out.error = "no #go-other"; return done(); }
      goOther.click();
      setTimeout(function(){
        var sel = d.getElementById("room-select");
        out.roomSelectValue = sel ? sel.value : "MISSING";

        // "Work a room" with no room chosen.
        var goRoom = d.getElementById("go-room");
        if (!goRoom) { out.error = "no #go-room"; return done(); }
        goRoom.click();

        setTimeout(function(){
          out.roomCardShown = !hid(d, "view-card");
          out.roomAlertShown = !hid(d, "notice");
          out.roomAlertText = txt(d, "notice");

          // "One S across a room" with no room chosen either.
          var goSpass = d.getElementById("go-spass");
          if (!goSpass) { out.error = "no #go-spass"; return done(); }
          goSpass.click();

          setTimeout(function(){
            out.spassCardShown = !hid(d, "view-card");
            out.spassAlertShown = !hid(d, "notice");
            out.spassAlertText = txt(d, "notice");

            // Now choose a real room and confirm the ordinary path still works.
            sel.selectedIndex = 1;
            out.chosenRoom = sel.options[sel.selectedIndex].value;
            goRoom.click();
            setTimeout(function(){
              out.withRoomCardShown = !hid(d, "view-card");
              out.withRoomZone = txt(d, "c-where");
              out.withRoomCount = txt(d, "c-count");
              done();
            }, 500);
          }, 500);
        }, 500);
      }, 400);
    }, 400);
  }, 900);
});
</script></body></html>"""


def main() -> int:
    found = B.find_browser()
    if not found:
        print("  no browser here, cannot drive the Quest. NOT VERIFIED.")
        return 0
    edge, extra = found

    profile = tempfile.mkdtemp(prefix="6s-quest-moderoom-profile-")
    wrap = os.path.join(SITE, "_quest_mode_requires_room_probe.html")
    io.open(wrap, "w", encoding="utf-8", newline="").write(WRAPPER)
    try:
        r = subprocess.run(
            [edge] + extra +
            ["--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", "--allow-file-access-from-files",
             "--user-data-dir=" + profile,
             "--window-size=520,1440", "--virtual-time-budget=15000",
             "--dump-dom", "file:///" + wrap.replace("\\", "/")],
            capture_output=True, timeout=180)
    finally:
        if os.path.exists(wrap):
            os.remove(wrap)
        shutil.rmtree(profile, ignore_errors=True)

    dom = r.stdout.decode("utf-8", "replace")
    m = re.search(r"Q(?:&gt;&gt;|>>)(.*?)(?:&lt;&lt;|<<)E", dom, re.S)
    if not m:
        print("  the probe did not run, so nothing was exercised. "
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

    bad = []
    if o.get("roomSelectValue") != "":
        bad.append("test setup did not leave the room dropdown on its "
                    "default: %r" % o.get("roomSelectValue"))
    if o.get("roomCardShown"):
        bad.append("'Work a room' with no room chosen opened a card anyway "
                    "(silently ran the whole house)")
    if not o.get("roomAlertShown"):
        bad.append("'Work a room' with no room chosen showed no message at all")
    if o.get("spassCardShown"):
        bad.append("'One S across a room' with no room chosen opened a card "
                    "anyway (silently ran the whole house)")
    if not o.get("spassAlertShown"):
        bad.append("'One S across a room' with no room chosen showed no "
                    "message at all")
    if not o.get("withRoomCardShown"):
        bad.append("choosing a real room and tapping 'Work a room' no longer "
                    "works at all")
    if o.get("withRoomCount") and not o["withRoomCount"].startswith("1 of "):
        bad.append("with a room chosen, the card count is not '1 of N': %r"
                    % o.get("withRoomCount"))
    # Entryway holds 30 cards; a whole-house run would read "1 of 114".
    if o.get("chosenRoom") == "Entryway" and o.get("withRoomCount") != "1 of 30":
        bad.append("choosing Entryway and tapping 'Work a room' did not scope "
                    "to Entryway's own 30 cards: got %r" % o.get("withRoomCount"))
    for b in bad:
        print("  FAIL " + b)
    if bad:
        print("  observed: %s" % json.dumps(o)[:800])
        return 1

    print("  ok  'Work a room' and 'One S across a room' both refuse with a "
          "plain message when no room is chosen, instead of silently running "
          "every room in the house; choosing a room still works correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
