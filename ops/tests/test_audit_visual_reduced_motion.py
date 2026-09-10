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
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = os.path.join(ROOT, "ops")
sys.path.insert(0, OPS)
import audit_visual as av                                      # noqa: E402
import browser as B                                             # noqa: E402


def test_audit_passes_force_reduced_motion_to_chrome():
    src = inspect.getsource(av.audit)
    assert "--force-prefers-reduced-motion" in src, (
        "ops/audit_visual.py's audit() no longer forces reduced motion; "
        "the .reveal fade-in race this test file documents is back."
    )


def test_force_reduced_motion_flag_actually_works_on_this_browser():
    found = B.find_browser()
    if not found:
        return  # no browser here; audit_visual.py's own gates already
                # report this honestly elsewhere, nothing new to prove
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


if __name__ == "__main__":
    fns = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok:", fn.__name__)
    print("%d of %d cases pass" % (len(fns), len(fns)))
