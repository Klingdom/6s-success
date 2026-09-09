#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_quest_card_victory_honesty() catches a hand
edit that silently brings back the "You can stop when" defect Phil's
commit fa491b1a (2026-09-07) fixed, or that drops the relabelling/note
that makes the fix true (site/assets/js/quest.js).

Run:  python ops/tests/test_gate_quest_card_victory_honesty.py
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
    '$("#c-done-look").textContent = c.zone.done || "";\n'
    'var note = $("#c-done-note");\n'
    'if (note) {\n'
    '  var pi = S_ORDER.indexOf(c.step.s);\n'
    '  note.textContent = c.zone.done\n'
    '    ? (pi >= 0\n'
    '       ? "That is all six passes together. This card is pass " + (pi + 1)\n'
    '         + " of 6, so you are not aiming for all of it right now."\n'
    '       : "That is all six passes together, not this one card.")\n'
    '    : "";\n'
    '}\n'
    'var doneHeading2 = document.querySelector("#c-done-wrap h3");\n'
    'if (doneHeading2) { doneHeading2.textContent = "The whole zone is done when"; }\n'
)


def _run(js: str):
    tmp = tempfile.mkdtemp()
    try:
        js_dir = os.path.join(tmp, "assets", "js")
        os.makedirs(js_dir)
        io.open(os.path.join(js_dir, "quest.js"), "w", encoding="utf-8").write(js)
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_quest_card_victory_honesty()
            return list(preflight.FAIL)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real fix, intact: no failure.
    r = _run(GOOD_JS)
    if r:
        fails.append("clean file wrongly flagged: %r" % (r,))

    # 2. The old, unreachable heading brought back: caught.
    r = _run(GOOD_JS + '\n$("#x").textContent = "You can stop when";\n')
    if not r or "You can stop when" not in r[0][1]:
        fails.append("reintroduced heading not caught: %r" % (r,))

    # 3. The relabelled heading dropped: caught.
    r = _run(GOOD_JS.replace("The whole zone is done when", "Something else"))
    if not r or "relabels" not in r[0][1]:
        fails.append("dropping the relabelled heading not caught: %r" % (r,))

    # 4. The clarifying note dropped: caught.
    r = _run(GOOD_JS.replace("you are not aiming for all of it right now",
                             "keep going"))
    if not r or "which pass of 6" not in r[0][1]:
        fails.append("dropping the clarifying note not caught: %r" % (r,))

    # 5. quest.js missing entirely: gate returns quietly rather than crashing.
    tmp = tempfile.mkdtemp()
    try:
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_quest_card_victory_honesty()
            if preflight.FAIL:
                fails.append("missing file wrongly flagged: %r" % (preflight.FAIL,))
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)

    # 6. The real, committed file: clean.
    real_js = os.path.join(ROOT, "site", "assets", "js", "quest.js")
    if not os.path.exists(real_js):
        print("  (skipped: real quest.js not found)")
    else:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_quest_card_victory_honesty()
        if preflight.FAIL:
            fails.append("real committed file failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_quest_card_victory_honesty, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
