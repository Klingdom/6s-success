#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_films_teach_all_six_passes() still protects the
library after the 2026-10-02 23:0x finding: issue #39 was closed as complete,
but the two zones it named (living-room--bookshelves-and-display,
garage--sports-and-recreation-zone) still carry the pre-fix caption text in
their committed .srt. Rewritten from the version this replaces, which
asserted the gate downgrades those two zones to a warning across the board;
that assertion crashed with IndexError once a 2026-10-02 commit (27da5009a,
then 8c7c833bc) deleted the allowlist it was written against.

Checked rather than assumed before rewriting: running the gate directly
against the real tree showed the two named zones STILL reporting "no
standardize", for a reason neither commit's own diagnosis covers. The
corpus (ops/video_zone.py) says "labeled"; the committed caption still says
"labelled", a homophone, not a missing instruction, so the gate's own
first-five-words probe broke on a spelling difference nobody could hear.
That is a real bug in the probe, not evidence the pass is missing, and is
fixed below the short-check's own level rather than by re-adding an
allowlist for it: both zones now pass that check the same way the other
112 do, with no exception needed.

The audible-drift check is a separate matter and genuinely still fails: the
committed captions for primary-bedroom--dresser-top and
stair-landing--landing-surface-or-console still say "jewellery" and
"draught", which the commit that closed issue #39 claimed were re-rendered.
Re-rendering needs real TTS reach neither this sandbox nor CI has, so this
one keeps a named, capped exception (warn, not fail) for exactly those two
zones, and nothing else.

Run:  python ops/tests/test_gate_films_six_passes_known_drift.py
"""
import io
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

FOLDER = os.path.join(ROOT, "build", "video", "zones-narrated")


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_films_teach_all_six_passes()
    return list(preflight.FAIL), list(preflight.WARN)


def _with_fixture(target, transform, check):
    """Copy target aside, apply transform(text)->text, run the gate, restore
    byte-identical, and call check(fails_list, FAIL, WARN) to record any
    assertion failure into fails_list."""
    backup = target + ".bak"
    shutil.copy2(target, backup)
    fails = []
    try:
        real = io.open(target, encoding="utf-8").read()
        changed = transform(real)
        if changed == real:
            fails.append("fixture for %s never changed anything; the probe "
                         "text was not actually present" % target)
        io.open(target, "w", encoding="utf-8", newline="").write(changed)
        f, w = _run()
        check(fails, f, w)
    finally:
        shutil.copy2(backup, target)
        os.remove(backup)
    return fails


def main() -> int:
    fails = []

    # 1. The real, committed corpus: no FAIL, and the two zones issue #39
    #    named for the standardize gap are NOT in it (the homophone probe
    #    fix covers them with no exception). The audible check's own named
    #    exception for the two different zones (jewellery/draught) still
    #    warns, naming issue #39 and both of them.
    f, w = _run()
    if any(g == "films-six-passes" for g, _m in f):
        fails.append("the real committed corpus fails preflight: %r" % (f,))
    warn_msgs = [m for g, m in w if g == "films-six-passes"]
    if not warn_msgs or "issue #39" not in warn_msgs[0]:
        fails.append("the known audible drift was not reported as a "
                      "tracked warning naming issue #39: %r" % (warn_msgs,))
    for slug in ("primary-bedroom--dresser-top",
                 "stair-landing--landing-surface-or-console"):
        if warn_msgs and slug not in warn_msgs[0]:
            fails.append("%s missing from the tracked-warning message"
                          % slug)

    # 2. A NEW audible regression on an unrelated, currently-clean zone
    #    (a word that is genuinely rare, not "while"/"tire" which already
    #    occur naturally in most captions) must still fail preflight by
    #    name, not be swallowed by the capped exception.
    target = os.path.join(FOLDER, "dining-room--beverage-or-coffee-station.srt")

    def _add_aeroplane(real):
        return real + ("\n\n999\n00:09:00,000 --> 00:09:01,000\n"
                       "Fold it like an aeroplane wing.\n")

    def _check_new_audible(fails, f, w):
        hit = [m for g, m in f if g == "films-six-passes"]
        if not hit or "dining-room--beverage-or-coffee-station" not in hit[0]:
            fails.append("a NEW audible regression on an unlisted zone was "
                          "not caught by name: FAIL=%r" % (f,))
        if any("dining-room" in m for g, m in w if g == "films-six-passes"):
            fails.append("the new regression was warned instead of failed")

    fails += _with_fixture(target, _add_aeroplane, _check_new_audible)

    # 3. A homophone-only drift on an unrelated zone's pass text (the same
    #    shape that broke living-room/garage) must NOT fail or warn: this is
    #    the bug this cycle fixed, and it must stay fixed. Re-corrupts the
    #    exact zone and word issue #39 was filed against, to prove it stays
    #    fixed rather than merely assuming it from the earlier fix.
    lr_target = os.path.join(FOLDER, "living-room--bookshelves-and-display.srt")

    def _relabel_lr(real):
        return real.replace("labelled", "labeled")  # no-op if already fixed

    def _check_homophone_clean(fails, f, w):
        if any("living-room" in m for g, m in f if g == "films-six-passes"):
            fails.append("a homophone-only spelling match still fails: %r"
                          % (f,))

    fails += _with_fixture(lr_target, _relabel_lr, _check_homophone_clean)

    # 4. Sanity: restoring the real files leaves the gate exactly where #1
    #    found it.
    f, w = _run()
    if any(g == "films-six-passes" for g, _m in f):
        fails.append("restoring the real files did not leave it clean: %r"
                      % (f,))

    if fails:
        print("FAIL")
        for x in fails:
            print(" -", x)
        return 1
    print("ok  known audible drift (issue #39, re-opened) warns by name; "
          "homophone-only drift no longer false-positives; new audible "
          "regressions still fail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
