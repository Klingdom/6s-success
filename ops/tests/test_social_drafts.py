#!/usr/bin/env python3
"""
ops/social_drafts.py, the Facebook/X sibling of linkedin_drafts.py.

Mirrors test_linkedin_drafts.py's own rotation-safety proof (a preview must
never spend a post; only a real send may), plus the one thing this file adds
that linkedin_drafts.py never needed: a hard per-platform length limit. X
rejects anything over 280 characters, so build("x", ...) must never hand back
a post that could not actually be posted as written.

Run:  python ops/tests/test_social_drafts.py

Found 2026-09-15: this test used to mutate the real, git-tracked
ops/corpus-rotation.json directly and restore it in a `finally` block, the
same shape test_linkedin_drafts.py had. A `finally` only runs if the
interpreter unwinds the stack; a hard interrupt (a `timeout`-bounded caller
sending SIGTERM, a crash, a killed subprocess) skips it, leaving the real
rotation file permanently polluted with fake served posts, which then makes
every later run of this same test flaky against whatever was left behind.
Reproduced live: an interrupted `preflight.py` run left three fake
`facebook-post` entries in the real file. Fixed the same way: point
corpus_posts.ROTATION at an isolated temp path for the duration of the
test, so the real file is never written at all, crash or no crash.
"""
import io
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import social_drafts as sd                                       # noqa: E402
import corpus_posts as cp                                         # noqa: E402


def _read_rotation():
    if not os.path.exists(cp.ROTATION):
        return None
    return io.open(cp.ROTATION, encoding="utf-8").read()


def _remaining(text: str) -> int:
    m = re.search(r"([\d,]+) usable", text)
    return int(m.group(1).replace(",", ""))


def main() -> int:
    fails = []
    real_rotation = cp.ROTATION
    fd, tmp_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.remove(tmp_path)                              # start absent, like a fresh install
    cp.ROTATION = tmp_path
    before = _read_rotation()

    try:
        sd.build("facebook")
        after_default = _read_rotation()
        if after_default != before:
            fails.append("build() with record left unset mutated "
                         "corpus-rotation.json; the default must behave "
                         "like a preview")

        sd.build("facebook", record=False)
        after_explicit_false = _read_rotation()
        if after_explicit_false != before:
            fails.append("build(record=False) mutated corpus-rotation.json")

        _, text_day1 = sd.build("facebook", record=True)
        after_record_true = _read_rotation()
        if after_record_true == before:
            fails.append("build(record=True) left corpus-rotation.json "
                         "unchanged; a real --send would never advance")

        # Found 2026-09-12: "remaining" was a bare len(pool(...)), so this
        # line reported the same full corpus size every single day forever,
        # never reflecting a single post actually served. Proved by replaying
        # three consecutive days against a scratch rotation file and watching
        # the number never move. A second real day must show it drop by
        # exactly the platform's own daily count, not stay frozen.
        remaining_day1 = _remaining(text_day1)
        _, text_day2 = sd.build("facebook", record=True)
        remaining_day2 = _remaining(text_day2)
        expected = remaining_day1 - sd.PLATFORMS["facebook"]["n"]
        if remaining_day2 != expected:
            fails.append(f"'remaining' read {remaining_day1} then "
                         f"{remaining_day2} across two served days; expected "
                         f"it to drop to {expected}, one day's worth of "
                         f"posts actually served")
    finally:
        # The real rotation file was never touched: only the temp path was.
        # Restoring the module attribute is enough; the crash-unsafe window
        # this used to have against the real file no longer exists.
        cp.ROTATION = real_rotation
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # An unknown platform is a programming error, not a silent no-op.
    try:
        sd.build("instagram")
        fails.append("build('instagram') should have raised, no such platform "
                     "is configured")
    except SystemExit:
        pass

    # Every real X post this ever hands back must fit in one actual tweet.
    # Run against the live corpus, not a fixture, because the defect this
    # guards (261 of 741 real posts still carrying a leftover character-count
    # annotation, found 2026-09-12 building this file) only shows up there.
    subject, text = sd.build("x")
    for chunk in text.split("=" * 64)[1:]:
        body = chunk.split("\n\n", 1)[1] if "\n\n" in chunk else chunk
        body = body.rsplit("\n\n", 1)[0].strip()
        if len(body) > sd.X_CHAR_CAP:
            fails.append(f"an X draft ran to {len(body)} characters, over "
                         f"the {sd.X_CHAR_CAP}-character limit: {body[:60]!r}")

    # And nothing served to either platform should carry the annotation
    # corpus_posts.split_numbered now strips: the regression this whole file
    # exists to protect from recurring silently in a downstream consumer.
    if "chars)" in text:
        fails.append("a leftover char-count annotation reached a real draft")

    total = 7
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
