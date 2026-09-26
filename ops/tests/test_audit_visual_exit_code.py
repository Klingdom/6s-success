"""Proves ops/audit_visual.py's own process exit code means what it says.

Found 2026-09-26, cold-reading the file: `main()`'s final line was
`return 1 if (bad_text or bad_img) else 0`, so the process only ever exited
non-zero for two of the nine categories the tool itself computes and prints.
A broken image, a missing form label, an invisible focus outline, a bad
landmark/h1, a heading level jump, or (on --mobile) a crowded tiny target or
a sideways-scrolling page, could all be printed right above a clean `$?`.

Not a live customer-facing defect: `gate_visual_audit` and
`gate_mobile_touch_targets` in ops/preflight.py both parse the tool's
printed counts directly, never this return value, so no gate was fooled.
But it is the same "check that cannot fail" shape the last several cold-read
cycles have been fixing elsewhere (merge_cardtext.py, wire_nav.py,
wire_landmarks.py): a person running this tool directly and trusting its
exit code would have been. Reproduced directly below with a real headless
Chromium render, not asserted from reading the source.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(ROOT, "ops"))
import browser as B                                             # noqa: E402


class NotVerified(Exception):
    """No browser here; see test_audit_visual_reduced_motion.py's own note."""


# A 1x1 transparent GIF, inline, so the page needs no network and no other
# fixture file to render a real, loaded <img> with no alt attribute at all
# (a defect in "images without alt", a category outside bad_text/bad_img).
_PAGE = (
    "<!doctype html><html><head><title>t</title></head><body>"
    "<main><h1>Title</h1>"
    "<img src='data:image/gif;base64,"
    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==' width='10' height='10'>"
    "</main></body></html>"
)


def test_exit_code_is_nonzero_for_a_real_finding_outside_bad_text_bad_img():
    if not B.find_browser():
        raise NotVerified("no browser here to render the probe page")
    page = os.path.join(SITE, "_test_audit_exit_code_probe.html")
    # Deliberately NOT underscore-prefixed at the point audit_visual.py reads
    # it: main() skips any page whose basename starts with "_" (its own
    # scratch-probe convention), so a leading underscore here would make the
    # tool silently measure nothing and still print "pages measured: 1".
    real_page = os.path.join(SITE, "audit_exit_code_probe.html")
    with open(real_page, "w", encoding="utf-8", newline="") as f:
        f.write(_PAGE)
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "ops", "audit_visual.py"),
             real_page],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert "pages measured        : 1" in r.stdout, (
            "the probe page was not actually measured, so this proves "
            "nothing: %r" % r.stdout[-400:])
        assert "images without alt    : 1" in r.stdout, (
            "the probe page's missing alt attribute was not detected at "
            "all, a different defect than the one this test targets: %r"
            % r.stdout[-400:])
        assert r.returncode == 1, (
            "a real, printed finding (images without alt: 1) left the "
            "process exiting %d; the exit code no longer reflects only "
            "bad_text/bad_img, so this regressed" % r.returncode)
    finally:
        if os.path.exists(real_page):
            os.remove(real_page)
        if os.path.exists(page):
            os.remove(page)


def test_exit_code_is_zero_for_a_page_with_no_findings():
    if not B.find_browser():
        raise NotVerified("no browser here to render the probe page")
    real_page = os.path.join(SITE, "audit_exit_code_clean_probe.html")
    with open(real_page, "w", encoding="utf-8", newline="") as f:
        f.write(
            "<!doctype html><html><head><title>t</title></head>"
            "<body><main><h1>Title</h1><p>Clean page, nothing to find.</p>"
            "</main></body></html>"
        )
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "ops", "audit_visual.py"),
             real_page],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert "pages measured        : 1" in r.stdout, (
            "the probe page was not actually measured: %r" % r.stdout[-400:])
        assert r.returncode == 0, (
            "a page with no real findings still exited %d: %r"
            % (r.returncode, r.stdout[-600:]))
    finally:
        if os.path.exists(real_page):
            os.remove(real_page)


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
