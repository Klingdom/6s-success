#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_image_prompts_tier0_count_honest() also
catches the retired "nine tier-0 images" count surviving in STATUS.md or
BACKLOG-2026-H2.md after the real count moved to six.

Found 2026-09-12: the gate already checked content/images/prompts/
tier-0-prompts.md itself (fixed 2026-09-07, when tier 0 shrank from nine
images to six), but two live, Phil-facing action items, STATUS.md's P3 and
BACKLOG-2026-H2.md's owner checklist item 4, both still read "the nine
tier-0 images" five days later. The source was corrected; these two
downstream copies never were. Extended the same gate to read both files
directly and fail if either still spells out a count that does not match
the real one in tier-0-prompts.md.

Run:  python ops/tests/test_gate_tier0_count_downstream.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

PROMPTS_FILE = (
    "# Start here: 6 images\n\n"
    "**whole first batch.** 6 images, one evening\n\n"
    "6 images. Style anchor v2.\n"
)

STALE_STATUS = "## P3: Publish the ten LinkedIn posts and generate the nine tier-0 images (backlog 3.1, 3.3)\n"
FIXED_STATUS = "## P3: Publish the ten LinkedIn posts and generate the six tier-0 images (backlog 3.1, 3.3)\n"

STALE_BACKLOG = "4. **Generate the nine tier-0 images** (3.3). Prompts ready.\n"
FIXED_BACKLOG = "4. **Generate the six tier-0 images** (3.3). Prompts ready.\n"

# A status entry honestly quoting the old, retired wording while describing
# the fix itself (exactly what this gate's own real STATUS.md entry does)
# must not read as a live restatement of the stale count.
QUOTED_HISTORY_STATUS = (
    '## P3: still said "generate the nine tier-0 images," now fixed to six.\n'
)


def _run(status_text, backlog_text):
    tmp = tempfile.mkdtemp()
    prompts_dir = os.path.join(tmp, "content", "images", "prompts")
    os.makedirs(prompts_dir)
    io.open(os.path.join(prompts_dir, "tier-0-prompts.md"), "w",
            encoding="utf-8").write(PROMPTS_FILE)
    io.open(os.path.join(tmp, "STATUS.md"), "w",
            encoding="utf-8").write(status_text)
    io.open(os.path.join(tmp, "BACKLOG-2026-H2.md"), "w",
            encoding="utf-8").write(backlog_text)

    old_root = preflight.ROOT
    preflight.ROOT = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_image_prompts_tier0_count_honest()
        return list(preflight.FAIL)
    finally:
        preflight.ROOT = old_root


def main():
    cases = [
        ("both files current", FIXED_STATUS, FIXED_BACKLOG, 0),
        ("STATUS.md stale", STALE_STATUS, FIXED_BACKLOG, 1),
        ("BACKLOG-2026-H2.md stale", FIXED_STATUS, STALE_BACKLOG, 1),
        ("both stale", STALE_STATUS, STALE_BACKLOG, 2),
        ("quoted history in STATUS.md, not a live claim",
         QUOTED_HISTORY_STATUS, FIXED_BACKLOG, 0),
    ]
    failures = 0
    for name, status_text, backlog_text, want in cases:
        got = _run(status_text, backlog_text)
        ok = len(got) == want
        if not ok:
            failures += 1
        print("%s  %-28s want %d fail(s), got %d" %
              ("ok  " if ok else "FAIL", name, want, len(got)))
        for g, m in got:
            print("       %s: %s" % (g, m[:100]))

    if failures:
        print("\n%d of %d case(s) failed" % (failures, len(cases)))
        return 1
    print("\n%d of %d case(s) passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
