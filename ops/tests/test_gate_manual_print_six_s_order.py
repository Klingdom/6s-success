#!/usr/bin/env python3
"""
Prove ops/build_manual_print.py's six_s_order_problems() catches an
out-of-order run of exactly 4 of the six 6S pass names, per D-014 (Safety is
the fourth S).

Real gap found 2026-09-21, cold-read of build_manual_print.py's gates(): the
order check only ran on runs of 5 or more matches (`len(seq) >= 5`), even
though the same function's own outer regex already requires at least 4
matches before a sequence counts as a "run" at all. A 4-item enumeration
listed out of canonical order (e.g. "Straighten, Shine, Sort, Safety") would
have been counted in the "runs checked" tally but silently excluded from the
order check itself, so a future edit that shipped exactly that shape would
not have failed the gate. No live document currently contains a 4-item run
(checked both content/manual/6S Home Micro Zone SOP Field Manual v3.html and
content/manual/print/6S-Micro-Zone-Manual-PRINT-7x10.html: both runs found in
each are length 5 and 6), so this was a gate gap, not a shipped defect.

Fixed by extracting the check into six_s_order_problems() and comparing the
full matched sequence against canonical order regardless of its length.
"""

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location(
    "build_manual_print", os.path.join(ROOT, "ops", "build_manual_print.py"))
bmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bmp)


def old_buggy_check(txt):
    """The pre-fix logic: only order-checks runs of 5 or more matches."""
    import re
    runs = re.findall(
        r"(?:%s)(?:\s*(?:,|and|&|·|>|/)\s*(?:%s)){3,}"
        % (bmp.SIX_S_ALT, bmp.SIX_S_ALT), txt)
    bad = []
    for r in runs:
        seq = re.findall(bmp.SIX_S_ALT, r)
        if len(seq) >= 5 and seq[:6] != bmp.SIX_S_CANON[:len(seq)]:
            bad.append(r.strip()[:70])
    return runs, bad


def test_old_logic_misses_a_4_item_out_of_order_run():
    txt = "Do Straighten, Shine, Sort, Safety before you finish the zone."
    runs, bad = old_buggy_check(txt)
    assert len(runs) == 1
    assert bad == [], "the bug: a 4-item out-of-order run was not flagged"


def test_fixed_logic_catches_the_same_run():
    txt = "Do Straighten, Shine, Sort, Safety before you finish the zone."
    runs, bad = bmp.six_s_order_problems(txt)
    assert len(runs) == 1
    assert len(bad) == 1, "the fix must flag the same 4-item out-of-order run"


def test_fixed_logic_still_passes_a_canonical_4_item_run():
    txt = "Do Sort, Straighten, Shine, Safety in that order."
    runs, bad = bmp.six_s_order_problems(txt)
    assert len(runs) == 1
    assert bad == []


def test_fixed_logic_still_catches_5_and_6_item_runs():
    for txt in [
        "Straighten, Shine, Safety, Standardize, Sort come next.",
        "Straighten, Sort, Shine, Safety, Standardize, Sustain, in order.",
    ]:
        runs, bad = bmp.six_s_order_problems(txt)
        assert len(runs) == 1
        assert len(bad) == 1


def test_fixed_logic_passes_the_real_canonical_full_run():
    txt = "Sort, Straighten, Shine, Safety, Standardize, Sustain."
    runs, bad = bmp.six_s_order_problems(txt)
    assert len(runs) == 1
    assert bad == []


def test_real_committed_manual_has_no_order_problems():
    for rel in [
        "content/manual/6S Home Micro Zone SOP Field Manual v3.html",
        "content/manual/print/6S-Micro-Zone-Manual-PRINT-7x10.html",
    ]:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        s = bmp.read(path)
        txt = bmp.strip_tags(s)
        runs, bad = bmp.six_s_order_problems(txt)
        assert bad == [], "%s: %s" % (rel, bad)


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print("ok  " + name)
    print("ALL PASSED")
