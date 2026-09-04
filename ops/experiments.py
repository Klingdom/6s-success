#!/usr/bin/env python3
"""
The experiment registry, the arithmetic that says whether one can run yet, and
the queries that answer the ones that are only counting.

WHY THE ARITHMETIC IS THE POINT
-------------------------------
Asking for experiments usually means asking for a split test. At this site's
traffic a split test cannot produce a usable answer, and the failure mode is not
"no result", it is a result that looks real. Two arms, four conversions, one arm
has three of them: that is a 75 percent win with a confidence interval spanning
almost the whole range, and somebody reads it as a decision.

So this file will not let an experiment be declared started without first
printing how many visitors it needs and how long that takes at the traffic
actually observed. If the answer is longer than the business has, it says so.

WHAT AN EXPERIMENT NEEDS TO BE REAL
-----------------------------------
CLAUDE.md section 16 asks for a hypothesis in the form: because we observed X,
we believe Y will improve Z for W because R. Every entry here carries that
shape, plus a primary metric, a guardrail, a stopping rule decided in advance,
and a decision recorded afterwards including the losses. A losing experiment
that was recorded is worth more than a winning one that was not.

WHY THIS FILE NOW TALKS TO THE DATABASE
---------------------------------------
It used to print, for every experiment, "blocked: read access to Umami". That
sentence was true when it was written and had been false for days by the time
anybody re-read it. `ops/traffic_query.sh` reads the Umami database directly
over ssh, and has since the API token was found expired; nothing ever told the
registry. Two experiments that needed no work at all sat marked blocked, and a
blocker nobody re-tests is indistinguishable from a decision not to do the work.

So blockers are no longer sentences. They are checks, listed in
ops/experiments.json, and this file runs them. `umami_read` is satisfied by
actually reading the database now. `event_flowing` is satisfied by that event
existing in it. `min_daily_visitors` is satisfied by the measured rate. A
blocker can therefore clear itself, which is the whole point.

THE ONE RULE THIS FILE MUST NOT BREAK
-------------------------------------
CLAUDE.md section 0.4. If the read did not happen, every number below is
UNCHECKED, and unchecked is printed as loudly as failed. It is never printed as
zero, and it is never quietly replaced by the last thing somebody typed into
the JSON. The specific way this goes wrong here is documented in
ops/traffic_query.sh: `docker exec` without `-i` returns silently empty, which
looks exactly like a site nobody visits. Every query below therefore ends with
a sentinel row, and a result without that sentinel is treated as a failed read
rather than as an empty one.

Run:  python ops/experiments.py
      python ops/experiments.py --offline          (skip the read, say so)
      python ops/experiments.py --answer EXP-001   (just that one)
      python ops/experiments.py --record           (write the readings back)
      python ops/experiments.py --power 0.02 0.03  (baseline, target)
"""
from __future__ import annotations

import collections
import datetime
import io
import json
import math
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "ops", "experiments.json")
SHOP = os.path.join(ROOT, "site", "shop.html")

# Same target ops/traffic_query.sh uses. Overridable so this is testable and so
# a moved container does not mean editing code.
SSH_HOST = os.environ.get("UMAMI_SSH_HOST", "root@187.77.25.50")
SSH_KEY = os.environ.get("UMAMI_SSH_KEY",
                         os.path.expanduser("~/.ssh/6s_deploy"))
CONTAINER = os.environ.get("UMAMI_DB_CONTAINER",
                           "umami-analytics-vi0p-umami-db-1")
WEBSITE = os.environ.get("UMAMI_WEBSITE_ID",
                         "f1fc5160-4473-422d-a89e-73ff6cbdca7a")

# A row psql can only print if it reached the end of the script. Its absence
# means the read failed, however plausible the rest of the output looks.
SENTINEL = "__6S_UMAMI_READ_OK__"


class Unreadable(Exception):
    """The database could not be read. Not "there was no data": not read."""


# --------------------------------------------------------------------- read

def umami_rows(sql: str, timeout: int = 60) -> list[list[str]]:
    """Run read-only SQL against Umami's Postgres and return split rows.

    SELECT only. Nothing in this repository has any business writing to the
    analytics database, and a tool that could would eventually be asked to.
    """
    stripped = re.sub(r"--[^\n]*", " ", sql).strip().lower()
    for banned in ("insert", "update", "delete", "drop", "alter", "truncate",
                   "create", "grant", "copy"):
        if re.search(r"\b%s\b" % banned, stripped):
            raise Unreadable("refusing to run a %s against the analytics "
                             "database; this reader is SELECT only" % banned)

    if not os.path.exists(SSH_KEY):
        raise Unreadable("no ssh key at %s, so the database was not reached"
                         % SSH_KEY)

    remote = ("docker exec -i %s psql -U umami -d umami -At -F'|' "
              "-v ON_ERROR_STOP=1" % CONTAINER)
    script = sql.rstrip().rstrip(";") + ";\nselect '%s';\n" % SENTINEL

    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20",
             "-i", SSH_KEY, SSH_HOST, remote],
            input=script.encode("utf-8"),
            capture_output=True, timeout=timeout)
    except FileNotFoundError:
        raise Unreadable("no ssh client on this machine")
    except subprocess.TimeoutExpired:
        raise Unreadable("the database did not answer within %ss" % timeout)

    out = r.stdout.decode("utf-8", "replace").splitlines()
    err = r.stderr.decode("utf-8", "replace").strip().splitlines()

    if not out or out[-1].strip() != SENTINEL:
        why = err[-1] if err else ("exit %s, no output at all" % r.returncode)
        raise Unreadable("the query did not complete (%s). An empty result "
                         "here is NOT zero traffic; it is an unread database."
                         % why[:200])

    return [ln.split("|") for ln in out[:-1] if ln != ""]


def one(sql: str, default=None):
    rows = umami_rows(sql)
    return rows[0] if rows else default


W = "'%s'" % WEBSITE


# ---------------------------------------------------------------- sku lookup

def plink_to_sku() -> dict:
    """Resolve Stripe payment link ids to SKUs from the generated catalogue.

    measure.js used to carry a hand-typed table of four link ids. Stripe
    reissues links, so all four went stale at once on 2026-08-27, and seven of
    the nine buy-clicks ever recorded came back sku "unknown" simply because
    the link clicked was not one of those four. site/shop.html's product schema
    is regenerated whenever the links are, and carries all 155.
    """
    if not os.path.exists(SHOP):
        return {}
    s = io.open(SHOP, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"buy\.stripe\.com/([A-Za-z0-9]+)", s):
        before = s[max(0, m.start() - 1500):m.start()]
        skus = re.findall(r'"sku":\s*"([A-Za-z0-9_-]+)"', before)
        if skus:
            out[m.group(1)] = skus[-1]
    return out


# ------------------------------------------------------------------- powering

def sample_size(p1: float, p2: float, power: float = 0.8,
                alpha: float = 0.05) -> int:
    """Visitors PER ARM for a two proportion test.

    Standard normal approximation. It is deliberately not clever: the point of
    printing it is to make the number visible, and at the magnitudes involved
    here no refinement changes the conclusion.
    """
    if p1 <= 0 or p2 <= 0 or p1 >= 1 or p2 >= 1 or p1 == p2:
        return 0
    z_a = 1.959964            # two sided, alpha 0.05
    z_b = 0.8416212           # power 0.80
    pbar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * pbar * (1 - pbar))
           + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / ((p2 - p1) ** 2))


def load() -> dict:
    if os.path.exists(REG):
        return json.load(io.open(REG, encoding="utf-8"))
    return {"observed_daily_visitors": None, "experiments": []}


# --------------------------------------------------------------------- facts

Facts = collections.namedtuple("Facts", "traffic events read_error")


def gather() -> Facts:
    """Everything the checks and the answers need, in as few round trips as the
    questions allow. Either it all reads or none of it is claimed."""
    try:
        t = one("""
            select count(*) filter (where event_type = 1),
                   count(distinct session_id),
                   count(distinct visit_id),
                   to_char(min(created_at), 'YYYY-MM-DD'),
                   to_char(max(created_at), 'YYYY-MM-DD')
            from website_event where website_id = %s
        """ % W)
        t30 = one("""
            select count(*) filter (where event_type = 1),
                   count(distinct session_id), count(distinct visit_id)
            from website_event where website_id = %s
              and created_at > now() - interval '30 days'
        """ % W)
        t7 = one("""
            select count(*) filter (where event_type = 1),
                   count(distinct session_id), count(distinct visit_id)
            from website_event where website_id = %s
              and created_at > now() - interval '7 days'
        """ % W)
        ev = umami_rows("""
            select event_name, count(*), count(distinct session_id)
            from website_event
            where website_id = %s and event_type = 2
            group by 1 order by 2 desc
        """ % W)
    except Unreadable as e:
        return Facts(None, None, str(e))

    traffic = {
        "pageviews": int(t[0]), "visitors": int(t[1]), "visits": int(t[2]),
        "first": t[3], "last": t[4],
        "pageviews_30d": int(t30[0]), "visitors_30d": int(t30[1]),
        "visits_30d": int(t30[2]),
        "pageviews_7d": int(t7[0]), "visitors_7d": int(t7[1]),
        "visits_7d": int(t7[2]),
    }
    traffic["daily_visitors_30d"] = round(traffic["visitors_30d"] / 30.0, 1)
    events = {r[0]: {"n": int(r[1]), "visitors": int(r[2])} for r in ev}
    return Facts(traffic, events, None)


# ------------------------------------------------------------------- blockers

def resolve_blockers(exp: dict, f: Facts) -> tuple[str, list[str]]:
    """Return (state, reasons). state is clear, blocked or unchecked.

    unchecked is a real answer and must never be collapsed into either of the
    others. A check that could not run has not passed and has not failed.
    """
    checks = exp.get("blocked_on") or []
    if isinstance(checks, str):
        # An old-style hand-written sentence. It cannot be re-tested, which is
        # exactly the defect that let "blocked: read access to Umami" survive
        # for days after it stopped being true, so say so rather than trust it.
        return "unchecked", [
            "this experiment still carries a hand-written blocker (%r) that "
            "nothing can re-test. Convert it to a check." % checks]
    if not checks:
        return "clear", []

    needs_db = any(c.get("check") in ("umami_read", "event_flowing",
                                      "min_daily_visitors") for c in checks)
    if needs_db and f.read_error:
        return "unchecked", ["could not read the analytics database, so this "
                             "experiment's blockers were NOT tested: %s"
                             % f.read_error]

    reasons = []
    for c in checks:
        kind = c.get("check")
        if kind == "umami_read":
            pass                                    # got here, so it read
        elif kind == "event_flowing":
            name = c["event"]
            n = (f.events or {}).get(name, {}).get("n", 0)
            if n < int(c.get("min", 1)):
                reasons.append("%s has fired %d times, needs at least %s"
                               % (name, n, c.get("min", 1)))
        elif kind == "min_daily_visitors":
            got = f.traffic["daily_visitors_30d"]
            if got < float(c["n"]):
                reasons.append("%s visitors a day measured, this needs %s"
                               % (got, c["n"]))
        elif kind == "manual":
            reasons.append(c.get("why", "a human gate with no description"))
        else:
            reasons.append("unknown check %r, so it was not tested" % kind)
    return ("blocked" if reasons else "clear"), reasons


# -------------------------------------------------------------------- answers

Answer = collections.namedtuple("Answer", "verdict headline lines caveats")


def answer_exp001(f: Facts) -> Answer:
    """Has anybody who is not us ever clicked a buy button."""
    rows = umami_rows("""
        select to_char(e.created_at, 'YYYY-MM-DD HH24:MI'),
               e.session_id::text, e.url_path,
               coalesce(pl.string_value, ''), coalesce(sk.string_value, ''),
               coalesce(s.browser, '') || ' ' || coalesce(s.screen, ''),
               coalesce(nullif(e.referrer_domain, ''), ''),
               coalesce(wh.string_value, '')
        from website_event e
        left join event_data pl
               on pl.website_event_id = e.event_id and pl.data_key = 'plink'
        left join event_data sk
               on sk.website_event_id = e.event_id and sk.data_key = 'sku'
        left join event_data wh
               on wh.website_event_id = e.event_id and wh.data_key = 'who'
        left join session s on s.session_id = e.session_id
        where e.website_id = %s and e.event_name = 'buy-click'
        order by e.created_at
    """ % W)

    # Did each clicking visitor ever arrive from somewhere outside the site?
    # An arrival with an external referrer is the nearest thing available to
    # evidence that a click was not ours, and it is weak evidence, not proof.
    refs = umami_rows("""
        with b as (select distinct session_id from website_event
                   where website_id = %s and event_name = 'buy-click')
        select e.session_id::text,
               string_agg(distinct nullif(e.referrer_domain, ''), ',')
        from website_event e join b on b.session_id = e.session_id
        where e.website_id = %s
        group by 1
    """ % (W, W))
    entry = {r[0]: (r[1] or "") for r in refs}

    lookup = plink_to_sku()
    visitors = sorted({r[1] for r in rows})
    external = sorted(v for v in visitors if entry.get(v))
    screens = collections.Counter(r[5].strip() for r in rows)

    resolved = 0
    for r in rows:
        if r[4] and r[4] != "unknown":
            resolved += 1
        elif r[3] and r[3] in lookup:
            resolved += 1

    known_internal = [r for r in rows if r[7] == "internal"]
    unattributed = [r for r in rows if r[7] != "internal"]

    lines = [
        "%d buy-click events from %d distinct visitors, out of %d visitors "
        "all time." % (len(rows), len(visitors), f.traffic["visitors"]),
        "%d clicks are known to be ours (who=internal). %d are unattributed, "
        "which is NOT the same as being a stranger's."
        % (len(known_internal), len(unattributed)),
        "%d of the %d clicks can be tied to a product; the rest were recorded "
        "before the payment link id was captured and their SKU reads "
        "'unknown'." % (resolved, len(rows)),
        "%d of the %d clicking visitors arrived from an external referrer at "
        "some point (%s)." % (
            len(external), len(visitors),
            ", ".join(sorted({d for v in external
                              for d in entry[v].split(",") if d})) or "none"),
        "Devices behind the clicks: %s." % ", ".join(
            "%s x%d" % (k or "unknown", n) for k, n in screens.most_common()),
    ]

    caveats = [
        "Umami is cookieless and stores no identity, so a click from our own "
        "laptop and a click from a stranger are the same row unless the "
        "browser was labelled first. measure.js gained that label on "
        "2026-09-03: load any page once with ?6s-internal=1 and everything "
        "that browser sends afterwards carries who=internal. Nothing recorded "
        "before that date carries it, so no historical click can be "
        "attributed either way, ever.",
        "Three of the clicks fall in the window when the payment links were "
        "being built and tested, which is when we would have clicked them.",
        "session_id in Umami is the VISITOR, not the visit. It persists across "
        "days here, so '%d visitors' is not '%d sessions'." % (
            f.traffic["visitors"], f.traffic["visitors"]),
        "An external referrer is weak evidence at best. It says the visitor "
        "arrived from LinkedIn or Bluesky at some point, not that they were "
        "not us; we post to both and click our own posts.",
    ]

    if not known_internal and unattributed:
        # The honest verdict. Not one of these clicks can be attributed to a
        # person who is not us, and not one can be ruled out either. Rounding
        # this to "yes, a stranger clicked" would be the single most expensive
        # false positive available to this business.
        return Answer(
            "ambiguous",
            "Unresolved. %d clicks exist, none carries the internal label "
            "because none predates it, and none can be shown to be a stranger "
            "or shown to be us." % len(rows),
            lines, caveats)
    return Answer(
        "ambiguous",
        "%d of %d clicks are known to be ours. The other %d remain "
        "unattributed: absent a label is not the same as a stranger."
        % (len(known_internal), len(rows), len(unattributed)),
        lines, caveats)


def answer_exp002(f: Facts) -> Answer:
    """Does anybody reach the offer at the bottom of a zone page."""
    rows = umami_rows("""
        select coalesce(ty.string_value, '(none)'),
               de.string_value,
               coalesce(sv.number_value::int::text, '1'),
               count(*)
        from website_event e
        join event_data de
          on de.website_event_id = e.event_id and de.data_key = 'depth'
        left join event_data ty
          on ty.website_event_id = e.event_id and ty.data_key = 'type'
        left join event_data sv
          on sv.website_event_id = e.event_id and sv.data_key = 'sv'
        where e.website_id = %s and e.event_name = 'scroll-depth'
        group by 1, 2, 3 order by 1, 2
    """ % W)
    views = umami_rows("""
        select case when url_path like '/zones/%%' then 'zone'
                    when url_path like '/rooms/%%' then 'room'
                    when url_path like '/articles/%%' then 'article'
                    else 'other' end,
               count(*)
        from website_event
        where website_id = %s and event_type = 1
        group by 1
    """ % W)
    seen = {r[0]: int(r[1]) for r in views}

    by_type = collections.defaultdict(collections.Counter)
    versions = collections.Counter()
    for t, depth, sv, n in rows:
        by_type[t][depth] += int(n)
        versions[sv] += int(n)

    lines = []
    for t in sorted(by_type):
        c = by_type[t]
        total = sum(c.values())
        deep = c["70-89"] + c["90-100"]
        lines.append(
            "%s: %d scroll-depth events, %d of them 70%% or deeper (%s). "
            "%d page views of that type were recorded."
            % (t, total, deep,
               ", ".join("%s=%d" % kv for kv in sorted(c.items())),
               seen.get(t, 0)))
    if not lines:
        lines.append("No scroll-depth events have been recorded at all.")

    v2 = versions.get("2", 0)
    lines.append("Schema versions present: %s. Only sv=2 events can be turned "
                 "into a share." % (dict(versions) or "none"))

    caveats = [
        "The events before sv=2 cannot answer the question they were built "
        "for. That version only fired when the reader had scrolled at all, so "
        "a visitor who landed and left emitted nothing, and 'did not scroll' "
        "is stored identically to 'the event was lost'. Six events against "
        "fifty-four zone page views is therefore not a 11 percent read-rate; "
        "it is an unknown mixture of the two.",
        "sv=2, shipped 2026-09-03, always emits exactly once per page view "
        "including a genuine 0-14, which is what supplies the denominator. "
        "Do not pool sv=2 with the earlier events.",
    ]

    if v2 < 30:
        return Answer(
            "insufficient data",
            "Cannot be answered yet: %d events on the version that can answer "
            "it. The counting is now correct and needs traffic through it."
            % v2,
            lines, caveats)
    z = by_type.get("zone", collections.Counter())
    tot = sum(z.values())
    deep = z["70-89"] + z["90-100"]
    return Answer(
        "answered",
        "%d of %d zone page views reached 70%% or deeper (%.0f%%)."
        % (deep, tot, 100.0 * deep / tot if tot else 0),
        lines, caveats)


def answer_exp004(f: Facts) -> Answer:
    """Does the Quest keep anybody past the first card."""
    rows = umami_rows("""
        select e.session_id::text, count(*), max(d.number_value)::int
        from website_event e
        left join event_data d
               on d.website_event_id = e.event_id and d.data_key = 'nth'
        where e.website_id = %s and e.event_name = 'quest-card-done'
        group by 1 order by 2 desc
    """ % W)
    quest_views = one("""
        select count(*), count(distinct session_id) from website_event
        where website_id = %s and event_type = 1 and url_path like '%%quest%%'
    """ % W, ["0", "0"])

    if not rows:
        return Answer("insufficient data",
                      "Nobody has finished a card.",
                      ["quest-card-done has never fired."], [])
    past_first = [r for r in rows if int(r[1]) > 1]
    lines = [
        "%s Quest page views by %s visitors."
        % (quest_views[0], quest_views[1]),
        "%d visitors finished at least one card; %d finished more than one "
        "(cards each: %s)."
        % (len(rows), len(past_first), ", ".join(r[1] for r in rows)),
    ]
    return Answer(
        "insufficient data" if len(rows) < 10 else "answered",
        "%d of %d visitors who started got past the first card, on %d "
        "visitors total. Too few to be a rate."
        % (len(past_first), len(rows), len(rows)),
        lines,
        ["Two visitors is an anecdote. It is recorded because the counter now "
         "works, not because it decides anything."])


ANSWERS = {"EXP-001": answer_exp001,
           "EXP-002": answer_exp002,
           "EXP-004": answer_exp004}


# --------------------------------------------------------------------- output

def wrap(text: str, indent: str = "              ") -> str:
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > 62:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    out.append(line)
    return ("\n" + indent).join(out)


def main() -> int:
    argv = sys.argv[1:]

    if "--power" in argv:
        i = argv.index("--power")
        p1, p2 = float(argv[i + 1]), float(argv[i + 2])
        n = sample_size(p1, p2)
        print(f"  {p1:.1%} to {p2:.1%}: {n:,} visitors per arm, {n*2:,} total")
        return 0

    reg = load()
    offline = "--offline" in argv
    only_id = argv[argv.index("--answer") + 1] if "--answer" in argv else None

    if offline:
        f = Facts(None, None, "--offline was passed, so nothing was read")
    else:
        f = gather()

    print("  EXPERIMENT REGISTRY\n")

    stated = reg.get("observed_daily_visitors")
    if f.read_error:
        print("  Traffic: UNCHECKED. %s" % wrap(f.read_error, "           "))
        print("  Nothing below has been evaluated against real data. The last")
        print("  figure anybody wrote down by hand was %s visitors a day, and"
              % stated)
        print("  this run has no way to know whether that is still true.\n")
    else:
        t = f.traffic
        print("  Measured from the Umami database just now, %s UTC:"
              % datetime.datetime.now(datetime.timezone.utc)
              .strftime("%Y-%m-%d %H:%M"))
        print("    all time    %d pageviews, %d visitors, %d visits (%s to %s)"
              % (t["pageviews"], t["visitors"], t["visits"],
                 t["first"], t["last"]))
        print("    last 30d    %d pageviews, %d visitors, %d visits"
              % (t["pageviews_30d"], t["visitors_30d"], t["visits_30d"]))
        print("    last 7d     %d pageviews, %d visitors, %d visits"
              % (t["pageviews_7d"], t["visitors_7d"], t["visits_7d"]))
        print("    %s visitors a day over 30 days"
              % t["daily_visitors_30d"])
        print("    NOTE  session_id is the visitor and persists across days.")
        print("          The visit is visit_id. Reporting distinct session_id")
        print("          as 'sessions' understates visits about threefold.")
        if stated is not None and abs(float(stated)
                                      - t["daily_visitors_30d"]) >= 0.05:
            print("    DRIFT ops/experiments.json says %s a day, the database"
                  % stated)
            print("          says %s. GOALS.md and ops/preflight.py's"
                  % t["daily_visitors_30d"])
            print("          goals-traffic-current gate pin that field, so it")
            print("          is corrected there, in one commit, or not at all.")
        print("    events      %s" % (", ".join(
            "%s %d" % (k, v["n"]) for k, v in f.events.items()) or "none"))
        print()

    daily = None if f.read_error else f.traffic["daily_visitors_30d"]
    states = {}

    for e in reg["experiments"]:
        if only_id and e["id"] != only_id:
            continue
        state, reasons = resolve_blockers(e, f)
        states[e["id"]] = state

        print(f"  {e['id']}  {e['title']}")
        print(f"     status   {e['status']}")
        print(f"     because  {wrap(e['because'])}")
        print(f"     believe  {wrap(e['believe'])}")
        print(f"     metric   {wrap(e['primary_metric'])}")
        print(f"     guard    {wrap(e['guardrail'])}")
        b, t_ = e.get("baseline"), e.get("target")
        if b and t_:
            n = sample_size(b, t_)
            print(f"     needs    {n:,} visitors per arm, {n*2:,} total "
                  f"to detect {b:.1%} to {t_:.1%}")
            if daily:
                print("     at the measured %s visitors a day that is %s days"
                      % (daily, format(math.ceil((n * 2) / daily), ",")))
            else:
                print("     at the measured rate: UNCHECKED, traffic not read")

        if state == "clear":
            print("     blocked  nothing, every check passed just now")
        elif state == "unchecked":
            for r in reasons:
                print("     blocked  UNCHECKED: %s" % wrap(r))
        else:
            for r in reasons:
                print("     blocked  %s" % wrap(r))

        if e.get("owner_action"):
            # A gate only Phil can pass. CLAUDE.md 0.5: name it, build
            # everything up to it, and never let it become invisible.
            print("     OWNER    %s" % wrap(e["owner_action"]))

        fn = ANSWERS.get(e["id"])
        if fn:
            if f.read_error:
                print("     answer   UNCHECKED. The database was not read, so "
                      "this")
                print("              experiment has no answer from this run. "
                      "It is not")
                print("              zero and it is not the last answer "
                      "recorded.")
            else:
                try:
                    a = fn(f)
                except Unreadable as ex:
                    print("     answer   UNCHECKED: %s" % wrap(str(ex)))
                else:
                    print("     answer   %s: %s"
                          % (a.verdict.upper(), wrap(a.headline)))
                    for ln in a.lines:
                        print("              - %s" % wrap(ln, "                "))
                    for c in a.caveats:
                        print("              caveat: %s"
                              % wrap(c, "                "))
                    if "--record" in argv:
                        e["last_reading"] = {
                            "measured_utc": datetime.datetime.now(
                                datetime.timezone.utc).strftime(
                                    "%Y-%m-%dT%H:%MZ"),
                            "verdict": a.verdict,
                            "headline": a.headline,
                            "detail": list(a.lines),
                            "caveats": list(a.caveats),
                        }
        print()

    clear = [i for i, s in states.items() if s == "clear"]
    blocked = [i for i, s in states.items() if s == "blocked"]
    unknown = [i for i, s in states.items() if s == "unchecked"]
    print("  %d shown, %d unblocked, %d blocked, %d UNCHECKED."
          % (len(states), len(clear), len(blocked), len(unknown)))
    if unknown:
        print("  Unchecked is not passing and it is not blocked. These were "
              "not tested: %s" % ", ".join(unknown))

    if "--record" in argv:
        if f.read_error:
            print("  --record ignored: nothing was read, and writing an "
                  "unread run over a real measurement is the exact failure "
                  "CLAUDE.md section 0.4 is about.")
        else:
            reg["_readings_note"] = (
                "last_reading blocks are written by ops/experiments.py "
                "--record and only ever after a successful database read. "
                "They are a snapshot with a timestamp, not a live value; "
                "re-run rather than quoting them.")
            io.open(REG, "w", encoding="utf-8", newline="\n").write(
                json.dumps(reg, indent=1, ensure_ascii=False) + "\n")
            print("  recorded to ops/experiments.json")

    # A registry that lets somebody start an unmeasurable test is a registry
    # that will eventually be used to justify a decision made from noise.
    live = [e for e in reg["experiments"] if e["status"] == "running"]
    assert not (live and daily is None), (
        "an experiment is marked running while traffic could not be measured. "
        "Stop it or fix the read first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
