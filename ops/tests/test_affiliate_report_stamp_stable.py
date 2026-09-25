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
    """The real tree, the real check CI performs."""
    A.main()
    out = subprocess.run(["git", "status", "--porcelain"] + REPORTS,
                         cwd=ROOT, capture_output=True, text=True, timeout=60)
    dirty = [l for l in (out.stdout or "").splitlines() if l.strip()]
    assert not dirty, (
        "a fresh run changes the committed reports, so gate_generator_"
        "ownership will refuse the next CI build: %s" % dirty)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
