#!/usr/bin/env python3
"""
Prove deploy.py can tell why production differs from the repository, instead
of always guessing that the image is still on its way.

WHY THIS EXISTS
---------------
When the live build id did not match, deploy.py said, always:

    "Usually the image has not finished publishing: check `gh run list`,
     then run this again."

That is right for the common case and wrong for the one that actually strands
work. On 2026-09-30 a site change was pushed; its push-triggered image build
FAILED on a fault in a concurrent session's commit (a misordered
NIGHTLY-LOG.md entry, unrelated to the change), and the upstream fix for that
fault touched no `site/**` path. publish-image.yml is correctly filtered to
`site/**`, `Dockerfile` and itself, so it declined to rebuild, and the change
sat with no image at all. Re-running deploy.py would have reported the same
mismatch forever, and its own advice was to do exactly that.

Four states, because they need four different actions, plus "unknown" kept
separate from "none" on purpose: "nobody built it" and "I could not look" are
different facts and only one is a reason to act.

Run:  python ops/tests/test_deploy_publish_state.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import deploy as D                                             # noqa: E402

HEAD = "headsha"


def _anc(*containing):
    """A run's commit contains HEAD only if it is named here."""
    return lambda run_sha: run_sha in containing


def case_a_running_build_is_building():
    runs = [{"sha": "A", "status": "in_progress", "conclusion": ""}]
    assert D.classify_publish(runs, HEAD, _anc("A"))[0] == "building"


def case_a_queued_build_is_also_building():
    runs = [{"sha": "A", "status": "queued", "conclusion": ""}]
    assert D.classify_publish(runs, HEAD, _anc("A"))[0] == "building"


def case_a_successful_build_is_ready():
    runs = [{"sha": "A", "status": "completed", "conclusion": "success"}]
    assert D.classify_publish(runs, HEAD, _anc("A"))[0] == "ready"


def case_a_failed_build_is_failed_not_building():
    """The defect this exists for: retrying will never produce the image."""
    runs = [{"sha": "A", "status": "completed", "conclusion": "failure"}]
    state, run = D.classify_publish(runs, HEAD, _anc("A"))
    assert state == "failed", state
    assert run["sha"] == "A"
    assert "will not change that" in D.PUBLISH_ADVICE["failed"]


def case_a_cancelled_build_is_also_failed():
    runs = [{"sha": "A", "status": "completed", "conclusion": "cancelled"}]
    assert D.classify_publish(runs, HEAD, _anc("A"))[0] == "failed"


def case_runs_that_do_not_contain_head_are_ignored():
    """A green build of an OLDER commit does not cover this change."""
    runs = [{"sha": "OLD", "status": "completed", "conclusion": "success"}]
    assert D.classify_publish(runs, HEAD, _anc())[0] == "none"


def case_the_newest_covering_run_decides():
    runs = [
        {"sha": "NEW", "status": "completed", "conclusion": "failure"},
        {"sha": "OLD", "status": "completed", "conclusion": "success"},
    ]
    assert D.classify_publish(runs, HEAD, _anc("NEW", "OLD"))[0] == "failed"


def case_a_non_covering_newer_run_does_not_mask_a_covering_one():
    runs = [
        {"sha": "SIDE", "status": "completed", "conclusion": "failure"},
        {"sha": "MINE", "status": "completed", "conclusion": "success"},
    ]
    assert D.classify_publish(runs, HEAD, _anc("MINE"))[0] == "ready"


def case_could_not_ask_is_unknown_not_none():
    state, run = D.classify_publish(None, HEAD, _anc())
    assert state == "unknown", state
    assert run is None
    assert "UNCHECKED" in D.PUBLISH_ADVICE["unknown"]


def case_empty_run_list_is_none_not_unknown():
    assert D.classify_publish([], HEAD, _anc())[0] == "none"


def case_every_state_has_advice():
    for state in ("building", "ready", "failed", "none", "unknown"):
        assert state in D.PUBLISH_ADVICE, state
        assert len(D.PUBLISH_ADVICE[state]) > 40, state


def case_the_two_actionable_states_name_the_command():
    for state in ("failed", "none"):
        assert "gh workflow run" in D.PUBLISH_ADVICE[state], state


def case_deploy_asks_before_advising():
    """The mismatch branch must consult the build, not guess about it."""
    import io
    src = io.open(os.path.join(ROOT, "ops", "deploy.py"),
                  encoding="utf-8").read()
    start = src.index("VERDICT production is serving a DIFFERENT build")
    end = src.index("return 1", start)
    branch = src[start:end]
    assert "publish_state()" in branch, branch
    assert "PUBLISH_ADVICE[state]" in branch, branch
    # The retired sentence may survive as a historical citation in a
    # docstring, the same allowance gate_no_stale_listmonk_blocker makes for
    # a retired diagnosis. What it must not be is live guidance again.
    assert "Usually the image has not finished publishing" not in branch


def case_every_different_build_verdict_consults_the_build():
    """There were TWO of these branches and the first version of this test
    only checked the first, which is how the second kept its old always-guess
    sentence. Every one of them now has to ask."""
    import io
    src = io.open(os.path.join(ROOT, "ops", "deploy.py"),
                  encoding="utf-8").read()
    needle = "VERDICT production is serving a DIFFERENT build"
    found = 0
    pos = 0
    while True:
        i = src.find(needle, pos)
        if i == -1:
            break
        found += 1
        pos = i + 1
        branch = src[i:src.index("return 1", i)]
        assert "publish_state()" in branch, (found, branch)
        assert "PUBLISH_ADVICE[state]" in branch, (found, branch)
        assert "Usually the image has not finished publishing" not in branch
    assert found >= 2, ("expected both mismatch branches, found %d" % found)


def main() -> int:
    cases = [v for k, v in sorted(globals().items()) if k.startswith("case_")]
    for c in cases:
        c()
        print("  ok  " + c.__name__)
    print("%d/%d cases passed" % (len(cases), len(cases)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
