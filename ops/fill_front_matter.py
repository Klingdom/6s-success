#!/usr/bin/env python3
"""
Fill the book and manual front matter placeholders in one pass.

Why this exists
---------------
Ten bracketed fields appear 13 times across 7 files, including both the book
front matter and three copies of the manual. Issue #3 has been open since
16 August partly because "fill in the front matter" sounds like a 20 minute
job and is actually a find-and-replace across files that are easy to miss.
This makes it one command, so the moment the values exist they land
everywhere at once and nothing is left half filled.

Answers live in ops/front-matter.json. Any field still set to null is left
bracketed rather than guessed, because a copyright page is legally material
and a plausible looking wrong value is worse than a visible blank.

Two fields deliberately have no sensible default and are called out in
--check, because filling them wrongly would be fabricated attribution:
DESIGNER and ILLUSTRATOR. Nobody designed the cover; ops/build_cover.py
generates it. Nobody drew the illustrations; they are model generated. Naming
a person there would invent a credit, which CLAUDE.md section 8 forbids.

Run:  python ops/fill_front_matter.py --check
      python ops/fill_front_matter.py --apply
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANSWERS = os.path.join(ROOT, "ops", "front-matter.json")

TARGETS = [
    "content/book/6S-Success-Front-Matter/FRONT_MATTER.md",
    "content/book/6S-Chapter-3-Content-Package/pdf-ebook/chapter-pdf-frontmatter.md",
    "content/book/6S-Success-Chapter-3/content-package/pdf-ebook/chapter-pdf-frontmatter.md",
    "content/book/6S-Success-Chapter-4/content-package/pdf-ebook/chapter-pdf-frontmatter.md",
    "content/manual/6S Home Micro Zone SOP Field Manual v3.html",
    "content/manual/micro-zone-manual-publishable.html",
    "content/manual/print/6S-Micro-Zone-Manual-PRINT-7x10.html",
]

FIELD = re.compile(r"\[([A-Z][A-Za-z0-9 ,._/-]+)\]")

# The same field is spelled several different ways across the book and the
# three copies of the manual, because they were drafted at different times.
# Issue #3 counted 13 blanks in one file; across all seven there are 63, under
# 19 different names for 9 actual questions. Answering the 13 would have left
# the manual still full of blanks, so every spelling maps to one canonical
# answer here and one value fills all of them.
ALIASES = {
    "AUTHOR / RIGHTS HOLDER": ["AUTHOR OR RIGHTS HOLDER", "AUTHOR NAME"],
    "IMPRINT / PUBLISHER NAME": ["IMPRINT OR PUBLISHER NAME",
                                 "PUBLISHER / IMPRINT PLACEHOLDER"],
    "ISBN": ["ISBN PLACEHOLDER"],
    "PUBLISHER CONTACT": ["CONTACT PLACEHOLDER", "CONTACT / RIGHTS PLACEHOLDER"],
    "TERRITORY / PRINTING STATEMENT": ["TERRITORY STATEMENT",
                                       "COUNTRY OF MANUFACTURE"],
}


def expand(answers):
    """One answer covers every spelling of the same question."""
    out = dict(answers)
    for canonical, others in ALIASES.items():
        value = answers.get(canonical)
        if value:
            for name in others:
                out.setdefault(name, value)
    return out


# Some placeholders are not unknowns waiting on an answer, they are lines that
# should not exist on a digital edition at all. An ISBN is a registered
# identifier and inventing one would collide with somebody's real book. A
# territory and printing statement describes a print run. A designer and an
# illustrator credit name people who did not do the work. Setting a field to
# this sentinel deletes the whole line rather than filling it.
DROP = "__DROP_LINE__"


def load_answers():
    if not os.path.exists(ANSWERS):
        return {}
    return json.load(io.open(ANSWERS, encoding="utf-8"))


def scan():
    """field -> {path: count}, over the files that actually exist."""
    found = {}
    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding="utf-8", errors="replace").read()
        for name in FIELD.findall(text):
            found.setdefault(name, {}).setdefault(rel, 0)
            found[name][rel] += 1
    return found


def main(apply_it):
    answers = load_answers()
    found = scan()
    if not found:
        print("  nothing bracketed left, front matter is filled")
        return 0

    ready = {k: v for k, v in expand(answers).items() if v}
    print(f"  {len(found)} fields still bracketed, "
          f"{sum(sum(f.values()) for f in found.values())} occurrences")
    for name in sorted(found):
        total = sum(found[name].values())
        state = f"-> {ready[name]!r}" if name in ready else "STILL NEEDED"
        print(f"    {name:34} x{total}  {state}")

    missing = [n for n in sorted(found) if n not in ready]
    if missing:
        print(f"\n  {len(missing)} without an answer in ops/front-matter.json")

    if not apply_it:
        return 0
    if not ready:
        print("\n  nothing to apply, ops/front-matter.json has no values yet")
        return 0

    changed = 0
    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = original = io.open(path, encoding="utf-8", errors="replace").read()
        for name, value in ready.items():
            token = "[" + name + "]"
            if value == DROP:
                # Drop the line the placeholder sits on rather than
                # filling it with something untrue.
                nl = chr(10)
                text = nl.join(ln for ln in text.split(nl) if token not in ln)
                continue
            text = text.replace(token, value)
        if text != original:
            io.open(path, "w", encoding="utf-8", newline="").write(text)
            changed += 1
            print(f"  filled {rel}")
    print(f"\n  {changed} files updated")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
