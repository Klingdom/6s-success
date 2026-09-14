#!/usr/bin/env python3
"""
Prove ops/preflight.py's check_no_hardcoded_git_history() catches a test
that fetches an old commit by hash, and leaves an ordinary test alone.

Found 2026-09-14: test_gate_shop_buy_claim_honest.py's own case 5 ran
`git show 94e0ce83:site/shop.html` to fetch the real pre-fix page. It
passed in every sandbox that had already unshallowed onto full history,
then crashed real CI outright (subprocess.CalledProcessError, exit 128,
"fatal: invalid object name '94e0ce83'") on the very next push, because
checks.yml's actions/checkout@v4 takes no fetch-depth and defaults to a
shallow, depth-1 clone: only the tip commit exists, so any older SHA a
test hardcodes is simply not there to show. Reproduced directly by cloning
this repository with --depth 1 and running the exact same command against
it. Fixed by reconstructing the pre-fix text from the live file's own
content instead (undo the known fix with a plain string replace), which
needs no git history at all.

Run:  python ops/tests/test_gate_no_hardcoded_git_history.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight  # noqa: E402

SHELL_STYLE = '''
import subprocess
pre_fix = subprocess.run(
    "git show 94e0ce83:site/shop.html", shell=True,
    capture_output=True, text=True, check=True,
).stdout
'''

LIST_STYLE = '''
import subprocess
pre_fix = subprocess.run(
    ["git", "show", "94e0ce83:site/shop.html"],
    cwd=ROOT, capture_output=True, text=True, check=True,
).stdout
'''

GIT_LOG_STYLE = '''
import subprocess
out = subprocess.run(
    ["git", "log", "94e0ce83", "--format=%s"],
    capture_output=True, text=True, check=True,
).stdout
'''

FIXED_RECONSTRUCTION = '''
old_lede = "Everything here can be bought today and delivered today."
new_lede = "Almost everything here can be bought today and delivered today."
pre_fix = live_text.replace(new_lede, old_lede)
'''

ORDINARY_GIT_USE = '''
import subprocess
# HEAD and relative refs are always present, shallow or not.
sha = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True, check=True,
).stdout.strip()
current = subprocess.run(
    ["git", "show", "HEAD:site/shop.html"],
    capture_output=True, text=True, check=True,
).stdout
'''


def main() -> int:
    bad = []

    if not preflight.check_no_hardcoded_git_history(SHELL_STYLE):
        bad.append("case 1: a shell-string `git show <sha>:path` must be caught")

    if not preflight.check_no_hardcoded_git_history(LIST_STYLE):
        bad.append("case 2: a subprocess list ['git', 'show', '<sha>:path'] "
                    "must be caught")

    if not preflight.check_no_hardcoded_git_history(GIT_LOG_STYLE):
        bad.append("case 3: `git log <sha>` on a specific old commit must "
                    "be caught, not only `git show`")

    if preflight.check_no_hardcoded_git_history(FIXED_RECONSTRUCTION):
        bad.append("case 4: reconstructing old text with a plain string "
                    "replace, no git at all, must never be flagged")

    if preflight.check_no_hardcoded_git_history(ORDINARY_GIT_USE):
        bad.append("case 5: `git rev-parse HEAD` and `git show HEAD:path` "
                    "are always safe under a depth-1 checkout and must "
                    "never be flagged")

    live_path = os.path.join(ROOT, "ops", "tests",
                              "test_gate_shop_buy_claim_honest.py")
    live_text = open(live_path, encoding="utf-8").read()
    if preflight.check_no_hardcoded_git_history(live_text):
        bad.append("case 6: the real, current "
                    "test_gate_shop_buy_claim_honest.py must pass clean; "
                    "its own fix for this exact defect should not still "
                    "trip the gate it caused to be written")

    for b in bad:
        print("  FAIL " + b)
    if not bad:
        print("  ok  6 of 6 cases pass: shell-string and list forms of "
              "`git show`/`git log` on a hardcoded old SHA are both caught, "
              "a plain-string reconstruction and ordinary HEAD-relative git "
              "use are never flagged, and the real fixed test file is clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
