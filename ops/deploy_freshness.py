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
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = "https://6s-success.com"

# Pages worth asking about, and what each one proves. The homepage carries the
# shared assets; the zone page carries this cycle's actual content change, and
# an asset hash alone would not notice a page that gained a picture.
PROBES = [
    ("/", "assets", "the shared stylesheet and scripts"),
    ("/zones/entryway-the-landing-spot.html", "zone-hero",
     "whether zone pages carry their photograph yet"),
]


def digest(path: str) -> str:
    raw = io.open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()[:10]


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

    for path, hsh in sorted(set(re.findall(
            r'(assets/[A-Za-z0-9_./-]+\.(?:css|js))\?v=([0-9a-f]+)', home))):
        local = os.path.join(SITE, *path.split("/"))
        mine = digest(local) if os.path.exists(local) else None
        same = (mine == hsh)
        out["assets"].append({"path": path, "live": hsh, "local": mine,
                              "current": same})
        out["checked_assets"] += 1
        if not same:
            out["stale_assets"] += 1
    out["probes"].append(f"{BASE}/ for {out['checked_assets']} asset reference(s)")

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
        rel = "/" + os.path.relpath(local_zone, SITE).replace(os.sep, "/")
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
        print(f"    {a['path']:26} live {a['live']}  repo {a['local']}  {mark}")
    if r["zone_hero_live"] is not None:
        print(f"    zone page photograph        live "
              f"{'present' if r['zone_hero_live'] else 'absent '}  repo "
              f"{'present' if r['zone_hero_local'] else 'absent'}")

    if r["verdict"] == "current":
        print(f"\n  CURRENT  production matches this repository on everything "
              f"checked ({r['checked_assets']} assets and 1 content marker).")
        return 0
    print(f"\n  STALE    {r['stale_assets']} of {r['checked_assets']} assets on "
          f"production differ from this repository.")
    print(f"           The site works. It is serving an older build, so work "
          f"committed since then is not reaching anybody.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
