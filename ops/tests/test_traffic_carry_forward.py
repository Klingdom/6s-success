#!/usr/bin/env python3
"""
An unmeasured run must not erase a measured traffic or affiliate-trigger reading.

traffic_line() and affiliate_trigger had no carry-forward at all before this
fix: revenue_month got carry_forward() early on, but the same class of bug
sat right next to it, unfixed, for these two rows. Found 2026-09-14 when a
session with a real ssh key measured traffic_line as a real pageview/visitor
count, committed it, and this environment's own next preflight run (no ssh
key, the common case here) silently regenerated it to "**not measured**",
about to be committed over the real reading. The exact "one blind run
poisons the well" bug carry_forward()'s own docstring already names for
revenue, just never fixed here.

These cannot be run against the real dashboard without a live analytics
database or Stripe-adjacent credential, which is exactly the condition being
tested, so the rule lives in a pure function.

Run:  python ops/tests/test_traffic_carry_forward.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "ops", "dashboard.py")

# dashboard.py runs its whole pipeline at import, so the function is lifted out
# of the source rather than imported, matching test_carry_forward.py's own
# method for the same reason.
src = open(SRC, encoding="utf-8").read()
ns = {}
ns["re"] = re
m = re.search(r"^_UNMEASURED_MARK.*?(?=\n\ndef count_files)", src, re.S | re.M)
exec(m.group(0), ns)
carry = ns["_carry_last_reading"]
prefer_owner_actions = ns["_prefer_owner_actions_traffic"]


def main() -> int:
    fails = []

    # A measuring run stands on its own: no carry, and it becomes the new
    # standing answer for the next blind run to fall back on.
    r = carry("traffic_line", True, "70 pageviews from 12 visitors", {}, "2026-09-14 10:00")
    if r.get("traffic_line") != "70 pageviews from 12 visitors":
        fails.append("a measured run must report its own fresh line")
    if r.get("traffic_line_carried_from") is not None:
        fails.append("a measured run must not claim to be carried")
    if r.get("traffic_line_last_measured") != "70 pageviews from 12 visitors":
        fails.append("a measured run must record itself as the standing answer")
    if r.get("traffic_line_measured_at") != "2026-09-14 10:00":
        fails.append("a measured run must date-stamp its own reading")

    # A blind run with a real prior reading must show it, not its own ignorance.
    prev = {"traffic_line_last_measured": "70 pageviews from 12 visitors",
            "traffic_line_measured_at": "2026-09-14 10:00"}
    r = carry("traffic_line", False, "**not measured** (no ssh key)", prev, "2026-09-14 11:00")
    if "70 pageviews from 12 visitors" not in r.get("traffic_line", ""):
        fails.append("a blind run must carry the last real reading forward, "
                     f"got {r.get('traffic_line')!r}")
    if "2026-09-14 10:00" not in r.get("traffic_line", ""):
        fails.append("a carried reading must say when it was actually measured")
    if r.get("traffic_line_carried_from") != "2026-09-14 10:00":
        fails.append("a carried reading must record where it came from")

    # A second consecutive blind run must still carry the same real reading,
    # the exact case that broke revenue_month before carry_forward() existed.
    blind1 = carry("traffic_line", False, "**not measured** (no ssh key)", prev, "2026-09-14 11:00")
    blind2 = carry("traffic_line", False, "**not measured** (no ssh key)", blind1, "2026-09-14 12:00")
    if "70 pageviews from 12 visitors" not in blind2.get("traffic_line", ""):
        fails.append("a second consecutive blind run must still carry the "
                     f"real reading, got {blind2.get('traffic_line')!r}")

    # Nothing measured, ever: nothing to carry, honest "not measured" stands.
    r = carry("traffic_line", False, "**not measured** (no ssh key)", {}, "2026-09-14 10:00")
    if r.get("traffic_line") != "**not measured** (no ssh key)":
        fails.append("with nothing ever measured, the honest not-measured "
                     f"line must stand unchanged, got {r.get('traffic_line')!r}")
    if r.get("traffic_line_carried_from") is not None:
        fails.append("with nothing to carry, carried_from must stay None, "
                     "not invent a source")

    # Bootstrap: a committed state.json written before this function existed
    # holds the real reading in the plain field, with no "_last_measured"
    # sibling yet. It must still be recognised and carried, not discarded.
    old_format_prev = {"traffic_line": "945 pageviews from 74 visitors, "
                        "2026-08-20 to 2026-09-14", "generated": "2026-09-14 11:46"}
    r = carry("traffic_line", False, "**not measured** (no ssh key)",
              old_format_prev, "2026-09-14 17:53")
    if "945 pageviews from 74 visitors" not in r.get("traffic_line", ""):
        fails.append("a pre-fix committed reading with no _last_measured "
                     f"sibling must still bootstrap into a carry, got "
                     f"{r.get('traffic_line')!r}")
    # But a pre-fix file whose plain field was ITSELF an honest "not
    # measured" must not bootstrap into a fake measurement.
    old_format_blind = {"traffic_line": "**not measured** (no ssh key)",
                        "generated": "2026-09-14 11:46"}
    r = carry("traffic_line", False, "**not measured** (no ssh key)",
              old_format_blind, "2026-09-14 17:53")
    if r.get("traffic_line_carried_from") is not None:
        fails.append("a pre-fix file that was itself unmeasured must not "
                     f"bootstrap into a fake carried measurement, got {r!r}")

    # affiliate_trigger uses the same function under a different key prefix;
    # confirm the prefix is not hardcoded to "traffic_line" anywhere inside.
    prev_a = {"affiliate_trigger_last_measured": "T2 not fired: 3 of 60",
              "affiliate_trigger_measured_at": "2026-09-13 09:00"}
    r = carry("affiliate_trigger", False,
             "T2 NOT EVALUATED: analytics unreadable", prev_a, "2026-09-14 09:00")
    if "T2 not fired: 3 of 60" not in r.get("affiliate_trigger", ""):
        fails.append("affiliate_trigger must carry forward under its own "
                     f"key, got {r.get('affiliate_trigger')!r}")
    if "traffic_line" in r:
        fails.append("carrying affiliate_trigger must not also write a "
                     "traffic_line key")

    # OWNER-ACTIONS.md citation preference: found 2026-09-21, a direct
    # database read landed straight in OWNER-ACTIONS.md/GOALS.md by hand
    # (ops/traffic_query.sh, run on the VPS) without ever running this
    # generator after, so state.json's own carried figure sat stale behind
    # a fresher, worse reading the owner-facing docs already showed.

    # No citation: carry_result passes through unchanged.
    stale_carry = {"traffic_line": "80 visitors, carried from 2026-09-20 10:15",
                    "traffic_line_measured_at": "2026-09-20 10:15"}
    r = prefer_owner_actions(dict(stale_carry), "**not measured**", None)
    if r != stale_carry:
        fails.append("no citation must leave the carried reading untouched, "
                     f"got {r!r}")

    # A fresher citation overrides a stale carried reading.
    r = prefer_owner_actions(dict(stale_carry), "**not measured**",
                              ("2026-09-21 14:05", 76, 190))
    if "76 visitors across 190 visits" not in r.get("traffic_line", ""):
        fails.append("a fresher OWNER-ACTIONS.md citation must override the "
                     f"stale carried reading, got {r.get('traffic_line')!r}")
    if r.get("traffic_line_measured_at") != "2026-09-21 14:05":
        fails.append("an applied citation must date-stamp itself so the "
                     "next run can compare against it in turn")
    if "**not measured**" not in r.get("traffic_line", ""):
        fails.append("an applied citation must still show this run's own "
                     f"honest attempt, got {r.get('traffic_line')!r}")

    # A citation no fresher than what is already carried must not regress
    # a richer existing reading back to the citation's coarser numbers.
    r = prefer_owner_actions(dict(stale_carry), "**not measured**",
                              ("2026-09-19 08:00", 50, 90))
    if r != stale_carry:
        fails.append("an older-or-equal citation must not override an "
                     f"already-fresher carried reading, got {r!r}")

    # Nothing ever carried (empty carry_result): any real citation still wins.
    r = prefer_owner_actions({}, "**not measured**", ("2026-09-21 14:05", 76, 190))
    if "76 visitors across 190 visits" not in r.get("traffic_line", ""):
        fails.append("a citation must apply even when nothing was carried "
                     f"before, got {r.get('traffic_line')!r}")

    total = 14
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
