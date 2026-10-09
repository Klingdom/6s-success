#!/usr/bin/env python3
"""
Is production actually serving what this repository contains?

THE GAP THIS CLOSES
-------------------
ops/verify_deploy.py reported 10 of 10 checks passed against 6s-success.com on
a day when production was serving a site weeks out of date: 102 zone pages had
been given a reviewed photograph and the live site had none of them. Every one
of those checks was true. The site answered 200, the legal pages loaded, a
missing path returned 404. None of them ask whether the site is current,
because "working" and "current" are different questions and only one of them
was being asked.

Meanwhile the dashboard reported "102/114 zone pages carry a reviewed picture",
measured honestly off the repository, where it is true. A reader would take
that as a fact about the website. It is a fact about a folder.

HOW IT KNOWS
------------
ops/fingerprint_assets.py already stamps every stylesheet and script reference
with a hash of that file's contents. So the live homepage states, in its own
HTML, exactly which version of each asset it expects. Comparing that to the
hash of the file on disk is a precise answer with no version endpoint, no
build metadata and nothing to keep in sync.

Line endings are normalised before hashing for the same reason the
fingerprinter does it: git rewrites them on checkout, and a digest that
disagrees between a Windows working copy and a Linux container would report
permanent staleness on a perfectly current site.

WHAT IT REFUSES TO DO
---------------------
Report freshness it could not measure. If the site cannot be reached, that is
"unknown", never "fresh". The whole reason this file exists is that a check
which cannot tell those two apart is worse than no check.

Run:  python ops/deploy_freshness.py
      python ops/deploy_freshness.py --json
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = "https://6s-success.com"

# Pages worth asking about, and what each one proves. The homepage carries the
# shared assets; the zone page carries this cycle's actual content change, and
# an asset hash alone would not notice a page that gained a picture.
PROBES = [
    ("/", "assets", "the shared stylesheet and scripts"),
    ("/zones/entryway-the-landing-spot", "zone-hero",
     "whether zone pages carry their photograph yet"),
]


# The pages asset references are discovered from. Named rather than inlined so
# ops/preflight.py's gate_checker_scope can check this list still covers every
# fingerprinted asset the site ships: the list going stale as the site grows is
# how quest.js came to be uncompared for months.
#
# Not actually every fingerprinted asset, corrected 2026-10-09: this comment
# used to claim it. site/downloads/assets/book.css is fingerprinted
# (ops/build_sample_html.py writes it, ops/fingerprint_assets.py stamps it)
# and was referenced by no page in this list, so it was never compared to
# production at all, and the sibling gate below could not catch the gap
# either, because os.path.exists() checked it at the wrong path (see
# resolve_asset_ref()). Added the one page that references it.
DISCOVERY_PAGES = ("/", "/quest.html", "/shop.html",
                   # fonts.css used to be pulled in on every page through an
                   # @import inside site.css, which this list never had to
                   # name directly because "/" already covers site.css. That
                   # @import was removed 2026-09-05 (it serialised a second
                   # request behind the first on every page); fonts.css is
                   # inlined into site.css now, but it is still its own
                   # shipped file, still directly <link>ed by invest.html
                   # and the book/print-and-play pages that use book.css
                   # instead of site.css. invest.html is the one of those
                   # still in site/ outside content/book, so it is what
                   # keeps fonts.css itself inside this list's coverage.
                   "/invest.html",
                   # The only page that references site/downloads/assets/
                   # book.css. Its href is "assets/book.css", relative to
                   # THIS page's own directory (site/downloads/), not to
                   # site/ root like every other page above; see
                   # resolve_asset_ref().
                   "/downloads/6S Success Home Edition - Sample (Chapters 1-30).html")


def resolve_asset_ref(page_rel: str, href: str) -> str:
    """The site-relative path (no leading slash) the asset `href` actually
    names, resolved against the page it was found on, the way a browser
    resolves a relative URL.

    Found 2026-10-09: every caller of this file's own asset regex used to
    join the raw match straight onto SITE, which is only correct for a page
    sitting directly in site/ (every DISCOVERY_PAGES entry, until now). The
    one page one level deeper, the downloads/ sample, writes a bare
    "assets/book.css" href that means downloads/assets/book.css on disk, not
    site/assets/book.css; the old code looked for the latter, found nothing,
    and silently treated the asset as uncovered rather than as what it
    hashes to. `href` may also carry a leading "../" (a zone or room page,
    not currently in DISCOVERY_PAGES, would), which this resolves the same
    way.
    """
    page_dir = os.path.dirname(page_rel.lstrip("/"))
    return os.path.normpath(os.path.join(page_dir, href)).replace(os.sep, "/")


# Captures the href/src text itself, including any leading "../" segments,
# so resolve_asset_ref() can resolve it against the page it was found on
# instead of assuming every page sits directly in site/ (see that function).
ASSET_REF = re.compile(
    r'((?:\.\./)*assets/[A-Za-z0-9_./-]+\.(?:css|js))\?v=([0-9a-f]+)')


def digest(path: str) -> str:
    raw = io.open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()[:10]


def canonical_path(path: str) -> str:
    """The form production actually serves 200 for.

    /rooms/ and /zones/ are extensionless-canonical: nginx 301s the .html
    form to it. Top-level pages keep .html and are served directly.

    Found 2026-09-29 in the persistent access log. This tool built its probe
    URL from the LOCAL FILENAME, so it asked for
    /zones/dining-room-the-beverage-or-coffee-station.html and took a 301
    every single time: 2,270 redirects in eight days, about twelve an hour,
    the single most requested path on the whole site. urllib follows the
    redirect so nothing was broken, which is exactly why it survived.

    The cost is not the extra round trip. The access log is the only SEO
    instrument this site has while Search Console is unverified, and our own
    monitoring was generating 94% of the redirects in it, which makes a real
    crawler redirect impossible to see.
    """
    if path.endswith(".html") and (path.startswith("/rooms/")
                                   or path.startswith("/zones/")):
        return path[:-len(".html")]
    return path


def fetch(url: str, timeout: int = 25) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "6s-freshness"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:                                         # noqa: BLE001
        return None


def check() -> dict:
    out = {"reachable": None, "assets": [], "stale_assets": 0,
           "checked_assets": 0, "zone_hero_live": None,
           "zone_hero_local": None, "verdict": "unknown", "probes": []}

    home = fetch(BASE + "/")
    out["reachable"] = home is not None
    if home is None:
        out["verdict"] = "unknown"
        return out

    # Asset references were discovered from the home page alone, which sees
    # four of them. Four more are referenced only from other pages and were
    # never compared: quest.js, quest-data.js, photos.js and shop.js. quest.js
    # is 39 KB and drives the only journey a visitor can finish while payments
    # are dead, so "production matches this repository" could have been printed
    # with the Quest arbitrarily out of date.
    #
    # These pages between them reference every fingerprinted asset the site
    # ships (gate_checker_scope in ops/preflight.py fails if a new one does
    # not). A page that cannot be fetched is skipped rather than fatal, and
    # the probe line below says how many were actually read.
    seen, read_pages = {}, []
    for rel in DISCOVERY_PAGES:
        body = home if rel == "/" else fetch(BASE + urllib.parse.quote(rel))
        if body is None:
            continue
        read_pages.append(rel)
        for href, hsh in ASSET_REF.findall(body):
            path = resolve_asset_ref(rel, href)
            seen.setdefault(path, hsh)

    for path, hsh in sorted(seen.items()):
        local = os.path.join(SITE, *path.split("/"))
        mine = digest(local) if os.path.exists(local) else None
        same = (mine == hsh)
        # Size, when it differs. "data.js differs" was reported truthfully for
        # eight days while the live file was 4 KB against 73 KB here, which is
        # the entire shop catalogue missing: 10 products live against 159. A
        # hash tells you two files are not the same and refuses to say how far
        # apart they are, and a reader cannot tell a whitespace change from a
        # file with 94 percent of its contents absent. Fetched only for assets
        # that already differ, so this costs nothing on a current deploy.
        live_bytes = repo_bytes = None
        if not same:
            body = fetch(BASE + "/" + urllib.parse.quote(path))
            if body is not None:
                live_bytes = len(body.encode("utf-8", "replace"))
            if os.path.exists(local):
                # Normalised the same way digest() does, so the comparison is
                # of content rather than of line endings.
                repo_bytes = len(io.open(local, "rb").read()
                                 .replace(b"\r\n", b"\n"))
        out["assets"].append({"path": path, "live": hsh, "local": mine,
                              "current": same, "live_bytes": live_bytes,
                              "repo_bytes": repo_bytes})
        out["checked_assets"] += 1
        if not same:
            out["stale_assets"] += 1
    out["probes"].append(
        f"{len(read_pages)} page(s) ({', '.join(read_pages)}) for "
        f"{out['checked_assets']} distinct asset reference(s)")

    # Pick the probe page from pages that actually carry the marker, rather
    # than naming one. The first attempt hard coded the Landing Spot, which is
    # one of the twelve zones whose image failed review, so the comparison was
    # absent against absent and would have read as current forever. A content
    # probe that cannot distinguish "not deployed" from "does not exist" is
    # the same defect this file was written to fix.
    marker = "zone-hero"
    have = sorted(f for f in glob.glob(os.path.join(SITE, "zones", "*.html"))
                  if marker in io.open(f, encoding="utf-8").read())
    if have:
        local_zone = have[0]
        rel = canonical_path(
            "/" + os.path.relpath(local_zone, SITE).replace(os.sep, "/"))
        out["zone_hero_local"] = True
        live_zone = fetch(BASE + rel)
        if live_zone is not None:
            out["zone_hero_live"] = marker in live_zone
            out["probes"].append(f"{BASE}{rel} for the {marker!r} marker, "
                                 f"chosen because it is one of {len(have)} "
                                 f"pages that carry one in this repository")
    else:
        out["zone_hero_local"] = False
        out["probes"].append("no local zone page carries a photograph, so that "
                             "marker was not compared")

    behind = out["stale_assets"] > 0 or (
        out["zone_hero_local"] and out["zone_hero_live"] is False)
    out["verdict"] = "stale" if behind else "current"
    return out


# STALE says production is behind. It does not say whether there is
# anything to catch up TO, and on 2026-09-30 there was not: a site change
# was pushed, its image build failed on an unrelated fault in a concurrent
# session's commit, the fix for that touched no site/** path so the
# workflow correctly declined to rebuild, and the change sat with no image
# at all. "Deploy it" is the wrong next move in that state, and it is the
# move this verdict invites, so the answer is printed beside it rather than
# left for somebody to discover. One implementation, imported from
# deploy.py, so the two tools cannot drift into disagreeing about what the
# build is doing.
from deploy import publish_state, PUBLISH_ADVICE   # noqa: E402


def main() -> int:
    r = check()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=1))
        return 0

    if not r["reachable"]:
        print(f"  UNKNOWN  {BASE} could not be reached from here, so freshness "
              f"was not measured. This is not the same as current.")
        return 0

    # Say what was looked at, always. A bare verdict is how a check that
    # examined the wrong thing goes unnoticed for weeks.
    print(f"  looked at: {'; '.join(r['probes'])}")
    for a in r["assets"]:
        mark = "same" if a["current"] else "STALE"
        size = ""
        lb, rb = a.get("live_bytes"), a.get("repo_bytes")
        if lb is not None and rb:
            ratio = ""
            if lb and rb / lb >= 1.5:
                ratio = f", {rb / lb:.0f}x smaller live"
            elif lb and lb / rb >= 1.5:
                ratio = f", {lb / rb:.0f}x larger live"
            size = f"  [{lb:,}B live vs {rb:,}B here{ratio}]"
        print(f"    {a['path']:26} live {a['live']}  repo {a['local']}  "
              f"{mark}{size}")
    if r["zone_hero_live"] is not None:
        print(f"    zone page photograph        live "
              f"{'present' if r['zone_hero_live'] else 'absent '}  repo "
              f"{'present' if r['zone_hero_local'] else 'absent'}")

    if r["verdict"] == "current":
        # zone_hero_live stays None, not True, when the marker page itself
        # could not be fetched (site reachable, that one page was not) or no
        # local page carries the marker to compare against. Either way the
        # marker was never actually confirmed, so it must not be counted as
        # checked: that is the exact "unchecked reported as checked" shape
        # this file exists to refuse.
        marker_note = " and 1 content marker" if r["zone_hero_live"] is not None else ""
        print(f"\n  CURRENT  production matches this repository on everything "
              f"checked ({r['checked_assets']} assets{marker_note}).")
        return 0
    print(f"\n  STALE    {r['stale_assets']} of {r['checked_assets']} assets on "
          f"production differ from this repository.")
    print(f"           The site works. It is serving an older build, so work "
          f"committed since then is not reaching anybody.")
    state, _run = publish_state()
    print(f"           image build for this commit: {state}")
    print(f"           {PUBLISH_ADVICE[state]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
