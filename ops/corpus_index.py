#!/usr/bin/env python3
"""
Index the content corpus so it can actually be used.

WHY THIS EXISTS
---------------
Chapter content packages sit in content/book, holding thousands of markdown
files: LinkedIn posts, Facebook posts, X posts, articles, newsletters, carousel
outlines, quote cards, infographic specs, diagram ideas, SEO briefs, key
takeaways.

All of it is written. Most of it is good. None of it is published, and the
dashboard has been reporting it as "unused" for a week without anybody being
able to do anything about that, because 2,601 files scattered across 53 folders
is not a library, it is a pile.

This turns the pile into a queue: what exists, of what kind, for which chapter,
how long it is, and whether it is ready to post as written.

WHAT IT DOES NOT DO
-------------------
It does not rewrite anything. The corpus is Phil's writing and the whole point
is that it is already finished. This reads and catalogues.

WHY READINESS IS SCORED RATHER THAN ASSUMED
-------------------------------------------
Some of these files are finished posts. Others are outlines, specs, or notes to
a designer. Publishing an infographic spec as though it were a post would be
embarrassing, so each file is classified by what it actually is, and only files
that read as finished prose are marked ready.

Run:  python ops/corpus_index.py
      python ops/corpus_index.py --ready linkedin
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, "content", "book")
OUT = os.path.join(ROOT, "ops", "corpus-index.json")

# What a filename tells us about what is inside. Ordered: the first match wins,
# so the more specific patterns come first.
KINDS = [
    (r"linkedin-posts",       "linkedin-post",     True),
    (r"linkedin-article",     "linkedin-article",  True),
    (r"linkedin-newsletter",  "newsletter",        True),
    (r"linkedin-carousel",    "carousel-outline",  False),
    (r"linkedin-comment",     "comment-prompt",    False),
    (r"facebook-longform",    "facebook-post",     True),
    (r"facebook-posts",       "facebook-post",     True),
    (r"facebook-group",       "facebook-post",     True),
    (r"x-thread",             "x-post",            True),
    (r"x-short-posts",        "x-post",            True),
    (r"twitter",              "x-post",            True),
    (r"^newsletter-version",  "newsletter",        True),
    (r"quote-card",           "quote-card",        True),
    (r"chapter-quotes",       "quote",             True),
    (r"chapter-summary",      "summary",           True),
    (r"chapter-key-takeaway", "takeaways",         True),
    (r"chapter-cta",          "cta",               False),
    (r"chapter-seo",          "seo-brief",         False),
    (r"chapter-outline",      "outline",           False),
    (r"infographic",          "design-spec",       False),
    (r"diagram",              "design-spec",       False),
    (r"image-generation",     "image-prompt",      False),
    (r"teleprompter|script",  "video-script",      True),
    (r"slides",               "design-spec",       False),
]


def classify(path: str) -> tuple[str, bool]:
    name = os.path.basename(path).lower()
    for pat, kind, publishable in KINDS:
        if re.search(pat, name):
            return kind, publishable
    return "other", False


def chapter_of(path: str) -> str:
    rel = os.path.relpath(path, BOOK).replace(os.sep, "/")
    m = re.search(r"[Cc]hapter[- _]?(\d+)", rel)
    return f"ch{int(m.group(1)):02d}" if m else rel.split("/")[0][:28]


def units_in(text: str, kind: str = "") -> int:
    """How many separate posts a file holds.

    These files are usually a numbered series under one heading, so a file is
    not one unit. Counting the h2 sections gives the real number of things that
    could be posted. X threads and short-post sets instead number each post
    "1/", "2/" on its own line with no heading, so that pattern is counted too.

    quote, summary and takeaways each hold their own real number worth its own
    rule rather than falling through to a count that never matches their
    shape and silently reports 1: a quote file is a numbered "Verbatim lines"
    list plus one quote per other heading; a summary file is one item per
    heading, source-files section excluded, or the whole headingless file;
    takeaways is a numbered list with a bold lead in most chapters, a plain
    bullet list in the rest.
    """
    if kind == "quote":
        n = len(re.findall(r'^\d+\.\s+"', text, re.M))
        n += sum(1 for h in re.findall(r"^##\s+(.+)$", text, re.M)
                 if "verbatim lines" not in h.lower())
        if n:
            return n
    elif kind == "summary":
        n = sum(1 for h in re.findall(r"^##\s+(.+)$", text, re.M)
                if "source" not in h.lower())
        if n:
            return n
    elif kind == "takeaways":
        n = len(re.findall(r"^\d+\.\s+\*\*", text, re.M))
        if not n:
            n = len(re.findall(r"^-\s+\S", text, re.M))
        if n:
            return n
    n = len(re.findall(r"^##\s+\d+\.", text, re.M))
    if not n:
        n = len(re.findall(r"^\**\d+[./]\**\s*$", text, re.M))
    return n if n else 1


def build_index() -> tuple[list, dict, dict]:
    """Scan the corpus and classify every file. No printing, no file write.

    The one place this logic lives, so a caller like ops/dashboard.py reports
    the same ready-unit count this module's own CLI prints, rather than a
    second hand-typed guess drifting away from it.
    """
    files = glob.glob(os.path.join(BOOK, "**", "*.md"), recursive=True)
    rows, by_kind, by_chapter = [], {}, {}

    for f in files:
        try:
            text = io.open(f, encoding="utf-8", errors="replace").read()
        except Exception:                                     # noqa: BLE001
            continue
        kind, publishable = classify(f)
        words = len(text.split())
        # A finished post has prose. A spec has bullet points and field names.
        # Below 60 words nothing is a finished anything.
        ready = publishable and words >= 60
        rows.append({
            "path": os.path.relpath(f, ROOT).replace(os.sep, "/"),
            "chapter": chapter_of(f), "kind": kind,
            "words": words, "units": units_in(text, kind) if ready else 0,
            "ready": ready,
        })
        by_kind[kind] = by_kind.get(kind, 0) + 1
        by_chapter[chapter_of(f)] = by_chapter.get(chapter_of(f), 0) + 1

    return rows, by_kind, by_chapter


def main() -> int:
    rows, by_kind, by_chapter = build_index()
    ready = [r for r in rows if r["ready"]]
    units = sum(r["units"] for r in ready)

    print(f"  {len(rows)} files across {len(by_chapter)} chapters\n")
    print(f"  {'kind':20} {'files':>6}  {'ready':>6}")
    print(f"  {'-'*20} {'-'*6}  {'-'*6}")
    for k in sorted(by_kind, key=lambda x: -by_kind[x]):
        r = sum(1 for x in rows if x["kind"] == k and x["ready"])
        print(f"  {k:20} {by_kind[k]:>6}  {r:>6}")

    print(f"\n  {len(ready)} files read as finished prose, holding about "
          f"{units} separately postable units.")
    print(f"  {len(rows) - len(ready)} are outlines, specs, prompts or notes, "
          "and are not postable as written.")

    json.dump({"files": rows,
               "summary": {"total": len(rows), "ready_files": len(ready),
                           "postable_units": units,
                           "by_kind": by_kind}},
              io.open(OUT, "w", encoding="utf-8", newline=""), indent=1)
    print(f"\n  written to {os.path.relpath(OUT, ROOT)}")

    if "--ready" in sys.argv:
        want = sys.argv[sys.argv.index("--ready") + 1]
        sel = [r for r in ready if want in r["kind"]]
        print(f"\n  {len(sel)} ready {want} file(s):")
        for r in sorted(sel, key=lambda x: x["chapter"])[:20]:
            print(f"    {r['chapter']}  {r['units']:>2} units  {r['path']}")

    # The corpus is the largest unexploited asset this business owns. If this
    # ever reports near zero, something has moved or been deleted and the
    # dashboard figure that depends on it is lying.
    assert len(rows) > 1000, f"only {len(rows)} corpus files found, expected thousands"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
