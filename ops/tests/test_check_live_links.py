#!/usr/bin/env python3
"""
Prove check_live_links.py's own verdict logic says all the things it claims to
say, without needing the network or a real Stripe key.

This file exists because of the 2026-08-30 revenue outage where every payment
link on the live site was silently dead. check_live_links.py has run inside
every preflight cycle since, but every one of those runs took the same early
exit ("no Stripe credential in this environment") because this sandbox has
never held one. That means the actual dead/unknown/ok branching inside
check() has never executed here, in any cycle, and nothing has ever proven it
still says the right thing. These monkeypatch secret/fetch/all_links/
repo_links so the decision logic is exercised directly, the same shape
test_deploy_freshness.py already uses for its own no-network sibling.

Run:  python ops/tests/test_check_live_links.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_live_links as C                                  # noqa: E402

PAGE_WITH = '<a href="https://buy.stripe.com/{slug}">Buy now</a>'
PAGE_WITHOUT = "<p>nothing here</p>"
NO_REPO = {"total": 0, "dead": [], "verdict": "unknown"}


def run(secret, fetch, all_links, repo_links=None) -> dict:
    real = (C.secret, C.fetch, C.all_links, C.repo_links)
    C.secret = secret
    C.fetch = fetch
    C.all_links = all_links
    C.repo_links = repo_links or (lambda active: dict(NO_REPO))
    try:
        return C.check()
    finally:
        C.secret, C.fetch, C.all_links, C.repo_links = real


def main() -> int:
    fails = []

    r = run(lambda: None, lambda u: PAGE_WITHOUT, lambda k: {})
    if r["verdict"] != "unknown" or "credential" not in r["note"]:
        fails.append("no credential must be unknown with a credential note, "
                      f"got {r['verdict']!r} note={r['note']!r}")

    r = run(lambda: "sk_test", lambda u: None, lambda k: {"abc123": True})
    if r["verdict"] != "unknown" or r["reachable"] is not False:
        fails.append("an unreachable site must be unknown and reachable=False, "
                      f"never ok, got {r['verdict']!r} reachable={r['reachable']!r}")

    r = run(lambda: "sk_test",
            lambda u: PAGE_WITH.format(slug="abc123"),
            lambda k: {"abc123": True})
    if r["verdict"] != "ok" or r["dead"] or r["unknown"]:
        fails.append("every served link active in Stripe must be ok with no "
                      f"dead/unknown, got {r['verdict']!r} dead={r['dead']} "
                      f"unknown={r['unknown']}")

    r = run(lambda: "sk_test",
            lambda u: PAGE_WITH.format(slug="dead1"),
            lambda k: {"dead1": False})
    if r["verdict"] != "dead" or [s for s, _ in r["dead"]] != ["dead1"]:
        fails.append("a deactivated served link must be the dead verdict, "
                      f"got {r['verdict']!r} dead={r['dead']}")

    r = run(lambda: "sk_test",
            lambda u: PAGE_WITH.format(slug="ghost1"),
            lambda k: {})
    if r["verdict"] != "unknown" or [s for s, _ in r["unknown"]] != ["ghost1"]:
        fails.append("a served link absent from the Stripe account entirely "
                      f"must be unknown, got {r['verdict']!r} unknown={r['unknown']}")

    def two_slugs(u):
        return PAGE_WITH.format(slug="dead1") + PAGE_WITH.format(slug="ghost1")

    r = run(lambda: "sk_test", two_slugs, lambda k: {"dead1": False})
    if r["verdict"] != "dead":
        fails.append("a real outage must outrank an unrelated unknown slug on "
                      f"the same run, got {r['verdict']!r}")

    # repo_links() itself has never executed for real in this sandbox either,
    # since check() only reaches it after a credential exists. Run it against
    # the real repository at least once so a crash cannot hide behind the
    # early-exit path above.
    try:
        rl = C.repo_links({})
    except Exception as e:                                     # noqa: BLE001
        fails.append(f"repo_links() crashed against the real repository: "
                      f"{type(e).__name__}: {e}")
    else:
        if rl["verdict"] not in ("unknown", "all-active", "some-dead"):
            fails.append(f"repo_links() returned an unrecognised verdict "
                          f"{rl['verdict']!r}")
        if rl["total"] > 0 and rl["verdict"] == "unknown":
            fails.append("repo_links() found links but left verdict unknown, "
                          f"total={rl['total']}")

    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {7 - len(fails)} of 7 cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
