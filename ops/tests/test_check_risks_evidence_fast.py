"""Prove ops/check_risks_evidence_fast.py actually catches a stale RISKS.md
citation, and stays silent on a current one, without needing gate_tests or
anything after it in preflight.py's own call order.

Found 2026-11-03: RISK-0012's `forms_dead=NNN` citation went stale at least
six times in one day, each time only caught by CI, because this sandbox's
own gate_tests hangs on a headless Chromium check and gate_risks_evidence_
current sits after it in preflight.py's call order, so a local run never
reaches it before push. ops/check_risks_evidence_fast.py (mirroring
ops/check_nightly_log_fast.py's own reasoning) calls the gate directly,
skipping gate_tests entirely, so it can run in the pre-push hook. This test
proves the wrapper's exit code and output, not the gate's own logic, which
ops/tests/test_gate_risks_evidence_tree_derived.py already covers.

Run:  python ops/tests/test_check_risks_evidence_fast.py
"""
import importlib.util
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = os.path.dirname(HERE)
sys.path.insert(0, OPS)
sys.argv = ["preflight.py"]

import preflight as P  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "check_risks_evidence_fast", os.path.join(OPS, "check_risks_evidence_fast.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

FORM = '<form onsubmit="return false"></form>'


def _run(citation, forms_on_disk, state_forms_dead=None):
    if state_forms_dead is None:
        state_forms_dead = citation
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "ops"))
        os.makedirs(os.path.join(root, "site", "a"))
        io.open(os.path.join(root, "RISKS.md"), "w", encoding="utf-8").write(
            "evidence:\n  - every form on the site is inert (forms_dead=%s)\n"
            % citation)
        json.dump({"forms_dead": state_forms_dead},
                   io.open(os.path.join(root, "ops", "state.json"), "w"))
        for n in range(forms_on_disk):
            io.open(os.path.join(root, "site", "a", "p%d.html" % n), "w",
                    encoding="utf-8").write(FORM)
        old_root = P.ROOT
        P.ROOT = root
        C.preflight.ROOT = root
        try:
            return C.main()
        finally:
            P.ROOT = old_root
            C.preflight.ROOT = old_root


def test_current_citation_passes():
    assert _run(3, 3) == 0


def test_stale_citation_fails():
    # Cited matches neither the tree (3 real forms) nor the stale snapshot
    # (5), the only case the gate itself treats as a real drift.
    assert _run(2, 3, state_forms_dead=5) == 1


def main():
    tests = [test_current_citation_passes, test_stale_citation_fails]
    bad = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            bad.append("%s: %s" % (t.__name__, e))
    if bad:
        print("FAIL: check_risks_evidence_fast wrapper")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: check_risks_evidence_fast wrapper, %d/%d" % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
