#!/usr/bin/env python3
"""
Cheap pre-check for whether anything has actually changed since the last
cycle that ran a full local re-verification (preflight --fast/--deep, a
full backlog re-read, the cold-read ledger).

WHY THIS EXISTS
---------------
ops/NIGHTLY-LOG.md's 2026-10-11 23:0x entry: "dozens of cycles today spent
a full pass reaching an identical, already-exhausted conclusion... the
honest fix, if one exists, is a cheaper way to confirm 'nothing changed
since the last cycle' before paying for a full re-verification, not
skipping verification." By 2026-10-11, every row in BACKLOG-2026-09-07.md
sections 2-4 was Done, Phil-gated, or closed by decision, confirmed
independently that same day. The repeated cost since has been concurrent
scheduled sessions each re-deriving the identical "nothing new" conclusion
from scratch, every ten to twenty minutes, against a repository that had
not materially changed between them.

WHAT THIS DOES NOT DO
----------------------
It never replaces verification with a guess. A cycle whose signal comes
back SAME still has to independently check the things no local file hash
can see: GitHub's open issues/PRs (one cheap read), the mail inbox, and
the scheduled workflows' latest runs. Those stay mandatory every cycle,
per CLAUDE.md 0.4 ("unknown is not unused"). What this tool lets a cycle
skip, honestly, is re-running the expensive LOCAL-ONLY checks (preflight's
multi-minute gate_tests sandbox hang, a full line-by-line backlog re-read,
the cold-read ledger's own scan) against a repository whose signal files
are byte-identical to the last time those checks ran clean. If any signal
file differs by even one byte, or no prior snapshot exists, this returns
CHANGED or MISSING and the full pass stays mandatory, no exceptions.

SIGNAL FILES
------------
A deliberately narrow set: the documents whose content is what "has
anything changed" means for backlog/priority purposes. Command-deck
regeneration (EXECUTIVE-DASHBOARD-LIVE.md, ops/dashboard.html,
ops/state.json) and ops/NIGHTLY-LOG.md are excluded on purpose: almost
every cycle rewrites them even when nothing else moved, so including them
would make the signal change every single cycle and defeat the point.

USAGE
-----
  python ops/cycle_signal.py --check
      Exit 0 and print SAME if every signal file matches the last
      recorded snapshot (safe to skip the expensive local re-verification
      this cycle). Exit 1 and print CHANGED (naming the files) or MISSING
      otherwise (run the full pass).

  python ops/cycle_signal.py --record --note "preflight fast clean, ..."
      After a full verification pass has actually run clean, record the
      current signal files as the new snapshot other cycles will compare
      against.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_PATH = os.path.join(ROOT, "ops", "cycle-signal.json")

SIGNAL_FILES = [
    "BACKLOG-2026-09-07.md",
    "BACKLOG-2026-H2.md",
    "OWNER-ACTIONS.md",
    "STATUS.md",
    "GOALS.md",
    "ops/deploy-verdict.json",
    "ops/cold-read-ledger.json",
]


def _hash_file(rel_path: str) -> str:
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def compute_signals(signal_files=None) -> dict:
    files = SIGNAL_FILES if signal_files is None else signal_files
    return {f: _hash_file(f) for f in files}


def combined_hash(signals: dict, signal_files=None) -> str:
    files = SIGNAL_FILES if signal_files is None else signal_files
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode("utf-8"))
        h.update(signals.get(f, "MISSING").encode("utf-8"))
    return h.hexdigest()


def git_head() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return "UNKNOWN"


def load_snapshot():
    if not os.path.exists(SNAPSHOT_PATH):
        return None
    try:
        with open(SNAPSHOT_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def record(note: str) -> dict:
    signals = compute_signals()
    snap = {
        "recorded_at": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": git_head(),
        "combined_hash": combined_hash(signals),
        "signals": signals,
        "note": note,
    }
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2, sort_keys=True)
        f.write("\n")
    return snap


def check() -> dict:
    prior = load_snapshot()
    current = compute_signals()
    current_hash = combined_hash(current)
    if prior is None:
        return {"verdict": "MISSING", "changed_files": [], "prior": None,
                "current_hash": current_hash}
    changed = [f for f in SIGNAL_FILES
               if prior.get("signals", {}).get(f) != current.get(f)]
    verdict = "CHANGED" if changed else "SAME"
    return {"verdict": verdict, "changed_files": changed, "prior": prior,
            "current_hash": current_hash}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                     help="Compare current signal files against the last recorded snapshot.")
    ap.add_argument("--record", action="store_true",
                     help="Record the current signal files as the new snapshot, "
                          "after a full verification pass.")
    ap.add_argument("--note", default="",
                     help="With --record: a short note on what was verified clean this cycle.")
    args = ap.parse_args()

    if args.record:
        snap = record(args.note)
        print(f"  recorded cycle signal snapshot at {snap['recorded_at']} "
              f"(git {snap['git_head'][:10]}, hash {snap['combined_hash'][:12]})")
        return 0

    result = check()
    if result["verdict"] == "MISSING":
        print("  MISSING: no prior cycle-signal snapshot exists. Treat this as changed, "
              "run the full local re-verification, then record one with --record once "
              "it is clean.")
        return 1
    if result["verdict"] == "SAME":
        prior = result["prior"]
        print(f"  SAME: every signal file is byte-identical to the snapshot recorded "
              f"{prior['recorded_at']} (git {prior['git_head'][:10]}, note: "
              f"{prior.get('note') or '(none)'}). A full local re-verification of these "
              f"files would be redundant this cycle; GitHub, the inbox and the scheduled "
              f"workflows still need a direct, independent check every cycle.")
        return 0
    print(f"  CHANGED: {len(result['changed_files'])} signal file(s) differ from the last "
          f"recorded snapshot ({result['prior']['recorded_at']}): {result['changed_files']}. "
          f"Run the full local re-verification, then --record a fresh snapshot once clean.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
