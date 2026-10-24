#!/usr/bin/env python3
"""
Prove gate_living_docs_total_size_tripwire() can actually fail (warn) on
a real oversized living document and stays silent once it is under its
own tripwire, for more than one tracked file so the per-file limit table
itself is exercised rather than one hardcoded path. A gate that cannot
go red is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_living_docs_total_size_tripwire.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402


def _run_gate(tmp, files):
    for name, text in files.items():
        with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
            f.write(text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_living_docs_total_size_tripwire()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


def main() -> int:
    fails = []
    gate_name = "living-docs-total-size-tripwire"

    # 1. A tracked file well past its own limit must warn, naming that
    #    file, and must not FAIL (this is a cost, not a customer break).
    for name, limit in preflight.LIVING_DOC_SIZE_LIMITS.items():
        oversized = {name: "x" * (limit + 10_000)}
        with tempfile.TemporaryDirectory() as tmp:
            g_fails, g_warns = _run_gate(tmp, oversized)
        if g_fails:
            fails.append("%s: gate should WARN, not FAIL, on an oversized "
                          "file: %r" % (name, g_fails))
        if not any(g == gate_name and name in m for g, m in g_warns):
            fails.append("%s: gate did not warn on a file %d bytes over "
                          "its limit: %r" % (name, 10_000, g_warns))

    # 2. Every tracked file comfortably under its own limit stays silent.
    under = {name: "x" * 100 for name in preflight.LIVING_DOC_SIZE_LIMITS}
    with tempfile.TemporaryDirectory() as tmp2:
        fails2, warns2 = _run_gate(tmp2, under)
    if fails2 or any(g == gate_name for g, _ in warns2):
        fails.append("gate warned on files nowhere near their limits: "
                      "fails=%r warns=%r" % (fails2, warns2))

    # 3. A mix: one tracked file over its limit, the rest absent entirely
    #    (e.g. a partial checkout). Must warn only for the present,
    #    oversized one and must not crash on the missing files.
    names = sorted(preflight.LIVING_DOC_SIZE_LIMITS)
    mixed_name = names[0]
    mixed = {mixed_name: "x" * (preflight.LIVING_DOC_SIZE_LIMITS[mixed_name]
                                 + 10_000)}
    with tempfile.TemporaryDirectory() as tmp3:
        fails3, warns3 = _run_gate(tmp3, mixed)
    if fails3:
        fails.append("gate FAILed instead of WARNed with only one file "
                      "present: %r" % (fails3,))
    matching = [m for g, m in warns3 if g == gate_name]
    if not any(mixed_name in m for m in matching):
        fails.append("gate did not warn on the one oversized file present: "
                      "%r" % (warns3,))
    if any(other in m for other in names[1:] for m in matching):
        fails.append("gate warned about a file that does not exist on "
                      "disk: %r" % (warns3,))

    # 4. No tracked files present at all (e.g. a repo subset checkout):
    #    must not crash.
    with tempfile.TemporaryDirectory() as tmp4:
        fails4, warns4 = _run_gate(tmp4, {})
    if fails4 or warns4:
        fails.append("gate did not stay silent with no tracked files "
                      "present: fails=%r warns=%r" % (fails4, warns4))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_living_docs_total_size_tripwire, fail-then-pass "
          "proved, %d/%d checks pass"
          % (len(preflight.LIVING_DOC_SIZE_LIMITS) + 3,
             len(preflight.LIVING_DOC_SIZE_LIMITS) + 3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
