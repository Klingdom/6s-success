#!/usr/bin/env python3
"""
Prove check_sellable.py's "N deliberately excluded" note names every real
reason, not just the first dropped item's.

Found 2026-10-02, second-pass cold-reading the 2026-09-26-dated ops/*.py
tier (ops/cold_read_ledger.py) per CLAUDE.md step 5d. The note printed
`f"{len(dropped)} deliberately excluded, {dropped[0][1]}"`: against the
real catalogue this read "note: 35 deliberately excluded, already free in
the Entryway deck", but only 6 of those 35 are excluded for that reason;
the other 29 are retired SKUs excluded for an unrelated pricing reason.
The line claimed one reason explained all 35, which is false. Fixed by
grouping dropped items by category and naming every one with its own
count.

Run:  python ops/tests/test_check_sellable_excluded_note.py
"""
import contextlib
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import check_sellable                                           # noqa: E402
import generated_products                                       # noqa: E402


def _run_check():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        check_sellable.main()
    return out.getvalue()


def main() -> int:
    fails = []
    orig_products = generated_products.products

    # Synthetic dropped set spanning two distinct reasons, the exact shape
    # that exposed the bug: a single-reason note would be wrong here.
    def fake_products():
        keep, _dropped = orig_products()
        dropped = [
            ("FAKE-A", "already free in the Entryway deck"),
            ("FAKE-B", "retired: made up reason one"),
            ("FAKE-C", "retired: made up reason two"),
        ]
        return keep, dropped

    # check_sellable.main() does `from generated_products import products`
    # locally, at call time, so the module attribute is what has to move.
    generated_products.products = fake_products
    try:
        out = _run_check()
    finally:
        generated_products.products = orig_products

    if "3 deliberately excluded" not in out:
        fails.append("note did not report the real total: %r" %
                      [l for l in out.splitlines() if "deliberately" in l])
    if "1 already free in the Entryway deck" not in out:
        fails.append("note did not name the 'already free' reason with "
                      "its own count")
    if "2 retired" not in out:
        fails.append("note did not name the 'retired' reason with its own "
                      "count")
    # The real historical bug: a note that names only the FIRST reason as
    # though it covered every dropped item.
    if "3 deliberately excluded, already free in the Entryway deck" in out:
        fails.append("note still attributes every exclusion to the first "
                      "item's reason alone (the real historical defect)")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: check_sellable.py 'deliberately excluded' note, 4/4 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
