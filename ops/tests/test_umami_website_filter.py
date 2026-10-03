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
    """The defect that made the first version of this guard a no-op.

    Reads refuse_unsafe_sql, not umami_rows. The guard moved there 2026-10-03
    when it was extracted to be testable, and this case kept passing against
    the now-two-line umami_rows: it was checking a function that no longer
    contains a regex, which is a check that cannot fail.
    """
    src = inspect.getsource(E.refuse_unsafe_sql)
    bad = sorted({c for c in src if ord(c) < 32 and c not in "\n\r\t"})
    assert not bad, ("umami_rows() contains control byte(s) %r; a mangled "
                     "escape here makes the guard match nothing while still "
                     "reading correctly in a diff" % bad)


def _probe_blocked(sql):
    """True when the PROBE-PATH guard (not another refusal) refused it."""
    try:
        E.refuse_unsafe_sql(sql)
        return False
    except E.Unreadable as exc:
        return "/__ probe paths" in str(exc)


def case_probe_paths_unexcluded_pageview_count_is_refused():
    """2026-10-03: verifying the headless-beacon guard meant POSTing a real
    beacon from a real browser user agent, and Umami recorded it as one
    pageview and one visitor on /__guard_probe. A synthetic arrival inside the
    metric every objective rests on, created by the check protecting it. The
    raw row is kept; the readers exclude it."""
    assert _probe_blocked(
        "select count(*) filter (where event_type = 1), "
        "count(distinct session_id) from website_event "
        "where website_id = '%s'" % E.WEBSITE)


def case_probe_paths_excluded_is_allowed():
    assert not _probe_blocked(
        "select count(*) filter (where event_type = 1) from website_event "
        "where website_id = '%s' "
        "and not starts_with(coalesce(url_path, ''), '/__')" % E.WEBSITE)


def case_named_event_counts_are_not_nagged():
    """The probe carried no event name, so it cannot appear in an
    event_type = 2 query. A guard that fired there would fire where there is
    nothing to catch, which is how a guard gets switched off."""
    assert not _probe_blocked(
        "select event_name, count(distinct session_id) from website_event "
        "where website_id = '%s' and event_type = 2 group by 1" % E.WEBSITE)


def case_counting_probes_on_purpose_is_allowed():
    assert not _probe_blocked(
        "-- counts-probes" + chr(10) +
        "select count(distinct session_id) from website_event "
        "where website_id = '%s'" % E.WEBSITE)


def case_a_like_pattern_would_not_satisfy_this():
    """Belt and braces on the mistake that was actually made: the first
    version of the filter in ops/traffic_query.sh used `not like '/__%'`,
    and _ is a single-character wildcard in LIKE, so it excluded every path of
    three or more characters and reported 117 all-time pageviews against a
    real 1,047. The guard accepts any query mentioning /__, including that
    broken one, so this case documents the trap rather than catching it: the
    refusal text must name it."""
    try:
        E.refuse_unsafe_sql("select count(distinct session_id) from "
                            "website_event where website_id = '%s'"
                            % E.WEBSITE)
    except E.Unreadable as exc:
        assert "_ is a wildcard" in str(exc), (
            "the refusal does not warn that LIKE treats _ as a wildcard, "
            "which is the mistake this guard's own first fix made: %s" % exc)
    else:
        raise AssertionError("the probe guard did not fire at all")


def case_experiments_own_queries_satisfy_every_guard():
    """Not just the website_id one. Every SQL literal in experiments.py is run
    through the real refusal function; four of them had to gain the probe
    filter when it was added, and a fifth would have to if anyone adds one."""
    body = io.open(os.path.join(ROOT, "ops", "experiments.py"),
                   encoding="utf-8").read()
    pat = (r'(?:one|umami_rows)\(' + chr(34) * 3 + '(.*?)' + chr(34) * 3)
    qs = re.findall(pat, body, re.S)
    assert len(qs) >= 10, ("found only %d SQL literal(s) in experiments.py; "
                           "this case would prove nothing" % len(qs))
    refused = []
    for q in qs:
        try:
            E.refuse_unsafe_sql(q.replace("%s", "'" + E.WEBSITE + "'"))
        except E.Unreadable as exc:
            refused.append((" ".join(q.split())[:70], str(exc)[:70]))
    assert not refused, ("experiments.py contains %d query it would refuse to "
                         "run itself: %s" % (len(refused), refused[:2]))


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
