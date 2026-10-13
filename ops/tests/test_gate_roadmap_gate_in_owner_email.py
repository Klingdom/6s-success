#!/usr/bin/env python3
"""
A roadmap gate about to close must appear in the email that can resolve it.

WHY THIS EXISTS
---------------
Found 2026-10-13 by reading ROADMAP-2026-2029.md against the owner email
rather than either on its own. Gate G2 was 19 days out. It resolves on whether
a capped local demand test produces 3 or more paid non-referral bookings or 1
or fewer, and OWNER-ACTIONS.md item 17.3 says in its own words that the budget
and stop date are the one piece that is a real financial commitment and that
the gate is holding the whole services-first funnel reframe open pending
exactly this result.

That ask appeared in none of the email's six BLOCKING items. So the roadmap
held a dated decision, the email held six undated asks, and nothing compared
the two.

A gate is not like the other asks. The others wait; a gate EXPIRES. G5 depends
on G1 and G2 having resolved, so a silently missed G2 does not merely delay a
choice, it removes the roadmap's own ability to re-baseline the $20,000 target
honestly, which is the one thing that document says it exists to protect.

Run:  python ops/tests/test_gate_roadmap_gate_in_owner_email.py
"""
import datetime as dt
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'ops'))

import preflight                                              # noqa: E402
import send_questions                                         # noqa: E402

TODAY = dt.date(2026, 10, 13)


def main():
    fails = []
    f = getattr(preflight, 'expiring_gate_problem', None)
    if f is None:
        print('FAIL')
        print(' - preflight.expiring_gate_problem is gone, so nothing '
              'compares the roadmap gates against the owner email')
        return 1

    near = [('G2', 'a capped local demand test', '~Nov 2026')]

    # 1. The real defect: a gate 19 days out, absent from the email.
    p = f(near, 'nothing about any gate here', TODAY)
    if not p:
        fails.append('a gate 19 days out and absent from the email did not '
                     'complain')
    else:
        for needed in ('G2', '19 days', 'EXPIRES'):
            if needed not in p:
                fails.append('the complaint omits %r, so a reader cannot tell '
                             'which gate or how urgent: %r' % (needed, p))

    # 2. Present in the email: silent. Without this the gate is a constant
    #    warning, which is the same as no warning.
    if f(near, 'BLOCKING ... ROADMAP gate G2 budget and stop date', TODAY):
        fails.append('a gate that IS named in the email still complained')

    # 3. Far away: silent, even though absent. A gate in 2028 is not an ask.
    far = [('G4', 'choose one bet', 'Q1 2028')]
    if f(far, 'no mention', TODAY):
        fails.append('a gate in Q1 2028 was treated as expiring')

    # 4. A condition rather than a date (G3 really is written this way) must
    #    not be guessed into a deadline.
    cond = [('G3', 'contacts produce zero conversations',
             'before any workplace content is written')]
    if f(cond, 'no mention', TODAY):
        fails.append('a gate whose by-when is a condition was given a '
                     'deadline it does not have')

    # 5. Past due must still complain, and say so rather than going quiet.
    past = [('G9', 'something', 'Aug 2026')]
    if not f(past, 'no mention', TODAY):
        fails.append('a gate whose date has already passed did not complain')

    # 6. The real roadmap must parse into real gates, or every check above is
    #    exercising an empty list and proving nothing.
    gates = send_questions.roadmap_gates()
    if len(gates) < 3:
        fails.append('only %d gate(s) parsed out of the real '
                     'ROADMAP-2026-2029.md, so this test is checking an '
                     'almost empty list' % len(gates))
    dated = [g for g in gates if send_questions.gate_due(g[2]) is not None]
    if len(dated) < 3:
        fails.append('only %d of %d real gates yielded a date, so the date '
                     'parser is probably broken' % (len(dated), len(gates)))

    # 7. And the gate must be registered, or none of this ever runs.
    src = io.open(os.path.join(ROOT, 'ops', 'preflight.py'),
                  encoding='utf-8').read()
    if 'run_gate(gate_roadmap_gate_in_owner_email)' not in src:
        fails.append('gate_roadmap_gate_in_owner_email is never registered '
                     'with run_gate')

    # 8. The gate must feed it the RENDERED EMAIL, not this module's source.
    #
    #    Every check above supplies email_text itself, so none of them would
    #    notice the gate reading the wrong thing. The first version of the gate
    #    read ops/send_questions.py as a file, which cannot fail: that file's
    #    own docstrings discuss G2 at length, so the string is present whether
    #    or not the ask reaches the owner. Proved at the time by planting the
    #    real pre-fix state and watching the gate report clean.
    import inspect
    gate_src = inspect.getsource(preflight.gate_roadmap_gate_in_owner_email)
    if 'sq.build()' not in gate_src:
        fails.append('the gate no longer reads the rendered email via '
                     'sq.build(), so it may be checking source text that '
                     'mentions a gate without asking for it')
    # Named by the mechanism rather than by the filename: the complaint text
    # and the explanatory comment both mention the file legitimately, and a
    # check that banned the string would fail on its own documentation.
    if 'io.open(' in gate_src:
        fails.append('the gate opens a file again. It should read the email '
                     'through sq.build() only; reading the module source '
                     'cannot fail, because that source discusses the gates '
                     'it is looking for')

    # 9. End to end against the real tree: the real gates, the real email.
    #    This is the only check here that would catch the ask being dropped.
    real = f(gates, send_questions.build(), dt.date.today())
    if real:
        fails.append('against the REAL roadmap and the REAL email: %s' % real)
    if fails:
        print('FAIL')
        for x in fails:
            print(' -', x)
        return 1
    print('OK: expiring roadmap gates, 9/9 checks pass (%d real gates, %d '
          'dated)' % (len(gates), len(dated)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
