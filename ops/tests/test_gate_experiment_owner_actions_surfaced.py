#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_experiment_owner_actions_surfaced() actually
catches an experiment's owner_action going unmentioned in OWNER-ACTIONS.md.

Found 2026-09-09, this operator: EXP-001's owner_action (visit
?6s-internal=1 on each of Phil's own devices, so a future buy-click is not
as unattributable as the historical nine) has existed in
ops/experiments.json since 2026-09-03 and was never once added to
OWNER-ACTIONS.md, the one file CLAUDE.md 0.5 designates for exactly this.
Nothing checked that the two stayed in step, so it sat unseen for six days.
This test proves the gate fires on that exact shape and stays quiet once
the experiment's id is surfaced.

Run:  python ops/tests/test_gate_experiment_owner_actions_surfaced.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run_gate(experiments, owner_actions_text, both_present=True):
    tmp_dir = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp_dir, "ops")
        os.makedirs(ops_dir)
        io.open(os.path.join(ops_dir, "experiments.json"), "w",
                encoding="utf-8").write(json.dumps({"experiments": experiments}))
        if both_present and owner_actions_text is not None:
            io.open(os.path.join(tmp_dir, "OWNER-ACTIONS.md"), "w",
                    encoding="utf-8").write(owner_actions_text)

        real_root = preflight.ROOT
        preflight.ROOT = tmp_dir
        before_fail, before_warn = len(preflight.FAIL), len(preflight.WARN)
        try:
            preflight.gate_experiment_owner_actions_surfaced()
        finally:
            preflight.ROOT = real_root
        return preflight.FAIL[before_fail:], preflight.WARN[before_warn:]
    finally:
        shutil.rmtree(tmp_dir)


def test_surfaced_owner_action_passes_clean():
    fails, warns = _run_gate(
        [{"id": "EXP-001", "owner_action": "Phil: do the thing"}],
        "# Owner actions\n\nSee EXP-001 for the device-labelling step.\n")
    assert not fails, fails
    assert not warns, warns
    print("ok  an owner_action mentioned by id in OWNER-ACTIONS.md passes clean")


def test_missing_owner_action_fails_by_name():
    fails, warns = _run_gate(
        [{"id": "EXP-001", "owner_action": "Phil: do the thing"}],
        "# Owner actions\n\nNothing relevant to that experiment is here.\n")
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "experiment-owner-actions-surfaced", fails
    assert "EXP-001" in msg, msg
    print("ok  an unsurfaced owner_action fails naming experiment-owner-actions-surfaced")


def test_experiment_without_owner_action_is_not_flagged():
    fails, warns = _run_gate(
        [{"id": "EXP-002", "status": "reading"}],
        "# Owner actions\n\nNothing relevant.\n")
    assert not fails, fails
    assert not warns, warns
    print("ok  an experiment with no owner_action is never checked")


def test_missing_owner_actions_file_does_not_crash():
    fails, warns = _run_gate(
        [{"id": "EXP-001", "owner_action": "Phil: do the thing"}],
        None, both_present=False)
    assert not fails, fails
    assert not warns, warns
    print("ok  a missing OWNER-ACTIONS.md does not crash or false-fail")


def test_real_repository_files_pass_right_now():
    """Not a synthetic fixture: the actual ops/experiments.json and
    OWNER-ACTIONS.md, run through the real gate exactly as preflight.py's
    main() calls it, so a passing test here means the repository is
    genuinely fixed, not just the logic.
    """
    before = len(preflight.FAIL)
    preflight.gate_experiment_owner_actions_surfaced()
    new_fails = preflight.FAIL[before:]
    assert not new_fails, (
        "a real experiment owner_action is unsurfaced right now: %s" % new_fails)
    print("ok  the real committed files pass right now")


if __name__ == "__main__":
    test_surfaced_owner_action_passes_clean()
    test_missing_owner_action_fails_by_name()
    test_experiment_without_owner_action_is_not_flagged()
    test_missing_owner_actions_file_does_not_crash()
    test_real_repository_files_pass_right_now()
    print("\nall gate_experiment_owner_actions_surfaced tests passed")
