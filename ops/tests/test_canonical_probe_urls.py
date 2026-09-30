#!/usr/bin/env python3
"""
Prove preflight's check_no_redirecting_probe_urls() refuses an ops/ tool that
asks production for a URL it 301s, and leaves canonical URLs alone.

WHY THIS EXISTS
---------------
Found 2026-09-29 in the persistent access log. The three most requested paths
on this entire site were all ours, and all redirects:

    2270  301  /zones/dining-room-the-beverage-or-coffee-station.html
     233  301  /rooms/kitchen.html
     232  301  /zones/entryway-the-landing-spot.html

ops/deploy_freshness.py built its probe URL from the local FILENAME, so it
asked for the .html form of a zone page about twelve times an hour;
ops/check_live_links.py named two .html paths by hand. urllib follows a 301,
so every check passed and nothing looked broken, which is why it survived.

The cost is not the round trip. While Search Console is unverified the access
log is the only instrument this site has for whether search engines read it,
and our own monitoring was producing roughly 94% of the redirects in it. A
real crawler redirect was invisible inside our own noise.

Run:  python ops/tests/test_canonical_probe_urls.py
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                          # noqa: E402


def case_zone_html_is_caught():
    out = P.check_no_redirecting_probe_urls(
        {"ops/x.py": 'fetch(BASE + "/zones/entryway-the-landing-spot.html")'})
    assert len(out) == 1 and "301s" in out[0], out


def case_room_html_is_caught():
    out = P.check_no_redirecting_probe_urls(
        {"ops/x.py": "fetch('/rooms/kitchen.html')"})
    assert len(out) == 1, out


def case_canonical_forms_are_silent():
    for url in ("/zones/entryway-the-landing-spot", "/rooms/kitchen",
                "/shop.html", "/book.html", "/", "/sitemap.xml",
                "/deck-gallery.html"):
        out = P.check_no_redirecting_probe_urls({"ops/x.py": '"%s"' % url})
        assert out == [], (url, out)


def case_every_offender_in_a_file_is_named():
    src = '"/zones/a-b.html" and "/rooms/c.html" and "/shop.html"'
    out = P.check_no_redirecting_probe_urls({"ops/x.py": src})
    assert len(out) == 2, out


def case_both_quote_styles_are_seen():
    for src in ('"/zones/a-b.html"', "'/zones/a-b.html'"):
        assert len(P.check_no_redirecting_probe_urls({"ops/x.py": src})) == 1, src


def case_the_real_ops_tree_is_clean():
    sources = {}
    for fp in sorted(glob.glob(os.path.join(ROOT, "ops", "*.py"))):
        base = os.path.basename(fp)
        if base == "preflight.py":
            continue
        sources["ops/" + base] = io.open(fp, encoding="utf-8",
                                         errors="replace").read()
    assert len(sources) > 20, len(sources)
    out = P.check_no_redirecting_probe_urls(sources)
    assert out == [], out[:3]


def case_deploy_freshness_canonicalises_a_zone_filename():
    """The specific defect: a probe URL built from a local filename."""
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import deploy_freshness as D
    assert D.canonical_path("/zones/a-b.html") == "/zones/a-b"
    assert D.canonical_path("/rooms/kitchen.html") == "/rooms/kitchen"
    # Top-level pages really are served at .html, so they must not be stripped.
    assert D.canonical_path("/shop.html") == "/shop.html"
    assert D.canonical_path("/") == "/"
    assert D.canonical_path("/zones/a-b") == "/zones/a-b"


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
