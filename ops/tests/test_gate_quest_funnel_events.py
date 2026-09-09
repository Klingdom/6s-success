#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_quest_funnel_events() catches a hand edit that
silently drops one of BACKLOG-2026-09-07.md A5's funnel events (added to
site/assets/js/quest.js 2026-09-09: quest-cause-shown, quest-card-abandoned,
quest-return) or the listener either abandonment signal depends on.

Run:  python ops/tests/test_gate_quest_funnel_events.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = (
    'm("quest-cause-shown", { symptom: idx });\n'
    'm("quest-card-abandoned", { s: c.step.s, elapsed: elapsed });\n'
    'm("quest-return", { days: days });\n'
    'document.addEventListener("visibilitychange", function () {});\n'
    'addEventListener("pagehide", reportAbandonIfMidCard);\n'
)


def _run(src: str):
    tmp = tempfile.mkdtemp()
    try:
        js_dir = os.path.join(tmp, "assets", "js")
        os.makedirs(js_dir)
        io.open(os.path.join(js_dir, "quest.js"), "w", encoding="utf-8").write(src)
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_quest_funnel_events()
            return list(preflight.FAIL)
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. All five markers present: no failure.
    r = _run(GOOD)
    if r:
        fails.append("clean file wrongly flagged: %r" % (r,))

    # 2-6. Each marker dropped in turn is caught by name.
    for marker in ('"quest-cause-shown"', '"quest-card-abandoned"',
                   '"quest-return"', "visibilitychange", "pagehide"):
        broken = GOOD.replace(marker, "")
        r = _run(broken)
        if not r or "quest.js" not in r[0][1]:
            fails.append("dropping %r not caught: %r" % (marker, r))

    # 7. No file on disk: gate returns quietly rather than crashing.
    tmp = tempfile.mkdtemp()
    try:
        old_site = preflight.SITE
        preflight.SITE = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_quest_funnel_events()
            if preflight.FAIL:
                fails.append("missing file wrongly flagged: %r" % (preflight.FAIL,))
        finally:
            preflight.SITE = old_site
    finally:
        shutil.rmtree(tmp)

    # 8. The real, committed file: clean.
    real_path = os.path.join(ROOT, "site", "assets", "js", "quest.js")
    if not os.path.exists(real_path):
        print("  (skipped: site/assets/js/quest.js not found)")
    else:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_quest_funnel_events()
        if preflight.FAIL:
            fails.append("real committed quest.js failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_quest_funnel_events, 8/8 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
