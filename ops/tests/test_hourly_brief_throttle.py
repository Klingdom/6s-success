#!/usr/bin/env python3
"""
hourly-brief.yml now fires on every push to main, not only its own unreliable
hourly cron (see ops/check_cron_cadence.py and gate_cron_cadence in
preflight.py for why: the cron's real gaps average 4 to 5 hours). Unlike
fulfil-orders.yml, this workflow emails Phil unconditionally rather than only
when a real order is waiting, so an unthrottled push trigger would replace
"arrives hours late" with "arrives on every one of a day's ~150 commits."
ops/hourly_brief.py's seconds_since_last_send()/record_sent() are the guard
against that. This proves the guard's own logic in isolation: no prior
record sends, a record younger than the floor skips, a record older than the
floor sends again, and the record it writes is what the next check reads.

Run:  python ops/tests/test_hourly_brief_throttle.py
"""
import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))


def main() -> int:
    import hourly_brief as hb

    fails = []
    real_path = hb.SENT_STATE
    tmp_path = real_path + ".test-tmp"
    hb.SENT_STATE = tmp_path
    try:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        gap = hb.seconds_since_last_send()
        if gap is not None:
            fails.append("no record yet: want None, got %r" % (gap,))

        now = datetime.datetime.now(datetime.timezone.utc)
        recent = now - datetime.timedelta(minutes=5)
        json.dump({"sent_at": recent.isoformat(timespec="seconds")},
                  io.open(tmp_path, "w", encoding="utf-8"), indent=1)
        gap = hb.seconds_since_last_send()
        if gap is None or gap >= hb.MIN_SEND_INTERVAL_MINUTES * 60:
            fails.append("5 min ago should read as inside the floor, got gap=%r "
                         "against a %d-minute floor" % (gap, hb.MIN_SEND_INTERVAL_MINUTES))

        old = now - datetime.timedelta(minutes=hb.MIN_SEND_INTERVAL_MINUTES + 5)
        json.dump({"sent_at": old.isoformat(timespec="seconds")},
                  io.open(tmp_path, "w", encoding="utf-8"), indent=1)
        gap = hb.seconds_since_last_send()
        if gap is None or gap < hb.MIN_SEND_INTERVAL_MINUTES * 60:
            fails.append("a send older than the floor should be eligible again, "
                         "got gap=%r" % (gap,))

        corrupt = tmp_path
        io.open(corrupt, "w", encoding="utf-8").write("not json")
        gap = hb.seconds_since_last_send()
        if gap is not None:
            fails.append("an unreadable record should read as never-sent (None), "
                         "got %r" % (gap,))

        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        hb.record_sent()
        gap = hb.seconds_since_last_send()
        if gap is None or gap > 5:
            fails.append("record_sent() should write a timestamp readable as "
                         "'just now', got gap=%r" % (gap,))
        if not os.path.exists(tmp_path):
            fails.append("record_sent() did not write %s" % tmp_path)
    finally:
        hb.SENT_STATE = real_path
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    for f in fails:
        print("FAIL", f)
    print("ok" if not fails else "%d failure(s)" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
