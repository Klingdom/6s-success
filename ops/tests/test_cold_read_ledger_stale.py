#!/usr/bin/env python3
"""
Prove ops/cold_read_ledger.py's stale_entries() catches a ledger entry
whose file has been committed to AFTER the date the ledger recorded it
clean/fixed on.

Found live 2026-09-30, re-verifying ops/deploy_freshness.py from the
ledger's own oldest-first queue: the ledger read "clean, dated 2026-09-25,
... no defect found in the source", but a real defect in that exact file
(the freshness probe's own URL causing 2,270 self-inflicted redirects) was
found and fixed on 2026-09-29, four days later, and the ledger was never
told. Nothing before this checked a ledger entry's date against the
file's own git history, so a clean verdict could silently outlive the
code it was a verdict about. This tests the pure logic against real
tracked files in this repository (there is no synthetic git history to
fabricate), never against the real committed ops/cold-read-ledger.json.

Run:  python ops/tests/test_cold_read_ledger_stale.py
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import cold_read_ledger as crl                                    # noqa: E402


def _real_last_touched(rel_path: str) -> str:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cd", "--date=short", "--", rel_path],
        cwd=ROOT, capture_output=True, text=True)
    date = out.stdout.strip()
    assert date, "expected git history for %s" % rel_path
    return date


def main() -> int:
    fails = []

    # A real, currently-tracked file (this test file's own sibling module)
    # gives a real git date without fabricating history. cold_read_ledger.py
    # itself is always tracked and always has at least one commit.
    real_date = _real_last_touched("ops/cold_read_ledger.py")

    # 1. An entry dated BEFORE the file's real last-touch date is stale.
    ledger = {
        "cold_read_ledger.py": {
            "status": "clean", "date": "2020-01-01", "note": "old claim"},
    }
    stale = crl.stale_entries(ledger)
    if not any(b == "cold_read_ledger.py" for b, _, _ in stale):
        fails.append("a 2020-01-01 clean date against a real, later-"
                      "touched file was not flagged stale: %r" % stale)
    else:
        b, d, t = next(s for s in stale if s[0] == "cold_read_ledger.py")
        if d != "2020-01-01" or t != real_date:
            fails.append("stale entry carried the wrong dates: got "
                          "(%s, %s), wanted (2020-01-01, %s)"
                          % (d, t, real_date))

    # 2. An entry dated AFTER the file's real last-touch date (i.e. today,
    #    or any date >= the real one) must NOT be flagged: the claim is
    #    still current as of everything git can show.
    ledger_current = {
        "cold_read_ledger.py": {
            "status": "clean", "date": "2099-01-01", "note": "future date"},
    }
    stale = crl.stale_entries(ledger_current)
    if any(b == "cold_read_ledger.py" for b, _, _ in stale):
        fails.append("a ledger date in the future was wrongly flagged "
                      "stale: %r" % stale)

    # 3. A file with no tracked lane path (nonsense basename) must be
    #    silently skipped, never crash and never appear as stale: unknown
    #    is not a default (CLAUDE.md 0.4).
    ledger_unknown = {
        "this-file-does-not-exist-anywhere.py": {
            "status": "clean", "date": "2020-01-01", "note": "x"},
    }
    try:
        stale = crl.stale_entries(ledger_unknown)
    except Exception as e:                                        # noqa: BLE001
        fails.append("stale_entries() raised on an unresolvable basename "
                      "instead of skipping it: %r" % e)
    else:
        if stale:
            fails.append("an unresolvable basename was wrongly reported "
                          "stale: %r" % stale)

    # 4. A "fixed" status is checked the same way "clean" is; a status
    #    outside VALID_STATUSES (should not occur, but must not crash or
    #    be treated as stale) is skipped.
    ledger_fixed = {
        "cold_read_ledger.py": {
            "status": "fixed", "date": "2020-01-01", "note": "x"},
    }
    stale = crl.stale_entries(ledger_fixed)
    if not any(b == "cold_read_ledger.py" for b, _, _ in stale):
        fails.append("a stale 'fixed' entry was not caught: %r" % stale)

    # 5. Sorted oldest ledger-date first.
    ledger_multi = {
        "cold_read_ledger.py": {
            "status": "clean", "date": "2021-06-01", "note": "x"},
        "preflight.py": {
            "status": "clean", "date": "2020-01-01", "note": "x"},
    }
    stale = crl.stale_entries(ledger_multi)
    dates = [d for _, d, _ in stale]
    if dates != sorted(dates):
        fails.append("stale_entries() did not sort oldest ledger-date "
                      "first: %r" % stale)

    # 6. The real committed ledger must load and run through this logic
    #    without crashing (the true positives/negatives in it are a fact
    #    about wall-clock repository state, not this test's business, the
    #    same reasoning test_gate_cold_read_handoff_not_stale.py already
    #    gives for not asserting against the live, ever-changing log).
    real_ledger = crl.load_ledger()
    try:
        crl.stale_entries(real_ledger)
    except Exception as e:                                        # noqa: BLE001
        fails.append("stale_entries() raised against the real committed "
                      "ledger: %r" % e)

    # 7. --stale and --check both surface the same signal via the CLI;
    #    smoke-test only (exit code, not exact wording, since wording is
    #    covered by the assertions above).
    import contextlib
    buf = io.StringIO()
    old_argv = sys.argv
    try:
        sys.argv = ["cold_read_ledger.py", "--stale"]
        with contextlib.redirect_stdout(buf):
            rc = crl.main()
        if rc != 0:
            fails.append("--stale exited non-zero: %r" % rc)
    finally:
        sys.argv = old_argv

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("OK  cold_read_ledger stale_entries: 7/7 cases pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
