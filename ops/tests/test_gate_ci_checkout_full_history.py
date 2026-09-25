#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_ci_checkout_full_history() catches a shallow
(default depth-1) actions/checkout step in checks.yml or publish-image.yml,
and leaves a correct one alone.

Found live 2026-09-25, run 36085673021 (commit 41cce0e5): checks.yml's
actions/checkout@v4 step had no fetch-depth, so ops/affiliate_report.py's
inputs_date() (git log -1 -- <path>, looking thousands of commits back for
ops/affiliate-accounts.json / ops/affiliate-catalogue.csv) found nothing in
the shallow history and fell back to the checked-out file's mtime, always
"now". Every run after that regenerated a report that differed from the
committed one, failing gate_generator_ownership on every push. Fixed by
adding fetch-depth: 0 to both workflows that run preflight.py; this test
protects that fix from silently regressing.

Run:  python ops/tests/test_gate_ci_checkout_full_history.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

FULL_HISTORY = """\
name: Checks
on:
  push:
    branches: [main]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Preflight
        run: python3 ops/preflight.py
"""

SHALLOW_DEFAULT = """\
name: Checks
on:
  push:
    branches: [main]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Preflight
        run: python3 ops/preflight.py
"""

SHALLOW_EXPLICIT = """\
name: Checks
on:
  push:
    branches: [main]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 50

      - name: Preflight
        run: python3 ops/preflight.py
"""

NO_CHECKOUT = """\
name: Checks
on:
  push:
    branches: [main]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - name: Preflight
        run: python3 ops/preflight.py
"""


def _run(checks_text, publish_text):
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "checks.yml"), "w",
                encoding="utf-8").write(checks_text)
        io.open(os.path.join(tmp, "publish-image.yml"), "w",
                encoding="utf-8").write(publish_text)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_ci_checkout_full_history(wf_dir=tmp)
        return list(preflight.FAIL)
    finally:
        shutil.rmtree(tmp)


def test_both_full_history_passes():
    fails = _run(FULL_HISTORY, FULL_HISTORY)
    assert not fails, "fetch-depth: 0 on both should pass: %r" % (fails,)


def test_checks_shallow_default_fails_by_name():
    fails = _run(SHALLOW_DEFAULT, FULL_HISTORY)
    assert fails, "a bare checkout with no fetch-depth should fail"
    msg = fails[0][1]
    assert "checks.yml" in msg and "fetch-depth" in msg


def test_publish_image_shallow_default_fails_by_name():
    fails = _run(FULL_HISTORY, SHALLOW_DEFAULT)
    assert fails, "publish-image.yml with no fetch-depth should fail"
    msg = fails[0][1]
    assert "publish-image.yml" in msg and "fetch-depth" in msg


def test_shallow_explicit_depth_fails():
    """A bounded depth (even a generous one) is still wrong here: these
    inputs can go thousands of commits between real edits, so anything
    short of full history can reproduce the exact bug this gate exists to
    catch."""
    fails = _run(SHALLOW_EXPLICIT, FULL_HISTORY)
    assert fails, "fetch-depth: 50 should not satisfy this gate"


def test_missing_checkout_step_fails():
    fails = _run(NO_CHECKOUT, FULL_HISTORY)
    assert fails, "a workflow with no checkout step at all should fail"
    msg = fails[0][1]
    assert "no actions/checkout step" in msg


def test_missing_workflow_file_is_skipped_not_crashed():
    """A workflow this gate does not find on disk is not this gate's
    problem to report; some other gate owns "does the file exist"."""
    tmp = tempfile.mkdtemp()
    try:
        io.open(os.path.join(tmp, "checks.yml"), "w",
                encoding="utf-8").write(FULL_HISTORY)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_ci_checkout_full_history(wf_dir=tmp)
        fails = list(preflight.FAIL)
        assert not fails, "a missing sibling workflow should not fail this gate: %r" % (fails,)
    finally:
        shutil.rmtree(tmp)


def test_real_repository_is_clean():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_ci_checkout_full_history()
    fails = list(preflight.FAIL)
    assert not fails, "the real workflows should be clean: %r" % (fails,)


TESTS = [test_both_full_history_passes,
         test_checks_shallow_default_fails_by_name,
         test_publish_image_shallow_default_fails_by_name,
         test_shallow_explicit_depth_fails,
         test_missing_checkout_step_fails,
         test_missing_workflow_file_is_skipped_not_crashed,
         test_real_repository_is_clean]


def main():
    n = 0
    for t in TESTS:
        t()
        n += 1
    print("  %d of %d cases pass" % (n, len(TESTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
