#!/usr/bin/env python3
"""
Prove ops/cycle_signal.py's --check/--record round trip actually detects
"nothing changed" versus "something changed", on synthetic files in an
isolated temp directory, never against the real committed
ops/cycle-signal.json.

Built 2026-10-11, operator, after independently confirming (direct GitHub
read, full BACKLOG-2026-09-07.md re-read, preflight clean) that every row
in the current backlog was Done, Phil-gated or closed by decision, the
same conclusion dozens of prior cycles that day had already reached. The
honest gap ops/NIGHTLY-LOG.md's own 2026-10-11 23:0x entry named was a
cheap way to confirm "nothing changed since the last cycle" before paying
for a full local re-verification; this proves that tool actually
distinguishes the two cases rather than always saying SAME (which would
be skipping verification, not shortcutting it) or always saying CHANGED
(which would buy nothing).

Run:  python ops/tests/test_cycle_signal.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import cycle_signal as cs                                         # noqa: E402


def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> int:
    fails = []

    with tempfile.TemporaryDirectory() as tmp:
        files = ["a.md", "b.md", "sub/c.json"]
        os.makedirs(os.path.join(tmp, "sub"), exist_ok=True)
        _write(os.path.join(tmp, "a.md"), "alpha one")
        _write(os.path.join(tmp, "b.md"), "beta one")
        _write(os.path.join(tmp, "sub", "c.json"), '{"v": 1}')

        old_root, old_snapshot, old_files = cs.ROOT, cs.SNAPSHOT_PATH, cs.SIGNAL_FILES
        cs.ROOT = tmp
        cs.SNAPSHOT_PATH = os.path.join(tmp, "cycle-signal.json")
        cs.SIGNAL_FILES = files
        try:
            # 1. No snapshot yet: must report MISSING, not SAME.
            result = cs.check()
            if result["verdict"] != "MISSING":
                fails.append("expected MISSING with no prior snapshot, got %r"
                             % result["verdict"])

            # 2. Record, then check immediately with nothing touched: SAME.
            cs.record("test: initial clean pass")
            result = cs.check()
            if result["verdict"] != "SAME":
                fails.append("expected SAME right after --record with no "
                             "edits, got %r (changed=%r)"
                             % (result["verdict"], result["changed_files"]))

            # 3. Mutate one signal file by a single byte: must report
            #    CHANGED and name exactly that file, not the others.
            _write(os.path.join(tmp, "b.md"), "beta one!")
            result = cs.check()
            if result["verdict"] != "CHANGED":
                fails.append("expected CHANGED after editing b.md, got %r"
                             % result["verdict"])
            if result["changed_files"] != ["b.md"]:
                fails.append("expected exactly ['b.md'] changed, got %r"
                             % result["changed_files"])

            # 4. A file that goes missing entirely is also a change, not a
            #    crash (a mid-cycle delete/rename must not be read as SAME).
            os.remove(os.path.join(tmp, "sub", "c.json"))
            result = cs.check()
            if result["verdict"] != "CHANGED" or "sub/c.json" not in result["changed_files"]:
                fails.append("expected a deleted signal file to show as "
                             "CHANGED, got %r" % result)

            # 5. Revert both edits byte-for-byte: hashes must match again,
            #    independent of git history or mtimes (content-only).
            _write(os.path.join(tmp, "b.md"), "beta one")
            _write(os.path.join(tmp, "sub", "c.json"), '{"v": 1}')
            result = cs.check()
            if result["verdict"] != "SAME":
                fails.append("expected SAME after reverting content "
                             "byte-for-byte, got %r (changed=%r)"
                             % (result["verdict"], result["changed_files"]))

            # 6. --record after a real change moves the baseline forward:
            #    checking against the OLD state must now read CHANGED.
            old_hash = cs.load_snapshot()["combined_hash"]
            _write(os.path.join(tmp, "a.md"), "alpha two")
            cs.record("test: second pass after a real edit")
            new_snap = cs.load_snapshot()
            if new_snap["combined_hash"] == old_hash:
                fails.append("recording after a real edit did not move "
                             "the combined hash")
            result = cs.check()
            if result["verdict"] != "SAME":
                fails.append("expected SAME immediately after recording "
                             "the new baseline, got %r" % result["verdict"])
        finally:
            cs.ROOT, cs.SNAPSHOT_PATH, cs.SIGNAL_FILES = old_root, old_snapshot, old_files

    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("OK: cycle_signal.py distinguishes SAME/CHANGED/MISSING correctly "
          "(6 cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
