#!/usr/bin/env python3
"""
Prove the affiliate reports carry a date that moves only when their inputs do.

WHY THIS EXISTS
---------------
These three files are regenerated and diffed by preflight's
gate_generator_ownership. They used to be stamped with
datetime.date.today(), which meant the committed copy disagreed with a fresh
run from the first second after midnight UTC, every single day, whether or not
anything about the affiliate programme had changed.

That is not hypothetical. The 2026-09-25 00:08 UTC build failed with

    generator-ownership: could not run: 2 file(s) in the working tree differ

naming AFFILIATE_COMPLIANCE_MATRIX.md, and the image for that commit was never
published. The gate was right and the generator was wrong: a date that moves
when nothing moved is noise with a timestamp.

The stamp is now the newest commit date of the two files that decide the
content, the same approach ops/build_seo.py takes to page lastmod.

Run:  python ops/tests/test_affiliate_report_stamp_stable.py
"""
import datetime
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import affiliate_report as A                                    # noqa: E402

REPORTS = ["AFFILIATE_COMPLIANCE_MATRIX.md", "AFFILIATE_INPUT_EXCEPTIONS.md"]


def case_stamp_is_not_todays_date_unless_inputs_changed_today():
    stamp = A.inputs_date()
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", stamp), stamp
    newest = ""
    for p in (A.ACCOUNTS, A.CATALOGUE):
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", p],
                             cwd=ROOT, capture_output=True, text=True,
                             timeout=30)
        d = (out.stdout or "").strip()
        if d > newest:
            newest = d
    if newest:
        assert stamp == newest, (
            "stamp %r does not match the newest input commit date %r"
            % (stamp, newest))


def case_stamp_does_not_follow_the_clock():
    """The defect itself: freeze 'today' far in the future, stamp must hold."""
    real = datetime.date

    class Frozen(real):
        @classmethod
        def today(cls):
            return real(2099, 12, 31)

    before = A.inputs_date()
    A.datetime.date = Frozen
    try:
        after = A.inputs_date()
    finally:
        A.datetime.date = real
    assert after == before, (
        "the stamp moved from %r to %r when only the clock changed; this is "
        "the failure that broke CI once a day" % (before, after))
    assert "2099" not in after, after


def case_refuses_to_guess_when_shallow():
    """The 2026-09-30 regression: a shallow clone's git log returns the
    boundary commit's date, not an error, for any file untouched since. That
    looks exactly like a real answer, so inputs_date() must refuse before
    ever calling git log, not try to catch a bad result after the fact."""
    real_is_shallow = A._is_shallow_clone
    A._is_shallow_clone = lambda: True
    try:
        try:
            A.inputs_date()
        except RuntimeError as e:
            assert "shallow" in str(e).lower(), e
        else:
            raise AssertionError(
                "inputs_date() returned a date while shallow instead of "
                "refusing; this is the exact silent-wrong-stamp regression")
    finally:
        A._is_shallow_clone = real_is_shallow


def case_running_twice_writes_identical_bytes():
    """What gate_generator_ownership actually does."""
    A.main()
    first = {}
    for name in REPORTS:
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            first[name] = io.open(p, "rb").read()
    assert first, "the generator wrote none of its reports"
    A.main()
    for name, blob in first.items():
        again = io.open(os.path.join(ROOT, name), "rb").read()
        assert again == blob, "%s differs between two consecutive runs" % name


def case_the_committed_reports_match_a_fresh_run():
    """The real tree, the real check CI performs.

    Compared with `git diff`, not `git status --porcelain`, and the difference
    is not cosmetic. `git status` consults the index stat cache and calls a
    file modified the moment its mtime moves, which a generator rewriting
    byte-identical content does on every run. Worse here: this workstation has
    core.autocrlf=true, so a report written with LF and committed through
    .gitattributes normalisation is reported modified forever, on this platform
    only, while CI stays clean.

    That made this case fail every local run for a reason that says nothing
    about the claim it exists to check, which is the worst shape a check can
    take: one that cries wolf until somebody stops reading it.
    `ops/preflight.py`'s own `worktree_changes()` documents the identical
    finding and solved it the same way, so this now matches the tool it is
    guarding rather than guessing differently.

    `git diff` does a content comparison with the repository's own
    normalisation applied, which is exactly the question being asked: would
    gate_generator_ownership see drift. A real content change still fails.
    """
    A.main()

    def names(*args):
        out = subprocess.run(['git'] + list(args) + ['--'] + REPORTS,
                             cwd=ROOT, capture_output=True, text=True,
                             timeout=60).stdout
        return [x for x in (out or '').splitlines() if x.strip()]

    dirty = sorted(set(names('diff', '--name-only')
                       + names('diff', '--cached', '--name-only')))
    assert not dirty, (
        'a fresh run changes the committed reports, so gate_generator_'
        'ownership will refuse the next CI build: %s' % dirty)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
