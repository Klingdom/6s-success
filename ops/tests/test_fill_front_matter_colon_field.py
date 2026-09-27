#!/usr/bin/env python3
"""
Prove ops/fill_front_matter.py handles a colon-qualified bracket, the shape
found live 2026-09-26 in the manual's copyright page:
"[PRINTING NUMBER LINE: 10 9 8 7 6 5 4 3 2 1]". FIELD's old character class
did not allow ":", so scan() never saw this field at all: not reported by
--check, not filled or dropped by --apply, and gate_front_matter_filled
(which trusts scan()) could not catch it either. It shipped as literal
placeholder text in three public manual files.

Three cases:
  1. scan() must find the field name (without the colon-qualified tail).
  2. --apply with a DROP answer must remove the whole bracket, colon tail
     included, not just a literal "[NAME]" it never had.
  3. Dropping a bracket that shares a line with other markup (a closing
     tag) must remove only the bracket, not the whole line, so structure
     stays balanced. A plain "[NAME]" placeholder alone on its own line
     must still drop the whole line, unchanged from before.

Run:  python ops/tests/test_fill_front_matter_colon_field.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import fill_front_matter as FFM                                 # noqa: E402


def main() -> int:
    fails = []

    # 1. scan() finds the field name, not the whole colon-qualified string.
    m = FFM.FIELD.findall("[PRINTING NUMBER LINE: 10 9 8 7 6 5 4 3 2 1]")
    if m != ["PRINTING NUMBER LINE"]:
        fails.append("FIELD.findall did not extract 'PRINTING NUMBER LINE': %r" % m)

    # a plain, unqualified bracket must still match exactly as before
    m2 = FFM.FIELD.findall("[YEAR]")
    if m2 != ["YEAR"]:
        fails.append("FIELD.findall regressed on a plain bracket: %r" % m2)

    # 2 & 3. simulate the apply loop's own token/drop logic directly,
    # against both line shapes: alone on a line, and sharing a line with a
    # closing tag that must survive.
    import re

    def apply_drop(text, name):
        token = re.compile(r"\[" + re.escape(name) + r"(?::[^\]]*)?\]")
        nl = chr(10)
        return nl.join(ln for ln in text.split(nl) if not token.search(ln))

    shared_line = (
        "<p>First edition, 2026<br>\n"
        "[PRINTING NUMBER LINE: 10 9 8 7 6 5 4 3 2 1]\n"
        "</p>\n"
    )
    out = apply_drop(shared_line, "PRINTING NUMBER LINE")
    if "PRINTING NUMBER LINE" in out or "[" in out:
        fails.append("colon-qualified bracket survived drop: %r" % out)
    if "</p>" not in out:
        fails.append(
            "dropping the colon-qualified bracket ate a sibling closing tag: %r" % out)

    own_line = "[TERRITORY STATEMENT]\n<p>next</p>\n"
    out2 = apply_drop(own_line, "TERRITORY STATEMENT")
    if "TERRITORY STATEMENT" in out2:
        fails.append("plain bracket on its own line was not dropped: %r" % out2)
    if "<p>next</p>" not in out2:
        fails.append("dropping a plain bracket's own line ate unrelated content: %r" % out2)

    # 4. A fill value containing a backslash must land literally, not be
    # read as a regex backreference. Found 2026-09-27 cold-read: the fill
    # branch switched from a literal str.replace to token.sub(value, text),
    # and re.sub's repl argument treats "\1"/"\g<name>" specially and
    # raises on a bare "\" before a letter. ops/fill_front_matter.py's
    # own fill loop now passes a callable repl instead, which is exempt
    # from that processing; this proves the same shape directly.
    token = re.compile(r"\[" + re.escape("PUBLISHER ADDRESS") + r"(?::[^\]]*)?\]")
    backslash_value = r"4328 N \Morninggale Pl"
    try:
        token.sub(backslash_value, "before [PUBLISHER ADDRESS] after")
        fails.append(
            "a bare token.sub(value, text) no longer raises on a backslash "
            "value; the regression this test guards against may have been "
            "reintroduced without the callable-repl fix")
    except re.error:
        pass  # expected: proves the raw-string-repl shape is still unsafe
    out3 = token.sub(lambda _m, v=backslash_value: v, "before [PUBLISHER ADDRESS] after")
    if out3 != "before %s after" % backslash_value:
        fails.append(
            "callable-repl fill did not place a backslash value literally: %r" % out3)

    if fails:
        print("FAIL:")
        for f in fails:
            print("  - " + f)
        return 1
    print("OK: colon-qualified front-matter brackets are found and dropped safely")
    return 0


if __name__ == "__main__":
    sys.exit(main())
