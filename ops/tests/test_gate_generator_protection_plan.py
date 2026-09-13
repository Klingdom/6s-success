#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_every_generator_has_a_protection_plan() catches
a new ops/build_*.py file that nobody has assigned a protection to yet, and
catches GENERATOR_PROTECTED_ELSEWHERE citing a gate that no longer exists.

Found 2026-09-10/11: gate_generator_ownership had named fifteen separate
generators as "found unprotected, fixed" data points over two weeks, each one
discovered by an operator happening to cold-read that one file. An audit of
all 34 ops/build_*.py files found the fifteen currently outside that gate's
own chain, and confirmed each already has a real, working gate protecting it
some other way, cited in GENERATOR_PROTECTED_ELSEWHERE. This meta-gate is
what stops that becoming a sixteenth data point found by luck: a new
generator with no entry anywhere fails immediately, by name.

Widened 2026-09-13: the glob used to be ROOT/ops/build_*.py, one directory
deep only, so it could not see ops/cardtext/build_kitchen_deck.py, and it
never looked outside ops/ at all, so it could not see build/listings/
build_etsy_assets.py or build/listings/build_kdp_cover.py either -- the
exact two generators the prior two cycles had just found unprotected by
cold-reading them, invisible to the very meta-gate meant to make that
unnecessary. Now recurses through ops/ and also covers build/. Checks 2b/2c
below prove the widened glob actually catches a subdirectory generator and
actually sees and cites all three real ones, not just that the old
fake-file-in-ops/ regression test (2/3 above) still passes.

Run:  python ops/tests/test_gate_generator_protection_plan.py
"""
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402


def _run():
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_every_generator_has_a_protection_plan()
    return list(preflight.FAIL)


def main() -> int:
    fails = []

    # 1. The real, committed ops/ directory today: clean. Every one of the 34
    #    real generators is either in the ownership chain or cited in
    #    GENERATOR_PROTECTED_ELSEWHERE with a gate that really exists.
    r = _run()
    if r:
        fails.append("the real ops/ directory failed: %r" % (r,))

    # 2. The real regression this gate exists to catch: a brand new generator
    #    with no entry in either list. Written into the real ops/ directory
    #    (not a fake ROOT), because the gate globs ROOT/ops/build_*.py
    #    directly rather than taking a path argument.
    fake_path = os.path.join(ROOT, "ops", "build_zzz_test_regression.py")
    try:
        io.open(fake_path, "w", encoding="utf-8").write(
            "# planted by test_gate_generator_protection_plan.py, deleted "
            "immediately after\n")
        r = _run()
        if not r or "build_zzz_test_regression.py" not in r[0][1]:
            fails.append("an unprotected new generator was not caught: %r"
                         % (r,))
    finally:
        if os.path.exists(fake_path):
            os.remove(fake_path)

    # 3. Confirm cleanup: the planted file is really gone and the gate is
    #    clean again, so this test does not leave the repository worse off
    #    than it found it even if an assertion above already failed.
    r = _run()
    if r:
        fails.append("gate not clean after removing the planted file: %r"
                     % (r,))

    # 2b. The 2026-09-13 regression this gate could not previously catch at
    #     all: a generator one directory deeper than ops/build_*.py. The
    #     original glob (ROOT/ops/build_*.py, non-recursive) would have
    #     missed this silently; the widened one must not.
    fake_dir = os.path.join(ROOT, "ops", "zzz_test_subdir")
    fake_sub = os.path.join(fake_dir, "build_zzz_test_subdir.py")
    try:
        os.makedirs(fake_dir, exist_ok=True)
        io.open(fake_sub, "w", encoding="utf-8").write(
            "# planted by test_gate_generator_protection_plan.py, deleted "
            "immediately after\n")
        r = _run()
        if not r or "build_zzz_test_subdir.py" not in r[0][1]:
            fails.append("an unprotected generator in an ops/ subdirectory "
                         "was not caught: %r" % (r,))
    finally:
        if os.path.exists(fake_sub):
            os.remove(fake_sub)
        if os.path.isdir(fake_dir):
            os.rmdir(fake_dir)
    r = _run()
    if r:
        fails.append("gate not clean after removing the planted subdirectory "
                     "file: %r" % (r,))

    # 2c. The three real generators this widening was for must actually be
    #     visible and cited, not just tolerated by the fake-file tests above.
    real = {}
    import glob as _glob
    for tree in ("ops", "build"):
        for p in _glob.glob(os.path.join(ROOT, tree, "**", "build_*.py"),
                            recursive=True):
            real[os.path.basename(p)] = True
    for name in ("build_etsy_assets.py", "build_kdp_cover.py",
                 "build_kitchen_deck.py"):
        if name not in real:
            fails.append("%s was not found by the widened glob at all" % name)
        elif name not in preflight.GENERATOR_PROTECTED_ELSEWHERE:
            fails.append("%s is found but has no GENERATOR_PROTECTED_"
                         "ELSEWHERE entry" % name)

    # 4. A stale citation: GENERATOR_PROTECTED_ELSEWHERE naming a gate that
    #    does not exist must fail too, not just a missing entry.
    old = preflight.GENERATOR_PROTECTED_ELSEWHERE
    try:
        patched = dict(old)
        patched["build_icons.py"] = ("gate_this_function_does_not_exist",)
        preflight.GENERATOR_PROTECTED_ELSEWHERE = patched
        r = _run()
        if not r or "gate_this_function_does_not_exist" not in r[0][1]:
            fails.append("a stale gate citation was not caught: %r" % (r,))
    finally:
        preflight.GENERATOR_PROTECTED_ELSEWHERE = old

    # 5. Restored: clean again.
    r = _run()
    if r:
        fails.append("gate not clean after restoring GENERATOR_PROTECTED_"
                     "ELSEWHERE: %r" % (r,))

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: gate_every_generator_has_a_protection_plan, 8/8 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
