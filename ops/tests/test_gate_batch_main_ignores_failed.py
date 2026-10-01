#!/usr/bin/env python3
"""
Proves check_batch_main_ignores_failed() catches the shape found six times
now (video_zone_photo.py, render_all_zone_videos.py, 2026-09-26;
render_all_narrated.py, video_srt.py, generate_card_heroes.py,
generate_zone_heroes.py, 2026-10-01): main() builds a `failed` list in a
loop and returns a value that ignores it.

Run:  python ops/tests/test_gate_batch_main_ignores_failed.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight as P                                             # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, detail))


BUGGY = """
def main():
    failed = []
    for job in jobs:
        ok = attempt(job)
        if not ok:
            failed.append(job)
    for f in failed[:5]:
        print("FAILED", f)
    return 0
"""

FIXED_CONDITIONAL_EXPR = """
def main():
    failed = []
    for job in jobs:
        ok = attempt(job)
        if not ok:
            failed.append(job)
    for f in failed[:5]:
        print("FAILED", f)
    return 1 if failed else 0
"""

FIXED_EARLY_GUARD = """
def main():
    failed = []
    for job in jobs:
        ok = attempt(job)
        if not ok:
            failed.append(job)
    if failed:
        for f in failed:
            print("FAILED", f)
        return 1
    return 0
"""

NO_FAILED_LIST_AT_ALL = """
def main():
    done = []
    for job in jobs:
        done.append(job)
    print(len(done))
    return 0
"""

OTHER_NAME_GUARDED_CORRECTLY = """
def main():
    missing = []
    for job in jobs:
        if not job.exists():
            missing.append(job)
    if missing:
        return 1
    return 0
"""


def test_catches_the_real_regression_shape():
    problem = P.check_batch_main_ignores_failed(BUGGY)
    check("catches-buggy", problem is not None, repr(problem))


def test_passes_the_conditional_expression_fix():
    problem = P.check_batch_main_ignores_failed(FIXED_CONDITIONAL_EXPR)
    check("passes-conditional-fix", problem is None, repr(problem))


def test_passes_the_early_guard_fix():
    problem = P.check_batch_main_ignores_failed(FIXED_EARLY_GUARD)
    check("passes-early-guard-fix", problem is None, repr(problem))


def test_silent_on_files_with_no_failed_list():
    problem = P.check_batch_main_ignores_failed(NO_FAILED_LIST_AT_ALL)
    check("silent-no-failed-list", problem is None, repr(problem))


def test_does_not_flag_a_differently_named_but_correctly_guarded_list():
    # Scoped deliberately to the literal name `failed`; a file using `missing`
    # and guarding it correctly must not be flagged by this narrow gate.
    problem = P.check_batch_main_ignores_failed(OTHER_NAME_GUARDED_CORRECTLY)
    check("silent-other-name", problem is None, repr(problem))


def test_real_repository_is_currently_clean():
    """The real fix: six files in ops/ had this shape and are now fixed.
    Proves the gate reads live files, not a cached belief that they are fine.
    """
    import glob
    import io as _io
    bad = []
    for p in sorted(glob.glob(os.path.join(ROOT, "ops", "*.py"))):
        src = _io.open(p, encoding="utf-8", errors="replace").read()
        problem = P.check_batch_main_ignores_failed(src)
        if problem:
            bad.append("%s: %s" % (os.path.basename(p), problem))
    check("real-repo-clean", not bad, bad)


if __name__ == "__main__":
    test_catches_the_real_regression_shape()
    test_passes_the_conditional_expression_fix()
    test_passes_the_early_guard_fix()
    test_silent_on_files_with_no_failed_list()
    test_does_not_flag_a_differently_named_but_correctly_guarded_list()
    test_real_repository_is_currently_clean()
    if FAILS:
        print("FAIL")
        for f in FAILS:
            print("  " + f)
        sys.exit(1)
    print("PASS  6 of 6 cases")
