#!/usr/bin/env python3
"""
What people outside the United States type, and whether we answer it.

WHY THIS EXISTS
---------------
ops/keyword_demand.py asks Google's autocomplete with gl=us and US spelling,
so every query this site has ever targeted is an American one. The owner's
direction on 2026-10-23 was to attract more GLOBAL visitors, and the same day
it was found that Umami had recorded no country for any visitor since launch
(fixed in site/nginx/default.conf), so there was no evidence at all about
where demand outside the US sits or what it sounds like.

This harvests the same corpus-built seeds from Google for the four largest
English-speaking markets after the US (gb, au, ca, in), with each market's own
spelling (organise where that is the local form), and records:

  * every suggestion, the markets it appeared in, and its best rank
  * whether the US harvest (ops/keyword-demand.json) already has it
  * our best page for it, scored by ops/keyword_demand.py's own scorer, so a
    gap here means exactly what it means there

WHAT IT IS NOT
--------------
Not search volume, for the reasons ops/keyword_demand.py gives at length. A
suggestion proves people in that market type the phrase often enough to be
predicted, nothing more. Ranks are per seed and are never summed.

HOW IT REFUSES TO LIE
---------------------
It reuses keyword_demand's canary and refusal ceilings PER MARKET: a canary
is fetched for each market before and after, and if any market's canary comes
back empty, or the error or empty rate crosses the ceiling, nothing is written
and the run exits 1 saying UNCHECKED.

Run:
  python ops/keyword_demand_global.py            harvest all four markets
  python ops/keyword_demand_global.py --dry-run  6 seeds, nothing written
  python ops/keyword_demand_global.py --status   summarise the last harvest
"""
import datetime
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keyword_demand as kd  # noqa: E402

ROOT = kd.ROOT
OUT_JSON = os.path.join(ROOT, "ops", "keyword-demand-global.json")
OUT_MD = os.path.join(ROOT, "ops", "KEYWORD-DEMAND-GLOBAL.md")

# market -> (gl, Accept-Language, uses British spelling)
MARKETS = {
    "gb": ("gb", "en-GB,en;q=0.9", True),
    "au": ("au", "en-AU,en;q=0.9", True),
    "ca": ("ca", "en-CA,en;q=0.9", False),
    "in": ("in", "en-IN,en;q=0.9", True),
}

_BRIT = [(r"\borganiz", "organis")]


def localise(seed, british):
    if not british:
        return seed
    out = seed
    for pat, rep in _BRIT:
        out = re.sub(pat, rep, out)
    return out


def suggest(seed, market):
    gl, lang, _ = MARKETS[market]
    url = ("https://suggestqueries.google.com/complete/search"
           "?client=chrome&hl=en&gl=%s&q=%s" % (gl, urllib.parse.quote(seed)))
    req = urllib.request.Request(
        url, headers={"User-Agent": kd.UA, "Accept-Language": lang})
    try:
        with urllib.request.urlopen(req, timeout=kd.TIMEOUT) as resp:
            status, body = resp.status, resp.read().decode("utf-8", "replace")
    except Exception as exc:                      # reported, never hidden
        return [], "%s: %s" % (type(exc).__name__, exc)
    if status != 200:
        return [], "http %s" % status
    out, err = kd._parse_opensearch(body)
    return (out or []), err


def canary(market, sleep=True):
    seed = localise(kd.CANARY, MARKETS[market][2])
    got, err = suggest(seed, market)
    if sleep:
        time.sleep(random.uniform(*kd.DELAY))
    if err:
        return False, err
    if not got:
        return False, "canary returned an empty 200: endpoint is refusing us"
    return True, ""


def us_queries():
    try:
        with open(kd.OUT_JSON, encoding="utf-8") as fh:
            return {r["query"] for r in json.load(fh)["rows"]}
    except (OSError, ValueError, KeyError):
        return None


def norm(q):
    """Spelling-blind key, so organise and organize are one query."""
    q = re.sub(r"\s+", " ", q).strip().lower()
    return q.replace("organis", "organiz").replace("colour", "color")


def harvest(markets, seeds, sleep=True, verbose=True):
    results, attempts = {}, []
    for i, base in enumerate(seeds, 1):
        for m in markets:
            seed = localise(base, MARKETS[m][2])
            got, err = suggest(seed, m)
            outcome = "error" if err else ("empty" if not got else "ok")
            attempts.append({"seed": seed, "source": m, "count": len(got),
                             "error": err, "outcome": outcome})
            for rank, s in enumerate(got, 1):
                q = re.sub(r"\s+", " ", s).strip().lower()
                row = results.setdefault(q, {"query": q, "markets": [],
                                             "best_rank": rank, "seeds": []})
                if m not in row["markets"]:
                    row["markets"].append(m)
                row["best_rank"] = min(row["best_rank"], rank)
                if seed not in row["seeds"]:
                    row["seeds"].append(seed)
            if verbose:
                print("  [%d/%d] %s %s %s" % (i, len(seeds), m, outcome, seed))
            if sleep:
                time.sleep(random.uniform(*kd.DELAY))
    return results, attempts


def score(results):
    rooms = kd.room_names()
    inventory = kd.page_inventory(rooms)
    shaped = {}
    for q, r in results.items():
        shaped[q] = {"query": q, "sources": r["markets"],
                     "best_rank": r["best_rank"], "seeds": r["seeds"]}
    rows = kd.score_rows(shaped, rooms, inventory)
    us = us_queries()
    us_norm = None if us is None else {norm(q) for q in us}
    for row in rows:
        row["markets"] = row.pop("sources")
        row["in_us_harvest"] = (None if us_norm is None
                                else norm(row["query"]) in us_norm)
    return rows, len(inventory)


def report(payload):
    rows = payload["rows"]
    bar = chr(124)
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    new = [r for r in rows if r["in_us_harvest"] is False]
    lines = [
        "# Keyword demand outside the US",
        "",
        "Generated by `ops/keyword_demand_global.py` at %s from Google "
        "autocomplete for %s. Not search volume: a suggestion proves people "
        "in that market type it, nothing more. Coverage is words on our "
        "pages, scored by `ops/keyword_demand.py`."
        % (payload["checked_at"], ", ".join(payload["markets"])),
        "",
        "%d distinct queries: %d covered, %d partial, %d gap. "
        "**%d never appeared in the US harvest.**"
        % (len(rows), by.get("covered", 0), by.get("partial", 0),
           by.get("gap", 0), len(new)),
        "",
        "## Not in the US harvest, top-ranked first",
        "",
    ]
    cols = ["rank", "status", "markets", "query", "our best page"]
    lines.append(bar + bar.join(" %s " % c for c in cols) + bar)
    lines.append(bar + bar.join("---" for _ in cols) + bar)
    order = sorted(new, key=lambda r: (r["best_rank"], -len(r["markets"]),
                                       r["query"]))
    for r in order[:150]:
        cells = [str(r["best_rank"]), r["status"], " ".join(r["markets"]),
                 r["query"], r["best_page"] or "-"]
        lines.append(bar + bar.join(" %s " % c for c in cells) + bar)
    return "\n".join(lines) + "\n"


def status():
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, ValueError):
        print("UNCHECKED: no global harvest on disk")
        return 1
    print(report(payload)[:3000])
    return 0


def main(argv):
    flags = {"--dry-run", "--status", "--help", "-h"}
    bad = [a for a in argv if a not in flags]
    if bad:
        print("unknown argument(s): %s. Refusing to harvest." % ", ".join(bad))
        return 2
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    if "--status" in argv:
        return status()
    markets = list(MARKETS)
    seeds = kd.build_seeds()
    dry = "--dry-run" in argv
    if dry:
        seeds = seeds[:6]
    print("Harvesting %d seeds x %d markets%s"
          % (len(seeds), len(markets), " (dry run)" if dry else ""))
    canaries = {m: canary(m) for m in markets}
    for m, (ok, why) in canaries.items():
        print("  canary %s: %s" % (m, "ok" if ok else why))
    results, attempts = harvest(markets, seeds)
    for m in markets:
        ok, why = canary(m)
        if not ok:
            canaries[m] = (ok, why)
        print("  canary %s, after: %s" % (m, "ok" if ok else why))
    reason = kd.refusal_reason(attempts, canaries)
    if reason:
        print("UNCHECKED: %s. Nothing written." % reason)
        return 1
    rows, pages = score(results)
    counts = kd.outcome_counts(attempts)
    payload = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "markets": markets,
        "seeds": len(seeds),
        "attempts": len(attempts),
        "ok_attempts": counts["ok"],
        "empty_attempts": counts["empty"],
        "failed_attempts": counts["error"],
        "canaries": {k: {"ok": v[0], "note": v[1]}
                     for k, v in sorted(canaries.items())},
        "pages_checked": pages,
        "rows": rows,
    }
    if dry:
        print("dry run: nothing written")
        for r in rows[:15]:
            print("  %-8s %-11s us=%s  %s" % (r["status"],
                                             " ".join(r["markets"]),
                                             r["in_us_harvest"], r["query"]))
        return 0
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(report(payload))
    print("wrote %s and %s" % (os.path.relpath(OUT_JSON, ROOT),
                               os.path.relpath(OUT_MD, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
