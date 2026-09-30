#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_preflight_lock_timing_current() catches its own
module docstring citing a stale STALE_AFTER-derived timeout floor.

Found 2026-09-30: preflight.py's own docstring warned callers not to wrap
the command in an external timeout shorter than "about 1050 seconds" and
cited test_audit_catalog.py's file lock self-healing "after 900 seconds."
Both numbers were already wrong: STALE_AFTER in test_audit_catalog.py had
dropped from 900 to 300 on 2026-09-25, five days earlier, and nobody had
told this docstring. Nothing checked that citation against the real
constant it describes, the exact "corrected source, unrederived artifact"
defect class this repository keeps finding elsewhere. Fixed the same cycle
this test was written: the docstring now names the correctly-derived figure
(STALE_AFTER + 120), and this gate keeps it honest against the real
constant going forward.

Drives the pure logic function directly against fabricated STALE_AFTER
values first (no I/O, no dirtied checkout needed to prove a fail-then-pass),
then checks the real committed preflight.py docstring against the real
committed test_audit_catalog.py constant.

Run:  python ops/tests/test_gate_preflight_lock_timing_current.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))
sys.path.insert(0, os.path.join(ROOT, "ops", "tests"))

import preflight                                               # noqa: E402
import test_audit_catalog as TAC                               # noqa: E402


def main() -> int:
    fails = []
    check = preflight.check_preflight_lock_timing_current

    # 1. The real regression shape: docstring still names the old figures
    #    (900/1050) after STALE_AFTER has moved to 300 (needs "420s, the
    #    STALE_AFTER").
    stale_doc = ("Do not wrap this command in an external timeout shorter "
                 "than about 1050 seconds. ... self-heals after 900 "
                 "seconds ...")
    msg = check(stale_doc, 300)
    if not msg:
        fails.append("a docstring citing the old 900/1050 figures against "
                      "a STALE_AFTER of 300 was not flagged")
    elif "420s, the STALE_AFTER" not in msg or "300" not in msg:
        fails.append("failure message did not name both the expected "
                      "figure and the real STALE_AFTER: %r" % msg)

    # 2. Docstring matches reality: no failure.
    current_doc = ("Do not wrap this command in an external timeout "
                   "shorter than about 480 seconds (test_audit_catalog.py's "
                   "own worst case: 420s, the STALE_AFTER age-based "
                   "fallback, plus ~60s of its own real audit_catalog.py "
                   "runs).")
    msg = check(current_doc, 300)
    if msg:
        fails.append("genuine agreement with reality wrongly flagged: %r"
                     % msg)

    # 3. STALE_AFTER moves again (e.g. to 250): a docstring that still says
    #    420s must now be flagged (proves this is not hardcoded to 420).
    msg = check(current_doc, 250)
    if not msg:
        fails.append("a docstring stuck on 420s after STALE_AFTER moved to "
                      "250 (needing 370s) was not flagged")

    # 4. Empty/missing docstring: flagged, not silently skipped.
    msg = check("", 300)
    if not msg:
        fails.append("an empty docstring was not flagged")

    # 5. The real, committed files: clean, now that both sides agree.
    real_msg = check(preflight.__doc__ or "", TAC.STALE_AFTER)
    if real_msg:
        fails.append("the real committed preflight.py docstring and "
                     "test_audit_catalog.py's real STALE_AFTER disagree: %s"
                     % real_msg)

    # 6. End to end through the real gate against the real files.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_preflight_lock_timing_current()
    if preflight.FAIL:
        fails.append("gate_preflight_lock_timing_current FAILed against the "
                     "real committed files: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_preflight_lock_timing_current, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
