#!/usr/bin/env python3
"""
A structured record of which files the standing low-mention cold-read
lane has actually read and cleared or fixed, so the next cycle does not
have to reconstruct that from a 40,000+ line, ever-growing
ops/NIGHTLY-LOG.md by eye.

Covers six lanes: ops/*.py (164 files, closed 2026-09-27), ops/*.js
(1 file, added 2026-09-27 after the three-lane version above sat at
"174 of 174" without ever covering the one hand-authored .js file
living in the ops/ directory itself), the hand-written
site/assets/js/*.js (7 files) and mobile/quest-app/lib/*.js (5 files,
excluding *.test.js: a test is read together with the module it tests,
not ledgered separately), photos/*.py (4 files, added 2026-10-16), and
ops/cardtext/*.py (21 files, added 2026-10-17: a non-recursive "ops/*.py"
glob cannot see its own subdirectory, so these 20 room-deck generators
and derive_room_deck.py had never been a ledger candidate at all, the
same blind spot the photos/ lane closed a day earlier for a different
subdirectory), and build/listings/*.py (9 files, added 2026-10-18: the
commerce-channel build/check/verify scripts behind the Amazon KDP and
Etsy listings, found genuinely un-ledgered the same way photos/ and
ops/cardtext were, by listing every *.py/*.js file outside the known
lanes rather than trusting "229 of 229" to mean every file. Read and ran
all 9: check_etsy.py, check_kdp.py, verify_epub.py and
verify_zone_claims.py all PASS with zero FAIL against the real committed
files; build_kdp_cover.py and build_etsy_assets.py both regenerate their
committed outputs byte-identical in content (build_etsy_assets.py's PDFs
differ by a Chromium-embedded timestamp and, for one listing, by
non-deterministic font/image re-encoding bytes with identical text and
page/card counts; the regenerated files were not committed, since
re-rendering is not a fix). No defect found), and 13 more lanes covering
40 files (added 2026-10-18, see LANES below and
`gate_cold_read_lanes_complete` in ops/preflight.py, which now makes this
kind of gap impossible to miss a fifth time rather than relying on a
cycle choosing to re-run the same manual sweep). Extended to the JS lanes 2026-09-27:
the log had been ranking them by raw mention count in prose ("already
exhausted this month by multiple cycles"), the exact proxy this file's
own history (below) shows failing at least three times for ops/*.py
before the ledger replaced it. Nothing in this repository's log had yet
shown the same failure for the JS lanes, but the failure mode is the
proxy itself, not something specific to Python files, and a cheap
extension of an already-proven fix is worth more than waiting for the
JS lanes to repeat the mistake first.

The photos/ lane was missing entirely until 2026-10-16, found only once
every other lane and the backlog had both come back fully exhausted and
a cycle went looking for genuinely unswept ground rather than stopping.
photos/*.py had been read twice before, by two independent adversarial
security passes (PHOTOS-API.md's "Found and fixed" section), but neither
is this lane: both hunted for attacker-triggered gaps, and the defect
this lane's own first read found, a lost-upload race under ordinary
concurrent use with no attacker involved, is exactly the class of
correctness bug a security review is not shaped to catch and a cold
read is.

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
LOG_ARCHIVE_PATH = os.path.join(ROOT, "ops", "NIGHTLY-LOG-ARCHIVE.md")
VALID_STATUSES = ("clean", "fixed")

# Generated, not hand-authored: a "Do not edit, rebuild from X" data dump
# cannot hide the kind of logic bug this lane exists to catch, and its
# actual source is ops/*.py, already covered by the ops lane. Found
# while adding the site/assets/js lane itself, 2026-09-27: a bare
# `site/assets/js/*.js` glob silently swept both of these in alongside
# the five genuinely hand-written files in that directory. zoneHeroes.js
# added 2026-10-18 adding the mobile/quest-app/assets lane: it is a flat
# require()-map generated by ops/build_mobile_corpus.py, not hand logic,
# the identical shape one directory over.
GENERATED_JS = frozenset({
    "data.js", "quest-data.js", "quest-data-symptoms.js", "zoneHeroes.js",
})

# Full repo-relative paths, outside every LANES directory, that are
# generated output rather than hand-authored logic (see GENERATED_JS for
# the in-lane equivalent). Checked by gate_cold_read_lanes_complete so
# this exclusion is never just "a file nobody looked at again": each
# entry names the generator that actually owns it.
NON_LANE_GENERATED = frozenset({
    # GENERATED by ops/build_pwa.py (see that file's own docstring); the
    # live service worker site visitors actually get. Its logic lives in
    # and is reviewed through ops/build_pwa.py, already in the ops lane.
    "site/sw.js",
})

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
    ("photos", "*.py"),
    ("ops/cardtext", "*.py"),
    ("build/listings", "*.py"),
    # Added 2026-10-18, found by gate_cold_read_lanes_complete's own
    # independent `git ls-files '*.py' '*.js'` sweep rather than by hand:
    # the same blind spot that found photos/, ops/cardtext/ and
    # build/listings/ three times before, now closed by a gate instead of
    # a fourth manual re-discovery. .githooks and mcp are single
    # standalone scripts; mobile/quest-app (non-recursive, so it does not
    # also match the already-covered lib/ subdirectory) and
    # mobile/quest-app/assets are the React Native app shell and its
    # zone-hero data module; the five content/*/source directories are
    # the hand-authored build/collect/validate scripts behind the app
    # spec, the print manual, and the three video-package pipelines.
    (".githooks", "*.py"),
    ("mcp", "*.py"),
    ("mobile/quest-app", "*.js"),
    ("mobile/quest-app/assets", "*.js"),
    ("content/app-mvp/app", "*.js"),
    ("content/app-mvp/native-providers/ios", "*.js"),
    ("content/app-mvp/proxy", "*.js"),
    ("content/app-mvp/source", "*.py"),
    ("content/app-spec/source", "*.py"),
    ("content/manual/source", "*.py"),
    ("content/video/media-package-entryway/source", "*.py"),
    ("content/video/pilot/source", "*.py"),
    ("content/video/source", "*.py"),
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
    """True only if the ledger explicitly records this file as read
    (clean or fixed). Accepts a bare basename, a lane-relative path, or
    an already-qualified ledger key; see _normalize_key for how a
    cross-lane basename collision is resolved.
    """
    ledger = load_ledger() if ledger is None else ledger
    key = _normalize_key(filename)
    entry = ledger.get(key)
    return bool(entry) and entry.get("status") in VALID_STATUSES


def _lane_files() -> list[tuple[str, str]]:
    """(lane_dir, base) for every real candidate file across LANES,
    excluding *.test.js (a test is read together with the module it
    tests, not ledgered on its own) and GENERATED_JS (generated output,
    not hand-authored logic). Before collision-qualification; internal
    helper for _collision_bases() and _all_candidate_files().
    """
    out = []
    for lane_dir, pattern in LANES:
        for p in glob.glob(os.path.join(ROOT, lane_dir, pattern)):
            if p.endswith(".test.js") or os.path.basename(p) in GENERATED_JS:
                continue
            out.append((lane_dir, os.path.basename(p)))
    return out


def _collision_bases() -> set[str]:
    """Basenames that exist in more than one lane directory, e.g.
    mcp/server.py and photos/server.py (found 2026-10-18 adding the mcp
    lane). These need the lane directory in their ledger key; every
    other basename keeps the plain bare-basename key the ledger has
    always used, so this never touches the other 237 entries.
    """
    by_base: dict[str, set[str]] = collections.defaultdict(set)
    for lane_dir, base in _lane_files():
        by_base[base].add(lane_dir)
    return {base for base, dirs in by_base.items() if len(dirs) > 1}


def _key_for(lane_dir: str, base: str, collisions: set[str] | None = None) -> str:
    """The ledger key for a file: its bare basename, unless that
    basename collides across lanes, in which case "lane_dir/base".
    """
    if collisions is None:
        collisions = _collision_bases()
    return "%s/%s" % (lane_dir, base) if base in collisions else base


def _all_candidate_files() -> list[str]:
    """Ledger keys for every real candidate file across LANES: a bare
    basename normally, or a collision-qualified "lane_dir/base" for the
    rare basename that exists in more than one lane (see
    _collision_bases). No longer raises on collision; it disambiguates
    instead, since a real one surfaced live (mcp/server.py vs
    photos/server.py, 2026-10-18) and the fix the raise exists to force
    is this function, not an endless stream of renamed source files.
    """
    collisions = _collision_bases()
    keys = {_key_for(lane_dir, base, collisions)
            for lane_dir, base in _lane_files()}
    return sorted(keys)


def lane_path(key: str) -> str | None:
    """The lane-relative path a ledger key actually lives at, or None.
    key is either a bare basename (the common case) or a
    collision-qualified "lane_dir/base" (see _collision_bases). A bare
    basename that is itself a collision is ambiguous and returns None:
    callers must pass the qualified form for those.
    """
    base = os.path.basename(key)
    if base.endswith(".test.js") or base in GENERATED_JS:
        return None
    if "/" in key:
        lane_dir = key.rsplit("/", 1)[0]
        for d, pattern in LANES:
            if d != lane_dir:
                continue
            candidate = os.path.join(ROOT, d, base)
            if os.path.exists(candidate) and fnmatch.fnmatch(base, pattern):
                return os.path.join(d, base)
        return None
    matches = [d for d, pattern in LANES
               if fnmatch.fnmatch(base, pattern)
               and os.path.exists(os.path.join(ROOT, d, base))]
    return os.path.join(matches[0], base) if len(matches) == 1 else None


def _normalize_key(filename: str) -> str:
    """Turn a CLI argument (a bare basename like "server.py", a
    lane-relative path like "mcp/server.py", or an already-qualified
    ledger key) into the correct ledger key, resolving the rare
    cross-lane basename collision (see _collision_bases) using whatever
    directory the caller already supplied, or raising with the
    qualified forms to choose from if they supplied none.
    """
    base = os.path.basename(filename)
    collisions = _collision_bases()
    if base not in collisions:
        return base
    given_dir = os.path.dirname(filename).replace(os.sep, "/")
    options = [d for d, _ in LANES
               if os.path.exists(os.path.join(ROOT, d, base))]
    if given_dir in options:
        return "%s/%s" % (given_dir, base)
    if len(options) == 1:
        return "%s/%s" % (options[0], base)
    raise SystemExit(
        "%r is ambiguous across lanes (%s); pass one of: %s"
        % (filename, ", ".join(options),
           ", ".join("%s/%s" % (d, base) for d in options)))


def lane_coverage_gaps(tracked_files: list[str]) -> list[str]:
    """Which of tracked_files (repo-relative *.py/*.js paths, in the
    form `git ls-files` reports them) carry hand-authored logic that no
    LANES entry covers and no known-generated exclusion accounts for.

    Pure function over an injected file list, so a test can prove this
    fails on a planted gap without waiting for a real new directory to
    go undiscovered a fifth time (see LANES's own history: photos/,
    ops/cardtext/, build/listings/ and then 13 more lanes covering 39
    files, 2026-10-16 through 2026-10-18, every one found by a cycle
    choosing to run `git ls-files '*.py' '*.js'` and read the directory
    list by eye rather than by anything that would have failed on its
    own).

    Excluded, same as _all_candidate_files(): ops/tests/** (a test is
    read together with the module it tests, never ledgered on its own,
    the same rule *.test.js already gets), *.test.js anywhere, any
    basename in GENERATED_JS, and any path in NON_LANE_GENERATED.
    """
    gaps = []
    for path in tracked_files:
        if not (path.endswith(".py") or path.endswith(".js")):
            continue
        if path.endswith(".test.js"):
            continue
        if path == "ops/tests" or path.startswith("ops/tests/"):
            continue
        if path in NON_LANE_GENERATED:
            continue
        base = os.path.basename(path)
        if base in GENERATED_JS:
            continue
        dirname = os.path.dirname(path)
        covered = any(dirname == lane_dir and fnmatch.fnmatch(base, pattern)
                      for lane_dir, pattern in LANES)
        if not covered:
            gaps.append(path)
    return sorted(gaps)


def git_tracked_py_js() -> list[str]:
    """Real `git ls-files '*.py' '*.js'` output, repo-relative paths.
    Never raises: a git failure (not a repo, git missing) returns [],
    which callers must read as "could not check", never as "no gaps
    exist" (CLAUDE.md 0.4, unknown is not a default).
    """
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.py", "*.js"],
            cwd=ROOT, capture_output=True, text=True, timeout=15)
    except Exception:                                            # noqa: BLE001
        return []
    if out.returncode != 0:
        return []
    return [line for line in out.stdout.splitlines() if line.strip()]


def _mention_counts() -> dict:
    """Rough secondary signal only, kept from the method this file
    replaces: how many times each candidate basename appears anywhere in
    ops/NIGHTLY-LOG.md or ops/NIGHTLY-LOG-ARCHIVE.md. Never used to claim a
    file is clean, only to rank otherwise-unledgered candidates.

    Reads both files, not just the live one, since ops/rotate_nightly_
    log.py (2026-10-14) started moving old entries verbatim into the
    archive: counting only the live file would silently undercount every
    mention older than its retention window, the exact "source corrected,
    downstream not updated" shape this repository keeps finding elsewhere.
    """
    counts = collections.defaultdict(int)
    texts = []
    for path in (LOG_PATH, LOG_ARCHIVE_PATH):
        if os.path.exists(path):
            texts.append(io.open(path, encoding="utf-8").read())
    if not texts:
        return counts
    combined = "\n".join(texts)
    for name in _all_candidate_files():
        counts[name] = len(re.findall(re.escape(name), combined))
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
    key = _normalize_key(filename)
    resolved = lane_path(key)
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
    data.setdefault("entries", {})[key] = {
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
        key = _normalize_key(args.check)
        path = lane_path(key) or key
        entry = ledger.get(key)
        if entry:
            note = ""
            touched = last_touched(lane_path(key) or "") if lane_path(key) else None
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
