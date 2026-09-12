#!/usr/bin/env python3
"""
Prove ops/status_report.py's recent_retros() returns the newest entries
from NIGHTLY-LOG.md, not the oldest.

Found 2026-09-12, this PM check-in, cold-reading status_report.py's
"retrospectives" block (never covered by a test before). NIGHTLY-LOG.md is
newest-first, by its own header, but the inline code did
`entries = re.split(r"\n## ", log)[1:]; ... entries[-3:]`, which is the
LAST three items of that list, i.e. the three OLDEST entries in the whole
file. With the real log running back to 2026-09-01, the four-hourly status
email's "RETROSPECTIVE: what went wrong" section (status-email.yml) was
showing a cycle from over a week earlier as if it were the most recent one.

Fixed by extracting the slice into recent_retros(log, n=3) and slicing
entries[:n] instead of entries[-3:].

Run:  python ops/tests/test_status_report_retros.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import status_report as sr                                       # noqa: E402


def entry(title, wrong=None, change=None):
    body = f"## {title}\n\n"
    if wrong:
        body += f"**Did not go well:** {wrong}\n\n"
    if change:
        body += f"**Changing next cycle:** {change}\n\n"
    return body


def main() -> int:
    fails = []

    # 1. A synthetic newest-first log: the newest entry must come back
    # first, not the oldest. The old entries[-3:] slice would return
    # "oldest" here instead of "newest".
    log = ("# Nightly log\n\nnewest first.\n\n"
           + entry("newest", wrong="w-newest", change="c-newest")
           + entry("middle", wrong="w-middle", change="c-middle")
           + entry("oldest", wrong="w-oldest", change="c-oldest"))
    retros = sr.recent_retros(log, n=2)
    titles = [r["title"] for r in retros]
    if titles != ["newest", "middle"]:
        fails.append(f"expected ['newest', 'middle'], got {titles!r}")
    if retros and retros[0]["wrong"] != "w-newest":
        fails.append(f"expected newest entry's 'wrong' text, got {retros[0]['wrong']!r}")

    # 2. n=3 default, with more than 3 entries present, must still return
    # only the top 3 in order.
    log4 = log + entry("oldest-still")
    retros3 = sr.recent_retros(log4)
    if [r["title"] for r in retros3] != ["newest", "middle", "oldest"]:
        fails.append(f"n=3 default returned {[r['title'] for r in retros3]!r}")

    # 3. The real, live file: the first retro's title must match the log's
    # own first "## " heading exactly, proving the live gather() path (via
    # recent_retros) reads the top of the file, not the bottom.
    real_log = sr.read(os.path.join(ROOT, "ops", "NIGHTLY-LOG.md"))
    first_heading = re.search(r"\n## (.+)", real_log)
    real_retros = sr.recent_retros(real_log)
    if not first_heading:
        fails.append("live NIGHTLY-LOG.md has no '## ' heading to compare against")
    elif not real_retros or real_retros[0]["title"] != first_heading.group(1):
        got = real_retros[0]["title"] if real_retros else None
        fails.append(f"live file's first retro title {got!r} != file's actual "
                      f"first heading {first_heading.group(1)!r}")

    if fails:
        print(f"FAIL ({len(fails)}):")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 3 cases (newest-first order, n=3 default, live-file top-entry match)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
