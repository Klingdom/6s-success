"""Tests for ops/checkin.py, the hourly self check-in.

Never had coverage before this file. Covers the pure logic only: carry_forward,
parse_undelivered, commits_24h_text, and next_action's branch selection,
including a real bug found reading this file cold: next_action() used a bare
truthy check on products_live, so a live catalogue reading zero (the single
worst outcome that field can report) was silently treated the same as "not
measured" and skipped the "Production is behind the repository. Deploy."
warning instead of triggering it.

A second real bug found 2026-09-23: next_action() compared products_live
against a hardcoded 159, correct the day it was written but never updated for
either of two legitimate SKU retirements since (159 to 138, then 138 to 130).
That made it report "Production is behind the repository. Deploy." every
hour for over a day straight while production genuinely matched the
repository, and it would do the same after any future retirement, since a
"<" check against a fixed number only ever tightens as the real count falls.
Fixed by taking the repository's own current count (repo_product_count(),
mirroring ops/deploy.py's function of the same name) as an explicit
want_products argument and comparing with !=, so either direction of drift
is caught and a legitimate shrink can never trip it again.

    python ops/tests/test_checkin.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import checkin  # noqa: E402


def _base_persisted(**overrides):
    p = {
        "youtube_published_last_measured": 12,
        "youtube_published": 12,
        "youtube_published_measured_at": "2026-09-12 12:00",
        "videos_vertical": 0,
        "videos_wide": 114,
        "captions": 114,
        "products_live": 159,
    }
    p.update(overrides)
    # Mirror main()'s own carry_forward: a fresh (non-None) raw reading
    # becomes the standing "last measured" value immediately. A case that
    # wants to test a *stale* carry-forward reading (this run could not
    # reach the live site at all) passes products_live_last_measured
    # itself, which this must not then overwrite.
    if "products_live_last_measured" not in overrides:
        p["products_live_last_measured"] = p["products_live"]
        p["products_live_measured_at"] = overrides.get("at", "2026-09-12 12:00")
    return p


def main() -> int:
    fails = []

    # commits_24h_text
    if checkin.commits_24h_text(7) != "7":
        fails.append("commits_24h_text(7) did not print '7'")
    if checkin.commits_24h_text(0) != "0":
        fails.append("commits_24h_text(0) treated zero as falsy")
    if checkin.commits_24h_text(None) != "unknown (shallow clone, could not verify)":
        fails.append("commits_24h_text(None) did not label itself unknown")

    # parse_undelivered
    if checkin.parse_undelivered(2, "anything") is not None:
        fails.append("parse_undelivered: exit 2 (no Desktop folder here) must "
                     "read as unmeasured, not a count")
    out = "12 file(s) exist only in build/, with no copy outside build/\n"
    if checkin.parse_undelivered(0, out) != 12:
        fails.append("parse_undelivered did not extract the real count 12")
    out0 = "every rendered file has a copy outside build/\n"
    if checkin.parse_undelivered(0, out0) != 0:
        fails.append("parse_undelivered did not read a confirmed zero as 0")
    if checkin.parse_undelivered(0, "some other message entirely") is not None:
        fails.append("parse_undelivered guessed at unrecognised output instead "
                     "of reporting unmeasured")

    # carry_forward
    now = {"at": "2026-09-12 12:00", "x": 5}
    prev = {"x_last_measured": 3, "x_measured_at": "2026-09-11 12:00"}
    got = checkin.carry_forward("x", now, prev)
    if got != (5, "2026-09-12 12:00", True):
        fails.append("carry_forward did not prefer a fresh measurement: %r" % (got,))

    now = {"at": "2026-09-12 12:00", "x": None}
    prev = {"x_last_measured": 3, "x_measured_at": "2026-09-11 12:00", "x": None}
    got = checkin.carry_forward("x", now, prev)
    if got != (3, "2026-09-11 12:00", False):
        fails.append("carry_forward did not keep the standing answer on a "
                     "blind run: %r" % (got,))

    now = {"at": "2026-09-12 12:00", "x": None}
    prev = {"x": None, "at": "2026-09-11 12:00"}
    got = checkin.carry_forward("x", now, prev)
    if got != (None, "2026-09-11 12:00", False):
        fails.append("carry_forward did not fall back to the raw previous "
                     "value when no standing answer exists yet: %r" % (got,))

    # next_action. 159 is the fixture's own "matches the repository" baseline
    # (see _base_persisted), passed explicitly as want_products so these
    # cases stay hermetic and do not depend on the real, currently-130
    # site/assets/js/data.js on disk.
    p = _base_persisted(youtube_published_last_measured=None)
    action = checkin.next_action(p, 159)
    if "no run has ever been able to reach YouTube" not in action:
        fails.append("next_action did not flag a channel never once reached")

    p = _base_persisted(youtube_published_last_measured=0, youtube_published=0)
    action = checkin.next_action(p, 159)
    if not action.startswith("Publish."):
        fails.append("next_action did not recommend publish on a confirmed "
                     "empty channel with videos ready: %r" % action)

    # The real bug: products_live == 0 is the worst possible reading of that
    # field (an empty live catalogue), not the absence of one, so it must
    # still trigger the deploy-behind warning rather than fall through to
    # the generic backlog message.
    p = _base_persisted(products_live=0)
    action = checkin.next_action(p, 159)
    if not action.startswith("Production is behind the repository. Deploy."):
        fails.append("next_action did not treat a live catalogue reading "
                     "zero as production being behind: %r" % action)

    p = _base_persisted(products_live=None, products_live_last_measured=None)
    action = checkin.next_action(p, 159)
    if "Production is behind" in action:
        fails.append("next_action claimed production was behind when "
                     "products_live was never measured at all")

    # The real bug found cold-reading this file 2026-09-26: this run has no
    # egress to the live site (products_live is None, the case on every
    # sandboxed run), but a real prior measurement already caught a
    # mismatch. The old code read the raw "products_live" field, which is
    # None here, so this warning silently never fired from any sandboxed
    # environment despite the carry-forward value existing for exactly
    # this. It must still fire, labelled with its own age.
    p = _base_persisted(products_live=None, products_live_last_measured=130,
                        products_live_measured_at="2026-09-20 10:00")
    action = checkin.next_action(p, 138)
    if not action.startswith("Production is behind the repository. Deploy."):
        fails.append("next_action did not use the carried-forward "
                     "products_live reading when this run had no egress "
                     "to the live site: %r" % action)
    if "not rechecked this run" not in action or "2026-09-20 10:00" not in action:
        fails.append("next_action's carried-forward deploy warning did not "
                     "label itself with its own age: %r" % action)

    # The matching negative: a stale carried-forward reading that agrees
    # with the current repository count must stay silent, not warn just
    # because this run could not recheck.
    p = _base_persisted(products_live=None, products_live_last_measured=138,
                        products_live_measured_at="2026-09-20 10:00")
    action = checkin.next_action(p, 138)
    if action.startswith("Production is behind"):
        fails.append("next_action warned on a stale carried-forward "
                     "reading that actually still matches the repository: "
                     "%r" % action)

    p = _base_persisted(products_live=100)
    action = checkin.next_action(p, 159)
    if not action.startswith("Production is behind the repository. Deploy."):
        fails.append("next_action did not flag production behind at 100 "
                     "of 159 live products")

    # The second real bug: a hardcoded threshold survives a legitimate
    # catalogue shrink by staying silent (100 < 159 still reads "behind"
    # forever), but the actual regression is the reverse direction going
    # uncaught by a "<" check: production sitting one full retirement's
    # worth AHEAD of a smaller repository count. 138 was correct against a
    # 138-item repository and must not be flagged; 138 against a
    # newly-130-item repository (a real retirement not yet deployed) must be.
    p = _base_persisted(products_live=138)
    action = checkin.next_action(p, 138)
    if action.startswith("Production is behind"):
        fails.append("next_action flagged production behind when live and "
                     "repository counts matched exactly: %r" % action)

    p = _base_persisted(products_live=138)
    action = checkin.next_action(p, 130)
    if not action.startswith("Production is behind the repository. Deploy."):
        fails.append("next_action did not catch a repository that shrank "
                     "(130) while production still serves the old, larger "
                     "count (138): %r" % action)
    if "138" not in action or "130" not in action:
        fails.append("next_action's deploy-behind message did not name both "
                     "the live and repository counts: %r" % action)

    # want_products unreadable (a None from repo_product_count(), e.g. no
    # site/assets/js/data.js on disk) must not be read as "any mismatch",
    # since that is unmeasured, not a known drift.
    p = _base_persisted(products_live=159)
    action = checkin.next_action(p, None)
    if "Production is behind" in action:
        fails.append("next_action claimed production was behind when the "
                     "repository's own catalogue count could not be read")

    p = _base_persisted(youtube_published=None,
                        youtube_published_measured_at="2026-09-10 09:00")
    action = checkin.next_action(p, 159)
    if ("this run could not reach YouTube to recheck" not in action
            or "2026-09-10 09:00" not in action):
        fails.append("next_action did not label a stale YouTube reading with "
                     "its own age: %r" % action)

    p = _base_persisted()
    action = checkin.next_action(p, 159)
    want = ("Work the next unblocked item in BACKLOG.md, checked against "
           "GOALS.md section 0 before starting.")
    if action != want:
        fails.append("next_action's default fell through to something else "
                     "when nothing was actionable: %r" % action)

    # repo_product_count() itself, against the real committed catalogue:
    # confirms it counts the same "sku" occurrences live_products() counts
    # remotely, just from the local file, and stays in sync with whatever
    # the catalogue currently is rather than needing a hardcoded number here.
    import re as _re
    real_data_js = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "site", "assets", "js", "data.js")
    with open(real_data_js, encoding="utf-8") as f:
        expected = len(_re.findall(r'"sku"\s*:', f.read()))
    got = checkin.repo_product_count()
    if got != expected:
        fails.append("repo_product_count() returned %r, expected %r counted "
                     "directly from the real site/assets/js/data.js" %
                     (got, expected))

    for k in checkin.OUTCOME_KEYS:
        if k not in checkin.MEANING:
            fails.append("OUTCOME_KEYS names %r, which MEANING does not "
                         "explain" % k)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 26 assertions, commits_24h_text, parse_undelivered, "
         "carry_forward, repo_product_count and next_action (including the "
         "products_live==0 fix, the hardcoded-159 fix, and the "
         "carried-forward-products_live-on-a-blind-run fix) all correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
