#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_quest_session_placement() catches a hand edit
that silently drops A2's fix (site/assets/js/quest.js and site/quest.html,
2026-09-09): the whole-zone session length withheld from card one of a first
run, and restated on the finish screen instead.

Run:  python ops/tests/test_gate_quest_session_placement.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD_JS = (
    'var withholdSession = run.i === 0 && isFirstRun();\n'
    '$("#c-session").textContent = (c.zone.session && !withholdSession)\n'
    '  ? c.zone.session + " for the whole zone, six passes"\n'
    '  : "";\n'
    'var fSession = $("#f-session");\n'
)
GOOD_HTML = '<p class="q-note" id="f-session" hidden></p>'


def _run(js: str, html: str):
    tmp = tempfile.mkdtemp()
    try:
        js_dir = os.path.join(tmp, "assets", "js")
        os.makedirs(js_dir)
        io.open(os.path.join(js_dir, "quest.js"), "w", encoding="utf-8").write(js)
        io.open(os.path.join(tmp, "quest.html"), "w", encoding="utf-8").write(html)
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_quest_session_placement()
            return list(preflight.FAIL)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. Both halves present: no failure.
    r = _run(GOOD_JS, GOOD_HTML)
    if r:
        fails.append("clean files wrongly flagged: %r" % (r,))

    # 2. withholdSession dropped from quest.js: caught.
    r = _run(GOOD_JS.replace("withholdSession", "somethingElse"), GOOD_HTML)
    if not r or "quest.js" not in r[0][1]:
        fails.append("dropping withholdSession not caught: %r" % (r,))

    # 3. #f-session dropped from quest.html: caught.
    r = _run(GOOD_JS, "<p>no finish-screen session line here</p>")
    if not r or "quest.html" not in r[0][1]:
        fails.append("dropping #f-session from quest.html not caught: %r" % (r,))

    # 4. #f-session read but never actually referenced by the JS: caught.
    r = _run(GOOD_JS.replace('$("#f-session")', '/* removed */'), GOOD_HTML)
    if not r or "populates #f-session" not in r[0][1]:
        fails.append("quest.js no longer populating #f-session not caught: %r" % (r,))

    # 5. Neither file on disk: gate returns quietly rather than crashing.
    tmp = tempfile.mkdtemp()
    try:
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_quest_session_placement()
            if preflight.FAIL:
                fails.append("missing files wrongly flagged: %r" % (preflight.FAIL,))
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)

    # 6. The real, committed files: clean.
    real_js = os.path.join(ROOT, "site", "assets", "js", "quest.js")
    real_html = os.path.join(ROOT, "site", "quest.html")
    if not os.path.exists(real_js) or not os.path.exists(real_html):
        print("  (skipped: real quest.js/quest.html not found)")
    else:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_quest_session_placement()
        if preflight.FAIL:
            fails.append("real committed files failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_quest_session_placement, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
