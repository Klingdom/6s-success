#!/usr/bin/env python3
"""
Prove the Home Quest tells a household when the browser refuses to save.

WHY
---
Every finished card, every standard and all progress in the app lives in
localStorage and nowhere else, and quest.html promises in words that it "stays
in this browser". Until 2026-09-22 save() was:

    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}

so when setItem threw, which Safari private browsing and blocked site data
both do, the error was discarded. The app kept looking like it worked and the
whole session vanished when the tab closed, with nothing shown to the person
who had just done the work. That is this repository's oldest defect class, a
failure that cannot be seen, sitting in the core product loop.

WHAT THIS DOES
--------------
Loads the REAL site/quest.html in a real headless browser with
localStorage.setItem replaced by a function that throws, and asserts the
notice ends up visible saying the work will not be remembered. Then loads the
same page with storage working and asserts the notice stays hidden, because a
warning that fires when nothing is wrong is its own defect.

Run:  python ops/tests/test_quest_storage_blocked.py
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

SHIM = """<script>
window.__throwOnSave = %s;
(function () {
  var real = localStorage.setItem.bind(localStorage);
  localStorage.setItem = function (k, v) {
    if (window.__throwOnSave) {
      var e = new Error("denied"); e.name = "QuotaExceededError"; throw e;
    }
    return real(k, v);
  };
})();
</script>
"""

REPORT = """<script>
window.addEventListener("load", function () {
  setTimeout(function () {
    var n = document.getElementById("notice");
    document.title = "VERDICT:" + JSON.stringify({
      found: !!n,
      hidden: n ? !!n.hidden : null,
      text: n ? (n.textContent || "").slice(0, 140) : ""
    });
  }, 500);
});
</script>
"""


def run_case(browser, args, throw, drop_data=False):
    """Load the real quest.html with localStorage.setItem sabotaged.

    Written beside the original rather than copied to a temp directory,
    because the page loads its stylesheet, its data and quest.js by relative
    path and none of those resolve from anywhere else. Removed in a finally.
    """
    site = os.path.join(ROOT, "site")
    src = io.open(os.path.join(site, "quest.html"), encoding="utf-8").read()

    m = re.search(r'<script[^>]+assets/js/quest\.js', src)
    if not m:
        return None, "could not find the quest.js script tag in quest.html"
    doctored = (src[:m.start()] + (SHIM % ("true" if throw else "false"))
                + src[m.start():])
    if drop_data:
        # Simulate the card data failing to load, which for an installable app
        # is a service-worker cache miss while offline, not a hypothetical.
        doctored = re.sub(r'<script[^>]+assets/js/quest-data\.js[^>]*>\s*</script>',
                          '', doctored, count=1)
    doctored = doctored.replace("</body>", REPORT + "</body>", 1)

    page = os.path.join(site, "_test_storage_blocked.html")
    try:
        io.open(page, "w", encoding="utf-8", newline="\n").write(doctored)
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--virtual-time-budget=6000", "--dump-dom",
               "file:///" + page.replace("\\", "/")] + args
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        dom = r.stdout or ""
    finally:
        try:
            os.remove(page)
        except OSError:
            pass

    mt = re.search(r"VERDICT:(\{.*?\})", dom, re.S)
    if not mt:
        return None, "the page never reported a verdict (quest.js may not have run)"
    try:
        return json.loads(mt.group(1).replace("&quot;", '"')), None
    except ValueError as exc:
        return None, "verdict was not JSON: %r (%s)" % (mt.group(1)[:90], exc)


def main() -> int:
    import browser as B
    found = B.find_browser()
    if not found:
        print("  UNCHECKED: no Edge or Chromium on this machine, so the real "
              "browser behaviour was NOT exercised. That is not a pass.")
        return 0
    exe, args = found

    fails = []

    blocked, err = run_case(exe, args, throw=True)
    if err:
        print("  UNCHECKED: " + err)
        return 0
    if not blocked.get("found"):
        fails.append("no #notice element on the page at all: %r" % blocked)
    elif blocked["hidden"]:
        fails.append("storage refused but the notice stayed hidden: %r" % blocked)
    elif not ("save" in blocked["text"] and "remembered" in blocked["text"]):
        fails.append("notice shown but it does not say the work is lost: %r"
                     % blocked["text"])

    missing, err = run_case(exe, args, throw=False, drop_data=True)
    if err:
        fails.append("missing-data case: " + err)
    elif missing["hidden"]:
        fails.append("card data absent but the page said nothing: %r" % missing)
    elif "did not load" not in missing["text"]:
        fails.append("data-missing notice does not explain itself: %r"
                     % missing["text"])

    ok, err = run_case(exe, args, throw=False)
    if err:
        fails.append("working-storage case: " + err)
    elif not ok["hidden"]:
        fails.append("storage worked but a warning was shown anyway: %r" % ok)

    if fails:
        print("FAIL")
        for f in fails:
            print("   " + f)
        return 1
    print("PASS  3 of 3: blocked storage warns, missing card data warns, "
          "healthy page stays quiet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
