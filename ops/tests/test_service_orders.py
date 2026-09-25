#!/usr/bin/env python3
"""
Prove ops/service_orders.py's find_time() cannot mis-parse a stated year as
part of the hour, and give which_service() and ics() their first coverage.

This file forwards real paid bookings to Phil and attaches a real .ics
calendar invite, and had no test file at all. Found 2026-09-09, reading the
file cold: DATE_PATTERNS captured an unanchored (\\d{1,2}) for the hour, so
"Oct 14, 2027 at 2pm" matched hour="20" out of the "2027" year and never
reached the real "2pm" later in the string, silently producing an invite for
2026-10-14 20:00 instead of the stated 2027-10-14 14:00. The file's own
docstring says "a wrong appointment time is worse than no invite, so
anything ambiguous returns None"; a stated year the parser cannot use is
exactly that kind of ambiguity, not something to guess through. Fixed by
wrapping every bare day/hour capture in (?<!\\d)...(?!\\d) so it can never
match a slice of a longer digit run.

Run:  python ops/tests/test_service_orders.py
"""
import datetime as dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import mailer                                                     # noqa: E402
import service_orders as so                                      # noqa: E402


def check_incremental_persistence():
    """A mail failure partway through a --send batch must not undo the
    idempotency of sends that already went out.

    Regression for a real bug found 2026-09-25, cold-reading this file:
    the state file used to be written once, after both loops finished. A
    batch of more than one new booking that raised on its second send (a
    timeout, a bad attachment, anything) meant the first booking's forward
    had already reached Phil but its id was never persisted, so the next
    run forwarded that same booking to him again, exactly the double-send
    this file's own docstring promises "idempotent" rules out.
    """
    orig_state, orig_charges, orig_emails, orig_argv = (
        so.STATE, so.recent_service_charges, so.service_emails, sys.argv)
    orig_send, orig_owner = mailer.send, mailer.owner

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.close()
    so.STATE = tmp.name
    sent = []

    def fake_send(to, subject, text, *a, **kw):
        sent.append(subject)
        if len(sent) == 2:
            raise RuntimeError("simulated send failure on the second booking")

    try:
        so.recent_service_charges = lambda limit=100: [
            {"id": "ch_1", "service": "Virtual Home Consult", "amount": 250.0,
             "email": "a@example.com", "name": "A", "created": 0},
            {"id": "ch_2", "service": "In-Home Reset Day", "amount": 1200.0,
             "email": "b@example.com", "name": "B", "created": 0},
        ]
        so.service_emails = lambda: []
        mailer.send = fake_send
        mailer.owner = lambda: "owner@example.com"
        sys.argv = ["service_orders.py", "--send"]
        try:
            so.main()
        except RuntimeError:
            pass
        try:
            with open(tmp.name, encoding="utf-8") as fh:
                state = json.load(fh)
        except Exception:                                          # noqa: BLE001
            return ["state file was never written after the first send "
                    "succeeded and the second raised"]
        if "ch_1" not in state.get("charges", []):
            return ["ch_1's forward was sent but never persisted to state, "
                     "so a rerun would forward it a second time"]
        return []
    finally:
        so.STATE, so.recent_service_charges, so.service_emails, sys.argv = (
            orig_state, orig_charges, orig_emails, orig_argv)
        mailer.send, mailer.owner = orig_send, orig_owner
        os.remove(tmp.name)


def main() -> int:
    fails = []

    # 1. The exact regression: a message that states an explicit year must
    #    return None, not a wrong time computed from a slice of that year.
    year_cases = [
        "Oct 14, 2027 at 2pm works for me",
        "I want the in-home reset on October 14 2027 at 2pm",
        "14 October 2027 at 2pm",
    ]
    for text in year_cases:
        when = so.find_time(text)
        if when is not None:
            fails.append("stated-year message did not return None: %r -> %r"
                         % (text, when))

    # 2. Ordinary dates with no year still parse, in both supported shapes,
    #    and the am/pm and 24-hour branches all land on the right hour.
    now = dt.datetime.now()
    cases = [
        ("14 October at 2pm", (10, 14, 14, 0)),
        ("Oct 14 at 2pm", (10, 14, 14, 0)),
        ("Oct. 14th, 2pm works", (10, 14, 14, 0)),
        ("Sept 5 at 9:30am please", (9, 5, 9, 30)),
        ("Oct 14 at 14:00", (10, 14, 14, 0)),
    ]
    for text, (month, day, hour, minute) in cases:
        when = so.find_time(text)
        if when is None:
            fails.append("ordinary date failed to parse at all: %r" % text)
            continue
        if (when.month, when.day, when.hour, when.minute) != (month, day, hour, minute):
            fails.append("wrong time for %r: got %s, wanted month=%d day=%d %02d:%02d"
                         % (text, when, month, day, hour, minute))
        # A date already in the past for "now" must roll to next year, not
        # sit in the past silently.
        naive_this_year = when.replace(year=now.year)
        if naive_this_year < now - dt.timedelta(days=1) and when.year != now.year + 1:
            fails.append("past date did not roll to next year: %r -> %s" % (text, when))

    # 3. The bare-hour-below-8 heuristic assumes a working-hours booking.
    when = so.find_time("reset day on 3 december at 3")
    if when is None or when.hour != 15:
        fails.append("bare hour 3 with no am/pm did not assume 3pm: %r" % when)

    # 4. Ambiguous text with no date at all returns None, not a guess.
    if so.find_time("home consult next monday at 2pm") is not None:
        fails.append("a relative date ('next monday') should not parse")
    if so.find_time("corporate lean 6s enquiry, no date yet") is not None:
        fails.append("text with no date at all should not parse")

    # 5. which_service: the subject decides over an incidental phrase in the
    #    body, per the file's own EARLIEST POSITION rule.
    if so.which_service("Virtual Home Consult booking") != "Virtual Home Consult":
        fails.append("which_service missed a direct match")
    if so.which_service("nothing here matches") is not None:
        fails.append("which_service should return None with no phrase present")
    mixed = "Corporate Lean 6S enquiry -- by the way is reset day still open"
    if so.which_service(mixed) != "Corporate Lean 6S":
        fails.append("which_service did not prefer the earlier subject phrase: %r"
                     % so.which_service(mixed))

    # 6. ics() produces a well-formed VEVENT with the right duration for each
    #    service, and CRLF line endings as the RFC requires.
    when = dt.datetime(2026, 10, 14, 14, 0)
    for service, minutes in so.DURATION.items():
        body = so.ics(service, when, "A Customer").decode("utf-8")
        if "BEGIN:VEVENT" not in body or "END:VEVENT" not in body:
            fails.append("ics() for %r missing VEVENT" % service)
        if "\r\n" not in body:
            fails.append("ics() for %r is not CRLF" % service)
        end = when + dt.timedelta(minutes=minutes)
        if "DTEND:" + end.strftime("%Y%m%dT%H%M%S") not in body:
            fails.append("ics() for %r has the wrong duration" % service)

    # 7. A send failure partway through a batch must not undo the
    #    idempotency of the sends that already succeeded.
    fails += check_incremental_persistence()

    if fails:
        print("FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS: %d case(s), find_time year-guard, which_service, ics, "
          "incremental persistence all correct"
          % (len(year_cases) + len(cases) + 4 + len(so.DURATION)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
