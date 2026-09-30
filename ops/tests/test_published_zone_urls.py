#!/usr/bin/env python3
"""
Prove preflight's check_published_zone_urls() refuses an off-site link that
needs a redirect, and one that points at a page this site does not have.

WHY THIS EXISTS
---------------
A YouTube description and a social caption are the only links this business
sends anybody. Found 2026-09-29: all 114 YouTube descriptions carried 228
links of the form /zones/<slug>.html, and all 114 social captions the same,
342 in total and not one canonical. /zones/ is extensionless-canonical here
and nginx 301s the .html form, so every outbound link published took a hop.

A redirect does not stop a click, so this could never appear as a broken link,
which is why it survived. The measured context is what makes it worth a gate:
the 12 videos already public have sent this site zero visitors in 26 days,
LinkedIn and Bluesky are the only channels that have ever produced one, and
Phil is being asked to hand-upload 102 more descriptions. Getting the link
right before that is cheaper than after.

The second half, a published slug that does not exist, is the one that would
actually hurt: a 404 in front of somebody who chose to click.

Run:  python ops/tests/test_published_zone_urls.py
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402

SLUGS = {"kitchen-the-cooking-zone", "entryway-the-landing-spot"}
BASE = "https://6s-success.com/zones/"


def case_canonical_link_is_silent():
    doc = {"a.json": '"url": "%skitchen-the-cooking-zone"' % BASE}
    assert P.check_published_zone_urls(doc, SLUGS) == []


def case_html_form_is_refused():
    doc = {"a.json": '"%skitchen-the-cooking-zone.html"' % BASE}
    out = P.check_published_zone_urls(doc, SLUGS)
    assert len(out) == 1 and "301s" in out[0], out


def case_unknown_slug_is_refused():
    doc = {"a.json": '"%snot-a-real-zone"' % BASE}
    out = P.check_published_zone_urls(doc, SLUGS)
    assert len(out) == 1 and "404" in out[0], out


def case_an_anchor_does_not_break_the_slug():
    doc = {"a.json": '"%skitchen-the-cooking-zone#sustain"' % BASE}
    assert P.check_published_zone_urls(doc, SLUGS) == []


def case_every_offender_is_named():
    doc = {"a.json": ('"%skitchen-the-cooking-zone.html" '
                      '"%sentryway-the-landing-spot.html" '
                      '"%skitchen-the-cooking-zone"') % (BASE, BASE, BASE)}
    out = P.check_published_zone_urls(doc, SLUGS)
    assert len(out) == 2, out


def case_the_real_published_artifacts_are_clean():
    zone_slugs = {os.path.basename(p)[:-len(".html")]
                  for p in glob.glob(os.path.join(ROOT, "site", "zones", "*.html"))}
    if not zone_slugs:
        print("  no zone pages here, NOT VERIFIED.")
        return
    docs = {}
    for pattern in (os.path.join(ROOT, "build", "video", "youtube", "*.json"),
                    os.path.join(ROOT, "build", "social", "captions", "*.json")):
        for fp in sorted(glob.glob(pattern)):
            docs[os.path.basename(fp)] = io.open(
                fp, encoding="utf-8", errors="replace").read()
    if not docs:
        print("  no published artifacts present here, NOT VERIFIED.")
        return
    assert len(docs) > 100, len(docs)
    out = P.check_published_zone_urls(docs, zone_slugs)
    assert out == [], out[:3]


def case_youtube_descriptions_really_carry_a_link():
    """A gate that passes because there are no links would be worthless."""
    found = 0
    for fp in glob.glob(os.path.join(ROOT, "build", "video", "youtube", "*.json")):
        d = json.load(io.open(fp, encoding="utf-8"))
        found += len(re.findall(r"https://6s-success\.com/zones/[a-z0-9-]+",
                                d.get("description") or ""))
    if not glob.glob(os.path.join(ROOT, "build", "video", "youtube", "*.json")):
        print("  no YouTube metadata here, NOT VERIFIED.")
        return
    assert found > 100, found


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
