#!/usr/bin/env python3
"""
Prove ops/experiments.py refuses a website_event query that does not name a
website, because this Umami instance serves more than one business.

WHY THIS EXISTS
---------------
On 2026-09-24 the same missing predicate produced two confidently wrong
numbers within an hour:

  - a top-line read of "239 visitors in 30 days", a 3.5x overnight jump on a
    site whose real figure was 57 and slightly falling;
  - the zone-page figures written into DECISIONS.md D-026's checkpoint, out by
    roughly a factor of two (536 pageviews where the truth was 270).

Both were other businesses' traffic counted as ours. Both were caught only by
comparing against ops/traffic_query.sh, which has carried `website_id` from
the day it was written. The mistake was writing a fresh query beside it.

A wrong number is worse than no number, because a wrong number gets written
into a decision and then argued from. This test pins the guard that stops it,
including the escape hatch, so a genuine cross-site read stays possible and
has to say so out loud.

It also checks the regex has no control bytes in it. The first version of the
guard shipped with its word boundaries mangled into literal 0x08 backspace
characters, so it matched nothing and silently allowed the exact query it was
written to stop. It looked right in a diff and passed a syntax check.

Run:  python ops/tests/test_umami_website_filter.py
"""
import inspect
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import experiments as E                                         # noqa: E402


def _blocked(sql):
    """True when the guard (not some other failure) refused the query."""
    try:
        E.umami_rows(sql)
        return False
    except E.Unreadable as exc:
        return "serves more than one" in str(exc)
    except Exception:                                           # noqa: BLE001
        return False


def case_unfiltered_is_refused():
    assert _blocked("select count(*) from website_event "
                    "where created_at > now() - interval '30 days'")


def case_filtered_is_allowed():
    assert not _blocked(
        "select count(*) from website_event where website_id = '%s' "
        "and created_at > now() - interval '1 day'" % E.WEBSITE)


def case_declared_cross_site_is_allowed():
    """Crossing every site is legitimate; it just has to be said on purpose."""
    assert not _blocked("-- all-websites\n"
                        "select count(distinct website_id) from website_event")


def case_other_tables_are_untouched():
    assert not _blocked("select count(*) from session")


def case_substring_tables_do_not_trip_it():
    """The boundaries are real boundaries, not a substring match."""
    assert not _blocked("select count(*) from my_website_events_archive")


def case_guard_regex_has_no_control_bytes():
    """The defect that made the first version of this guard a no-op."""
    src = inspect.getsource(E.umami_rows)
    bad = sorted({c for c in src if ord(c) < 32 and c not in "\n\r\t"})
    assert not bad, ("umami_rows() contains control byte(s) %r; a mangled "
                     "escape here makes the guard match nothing while still "
                     "reading correctly in a diff" % bad)


def case_the_repositorys_own_queries_would_pass():
    """Every website_event query in ops/ must satisfy the guard it now faces."""
    offenders = []
    for name in sorted(os.listdir(os.path.join(ROOT, "ops"))):
        if not name.endswith(".py") or name == "experiments.py":
            continue
        body = io.open(os.path.join(ROOT, "ops", name),
                       encoding="utf-8", errors="replace").read()
        if re.search(r"\bwebsite_event\b", body) and "website_id" not in body:
            offenders.append(name)
    assert not offenders, ("these read website_event without ever naming a "
                           "website: %s" % ", ".join(offenders))


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
