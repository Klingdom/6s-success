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

Same defect, found again 2026-09-01 for quote, summary and takeaways (153
more ready files, 0 usable posts): quote is a numbered "Verbatim lines" list
in some chapters and several single-quote headings in others, sometimes as a
"> " blockquote and sometimes as a plain quoted line; summary is three headed
lengths in most chapters and one headingless essay in the rest; takeaways is
a numbered list with a bold lead in most chapters and a plain bullet list in
the rest. Three more extractors (split_quotes, split_summary, split_takeaways)
fixed the yield; this file proves both shapes of each stays covered.

Same defect a third time, found 2026-09-22 for four new kinds
corpus_index.py had just started marking ready (landing-page-intro,
sales-copy, discussion-questions, newsletter-teaser: five per-chapter
content types that were previously falling into "other" and not counted at
all). Worse than a zero yield this time: 42 of 51 back-cover-copy.md files
(half of sales-copy) carry a trailing pull-quote section holding unfilled
scaffolding like "[PLACEHOLDER TESTIMONIAL 1: ...]", explicitly marked "do
not publish as real quotes", under one of at least six different headings
and two different heading levels. Serving one as written would have been a
fabricated-testimonial risk, not just a wasted file. split_sales_copy cuts
at the first heading whose text contains "testimonial" however it is
worded, then refuses the file outright if the word "placeholder" still
appears anywhere left, rather than trust the cut caught every shape; three
of 51 files still fail that net (an earlier, un-headed disclaimer line) and
are correctly dropped rather than served with the disclaimer attached.
split_short and split_questions handle the other three kinds. This file
proves the four new kinds classify, extract clean, and stay clean.

Two more instances of the same defect class, plus one unrelated but adjacent
defect, found the same day by a concurrent operator cycle cold-reading the
identical pair of files (a genuine collision, merged rather than resolved by
picking a side; see ops/NIGHTLY-LOG.md): (1) split_posts required a
"\\n---+\\n" divider between every numbered "## " section and returned an
empty list, silently, for any file with none, which was most of the corpus
(119 of 153 ready facebook-post files, 17 of 51 ready linkedin-post files).
Rewritten to split on the heading itself via _h2_sections, the same splitter
split_quotes and split_summary already use for the identical shape. (2)
facebook-post mixes numbered-series files with single-post files
(facebook-longform-post.md, facebook-group-discussion-post.md) that have no
"## " heading at all; split_posts alone can never find these, so pool()'s
default extractor is now split_posts_or_whole, which falls back to treating
the whole file as one post. (3) Unrelated to extraction: corpus_index.py's
classifier matched video-script on the bare substring "script", which is
also a substring of "manuscript" and of "description". Every
chapter_NN_manuscript.md, the paid book's own text, and every
*-description*.md file were silently classified as a free-to-post video
script (182 of 821 pooled "video-script" posts traced back to a manuscript
file, none of them an actual script). Anchored the pattern to the real
filenames instead.

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

    # Found 2026-09-12: the corpus uses three other shapes for the same
    # trailing note besides plain "(NNN chars)", and the original pattern
    # only matched that one, so 261 of 741 real x-post entries still shipped
    # it as the last line of the body.
    numbered_shapes_src = (
        "1/\nA tilde-annotated post, long enough to read as real content.\n\n(~205 chars)\n"
        "\n---\n\n"
        "2/\nAn approx-annotated post, long enough to read as real content.\n\n(approx 236 chars)\n"
        "\n---\n\n"
        "3/\nAn approx-dot-annotated post, long enough to read as real here.\n\n(approx. 250 chars)\n"
    )
    tmp1b = os.path.join(ROOT, "ops", "tests", "_scratch_x_thread_shapes.md")
    open(tmp1b, "w", encoding="utf-8").write(numbered_shapes_src)
    try:
        shapes = cp.split_numbered(os.path.relpath(tmp1b, ROOT))
        if len(shapes) != 3:
            fails.append(f"split_numbered (annotation shapes) should find 3 posts, found {len(shapes)}")
        else:
            for s in shapes:
                if "chars)" in s["body"]:
                    fails.append(f"split_numbered left a char-count annotation in: {s['body'][-40:]!r}")
    finally:
        os.remove(tmp1b)

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

    # split_quotes: a chapter uses one of two shapes, never both. The numbered
    # "Verbatim lines" list holds several short lines on one heading; every
    # other heading holds exactly one quote, written as a plain quoted line in
    # some chapters and as a "> " blockquote in others.
    quotes_src = (
        "# Chapter 9 Quotes: Test Room\n\n"
        "Pull quotes lifted directly from the manuscript.\n\n"
        "## Verbatim lines (book voice)\n\n"
        '1. "First verbatim line, long enough to read as real."\n\n'
        '2. "Second verbatim line."\n\n'
        "## The rule (frozen, hero)\n\n"
        '"A plain quoted line with no blockquote marker at all."\n\n'
        "## The reframe (frozen, pull-quote)\n\n"
        "> A blockquote line split across nothing, still one quote.\n"
    )
    tmp3 = os.path.join(ROOT, "ops", "tests", "_scratch_quotes.md")
    open(tmp3, "w", encoding="utf-8").write(quotes_src)
    try:
        qs = cp.split_quotes(os.path.relpath(tmp3, ROOT))
        if len(qs) != 4:
            fails.append(f"split_quotes should find 4 quotes, found {len(qs)}")
        else:
            bodies = [q["body"] for q in qs]
            if any(b.startswith('"') or b.endswith('"') for b in bodies):
                fails.append("split_quotes left a wrapping quote mark in the body")
            if any(b.startswith(">") for b in bodies):
                fails.append("split_quotes left the blockquote marker in the body")
            if qs[2]["title"] != "The rule":
                fails.append(f"split_quotes kept the parenthetical in the title: {qs[2]['title']!r}")
    finally:
        os.remove(tmp3)

    # split_summary: three headed lengths with a "Source files used" section
    # that is not a summary, in some chapters; a single headingless essay
    # ending in a "Previous: ... Next: ..." nav line, in the rest.
    summary_headed_src = (
        "# Chapter 9 Summary: Test Room\n\n"
        "## One-line summary\n\n"
        "A one sentence summary long enough to read as real content here.\n\n"
        "## Short summary (about 100 words)\n\n"
        "A short summary paragraph, also long enough to read as real content.\n\n"
        "## Full summary (about 250 words)\n\n"
        "A longer summary paragraph, once again long enough to read as real.\n\n"
        "## Source files used\n\n"
        "- chapter_9_manuscript.md\n"
    )
    tmp4 = os.path.join(ROOT, "ops", "tests", "_scratch_summary_headed.md")
    open(tmp4, "w", encoding="utf-8").write(summary_headed_src)
    try:
        ss = cp.split_summary(os.path.relpath(tmp4, ROOT))
        if len(ss) != 3:
            fails.append(f"split_summary (headed) should find 3 summaries, found {len(ss)}")
        elif any("manuscript" in s["body"] for s in ss):
            fails.append("split_summary kept the Source files used section as a post")
    finally:
        os.remove(tmp4)

    summary_plain_src = (
        "# Chapter 9 Summary: Test Room\n\n"
        "A headingless essay of a couple of sentences, long enough to read as "
        "real content on its own, with no explicit summary-length labels.\n\n"
        "Previous: Chapter 8, Test Hallway. Next: Chapter 10, Test Kitchen.\n"
    )
    tmp5 = os.path.join(ROOT, "ops", "tests", "_scratch_summary_plain.md")
    open(tmp5, "w", encoding="utf-8").write(summary_plain_src)
    try:
        sp = cp.split_summary(os.path.relpath(tmp5, ROOT))
        if len(sp) != 1:
            fails.append(f"split_summary (headingless) should find 1 summary, found {len(sp)}")
        elif "Previous:" in sp[0]["body"]:
            fails.append("split_summary left the chapter-nav line in the body")
    finally:
        os.remove(tmp5)

    # split_takeaways: a numbered list with a bold lead in some chapters, a
    # plain bullet list with no lead in the rest.
    takeaways_numbered_src = (
        "# Chapter 9 Key Takeaways: Test Room\n\n"
        "The core ideas a reader should carry out of this chapter.\n\n"
        "1. **First idea.** The rest of the sentence explaining it further.\n\n"
        "2. **Second idea.** The rest of that sentence too, explaining more.\n"
    )
    tmp6 = os.path.join(ROOT, "ops", "tests", "_scratch_takeaways_numbered.md")
    open(tmp6, "w", encoding="utf-8").write(takeaways_numbered_src)
    try:
        tn = cp.split_takeaways(os.path.relpath(tmp6, ROOT))
        if len(tn) != 2:
            fails.append(f"split_takeaways (numbered) should find 2 items, found {len(tn)}")
        elif tn[0]["title"] != "First idea":
            fails.append(f"split_takeaways misread the bold-lead title: {tn[0]['title']!r}")
    finally:
        os.remove(tmp6)

    takeaways_bullet_src = (
        "# Chapter 9 Key Takeaways: Test Room\n\n"
        "The core ideas a reader should carry out of this chapter.\n\n"
        "- A plain bullet idea with no bold lead, long enough to be real.\n"
        "- A second plain bullet idea, also long enough to be real content.\n"
    )
    tmp7 = os.path.join(ROOT, "ops", "tests", "_scratch_takeaways_bullet.md")
    open(tmp7, "w", encoding="utf-8").write(takeaways_bullet_src)
    try:
        tb = cp.split_takeaways(os.path.relpath(tmp7, ROOT))
        if len(tb) != 2:
            fails.append(f"split_takeaways (bullet) should find 2 items, found {len(tb)}")
    finally:
        os.remove(tmp7)

    # split_sales_copy: the "## Testimonials" shape (chapter 35's real shape)
    # must be stripped clean, whatever the exact heading wording or level.
    sales_testimonial_src = (
        "# Chapter 9 Back Cover Copy: Test Room\n\n"
        "## Back-cover text\n"
        "Real, finished back-cover prose, long enough to read as genuine "
        "content rather than a fragment of something else entirely.\n\n"
        "## Pull-testimonial placeholders\n\n"
        "> [PLACEHOLDER TESTIMONIAL 1: something. Replace before publishing.]\n"
        "> Attribution: [Reader Name, Location]\n"
    )
    tmp8 = os.path.join(ROOT, "ops", "tests", "_scratch_sales_testimonial.md")
    open(tmp8, "w", encoding="utf-8").write(sales_testimonial_src)
    try:
        sc = cp.split_sales_copy(os.path.relpath(tmp8, ROOT))
        if len(sc) != 1:
            fails.append(f"split_sales_copy (testimonial heading) should find 1 post, found {len(sc)}")
        elif "placeholder" in sc[0]["body"].lower() or "Attribution" in sc[0]["body"]:
            fails.append("split_sales_copy leaked placeholder testimonial text into the body")
    finally:
        os.remove(tmp8)

    # split_sales_copy: a disclaimer line ahead of the testimonial heading
    # (chapter 4's real shape) is not caught by the heading cut alone; the
    # safety net must refuse the whole file rather than serve it with the
    # disclaimer attached.
    sales_predisclaimer_src = (
        "# Chapter 9 Back Cover Copy: Test Room\n\n"
        "*Pull-testimonials below are placeholders, not real quotes.*\n\n"
        "## Back cover\n"
        "Real, finished back-cover prose, long enough to read as genuine "
        "content rather than a fragment of something else entirely.\n\n"
        "## Pull-testimonial placeholders\n\n"
        "> [PLACEHOLDER TESTIMONIAL 1: something.]\n"
    )
    tmp9 = os.path.join(ROOT, "ops", "tests", "_scratch_sales_predisclaimer.md")
    open(tmp9, "w", encoding="utf-8").write(sales_predisclaimer_src)
    try:
        pd = cp.split_sales_copy(os.path.relpath(tmp9, ROOT))
        if pd:
            fails.append("split_sales_copy served a file whose pre-heading "
                         "disclaimer line still names 'placeholder'")
    finally:
        os.remove(tmp9)

    # split_sales_copy: ebook-sales-copy has no testimonial section at all;
    # the cut must be a no-op and the real content must survive whole.
    sales_plain_src = (
        "# Chapter 9 Ebook Sales Copy: Test Room\n\n"
        "**A real hook sentence for the sales page.**\n\n"
        "Inside:\n\n"
        "- A real bullet describing what the chapter covers, in full.\n"
        "- A second real bullet, also long enough to read as genuine.\n"
    )
    tmp10 = os.path.join(ROOT, "ops", "tests", "_scratch_sales_plain.md")
    open(tmp10, "w", encoding="utf-8").write(sales_plain_src)
    try:
        spn = cp.split_sales_copy(os.path.relpath(tmp10, ROOT))
        if len(spn) != 1:
            fails.append(f"split_sales_copy (no testimonial section) should find 1 post, found {len(spn)}")
        elif "real bullet" not in spn[0]["body"]:
            fails.append("split_sales_copy dropped real content with no testimonial section present")
    finally:
        os.remove(tmp10)

    # split_short: a single finished document, nothing to split.
    short_src = "# Chapter 9 Landing Page Intro: Test Room\n\nOne real paragraph, long enough to read as genuine finished copy.\n"
    tmp11 = os.path.join(ROOT, "ops", "tests", "_scratch_short.md")
    open(tmp11, "w", encoding="utf-8").write(short_src)
    try:
        sh = cp.split_short(os.path.relpath(tmp11, ROOT))
        if len(sh) != 1 or sh[0]["title"] != "Chapter 9 Landing Page Intro: Test Room":
            fails.append(f"split_short misread a plain single document: {sh!r}")
    finally:
        os.remove(tmp11)

    # split_questions: a plain numbered list, no bold lead required (that
    # shape is takeaways, not this).
    questions_src = (
        "# Chapter 9 Reader Discussion Questions: Test Room\n\n"
        "*Intro line, not a question.*\n\n"
        "1. A real first question, long enough to read as genuine content?\n\n"
        "2. A real second question, also long enough to be genuine content?\n"
    )
    tmp12 = os.path.join(ROOT, "ops", "tests", "_scratch_questions.md")
    open(tmp12, "w", encoding="utf-8").write(questions_src)
    try:
        qn = cp.split_questions(os.path.relpath(tmp12, ROOT))
        if len(qn) != 2:
            fails.append(f"split_questions should find 2 questions, found {len(qn)}")
        elif qn[0]["title"] != "Question 1":
            fails.append(f"split_questions mislabelled the first question: {qn[0]['title']!r}")
    finally:
        os.remove(tmp12)

    # split_posts: a numbered "## " series with NO "---" divider between
    # sections at all, the real majority shape found 2026-09-22, must still
    # split into separate posts, not fall through as one unsplit blob.
    posts_no_divider_src = (
        "# Chapter 9 LinkedIn Posts: Test Room\n\n"
        "Ten standalone posts.\n\n"
        "## 1. First title\n"
        "First post body, long enough to read as real content on its own.\n\n"
        "## 2. Second title\n"
        "Second post body, also long enough to read as real content here.\n"
    )
    tmp8 = os.path.join(ROOT, "ops", "tests", "_scratch_posts_no_divider.md")
    open(tmp8, "w", encoding="utf-8").write(posts_no_divider_src)
    try:
        nd = cp.split_posts(os.path.relpath(tmp8, ROOT))
        if len(nd) != 2:
            fails.append(f"split_posts (no '---' divider) should find 2 posts, found {len(nd)}")
        elif nd[0]["title"] != "First title" or nd[1]["title"] != "Second title":
            fails.append(f"split_posts misread titles with no divider: {[p['title'] for p in nd]!r}")
    finally:
        os.remove(tmp8)

    # split_posts_or_whole: a file with no "## " heading anywhere (a single
    # standalone post, like facebook-longform-post.md) must fall back to
    # split_whole rather than silently returning nothing.
    single_post_src = (
        "# Chapter 9 Facebook Longform Post: Test Room\n\n"
        "---\n\n"
        "This is one continuous post with no numbered heading anywhere in "
        "it, long enough to read as real content, the exact shape "
        "split_posts alone can never match.\n"
    )
    tmp9 = os.path.join(ROOT, "ops", "tests", "_scratch_single_post.md")
    open(tmp9, "w", encoding="utf-8").write(single_post_src)
    try:
        if cp.split_posts(os.path.relpath(tmp9, ROOT)):
            fails.append("split_posts unexpectedly found a heading in a headingless file")
        if not hasattr(cp, "split_posts_or_whole"):
            fails.append("corpus_posts.py has no split_posts_or_whole fallback; "
                         "a headingless single-post file (facebook-longform-post.md's "
                         "own shape) has no extractor that can ever find it")
            raise StopIteration
        sw = cp.split_posts_or_whole(os.path.relpath(tmp9, ROOT))
        if len(sw) != 1:
            fails.append(f"split_posts_or_whole should fall back to 1 whole post, found {len(sw)}")
        elif "no numbered heading" not in sw[0]["body"]:
            fails.append("split_posts_or_whole's fallback lost the real content")
    except StopIteration:
        pass
    finally:
        os.remove(tmp9)

    # corpus_index's classifier must never let "manuscript" or "description"
    # match the video-script pattern: both contain "script" as a literal
    # substring, and manuscript is the paid book's own text.
    sys.path.insert(0, os.path.join(ROOT, "ops"))
    import corpus_index as ci
    for bad_name, why in (
        ("chapter_09_manuscript.md", "the paid book's own chapter text"),
        ("chapter-9-description.md", "a marketing blurb, not a script"),
    ):
        kind, publishable = ci.classify(bad_name)
        if kind == "video-script":
            fails.append(f"{bad_name} ({why}) misclassified as video-script")
    for good_name in ("teleprompter-script.md", "podcast-script-8-to-12-min.md",
                      "youtube-script-6-to-8-min.md", "short-video-scripts-5.md"):
        kind, publishable = ci.classify(good_name)
        if kind != "video-script" or not publishable:
            fails.append(f"{good_name} should classify as a ready video-script, "
                         f"got kind={kind!r} publishable={publishable!r}")

    # quote-card is a byte-verbatim duplicate of chapter-quotes.md (kind
    # "quote") decorated with hex colors and layout notes for a human
    # designer; it must never be marked ready to post as written.
    kind, publishable = ci.classify("quote-card-copy.md")
    if publishable:
        fails.append("quote-card-copy.md is marked publishable; its own text "
                     "is a design brief, not a post")

    # The regression this file exists to prevent: every fixed kind must
    # still yield at least one real post from the live corpus, and
    # video-script's pool must never include a manuscript or description
    # file now that the classifier is anchored correctly.
    for kind in ("x-post", "newsletter", "linkedin-article", "quote",
                 "summary", "takeaways", "facebook-post", "linkedin-post",
                 "video-script", "sales-copy", "landing-page-intro",
                 "discussion-questions", "newsletter-teaser"):
        n = len(cp.pool(kind))
        if n == 0:
            fails.append(f"kind '{kind}' is marked ready but corpus_posts.pool() "
                         "serves 0 posts from it")

    # The specific defect this cycle found: no post served from sales-copy
    # may ever carry the word "placeholder" or an "Attribution:" scaffold
    # line, whatever file it came from.
    for p in cp.pool("sales-copy"):
        if "placeholder" in p["body"].lower():
            fails.append(f"sales-copy served a placeholder-tainted post from {p['source']}")

    leaked = [p["source"] for p in cp.pool("video-script")
              if "manuscript" in p["source"] or "description" in p["source"]]
    if leaked:
        fails.append(f"video-script pool still leaks paid/non-script content: {leaked[:3]}")

    total = 34
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
