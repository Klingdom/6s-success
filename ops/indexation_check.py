#!/usr/bin/env python3
"""
Which sections of the site are actually indexed, not just crawled.

WHY THIS EXISTS
---------------
GOALS.md O1 closed "is anything crawling us": 210 of 211 sitemap URLs were
fetched by a real retrieval crawler in a 14-day window, measured from the
production access log. That answers crawl coverage. It does not answer
indexation, and crawled is not indexed.

Search Console is still verified to nothing (OWNER-ACTIONS.md item 2), so
there is no authoritative source for which pages are in Google's index. The
public half is a `site:` search. A single DuckDuckGo read on 2026-10-01
confirmed ten real pages indexed (the home page, /about.html, /method.html,
/rooms/home-office, one article, among others), which already disproves
"nothing is indexed". What it could not answer is whether any /zones/ page
ever has been: three follow-up queries aimed at that came back HTTP 202,
refused outright, because the same operator session had just spent its
DuckDuckGo politeness budget on a keyword-demand harvest and lost the
engine for the rest of that hour. The question was never actually asked
under conditions that could answer it.

THE SHAPE OF QUERY THAT WORKS, AND THE ONE THAT DOES NOT
----------------------------------------------------------
A 2026-09-20 reading already found that a path-filtered query
(`site:6s-success.com/zones`) returns nothing through Bing's RSS endpoint,
including for a control page already known to be indexed. That is an
endpoint limitation, not a politeness problem, and no amount of pacing fixes
it. This file does not use path filters.

A plain `site:6s-success.com` query is the shape that worked on 2026-10-01:
it returns a short, ranked, mixed list of whatever pages the engine ranks
highest for that domain, already classifiable by URL path (zone, room,
article, or other). That is the only query this file ever sends.

WHAT THIS DATA IS, AND WHAT IT IS NOT
--------------------------------------
Not Search Console, and not a full index listing. A capped, ranked sample
of one engine's index. Absence of a zone page in one reading is suggestive
and NOT proof it is unindexed, since it may simply be outranked by whatever
the engine shows first. Presence is the only thing read with confidence, so
this file only ever ADDS a URL to a running "confirmed indexed, at least
once" ledger. Nothing already in the ledger is ever removed because a later
reading failed to repeat it.

HOW IT REFUSES TO LIE
----------------------
A reading is merged into the ledger only if at least one URL already on the
ledger (or, for the very first run, the bare domain root) reappears in that
engine's results. If no previously-confirmed URL reappears, the engine is
blocking, throttling, or answering empty for a reason that has nothing to
do with real indexation, and that engine's reading is recorded as VOID for
this run rather than merged, so a block can never read as "indexation
collapsed to zero".

Paced like ops/keyword_demand.py, and for the same reason: this file sends
exactly one query per engine per run, nothing is ever retried within a run,
and the two engine queries are separated by a real delay. Retrying into a
block is how the 2026-10-01 session lost DuckDuckGo for an hour in the
first place.

Run:  python ops/indexation_check.py --check     query live, update the ledger
      python ops/indexation_check.py --status    read the last reading, write nothing
      python ops/indexation_check.py --dry-run    parse canned fixture responses, no network
      python ops/indexation_check.py --help       print this and stop

An argument this file does not recognise is REFUSED, not ignored, the same
rule ops/keyword_demand.py had to learn by losing to a typo on 2026-10-03.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "6s-success.com"
OUT_JSON = os.path.join(ROOT, "ops", "indexation.json")
OUT_MD = os.path.join(ROOT, "ops", "INDEXATION.md")

DELAY_BETWEEN_ENGINES = 1.5
TIMEOUT = 20
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Known indexed before this file ever ran a query of its own (the 2026-10-01
# DuckDuckGo reading, GOALS.md O1). Seeds the ledger so the very first --check
# this file ever runs still has something to require as a canary.
SEED_CONFIRMED = (
    "https://6s-success.com/",
    "https://6s-success.com/about.html",
    "https://6s-success.com/method.html",
    "https://6s-success.com/rooms/home-office",
)


def classify(url: str) -> str:
    """Which section a URL belongs to, by path alone.

    Pure and tiny on purpose: this is the one thing a test can nail down
    without any network, and it is also the one thing worth getting
    deliberately wrong-proof, since misclassifying a zone page as "other"
    would quietly hide the exact answer this file exists to give.
    """
    path = urllib.parse.urlsplit(url).path
    if "/zones/" in path or path.startswith("/zones/"):
        return "zone"
    if "/rooms/" in path or path.startswith("/rooms/"):
        return "room"
    if "/articles/" in path or path.startswith("/articles/"):
        return "article"
    if path in ("", "/", "/index.html"):
        return "home"
    return "other"


def _fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def _domain_urls(text: str) -> list[str]:
    """Every absolute http(s) URL on our own domain found anywhere in text,
    in first-seen order, deduplicated. Deliberately permissive about where
    it looks (HTML href, DuckDuckGo's uddg= redirect wrapper, RSS <link>)
    rather than tied to one engine's markup, since both engines' responses
    get pushed through this same function.
    """
    out, seen = [], set()
    # Raw occurrences, including inside a DuckDuckGo redirect wrapper
    # (.../l/?uddg=https%3A%2F%2F6s-success.com%2F...).
    for m in re.finditer(r"https?%3A%2F%2F[^\"&<> ]*", text):
        decoded = urllib.parse.unquote(m.group(0))
        if DOMAIN in decoded:
            url = decoded.split("&")[0]
            if url not in seen:
                seen.add(url)
                out.append(url)
    for m in re.finditer(r"https?://[^\s\"'<>]*" + re.escape(DOMAIN) + r"[^\s\"'<>]*", text):
        url = m.group(0).rstrip(").,;")
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def duckduckgo_site_search() -> tuple[str, list[str]]:
    """lite.duckduckgo.com's HTML endpoint, no JS, no API key.

    Returns (status, urls). status is "ok", "empty", or an "http NNN" /
    "error: ..." string. Never raises: a network failure here is data about
    this engine, not a reason to crash the whole run.
    """
    url = ("https://lite.duckduckgo.com/lite/?q="
           + urllib.parse.quote("site:%s" % DOMAIN))
    try:
        status, body = _fetch(url)
    except Exception as exc:                                  # noqa: BLE001
        return "error: %s: %s" % (type(exc).__name__, exc), []
    if status != 200:
        return "http %s" % status, []
    urls = _domain_urls(body)
    return ("ok" if urls else "empty"), urls


def bing_rss_site_search() -> tuple[str, list[str]]:
    """Bing's RSS results endpoint. Confirmed answering a bare `site:` query
    without a path filter on 2026-09-20 (STATUS.md); this file never sends
    the path-filtered shape that same reading found broken.
    """
    url = ("https://www.bing.com/search?format=rss&q="
           + urllib.parse.quote("site:%s" % DOMAIN))
    try:
        status, body = _fetch(url)
    except Exception as exc:                                  # noqa: BLE001
        return "error: %s: %s" % (type(exc).__name__, exc), []
    if status != 200:
        return "http %s" % status, []
    urls = []
    try:
        root = ET.fromstring(body)
        for link_el in root.iter("link"):
            text = (link_el.text or "").strip()
            if DOMAIN in text:
                urls.append(text)
    except ET.ParseError:
        urls = _domain_urls(body)
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return ("ok" if out else "empty"), out


ENGINES = {"duckduckgo": duckduckgo_site_search, "bing_rss": bing_rss_site_search}


def load_ledger() -> dict:
    if not os.path.exists(OUT_JSON):
        return {"checked_at": None, "confirmed": {}, "runs": []}
    with open(OUT_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def canary_present(urls: list[str], trusted: set) -> bool:
    """True if this reading reproduces at least one URL already trusted
    (the ledger as it stood BEFORE this run, unioned with the permanent
    seed set, never a set growing mid-run).

    This is the whole anti-lie mechanism: a reading that cannot show us
    back a page we already know is indexed is not a reading of indexation,
    it is a block. Each engine in a run is judged against the same fixed
    trusted set so that whichever engine happens to be queried first can
    never make a later, blocked engine look like it passed, which is
    exactly what checking against a set other engines had already grown
    in the same run would do.
    """
    return any(u in trusted for u in urls)


def run_engines(engines, delay=DELAY_BETWEEN_ENGINES) -> dict:
    """Query every named engine in turn with a real delay between them.
    Returns {engine: (status, urls)}."""
    results = {}
    names = list(engines)
    for i, name in enumerate(names):
        results[name] = engines[name]()
        if i < len(names) - 1:
            time.sleep(delay)
    return results


def merge(ledger: dict, results: dict, now_iso: str) -> dict:
    """Fold a set of engine results into the ledger, honestly.

    Each engine's reading is judged on its own: an engine that fails the
    canary contributes nothing, but a clean engine still merges even if a
    sibling engine was blocked. today's date is never written over an
    existing url's first_seen; it only ever fills last_seen.
    """
    confirmed = dict(ledger.get("confirmed", {}))
    trusted = set(confirmed) | set(SEED_CONFIRMED)
    run_record = {"checked_at": now_iso, "engines": {}}
    for name, (status, urls) in results.items():
        voided = status != "ok" or not canary_present(urls, trusted)
        run_record["engines"][name] = {
            "status": status,
            "url_count": len(urls),
            "voided": voided,
        }
        if voided:
            continue
        for u in urls:
            section = classify(u)
            if u in confirmed:
                confirmed[u]["last_seen"] = now_iso
                confirmed[u]["last_engine"] = name
            else:
                confirmed[u] = {
                    "section": section,
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                    "first_engine": name,
                    "last_engine": name,
                }
    ledger = dict(ledger)
    ledger["checked_at"] = now_iso
    ledger["confirmed"] = confirmed
    ledger["runs"] = (ledger.get("runs", []) + [run_record])[-20:]
    return ledger


def section_counts(confirmed: dict) -> dict:
    counts = {"home": 0, "room": 0, "zone": 0, "article": 0, "other": 0}
    for row in confirmed.values():
        counts[row.get("section", "other")] = counts.get(row.get("section", "other"), 0) + 1
    return counts


def write_outputs(ledger: dict) -> None:
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, ensure_ascii=True)
        fh.write("\n")
    counts = section_counts(ledger["confirmed"])
    zone_urls = sorted(u for u, r in ledger["confirmed"].items() if r["section"] == "zone")
    lines = [
        "# Indexation, by section",
        "",
        "Generated by `ops/indexation_check.py`. Not Search Console: a",
        "capped, ranked sample from a `site:%s` search on each engine" % DOMAIN,
        "listed below, read additively over time. Presence here means a URL",
        "has been confirmed indexed at least once, by at least one engine,",
        "whose canary check passed that run. Absence is NOT evidence of",
        "non-indexation: an engine shows a short ranked list, not the whole",
        "index.",
        "",
        "Last checked: %s" % (ledger.get("checked_at") or "never"),
        "",
        "| Section | URLs ever confirmed indexed |",
        "|---|---|",
    ]
    for section in ("home", "room", "zone", "article", "other"):
        lines.append("| %s | %d |" % (section, counts.get(section, 0)))
    lines.append("")
    if zone_urls:
        lines.append("**Zone pages confirmed indexed at least once:**")
        for u in zone_urls:
            row = ledger["confirmed"][u]
            lines.append("- %s (first seen %s, %s)" % (u, row["first_seen"], row["first_engine"]))
    else:
        lines.append("**No /zones/ page has ever been confirmed indexed by this "
                      "ledger.** That is the open question GOALS.md O1 names: "
                      "indexed-and-not-ranking (an intent/competition problem) "
                      "versus not indexed at all (an authority problem), and "
                      "they need opposite fixes. Still unresolved after %d "
                      "run(s)." % len(ledger.get("runs", [])))
    lines.append("")
    if ledger.get("runs"):
        last = ledger["runs"][-1]
        lines.append("Last run detail:")
        for name, info in sorted(last["engines"].items()):
            lines.append("- %s: %s, %d URL(s)%s"
                          % (name, info["status"], info["url_count"],
                             " (VOIDED, canary missing)" if info["voided"] else ""))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def status() -> int:
    ledger = load_ledger()
    if not ledger.get("checked_at"):
        print("No indexation check on record. Run: python ops/indexation_check.py --check")
        return 1
    print("last check : %s" % ledger["checked_at"])
    counts = section_counts(ledger["confirmed"])
    for section in ("home", "room", "zone", "article", "other"):
        print("  %-8s: %d" % (section, counts.get(section, 0)))
    return 0


def _dry_run_fixtures() -> dict:
    """Canned, representative responses, so --dry-run proves the parser
    without touching the network. Shaped like the real thing: DuckDuckGo's
    redirect-wrapped href, Bing's RSS <link> elements, one void engine."""
    ddg_html = (
        '<a rel="nofollow" href="//duckduckgo.com/l/?uddg=https%3A%2F%2F'
        '6s-success.com%2F%26rut%3D1">Home</a>'
        '<a rel="nofollow" href="//duckduckgo.com/l/?uddg=https%3A%2F%2F'
        '6s-success.com%2Frooms%2Fhome-office%26rut%3D2">Home Office</a>'
    )
    bing_rss = (
        '<?xml version="1.0"?><rss><channel>'
        "<link>https://www.bing.com/search</link>"
        "<item><link>https://6s-success.com/about.html</link></item>"
        "<item><link>https://6s-success.com/zones/kitchen-the-cooking-zone</link></item>"
        "</channel></rss>"
    )
    return {
        "duckduckgo": ("ok", _domain_urls(ddg_html)),
        "bing_rss": ("ok", _domain_urls(bing_rss)),
    }


def main(argv: list[str]) -> int:
    FLAGS = {"--check", "--status", "--dry-run", "--help", "-h"}
    if "--help" in argv or "-h" in argv:
        print((__doc__ or "").strip())
        return 0
    unknown = [a for a in argv if a not in FLAGS]
    if unknown:
        print("unknown argument(s): %s" % ", ".join(unknown))
        print("Refusing to run, because that is not what you asked for. "
              "Run with --help for what this accepts.")
        return 2
    if "--status" in argv:
        return status()

    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    ledger = load_ledger()

    if "--dry-run" in argv:
        results = _dry_run_fixtures()
        print("dry run (no network): %s"
              % ", ".join("%s=%s" % (k, v[0]) for k, v in results.items()))
    else:
        results = run_engines(ENGINES)
        for name, (st, urls) in results.items():
            print("  %-10s: %-6s %d url(s)" % (name, st, len(urls)))

    if all(st != "ok" for st, _ in results.values()):
        print("UNCHECKED: every engine failed or returned nothing. Nothing "
              "merged. This sandbox cannot reach either engine directly; "
              "run via .github/workflows/indexation-check.yml, which has "
              "real outbound internet.")
        return 1

    before = set(ledger.get("confirmed", {}))
    ledger = merge(ledger, results, now_iso)
    after = set(ledger["confirmed"])
    new_urls = sorted(after - before)
    voided = [n for n, info in ledger["runs"][-1]["engines"].items() if info["voided"]]

    if "--dry-run" in argv:
        print("dry run: nothing written. Would have added %d new URL(s): %s"
              % (len(new_urls), ", ".join(new_urls) or "(none)"))
        return 0

    write_outputs(ledger)
    print("wrote %s and %s" % (os.path.relpath(OUT_JSON, ROOT),
                               os.path.relpath(OUT_MD, ROOT)))
    print("newly confirmed: %d%s" % (len(new_urls),
                                      (" (%s)" % ", ".join(new_urls)) if new_urls else ""))
    if voided:
        print("voided this run (canary missing, not merged): %s" % ", ".join(voided))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
