#!/usr/bin/env python3
"""
A file corpus_index.py marks "ready" has to actually turn into a postable
unit, or "ready" is a claim nobody can act on.

Found 2026-09-01: x-post, newsletter and linkedin-article had 255 files
marked ready between them, and corpus_posts.py served exactly zero posts from
any of them, because its only extractor (split_posts) understood a single
shape, numbered sections under a "## " heading, and none of these three kinds
are written that way. x-post uses a bare "N/" line; newsletter and
linkedin-article are each one whole document. Two new extractors
(split_numbered, split_whole) fixed the yield; this file proves it stays
fixed and, separately, that broadening the false "free chapter" claim filter
to catch the real phrasing found in chapters 31 to 33 does not let it slip
back to the narrower, blind version.

Run:  python ops/tests/test_corpus_posts.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import corpus_posts as cp                                        # noqa: E402


def main() -> int:
    fails = []

    # split_numbered: a thread's "N/" chunks, with the "(NNN chars)" line
    # split_posts would have left sitting in the body.
    numbered_src = (
        "1/\nFirst post body, long enough to read as real.\n\n(48 chars)\n"
        "\n---\n\n"
        "2/\nSecond post body, also long enough to read as real.\n\n(53 chars)\n"
    )
    tmp = os.path.join(ROOT, "ops", "tests", "_scratch_x_thread.md")
    open(tmp, "w", encoding="utf-8").write(numbered_src)
    try:
        chunks = cp.split_numbered(os.path.relpath(tmp, ROOT))
        if len(chunks) != 2:
            fails.append(f"split_numbered should find 2 posts, found {len(chunks)}")
        elif "(48 chars)" in chunks[0]["body"] or "(53 chars)" in chunks[1]["body"]:
            fails.append("split_numbered left the char-count line in the body")
    finally:
        os.remove(tmp)

    # split_whole: one document is one post; the subject/preview meta lines
    # and a bare "---" rule are for the sender, not the reader, and must not
    # survive into the body.
    whole_src = (
        "# A Newsletter Title\n\n"
        "**Subject line (placeholder):** something\n\n"
        "**Preview text (placeholder):** something else\n\n"
        "---\n\n"
        "Hi friend, this is the real body of the newsletter issue.\n"
    )
    tmp2 = os.path.join(ROOT, "ops", "tests", "_scratch_newsletter.md")
    open(tmp2, "w", encoding="utf-8").write(whole_src)
    try:
        posts = cp.split_whole(os.path.relpath(tmp2, ROOT))
        if len(posts) != 1:
            fails.append(f"split_whole should find 1 post, found {len(posts)}")
        else:
            b = posts[0]["body"]
            if "Subject line" in b or "Preview text" in b:
                fails.append("split_whole left sender-only meta lines in the body")
            if "---" in b:
                fails.append("split_whole left a bare divider rule in the body")
            if "real body of the newsletter" not in b:
                fails.append("split_whole dropped the real content")
            if posts[0]["title"] != "A Newsletter Title":
                fails.append(f"split_whole misread the title: {posts[0]['title']!r}")
    finally:
        os.remove(tmp2)

    # The false-claim filter has to catch the real phrasing found live in the
    # corpus, not only the older "free online" wording it was first written
    # against. Body is padded past the 40-word floor so a rejection is only
    # ever about the claim, never the length.
    pad = " ".join(["Real corpus sentence standing in for length."] * 6)
    bad = {"body": f"{pad} Read the free chapter.", "chapter": "ch31"}
    good = {"body": f"{pad} Read more in the eBook.", "chapter": "ch31"}
    free_chapter_ok = {"body": f"{pad} Read the free chapter.", "chapter": "ch05"}

    if cp.clean(dict(bad)) is not None:
        fails.append("'Read the free chapter.' on a paid chapter (31) was not caught")
    if cp.clean(dict(good)) is None:
        fails.append("a clean paid-chapter post with no free claim was wrongly rejected")
    if cp.clean(dict(free_chapter_ok)) is None:
        fails.append("'Read the free chapter.' on a real free chapter (5) was "
                     "wrongly rejected, the claim is true there")

    # A newsletter/article-length body must not be squeezed through the same
    # 40-to-400-word box a short social post uses, and pool() has to be the
    # thing making that call, not clean()'s own default.
    short_newsletter = "One short paragraph, nowhere near newsletter length. " * 3
    if cp.clean({"body": short_newsletter, "chapter": "ch05"}, *cp.WORD_BOUNDS["newsletter"]) is not None:
        fails.append("a too-short body passed the newsletter word bounds")

    # The regression this file exists to prevent: each of the three fixed
    # kinds must still yield at least one real post from the live corpus.
    for kind in ("x-post", "newsletter", "linkedin-article"):
        n = len(cp.pool(kind))
        if n == 0:
            fails.append(f"kind '{kind}' is marked ready but corpus_posts.pool() "
                         "serves 0 posts from it")

    total = 8
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
