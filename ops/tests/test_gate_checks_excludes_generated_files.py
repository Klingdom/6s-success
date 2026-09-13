#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_checks_excludes_generated_files() catches
checks.yml's push.paths losing the exclusions for ops/state.json,
ops/dashboard.html and ops/NIGHTLY-LOG.md, and leaves a correct file alone.

Found 2026-09-13, this operator, reading the real commit diffs behind that
day's multi-hour CI outage: ops/dashboard.py writes the first two on every
cycle (CLAUDE.md step 11b, mandatory) and the log gets one entry every cycle
too, all three under ops/**, so a commit touching only bookkeeping output
started its own full Checks run exactly like a real ops/*.py change.
Combined with checks.yml's own cancel-in-progress concurrency group, that
shape of commit repeatedly cancelled whatever real fix's own verification
run was still in flight seconds earlier. Fixed by excluding the three paths;
this test protects that fix from silently regressing.

Run:  python ops/tests/test_gate_checks_excludes_generated_files.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

CORRECT = """\
on:
  push:
    branches: [main]
    paths:
      - 'ops/**'
      - '.github/workflows/checks.yml'
      - '!ops/state.json'
      - '!ops/dashboard.html'
      - '!ops/NIGHTLY-LOG.md'
  pull_request:
    paths:
      - 'ops/**'
  workflow_dispatch:

jobs:
  checks:
    runs-on: ubuntu-latest
"""

MISSING_ALL = """\
on:
  push:
    branches: [main]
    paths:
      - 'ops/**'
      - '.github/workflows/checks.yml'
  pull_request:
    paths:
      - 'ops/**'
  workflow_dispatch:

jobs:
  checks:
    runs-on: ubuntu-latest
"""

MISSING_ONE = """\
on:
  push:
    branches: [main]
    paths:
      - 'ops/**'
      - '.github/workflows/checks.yml'
      - '!ops/state.json'
      - '!ops/dashboard.html'
  pull_request:
    paths:
      - 'ops/**'
  workflow_dispatch:

jobs:
  checks:
    runs-on: ubuntu-latest
"""

NO_OPS_TRIGGER = """\
on:
  push:
    branches: [main]
    paths:
      - 'site/**'
  workflow_dispatch:

jobs:
  checks:
    runs-on: ubuntu-latest
"""


def _run(text: str):
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "checks.yml")
        io.open(path, "w", encoding="utf-8").write(text)
        preflight.FAIL, preflight.WARN = [], []
        preflight.gate_checks_excludes_generated_files(wf_path=path)
        return list(preflight.FAIL)
    finally:
        shutil.rmtree(tmp)


def test_correct_file_passes():
    fails = _run(CORRECT)
    assert not fails, "a correctly-excluded checks.yml should pass: %r" % (fails,)


def test_missing_all_excludes_fails():
    fails = _run(MISSING_ALL)
    assert fails, "checks.yml with none of the three excludes should fail"
    msg = fails[0][1]
    assert "ops/state.json" in msg
    assert "ops/dashboard.html" in msg
    assert "ops/NIGHTLY-LOG.md" in msg


def test_missing_one_exclude_fails_by_name():
    fails = _run(MISSING_ONE)
    assert fails, "checks.yml missing one exclude should still fail"
    msg = fails[0][1]
    assert "ops/NIGHTLY-LOG.md" in msg, \
        "the failure should name the specific missing path: %r" % (msg,)
    assert "ops/state.json" not in msg
    assert "ops/dashboard.html" not in msg


def test_no_ops_trigger_is_a_different_failure():
    """If push.paths no longer even mentions ops/**, that is a bigger
    regression than this gate exists to catch, but it must still fail
    loudly rather than silently pass because none of the excludes matched
    anything to check against."""
    fails = _run(NO_OPS_TRIGGER)
    assert fails, "a checks.yml that dropped ops/** entirely should fail"


def test_real_repository_is_clean():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_checks_excludes_generated_files()
    fails = list(preflight.FAIL)
    assert not fails, "the real checks.yml should be clean: %r" % (fails,)


TESTS = [test_correct_file_passes, test_missing_all_excludes_fails,
         test_missing_one_exclude_fails_by_name,
         test_no_ops_trigger_is_a_different_failure,
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
