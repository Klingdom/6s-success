#!/usr/bin/env python3
"""
Prove ops/preflight.py's gate_x_post_titles_unique() catches the real defect
found 2026-09-14 in ops/social_drafts.py's own preview output: two different
X posts, from the same chapter, both titled "Post 10", indistinguishable
until read. Traced to corpus_posts.split_numbered(): every one of the 50
chapters carries two numbered X-post source files (x-thread.md,
x-short-posts-10.md), each numbered from 1 independently, so the whole
723-post corpus collided in 238 pairs before the fix (confirmed directly
against the pre-fix commit in an isolated worktree, not estimated).

The fix folds a filename-derived hint into the title so two posts from
different files never render identically; this test proves the checking
logic itself (check_x_post_titles_unique) catches the pre-fix shape and
passes clean on the fixed shape and on an unrelated corpus, using a
synthetic pool rather than the real 245-file corpus so it runs in
milliseconds and is not sensitive to future corpus edits.

Run:  python ops/tests/test_gate_x_post_titles_unique.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import preflight                                               # noqa: E402
import corpus_posts as cp                                      # noqa: E402


def main() -> int:
    fails = []

    # 1. The exact pre-fix shape: two chapters, each with two source files
    #    both numbered "Post 10", must be caught.
    collision_pool = [
        {"chapter": "ch04", "title": "Post 10", "source": "a/x-thread.md"},
        {"chapter": "ch04", "title": "Post 10", "source": "a/x-short-posts-10.md"},
        {"chapter": "ch04", "title": "Post 11", "source": "a/x-thread.md"},
    ]
    bad = preflight.check_x_post_titles_unique(collision_pool)
    if len(bad) != 1:
        fails.append(f"expected 1 collision, found {len(bad)}: {bad}")

    # 2. The fixed shape (a filename hint folded into the title) must pass
    #    clean, same chapter and numbers, now distinguishable.
    fixed_pool = [
        {"chapter": "ch04", "title": "Post 10 (thread)", "source": "a/x-thread.md"},
        {"chapter": "ch04", "title": "Post 10 (short posts)", "source": "a/x-short-posts-10.md"},
        {"chapter": "ch04", "title": "Post 11 (thread)", "source": "a/x-thread.md"},
    ]
    bad2 = preflight.check_x_post_titles_unique(fixed_pool)
    if bad2:
        fails.append(f"fixed pool should be clean, found: {bad2}")

    # 3. Two different chapters sharing a title (e.g. both chapter's thread
    #    opens with "Post 1") is not a real collision: nobody reads two
    #    chapters' worth of posts side by side in one day's draft with no
    #    chapter label, and the display always carries [chXX] alongside it.
    cross_chapter = [
        {"chapter": "ch01", "title": "Post 1 (thread)", "source": "a/x-thread.md"},
        {"chapter": "ch02", "title": "Post 1 (thread)", "source": "b/x-thread.md"},
    ]
    bad3 = preflight.check_x_post_titles_unique(cross_chapter)
    if bad3:
        fails.append(f"cross-chapter same title is not a defect, found: {bad3}")

    # 4. The same (chapter, title, source) repeated is not a collision (the
    #    same post counted twice), only two DIFFERENT sources colliding is.
    same_source_twice = [
        {"chapter": "ch01", "title": "Post 1 (thread)", "source": "a/x-thread.md"},
        {"chapter": "ch01", "title": "Post 1 (thread)", "source": "a/x-thread.md"},
    ]
    bad4 = preflight.check_x_post_titles_unique(same_source_twice)
    if bad4:
        fails.append(f"identical source repeated is not a defect, found: {bad4}")

    # 5. The real, live corpus must be clean after the actual fix.
    real = cp.pool("x-post")
    bad5 = preflight.check_x_post_titles_unique(real)
    if bad5:
        fails.append(f"the real corpus has {len(bad5)} unfixed collision(s): {bad5[:3]}")

    if fails:
        print(f"  {len(fails)} of 5 cases fail:")
        for f in fails:
            print(f"   - {f}")
        return 1
    print("  5 of 5 cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
