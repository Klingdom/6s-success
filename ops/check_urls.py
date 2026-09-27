"""Does every URL we advertise actually resolve?

Three directories spent months answering 403 Forbidden on the live site and
were found by accident, because nothing in this repository had ever asked what
a given public URL returns. This asks, for every URL in the sitemap, which is
the list we hand to search engines and therefore the list we are promising is
real.

Two modes:

  static (default)  Resolve each sitemap URL against site/ using the same rules
                    nginx uses, so it needs no network and no running server and
                    can gate every push.
  --live BASE       Ask a real server. Used against the container in CI, and can
                    be pointed at production.

The static resolver mirrors these lines of site/nginx/default.conf:

    location / { try_files $uri $uri.html $uri/ =404; }
    location = / { try_files /index.html =404; }

so "resolves" here means what nginx will actually do, not what looks plausible.
The $uri/ step is the one that bit us: a directory with no index.html does not
fall through to a plain 404, it 403s internally, because autoindex is off.
That is treated as a failure with its own name rather than folded into
"missing", because the fix is different: an index.html or a redirect, not a
missing file.

Checked against the live config, not assumed: since 2026-08-30 the same file
also carries `error_page 403 =404 /404.html;` at server level, so that internal
403 is remapped before it ever reaches a visitor or a crawler. What actually
lands on the wire is this site's own 404 page with a 404 status, the same as
a plain missing file. The "directory-403" verdict name describes the root
cause nginx hits internally, not the status code a client receives; both
verdicts already fail this check either way, so nothing about what gets
flagged changes, only what the failure is honestly said to look like from
outside.
"""
import argparse
import io
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SITEMAP = os.path.join(SITE, "sitemap.xml")

# Paths nginx answers itself rather than from a file on disk. Each needs a
# reason, so that adding one is a decision rather than a way to silence a
# failure.
SERVED_BY_CONFIG = {
    "/stats/script.js": "proxied to Umami",
    "/stats/api/send": "proxied to Umami",
    "/subscribe": "proxied to Listmonk",
    "/rooms/": "redirected to /resources.html",
    "/deck/": "redirected to /deck.html",
}


def sitemap_urls() -> list:
    if not os.path.exists(SITEMAP):
        return []
    xml = io.open(SITEMAP, encoding="utf-8", errors="replace").read()
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def path_of(url: str) -> str:
    """The path part of an absolute or relative URL."""
    p = re.sub(r"^https?://[^/]+", "", url.strip())
    return p or "/"


def resolve(path: str) -> tuple:
    """(verdict, detail) for one path, by nginx's own rules.

    verdict is "ok", "missing", or "directory-403". "directory-403" names the
    internal try_files step nginx hits (a directory with no index.html,
    autoindex off); since 2026-08-30 the config's own
    `error_page 403 =404 /404.html;` remaps that to a 404 before it reaches
    the visitor, so the client never actually sees a bare 403. Named for the
    cause, not the wire status, and still a failure either way.
    """
    if path in SERVED_BY_CONFIG:
        return "ok", SERVED_BY_CONFIG[path]

    rel = path.lstrip("/")
    if path == "/":
        f = os.path.join(SITE, "index.html")
        return ("ok", "index.html") if os.path.exists(f) else ("missing", "no index.html")

    # try_files $uri
    direct = os.path.join(SITE, rel.replace("/", os.sep))
    if os.path.isfile(direct):
        return "ok", rel

    # try_files $uri.html
    withhtml = direct + ".html"
    if not rel.endswith("/") and os.path.isfile(withhtml):
        return "ok", rel + ".html"

    # try_files $uri/  -- a directory only resolves if it holds an index.html.
    # Without one nginx answers 403 Forbidden internally, because autoindex is
    # off; the config's own error_page directive then remaps that to a 404
    # before a visitor or crawler ever sees it (site/nginx/default.conf,
    # confirmed 2026-09-27). Still a different symptom and a different fix
    # from a genuinely missing file, so it is named separately.
    if os.path.isdir(direct):
        if os.path.isfile(os.path.join(direct, "index.html")):
            return "ok", rel.rstrip("/") + "/index.html"
        return "directory-403", "directory with no index.html"

    return "missing", "no file, no .html, no directory"


def check_static() -> int:
    urls = sitemap_urls()
    if not urls:
        print("  sitemap.xml is missing or has no <loc> entries. "
              "Nothing was checked, which is not the same as nothing being wrong.")
        return 1

    bad = []
    for u in urls:
        verdict, detail = resolve(path_of(u))
        if verdict != "ok":
            bad.append((path_of(u), verdict, detail))

    print("  checked %d sitemap URL(s) against site/" % len(urls))
    for p, verdict, detail in bad:
        print("    %-11s %-48s %s" % (verdict, p, detail))
    if bad:
        n403 = sum(1 for b in bad if b[1] == "directory-403")
        print("\n  %d URL(s) we publish to search engines do not resolve"
              "%s." % (len(bad),
                       ", %d of them a directory with no index.html "
                       "(nginx's error_page remaps the 403 to a 404 before "
                       "a visitor sees it, but there is still no page there)"
                       % n403 if n403 else ""))
        return 1
    print("  every URL in the sitemap resolves.")
    return 0


def check_live(base: str) -> int:
    base = base.rstrip("/")
    urls = sitemap_urls()
    if not urls:
        print("  no sitemap URLs to check.")
        return 1

    bad, unreachable = [], 0
    for u in urls:
        p = path_of(u)
        req = urllib.request.Request(base + p, method="HEAD",
                                     headers={"User-Agent": "6s-url-check"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:                                     # noqa: BLE001
            unreachable += 1
            continue
        if code >= 400:
            bad.append((p, code))

    looked = len(urls) - unreachable
    print("  asked %s for %d URL(s), %d could not be reached"
          % (base, looked, unreachable))
    for p, code in bad[:40]:
        print("    %s  %s" % (code, p))

    if unreachable and looked == 0:
        print("\n  nothing was measured. This is not the same as everything working.")
        return 1
    if bad:
        print("\n  %d URL(s) in the sitemap return an error." % len(bad))
        return 1
    print("  every reachable sitemap URL answers below 400.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", metavar="BASE",
                    help="ask a running server instead of resolving on disk")
    a = ap.parse_args()
    return check_live(a.live) if a.live else check_static()


if __name__ == "__main__":
    sys.exit(main())
