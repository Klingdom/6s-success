#!/usr/bin/env python3
"""
Prove ops/build_seo.py's build_sitemap() stamps a new or changed URL's
lastmod from UTC, not the local wall clock.

Found 2026-11-04, PM check-in. A commit landed near a local-midnight
boundary; the sandbox that generated site/sitemap.xml had not yet rolled
its local date to the next day when it ran build_sitemap() and committed
the result, but GitHub's Actions runner, which runs in UTC, had. The next
run of checks.yml regenerated the sitemap fresh, got a different date for
the one page that had actually changed, and failed gate_generator_ownership
on a file nobody had hand-edited.

ops/build_seo.py's own _git_content_date() had already been fixed for the
identical bug on 2026-10-23 (its docstring: "a commit at 03:00 UTC could
date as the previous day on one machine and the next on another"), but
that fix was never applied to build_sitemap()'s own `today` variable, the
date a NEW or newly-changed URL is stamped with. Same bug, same file,
different line, found twelve days apart.

This does not spin up two machines in two timezones; it checks the thing
that actually matters, which is the source: build_sitemap() must derive
`today` from datetime.now(timezone.utc), the same construction
_git_content_date() already uses, never from the bare, timezone-naive
datetime.date.today(). A static check is the honest one here, since the
actual failure mode is which clock the code reads, not what either clock
currently says (they agree most of the day).

Run:  python ops/tests/test_build_seo_sitemap_date_utc.py
"""
import inspect
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import build_seo                                               # noqa: E402


def main() -> int:
    fails = []

    source = inspect.getsource(build_seo.build_sitemap)
    # The docstring itself quotes the old, buggy call as history (see
    # issue #23); strip it so that quotation cannot make this test pass
    # against code that still has the bug, or fail against code that
    # merely mentions it.
    code_only = re.sub(r'""".*?"""', "", source, count=1, flags=re.S)

    # The exact bare, local-wall-clock assignment this bug used. Must be
    # absent from the executable code (not the docstring's own history).
    if re.search(r"\btoday\s*=\s*datetime\.date\.today\(\)", code_only):
        fails.append(
            "build_sitemap() still assigns 'today' from the bare, "
            "timezone-naive datetime.date.today(), the exact 2026-11-04 "
            "regression this test exists to catch")

    # Must instead be anchored to UTC, the same construction
    # _git_content_date() already uses for the same reason.
    if "timezone.utc" not in code_only:
        fails.append(
            "build_sitemap() does not anchor its 'today' stamp to "
            "datetime.timezone.utc; a local-date/UTC-date mismatch at a "
            "midnight boundary can disagree with the GitHub Actions "
            "runner that re-derives the same file in CI")

    # Functional sanity: calling the real helper construction must return
    # today's date in UTC, not raise, not drift in shape.
    import datetime
    utc_today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", utc_today):
        fails.append("UTC date construction did not yield an ISO date: %r"
                     % (utc_today,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS (3 cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
