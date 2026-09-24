#!/usr/bin/env python3
"""
Prove ops/crawl_report.py cannot silently report "0 traffic in the window"
when the real cause is that every line failed to parse, and prove the check
can fail (the class of defect it exists to prevent).

Found 2026-09-24, cold-read: main()'s "if not rows" branch printed "the log
holds N line(s) but none inside the last D day(s)" whenever rows was empty,
whether that was because the window genuinely had no traffic or because
every single line failed PROXY_LINE/LINE and was silently dropped into
`unparsed`. The `unparsed lines : %d (log format changed?)` diagnostic that
exists specifically to catch that only printed inside the non-empty-rows
branch, so it never ran in the total-failure case. This is exactly the class
CLAUDE.md 0.4 names: "A tool that could not read the live site has not
proved the link is unused" applied to this file's own log parser, and it is
not hypothetical: the module's own docstring records this log format
drifting once already (1,162 lines dropped until PROXY_LINE was widened).

Run:  python ops/tests/test_crawl_report_unparsed_reporting.py
"""
import contextlib
import datetime
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import crawl_report as CR                                     # noqa: E402


def run(raw_lines, days=7):
    CR.fetch_proxy = lambda: (raw_lines, "")
    sys.argv = ["crawl_report.py", "--days", str(days)]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = CR.main()
    return rc, buf.getvalue()


def main() -> int:
    fails = []

    # Case 1: every line fails to parse (the real historical shape, format
    # drift). Must be reported as UNCHECKED, not as a measured zero.
    garbage = ["not a log line at all", "also garbage", "still garbage"]
    rc, out = run(garbage)
    if rc != 2:
        fails.append(
            f"100%% unparsed: exit code was {rc}, expected 2 (UNCHECKED); "
            "a silent 'clean' exit here is the exact bug this test guards")
    if "UNCHECKED" not in out:
        fails.append(
            "100%% unparsed: output did not say UNCHECKED; a reader would "
            "see this as a real measurement of zero traffic")
    if "the log holds" in out:
        fails.append(
            "100%% unparsed: printed the genuine-zero-traffic message "
            "instead of the parse-failure message; this is the exact "
            "regression the fix closes")

    # Case 2: lines parse fine but are genuinely outside the requested
    # window. Must still report the honest "no traffic in window" message,
    # not be swept into the UNCHECKED path (that would be a new, opposite
    # false-alarm defect).
    old_line = (
        '[01/Jan/2020:00:00:00 +0000] 200 GET https example.com "/" '
        '[Client 1.2.3.4] [Length 100] "Mozilla/5.0" "-"'
    )
    assert CR.PROXY_LINE.match(old_line), "test setup broken: old_line must parse"
    rc2, out2 = run([old_line, old_line])
    if rc2 != 0:
        fails.append(
            f"genuine no-traffic-in-window: exit code was {rc2}, expected 0")
    if "UNCHECKED" in out2:
        fails.append(
            "genuine no-traffic-in-window: incorrectly reported UNCHECKED; "
            "a real (if old) log line was misclassified as a parse failure")
    if "the log holds" not in out2:
        fails.append(
            "genuine no-traffic-in-window: did not print the expected "
            "honest zero-traffic message")

    # Case 3: mixed real traffic plus some unparseable noise. Must report
    # real rows AND surface the unparsed count, not hide either.
    now = datetime.datetime.now(datetime.timezone.utc)
    ts = now.strftime("%d/%b/%Y:%H:%M:%S +0000")
    good = (
        '[%s] 200 GET https example.com "/" [Client 1.2.3.4] '
        '[Length 100] "Mozilla/5.0 (compatible; Googlebot/2.1)" "-"' % ts
    )
    assert CR.PROXY_LINE.match(good), "test setup broken: good must parse"
    rc3, out3 = run([good, good, "garbage line"])
    if rc3 != 0:
        fails.append(f"mixed traffic: exit code was {rc3}, expected 0")
    if "requests       : 2" not in out3:
        fails.append("mixed traffic: did not report the 2 real requests")
    if "unparsed lines : 1" not in out3:
        fails.append("mixed traffic: did not surface the 1 unparsed line")

    if fails:
        print("FAIL:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK: 100%% unparsed reports UNCHECKED/exit 2, a genuine empty "
          "window still reports its honest zero, and mixed traffic reports "
          "both its real rows and its unparsed count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
