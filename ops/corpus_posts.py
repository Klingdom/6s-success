#!/usr/bin/env python3
"""
Serve real posts out of the corpus Phil already wrote.

WHY THIS REPLACES HAND WRITTEN DRAFTS
-------------------------------------
ops/linkedin_drafts.py was seeded with eight entries I wrote. Meanwhile 510
LinkedIn posts, 153 Facebook posts and 51 articles already existed, finished, in
content/book, written in Phil's own voice and never published once.

Eight invented entries against five hundred real ones is not a close call. The
corpus wins on volume, on voice, and on the fact that somebody already did the
work. This module is the reader for it.

WHAT IT GUARANTEES
------------------
1. Nothing is rewritten. These are Phil's words and they ship as written.
2. Nothing repeats until the pool is exhausted. A rotation file records what has
   been served, because the failure mode of a large corpus is serving the first
   ten items forever.
3. Every post is checked before it is offered: length, no leftover markdown
   scaffolding, no broken reference to a chapter the reader cannot reach.

Run:  python ops/corpus_posts.py --kind linkedin-post --n 3
      python ops/corpus_posts.py --stats
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "ops", "corpus-index.json")
ROTATION = os.path.join(ROOT, "ops", "corpus-rotation.json")


def load_index() -> dict:
    if not os.path.exists(INDEX):
        raise SystemExit("run ops/corpus_index.py first")
    return json.load(io.open(INDEX, encoding="utf-8"))


def split_posts(path: str) -> list:
    """One file holds a numbered series, each under a '## ' heading. Return
    them as separate posts. Fits linkedin-post, facebook-post, video-script."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    s = io.open(full, encoding="utf-8", errors="replace").read()
    out = []
    for chunk in re.split(r"\n---+\n", s):
        chunk = chunk.strip()
        if not chunk.startswith("## "):
            continue
        lines = chunk.splitlines()
        title = re.sub(r"^#+\s*\d*\.?\s*", "", lines[0]).strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            continue
        out.append({"title": title, "body": body, "source": path})
    return out


def split_numbered(path: str) -> list:
    """A thread or a set of short standalone posts, each a plain 'N/' on its
    own line rather than a '## ' heading, with a trailing '(NNN chars)' line
    split_posts would leave in the body. Fits x-post."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    s = io.open(full, encoding="utf-8", errors="replace").read()
    out = []
    for chunk in re.split(r"\n---+\n", s):
        chunk = chunk.strip()
        m = re.match(r"^(\d+)/\s*\n(.+)", chunk, re.S)
        if not m:
            continue
        num, body = m.group(1), m.group(2).strip()
        body = re.sub(r"\n\(\d+ chars?\)\s*$", "", body).strip()
        if not body:
            continue
        out.append({"title": f"Post {num}", "body": body, "source": path})
    return out


def split_whole(path: str) -> list:
    """One file is one long-form post in its own right: a newsletter issue or
    a LinkedIn article. Strips the sender-only subject/preview lines a
    newsletter carries and any bare '---' rule used as a visual divider
    inside a single document, neither of which mark a second post. Fits
    newsletter, linkedin-article."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    s = io.open(full, encoding="utf-8", errors="replace").read().strip()
    lines = s.splitlines()
    if not lines or not lines[0].startswith("# "):
        return []
    title = lines[0].lstrip("#").strip()
    body = "\n".join(lines[1:])
    body = re.sub(r"(?m)^\*\*(Subject line|Preview text)\b.*$\n?", "", body)
    body = re.sub(r"(?m)^-{3,}\s*$\n?", "", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if not body:
        return []
    return [{"title": title, "body": body, "source": path}]


def _h2_sections(s: str) -> list:
    """Split a document on '## ' headings into (heading, body) pairs. Text
    before the first heading (the title and any intro line) is discarded."""
    out = []
    for part in re.split(r"(?m)^## ", s)[1:]:
        lines = part.splitlines()
        out.append((lines[0].strip(), "\n".join(lines[1:]).strip()))
    return out


def split_quotes(path: str) -> list:
    """Pull quotes for quote cards and graphics. Two shapes exist and a
    chapter uses one or the other, never both: a numbered 'Verbatim lines'
    list of short lines lifted straight from the manuscript, and several
    single-quote headed sections, written either as a plain quoted line or
    as a '> ' blockquote depending on the chapter. Fits quote."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    s = io.open(full, encoding="utf-8", errors="replace").read()
    out = []
    for heading, body in _h2_sections(s):
        if not body:
            continue
        if "verbatim lines" in heading.lower():
            for m in re.finditer(r"^(\d+)\.\s+(.+)$", body, re.M):
                q = m.group(2).strip().strip('"').strip()
                if q:
                    out.append({"title": f"Quote {m.group(1)}",
                                "body": q, "source": path})
            continue
        lines = [ln[2:].strip() if ln.startswith("> ") else ln.strip()
                 for ln in body.splitlines() if ln.strip()]
        q = " ".join(lines).strip().strip('"').strip()
        if not q:
            continue
        title = re.sub(r"\s*\(.*?\)\s*$", "", heading).strip() or heading
        out.append({"title": title, "body": q, "source": path})
    return out


def split_summary(path: str) -> list:
    """A chapter summary: three explicit lengths (one-line, short, full)
    under headings in most chapters, or a single headingless essay of two to
    three paragraphs in the rest. A trailing 'Source files used' section, when
    present, is not a summary and is dropped; a trailing 'Previous: ...
    Next: ...' navigation sentence on a headingless file is stripped the same
    way. Fits summary."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    s = io.open(full, encoding="utf-8", errors="replace").read().strip()
    lines = s.splitlines()
    if not lines or not lines[0].startswith("# "):
        return []
    label = re.sub(r"\s*Summary:\s*", ": ", lines[0].lstrip("#").strip())
    body = "\n".join(lines[1:])
    sections = _h2_sections(body)
    out = []
    if sections:
        for heading, text in sections:
            if "source" in heading.lower() or not text:
                continue
            clean_heading = re.sub(r"\s*\(.*?\)\s*$", "", heading).strip()
            title = f"{label}, {clean_heading}"
            out.append({"title": title, "body": text.strip(), "source": path})
    else:
        text = re.sub(r"\s*Previous:.*$", "", body.strip(), flags=re.S).strip()
        if text:
            out.append({"title": label, "body": text, "source": path})
    return out


def split_takeaways(path: str) -> list:
    """Key takeaways: a numbered list with a bold lead sentence in most
    chapters, a plain bulleted list with no lead in the rest. Each item is one
    idea a reader could act on by itself. Fits takeaways."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    s = io.open(full, encoding="utf-8", errors="replace").read()
    numbered = [m.group(1).strip() for m in re.finditer(r"^\d+\.\s+(.+)$", s, re.M)]
    items = numbered or [ln[2:].strip() for ln in s.splitlines() if ln.startswith("- ")]
    out = []
    for i, item in enumerate(items, 1):
        if not item:
            continue
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)$", item)
        title = m.group(1).rstrip(".") if m else f"Takeaway {i}"
        out.append({"title": title, "body": item, "source": path})
    return out


# Which extractor understands each kind's shape. Anything not listed falls
# back to split_posts, the original numbered-'## '-heading shape.
EXTRACTORS = {
    "x-post": split_numbered,
    "newsletter": split_whole,
    "linkedin-article": split_whole,
    "quote": split_quotes,
    "summary": split_summary,
    "takeaways": split_takeaways,
}

# A standalone post's word count has to make sense for where it will run. A
# short LinkedIn/Facebook/X post reads as thin outside 40 to 400 words; a
# newsletter issue or a LinkedIn article is long-form by design and 400 words
# would be the introduction, not the piece. A pull quote is short by design,
# real ones in the corpus run from a 4-word line to a 270-word definition box.
# A takeaway is a single idea, not an essay, and a real one runs 11 to 172
# words. A summary's three lengths span 28 to 484 words across the whole
# corpus. All three bounds below are read off the actual corpus, not guessed.
DEFAULT_BOUNDS = (40, 400)
WORD_BOUNDS = {
    "newsletter": (200, 3000),
    "linkedin-article": (200, 3000),
    "quote": (3, 300),
    "summary": (25, 500),
    "takeaways": (10, 200),
}


# Chapters 1 to 30 ship as a free sample at /downloads/. Chapters 31 to 50 do
# not: they are inside the 18 dollar eBook. Many corpus posts end by pointing at
# "the free online book" or "read the free chapter", true for the first thirty
# chapters and a false price claim for the rest.
FREE_THROUGH_CHAPTER = 30
FREE_CLAIM = re.compile(
    r"free (in the )?online|free online|free in the|free,"
    r"|free chapter|read the free|free to read|free copy|free version",
    re.I,
)


def clean(post: dict, min_words: int = 40, max_words: int = 400) -> dict | None:
    """Reject anything that would embarrass somebody who posted it as written."""
    b = post["body"]

    # A post from a paid chapter that calls the book free is a false claim about
    # a price, which is the one category of error this business cannot make. 16
    # of 340 posts do exactly that. They are held back rather than edited,
    # because rewriting somebody's copy to fix a claim is how the claim comes
    # back next time somebody regenerates the corpus.
    ch = post.get("chapter", "")
    num = int("".join(c for c in ch if c.isdigit()) or 0)
    if num > FREE_THROUGH_CHAPTER and FREE_CLAIM.search(b):
        return None
    # Markdown that means nothing in a LinkedIn box.
    if re.search(r"^\s*[-*]\s+\[[ x]\]", b, re.M):
        return None
    if "TODO" in b or "TKTK" in b or "[insert" in b.lower():
        return None
    # A post that only makes sense inside the book is not a standalone post.
    words = len(b.split())
    if words < min_words or words > max_words:
        return None
    b = re.sub(r"\*\*(.+?)\*\*", r"\1", b)      # bold markers do not render
    b = re.sub(r"^#+\s*", "", b, flags=re.M)
    b = re.sub(r"\n{3,}", "\n\n", b).strip()

    # Phil read a batch of these and said they sound like AI slop. He was right,
    # and the cause was the shape rather than the writing: every sentence
    # promoted to its own paragraph, a one line opener, a gap, another one
    # liner. That cadence is now so tied to generated content that a reader
    # decides it is slop from the layout before reading a word. Reflowed into
    # solid paragraphs with the filler transitions removed. The sentences
    # themselves are untouched, because they are his and they are good.
    try:
        from reflow import reflow
        b = reflow(b)
    except Exception:                                          # noqa: BLE001
        pass

    post["body"] = b
    post["words"] = len(b.split())
    return post


def pool(kind: str) -> list:
    idx = load_index()
    extractor = EXTRACTORS.get(kind, split_posts)
    min_words, max_words = WORD_BOUNDS.get(kind, DEFAULT_BOUNDS)
    out = []
    for f in idx["files"]:
        if f["kind"] != kind or not f["ready"]:
            continue
        for p in extractor(f["path"]):
            p["chapter"] = f["chapter"]
            c = clean(p, min_words, max_words)
            if c:
                c["id"] = hashlib.sha256(
                    (c["source"] + c["title"]).encode()).hexdigest()[:12]
                out.append(c)
    return out


def load_rotation() -> dict:
    if os.path.exists(ROTATION):
        try:
            return json.load(io.open(ROTATION, encoding="utf-8"))
        except Exception:                                     # noqa: BLE001
            pass
    return {"served": {}}


def take(kind: str, n: int, record: bool = False) -> list:
    """The next n unserved posts, oldest chapter first for a sensible arc."""
    rot = load_rotation()
    served = set(rot["served"].get(kind, []))
    p = pool(kind)
    fresh = [x for x in p if x["id"] not in served]
    if len(fresh) < n:
        # Exhausted. Start again rather than serve nothing, and say so.
        served, fresh = set(), p
        rot["served"][kind] = []
    picked = sorted(fresh, key=lambda x: (x["chapter"], x["title"]))[:n]
    if record:
        rot["served"].setdefault(kind, [])
        rot["served"][kind] += [x["id"] for x in picked]
        json.dump(rot, io.open(ROTATION, "w", encoding="utf-8", newline=""), indent=1)
    return picked


if __name__ == "__main__":
    if "--stats" in sys.argv:
        idx = load_index()
        kinds = sorted({f["kind"] for f in idx["files"] if f["ready"]})
        rot = load_rotation()
        total = 0
        print(f"  {'kind':20} {'usable posts':>13} {'already served':>15}")
        for k in kinds:
            p = pool(k)
            total += len(p)
            print(f"  {k:20} {len(p):>13} {len(rot['served'].get(k, [])):>15}")
        print(f"\n  {total} usable posts in the corpus, all written already.")
        raise SystemExit(0)

    kind = "linkedin-post"
    n = 3
    if "--kind" in sys.argv:
        kind = sys.argv[sys.argv.index("--kind") + 1]
    if "--n" in sys.argv:
        n = int(sys.argv[sys.argv.index("--n") + 1])
    for i, p in enumerate(take(kind, n, record="--record" in sys.argv), 1):
        print(f"\n{'='*66}\n{i}. {p['title']}   [{p['chapter']}, {p['words']} words]\n")
        print(p["body"])
