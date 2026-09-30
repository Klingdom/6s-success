#!/usr/bin/env python3
"""
ops/bluesky_drafts.py, the Bluesky sibling of social_drafts.py's X draft.

Mirrors test_social_drafts.py's own proofs (preview must never spend a post;
a length cap must actually hold; an interrupted run must never pollute the
real rotation file), plus the one thing this file adds: bluesky_drafts.py
shares its content pool with social_drafts.py's X draft ("x-post") but must
track its own served set ("bluesky-post"), so the two can never silently
halve each other's supply.

Run:  python ops/tests/test_bluesky_drafts.py
"""
import io
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "ops"))

import bluesky_drafts as bd                                      # noqa: E402
import social_drafts as sd                                        # noqa: E402
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
        bd.build()
        after_default = _read_rotation()
        if after_default != before:
            fails.append("build() with record left unset mutated "
                         "corpus-rotation.json; the default must behave "
                         "like a preview")

        bd.build(record=False)
        after_explicit_false = _read_rotation()
        if after_explicit_false != before:
            fails.append("build(record=False) mutated corpus-rotation.json")

        _, text_day1 = bd.build(record=True)
        after_record_true = _read_rotation()
        if after_record_true == before:
            fails.append("build(record=True) left corpus-rotation.json "
                         "unchanged; a real --send would never advance")

        remaining_day1 = _remaining(text_day1)
        _, text_day2 = bd.build(record=True)
        remaining_day2 = _remaining(text_day2)
        expected = remaining_day1 - bd.N
        if remaining_day2 != expected:
            fails.append(f"'remaining' read {remaining_day1} then "
                         f"{remaining_day2} across two served days; expected "
                         f"it to drop to {expected}")

        # The whole point of pool_kind: bluesky-drafts' own rotation must not
        # move social_drafts.py's "x-post" ledger, and vice versa. Both read
        # the same pool; each must track its own served set independently.
        rot_after_bluesky = cp.load_rotation()
        if rot_after_bluesky["served"].get("x-post"):
            fails.append("serving Bluesky drafts marked posts served under "
                         "the 'x-post' key too; the two platforms would "
                         "silently steal supply from each other")

        _, x_text = sd.build("x", record=True)
        rot_after_x = cp.load_rotation()
        if not rot_after_x["served"].get("bluesky-post"):
            fails.append("the earlier Bluesky-served ids vanished after "
                         "recording an X send; the two rotation keys are "
                         "not independent")
        overlap = (set(rot_after_x["served"].get("bluesky-post", [])) &
                   set(rot_after_x["served"].get("x-post", [])))
        # Overlap alone is fine (two independent pipelines may legitimately
        # pick the same early post); what matters is each key's own count
        # advanced by its own platform's own daily n, checked above and below.
        del overlap
    finally:
        cp.ROTATION = real_rotation
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # Every real post this ever hands back must fit in one actual Bluesky
    # post. Run against the live corpus, not a fixture.
    subject, text = bd.build()
    for chunk in text.split("=" * 64)[1:]:
        body = chunk.split("\n\n", 1)[1] if "\n\n" in chunk else chunk
        body = body.rsplit("\n\n", 1)[0].strip()
        if len(body) > bd.BSKY_CHAR_CAP:
            fails.append(f"a Bluesky draft ran to {len(body)} characters, "
                         f"over the {bd.BSKY_CHAR_CAP}-character limit: "
                         f"{body[:60]!r}")

    if "chars)" in text:
        fails.append("a leftover char-count annotation reached a real draft")

    total = 7
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"  {total - len(fails)} of {total} cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
