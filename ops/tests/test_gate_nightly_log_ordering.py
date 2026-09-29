#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_nightly_log_ordering() catches an entry dated
the file's own most recent date landing after the entry sequence has already
moved on to an older date, the exact shape a cycle produces when it reads
STEP 1's "read the last four entries" as "the physical end of the file"
(a natural reading, and the one a plain `tail` gives) and appends its own
entry there instead of prepending it to the top.

Found first 2026-09-05 (ninth cycle of the day, the gate's own docstring),
and again 2026-09-29 (a PM check-in's own entry landed after 42,000+ lines
of 2026-09-04 history), the second occurrence with no test proving the
gate itself, unlike its sibling gate_nightly_log_no_duplicate_entries.

Run:  python ops/tests/test_gate_nightly_log_ordering.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

NEWEST_A = "## 2026-09-29, scheduled operator cycle (a real fix)\n\n**Did:** fixed a real thing.\n\nPushed to main.\n"
NEWEST_B = "## 2026-09-29, PM check-in (30-minute triage)\n\n**Did:** confirmed nothing new.\n\nPushed to main.\n"
OLDER_A = "## 2026-09-04, cycle (seventh today)\n\n**Did:** older work.\n\nPushed to main.\n"
OLDER_B = "## 2026-09-04, cycle (sixth today)\n\n**Did:** older work.\n\nPushed to main.\n"


def _run(entries):
    tmp = tempfile.mkdtemp()
    ops_dir = os.path.join(tmp, "ops")
    os.makedirs(ops_dir, exist_ok=True)
    io.open(os.path.join(ops_dir, "NIGHTLY-LOG.md"), "w",
            encoding="utf-8").write("# Nightly log\n\n" + "\n".join(entries))
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_nightly_log_ordering()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. Correctly newest-first, no legacy older section: clean.
    r = _run([NEWEST_B, NEWEST_A, OLDER_A, OLDER_B])
    if r:
        fails.append("correct newest-first ordering wrongly flagged: %r" % (r,))

    # 2. The exact real-world regression: a newest-dated entry appended
    #    after the sequence has already moved on to an older date.
    r = _run([NEWEST_A, OLDER_A, OLDER_B, NEWEST_B])
    if not r or "appended" not in r[0][1]:
        fails.append("misplaced newest-date entry not caught by name: %r" % (r,))

    # 3. Only one date present anywhere: nothing to compare, must not
    #    crash or fail.
    r = _run([NEWEST_A, NEWEST_B])
    if r:
        fails.append("a single date wrongly flagged: %r" % (r,))

    # 4. Legacy oldest-first section alone (many same-day entries, no
    #    single newest date reappearing later): must not be flagged, since
    #    rewriting historical order is not this gate's job.
    r = _run([OLDER_B, OLDER_A])
    if r:
        fails.append("legacy oldest-first section wrongly flagged: %r" % (r,))

    # 5. The real, committed file: clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_nightly_log_ordering()
    if preflight.FAIL:
        fails.append("the real committed ops/NIGHTLY-LOG.md failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_nightly_log_ordering, 5/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
