#!/usr/bin/env python3
"""
Prove gate_status_metadata_not_oversized() can actually warn on a STATUS.md
whose section 1 chain has grown past its buffer of non-latest-date entries,
and stays silent once it is down to the buffer. A gate that cannot go red
is theatre (ops/preflight.py's own stated rule).

Run:  python ops/tests/test_gate_status_metadata_not_oversized.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                                # noqa: E402

POINTER = ("**Older entries (5 of them, 2026-08 to 2026-10-01) live in "
           "`STATUS-ARCHIVE.md`.** Some trailing prose.")
FOOTER = "\n\n# 2. Executive Snapshot\n\nmore file follows.\n"


def _status_text(n_old_entries, newest_date="2026-10-26"):
    """One live entry at `newest_date`, plus n_old_entries older ones each
    on a distinct earlier date, oldest-looking label style mixed in to
    match the real chain's variety.
    """
    parts = ["**Last Updated:** %s: the current entry." % newest_date]
    for i in range(n_old_entries):
        parts.append("**Earlier, 2026-09-%02d: an older entry." % (i + 1))
    body = "\n\n".join(parts)
    return "# 1. Status Metadata\n\n" + body + "\n\n" + POINTER + FOOTER


def _run_gate(tmp, status_text):
    io.open(os.path.join(tmp, "STATUS.md"), "w", encoding="utf-8").write(
        status_text)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_status_metadata_not_oversized()
        return list(preflight.FAIL), list(preflight.WARN)
    finally:
        preflight.ROOT = old_root


GATE = "status-metadata-not-oversized"


def main() -> int:
    fails = []

    # 1. Well past the buffer (10 older entries behind the newest): warns.
    with tempfile.TemporaryDirectory() as tmp:
        f1, w1 = _run_gate(tmp, _status_text(10))
    if f1:
        fails.append("should WARN, not FAIL, on an oversized chain: %r"
                      % (f1,))
    if not any(g == GATE for g, _ in w1):
        fails.append("did not warn on a chain with 10 older entries: %r"
                      % (w1,))

    # 2. Only the newest entry, nothing older: silent.
    with tempfile.TemporaryDirectory() as tmp2:
        f2, w2 = _run_gate(tmp2, _status_text(0))
    if f2 or any(g == GATE for g, _ in w2):
        fails.append("warned on a chain with only the newest entry: "
                      "fails=%r warns=%r" % (f2, w2))

    # 3. Right at the buffer (3 older entries): still silent.
    with tempfile.TemporaryDirectory() as tmp3:
        f3, w3 = _run_gate(tmp3, _status_text(3))
    if f3 or any(g == GATE for g, _ in w3):
        fails.append("warned on a chain still inside the buffer: "
                      "fails=%r warns=%r" % (f3, w3))

    # 4. One past the buffer (4 older entries): warns.
    with tempfile.TemporaryDirectory() as tmp4:
        f4, w4 = _run_gate(tmp4, _status_text(4))
    if f4 or not any(g == GATE for g, _ in w4):
        fails.append("did not warn one entry past the buffer: "
                      "fails=%r warns=%r" % (f4, w4))

    # 5. Two entries tied at the same (latest) date, both counted as
    #    current, not as "older": still silent even with the buffer-sized
    #    tail, since only the tied pair is exempt, not a free pass.
    with tempfile.TemporaryDirectory() as tmp5:
        tied = ("# 1. Status Metadata\n\n"
                "**Last Updated:** 2026-10-26: first of a tie.\n\n"
                "**Earlier, 2026-10-26: second of a tie.\n\n"
                "**Earlier, 2026-09-01: one older entry.\n\n" + POINTER
                + FOOTER)
        f5, w5 = _run_gate(tmp5, tied)
    if f5 or any(g == GATE for g, _ in w5):
        fails.append("warned on a tied-latest-date pair with only 1 older "
                      "entry (inside the buffer): fails=%r warns=%r"
                      % (f5, w5))

    # 6. No STATUS.md at all: must not crash.
    with tempfile.TemporaryDirectory() as tmp6:
        old_root = preflight.ROOT
        preflight.ROOT = tmp6
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_status_metadata_not_oversized()
        except Exception as exc:                                # noqa: BLE001
            fails.append("gate crashed with no STATUS.md present: %r"
                          % (exc,))
        finally:
            preflight.ROOT = old_root

    # 7. A STATUS.md whose section 1 does not match this script's
    #    expectations must not crash: stay silent rather than guess.
    with tempfile.TemporaryDirectory() as tmp7:
        f7, w7 = _run_gate(tmp7, "# Some other file entirely\n\nno chain "
                           "here.\n")
    if f7 or w7:
        fails.append("gate reacted to a file with no recognisable chain: "
                      "fails=%r warns=%r" % (f7, w7))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_status_metadata_not_oversized, fail-then-pass proved, "
          "7/7 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
