#!/usr/bin/env python3
"""
Prove check_integrations.py tells "not reached" apart from "answered wrong"
on every check, not just the first one.

Found 2026-09-12: the beacon check (/stats/api/send) and the mailing-list
check (/subscribe) both folded a fetch() failure (None status, meaning the
request never got an answer at all) into the same False the code uses for a
real wrong answer. A single flaky hop on just one of those two paths, while
the site is otherwise reachable, printed "BROKEN, an integration answers but
is not the service it should be" on evidence that only supports "could not
be reached". CLAUDE.md 0.4: unknown must never be reported as failing. The
site-id check already got this right (ok=None, "could not compare"); the fix
makes the other two follow the same pattern. Monkeypatches fetch() so this
exercises the real branching without touching the network.

Run:  python ops/tests/test_check_integrations.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_integrations as C                                # noqa: E402

UMAMI_JS = "x" * 1500 + "doNotTrack navigator"
LISTMONK_PAGE = "<html><body>Subscribe to our list</body></html>"
HOME_PAGE = '<html data-website-id="abc-123">home</html>'


def run(responses: dict, repo_id="abc-123") -> dict:
    """responses maps path -> (status, body), defaulting to (None, None)."""
    real_fetch, real_id = C.fetch, C.repo_website_id

    def fake_fetch(path, method="GET", timeout=25):
        return responses.get(path, (None, None))

    C.fetch = fake_fetch
    C.repo_website_id = lambda: repo_id
    try:
        return C.check()
    finally:
        C.fetch, C.repo_website_id = real_fetch, real_id


def by_name(r, name):
    return next(c for c in r["checks"] if c["name"] == name)


def main() -> int:
    fails = []

    # The exact bug: everything reachable except one flaky hop on the beacon
    # path. Must read as partial/unknown, never broken/false.
    r = run({
        "/stats/script.js": (200, UMAMI_JS),
        "/stats/api/send": (None, None),
        "/subscribe": (200, LISTMONK_PAGE),
        "/": (200, HOME_PAGE),
    })
    c = by_name(r, "analytics beacon rejects GET")
    if c["ok"] is not None:
        fails.append(f"a fetch() failure on the beacon path must record "
                      f"ok=None, got ok={c['ok']!r}")
    if r["verdict"] == "broken":
        fails.append("a single unreachable hop must never read as BROKEN, "
                      f"got verdict={r['verdict']!r}")
    if r["verdict"] != "partial":
        fails.append(f"expected partial verdict, got {r['verdict']!r}")

    # Same bug, on the mailing-list path instead.
    r = run({
        "/stats/script.js": (200, UMAMI_JS),
        "/stats/api/send": (404, ""),
        "/subscribe": (None, None),
        "/": (200, HOME_PAGE),
    })
    c = by_name(r, "mailing list form")
    if c["ok"] is not None:
        fails.append(f"a fetch() failure on /subscribe must record ok=None, "
                      f"got ok={c['ok']!r}")
    if r["verdict"] != "partial":
        fails.append(f"expected partial verdict, got {r['verdict']!r}")

    # A real wrong answer (not a fetch failure) on the same two checks must
    # still fail loudly. The fix must not blunt a genuine defect into unknown.
    r = run({
        "/stats/script.js": (200, UMAMI_JS),
        "/stats/api/send": (200, "ok"),          # should have rejected GET
        "/subscribe": (200, "<html>nothing to do with a list</html>"),
        "/": (200, HOME_PAGE),
    })
    if by_name(r, "analytics beacon rejects GET")["ok"] is not False:
        fails.append("a 200 answer to the beacon's GET is a real defect and "
                      "must still record ok=False")
    if by_name(r, "mailing list form")["ok"] is not False:
        fails.append("a page with no subscribe content is a real defect and "
                      "must still record ok=False")
    if r["verdict"] != "broken":
        fails.append(f"a genuine wrong answer must still read as broken, "
                      f"got {r['verdict']!r}")

    # Everything genuinely fine reads as ok.
    r = run({
        "/stats/script.js": (200, UMAMI_JS),
        "/stats/api/send": (405, ""),
        "/subscribe": (200, LISTMONK_PAGE),
        "/": (200, HOME_PAGE),
    })
    if r["verdict"] != "ok":
        fails.append(f"a fully working set of integrations must read ok, "
                      f"got {r['verdict']!r}")

    # The site being unreachable at all must still short-circuit to unknown,
    # never reach the per-check logic this fix touched.
    r = run({})
    if r["reachable"] is not None or r["verdict"] != "unknown":
        fails.append("an unreachable site must stay reachable=None, "
                      f"verdict=unknown, got reachable={r['reachable']!r} "
                      f"verdict={r['verdict']!r}")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {5 - len(fails)} of 5 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
