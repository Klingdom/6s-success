"""Prove ops/check_also_called_digital_collision_fast.py actually catches a
colliding also-called name, and stays silent on a clean one, without
needing gate_tests or anything after it in preflight.py's own call order.

Found 2026-11-03: "grilling station" shared "station" with the unrelated
digital-context query "desktop charging station organizer" and shipped,
because every local preflight run that cycle used --skip-tests to route
around this sandbox's own gate_tests Chromium hang, and
gate_also_called_no_digital_collision lives inside that skipped suite.
ops/check_also_called_digital_collision_fast.py (mirroring
ops/check_risks_evidence_fast.py's own reasoning) calls the gate directly,
skipping gate_tests entirely, so it can run in the pre-push hook. This test
proves the wrapper's exit code and output, not the gate's own logic, which
ops/tests/test_gate_also_called_no_digital_collision.py already covers.

Run:  python ops/tests/test_check_also_called_digital_collision_fast.py
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
    "check_also_called_digital_collision_fast",
    os.path.join(OPS, "check_also_called_digital_collision_fast.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def _run(name, query):
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "ops"))
        json.dump({"zones": {"Test Room|Test Zone": {"names": [name]}}},
                  io.open(os.path.join(root, "ops", "zone-also-called.json"), "w"))
        json.dump({"rows": [{"query": query, "best_page": "/zones/x.html"}]},
                  io.open(os.path.join(root, "ops", "keyword-demand.json"), "w"))
        json.dump({"rows": []},
                  io.open(os.path.join(root, "ops", "keyword-demand-global.json"), "w"))
        old_root = P.ROOT
        P.ROOT = root
        C.preflight.ROOT = root
        try:
            return C.main()
        finally:
            P.ROOT = old_root
            C.preflight.ROOT = old_root


def test_colliding_name_fails():
    assert _run("grilling station", "desktop charging station organizer") == 1


def test_clean_name_passes():
    assert _run("grilling zone", "desktop charging station organizer") == 0


def main():
    tests = [test_colliding_name_fails, test_clean_name_passes]
    bad = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            bad.append("%s: %s" % (t.__name__, e))
    if bad:
        print("FAIL: check_also_called_digital_collision_fast wrapper")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK: check_also_called_digital_collision_fast wrapper, %d/%d"
          % (len(tests), len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
