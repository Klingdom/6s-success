#!/usr/bin/env python3
"""
The owner must actually be receiving the email that asks him to unblock things.

WHY THIS EXISTS
---------------
Found 2026-10-10. Three gates check what ops/send_questions.py SAYS:
gate_send_questions_current, gate_send_questions_covers_top_owner_actions and
gate_no_frozen_deck_link. Between them they have caught a false 'deploys are
automatic' claim, a stale list that had never been told about two of
OWNER-ACTIONS.md's own top three items, and a frozen link to an eleven-day-old
artifact. All three look at the content.

Nothing looked at whether it is delivered, and nothing in .github/workflows
referenced the script at all. It was sent by whichever scheduled Routine
happened to run, which is the same thing that went silently dark from
2026-10-04 to 2026-10-09 on USAGE_LIMIT_REACHED (INCIDENT-002, issue #40). For
those five days the hourly status email kept arriving, because
status-email.yml is a real workflow, and the one email that asks the owner to
unblock the business did not, because it was not one.

All nine open issues are decision or blocked-on-art, and GOALS.md has named
arrivals the constraint since 2026-09-02 with every lever behind an owner
action. So a silent channel here stalls everything, and it did.

Run:  python ops/tests/test_gate_owner_questions_not_stale.py
"""
import datetime as dt
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'ops'))

import preflight                                              # noqa: E402

NOW = dt.datetime(2026, 10, 10, 12, 0, 0, tzinfo=dt.timezone.utc)


def stamp(days_ago):
    when = NOW - dt.timedelta(days=days_ago)
    return {'sent_at': when.strftime('%Y-%m-%dT%H:%M:%SZ')}


def main():
    fails = []
    f = getattr(preflight, 'owner_questions_staleness_problem', None)
    if f is None:
        print('FAIL')
        print(' - preflight.owner_questions_staleness_problem is gone, so '
              'nothing checks whether the owner email is being delivered')
        return 1

    # 1. A send three weeks ago must complain, and say how long it has been.
    p = f(stamp(21), NOW)
    if not p:
        fails.append('a send 21 days ago did not complain at all')
    elif '21 days' not in p:
        fails.append('the complaint does not say how long it has been: %r' % p)

    # 2. A send yesterday must not complain. Without this the gate could be a
    #    constant warning, which is the same as no warning.
    if f(stamp(1), NOW):
        fails.append('a send yesterday complained: %r' % f(stamp(1), NOW))

    # 3. The boundary, both sides of it. One missed Monday is GitHub being
    #    GitHub (check_cron_cadence measures this repository's crons firing at
    #    5x their configured interval); two missed Mondays is a dead channel.
    if f(stamp(10), NOW):
        fails.append('10 days complained, so one missed weekly run is treated '
                     'as a dead channel')
    if not f(stamp(11), NOW):
        fails.append('11 days did not complain, so two missed weekly runs '
                     'pass silently')

    # 4. No record at all is UNKNOWN, never 'fine'. This is the state the real
    #    repository was in when this was written.
    p = f(None, NOW)
    if not p or 'UNKNOWN' not in p:
        fails.append('a missing record did not report UNKNOWN: %r' % p)
    p = f({}, NOW)
    if not p:
        fails.append('an empty record did not complain')

    # 5. A malformed stamp must not be read as a recent send. A crash here
    #    would also do, but silence would not.
    p = f({'sent_at': 'last Tuesday'}, NOW)
    if not p or 'UNKNOWN' not in p:
        fails.append('an unparseable sent_at did not report UNKNOWN: %r' % p)

    # 6. The gate must be registered, or none of the above ever runs.
    src = io.open(os.path.join(ROOT, 'ops', 'preflight.py'),
                  encoding='utf-8').read()
    if 'run_gate(gate_owner_questions_not_stale)' not in src:
        fails.append('gate_owner_questions_not_stale is defined but never '
                     'registered with run_gate, so it never runs')

    # 7. And the workflow that does the sending must exist, because the gate
    #    only reports the silence; the workflow is what prevents it.
    wf = os.path.join(ROOT, '.github', 'workflows', 'owner-questions.yml')
    if not os.path.exists(wf):
        fails.append('.github/workflows/owner-questions.yml is gone, so the '
                     'email is back to being sent only by whichever session '
                     'happens to run')
    else:
        body = io.open(wf, encoding='utf-8').read()
        if 'send_questions.py --send' not in body:
            fails.append('owner-questions.yml does not actually send the '
                         'email')
        if 'schedule:' not in body:
            fails.append('owner-questions.yml has no schedule, so it only '
                         'runs when somebody remembers')

    if fails:
        print('FAIL')
        for x in fails:
            print(' -', x)
        return 1
    print('OK: owner-questions delivery staleness, 7/7 checks pass')
    return 0


if __name__ == '__main__':
    sys.exit(main())
