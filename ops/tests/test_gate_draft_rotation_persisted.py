#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_draft_rotation_persisted() catches a draft
mailer workflow that "records" a served post only on its own runner's disk.

Found 2026-09-15: ops/corpus-rotation.json had not moved since 2026-09-06,
9 real days after linkedin-drafts.yml's own scheduled runs kept firing
(confirmed live against real, non-skipped sends on 2026-09-09/10/12/13/14).
ops/corpus_posts.py's take(record=True) writes the rotation to disk, but
neither linkedin-drafts.yml nor social-drafts.yml ever committed it back:
a GitHub Actions checkout is thrown away when the job ends, so every run
re-read the same committed served-set and, selection being purely
deterministic on that set, served the identical posts every single time.
Fixed by adding a commit-and-push step (mirroring hourly-brief.yml's own
already-proven pattern) and `permissions.contents: write` to both
workflows. This gate stops either regressing silently.

Run:  python ops/tests/test_gate_draft_rotation_persisted.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

GOOD = """\
name: LinkedIn drafts
on:
  schedule:
    - cron: '47 10 * * *'
jobs:
  drafts:
    permissions:
      contents: write
      actions: read
    steps:
      - name: Write three drafts and send them
        run: python ops/linkedin_drafts.py --send "$OWNER_EMAIL"
      - name: Persist the rotation so tomorrow does not repeat today
        run: |
          git add ops/corpus-rotation.json
          git commit -m 'advance rotation'
          git push origin HEAD:main || true
"""

NO_WRITE_PERMISSION = """\
name: LinkedIn drafts
on:
  schedule:
    - cron: '47 10 * * *'
jobs:
  drafts:
    permissions:
      contents: read
      actions: read
    steps:
      - name: Write three drafts and send them
        run: python ops/linkedin_drafts.py --send "$OWNER_EMAIL"
      - name: Persist the rotation so tomorrow does not repeat today
        run: |
          git add ops/corpus-rotation.json
          git commit -m 'advance rotation'
          git push origin HEAD:main || true
"""

# The real pre-fix shape: write permission never even requested, and no
# step touches the rotation file or pushes at all.
NO_PERSIST_STEP = """\
name: LinkedIn drafts
on:
  schedule:
    - cron: '47 10 * * *'
jobs:
  drafts:
    permissions:
      contents: read
      actions: read
    steps:
      - name: Write three drafts and send them
        run: python ops/linkedin_drafts.py --send "$OWNER_EMAIL"
"""

# permissions correct, but the "persist" step only pushes something else,
# never actually touching the rotation file: a plausible future regression
# (e.g. a step that commits the command deck but not this file) that a
# bare "does it push anything" check would miss.
WRITE_PERMISSION_BUT_WRONG_FILE = """\
name: LinkedIn drafts
on:
  schedule:
    - cron: '47 10 * * *'
jobs:
  drafts:
    permissions:
      contents: write
      actions: read
    steps:
      - name: Write three drafts and send them
        run: python ops/linkedin_drafts.py --send "$OWNER_EMAIL"
      - name: Regenerate the command deck
        run: |
          git add EXECUTIVE-DASHBOARD-LIVE.md
          git commit -m 'deck'
          git push origin HEAD:main || true
"""


def make(tmpdir: str, contents: dict) -> str:
    # A fresh, uniquely named subdirectory per call: reusing one directory
    # across cases would leak a file a prior case wrote (e.g. case 4's
    # linkedin-drafts.yml surviving into case 5's "missing entirely" check).
    d = tempfile.mkdtemp(dir=tmpdir)
    for name, text in contents.items():
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(text)
    return d


def run() -> int:
    cases = 0
    failures = []

    def check(label, got, want_substring=None, want_empty=False):
        nonlocal cases
        cases += 1
        if want_empty:
            if got:
                failures.append(f"{label}: expected clean, got {got}")
            return
        if not got:
            failures.append(f"{label}: expected a problem, got none")
            return
        if want_substring and not any(want_substring in g for g in got):
            failures.append(f"{label}: expected {want_substring!r} in {got}")

    with tempfile.TemporaryDirectory() as tmp:
        # 1. Both workflows fixed: clean.
        d = make(tmp, {"linkedin-drafts.yml": GOOD, "social-drafts.yml": GOOD})
        check("both good", preflight.check_draft_rotation_persisted(d),
              want_empty=True)

        # 2. permissions.contents left at read: caught by name, even though
        #    a persist step exists (it could never actually push).
        d = make(tmp, {"linkedin-drafts.yml": NO_WRITE_PERMISSION,
                        "social-drafts.yml": GOOD})
        check("no write permission",
              preflight.check_draft_rotation_persisted(d),
              want_substring="contents: write")

        # 3. The real pre-fix shape: no persist step, no write permission.
        d = make(tmp, {"linkedin-drafts.yml": NO_PERSIST_STEP,
                        "social-drafts.yml": GOOD})
        check("no persist step at all",
              preflight.check_draft_rotation_persisted(d),
              want_substring="contents: write")

        # 4. Write permission granted, but nothing actually touches the
        #    rotation file: the exact "looks fixed, is not" shape.
        d = make(tmp, {"linkedin-drafts.yml": WRITE_PERMISSION_BUT_WRONG_FILE,
                        "social-drafts.yml": GOOD})
        check("push exists but never touches the rotation file",
              preflight.check_draft_rotation_persisted(d),
              want_substring="corpus-rotation.json")

        # 5. A workflow file missing entirely.
        d = make(tmp, {"social-drafts.yml": GOOD})
        check("linkedin-drafts.yml missing",
              preflight.check_draft_rotation_persisted(d),
              want_substring="not found")

    # 6. Against the real, committed, fixed workflow files: must be clean.
    real_dir = os.path.join(ROOT, ".github", "workflows")
    real = preflight.check_draft_rotation_persisted(real_dir)
    check("real committed workflows", real, want_empty=True)

    if failures:
        print(f"FAIL: {len(failures)} of {cases} case(s)")
        for f in failures:
            print(" -", f)
        return 1
    print(f"OK: {cases}/{cases} cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(run())
