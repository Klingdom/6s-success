#!/usr/bin/env python3
"""Prepend a dated entry to ops/NIGHTLY-LOG.md at the correct position.

ops/NIGHTLY-LOG.md's own header says "newest first", and
gate_nightly_log_ordering() in preflight.py enforces it, but nothing before
this script actually wrote the file: every cycle has hand-edited it. The
same mistake has recurred across many unrelated cycles (first found
2026-09-05, again 2026-09-18, 2026-09-29, 2026-10-03, 2026-10-10): the
operating prompt's STEP 1 says to read "the last four entries", a session
reads that as the physical end of the file (the natural reading, and the
one a plain `tail` gives), concludes today has not started yet, and
APPENDS its own entry there instead of prepending it to the top, burying
a real cycle's findings behind the entire legacy history. Each time, a
later preflight --deep run (or a failed CI check) has had to catch it and
a cycle has had to hand-fix it. Root cause before a sixth retelling: this
script removes the hand-edit step, so there is no "end of the file" to
misread in the first place. Use it instead of editing the file directly.

Usage:
    python ops/nightly_log.py --title "2026-10-10, PM check-in (...)" --body-file /tmp/entry.md
    python ops/nightly_log.py --title "..." --body "**Did:** ..."
    echo "**Did:** ..." | python ops/nightly_log.py --title "..."

--title is the heading text without the leading "## ". The body is
written as-is below it, with one blank line in between and a trailing
blank line before the next entry.
"""
import argparse
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "ops", "NIGHTLY-LOG.md")

HEADER_FIRST_LINE = "# Nightly log"
HEADER_THIRD_PREFIX = "One entry per unattended pass"


def prepend_entry(path: str, title: str, body: str) -> str:
    """Insert '## <title>\\n\\n<body>\\n' directly below the file's
    three-line header, ahead of every existing entry. Returns the new
    file text; does not write it (callers write it, so this stays
    testable against a string without touching disk).
    """
    text = io.open(path, encoding="utf-8").read()
    lines = text.split("\n")
    if len(lines) < 3 or not lines[0].startswith(HEADER_FIRST_LINE) \
            or not lines[2].startswith(HEADER_THIRD_PREFIX):
        raise ValueError(
            "ops/NIGHTLY-LOG.md's header does not match the expected "
            "three-line shape ('%s', blank, '%s...'); refusing to guess "
            "where the top is. Fix the header, or prepend this one entry "
            "by hand and fix the generator after." % (
                HEADER_FIRST_LINE, HEADER_THIRD_PREFIX))
    header = "\n".join(lines[:3])
    rest = "\n".join(lines[3:]).lstrip("\n")
    title = title.strip()
    if title.startswith("## "):
        title = title[3:].strip()
    body = body.strip("\n")
    entry = "## %s\n\n%s\n" % (title, body)
    return header + "\n\n" + entry + "\n" + rest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--title", required=True,
                     help="Heading text, without the leading '## '.")
    ap.add_argument("--body", help="Entry body text.")
    ap.add_argument("--body-file",
                     help="Read the entry body from this file instead of "
                          "--body.")
    args = ap.parse_args()
    if args.body_file:
        body = io.open(args.body_file, encoding="utf-8").read()
    elif args.body is not None:
        body = args.body
    else:
        body = sys.stdin.read()
    if not body.strip():
        print("Refusing to prepend an empty entry body.", file=sys.stderr)
        return 1
    new_text = prepend_entry(LOG_PATH, args.title, body)
    io.open(LOG_PATH, "w", encoding="utf-8").write(new_text)
    print("Prepended %r to %s" % (args.title, LOG_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
