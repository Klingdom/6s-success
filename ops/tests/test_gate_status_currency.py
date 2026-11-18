#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_status_currency() can actually fail, and that
it does not fire on the ordinary short lag every check-in absorbs.

Found reading ops/NIGHTLY-LOG.md cold, 2026-09-11: "STATUS.md was N commits
stale" recurs at least six separate times this week alone, each caught only
by a human or a dedicated PM pass happening to compare STATUS.md's own
account against real git history by hand. Prior cycles explicitly declined
to gate this ("STATUS.md's own prose is not mechanically diffable the way a
generator's output is"), which is true and stays true here: this does not
diff content, it only tracks whether a material commit's hash was ever cited.

Run:  python ops/tests/test_gate_status_currency.py
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def fake_hash(seed: str) -> str:
    """A real-looking 40 character hex hash, distinct per seed and never a
    prefix of another seed's hash (a sequential counter like "0000000N"
    shares a 7 character prefix with its neighbours and would silently
    defeat the very thing case 5 below is testing)."""
    return hashlib.sha1(seed.encode()).hexdigest()


def commit(h, subject, files):
    return (h, subject, files)


def main() -> int:
    fails = []

    # 1. Nine material commits, none cited anywhere in STATUS.md: the real
    #    shape this exists to catch. Must fire, and must name real hashes.
    commits = [
        commit(fake_hash("material-%d" % i), "Fix real thing %d" % i,
               ["ops/build_zone_pages.py"])
        for i in range(9)
    ]
    gap = preflight.status_currency_gap("nothing about any of this here.",
                                         commits)
    if len(gap) != 9:
        fails.append("9 unmentioned material commits: expected a gap of 9, "
                     "got %r" % (gap,))

    # 2. Same nine commits, but STATUS.md's own text cites every hash: must
    #    not fire. Proves this is checking citation, not merely staleness.
    status_text = " ".join("`%s`" % h[:8] for h, _, _ in commits)
    gap = preflight.status_currency_gap(status_text, commits)
    if gap:
        fails.append("every commit cited by hash, but still flagged: %r"
                     % (gap,))

    # 3. Only three unmentioned material commits: an ordinary short lag
    #    between check-ins, not the compounding defect. Must not fire.
    gap = preflight.status_currency_gap("nothing here.", commits[:3])
    if gap:
        fails.append("3 unmentioned commits (an ordinary lag) wrongly "
                     "flagged: %r" % (gap,))

    # 4. Nine commits touching only excluded, non-material paths (the
    #    command deck, the log, STATUS.md itself): must not fire, even
    #    though none is cited, because a routine pass that only regenerates
    #    those is not the drift this exists to catch.
    routine = [
        commit(fake_hash("routine-%d" % i), "Regenerate the command deck",
               ["EXECUTIVE-DASHBOARD-LIVE.md", "ops/dashboard.html",
              "ops/state.json", "ops/NIGHTLY-LOG.md"])
        for i in range(9)
    ]
    gap = preflight.status_currency_gap("nothing here.", routine)
    if gap:
        fails.append("9 routine, non-material commits wrongly flagged: %r"
                     % (gap,))

    # 5. A mix: 9 material commits, only 1 cited, leaves 8 unmentioned,
    #    exactly the threshold, and must still fire.
    status_text = " ".join("`%s`" % h[:8] for h, _, _ in commits[:1])
    gap = preflight.status_currency_gap(status_text, commits)
    if len(gap) != 8:
        fails.append("1 of 9 cited: expected a gap of 8, got %r" % (gap,))

    # 6. _status_material_path itself: site/ and ops/build_* are material,
    #    the dashboard/log/STATUS.md artifacts and an unrelated ops/ file
    #    are not.
    cases = [
        ("site/zones/entryway-the-landing-spot.html", True),
        ("ops/build_zone_pages.py", True),
        ("ops/preflight.py", True),
        ("GOALS.md", True),
        ("STATUS.md", False),
        ("ops/NIGHTLY-LOG.md", False),
        ("EXECUTIVE-DASHBOARD-LIVE.md", False),
        ("ops/dashboard.html", False),
        ("ops/state.json", False),
        ("site/build-id.txt", False),
        ("ops/checkin.py", False),
        ("README.md", False),
    ]
    for path, want in cases:
        got = preflight._status_material_path(path)
        if got != want:
            fails.append("_status_material_path(%r): expected %r, got %r"
                         % (path, want, got))

    # 7. gate_status_currency() itself must refuse to trust a shallow-clone
    #    boundary commit as STATUS.md's real last-edit hash. Found
    #    2026-11-18: `git log -1 -- STATUS.md` credits the boundary commit
    #    (no visible parent, so git cannot tell what it really changed) with
    #    having touched every path in its own tree, including STATUS.md if
    #    it was not really edited since well before the boundary. Treating
    #    that hash as the real last edit would miscount the commit range
    #    (`last..HEAD`): on a depth-1 clone where the boundary commit IS
    #    HEAD, the range is empty and the gate would silently report
    #    STATUS.md current with nothing actually measured. Cannot be
    #    reproduced by actually shrinking this checkout mid-test, so it
    #    fakes the boundary via monkeypatching, the same technique the
    #    sibling fixes in cold_read_ledger.py/build_seo.py/
    #    check_cron_cadence.py verified with.
    # Fully synthetic git plumbing: the boundary hash resolves as
    # STATUS.md's "last" edit, the range query then reports 9 fabricated
    # material commits none of which STATUS.md's own real text cites,
    # exactly the shape case 1 above proves status_currency_gap() itself
    # flags. Without the guard this fix adds, gate_status_currency() would
    # warn on all 9; with it, resolving "last" to a recognised boundary
    # commit must skip the whole range as unmeasurable instead.
    boundary_hash = "b" * 40
    fake_commits = [(fake_hash("gsc-material-%d" % i),
                      "Fix real thing %d" % i) for i in range(9)]

    class _Result:
        def __init__(self, stdout):
            self.stdout = stdout

    def fake_run(cmd, *a, **kw):
        if cmd[:3] == ["git", "log", "-1"] and cmd[-1] == "STATUS.md":
            return _Result(boundary_hash + "\n")
        if cmd[1] == "log" and ".." in cmd[2]:
            return _Result("\n".join(
                "%s\x01%s" % (h, s) for h, s in fake_commits) + "\n")
        if cmd[1] == "diff-tree":
            return _Result("ops/build_zone_pages.py\n")
        raise AssertionError("unexpected git call in gate_status_currency "
                             "test: %r" % (cmd,))

    orig_boundary = preflight._shallow_boundary_commits
    orig_run = preflight.subprocess.run
    preflight._shallow_boundary_commits = lambda: {boundary_hash}
    preflight.subprocess.run = fake_run
    before = len(preflight.WARN)
    try:
        preflight.gate_status_currency()
    finally:
        preflight._shallow_boundary_commits = orig_boundary
        preflight.subprocess.run = orig_run
    if len(preflight.WARN) != before:
        fails.append(
            "gate_status_currency() recorded a warning after resolving "
            "STATUS.md's last-edit hash to a faked shallow boundary "
            "commit, instead of skipping an unmeasurable range: %r"
            % (preflight.WARN[before:],))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: %d checks" % (2 + 3 + len(cases) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
