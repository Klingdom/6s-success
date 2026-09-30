#!/usr/bin/env python3
"""
A structured record of which files the standing low-mention cold-read
lane has actually read and cleared or fixed, so the next cycle does not
have to reconstruct that from a 40,000+ line, ever-growing
ops/NIGHTLY-LOG.md by eye.

Covers four lanes: ops/*.py (164 files, closed 2026-09-27), ops/*.js
(1 file, added 2026-09-27 after the three-lane version above sat at
"174 of 174" without ever covering the one hand-authored .js file
living in the ops/ directory itself), and the hand-written
site/assets/js/*.js (7 files) and mobile/quest-app/lib/*.js (5 files,
excluding *.test.js: a test is read together with the module it tests,
not ledgered separately). Extended to the JS lanes 2026-09-27:
the log had been ranking them by raw mention count in prose ("already
exhausted this month by multiple cycles"), the exact proxy this file's
own history (below) shows failing at least three times for ops/*.py
before the ledger replaced it. Nothing in this repository's log had yet
shown the same failure for the JS lanes, but the failure mode is the
proxy itself, not something specific to Python files, and a cheap
extension of an already-proven fix is worth more than waiting for the
JS lanes to repeat the mistake first.

WHY THIS EXISTS
---------------
That log-grepping method is unreliable in practice, not in theory. This
repository's own log records it failing at least three separate times:
2026-09-11 (two concurrent sessions independently picked the same "next"
pair because neither could tell the other had already started); 2026-09-24
(a handoff named nine files as "unread", four of which a plain grep would
have shown were already cold-read and cleared earlier the same day); and
2026-09-25 00:1x (a handoff named five files, build_feed.py,
build_image_prompts.py, build_printpack.py, canonical_links.py and
room_image_variants.py, as "genuinely unread" when every one of the five
had already been read, and either cleared or fixed, on 2026-09-08 through
2026-09-24). Raw mention count is a poor proxy for "already read": a file
can be named many times in passing "next candidate" lists without ever
being opened, and a file that WAS read and fixed only shows up once, in
the entry that fixed it. This module replaces the proxy with an explicit,
append-only record that a cycle writes to only after it has actually read
a file, so presence in the ledger means "read", not "mentioned".

This is deliberately not a full backfill of this repository's cold-read
history; see ops/cold-read-ledger.json's own "_comment" field. A file's
absence from the ledger means unknown, never "confirmed unread": the
--next output still falls back to the old log-mention count as a rough
secondary signal for files neither the ledger nor a run of this tool has
seen.

Run:
    python ops/cold_read_ledger.py --next [N]        list N candidates
    python ops/cold_read_ledger.py --check FILE       report FILE's status
    python ops/cold_read_ledger.py --add FILE --status clean|fixed
        --note "..." [--date YYYY-MM-DD]              record a result
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import fnmatch
import glob
import io
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(ROOT, "ops", "cold-read-ledger.json")
LOG_PATH = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")
VALID_STATUSES = ("clean", "fixed")

# Generated, not hand-authored: a "Do not edit, rebuild from X" data dump
# cannot hide the kind of logic bug this lane exists to catch, and its
# actual source is ops/*.py, already covered by the ops lane. Found
# while adding the site/assets/js lane itself, 2026-09-27: a bare
# `site/assets/js/*.js` glob silently swept both of these in alongside
# the five genuinely hand-written files in that directory.
GENERATED_JS = frozenset({"data.js", "quest-data.js", "quest-data-symptoms.js"})

# (lane directory relative to ROOT, glob pattern within it). A basename
# collision across lanes would make the ledger's bare-name keys
# ambiguous; _all_candidate_files() checks for that rather than assume
# it stays true (checked 2026-09-27: 175 hand-authored files, zero
# collisions, after excluding GENERATED_JS and *.test.js).
#
# Found live 2026-09-27, PM check-in: the JS lanes only ever globbed
# site/assets/js and mobile/quest-app/lib, so ops/social_pin_fit.js, the
# one hand-authored .js file living inside the "ops" lane directory
# itself, was never a candidate under any pattern, not even a cleared
# one; "174 of 174" and "the JS lane is exhausted" were both true only
# for the lanes as narrowly defined, not for every hand-authored file
# this repository actually has. Added ("ops", "*.js") rather than widen
# the "ops" pattern to "*.py,*.js" so a future ops/*.py glob change
# cannot silently start matching .js files it was never meant to.
LANES = (
    ("ops", "*.py"),
    ("ops", "*.js"),
    ("site/assets/js", "*.js"),
    ("mobile/quest-app/lib", "*.js"),
)


def load_ledger() -> dict:
    """Returns {filename: {"status": ..., "date": ..., "note": ...}}.

    Missing file or malformed JSON both return {} rather than raising:
    a ledger that cannot be read must behave as "nothing is recorded",
    never as "everything is clean" (CLAUDE.md 0.4, unknown is not a
    default).
    """
    if not os.path.exists(LEDGER_PATH):
        return {}
    try:
        data = json.loads(io.open(LEDGER_PATH, encoding="utf-8").read())
    except Exception:                                          # noqa: BLE001
        return {}
    entries = data.get("entries", {})
    return entries if isinstance(entries, dict) else {}


def last_touched(path: str) -> str | None:
    """The date (YYYY-MM-DD) of the most recent commit that changed path,
    relative to ROOT, or None if git has nothing to say (untracked, no
    history, or git itself unavailable). Never raises: a git failure must
    read as "unknown", not as "never touched" or "touched today".
    """
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=10)
    except Exception:                                            # noqa: BLE001
        return None
    date = out.stdout.strip()
    return date or None


def stale_entries(ledger: dict | None = None) -> list[tuple[str, str, str]]:
    """Ledger entries whose file has been committed to AFTER the date the
    ledger recorded it clean/fixed on, so the entry's "no defect found" (or
    "fixed") claim is no longer a claim about the code that exists today.

    Found live 2026-09-30, re-verifying ops/deploy_freshness.py from the
    ledger's own oldest-first queue: the ledger still read "clean, dated
    2026-09-25, ... no defect found in the source", but a real defect (the
    freshness probe's own URL causing 2,270 self-inflicted redirects) was
    found and fixed in this exact file on 2026-09-29, four days later,
    without the ledger ever being told. Nothing before this function ever
    compared a ledger entry's date against the file's own git history, so
    a clean verdict could silently outlive the code it was a verdict about,
    the same "source corrected, artifact never re-derived" shape
    BACKLOG-2026-09-07.md section 7 names as this repository's dominant
    defect class, here applied to the ledger's own bookkeeping rather than
    a generated page.

    Returns (basename, ledger_date, last_touched_date) tuples, oldest
    ledger_date first. A file git cannot date (untracked, or the git call
    itself failed) is silently skipped, never treated as stale: unknown is
    not a default (CLAUDE.md 0.4), and this must not manufacture a false
    positive out of a sandbox limitation.
    """
    ledger = load_ledger() if ledger is None else ledger
    out = []
    for base, entry in ledger.items():
        if entry.get("status") not in VALID_STATUSES:
            continue
        rel = lane_path(base)
        if rel is None:
            continue
        touched = last_touched(rel)
        if touched and touched > entry.get("date", ""):
            out.append((base, entry["date"], touched))
    out.sort(key=lambda t: t[1])
    return out


def is_cleared(filename: str, ledger: dict | None = None) -> bool:
    """True only if the ledger explicitly records this basename as read
    (clean or fixed). Accepts either a bare name or an ops/-prefixed path.
    """
    ledger = load_ledger() if ledger is None else ledger
    base = os.path.basename(filename)
    entry = ledger.get(base)
    return bool(entry) and entry.get("status") in VALID_STATUSES


def _all_candidate_files() -> list[str]:
    """Basenames across every lane in LANES, excluding *.test.js (a test
    is read together with the module it tests, not ledgered on its own)
    and GENERATED_JS (generated output, not hand-authored logic).

    Raises rather than silently picking one if two lanes ever produce
    the same basename: the ledger keys on bare basenames, so a
    collision would make one file's entry shadow the other's.
    """
    seen: dict[str, str] = {}
    for lane_dir, pattern in LANES:
        for p in glob.glob(os.path.join(ROOT, lane_dir, pattern)):
            if p.endswith(".test.js") or os.path.basename(p) in GENERATED_JS:
                continue
            base = os.path.basename(p)
            if base in seen and seen[base] != lane_dir:
                raise SystemExit(
                    "cold_read_ledger: %r exists in both %s and %s; "
                    "the ledger's bare-basename keys assume no collision"
                    % (base, seen[base], lane_dir))
            seen[base] = lane_dir
    return sorted(seen)


def lane_path(base: str) -> str | None:
    """The lane-relative path a basename actually lives at, or None."""
    if base.endswith(".test.js") or base in GENERATED_JS:
        return None
    for lane_dir, pattern in LANES:
        candidate = os.path.join(ROOT, lane_dir, base)
        if os.path.exists(candidate) and fnmatch.fnmatch(base, pattern):
            return os.path.join(lane_dir, base)
    return None


def _mention_counts() -> dict:
    """Rough secondary signal only, kept from the method this file
    replaces: how many times each candidate basename appears anywhere in
    ops/NIGHTLY-LOG.md. Never used to claim a file is clean, only to rank
    otherwise-unledgered candidates.
    """
    counts = collections.defaultdict(int)
    if not os.path.exists(LOG_PATH):
        return counts
    text = io.open(LOG_PATH, encoding="utf-8").read()
    for name in _all_candidate_files():
        counts[name] = len(re.findall(re.escape(name), text))
    return counts


def next_candidates(n: int = 15) -> list[tuple[str, int]]:
    """Genuinely un-ledgered candidate files, ranked lowest-mention first."""
    ledger = load_ledger()
    counts = _mention_counts()
    candidates = [
        (name, counts.get(name, 0))
        for name in _all_candidate_files()
        if not is_cleared(name, ledger)
    ]
    candidates.sort(key=lambda t: (t[1], t[0]))
    return candidates[:n]


def add_entry(filename: str, status: str, note: str,
              date: str | None = None) -> None:
    if status not in VALID_STATUSES:
        raise SystemExit("--status must be one of %s" % (VALID_STATUSES,))
    base = os.path.basename(filename)
    if base in GENERATED_JS:
        raise SystemExit("%s is generated output, not hand-authored "
                          "logic; not tracked in this ledger" % base)
    resolved = lane_path(base)
    if resolved is None:
        raise SystemExit("no such file in a tracked lane (%s): %s"
                          % (", ".join(d for d, _ in LANES), base))
    if os.path.exists(LEDGER_PATH):
        try:
            data = json.loads(io.open(LEDGER_PATH, encoding="utf-8").read())
        except Exception:                                       # noqa: BLE001
            data = {"_comment": "", "entries": {}}
    else:
        data = {"_comment": "", "entries": {}}
    data.setdefault("entries", {})[base] = {
        "status": status,
        "date": date or dt.date.today().isoformat(),
        "note": note,
    }
    data["entries"] = dict(sorted(data["entries"].items()))
    with io.open(LEDGER_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=2, ensure_ascii=False))
        fh.write("\n")
    print("recorded %s as %s" % (resolved, status))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", nargs="?", const=15, type=int, default=None)
    ap.add_argument("--stale", action="store_true",
                     help="list ledger entries the git history has "
                          "outdated (file committed to after its clean/"
                          "fixed date)")
    ap.add_argument("--check")
    ap.add_argument("--add")
    ap.add_argument("--status", choices=VALID_STATUSES)
    ap.add_argument("--note", default="")
    ap.add_argument("--date")
    args = ap.parse_args()

    if args.add:
        if not args.status:
            raise SystemExit("--add requires --status clean|fixed")
        add_entry(args.add, args.status, args.note, args.date)
        return 0

    if args.stale:
        stale = stale_entries()
        if not stale:
            print("0 ledger entries are stale: every clean/fixed date is "
                  ">= the file's own last commit date.")
            return 0
        print("%d ledger entr%s the file's git history has outdated:\n"
              % (len(stale), "y" if len(stale) == 1 else "ies"))
        for base, ledger_date, touched in stale:
            print("  %s: ledgered %s, but last touched %s"
                  % (lane_path(base) or base, ledger_date, touched))
        return 0

    if args.check:
        ledger = load_ledger()
        base = os.path.basename(args.check)
        path = lane_path(base) or base
        entry = ledger.get(base)
        if entry:
            note = ""
            touched = last_touched(lane_path(base) or "") if lane_path(base) else None
            if touched and touched > entry.get("date", ""):
                note = (" -- STALE: last touched %s, after this entry's "
                         "own %s clean/fixed date" % (touched, entry["date"]))
            print("%s: %s (%s) - %s%s"
                  % (path, entry["status"], entry["date"], entry["note"], note))
        else:
            print("%s: not in the ledger (unknown, not unread)" % path)
        return 0

    n = args.next if args.next is not None else 15
    ledger = load_ledger()
    all_files = _all_candidate_files()
    ledger_size = sum(1 for f in all_files if is_cleared(f, ledger))
    total = len(all_files)
    lane_dirs = list(dict.fromkeys(d for d, _ in LANES))
    stale_count = len(stale_entries(ledger))
    print("%d of %d files across %s are in the ledger (%d stale: run "
          "--stale). Next %d un-ledgered candidates, lowest log-mention "
          "count first (mention count is a rough secondary signal only):\n"
          % (ledger_size, total, ", ".join(lane_dirs), stale_count, n))
    for name, count in next_candidates(n):
        print("  %3d  %s" % (count, lane_path(name) or name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
