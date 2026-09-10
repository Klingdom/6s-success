#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_stray_probe_files() both fails loudly on a
leftover probe/fixture file and actually deletes it, and that it runs first
in main()'s own gate order, ahead of gate_existing and gate_tests.

Found 2026-09-10, this operator: a preflight run killed mid-audit (SIGTERM,
outer timeout) left site/zones/_visual_probe.html sitting on disk. The very
next preflight run hit gate_existing (audit_pages.py's "pages" gate) and
gate_tests (test_gate_zone_short_answer.py) BEFORE it ever reached
gate_no_stray_probe_files, which sat much later in main()'s own list. Both
misread the stray file as a real, malformed zone page and failed on that
symptom, naming nothing about the real cause; only cleaned up somewhere
between then and a third rerun, and this file's own docstring already
described exactly this shape of bug for two other cases (2026-09-03,
2026-09-05) without anyone noticing the gate itself still ran too late to
protect the gates ahead of it. Fixed by moving the run_gate() call to the
top of main(), right after bootstrap_fresh_sandbox(), and having the gate
delete what it finds after reporting it, so gate_existing/gate_tests in the
same run see a clean tree instead of inheriting the same failure twice
under two different, more confusing names.

Run:  python ops/tests/test_gate_no_stray_probe_files.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_with_stray(name):
    tmp = tempfile.mkdtemp()
    zones = os.path.join(tmp, "zones")
    os.makedirs(zones)
    path = None
    if name is not None:
        path = os.path.join(zones, name)
        io.open(path, "w", encoding="utf-8").write("<html></html>")
    old_site = preflight.SITE
    preflight.SITE = tmp
    preflight.FAIL, preflight.WARN = [], []
    try:
        preflight.gate_no_stray_probe_files()
        still_there = path is not None and os.path.exists(path)
        return list(preflight.FAIL), still_there
    finally:
        preflight.SITE = old_site


def test_clean_tree_passes():
    fails, _ = _run_with_stray(None)
    assert fails == [], f"expected no failure on a clean tree, got {fails}"


def test_stray_visual_probe_fails_and_is_deleted():
    fails, still_there = _run_with_stray("_visual_probe.html")
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert "_visual_probe.html" in fails[0][1], fails[0][1]
    assert not still_there, "gate must delete the stray file it just reported"


def test_stray_fixture_file_also_caught():
    fails, still_there = _run_with_stray("_audit_catalog_fixture.html")
    assert len(fails) == 1 and fails[0][0] == "stray-probe-files", fails
    assert not still_there


def test_runs_before_gate_existing_and_gate_tests_in_main():
    src = io.open(os.path.join(ROOT, "ops", "preflight.py"),
                  encoding="utf-8").read()
    start = src.index("\ndef main(")
    body = src[start:]
    probe_pos = body.index("run_gate(gate_no_stray_probe_files)")
    existing_pos = body.index("run_gate(gate_existing")
    tests_pos = body.index("run_gate(gate_tests)")
    assert probe_pos < existing_pos, (
        "gate_no_stray_probe_files must run before gate_existing, or a "
        "stray file from an earlier killed run pollutes the pages gate "
        "again before this gate ever gets to clear it")
    assert probe_pos < tests_pos, (
        "gate_no_stray_probe_files must run before gate_tests, same reason")
    assert body.count("run_gate(gate_no_stray_probe_files)") == 1, (
        "the gate must be wired into main() exactly once")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for t in tests:
        t()
        ok += 1
    print(f"OK: gate_no_stray_probe_files, {ok}/{len(tests)} checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
