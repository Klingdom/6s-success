#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_architecture_workflow_count_current() catches
ARCHITECTURE.md citing two different workflow counts for the same fact, or
either one drifting from the real file count in .github/workflows/.

Found 2026-09-20, this operator, self-arithmetic cross-check pass: section 8
of ARCHITECTURE.md was corrected on 2026-09-13 to say "10 workflows as of
2026-09-13, corrected from 9: `social-drafts.yml` had shipped and was never
added to this list", and named all ten files by name. Five lines later, in
the same section, the sibling bullet still read "9 workflows exist, see
above" (the stale number that same paragraph had just replaced), even
though .github/workflows/ holds 10 real files. One correction landed and a
second citation of the identical fact, right next to it, never got it.

Run:  python ops/tests/test_gate_architecture_workflow_count_current.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

REAL_WORKFLOW_NAMES = [
    "checks.yml", "fulfil-orders.yml", "hourly-brief.yml",
    "linkedin-drafts.yml", "mobile-checks.yml", "publish-image.yml",
    "publish-mcp.yml", "roadmap-report.yml", "social-drafts.yml",
    "status-email.yml",
]

# The actual 2026-09-13/2026-09-20 regression shape: one paragraph correctly
# says 10 and names all ten files, a second, nearby mention still says 9.
STALE_DOC = (
    "# Architecture\n\n"
    "CI exists (**10 workflows as of 2026-09-13, corrected from 9: "
    "`social-drafts.yml` had shipped and was never added to this list**, "
    "under `.github/workflows/`: `checks.yml`, `fulfil-orders.yml`, "
    "`hourly-brief.yml`, `linkedin-drafts.yml`, `mobile-checks.yml`, "
    "`publish-image.yml`, `publish-mcp.yml`, `roadmap-report.yml`, "
    "`social-drafts.yml`, `status-email.yml`).\n\n"
    "- ~~no CI, no `.github` directory, no workflows~~ **9 workflows "
    "exist, see above.**\n"
)

FIXED_DOC = (
    "# Architecture\n\n"
    "CI exists (**10 workflows as of 2026-09-13, corrected from 9: "
    "`social-drafts.yml` had shipped and was never added to this list**, "
    "under `.github/workflows/`: `checks.yml`, `fulfil-orders.yml`, "
    "`hourly-brief.yml`, `linkedin-drafts.yml`, `mobile-checks.yml`, "
    "`publish-image.yml`, `publish-mcp.yml`, `roadmap-report.yml`, "
    "`social-drafts.yml`, `status-email.yml`).\n\n"
    "- ~~no CI, no `.github` directory, no workflows~~ **10 workflows "
    "exist, see above.**\n"
)

# A doc whose named list is missing a real file (an add nobody documented).
MISSING_FROM_LIST_DOC = (
    "# Architecture\n\n"
    "CI exists (**9 workflows**, under `.github/workflows/`: `checks.yml`, "
    "`fulfil-orders.yml`, `hourly-brief.yml`, `linkedin-drafts.yml`, "
    "`mobile-checks.yml`, `publish-image.yml`, `publish-mcp.yml`, "
    "`roadmap-report.yml`, `status-email.yml`)\n"
)


def _run(doc, workflow_names):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "ARCHITECTURE.md"), "w",
                encoding="utf-8").write(doc)
        wf_dir = os.path.join(tmp, ".github", "workflows")
        os.makedirs(wf_dir)
        for name in workflow_names:
            io.open(os.path.join(wf_dir, name), "w",
                    encoding="utf-8").write("name: x\n")
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_architecture_workflow_count_current()
            return list(preflight.FAIL)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def _run_against_real_file(mutate):
    """Back up the real committed ARCHITECTURE.md, apply `mutate` to its
    text, run the gate, then restore the original bytes no matter what,
    proving the gate against the actual file this repository ships rather
    than only a synthetic stand-in."""
    path = os.path.join(ROOT, "ARCHITECTURE.md")
    original = io.open(path, encoding="utf-8").read()
    try:
        mutated = mutate(original)
        assert mutated != original, "mutate() did not change the text"
        io.open(path, "w", encoding="utf-8").write(mutated)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_architecture_workflow_count_current()
        return list(preflight.FAIL)
    finally:
        io.open(path, "w", encoding="utf-8").write(original)
        restored = io.open(path, encoding="utf-8").read()
        assert restored == original, "restore failed to reproduce the original"


def main() -> int:
    fails = []

    # 1. The real regression shape: two different counts for the same
    #    fact in one document. Must fail.
    r = _run(STALE_DOC, REAL_WORKFLOW_NAMES)
    if not r:
        fails.append("STALE_DOC (10 vs 9, both wrong-in-one-direction "
                      "9) was wrongly passed")
    elif "9" not in r[0][1] or "10" not in r[0][1]:
        fails.append("STALE_DOC failed but did not name both the stale "
                      "and the real count: %r" % (r,))

    # 2. Same document with the second mention corrected to agree: must
    #    not fail.
    r = _run(FIXED_DOC, REAL_WORKFLOW_NAMES)
    if r:
        fails.append("FIXED_DOC (both mentions say 10, matching 10 real "
                      "files) was wrongly flagged: %r" % (r,))

    # 3. A single correct count still fails if the real file count later
    #    changes out from under it (a workflow removed, doc not updated).
    r = _run(FIXED_DOC, REAL_WORKFLOW_NAMES[:-1])  # 9 real files now
    if not r:
        fails.append("FIXED_DOC against only 9 real files (one removed) "
                      "was wrongly passed")

    # 4. The document's own named inventory omitting a real file must
    #    fail even when the headline number matches nothing yet.
    r = _run(MISSING_FROM_LIST_DOC, REAL_WORKFLOW_NAMES)
    if not r:
        fails.append("a named list missing a real workflow file "
                      "(social-drafts.yml) was wrongly passed")

    # 5. Fail-then-pass against the real, committed ARCHITECTURE.md:
    #    reintroduce the exact historical defect (the second mention
    #    reverted to "9 workflows exist, see above"), confirm the gate
    #    fails naming it, restore, confirm clean.
    def reintroduce_bug(text):
        needle = (
            '**10 workflows exist, see above (corrected from a stale "9" '
            "here: the section above already counts 10 and names "
            "`social-drafts.yml` as the one this line had not been "
            "updated for). They build and check the site; nothing in the "
            "served page path changed.**"
        )
        replacement = (
            "**9 workflows exist, see above. They build and check the "
            "site; nothing in the served page path changed.**"
        )
        assert needle in text, (
            "the fixed sentence this test expects is not in the real "
            "file; has ARCHITECTURE.md been edited since?")
        return text.replace(needle, replacement)

    r = _run_against_real_file(reintroduce_bug)
    if not r:
        fails.append("reintroducing the real 2026-09-20 defect into the "
                      "committed ARCHITECTURE.md did not fail")
    elif "9" not in r[0][1] or "10" not in r[0][1]:
        fails.append("reintroduced defect failed but message did not "
                      "name both numbers: %r" % (r,))

    # 6. The real, committed, restored ARCHITECTURE.md: clean.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_architecture_workflow_count_current()
    if preflight.FAIL:
        fails.append("the real committed ARCHITECTURE.md (after restore) "
                      "failed: %r" % (preflight.FAIL,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_architecture_workflow_count_current, 6/6 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
