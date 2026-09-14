"""Proves the fix for a real, reproduced flake in ops/audit_visual.py.

2026-09-10: two back to back `audit_visual.py --all` runs on the same
unchanged site produced wildly different contrast numbers for
site/shop.html, some as low as 1.52:1 against a 4.5:1 floor. Computing WCAG
contrast by hand for the exact RGB pairs the tool reported (e.g. rgb(106,98,90)
on rgb(251,247,239)) gives 5.6:1, not 1.61:1: the numbers did not match the
page's real, static colours at all, so the failure was in the measurement,
not the page. `gate_visual_audit` in preflight.py turns this into a hard FAIL,
so a timing-dependent false positive here can block a whole cycle over
nothing.

Root cause: site.css fades every `.reveal` element in from `opacity:0` over a
real, wall-clock-timed 0.7s CSS transition once JavaScript adds `.in`
(site.js's IntersectionObserver, or its 200/250ms setTimeout fallbacks).
`audit_visual.py`'s own settle timer waits a fixed 250ms after images finish
loading, a real, variable amount of wall-clock time on a loaded machine, so
the DOM dump can land mid-transition. CSS transitions are driven by the
compositor's real elapsed time, not by Chrome's `--virtual-time-budget`
timers, so the two clocks can drift apart under load, exactly the way
audit_visual.py's own docstring already describes for the unrelated
one-in-190 "page NOT measured" case.

The fix passes `--force-prefers-reduced-motion` to the headless browser,
which makes it apply site.css's own `@media (prefers-reduced-motion:reduce)`
rule: `.reveal{opacity:1;transform:none}`, with no transition at all. That is
already a real, supported state (a visitor with that OS preference sees it
today) and it removes the race instead of trying to outrun it with a longer
timer.

A true fail/pass reproduction of the race itself is not practical here: it
depends on real CPU contention across a ~190 page run, and a synthetic
single-page test with a controlled transition did not reproduce it (Chrome's
IntersectionObserver did not fire at all under `--dump-dom`, and a
synchronous class-flip before first paint does not trigger a CSS transition
in the first place). So this proves the two things that are actually
checkable without racing the clock: the flag is present in the real,
committed subprocess call, and the flag genuinely does what the fix depends
on in this machine's real browser.
"""
import inspect
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import audit_visual as av                                      # noqa: E402
import browser as B                                             # noqa: E402


class NotVerified(Exception):
    """Raised when a case cannot exercise anything here (no browser).

    Returning normally used to print "ok:" for a case that never looked.
    CI runs these files on a GitHub runner where ops/browser.py finds no
    browser, so two of four cases reported passing without running. The
    runner prints NOT VERIFIED instead, the exact string gate_tests() in
    preflight.py already reports as tests-unverified.
    """


def test_audit_passes_force_reduced_motion_to_chrome():
    src = inspect.getsource(av.audit)
    assert "--force-prefers-reduced-motion" in src, (
        "ops/audit_visual.py's audit() no longer forces reduced motion; "
        "the .reveal fade-in race this test file documents is back."
    )


def test_force_reduced_motion_flag_actually_works_on_this_browser():
    found = B.find_browser()
    if not found:
        raise NotVerified("no browser here to test the reduced-motion flag")
    exe, extra = found
    page = os.path.join(os.path.dirname(__file__), "_rm_probe.html")
    with open(page, "w", encoding="utf-8", newline="") as f:
        f.write(
            "<!doctype html><html><body>"
            "<script>document.title="
            "matchMedia('(prefers-reduced-motion: reduce)').matches"
            "?'YES':'NO';</script></body></html>"
        )
    try:
        p = subprocess.run(
            [exe, "--headless=new", "--disable-gpu",
             "--force-prefers-reduced-motion",
             "--virtual-time-budget=2000", "--dump-dom", *extra,
             "file:///" + page.replace(os.sep, "/")],
            capture_output=True, text=True, timeout=30)
        m = re.search(r"<title>(\w+)</title>", p.stdout)
        assert m and m.group(1) == "YES", (
            "--force-prefers-reduced-motion did not make this browser match "
            "prefers-reduced-motion: reduce, so the fix's own mechanism "
            "cannot be relied on here: %r" % (p.stdout[:200],))
    finally:
        if os.path.exists(page):
            os.remove(page)


def test_site_css_still_disables_reveal_transition_under_reduced_motion():
    css = open(os.path.join(ROOT, "site", "assets", "css", "site.css"),
                encoding="utf-8").read()
    m = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*\}[^}]*)\}",
                   css, re.S)
    assert m, "no prefers-reduced-motion:reduce block in site.css"
    block = m.group(1)
    assert re.search(r"\.reveal\s*\{\s*opacity:\s*1", block), (
        "the reduced-motion block no longer forces .reveal to opacity:1; "
        "the fix in audit_visual.py relies on this rule existing."
    )



def test_reduced_motion_reveal_is_visible_in_a_real_browser():
    """The CSS text can say opacity:1 and still lose the cascade.

    Found 2026-09-14: the reduced-motion block wrote `.reveal{opacity:1}`
    while the fade rule is `.js .reveal{opacity:0; transition...}`, which is
    more specific. The text check above passed; the browser still rendered
    every reveal at opacity 0 with a 0.7s transition. So this reads the
    computed style of a real page, with reduced motion forced.
    """
    import subprocess
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import browser as B
    found = B.find_browser()
    if not found:
        raise NotVerified("no browser here to read the computed style")
    exe, extra = found
    probe = os.path.join(ROOT, "site", "_reduced_motion_probe.html")
    io.open(probe, "w", encoding="utf-8").write(
        '<!doctype html><meta charset="utf-8">'
        '<iframe id="f" src="book.html" style="width:1280px;height:900px"></iframe>'
        '<script>var f=document.getElementById("f");f.onload=function(){'
        'var d=f.contentDocument,w=f.contentWindow;'
        'var el=[].slice.call(d.querySelectorAll(".reveal")).filter('
        'function(e){return !e.classList.contains("in")})[0];'
        'var o=el?{found:1,opacity:w.getComputedStyle(el).opacity,'
        'dur:w.getComputedStyle(el).transitionDuration}:{found:0};'
        'var p=document.createElement("pre");'
        'p.textContent="RESULT"+JSON.stringify(o)+"ENDRESULT";'
        'document.body.appendChild(p)};</script>')
    try:
        p = subprocess.run(
            [exe, "--headless=new", "--disable-gpu",
             "--allow-file-access-from-files", "--force-prefers-reduced-motion",
             "--virtual-time-budget=100", "--dump-dom", *extra,
             "file:///" + probe.replace(os.sep, "/")],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=90)
    finally:
        os.remove(probe)
    m = re.search(r"RESULT(\{.*?\})ENDRESULT", p.stdout or "")
    assert m, "probe produced no result; unchecked, not passing"
    import json
    r = json.loads(m.group(1))
    assert r["found"], "no un-revealed .reveal element on book.html to measure"
    assert float(r["opacity"]) == 1.0, (
        "under prefers-reduced-motion a .reveal element renders at opacity "
        "%s, so reduced-motion visitors still get the fade" % r["opacity"])
    assert all(float(x.rstrip("s")) == 0 for x in r["dur"].split(",")), (
        "under prefers-reduced-motion .reveal still transitions (%s)" % r["dur"])

if __name__ == "__main__":
    fns = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, unverified = 0, 0
    for fn in fns:
        try:
            fn()
        except NotVerified as e:
            unverified += 1
            print("SKIPPED (NOT VERIFIED): %s: %s" % (fn.__name__, e))
            continue
        passed += 1
        print("ok:", fn.__name__)
    print("%d of %d cases pass%s" % (
        passed, len(fns),
        ", %d NOT VERIFIED (unchecked, not passing)" % unverified if unverified else ""))
