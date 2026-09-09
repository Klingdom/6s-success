#!/usr/bin/env python3
"""
Prove gate_affiliate_trigger reports "could not evaluate" instead of going
silent, the exact failure this repository keeps re-finding under a new name.

check_affiliate_trigger.verdict() returns three states: True (T2 fired,
warn), False (measured, below threshold, silent on purpose so a "0 of 60"
line does not get skipped for a year), and None (the database could not be
read at all, distinct from a measured zero). The gate as first written only
checked `if fired:`, and None is falsy in Python, so the unreadable case
printed nothing, every single run in every credential-less sandbox since the
gate shipped, which is every sandbox this operator has run in. CLAUDE.md 0.4
calls this exact shape out by name: "unknown is not unused, and unchecked is
not passing." The gate meant to guard the affiliate decision against being
forgotten was itself silently forgetting to say it could not check.

Run:  python ops/tests/test_gate_affiliate_trigger.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402
import check_affiliate_trigger as T                             # noqa: E402


def with_reading(result):
    real = T.reading
    T.reading = lambda: result
    P.WARN.clear()
    try:
        P.gate_affiliate_trigger()
    finally:
        T.reading = real
    return list(P.WARN)


def main() -> int:
    fails = []

    # Case 1: T2 has genuinely fired. Must warn, and name it.
    w = with_reading({"ok": True, "clicks": 60, "people": 12, "why": ""})
    if not any(g == "affiliate-trigger" and "T2 HAS FIRED" in m for g, m in w):
        fails.append(f"a fired trigger must warn by name, got {w}")

    # Case 2: measured and genuinely below threshold. Silent on purpose,
    # per the gate's own docstring, so the warning that matters is not
    # buried under a "0 of 60" line every run for a year.
    w = with_reading({"ok": True, "clicks": 3, "people": 2, "why": ""})
    if w:
        fails.append(f"a measured below-threshold reading must stay silent, got {w}")

    # Case 3: the real shape in every credential-less sandbox today. The
    # database could not be reached, so fired is None, not False. This must
    # warn UNCHECKED, never sit silent the way a measured zero does.
    w = with_reading({"ok": False, "clicks": 0, "people": 0,
                       "why": "no ssh key at /root/.ssh/6s_deploy"})
    if not any(g == "affiliate-trigger" and "NOT EVALUATED" in m for g, m in w):
        fails.append(f"an unreadable database must warn NOT EVALUATED, "
                     f"not sit silent like a measured zero, got {w}")

    # Case 4: the module itself is missing or raises before returning a
    # result at all. The existing except clause must still catch this.
    real_reading = T.reading
    def boom():
        raise RuntimeError("no analytics module")
    T.reading = boom
    P.WARN.clear()
    try:
        P.gate_affiliate_trigger()
        w = list(P.WARN)
    finally:
        T.reading = real_reading
    if not any(g == "affiliate-trigger" and "could not evaluate" in m for g, m in w):
        fails.append(f"a raised exception must warn UNCHECKED, got {w}")

    if fails:
        print(f"FAIL: {len(fails)} of 4 cases")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 4 of 4 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
