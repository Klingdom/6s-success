#!/usr/bin/env python3
"""
Prove ops/prerender_shop.py, ops/wire_pwa.py, ops/wire_signup.py and
ops/wire_measure.py no longer pass a built HTML block directly as an
re.sub repl argument. Found 2026-09-27 cold-read: all four shared the
exact bug shape fixed in ops/fill_front_matter.py the same day: re.sub's
repl string treats a bare backslash before a digit/letter as a
backreference and raises. None had fired live (no backslash in today's
catalogue/copy content), but a future one would crash the script or
corrupt a public page. ops/wire_zone_heroes.py already used the safe
callable-repl shape (FIG.sub(lambda _m: fig, s, count=1)); this test
proves each of the four now matches it.

Run:  python ops/tests/test_wire_scripts_backslash_repl.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = [
    "ops/prerender_shop.py",
    "ops/wire_pwa.py",
    "ops/wire_signup.py",
    "ops/wire_measure.py",
]

# The exact repl-argument shape the bug had: the built string passed
# straight through as repl (a bare identifier, no lambda/def wrapping it).
BUGGY_REPL = re.compile(r"re\.sub\([^,]+,\s*[A-Za-z_][A-Za-z0-9_]*\s*,")


def main() -> int:
    fails = []

    for rel in FILES:
        path = os.path.join(ROOT, rel)
        src = io.open(path, encoding="utf-8").read()
        bad = [m.group(0) for m in BUGGY_REPL.finditer(src)]
        if bad:
            fails.append("%s still passes a bare identifier as repl: %r" % (rel, bad))

    # Prove the underlying shape directly: a raw string repl containing a
    # literal backslash raises, a callable repl does not.
    MARK, END = "<!-- MARK -->", "<!-- END -->"
    s = "before\n" + MARK + "\nold\n" + END + "\nafter"
    block = r"a backslash literal: \1 in this block"

    try:
        re.sub(re.escape(MARK) + r".*?" + re.escape(END), block, s, flags=re.S)
        fails.append(
            "a bare re.sub(pattern, block, text) no longer raises on a "
            "backslash value; the regression this test guards against may "
            "have been reintroduced without the callable-repl fix")
    except re.error:
        pass  # expected: proves the raw-string-repl shape is still unsafe

    fixed = re.sub(re.escape(MARK) + r".*?" + re.escape(END),
                    lambda _m: block, s, flags=re.S)
    if block not in fixed or "old" in fixed:
        fails.append("callable-repl substitution did not place block correctly: %r" % fixed)

    if fails:
        print("FAIL:")
        for f in fails:
            print("  - " + f)
        return 1
    print("OK: all four wire/prerender scripts use callable repl, immune to "
          "backslash-as-backreference parsing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
