"""gate_risks_evidence_current accepts a tree-derived count the snapshot lags.

Found 2026-10-29: every new page adds one footer form, so a commit adding a
page could cite forms_dead to match either the hourly ops/state.json snapshot
(stale an hour later) or the tree (failing CI and publish-image until the
hourly run). A citation matching the working tree is current; one matching
neither still fails, and keys the tree cannot derive still compare to the
snapshot only.
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.argv = ["preflight.py"]

import preflight as P                                            # noqa: E402

FORM = '<form onsubmit="return false"></form>'


def _run(risks, state, forms):
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "ops"))
        os.makedirs(os.path.join(root, "site", "a"))
        io.open(os.path.join(root, "RISKS.md"), "w", encoding="utf-8").write(risks)
        json.dump(state, io.open(os.path.join(root, "ops", "state.json"), "w"))
        for n in range(forms):
            io.open(os.path.join(root, "site", "a", "p%d.html" % n), "w",
                    encoding="utf-8").write(FORM)
        io.open(os.path.join(root, "site", "a", "_skip.html"), "w",
                encoding="utf-8").write(FORM)
        old_root, old_fail = P.ROOT, list(P.FAIL)
        P.ROOT = root
        try:
            del P.FAIL[:]
            P.gate_risks_evidence_current()
            return list(P.FAIL)
        finally:
            P.ROOT = old_root
            P.FAIL[:] = old_fail


def test_matches_tree_ahead_of_snapshot_passes():
    assert _run("forms_dead=3", {"forms_dead": 2}, 3) == []


def test_matches_snapshot_passes():
    assert _run("forms_dead=2", {"forms_dead": 2}, 3) == []


def test_matches_neither_fails():
    assert _run("forms_dead=7", {"forms_dead": 2}, 3) != []


def test_underscore_pages_not_counted():
    assert _run("forms_dead=4", {"forms_dead": 2}, 3) != []


def test_non_derived_key_still_uses_snapshot():
    assert _run("email_list=5", {"email_list": 0}, 0) != []


def main():
    tests = [test_matches_tree_ahead_of_snapshot_passes,
             test_matches_snapshot_passes, test_matches_neither_fails,
             test_underscore_pages_not_counted,
             test_non_derived_key_still_uses_snapshot]
    bad = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            bad.append("%s: %s" % (t.__name__, e))
    if bad:
        print("FAIL: risks evidence tree-derived")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: risks evidence accepts tree-derived counts, %d/%d" % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
