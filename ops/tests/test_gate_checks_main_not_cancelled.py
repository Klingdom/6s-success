#!/usr/bin/env python3
"""
Prove gate_checks_main_not_cancelled fires when main's own CI verification
can be cancelled by the next push.

Added 2026-09-17. checks.yml carried `cancel-in-progress: true` for every
ref. Measured from the Actions API that day: a successful Checks run takes
28 to 31 minutes, and 5 of the last 12 runs were cancelled, because
concurrent sessions push to main faster than that. The practical effect was
that main's verification usually never finished, so "CI is green" was a
statement about an older commit. Fixed by making cancellation conditional
on the ref; branches still supersede their stale runs.

Run:  python ops/tests/test_gate_checks_main_not_cancelled.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

GOOD = ("concurrency:\n  group: checks-${{ github.ref }}-"
        "${{ github.ref == 'refs/heads/main' && github.sha || 'branch' }}\n"
        "  cancel-in-progress: true\n")

PER_REF_EXPR = ("concurrency:\n  group: checks-${{ github.ref }}\n"
                "  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}\n")

PER_REF_TRUE = ("concurrency:\n  group: checks-${{ github.ref }}\n"
                "  cancel-in-progress: true\n")

SHA_ONLY = ("concurrency:\n  group: checks-${{ github.sha }}\n"
            "  cancel-in-progress: true\n")

CASES = [
    ("correct shape (group unique per commit on main)", GOOD, False),
    ("real checks.yml", None, False),
    ("the 2026-09-17 attempt: expression in cancel-in-progress",
     PER_REF_EXPR, True),
    ("one group per ref, cancel true", PER_REF_TRUE, True),
    ("declaration removed", "jobs:\n  checks:\n", True),
    ("group keeps the sha but drops main", SHA_ONLY, True),
]


def fired(text):
    calls = []
    real = P.fail
    P.fail = lambda *a, **k: calls.append(a)
    try:
        if text is None:
            P.gate_checks_main_not_cancelled()
        else:
            d = tempfile.mkdtemp()
            path = os.path.join(d, "checks.yml")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            P.gate_checks_main_not_cancelled(path)
    finally:
        P.fail = real
    return bool(calls)


def main():
    failures = []
    for name, text, should_fire in CASES:
        got = fired(text)
        if got != should_fire:
            failures.append("%s: expected fire=%s, got %s" % (name, should_fire, got))
    for f in failures:
        print("FAIL:", f)
    print("ok, %d cases" % len(CASES) if not failures else "%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
