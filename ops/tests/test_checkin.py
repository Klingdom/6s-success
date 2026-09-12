"""Tests for ops/checkin.py, the hourly self check-in.

Never had coverage before this file. Covers the pure logic only: carry_forward,
parse_undelivered, commits_24h_text, and next_action's branch selection,
including a real bug found reading this file cold: next_action() used a bare
truthy check on products_live, so a live catalogue reading zero (the single
worst outcome that field can report) was silently treated the same as "not
measured" and skipped the "Production is behind the repository. Deploy."
warning instead of triggering it.

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

    # next_action
    p = _base_persisted(youtube_published_last_measured=None)
    action = checkin.next_action(p)
    if "no run has ever been able to reach YouTube" not in action:
        fails.append("next_action did not flag a channel never once reached")

    p = _base_persisted(youtube_published_last_measured=0, youtube_published=0)
    action = checkin.next_action(p)
    if not action.startswith("Publish."):
        fails.append("next_action did not recommend publish on a confirmed "
                     "empty channel with videos ready: %r" % action)

    # The real bug: products_live == 0 is the worst possible reading of that
    # field (an empty live catalogue), not the absence of one, so it must
    # still trigger the deploy-behind warning rather than fall through to
    # the generic backlog message.
    p = _base_persisted(products_live=0)
    action = checkin.next_action(p)
    if action != "Production is behind the repository. Deploy.":
        fails.append("next_action did not treat a live catalogue reading "
                     "zero as production being behind: %r" % action)

    p = _base_persisted(products_live=None)
    action = checkin.next_action(p)
    if "Production is behind" in action:
        fails.append("next_action claimed production was behind when "
                     "products_live was never measured at all")

    p = _base_persisted(products_live=100)
    action = checkin.next_action(p)
    if action != "Production is behind the repository. Deploy.":
        fails.append("next_action did not flag production behind at 100 "
                     "of 159 live products")

    p = _base_persisted(youtube_published=None,
                        youtube_published_measured_at="2026-09-10 09:00")
    action = checkin.next_action(p)
    if ("this run could not reach YouTube to recheck" not in action
            or "2026-09-10 09:00" not in action):
        fails.append("next_action did not label a stale YouTube reading with "
                     "its own age: %r" % action)

    p = _base_persisted()
    action = checkin.next_action(p)
    want = ("Work the next unblocked item in BACKLOG.md, checked against "
           "GOALS.md section 0 before starting.")
    if action != want:
        fails.append("next_action's default fell through to something else "
                     "when nothing was actionable: %r" % action)

    for k in checkin.OUTCOME_KEYS:
        if k not in checkin.MEANING:
            fails.append("OUTCOME_KEYS names %r, which MEANING does not "
                         "explain" % k)

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: 15 cases, commits_24h_text, parse_undelivered, carry_forward "
         "and next_action (including the products_live==0 fix) all correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
