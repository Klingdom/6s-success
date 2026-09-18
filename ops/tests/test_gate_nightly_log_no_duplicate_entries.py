#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_nightly_log_no_duplicate_entries() catches a
marker-free git merge leaving two byte-identical copies of the same
ops/NIGHTLY-LOG.md entry, the exact shape that happened three separate
times on 2026-09-18 (concurrent sessions each moving or adding the same
entry against slightly different surrounding context, so git's own
three-way merge saw no conflicting hunk and produced no `<<<<<<<` marker).
Each time, the only thing that caught it was a cycle manually grepping
for the entry's own title after the merge. This gate replaces that manual
grep with a standing check, per CLAUDE.md step 10b: the same defect class
recurring three times in one day gets a gate, not a fourth restatement.

Run:  python ops/tests/test_gate_nightly_log_no_duplicate_entries.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

ENTRY_A = (
    "## 2026-09-18, scheduled operator cycle (a real fix)\n\n"
    "**Did:** fixed a real thing. Verified end to end.\n\n"
    "Pushed to main.\n"
)

ENTRY_B = (
    "## 2026-09-18, PM check-in (30-minute triage, previous work finished)\n\n"
    "**Did:** confirmed nothing new. Preflight clean.\n\n"
    "Pushed to main.\n"
)

# A different date, different body, but the SAME heading text as ENTRY_B's
# generic "PM check-in (30-minute triage...)" title. This is legitimate:
# the file reuses this exact heading phrasing across many real, distinct
# cycles, and must never be flagged on heading alone.
ENTRY_B_DIFFERENT_DAY = (
    "## 2026-09-17, PM check-in (30-minute triage, previous work finished)\n\n"
    "**Did:** a completely different cycle, a different finding entirely.\n\n"
    "Pushed to main.\n"
)


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
        preflight.gate_nightly_log_no_duplicate_entries()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. Two distinct entries, no duplication: clean.
    r = _run([ENTRY_A, ENTRY_B])
    if r:
        fails.append("two distinct entries wrongly flagged: %r" % (r,))

    # 2. The exact real-world regression: the same entry appears twice,
    #    byte-identical, with something else between them (as a genuine
    #    merge would leave it), not adjacent.
    r = _run([ENTRY_A, ENTRY_B, ENTRY_A])
    if not r or "byte-identical" not in r[0][1]:
        fails.append("duplicated entry not caught by name: %r" % (r,))

    # 3. Adjacent duplication (the simplest shape a merge can produce).
    r = _run([ENTRY_B, ENTRY_B])
    if not r or "byte-identical" not in r[0][1]:
        fails.append("adjacent duplicated entry not caught: %r" % (r,))

    # 4. Same heading text, different day and different body: must NOT be
    #    flagged. This file legitimately reuses this exact heading many
    #    times across real, distinct cycles.
    r = _run([ENTRY_B, ENTRY_B_DIFFERENT_DAY])
    if r:
        fails.append("same heading, different real entries, wrongly "
                      "flagged: %r" % (r,))

    # 5. Fewer than two headings: nothing to compare, must not crash or
    #    fail.
    r = _run([ENTRY_A])
    if r:
        fails.append("a single entry wrongly flagged: %r" % (r,))

    # 6. The real, committed file: clean (the actual 2026-09-18 incident
    #    was already deduplicated by hand before this gate existed).
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_nightly_log_no_duplicate_entries()
    if preflight.FAIL:
        fails.append("the real committed ops/NIGHTLY-LOG.md failed: %r"
                     % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_nightly_log_no_duplicate_entries, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
