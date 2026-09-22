#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_corpus_posts_no_manuscript_leak() and
gate_corpus_posts_extraction_yield() actually catch the two defects they
were written for.

Found 2026-09-22 cold-reading ops/corpus_index.py and ops/corpus_posts.py
together: (1) the classifier matched kind "video-script" on the bare
substring "script", also a literal substring of "manuscript" and
"description", so 50 chapter_NN_manuscript.md files (the paid book's own
text) were classified ready to post as free video scripts. (2) split_posts
required a "\\n---+\\n" divider between every numbered "## " section and
returned an empty list, silently, for any file with none, which was most of
the corpus (119 of 153 ready facebook-post files, 17 of 51 ready
linkedin-post files). Both gates re-derive their own check on every run
instead of trusting the fix stays fixed; this file proves each one fires on
the exact regression shape and stays quiet on the real, current corpus.

Run:  python ops/tests/test_gate_corpus_posts.py
"""
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import corpus_index as ci                                      # noqa: E402
import corpus_posts as cp                                      # noqa: E402


def _with_temp_book(files: dict):
    """files: {relative/path.md: text}. Points corpus_index.BOOK at a fresh
    temp dir holding exactly these files, yields nothing, restores after."""
    tmp_dir = tempfile.mkdtemp()
    real_book = ci.BOOK
    try:
        for rel, text in files.items():
            full = os.path.join(tmp_dir, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            io.open(full, "w", encoding="utf-8").write(text)
        ci.BOOK = tmp_dir
        yield
    finally:
        ci.BOOK = real_book
        shutil.rmtree(tmp_dir)


def _run(fn):
    before_fail = len(preflight.FAIL)
    fn()
    fails = preflight.FAIL[before_fail:]
    del preflight.FAIL[before_fail:]
    return fails


PROSE = " ".join(["Real sentence long enough to read as finished prose."] * 10)


def test_manuscript_leak_fails_by_name():
    """The gate's own invariant, not today's specific fix: whatever pattern
    corpus_index.KINDS carries in the future, a file with "manuscript" in
    its path must never come back "ready". Reintroduces the original bug
    (a bare "script" substring pattern, which also matches "manuscript")
    against corpus_index.classify() directly, the same shape found
    2026-09-22, so this test does not depend on today's fix staying
    word-for-word the same to keep proving anything."""
    real_kinds = ci.KINDS
    gen = _with_temp_book({
        "6S-Chapter-9/chapter_09_manuscript.md": f"# Chapter 9\n\n{PROSE}\n",
    })
    next(gen)
    try:
        ci.KINDS = [(r"script", "video-script", True)]
        fails = _run(preflight.gate_corpus_posts_no_manuscript_leak)
    finally:
        ci.KINDS = real_kinds
        next(gen, None)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "corpus-posts-manuscript-leak", fails
    assert "manuscript" in msg, msg
    print("ok  a manuscript file classified ready fails by name")


def test_real_script_file_does_not_leak():
    gen = _with_temp_book({
        "6S-Chapter-9/teleprompter-script.md": f"# Chapter 9 Script\n\n{PROSE}\n",
    })
    next(gen)
    try:
        fails = _run(preflight.gate_corpus_posts_no_manuscript_leak)
    finally:
        next(gen, None)
    assert not fails, fails
    print("ok  a real teleprompter-script.md file passes clean")


def test_description_file_does_not_match_video_script():
    kind, publishable = ci.classify("chapter-9-description.md")
    assert kind != "video-script", (kind, publishable)
    print("ok  a *-description*.md file no longer classifies as video-script")


def test_extraction_yield_fails_when_most_files_yield_nothing():
    # "quote" (chapter-quotes.md) is explicitly in EXTRACTORS with its own
    # split_quotes, which has no whole-file fallback: it needs at least one
    # "## " heading to find anything. Four files with none reproduce the
    # exact "ready but the extractor finds nothing" shape.
    files = {}
    for i in range(4):
        files[f"6S-Chapter-{i}/chapter-quotes.md"] = (
            f"# Chapter {i} Quotes\n\n"
            f"No '## ' heading anywhere in this file, just prose with "
            f"nothing split_quotes can section on. {PROSE}"
        )
    gen = _with_temp_book(files)
    next(gen)
    try:
        fails = _run(preflight.gate_corpus_posts_extraction_yield)
    finally:
        next(gen, None)
    assert len(fails) == 1, fails
    gate, msg = fails[0]
    assert gate == "corpus-posts-extraction-yield", fails
    assert "quote" in msg, msg
    print("ok  a kind whose files yield nothing fails by name")


def test_extraction_yield_passes_on_real_corpus():
    fails = _run(preflight.gate_corpus_posts_extraction_yield)
    assert not fails, (
        "the real corpus fails this gate right now: %s" % fails)
    print("ok  the real committed corpus passes clean")


def test_no_manuscript_leak_passes_on_real_corpus():
    fails = _run(preflight.gate_corpus_posts_no_manuscript_leak)
    assert not fails, (
        "the real corpus fails this gate right now: %s" % fails)
    print("ok  the real committed corpus passes clean")


if __name__ == "__main__":
    test_manuscript_leak_fails_by_name()
    test_real_script_file_does_not_leak()
    test_description_file_does_not_match_video_script()
    test_extraction_yield_fails_when_most_files_yield_nothing()
    test_extraction_yield_passes_on_real_corpus()
    test_no_manuscript_leak_passes_on_real_corpus()
    print("\nall gate_corpus_posts tests passed")
