#!/usr/bin/env python3
"""
Prove CI installs eslint, because without it one gate silently never runs.

WHY THIS EXISTS
---------------
gate_no_dangling_js_references scans every shipped script for a reference to
something never defined. That is the exact shape of the 2026-09-23 defect which
broke the mobile nav and all .reveal content across the site: a stray call to a
deleted function.

The gate is careful in the right way. With eslint absent it warns UNCHECKED
rather than passing clean, exactly as CLAUDE.md 0.4 requires. What nobody
noticed is that eslint was absent from the CI runner, so every CI run since the
gate was written reported it unchecked and the scan had never actually happened
there. A check that is correct about its own ignorance is still a check that is
not running.

Verified 2026-09-29 by replanting the original paint() call into a scratch copy
of site.js: with eslint present the gate fails by name and line; without it, it
reports unchecked.

Run:  python ops/tests/test_ci_installs_eslint.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WF = os.path.join(ROOT, ".github", "workflows", "checks.yml")


def _workflow() -> str:
    return io.open(WF, encoding="utf-8", errors="replace").read()


def case_checks_workflow_installs_eslint():
    s = _workflow()
    assert re.search(r"npm install -g eslint", s), (
        "checks.yml no longer installs eslint, so "
        "gate_no_dangling_js_references reports UNCHECKED on every CI run and "
        "shipped JavaScript is not actually being scanned")


def case_node_is_set_up_before_eslint():
    """npm install without a node runtime fails the step, not the gate."""
    s = _workflow()
    assert "actions/setup-node" in s, "no node runtime set up for eslint"
    assert s.index("actions/setup-node") < s.index("npm install -g eslint"), (
        "node is set up after eslint is installed")


def case_eslint_is_pinned():
    """An unpinned major could change the config format under the gate.

    The gate writes its own flat eslint.config.js, which is 9+ only. A bare
    `npm install -g eslint` would one day pull a major that reads it
    differently, and the failure would look like a code defect rather than a
    tooling change.
    """
    s = _workflow()
    m = re.search(r"npm install -g eslint@(\d+)", s)
    assert m, "eslint is installed without a pinned major"
    assert int(m.group(1)) >= 9, (
        "eslint " + m.group(1) + " predates flat config, which the gate writes")


def case_the_gate_still_warns_when_eslint_is_absent():
    """The safe half: no eslint must never read as clean."""
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import shutil
    import preflight as P
    real = shutil.which
    shutil.which = lambda name, *a, **k: None if name == "eslint" else real(name, *a, **k)
    try:
        P.FAIL.clear()
        P.WARN.clear()
        P.gate_no_dangling_js_references()
        assert not P.FAIL, P.FAIL
        assert P.WARN and "nchecked" in P.WARN[0][1], P.WARN
    finally:
        shutil.which = real
        P.FAIL.clear()
        P.WARN.clear()


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
