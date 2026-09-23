#!/usr/bin/env python3
"""
Prove gate_tests tells "the browser never started" apart from "the test failed".

WHY
---
On 2026-09-23 three consecutive full preflight runs went red on browser-driven
test files, a different file each time, and every one of them passed on its own
immediately afterwards. The machine had 1.8 GB free with the owner's own 22
background Edge processes resident, so Edge simply could not start inside the
timeout.

Reporting that as FAIL is the same defect this file exists to prevent, pointed
the other way. gate_image_coverage was fixed because it could not tell
"confirmed fine" from "never looked"; gate_tests could not tell "found a
defect" from "never looked". A red build that clears itself on a re-run
teaches people to re-run instead of read, and then a real failure gets re-run
too.

The rule has to be narrow or it becomes an excuse. Both halves are required:
a subprocess.TimeoutExpired AND a browser binary named in the command that
timed out.

Run:  python ops/tests/test_browser_timeout_is_unchecked.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_EDGE_TIMEOUT = (
    "Traceback (most recent call last):\n"
    "  File \"ops/tests/test_corporate_form_interactive.py\", line 88\n"
    "    r = subprocess.run(cmd, ...)\n"
    "subprocess.TimeoutExpired: Command '['C:\\Program Files (x86)\\\\"
    "Microsoft\\Edge\\Application\\msedge.exe', '--headless=new']' "
    "timed out after 60 seconds\n")


def main() -> int:
    fails = []
    f = preflight._browser_launch_timeout

    # 1. The real shape seen in production output must be recognised.
    if not f(REAL_EDGE_TIMEOUT):
        fails.append("the real Edge timeout output was not recognised")

    # 2. Chromium and Chrome spellings too.
    for s in ("subprocess.TimeoutExpired: Command '['/usr/bin/chromium']'",
              "subprocess.TimeoutExpired: Command '['chrome.exe']'"):
        if not f(s):
            fails.append("not recognised: %r" % s[:50])

    # 3. A REAL failure must never be excused. These are the cases that make
    #    the rule narrow rather than convenient.
    for s in ("AssertionError: expected 3 cards, got 2",
              "FAIL\n - the notice stayed hidden",
              # a timeout on something that is not a browser
              "subprocess.TimeoutExpired: Command '['git', 'log']' timed out",
              # a browser named, but no timeout: a genuine assertion failure
              "AssertionError: msedge.exe rendered the wrong title",
              ""):
        if f(s):
            fails.append("wrongly excused a real failure: %r" % s[:50])

    if fails:
        print("FAIL")
        for x in fails:
            print("   " + x)
        return 1
    print("PASS  8 of 8: browser-launch timeouts are unchecked, everything "
          "else still fails")
    return 0


if __name__ == "__main__":
    sys.exit(main())
