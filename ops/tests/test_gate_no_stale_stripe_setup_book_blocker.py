#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_no_stale_stripe_setup_book_blocker() catches
ops/stripe_setup.py's own printed output describing the book and manual as
blocked on front matter, issue #3, once that issue is closed.

Found 2026-09-18, this operator, the standing low-mention ops/*.py cold-read
tier the prior cycle's handoff named next. stripe_setup.py's "Not created,
deliberately" block printed "Book and manual        blocked on front
matter, issue #3" unconditionally on every --plan/--apply run, months after
issue #3 closed (2026-08-25) and after both products started selling live
via a separate catalogue-driven script, ops/stripe_catalog.py.

Run:  python ops/tests/test_gate_no_stale_stripe_setup_book_blocker.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402

STALE_LINE = (
    '    print("  Book and manual        blocked on front matter, '
    'issue #3")\n'
)
FIXED_LINE = (
    '    print("  Book and manual        catalogue SKUs, created by '
    'ops/stripe_catalog.py, not here")\n'
)
OTHER_LINE = (
    '    print("  Tools, 24 SKUs         no supplier")\n'
)


def _run(script_text):
    tmp = tempfile.mkdtemp()
    try:
        ops_dir = os.path.join(tmp, "ops")
        os.makedirs(ops_dir)
        io.open(os.path.join(ops_dir, "stripe_setup.py"), "w",
                encoding="utf-8").write(script_text)
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_no_stale_stripe_setup_book_blocker()
            return list(preflight.FAIL), list(preflight.WARN)
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    fails = []

    # 1. The real, pre-fix regression shape: the stale line is present.
    r, w = _run(OTHER_LINE + STALE_LINE)
    if not r or "no-stale-stripe-setup-book-blocker" != r[0][0]:
        fails.append("the stale line was not caught: %r" % (r,))

    # 2. The fixed line: no stale claim, no failure.
    r, w = _run(OTHER_LINE + FIXED_LINE)
    if r:
        fails.append("the fixed line was wrongly flagged: %r" % (r,))

    # 3. Neither line present at all (file rewritten some other way): no
    #    failure, nothing to check.
    r, w = _run(OTHER_LINE)
    if r:
        fails.append("absence of either line was wrongly flagged: %r" % (r,))

    # 4. The real, currently-committed file must pass clean against the
    #    actual repository, not only a synthetic fixture.
    preflight.FAIL, preflight.WARN = [], []
    preflight.gate_no_stale_stripe_setup_book_blocker()
    if preflight.FAIL:
        fails.append("the real committed file failed: %r" % (preflight.FAIL,))

    # 5. Missing file entirely: no failure, gate returns quietly.
    tmp = tempfile.mkdtemp()
    try:
        old_root = preflight.ROOT
        preflight.ROOT = tmp
        preflight.FAIL, preflight.WARN = [], []
        try:
            preflight.gate_no_stale_stripe_setup_book_blocker()
            if preflight.FAIL:
                fails.append("missing file wrongly flagged: %r" % (preflight.FAIL,))
        finally:
            preflight.ROOT = old_root
    finally:
        shutil.rmtree(tmp)

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS: 5 of 5 cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
