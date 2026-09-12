#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_data_sources_current() catches DATA-SOURCES.md
claiming GitHub or Analytics are UNVERIFIED, and catches the file still
reading as its original, never-updated 2026-08-17 bootstrap text.

Found 2026-09-12: DATA-SOURCES.md's Section 116 ("Current Source State")
and its Section 5 registry table had read a blanket UNVERIFIED for every
source since the file's creation, unchanged even as GitHub (used every
cycle via the API) and Analytics (real traffic figures read directly from
the production Umami database, GOALS.md O1, three separate dated reads)
were each verified repeatedly elsewhere in this repository. The same
"source corrected, artifact never re-derived" class this repository's own
log names as dominant, here in the one document whose purpose is to say
which sources can be trusted. Fixed by hand; this gate stops the
correction silently regressing back to the original blanket claim.

Run:  python ops/tests/test_gate_data_sources_current.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

FIXED = (
    "# Data Sources\n\n"
    "# 116. Current Source State\n\n"
    "**Corrected 2026-09-12.** This section described the state at the "
    "file's creation and was never updated.\n\n"
    "**GitHub:** VERIFIED, used every cycle via the API.\n"
    "**Analytics:** VERIFIED, real traffic figures read directly from the "
    "production Umami database.\n"
)

STALE_GITHUB = (
    "# Data Sources\n\n"
    "# 116. Current Source State\n\n"
    "**Corrected 2026-09-12.**\n\n"
    "**GitHub:** UNVERIFIED\n"
    "**Analytics:** VERIFIED, real traffic figures read directly.\n"
)

STALE_ANALYTICS = (
    "# Data Sources\n\n"
    "# 116. Current Source State\n\n"
    "**Corrected 2026-09-12.**\n\n"
    "**GitHub:** VERIFIED, used every cycle via the API.\n"
    "**Analytics:** UNVERIFIED\n"
)

ORIGINAL_BOOTSTRAP = (
    "# Data Sources\n\n"
    "# 116. Current Source State\n\n"
    "At creation of this document, actual production integrations have "
    "**not been verified within this file**.\n\n"
    "**GitHub:** UNVERIFIED\n"
    "**Analytics:** UNVERIFIED\n"
)


def _run(body):
    tmp = tempfile.mkdtemp()
    io.open(os.path.join(tmp, "DATA-SOURCES.md"), "w",
            encoding="utf-8").write(body)
    old_root = preflight.ROOT
    preflight.ROOT = tmp
    old_fail, old_warn = list(preflight.FAIL), list(preflight.WARN)
    preflight.FAIL.clear()
    preflight.WARN.clear()
    try:
        preflight.gate_data_sources_current()
        failed = bool(preflight.FAIL)
        msg = preflight.FAIL[0][1] if preflight.FAIL else ""
    finally:
        preflight.ROOT = old_root
        preflight.FAIL[:] = old_fail
        preflight.WARN[:] = old_warn
    return failed, msg


def main():
    cases = [
        ("fixed file passes clean", FIXED, False, None),
        ("stale GitHub claim fails", STALE_GITHUB, True, "GitHub"),
        ("stale Analytics claim fails", STALE_ANALYTICS, True, "Analytics"),
        ("original bootstrap text fails", ORIGINAL_BOOTSTRAP, True, "GitHub"),
    ]
    failures = []
    for name, body, want_fail, want_substr in cases:
        got_fail, msg = _run(body)
        if got_fail != want_fail:
            failures.append(
                "%s: expected failed=%s, got failed=%s (msg=%r)"
                % (name, want_fail, got_fail, msg))
        elif want_fail and want_substr not in msg:
            failures.append(
                "%s: failure message %r did not name %r"
                % (name, msg, want_substr))

    missing = _run("# Data Sources\n\nno such file here\n")
    # A file with neither pattern nor the bootstrap phrase should pass.
    if missing[0]:
        failures.append("file with no matching claims wrongly failed: %r"
                         % (missing[1],))

    no_file = tempfile.mkdtemp()
    old_root = preflight.ROOT
    preflight.ROOT = no_file
    old_fail = list(preflight.FAIL)
    preflight.FAIL.clear()
    try:
        preflight.gate_data_sources_current()
        no_file_failed = bool(preflight.FAIL)
        no_file_msg = preflight.FAIL[0][1] if preflight.FAIL else ""
    finally:
        preflight.ROOT = old_root
        preflight.FAIL[:] = old_fail
    if not no_file_failed or "does not exist" not in no_file_msg:
        failures.append("missing DATA-SOURCES.md should fail naming the "
                         "missing file, got: %r" % (no_file_msg,))

    total = len(cases) + 2
    if failures:
        print("FAIL: %d of %d cases" % (len(failures), total))
        for f in failures:
            print("  -", f)
        return 1
    print("PASS: %d of %d cases" % (total, total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
