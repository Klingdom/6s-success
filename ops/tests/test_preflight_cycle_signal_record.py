#!/usr/bin/env python3
"""
Prove preflight.py's maybe_record_cycle_signal() actually gates on a
clean pass, fail-then-pass, against synthetic files in an isolated temp
directory, never against the real committed ops/cycle-signal.json.

Built 2026-10-19, this operator: cycle_signal.py existed since 2026-10-11
with a --record step its own docstring says to run "after a full
verification pass has actually run clean", but no cycle prompt ever
called --record, so 58 consecutive cycles since the last legitimate
STATUS.md edit (2026-10-18 20:4x) each paid for cycle_signal.py's
CHANGED path (a manual diff) instead of getting SAME for free.
preflight.py now calls maybe_record_cycle_signal(FAIL) itself at the end
of a run that reaches that point at all, so the snapshot updates without
depending on a cycle remembering a step no prompt asked for. This proves
two things a stray call could get wrong: a run with any FAIL must never
record (that would mark a broken tree as the trusted baseline), and a
genuinely clean run must record so the next cycle's cycle_signal --check
reports SAME.

Run:  python ops/tests/test_preflight_cycle_signal_record.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import cycle_signal as cs                                         # noqa: E402
import preflight                                                  # noqa: E402


def main() -> int:
    fails = []

    with tempfile.TemporaryDirectory() as tmp:
        files = ["a.md", "b.md"]
        with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as f:
            f.write("alpha")
        with open(os.path.join(tmp, "b.md"), "w", encoding="utf-8") as f:
            f.write("beta")

        old_root, old_snapshot, old_files = cs.ROOT, cs.SNAPSHOT_PATH, cs.SIGNAL_FILES
        cs.ROOT = tmp
        cs.SNAPSHOT_PATH = os.path.join(tmp, "cycle-signal.json")
        cs.SIGNAL_FILES = files
        try:
            # 1. FAIL-then-PASS, part one: a run with a failing gate must
            # never record, proving this is a real gate and not theatre.
            wrote = preflight.maybe_record_cycle_signal([("gate_x", "broke")])
            if wrote:
                fails.append("recorded a snapshot despite a FAIL present")
            if os.path.exists(cs.SNAPSHOT_PATH):
                fails.append("a snapshot file was written despite a FAIL present")

            # 2. A clean run (empty FAIL list) must record.
            wrote = preflight.maybe_record_cycle_signal([])
            if not wrote:
                fails.append("did not record on a clean (empty FAIL) run")
            if not os.path.exists(cs.SNAPSHOT_PATH):
                fails.append("no snapshot file exists after a clean run recorded")

            # 3. The next cycle's own --check must now see SAME, which is
            # the entire point: a clean preflight run should make the
            # cheap pre-check usable without a separate manual --record.
            result = cs.check()
            if result["verdict"] != "SAME":
                fails.append("cycle_signal.check() did not report SAME "
                              "right after a clean-run auto-record, got %r"
                              % result["verdict"])

            # 4. Touching a signal file after that must flip it back to
            # CHANGED, proving the recorded snapshot is a real baseline
            # and not a permanent SAME short-circuit.
            with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as f:
                f.write("alpha, edited")
            result = cs.check()
            if result["verdict"] != "CHANGED":
                fails.append("expected CHANGED after editing a signal file "
                              "post-record, got %r" % result["verdict"])
        finally:
            cs.ROOT, cs.SNAPSHOT_PATH, cs.SIGNAL_FILES = old_root, old_snapshot, old_files

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: maybe_record_cycle_signal() gates on FAIL and makes the "
          "next cycle's cycle_signal.check() report SAME, 4/4 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
