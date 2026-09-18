#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_hero_fallback_current() catches
ops/hero-fallback.json drifting from the real, committed zone pages.

Found 2026-09-18, cold-reading ops/refresh_hero_fallback.py: it exists
because on 2026-09-17 five newly approved zone heroes went live on their
pages while four stayed missing from this file, which matters twice over.
wire_zone_heroes.fallback_wire() restores figures FROM this file in every
environment without build/heroes/zones/ (every CI checkout, gitignored),
and build_quest.py treats an entry's absence here as "no picture", so the
Home Quest app kept showing none for a zone whose photo was already live on
its own web page. refresh_hero_fallback.py fixes drift once run, but
nothing re-asserted it had been, and its filename does not match the
build_*.py glob gate_every_generator_has_a_protection_plan() checks, so it
had no gate at all. This one closes that gap directly.

Run:  python ops/tests/test_gate_hero_fallback_current.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def main() -> int:
    fails = []

    fresh = {
        "a.html": {"figure_html": "<figure>A</figure>", "stem": "a",
                    "og_image": "https://6s-success.com/assets/zones/a-lg.avif"},
        "b.html": {"figure_html": "<figure>B</figure>", "stem": "b"},
    }

    # 1. Identical: no problems.
    r = preflight.check_hero_fallback_current(fresh, dict(fresh))
    if r:
        fails.append("identical record wrongly flagged: %r" % (r,))

    # 2. A page now wired with a hero the committed record never got: the
    #    exact 2026-09-17 regression shape (new approval, record not
    #    refreshed).
    committed_missing_b = {"a.html": fresh["a.html"]}
    r = preflight.check_hero_fallback_current(fresh, committed_missing_b)
    if not r or "b.html" not in r[0]:
        fails.append("a newly wired page missing from the record was not "
                      "caught by name: %r" % (r,))

    # 3. A page in the committed record no longer wired on the real page
    #    (e.g. a hero withdrawn): flagged as dropped, not silently kept.
    committed_extra = dict(fresh)
    committed_extra["c.html"] = {"figure_html": "<figure>C</figure>", "stem": "c"}
    r = preflight.check_hero_fallback_current(fresh, committed_extra)
    if not r or not any("c.html" in p for p in r):
        fails.append("a stale entry no longer wired was not caught by "
                      "name: %r" % (r,))

    # 4. A page whose figure or preview URL moved: flagged as changed, not
    #    treated as identical because the key still exists.
    committed_stale_stem = {
        "a.html": {"figure_html": "<figure>A</figure>", "stem": "old-stem",
                    "og_image": "https://6s-success.com/assets/zones/a-lg.avif"},
        "b.html": fresh["b.html"],
    }
    r = preflight.check_hero_fallback_current(fresh, committed_stale_stem)
    if not r or not any("a.html" in p for p in r):
        fails.append("a stale figure/preview was not caught by name: %r"
                      % (r,))

    # 5. Missing file entirely: fail(), not warn(), since the file is
    #    committed and its absence is not an environment limitation. The
    #    gate reloads the module internally, so a monkeypatched OUT would
    #    not survive; move the real committed file aside instead.
    real_path = os.path.join(ROOT, "ops", "hero-fallback.json")
    moved_aside = real_path + ".test-moved-aside"
    os.rename(real_path, moved_aside)
    try:
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_hero_fallback_current()
        if not preflight.FAIL or "does not exist" not in preflight.FAIL[0][1]:
            fails.append("a missing hero-fallback.json was not caught: %r"
                          % (preflight.FAIL,))
    finally:
        os.rename(moved_aside, real_path)

    # 6. The real, committed file against the real, committed zone pages:
    #    clean today. Proves the gate as actually wired, not just the pure
    #    logic above.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_hero_fallback_current()
    if preflight.FAIL:
        fails.append("the real committed hero-fallback.json failed: %r"
                     % (preflight.FAIL,))

    # 7. The real gate genuinely catches drift, not just the pure function:
    #    plant the exact 2026-09-17 regression shape in the real committed
    #    file, confirm the gate fails by name, then restore it byte for
    #    byte so this test leaves no trace.
    real_path = os.path.join(ROOT, "ops", "hero-fallback.json")
    original = io.open(real_path, encoding="utf-8").read()
    try:
        data = json.loads(original)
        keys = list(data.keys())
        dropped_key = keys[0]
        del data[dropped_key]
        io.open(real_path, "w", encoding="utf-8").write(json.dumps(data, indent=1))

        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_hero_fallback_current()
        if not preflight.FAIL or dropped_key not in preflight.FAIL[0][1]:
            fails.append("planting a real drop in the live file was not "
                          "caught by name: %r" % (preflight.FAIL,))
    finally:
        io.open(real_path, "w", encoding="utf-8").write(original)

    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_hero_fallback_current()
    if preflight.FAIL:
        fails.append("restoring the real file did not leave it clean: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_hero_fallback_current, 7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
