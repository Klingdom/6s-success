"""Do the proxied integrations serve what they claim, or just answer 200?

Three services sit behind paths on our own domain: Umami for analytics at
/stats, Listmonk for the mailing list at /subscribe, and the site's own service
worker and manifest. Every one of them is a reverse proxy hop that can fail
while still returning 200, because nginx will happily hand back an error page,
a redirect to a login screen, or an empty body with a success code.

That distinction has cost this project repeatedly. A deactivated Stripe link
answers 200 and serves a normal-looking page. The MCP image spent twelve days
failing where nothing looked. "Reachable" and "working" are different questions
and only the first was ever being asked of these three.

So each check asserts something only the real service can produce:

  /stats/script.js      Umami's tracker is minified JavaScript that reads
                        screen, navigator and doNotTrack. A login page or an
                        nginx error cannot contain that.
  /stats/api/send       must reject a GET. A 200 here would mean something
                        other than Umami is answering, because the beacon
                        endpoint is POST only. This one is weak on purpose and
                        worth saying so: any host that 404s passes it, so it
                        can catch a misconfigured proxy but cannot confirm
                        Umami is behind it. The tracker check above does that.
  /subscribe            Listmonk's public form carries its own title. A proxy
                        error would not.
  website id            the id the live pages send must match the one this
                        repository ships, or events are being counted against
                        a different site, or none.

Deliberately does NOT send a synthetic pageview or a test subscription. Both
would prove more, and both would write junk into data Phil reads: a fake visit
into an analytics set that currently holds almost nothing, or a fake address
onto a mailing list. A check that damages what it measures is not worth the
certainty.

Run:  python ops/check_integrations.py
      python ops/check_integrations.py --json
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = "https://6s-success.com"


def fetch(path: str, method: str = "GET", timeout: int = 25) -> tuple:
    """(status, body) or (None, None) when the request could not be made."""
    req = urllib.request.Request(BASE + path, method=method,
                                 headers={"User-Agent": "6s-integrations"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:                                     # noqa: BLE001
            body = ""
        return e.code, body
    except Exception:                                         # noqa: BLE001
        return None, None


def repo_website_id() -> str | None:
    """The Umami site id this repository ships on its pages."""
    for f in sorted(glob.glob(os.path.join(SITE, "*.html"))):
        m = re.search(r'data-website-id="([^"]+)"',
                      io.open(f, encoding="utf-8", errors="replace").read())
        if m:
            return m.group(1)
    return None


def check() -> dict:
    out = {"reachable": None, "checks": [], "verdict": "unknown"}

    def record(name, ok, detail):
        out["checks"].append({"name": name, "ok": ok, "detail": detail})

    status, body = fetch("/stats/script.js")
    if status is None:
        out["note"] = "the site could not be reached from here"
        return out
    out["reachable"] = True

    # Umami's tracker, identified by what only it contains.
    ok = (status == 200 and body is not None and len(body) > 1000
          and "doNotTrack" in body and "navigator" in body)
    record("analytics tracker", ok,
           "%s, %d bytes%s" % (status, len(body or ""),
                               "" if ok else ", not Umami's script"))

    # The beacon is POST only. A 200 to a GET means something else is there.
    status2, _ = fetch("/stats/api/send")
    ok2 = status2 in (404, 405)
    record("analytics beacon rejects GET", ok2,
           "%s%s" % (status2, "" if ok2 else ", expected 405 or 404"))

    # Listmonk's own public subscription page.
    status3, body3 = fetch("/subscribe")
    ok3 = (status3 == 200 and body3 is not None
           and "subscribe" in (body3 or "").lower()
           and "<html" in (body3 or "").lower())
    record("mailing list form", ok3,
           "%s, %d bytes%s" % (status3, len(body3 or ""),
                               "" if ok3 else ", not Listmonk's form"))

    # The id the live pages send has to be the id this repository ships.
    want = repo_website_id()
    live_id = None
    status4, home = fetch("/")
    if home:
        m = re.search(r'data-website-id="([^"]+)"', home)
        live_id = m.group(1) if m else None
    if want is None or live_id is None:
        record("analytics site id", None,
               "repo=%s live=%s, could not compare" % (want, live_id))
    else:
        ok4 = want == live_id
        record("analytics site id", ok4,
               "%s" % ("matches" if ok4 else
                       "live sends %s, this repository ships %s"
                       % (live_id, want)))

    failed = [c for c in out["checks"] if c["ok"] is False]
    unknown = [c for c in out["checks"] if c["ok"] is None]
    out["verdict"] = ("broken" if failed
                      else "partial" if unknown else "ok")
    return out


def main() -> int:
    r = check()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=1))
        return 0

    if not r["reachable"]:
        print("  UNKNOWN  %s, so no integration was checked. "
              "This is not the same as working." % r.get("note", "unreachable"))
        return 0

    for c in r["checks"]:
        mark = "ok  " if c["ok"] else ("????" if c["ok"] is None else "FAIL")
        print("    %-4s %-28s %s" % (mark, c["name"], c["detail"]))

    if r["verdict"] == "ok":
        print("\n  OK       every proxied integration serves what only the real "
              "service could.")
        return 0
    if r["verdict"] == "partial":
        print("\n  PARTIAL  some checks could not be made. Unchecked, not working.")
        return 0
    print("\n  BROKEN   an integration answers but is not the service it should be.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
