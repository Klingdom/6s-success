#!/usr/bin/env python3
"""
A structured record of which ops/*.py files the standing low-mention
cold-read lane has actually read and cleared or fixed, so the next cycle
does not have to reconstruct that from a 37,000+ line, ever-growing
ops/NIGHTLY-LOG.md by eye.

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
import glob
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(ROOT, "ops", "cold-read-ledger.json")
LOG_PATH = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")
VALID_STATUSES = ("clean", "fixed")


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


def is_cleared(filename: str, ledger: dict | None = None) -> bool:
    """True only if the ledger explicitly records this basename as read
    (clean or fixed). Accepts either a bare name or an ops/-prefixed path.
    """
    ledger = load_ledger() if ledger is None else ledger
    base = os.path.basename(filename)
    entry = ledger.get(base)
    return bool(entry) and entry.get("status") in VALID_STATUSES


def _all_ops_py_files() -> list[str]:
    return sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(ROOT, "ops", "*.py"))
    )


def _mention_counts() -> dict:
    """Rough secondary signal only, kept from the method this file
    replaces: how many times each ops/*.py basename appears anywhere in
    ops/NIGHTLY-LOG.md. Never used to claim a file is clean, only to rank
    otherwise-unledgered candidates.
    """
    counts = collections.defaultdict(int)
    if not os.path.exists(LOG_PATH):
        return counts
    text = io.open(LOG_PATH, encoding="utf-8").read()
    for name in _all_ops_py_files():
        counts[name] = len(re.findall(re.escape(name), text))
    return counts


def next_candidates(n: int = 15) -> list[tuple[str, int]]:
    """Genuinely un-ledgered ops/*.py files, ranked lowest-mention first."""
    ledger = load_ledger()
    counts = _mention_counts()
    candidates = [
        (name, counts.get(name, 0))
        for name in _all_ops_py_files()
        if not is_cleared(name, ledger)
    ]
    candidates.sort(key=lambda t: (t[1], t[0]))
    return candidates[:n]


def add_entry(filename: str, status: str, note: str,
              date: str | None = None) -> None:
    if status not in VALID_STATUSES:
        raise SystemExit("--status must be one of %s" % (VALID_STATUSES,))
    base = os.path.basename(filename)
    if not os.path.exists(os.path.join(ROOT, "ops", base)):
        raise SystemExit("no such file: ops/%s" % base)
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
    print("recorded ops/%s as %s" % (base, status))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", nargs="?", const=15, type=int, default=None)
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

    if args.check:
        ledger = load_ledger()
        base = os.path.basename(args.check)
        entry = ledger.get(base)
        if entry:
            print("ops/%s: %s (%s) - %s"
                  % (base, entry["status"], entry["date"], entry["note"]))
        else:
            print("ops/%s: not in the ledger (unknown, not unread)" % base)
        return 0

    n = args.next if args.next is not None else 15
    ledger_size = len(load_ledger())
    total = len(_all_ops_py_files())
    print("%d of %d ops/*.py files are in the ledger. "
          "Next %d un-ledgered candidates, lowest log-mention count first "
          "(mention count is a rough secondary signal only):\n"
          % (ledger_size, total, n))
    for name, count in next_candidates(n):
        print("  %3d  %s" % (count, name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
