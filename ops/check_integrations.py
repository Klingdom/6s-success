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
  /subscribe            must NOT serve another business's mailing lists. This
                        used to assert the opposite: that Listmonk's public
                        form was reachable here, which it was, rendering two
                        Compassion Benchmark lists pre-ticked beside ours. A
                        404 is the correct answer until a 6S-only subscription
                        surface exists.
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


# The exact list names Listmonk rendered on /subscribe on 2026-10-04,
# alongside 6S Success Readers and all three pre-ticked. Hardcoded on purpose:
# a pattern like "any list that is not ours" would need to know every list
# this instance will ever hold, and these two are the ones measured live.
FOREIGN_LISTS = (
    "Compassion Benchmark Weekly Digest",
    "Compassion Benchmark Product",
)

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
    if status2 is None:
        # A network-level failure on this one path is "not reached", not
        # "answered wrong". Treating it as False said BROKEN on evidence
        # that only supports UNKNOWN, the exact distinction this file
        # exists to draw (CLAUDE.md 0.4: unchecked is not failing).
        record("analytics beacon rejects GET", None, "could not be reached")
    else:
        ok2 = status2 in (404, 405)
        record("analytics beacon rejects GET", ok2,
               "%s%s" % (status2, "" if ok2 else ", expected 405 or 404"))

    # THIS CHECK USED TO ASSERT THE DEFECT WAS PRESENT AND CALL IT HEALTHY.
    #
    # It fetched /subscribe and passed if the body contained the word
    # subscribe and an <html> tag, i.e. if Listmonk's public form was being
    # served under our domain. On 2026-10-04 that page was READ rather than
    # pattern-matched, and it rendered three list checkboxes with every one
    # pre-ticked, two of them belonging to a different business sharing this
    # Listmonk instance. So the healthy result this check reported for weeks
    # was a page that opted a 6S Success visitor into Compassion Benchmark's
    # two lists by default.
    #
    # The route is gone (see site/nginx/default.conf, which carries the full
    # account). What this now checks is the opposite thing: our domain must
    # not serve another business's consent checkboxes. A 404 is the correct,
    # expected answer today and reports as ok, with the honest note that email
    # capture is consequently NOT working, which it was not before either.
    status3, body3 = fetch("/subscribe")
    foreign = [name for name in FOREIGN_LISTS if name in (body3 or "")]
    if status3 is None:
        record("no foreign consent on our domain", None,
               "/subscribe could not be reached, so it was not checked")
    elif foreign:
        record("no foreign consent on our domain", False,
               "/subscribe returns %s and renders %d list(s) belonging to "
               "another business: %s. A visitor submitting this form is "
               "opted into them." % (status3, len(foreign), foreign))
    elif status3 == 404:
        record("no foreign consent on our domain", True,
               "404, as intended: no subscription surface is exposed here "
               "until a 6S-only one exists. Email capture is NOT working, "
               "by decision, not by accident (OWNER-ACTIONS item 7).")
    else:
        record("no foreign consent on our domain", True,
               "%s, %d bytes, and no other business's list names in it"
               % (status3, len(body3 or "")))

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
