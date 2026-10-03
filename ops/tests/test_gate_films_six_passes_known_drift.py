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

ISSUE #39 IS NOW ACTUALLY CLOSED, 2026-10-03, and this file was rewritten
again to say so. The audible half used to be a named, capped exception: the
committed captions for primary-bedroom--dresser-top and
stair-landing--landing-surface-or-console still said "jewellery" and "draught",
where the corpus said jewelry and draft, and re-rendering them needed real TTS
reach neither this sandbox nor CI had. All four files (both orientations of
both zones) have since been re-rendered and committed in 71eab2f44, and the
gate now returns no FAIL and no warning against the real tree. Case 1 below
asserts the clean result AND greps the whole caption library for both words,
so "clean" cannot mean "the gate stopped looking".

The homophone case moved from a planted fixture to the real tree for a reason
worth naming: its transform replaced "labelled" with "labeled" in one file, and
the moment that file was re-rendered the transform became a no-op and the case
proved nothing while still passing. 98 committed captions genuinely carry the
homophone today, so the real tree is the better fixture, and the case reports
NOT VERIFIED rather than passing if that ever stops being true.

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

    # 1. The real, committed corpus is CLEAN: no FAIL and no tracked warning.
    #
    #    This case used to assert the opposite, that the two zones issue #39
    #    named (primary-bedroom--dresser-top, stair-landing--landing-surface-
    #    or-console) still warned because their committed captions said
    #    'jewellery' and 'draught' where the corpus said jewelry and draft.
    #    Re-rendering them needed real TTS reach, which neither this sandbox
    #    nor CI had, so the drift was carried as a named, capped exception.
    #
    #    It is now actually fixed. All four re-rendered .srt files (both
    #    orientations of both zones) were committed in 71eab2f44 and the
    #    audible words are gone; the gate returns no FAIL and no warning for
    #    films-six-passes against the real tree. Checked before rewriting this,
    #    not assumed from the commit subject.
    f, w = _run()
    if any(g == 'films-six-passes' for g, _m in f):
        fails.append('the real committed corpus fails preflight: %r' % (f,))
    warn_msgs = [m for g, m in w if g == 'films-six-passes']
    if warn_msgs:
        fails.append('the issue #39 drift was re-rendered and committed, so nothing should warn here any more. Still warning: %r' % (warn_msgs,))
    for word in ('jewellery', 'draught'):
        hits = [n for n in os.listdir(FOLDER)
                if n.endswith('.srt')
                and word in io.open(os.path.join(FOLDER, n),
                                    encoding='utf-8').read()]
        if hits:
            fails.append('%r is still in %d committed caption(s), so the clean result above is the gate missing it rather than the drift being fixed: %r' % (word, len(hits), hits[:3]))

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

    # 3. A homophone-only difference between a committed caption and the
    #    corpus must NOT fail or warn, because nobody can hear it. This is
    #    the probe bug that made issue #39 look like a missing instruction
    #    when it was a spelling.
    #
    #    Checked against the real tree rather than a planted fixture, because
    #    the tree still contains the case: the dialect sweep moved the corpus
    #    to 'labeled' and 98 committed captions still say 'labelled'. If that
    #    ever stops being true this case says so instead of passing vacuously,
    #    which is what the old fixture version did the moment the file it
    #    corrupted was re-rendered: its transform became a no-op and it
    #    proved nothing.
    homophone = [n for n in sorted(os.listdir(FOLDER))
                 if n.endswith('.srt')
                 and 'labelled' in io.open(os.path.join(FOLDER, n),
                                           encoding='utf-8').read()]
    if not homophone:
        fails.append("NOT VERIFIED: no committed caption carries 'labelled' "
                     'any more, so this case exercised nothing. Re-point it at '
                     'a homophone that is actually present, or delete it.')
    else:
        f, w = _run()
        named = [m for g, m in list(f) + list(w) if g == 'films-six-passes'
                 and any(n[:-4] in m for n in homophone)]
        if named:
            fails.append('a homophone-only spelling difference is being '
                         'reported across %d caption(s): %r'
                         % (len(homophone), named[:2]))

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
    print("ok  issue #39 is genuinely closed (no jewellery/draught left in any "
          "committed caption, gate clean); homophone-only drift still does not "
          "false-positive across 98 real captions; a new audible regression "
          "on an unlisted zone still fails by name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
